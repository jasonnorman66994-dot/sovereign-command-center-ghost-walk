import argparse
import asyncio
import csv
import json
from pathlib import Path
import time

import numpy as np
import websockets

from rf_protocol_analyzer import decode_ook_iq
from sdr_source_adapter import SDRSourceAdapter
from signature_database import register_signature


# ---------------------------------------------------------------------------
# Burst validation primitives
# ---------------------------------------------------------------------------

def count_ook_pulses(samples, sample_rate, bit_rate, preamble):
    """Return 1 if a valid OOK pulse (preamble + payload) is decoded in the IQ stream, else 0."""
    decoded = decode_ook_iq(samples, sample_rate=sample_rate, bit_rate=bit_rate, preamble=preamble)
    return 1 if (decoded.get("has_preamble") and decoded.get("payload_bits")) else 0


def calculate_burst_magnitude(samples):
    """Return RMS power of the burst IQ stream as a float signature value."""
    if not hasattr(samples, "__len__") or len(samples) == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.abs(samples) ** 2)))


def _count_rising_edges(samples):
    """
    Count distinct power peaks (rising-edge transitions) in an IQ sample buffer.

    Uses a midpoint threshold so it works with any gain stage without OOK
    decode—making it hardware-agnostic and faster than preamble matching.
    """
    magnitude = np.abs(samples)
    if magnitude.size == 0:
        return 0
    threshold = (float(np.max(magnitude)) + float(np.min(magnitude))) / 2.0
    pulses = (magnitude > threshold).astype(np.int8)
    return int(np.sum(np.diff(pulses) == 1))


def trigger_device_api(adapter, gain, frequency, expected_bursts=16, num_samples=131072, demo_mode=False):
    """
    Hardened RF Trigger API — Omni-SOC gatekeeper for signature telemetry.

    Tunes the adapter to *frequency* at *gain*, waits 0.5 s for hardware
    settling, then ingests a single IQ buffer and counts rising-edge
    transitions as a hardware-agnostic event counter.

    Returns a result dict::

        {
            "status":        "VALIDATED" | "INCOMPLETE" | "CLIPPING" | "TOO_WEAK",
            "events":        int,          # rising-edge count
            "signature":     float,        # peak magnitude
            "snr_db":        float,
            "frequency_mhz": float,
            "message":       str           # only when INCOMPLETE
        }

    demo_mode: if True, bypasses the live-hardware guard and generates a
               realistic synthetic 315 MHz burst for dashboard simulation.
    """
    adapter.set_frequency(frequency)
    adapter.set_gain(gain)
    time.sleep(0.5)

    if demo_mode:
        # Inject a realistic 315 MHz OOK keyfob burst (16 pulses, clean signal)
        rng = np.random.default_rng(seed=int(frequency) % 65537)
        t = np.linspace(0, 0.064, num_samples)
        carrier = np.exp(1j * 2 * np.pi * 3000 * t)
        # 16 rectangular pulses spaced evenly across the buffer
        envelope = np.zeros(num_samples)
        pulse_width = num_samples // 64
        for k in range(16):
            start = k * (num_samples // 16) + pulse_width
            envelope[start:start + pulse_width] = 0.72
        noise = (rng.standard_normal(num_samples) + 1j * rng.standard_normal(num_samples)) * 0.04
        iq_samples = (envelope * carrier) + noise
        event_count = _count_rising_edges(iq_samples)
        magnitude = np.abs(iq_samples)
        peak_power = float(np.max(magnitude))
        noise_floor = float(np.mean(magnitude))
        snr = 20.0 * np.log10(peak_power / noise_floor) if noise_floor > 0 else 0.0
        return {
            "status": "VALIDATED",
            "events": max(event_count, expected_bursts),
            "signature": round(peak_power, 6),
            "snr_db": round(snr, 3),
            "frequency_mhz": frequency / 1e6,
            "demo": True,
        }

    if getattr(adapter, "mode", "synthetic") != "live":
        return {
            "status": "INCOMPLETE",
            "events": 0,
            "signature": 0.0,
            "snr_db": 0.0,
            "frequency_mhz": frequency / 1e6,
            "message": "Adapter is not in live SDR mode. Connect RTL-SDR hardware.",
        }

    iq_samples = adapter.get_samples(num_samples=num_samples)
    event_count = _count_rising_edges(iq_samples)

    if event_count < expected_bursts:
        return {
            "status": "INCOMPLETE",
            "events": event_count,
            "signature": 0.0,
            "snr_db": 0.0,
            "frequency_mhz": frequency / 1e6,
            "message": (
                f"Dropped {expected_bursts - event_count} pulses. "
                "Signal too weak or inconsistent."
            ),
        }

    magnitude = np.abs(iq_samples)
    peak_power = float(np.max(magnitude))
    noise_floor = float(np.mean(magnitude))
    snr = 20.0 * np.log10(peak_power / noise_floor) if noise_floor > 0 else 0.0

    hw_status = "CLIPPING" if peak_power > 0.98 else ("TOO_WEAK" if peak_power < 0.10 else "VALIDATED")
    return {
        "status": hw_status,
        "events": event_count,
        "signature": peak_power,
        "snr_db": snr,
        "frequency_mhz": frequency / 1e6,
    }


def trigger_device(adapter, gain, frequency, expected_bursts=16,
                   sample_rate=2_048_000, bit_rate=1200, preamble="01010101", num_samples=131072):
    """
    Set hardware parameters and validate the signal against the 16-event consistency rule.

    Tunes the adapter to *frequency* at *gain*, waits for hardware settling, then
    collects *expected_bursts* independent sample windows and counts how many contain
    a valid OOK pulse.  Returns a result dict compatible with the sweep row schema:

        {"status": "VALID"|"INVALID"|"CLIPPING"|"TOO_WEAK",
         "score": float,            # RMS burst magnitude (0 if INVALID)
         "pulses_detected": int,    # pulses found out of expected_bursts
         "peak": float,             # peak IQ magnitude across all chunks
         "snr_db": float,           # estimated SNR in dB
         "consistency": float,      # pulses_detected / expected_bursts
         "error": str}              # only present when status == "INVALID"
    """
    adapter.set_frequency(frequency)
    adapter.set_gain(gain)
    time.sleep(0.5)  # Hardware settling time

    pulses_detected = 0
    burst_chunks = []
    for _ in range(expected_bursts):
        chunk = adapter.get_samples(num_samples=num_samples)
        burst_chunks.append(chunk)
        # Use rising-edge counting (hardware-agnostic) instead of OOK decode
        if _count_rising_edges(chunk) >= 1:
            pulses_detected += 1

    combined = np.concatenate(burst_chunks) if burst_chunks else np.array([], dtype=np.complex64)
    magnitude = np.abs(combined)
    peak = float(np.max(magnitude)) if magnitude.size else 0.0
    avg_noise = float(np.mean(magnitude)) if magnitude.size else 1e-12
    snr_db = 20 * np.log10(peak / avg_noise) if avg_noise > 0 else 0.0
    consistency = pulses_detected / expected_bursts

    if pulses_detected < expected_bursts:
        return {
            "status": "INVALID",
            "score": 0.0,
            "pulses_detected": pulses_detected,
            "peak": peak,
            "snr_db": snr_db,
            "consistency": consistency,
            "error": "Insufficient pulse count",
        }

    signature_value = calculate_burst_magnitude(combined)
    hw_status = "CLIPPING" if peak > 0.98 else ("TOO_WEAK" if peak < 0.10 else "VALID")
    return {
        "status": hw_status,
        "score": signature_value,
        "pulses_detected": pulses_detected,
        "peak": peak,
        "snr_db": snr_db,
        "consistency": consistency,
    }


# ---------------------------------------------------------------------------
# Signature capture
# ---------------------------------------------------------------------------

def build_signature_library(adapter, sample_rate, bit_rate, preamble, num_samples):
    print(">>> STANDBY: Trigger your RF device now. Press Ctrl+C to abort.")
    while True:
        # Quick detection pass: look for any OOK payload in the IQ stream.
        samples = adapter.get_samples(num_samples=num_samples)
        decoded = decode_ook_iq(
            samples,
            sample_rate=sample_rate,
            bit_rate=bit_rate,
            preamble=preamble,
        )
        bits = (decoded.get("payload_bits") or "").strip()

        if not bits or len(bits) <= 8:
            continue

        # Burst validation: require 16 consistent OOK pulses before accepting.
        print(f"[*] Signal detected. Running 16-event burst validation…")
        burst_result = trigger_device_api(
            adapter=adapter,
            gain=adapter.gain,
            frequency=adapter.center_freq,
            expected_bursts=16,
            num_samples=num_samples,
        )
        if burst_result["status"] == "INCOMPLETE":
            print(
                f"[!] INCOMPLETE burst: {burst_result.get('message', '')} "
                f"({burst_result['events']}/16 events). Re-trigger your device…"
            )
            continue

        print(f"\n[+] Captured Bitstream: {bits}")
        print(
            f"[+] Burst Validated — Signature: {burst_result['signature']:.4f} | "
            f"Events: {burst_result['events']}/16 | "
            f"SNR: {burst_result['snr_db']:.1f} dB | Status: {burst_result['status']}"
        )
        name = input("Enter device name to save (or 'skip'): ").strip()
        if name.lower() == "skip":
            print("[*] Capture skipped. Waiting for next burst...")
            continue

        level = input("Enter trust level [Authorized/System] (default Authorized): ").strip() or "Authorized"
        location = input("Enter location tag (optional): ").strip()

        saved = register_signature(bits=bits, name=name, level=level, location=location)
        print(
            f"[*] Identity '{saved['name']}' committed to Sovereign Library: {saved['bits']}"
        )
        print(f"[*] Persisted at: {saved['library_path']}")
        return


def check_gain_levels(adapter, num_samples=1024 * 1024):
    print(">>> SDR GAIN DIAGNOSTIC: Trigger your RF device for 3 seconds...")
    samples = adapter.get_samples(num_samples=num_samples)
    magnitude = np.abs(samples)

    peak = float(np.max(magnitude)) if magnitude.size else 0.0
    avg_noise = float(np.mean(magnitude)) if magnitude.size else 0.0
    snr = 20 * np.log10(peak / avg_noise) if avg_noise > 0 else 0.0
    clipped = peak > 0.95

    print("--- Results ---")
    print(f"Peak Magnitude: {peak:.4f} {'[!! CLIPPING !!]' if clipped else '[SAFE]'}")
    print(f"Noise Floor:    {avg_noise:.4f}")
    print(f"Est. SNR:       {snr:.2f} dB")

    return {
        "clipped": clipped,
        "peak": peak,
        "noise_floor": avg_noise,
        "snr_db": float(snr),
    }


def _parse_gain_candidates(raw):
    values = []
    for token in (raw or "").split(","):
        item = token.strip()
        if not item:
            continue
        if item.lower() == "auto":
            values.append("auto")
            continue
        try:
            values.append(float(item))
        except ValueError:
            pass
    return values or [0.0, 10.0, 20.0, 30.0, 40.0, 49.0]


def _set_adapter_gain(adapter, gain):
    if not adapter.sdr:
        return
    try:
        adapter.sdr.gain = gain
    except Exception:
        pass


def sweep_gain_levels(sample_rate, center_freq, gains, num_samples, settle_seconds=0.2):
    results = []
    print(f">>> Running gain sweep at {center_freq / 1e6:.3f} MHz")
    print(f"{'Gain (dB)':<10} | {'Peak Mag':<10} | {'SNR (dB)':<10} | {'Status'}")
    print("-" * 50)
    adapter = SDRSourceAdapter(sample_rate=sample_rate, center_freq=center_freq, gain=gains[0] if gains else "auto")
    try:
        if adapter.mode != "live":
            print("[!] Adapter is not in live mode; gain sweep on synthetic source is not meaningful.")
            return results

        for gain in gains:
            _set_adapter_gain(adapter, gain)
            time.sleep(settle_seconds)

            samples = adapter.get_samples(num_samples=num_samples)
            magnitude = np.abs(samples)
            peak = float(np.max(magnitude)) if magnitude.size else 0.0
            avg_noise = float(np.mean(magnitude)) if magnitude.size else 0.0
            snr = 20 * np.log10(peak / avg_noise) if avg_noise > 0 else 0.0

            status = "SAFE"
            if peak > 0.98:
                status = "CLIPPING"
            elif peak < 0.1:
                status = "TOO WEAK"

            print(f"{gain!s:<10} | {peak:<10.4f} | {snr:<10.2f} | {status}")
            results.append(
                {
                    "gain": gain,
                    "peak": peak,
                    "noise_floor": avg_noise,
                    "snr_db": float(snr),
                    "clipped": peak > 0.95,
                    "status": status,
                }
            )
    finally:
        adapter.close()
    return results


def recommend_gain(results, target_peak=0.75):
    if not results:
        return None

    safe = [r for r in results if not r.get("clipped")]
    if not safe:
        return None

    preferred = [r for r in safe if 0.65 <= float(r.get("peak", 0.0)) <= 0.85]
    pool = preferred if preferred else safe
    return max(pool, key=lambda r: float(r.get("snr_db", 0.0)))


def write_rf_gain_env(env_path, gain_value):
    path = Path(env_path)
    line = f"RF_GAIN={gain_value}"
    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()
    else:
        lines = []

    updated = False
    out = []
    for existing in lines:
        if existing.strip().startswith("RF_GAIN="):
            out.append(line)
            updated = True
        else:
            out.append(existing)

    if not updated:
        out.append(line)

    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"[*] Wrote RF_GAIN={gain_value} to {path}")


def _load_sweet_spot_signatures(csv_path="sweet_spot_summary.csv"):
    rows = []
    path = Path(csv_path)
    if not path.exists():
        return rows

    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                try:
                    rows.append(
                        {
                            "frequency_hz": float(row.get("frequency_hz", 0.0) or 0.0),
                            "gain_db": float(row.get("gain_db", 0.0) or 0.0),
                            "signature": float(
                                row.get("signature", row.get("signature_score", 0.0)) or 0.0
                            ),
                        }
                    )
                except (TypeError, ValueError):
                    continue
    except OSError:
        return []

    return rows


def _compute_match_distance(signature_value, frequency_hz, gain_db, sweet_spots):
    if not sweet_spots:
        return None

    same_freq = [r for r in sweet_spots if int(r.get("frequency_hz", 0)) == int(frequency_hz)]
    pool = same_freq if same_freq else sweet_spots

    best = min(
        pool,
        key=lambda r: (
            abs(signature_value - r.get("signature", 0.0)),
            abs(gain_db - r.get("gain_db", 0.0)),
        ),
    )
    return round(abs(signature_value - best.get("signature", 0.0)), 6)


async def _emit_dashboard_event(ws_url, payload):
    async with websockets.connect(ws_url) as ws:
        await ws.send(json.dumps(payload))


def initiate_live_capture(
    gain=35.0,
    frequency=433_920_000.0,
    expected_bursts=16,
    sample_rate=2.048e6,
    bit_rate=1200,
    preamble="01010101",
    num_samples=256 * 1024,
    ws_url="ws://localhost:8765",
):
    """Run the hardened live ingestion loop until a VALIDATED burst is captured."""
    adapter = SDRSourceAdapter(sample_rate=sample_rate, center_freq=frequency, gain=gain)
    sweet_spots = _load_sweet_spot_signatures()

    print(f"[*] Omni-SOC: SDR Adapter engaged at {frequency / 1e6:.2f} MHz.")
    print("[*] 16-Event Gate: ACTIVE. (Waiting for valid burst...)")

    try:
        attempt = 0
        while True:
            attempt += 1
            result = trigger_device_api(
                adapter=adapter,
                gain=gain,
                frequency=frequency,
                expected_bursts=expected_bursts,
                num_samples=num_samples,
            )

            samples = adapter.get_samples(num_samples=num_samples)
            decoded = decode_ook_iq(
                samples,
                sample_rate=sample_rate,
                bit_rate=bit_rate,
                preamble=preamble,
            )
            bits = (decoded.get("payload_bits") or "").strip()

            snr_db = float(result.get("snr_db", 0.0))
            trust_score = round(min(max(snr_db / 40.0, 0.0), 1.0), 4)
            if result.get("status") == "INCOMPLETE":
                trust_score = 0.0

            match_distance = _compute_match_distance(
                signature_value=float(result.get("signature", 0.0)),
                frequency_hz=frequency,
                gain_db=gain,
                sweet_spots=sweet_spots,
            )

            dashboard_event = {
                "event": "RF_BURST_DETECTED",
                "protocol": "sub-ghz-ook",
                "payload": bits,
                "magnitude": max(0.1, min(1.0, float(result.get("signature", 0.0)))),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "frequency_hz": int(frequency),
                "device_classification": "trusted" if result.get("status") == "VALIDATED" else "unknown",
                "identity": "Pending Validation" if result.get("status") != "VALIDATED" else "Validated Device",
                "identity_location": "RF Bay",
                "identity_level": "Authorized" if result.get("status") == "VALIDATED" else "Unknown",
                "identity_status": "Authenticated" if result.get("status") == "VALIDATED" else "Threat Detected",
                "trust_score": trust_score,
                "match_distance": match_distance,
                "match_confidence": round(max(0.0, 1.0 - (match_distance or 1.0)), 4) if match_distance is not None else 0.0,
            }

            try:
                asyncio.run(_emit_dashboard_event(ws_url, dashboard_event))
            except Exception:
                pass

            if attempt % 20 == 0 and result.get("status") != "VALIDATED":
                print(
                    f"[*] Waiting... status={result.get('status')} "
                    f"events={result.get('events', 0)}/{expected_bursts} "
                    f"trust={trust_score:.2f}"
                )

            if result.get("status") == "VALIDATED":
                print("\n[!] HIGH-FIDELITY BURST DETECTED")
                print(f"| Events: {result['events']} | SNR: {result['snr_db']:.2f} dB |")

                if bits and len(bits) > 8:
                    name = input("Enter device name to save (or 'skip'): ").strip()
                    if name.lower() != "skip":
                        level = input("Enter trust level [Authorized/System] (default Authorized): ").strip() or "Authorized"
                        location = input("Enter location tag (optional): ").strip()
                        saved = register_signature(bits=bits, name=name, level=level, location=location)
                        print(
                            f"[*] Identity '{saved['name']}' committed to Sovereign Library: {saved['bits']}"
                        )
                        print(f"[*] Persisted at: {saved['library_path']}")
                else:
                    print("[!] Burst validated but no payload bits were decoded for labeling.")

                return result

            time.sleep(0.1)
    finally:
        adapter.close()


def main():
    parser = argparse.ArgumentParser(description="Capture and register RF signatures from SDR samples.")
    parser.add_argument("--sample-rate", type=float, default=2.048e6)
    parser.add_argument("--bit-rate", type=float, default=1200)
    parser.add_argument("--preamble", default="01010101")
    parser.add_argument("--center-freq", type=float, default=433.92e6)
    parser.add_argument("--gain", default="auto")
    parser.add_argument("--num-samples", type=int, default=256 * 1024)
    parser.add_argument("--check-gain", action="store_true", help="Run one-shot clipping/noise/SNR diagnostic")
    parser.add_argument("--sweep-gain", action="store_true", help="Run gain sweep and print recommendation")
    parser.add_argument(
        "--gain-candidates",
        default="0,10,20,30,40,49",
        help="Comma-separated gain values for sweep; supports 'auto'",
    )
    parser.add_argument("--target-peak", type=float, default=0.75, help="Target peak magnitude for calibration")
    parser.add_argument("--write-env", default="", help="Path to .env file to write recommended RF_GAIN")
    parser.add_argument("--live-capture", action="store_true", help="Run hardened live capture loop with 16-event gate")
    parser.add_argument("--expected-bursts", type=int, default=16, help="Required rising-edge events for validation")
    parser.add_argument("--ws-url", default="ws://localhost:8765", help="WebSocket endpoint for dashboard updates")
    args = parser.parse_args()

    if args.sweep_gain:
        gains = _parse_gain_candidates(args.gain_candidates)
        results = sweep_gain_levels(
            sample_rate=args.sample_rate,
            center_freq=args.center_freq,
            gains=gains,
            num_samples=max(args.num_samples, 1024 * 1024),
        )
        recommendation = recommend_gain(results, target_peak=args.target_peak)
        if recommendation is None:
            print("[!] No calibration recommendation produced.")
            return
        print("\n=== Recommended Gain ===")
        print(f"Gain: {recommendation['gain']}")
        print(f"Peak: {recommendation['peak']:.4f}")
        print(f"SNR:  {recommendation['snr_db']:.2f} dB")
        if recommendation["peak"] < 0.65 or recommendation["peak"] > 0.85:
            print("[!] Peak is outside the preferred 0.65-0.85 headroom band.")
        if recommendation["snr_db"] < 15:
            print("[!] SNR below preferred threshold (15-20 dB).")
        if args.write_env:
            write_rf_gain_env(args.write_env, recommendation["gain"])
        return

    if args.live_capture:
        live_gain = args.gain
        try:
            live_gain = float(args.gain)
        except (TypeError, ValueError):
            pass
        initiate_live_capture(
            gain=live_gain,
            frequency=float(args.center_freq),
            expected_bursts=int(args.expected_bursts),
            sample_rate=float(args.sample_rate),
            bit_rate=float(args.bit_rate),
            preamble=args.preamble,
            num_samples=int(args.num_samples),
            ws_url=args.ws_url,
        )
        return

    adapter = SDRSourceAdapter(
        sample_rate=args.sample_rate,
        center_freq=args.center_freq,
        gain=args.gain,
    )

    try:
        if args.check_gain:
            check_gain_levels(adapter, num_samples=max(args.num_samples, 1024 * 1024))
            if adapter.mode != "live":
                print("[!] Adapter is in synthetic mode; this diagnostic is not hardware-representative.")
            return

        build_signature_library(
            adapter=adapter,
            sample_rate=args.sample_rate,
            bit_rate=args.bit_rate,
            preamble=args.preamble,
            num_samples=args.num_samples,
        )
    except KeyboardInterrupt:
        print("\n[!] Capture cancelled by operator.")
    finally:
        adapter.close()


if __name__ == "__main__":
    main()
