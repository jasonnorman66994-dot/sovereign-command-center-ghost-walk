"""RF signature identity database with live capture persistence support.

Zero-Trust Vault Mode
---------------------
If a Sovereign Vault USB drive is present (marked with a SOVEREIGN_VAULT
file at its root), the signature library is read from and written to the
drive instead of the local workspace.  Without the drive, the Omni-SOC has
no reference for any captured device — the workstation itself holds no
cleartext identity mappings.

Priority chain for library path:
  1. $SOVEREIGN_VAULT_LIBRARY env var (explicit override)
  2. <vault_drive>/sovereign_signatures/known_devices_library.json (USB vault)
  3. <workspace>/known_devices_library.json (local fallback)
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from sdr_source_adapter import find_vault_drive, vault_sig_dir

# ---------------------------------------------------------------------------
# Known device signatures
# Key   : canonical payload_bits (post-preamble OOK payload, no padding)
# Value : device metadata
# ---------------------------------------------------------------------------
DEFAULT_KNOWN_DEVICES: dict[str, dict] = {
    "1011001111001111": {
        "name": "Richard's Workspace Keyfob",
        "level": "Authorized",
        "location": "Office – Desk A",
    },
    "1110101011110001": {
        "name": "Server Room PIR Sensor",
        "level": "System",
        "location": "Server Room – Bay 2",
    },
    "1000111101010101": {
        "name": "Perimeter Gate Trigger",
        "level": "Authorized",
        "location": "East Gate – Panel 3",
    },
    "1100111011110001": {
        "name": "HVAC Control Module",
        "level": "System",
        "location": "Roof – HVAC Unit 1",
    },
    "1111001110001111": {
        "name": "Lab Door Proximity Tag",
        "level": "Authorized",
        "location": "Lab B – Entry",
    },
    # Legacy / stripped variants (preamble stripped)
    "101101001010": {
        "name": "Richard's Workspace Keyfob (legacy)",
        "level": "Authorized",
        "location": "Office – Desk A",
    },
    "111100001111": {
        "name": "Server Room PIR Sensor (legacy)",
        "level": "System",
        "location": "Server Room – Bay 2",
    },
    "000011110000": {
        "name": "Perimeter Gate Trigger (legacy)",
        "level": "Authorized",
        "location": "East Gate – Panel 3",
    },
}

LIBRARY_PATH = Path(__file__).with_name("known_devices_library.json")

# Runtime library map (defaults + user captured signatures)
KNOWN_DEVICES: dict[str, dict] = dict(DEFAULT_KNOWN_DEVICES)

# Maximum Hamming distance to still classify as "trusted"
# 0 = exact match only; 2 = tolerates 2 bit-flips (radio noise)
FUZZY_THRESHOLD: int = 2


# ---------------------------------------------------------------------------
# Library path resolution (zero-trust vault)
# ---------------------------------------------------------------------------

def _resolve_library_path() -> Path:
    """
    Return the active library JSON path.

    Priority:
      1. $SOVEREIGN_VAULT_LIBRARY env var
      2. USB vault drive  → <vault>/sovereign_signatures/known_devices_library.json
      3. Local workspace  → known_devices_library.json
    """
    env_override = os.environ.get("SOVEREIGN_VAULT_LIBRARY")
    if env_override:
        return Path(env_override)

    vault = find_vault_drive()
    if vault is not None:
        sig_dir = vault_sig_dir(vault)
        return sig_dir / "known_devices_library.json"

    return Path(__file__).with_name("known_devices_library.json")


def get_library_path() -> Path:
    """Return the currently active library path (vault or local)."""
    return _resolve_library_path()


def vault_status() -> dict:
    """Return vault presence info for API/dashboard consumption."""
    vault = find_vault_drive()
    lib_path = _resolve_library_path()
    return {
        "vault_present": vault is not None,
        "vault_drive": str(vault) if vault else None,
        "library_path": str(lib_path),
        "library_exists": lib_path.exists(),
        "zero_trust_active": vault is not None,
    }


def _sanitize_bits(raw_bits: str) -> str:
    return "".join(ch for ch in (raw_bits or "") if ch in {"0", "1"})


def _load_library_file() -> dict[str, dict]:
    path = _resolve_library_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    if not isinstance(data, dict):
        return {}

    loaded: dict[str, dict] = {}
    for bits, meta in data.items():
        clean_bits = _sanitize_bits(bits)
        if not clean_bits or not isinstance(meta, dict):
            continue
        loaded[clean_bits] = {
            "name": str(meta.get("name", "Unnamed Device")),
            "level": str(meta.get("level", "Authorized")),
            "location": str(meta.get("location", "")),
        }
    return loaded


def _save_library_file(entries: dict[str, dict]) -> None:
    path = _resolve_library_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, indent=2, sort_keys=True), encoding="utf-8")


def reload_known_devices() -> dict[str, dict]:
    """Reload runtime known-device map from defaults + persisted library file."""
    KNOWN_DEVICES.clear()
    KNOWN_DEVICES.update(DEFAULT_KNOWN_DEVICES)
    KNOWN_DEVICES.update(_load_library_file())
    return KNOWN_DEVICES


def register_signature(bits: str, name: str, level: str = "Authorized", location: str = "") -> dict:
    """Persist and activate a captured signature in the local signature library."""
    full_bits = _sanitize_bits(bits)
    stripped_bits = full_bits.strip("0")

    if not full_bits:
        raise ValueError("Captured bitstream is empty after sanitation.")
    if len(full_bits) < 8 and len(stripped_bits) < 8:
        raise ValueError("Captured bitstream too short for reliable identity matching.")

    entry = {
        "name": (name or "Unnamed Device").strip(),
        "level": (level or "Authorized").strip(),
        "location": (location or "").strip(),
    }

    library = _load_library_file()
    library[full_bits] = entry
    # Alias stripped variant for payloads that include decoder padding.
    if stripped_bits and stripped_bits != full_bits:
        library[stripped_bits] = entry

    _save_library_file(library)
    KNOWN_DEVICES[full_bits] = entry
    if stripped_bits and stripped_bits != full_bits:
        KNOWN_DEVICES[stripped_bits] = entry

    lib_path = _resolve_library_path()
    return {
        "bits": full_bits,
        "name": entry["name"],
        "level": entry["level"],
        "location": entry["location"],
        "library_path": str(lib_path),
        "vault_active": find_vault_drive() is not None,
    }


def _hamming_distance(a: str, b: str) -> int:
    """Bit-level Hamming distance between two binary strings of any length."""
    length = min(len(a), len(b))
    diff = sum(1 for i in range(length) if a[i] != b[i])
    diff += abs(len(a) - len(b))
    return diff


def identify_payload(decoded_bits: str) -> dict:
    """
    Match decoded_bits against the signature database.

    Returns a dict with:
        identity      – device name or 'Unknown Device'
        location      – physical location or ''
        level         – 'Authorized' | 'System' | 'Unknown'
        trust_score   – 0.0–1.0 (1.0 = exact match)
        status        – 'Authenticated' | 'Threat Detected'
        match_distance – Hamming distance to best match (None if no match)
    """
    if not decoded_bits:
        return _unknown_result(None)

    # 1. Try exact match first (fastest path)
    if decoded_bits in KNOWN_DEVICES:
        device = KNOWN_DEVICES[decoded_bits]
        return {
            "identity": device["name"],
            "location": device.get("location", ""),
            "level": device["level"],
            "trust_score": 1.0,
            "status": "Authenticated",
            "match_distance": 0,
        }

    # 2. Try stripped variant (remove leading/trailing 0s — decoder padding)
    stripped = decoded_bits.strip("0")
    if stripped and stripped in KNOWN_DEVICES:
        device = KNOWN_DEVICES[stripped]
        return {
            "identity": device["name"],
            "location": device.get("location", ""),
            "level": device["level"],
            "trust_score": 0.95,
            "status": "Authenticated",
            "match_distance": 0,
        }

    # 3. Fuzzy Hamming match
    best_name = None
    best_device = None
    best_distance = None

    candidates = list(KNOWN_DEVICES.items())
    # Only compare against signatures of similar length (±4 bits)
    for signature, device in candidates:
        if abs(len(signature) - len(decoded_bits)) > 4:
            continue
        dist = _hamming_distance(decoded_bits, signature)
        if best_distance is None or dist < best_distance:
            best_distance = dist
            best_name = signature
            best_device = device

    if best_device is not None and best_distance is not None and best_distance <= FUZZY_THRESHOLD:
        denom = max(len(decoded_bits), len(best_name), 1)
        trust = round(max(0.0, 1.0 - (best_distance / denom)), 4)
        return {
            "identity": best_device["name"],
            "location": best_device.get("location", ""),
            "level": best_device["level"],
            "trust_score": trust,
            "status": "Authenticated",
            "match_distance": best_distance,
        }

    return _unknown_result(best_distance)


def _unknown_result(distance) -> dict:
    return {
        "identity": "Unknown Device",
        "location": "",
        "level": "Unknown",
        "trust_score": 0.05,
        "status": "Threat Detected",
        "match_distance": distance,
    }


# Hydrate runtime map on module import.
reload_known_devices()
