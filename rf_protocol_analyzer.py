import numpy as np


def _moving_average(values, window):
    window = max(1, int(window))
    kernel = np.ones(window, dtype=float) / float(window)
    return np.convolve(values, kernel, mode="same")


def _slice_bits(binary_stream, samples_per_bit, phase):
    bits = binary_stream[phase::samples_per_bit]
    return "".join(str(int(v)) for v in bits)


def _score_preamble(bitstream, preamble):
    if not preamble or len(bitstream) < len(preamble):
        return 0
    score = 0
    for idx in range(0, len(bitstream) - len(preamble) + 1):
        if bitstream[idx : idx + len(preamble)] == preamble:
            score += 1
    return score


def decode_ook_iq(iq_samples, sample_rate, bit_rate, preamble="01010101", max_bits=1024):
    """Decodes raw complex IQ samples into an OOK/ASK bitstream.

    Returns a dict with decoded bitstream metadata for telemetry pipelines.
    """
    if iq_samples is None or len(iq_samples) == 0:
        return {
            "decoder": "ook",
            "status": "NO_SIGNAL",
            "decoded_bits": "",
            "payload_bits": "",
            "has_preamble": False,
        }

    samples_per_bit = max(1, int(sample_rate / bit_rate))

    # 1) Magnitude extraction (envelope)
    magnitude = np.abs(iq_samples)

    # 2) Low-pass smoothing (moving average)
    smoothed = _moving_average(magnitude, samples_per_bit)

    # 3) Dynamic thresholding to binary
    threshold = (float(np.max(smoothed)) + float(np.min(smoothed))) / 2.0
    binary_stream = (smoothed > threshold).astype(np.int8)

    # 4) Symbol slicing with phase search
    best_phase = 0
    best_score = -1
    best_bits = ""
    phases_to_check = min(samples_per_bit, 64)

    for phase in range(phases_to_check):
        candidate = _slice_bits(binary_stream, samples_per_bit, phase)[:max_bits]
        score = _score_preamble(candidate, preamble)
        if score > best_score:
            best_score = score
            best_phase = phase
            best_bits = candidate

    if not best_bits:
        return {
            "decoder": "ook",
            "status": "NO_SIGNAL",
            "decoded_bits": "",
            "payload_bits": "",
            "has_preamble": False,
        }

    payload_bits = best_bits
    has_preamble = False
    preamble_index = -1

    if preamble:
        preamble_index = best_bits.find(preamble)
        if preamble_index >= 0:
            has_preamble = True
            payload_bits = best_bits[preamble_index + len(preamble) :]

    return {
        "decoder": "ook",
        "status": "OK" if has_preamble else "NO_PREAMBLE",
        "samples_per_bit": samples_per_bit,
        "phase": best_phase,
        "threshold": threshold,
        "has_preamble": has_preamble,
        "preamble": preamble,
        "preamble_index": preamble_index,
        "decoded_bits": best_bits,
        "payload_bits": payload_bits,
    }


def synthesize_ook_iq(bitstream, sample_rate, bit_rate, noise_std=0.08):
    """Generate synthetic OOK IQ samples for simulation and testing."""
    samples_per_bit = max(1, int(sample_rate / bit_rate))
    levels = np.array([1.0 if b == "1" else 0.0 for b in bitstream], dtype=float)
    envelope = np.repeat(levels, samples_per_bit)

    i = envelope + np.random.normal(0.0, noise_std, len(envelope))
    q = np.random.normal(0.0, noise_std, len(envelope))
    return i + 1j * q
