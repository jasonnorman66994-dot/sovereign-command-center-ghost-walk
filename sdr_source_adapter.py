import os
import sys
import glob
from pathlib import Path

import numpy as np

# Ensure the pyrtlsdr package directory is in the DLL search path on Windows
# so rtlsdr.dll (copied there) is found by ctypes.CDLL
if sys.platform == "win32":
    try:
        _rtlsdr_pkg = os.path.join(
            os.path.dirname(sys.executable), "..", "Lib", "site-packages", "rtlsdr"
        )
        _rtlsdr_pkg = os.path.normpath(_rtlsdr_pkg)
        if os.path.isdir(_rtlsdr_pkg):
            os.add_dll_directory(_rtlsdr_pkg)
        # Also add the workspace root in case user placed the DLL there
        _workspace = os.path.dirname(os.path.abspath(__file__))
        os.add_dll_directory(_workspace)
    except Exception:
        pass

try:
    from rtlsdr import RtlSdr

    HAS_SDR_HARDWARE = True
except ImportError:
    HAS_SDR_HARDWARE = False


# ---------------------------------------------------------------------------
# USB Vault Detection
# ---------------------------------------------------------------------------
# Directory name written to the root of the Sovereign vault drive.
# Touch a file named "SOVEREIGN_VAULT" on the drive root to register it.
_VAULT_MARKER = "SOVEREIGN_VAULT"
_IQ_SUBDIR    = "sovereign_iq"          # .iq files live here
_SIG_SUBDIR   = "sovereign_signatures"  # signature DB lives here


def _explicit_vault_path() -> Path | None:
    raw = os.getenv("VAULT_PATH", "").strip()
    if not raw:
        return None
    return Path(raw)


def find_vault_drive() -> Path | None:
    """
    Scan all removable/fixed drive roots for a SOVEREIGN_VAULT marker file.
    Returns the vault root Path on the first match, or None if absent.
    """
    explicit = _explicit_vault_path()
    if explicit is not None:
        return explicit.parent if explicit.suffix else explicit

    if sys.platform == "win32":
        import string
        import ctypes
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        candidates = [
            Path(f"{letter}:\\")
            for i, letter in enumerate(string.ascii_uppercase)
            if bitmask & (1 << i)
        ]
    else:
        # Linux/macOS: check /media and /mnt mount points
        candidates = list(Path("/media").glob("*/*")) + list(Path("/mnt").glob("*"))
        candidates += [Path("/Volumes") / d for d in Path("/Volumes").iterdir()] if Path("/Volumes").exists() else []

    for drive in candidates:
        if (drive / _VAULT_MARKER).exists():
            return drive
    return None


def vault_iq_dir(vault: Path) -> Path:
    d = vault / _IQ_SUBDIR
    d.mkdir(parents=True, exist_ok=True)
    return d


def vault_sig_dir(vault: Path) -> Path:
    explicit = _explicit_vault_path()
    if explicit is not None:
        d = explicit.parent if explicit.suffix else explicit
        d.mkdir(parents=True, exist_ok=True)
        return d

    d = vault / _SIG_SUBDIR
    d.mkdir(parents=True, exist_ok=True)
    return d


class SDRSourceAdapter:
    def __init__(self, sample_rate=2.048e6, center_freq=433.92e6, gain="auto",
                 iq_file: str | None = None):
        self.sample_rate = float(sample_rate)
        self.center_freq = float(center_freq)
        self.gain = gain
        self.sdr = None
        self.is_live = False
        self.mode = "synthetic"

        # IQ file playback state
        self._iq_file: Path | None = None
        self._iq_data: np.ndarray | None = None
        self._iq_cursor: int = 0

        # Vault
        self.vault: Path | None = find_vault_drive()

        # Priority: explicit iq_file arg → vault IQ files → hardware → synthetic
        if iq_file:
            self._load_iq_file(Path(iq_file))
        elif self.vault is not None:
            self._try_load_vault_iq()

        if self.mode not in ("file",):
            self._initialize_source()

    def _load_iq_file(self, path: Path) -> bool:
        """Load a raw interleaved float32 IQ file (I,Q,I,Q,...) into memory."""
        try:
            raw = np.fromfile(str(path), dtype=np.float32)
            if len(raw) < 2:
                return False
            # Interleaved → complex
            n = (len(raw) // 2) * 2
            self._iq_data = raw[:n:2] + 1j * raw[1:n:2]
            self._iq_data = self._iq_data.astype(np.complex64)
            self._iq_cursor = 0
            self._iq_file = path
            self.mode = "file"
            self.is_live = False
            print(f"[+] Vault IQ loaded: {path.name} ({len(self._iq_data):,} samples)")
            return True
        except Exception as exc:
            print(f"[!] Failed to load IQ file {path}: {exc}")
            return False

    def _try_load_vault_iq(self):
        """Pick the most recent .iq file from the vault that matches center_freq."""
        iq_dir = vault_iq_dir(self.vault)
        freq_mhz = f"{self.center_freq / 1e6:.3f}"
        # Prefer files whose name contains the target frequency
        matches = sorted(iq_dir.glob(f"*{freq_mhz}*.iq"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not matches:
            matches = sorted(iq_dir.glob("*.iq"), key=lambda p: p.stat().st_mtime, reverse=True)
        if matches:
            self._load_iq_file(matches[0])
            return
        print(f"[*] Vault present at {self.vault} but no .iq files found — falling through to synthetic.")

    def _read_iq_chunk(self, num_samples: int) -> np.ndarray:
        """Return num_samples from the loaded IQ buffer, looping as needed."""
        buf = self._iq_data
        n = len(buf)
        if n == 0:
            return np.zeros(num_samples, dtype=np.complex64)
        out = np.empty(num_samples, dtype=np.complex64)
        filled = 0
        while filled < num_samples:
            remaining_in_buf = n - self._iq_cursor
            need = num_samples - filled
            take = min(remaining_in_buf, need)
            out[filled:filled + take] = buf[self._iq_cursor:self._iq_cursor + take]
            filled += take
            self._iq_cursor = (self._iq_cursor + take) % n
        return out

    def _resolved_gain(self):
        if isinstance(self.gain, str):
            if self.gain.lower() == "auto":
                return "auto"
            try:
                return float(self.gain)
            except ValueError:
                return "auto"
        return self.gain

    def _initialize_source(self):
        if HAS_SDR_HARDWARE:
            try:
                self.sdr = RtlSdr()
                self.sdr.sample_rate = self.sample_rate
                self.sdr.center_freq = self.center_freq
                self.sdr.gain = self._resolved_gain()
                self.is_live = True
                self.mode = "live"
                print(f"[+] SDR Hardware Initialized: {self.center_freq / 1e6:.3f} MHz")
                return
            except Exception as exc:
                print(f"[!] Hardware found but failed to open: {exc}. Falling back to simulation.")

        print("[*] No SDR library/hardware detected. Initializing Simulation Mode.")
        self.is_live = False
        self.mode = "synthetic"

    def _synthetic_burst(self, num_samples):
        t = np.linspace(0, num_samples / self.sample_rate, num_samples, endpoint=False)

        pulse_rate = float(os.getenv("RF_SYNTH_PULSE_HZ", "1000"))
        envelope = (np.sin(2.0 * np.pi * pulse_rate * t) > 0).astype(np.float32)

        bits = "01010101" + "1011001110001111"
        samples_per_bit = max(1, int(self.sample_rate / float(os.getenv("RF_BIT_RATE", "1200"))))
        bit_levels = np.array([1.0 if b == "1" else 0.0 for b in bits], dtype=np.float32)
        burst = np.repeat(bit_levels, samples_per_bit)
        if len(burst) < num_samples:
            burst = np.pad(burst, (0, num_samples - len(burst)))
        else:
            burst = burst[:num_samples]

        amp = float(os.getenv("RF_SYNTH_SIGNAL_AMP", "0.1"))
        noise_scale = float(os.getenv("RF_SYNTH_NOISE_AMP", "0.01"))

        i = (0.6 * envelope + 0.4 * burst) * amp + np.random.randn(num_samples) * noise_scale
        q = np.random.randn(num_samples) * noise_scale
        return i.astype(np.float32) + 1j * q.astype(np.float32)

    def get_samples(self, num_samples=256 * 1024):
        num_samples = int(num_samples)
        if self.mode == "file" and self._iq_data is not None:
            return self._read_iq_chunk(num_samples)
        if self.is_live and self.sdr:
            try:
                return self.sdr.read_samples(num_samples)
            except Exception as exc:
                print(f"[!] Stream Interrupted: {exc}. Switching to fallback.")
                self.is_live = False
                self.mode = "synthetic"

        return self._synthetic_burst(num_samples)

    def set_frequency(self, center_freq):
        self.center_freq = float(center_freq)
        if self.is_live and self.sdr:
            try:
                self.sdr.center_freq = self.center_freq
            except Exception as exc:
                print(f"[!] Failed to set center frequency: {exc}")
                self.is_live = False
                self.mode = "synthetic"

    def set_gain(self, gain):
        self.gain = gain
        if self.is_live and self.sdr:
            try:
                self.sdr.gain = self._resolved_gain()
            except Exception as exc:
                print(f"[!] Failed to set gain: {exc}")
                self.is_live = False
                self.mode = "synthetic"

    def close(self):
        if self.sdr:
            try:
                self.sdr.close()
            except Exception:
                pass
            finally:
                self.sdr = None
                self.is_live = False
                self.mode = "closed"
