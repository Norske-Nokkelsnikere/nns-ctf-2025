#!/usr/bin/env python3
"""
settings.py

Rebuild Zephyr Settings from a full NVS sector, showing historical
value blobs.
"""

import sys
from pathlib import Path
import nvs
from collections import defaultdict
from typing import Dict, List, Tuple


# ───────────────────────────── settings extraction ──────────────────────────
def gather_versions(sector: nvs.Sector
                    ) -> Dict[str, List[Tuple[bytes, bool]]]:
    """
    key → [ (value_bytes, is_current), ... ]  (oldest → newest)
    """
    uid_to_name: Dict[int, str] = {}
    for rec in sector.records:
        if rec.flags == 2:                           # name entry
            try:
                key = rec.data.rstrip(b"\xFF").decode("ascii")
            except UnicodeDecodeError:
                key = "<non-ascii-key-uid-%d>" % rec.uid
            uid_to_name[rec.uid] = key

    uid_to_vals: Dict[int, List[bytes]] = defaultdict(list)
    for rec in sector.records:
        if rec.flags == 3 and rec.length:
            uid_to_vals[rec.uid].append(rec.data)

    out: Dict[str, List[Tuple[bytes, bool]]] = {}
    for uid, key in uid_to_name.items():
        vals = uid_to_vals.get(uid, [])
        tagged = [(v, i == len(vals) - 1) for i, v in enumerate(vals)]
        out[key] = tagged
    return out


# ────────────────────────────── pretty-printing ─────────────────────────────
def _is_printable_ascii(b: bytes) -> bool:
    try:
        txt = b.decode("ascii")
        return all(32 <= ord(c) < 127 for c in txt)
    except UnicodeDecodeError:
        return False


def _dump_hex(b: bytes, indent: str = " " * 12, width: int = 16) -> str:
    lines = []
    for i in range(0, len(b), width):
        chunk = b[i:i+width]
        hexpart = " ".join(f"{byte:02X}" for byte in chunk)
        lines.append(f"{indent}{hexpart}")
    return "\n".join(lines)


def pretty_print(settings: Dict[str, List[Tuple[bytes, bool]]]) -> None:
    if not settings:
        print("No Settings entries found."); return

    key_width = max(len(k) for k in settings) + 1
    for key, versions in settings.items():
        if not versions:
            print(f"{key:<{key_width}}  <no value records>")
            continue

        print(key)                                     # key once
        for idx, (val, is_cur) in enumerate(versions):
            tag  = "current" if is_cur else f"old-{idx}"
            head = f"    ({tag}, {len(val)} B)"

            if len(val) <= 32 and _is_printable_ascii(val):
                ascii_val = val.decode("ascii")
                print(f"{head:<{key_width+12}}  {ascii_val}")
            else:
                print(head)
                print(_dump_hex(val))
        print()                                        # blank line


# ─────────────────────────────────── main ───────────────────────────────────
def _main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: settings.py <sector.bin> [origin]")

    data   = Path(sys.argv[1]).read_bytes()
    origin = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0

    sector   = nvs.Sector(data, origin)
    settings = gather_versions(sector)
    pretty_print(settings)


if __name__ == "__main__":
    _main()
