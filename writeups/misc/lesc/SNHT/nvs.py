#!/usr/bin/env python3
"""
nvs.py

Reusable helper for decoding an entire Zephyr-NVS sector that contains both
Data records and their Allocation-Table-Entries (ATEs).

Public API (import side)
------------------------
>>> import nvs_sector as nvs
>>> data    = Path("sector.bin").read_bytes()
>>> sector  = nvs.Sector(data, origin=0x3E000)
>>> sector.ates        # list[ATE]
>>> sector.records      # list[Record]
>>> sector.live_records # dict[(uid, flags) -> Record]
"""

from __future__ import annotations
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple

POLY, CRC_INIT = 0x07, 0xFF           # CRC‑8 / CCITT parameters


# ─────────────────────────────────── CRC‑8 ──────────────────────────────────
def crc8_ccitt(buf: bytes, poly: int = POLY, init: int = CRC_INIT) -> int:
    crc = init
    for b in buf:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ poly) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


# ───────────────────────────────── data classes ─────────────────────────────
@dataclass(frozen=True)
class ATE:
    """Represents a single Allocation-Table-Entry (ATE). Only fields that are
    *directly* stored in flash are kept here. Higher-level interpretations such
    as UID or flag bits are now derived lazily where needed instead of being
    stored in this class.
    """

    idx:     int
    address: int             # absolute flash address
    id:      int             # 16‑bit ID as stored in flash (incl. setting flag bits)
    offset:  int
    length:  int
    part:    int
    crc:     int
    crc_ok:  bool

    @classmethod
    def from_bytes(cls, idx: int, address: int, chunk: bytes) -> "ATE":
        id_    = int.from_bytes(chunk[0:2], "little")
        offset = int.from_bytes(chunk[2:4], "little")
        length = int.from_bytes(chunk[4:6], "little")
        part   = chunk[6]
        crc_st = chunk[7]
        crc_ok = crc_st == crc8_ccitt(chunk[:7])
        return cls(idx, address, id_, offset, length, part, crc_st, crc_ok)


@dataclass(frozen=True)
class Record:
    uid:     int
    flags:   int            # 2 = name, 3 = value
    offset:  int
    length:  int
    data:    bytes


# ───────────────────────────────── sector parser ────────────────────────────
class Sector:
    """Represents one flash sector that Zephyrs NVS has written to."""

    def __init__(self, buf: bytes, origin: int = 0) -> None:
        self._buf    = buf
        self.origin  = origin
        self.ates    = self._collect_ates()
        self.records = self._extract_records()

        # convenient lookup: (uid, flags) → Record
        self.live_records: Dict[Tuple[int, int], Record] = {
            (r.uid, r.flags): r for r in self.records
        }

    # ───────────────────────── private helpers ─────────────────────────────
    def _collect_ates(self) -> List[ATE]:
        """Walk backwards, gather ATEs until encountering blank flash or bad CRC."""
        rows: List[ATE] = []
        pos  = len(self._buf) - 8
        idx  = 0

        # skip trailing 0xFF blocks
        while pos >= 0 and self._buf[pos:pos+8] == b"\xFF"*8:
            pos -= 8

        while pos >= 0:
            chunk = self._buf[pos:pos+8]
            ate   = ATE.from_bytes(idx, self.origin + pos, chunk)
            if not ate.crc_ok:
                break                     # first corruption ends list
            rows.append(ate)
            pos -= 8
            idx += 1
            if pos < 0 or self._buf[pos:pos+8] == b"\xFF"*8:
                break

        return list(reversed(rows))

    def _extract_records(self) -> List[Record]:
        """Turn ATEs into `Record` objects (skip zero-len & deleted ones)."""
        recs: List[Record] = []
        for ate in self.ates:
            if not ate.crc_ok or ate.length == 0:
                continue
            data = self._buf[ate.offset: ate.offset + ate.length]
            # derive UID and flag bits on‑the‑fly from the 16‑bit ID
            uid   = ate.id & 0x3FFF
            flags = (ate.id >> 14) & 0x3
            recs.append(Record(uid, flags, ate.offset, ate.length, data))
        return recs

    # ─────────────────────────—— CLI pretty‑printing —──────────────────────
    def print_ate_table(self) -> None:
        hdrs = [
            "Idx", "Address", "ID", "Off", "Len", "Prt", "CRC", "OK"
        ]
        w = {h: len(h) for h in hdrs}
        for a in self.ates:
            for h, val in zip(hdrs, [a.idx,
                                      f"0x{a.address:06X}",
                                      f"{a.id:04X}",
                                      a.offset, a.length,
                                      a.part, f"0x{a.crc:02X}", a.crc_ok]):
                w[h] = max(w[h], len(str(val)))

        def fmt(row):
            return "  ".join(f"{str(row[h]):>{w[h]}}" for h in hdrs)

        print(fmt(dict(zip(hdrs, hdrs))))
        print(fmt({h: "-"*w[h] for h in hdrs}))
        for a in self.ates:
            print(fmt({
                "Idx": a.idx,
                "Address": f"0x{a.address:06X}",
                "ID": f"{a.id:04X}",
                "Off": a.offset,
                "Len": a.length,
                "Prt": a.part,
                "CRC": f"0x{a.crc:02X}",
                "OK":  a.crc_ok,
            }))
        print()

    def dump_records(self) -> None:
        for r in self.records:
            print(
                f"Record UID {r.uid} (flags={r.flags}) "
                f"offset 0x{r.offset:04X} len {r.length}"
            )
            self._hexdump(r.data, r.offset)
            print()

    @staticmethod
    def _hexdump(buf: bytes, base: int, cols: int = 16) -> None:
        for i in range(0, len(buf), cols):
            chunk = buf[i:i+cols]
            hexp  = " ".join(f"{b:02X}" for b in chunk)
            txt   = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            print(f"  0x{base+i:04X}  {hexp:<{cols*3}}  {txt}")


# ─────────────────────────── Stand‑alone CLI ───────────────────────────────
def _main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: nvs.py <sector.bin> [origin]")
    data   = Path(sys.argv[1]).read_bytes()
    origin = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0

    sec = Sector(data, origin)
    sec.print_ate_table()
    sec.dump_records()


if __name__ == "__main__":
    _main()
