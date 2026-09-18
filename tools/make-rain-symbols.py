#!/usr/bin/env python3
"""Print Matrix-Code's codepoints shifted into plane 16, for the screensaver.

The rain in scripts/system/ttfx falls in the film's own glyphs rather than
ttfx's default halfwidth katakana. Those glyphs are reached through
MatrixCodeTerminal.ttf, which maps every one of them to 0x100000 + its original
codepoint -- plane 16, which nothing else on a system uses, so the font can sit
in a terminal's font chain without ever supplying a character anyone types.

The list is embedded in the shim rather than computed at runtime: the shim runs
inside the screensaver, where a failure is a black screen with no way to read
the error.

    tools/make-rain-symbols.py
"""

import pathlib
import struct
import sys

PUA_BASE = 0x100000
CANDIDATES = [
    "~/.local/share/matrix-rain/assets/Matrix-Code.ttf",
    "~/.local/share/fonts/Matrix-Code.ttf",
    "~/Downloads/Matrix-Code.ttf",
]


def codepoints(path):
    """The cmap of a format 4 TrueType font, the way redpill-render reads it."""
    d = pathlib.Path(path).expanduser().read_bytes()
    n = struct.unpack(">H", d[4:6])[0]
    tabs = {d[12 + i * 16:16 + i * 16].decode("latin1"):
            struct.unpack(">II", d[20 + i * 16:28 + i * 16]) for i in range(n)}
    base = tabs["cmap"][0]
    sub = None
    for i in range(struct.unpack(">H", d[base + 2:base + 4])[0]):
        off = struct.unpack(">HHI", d[base + 4 + i * 8:base + 12 + i * 8])[2]
        if struct.unpack(">H", d[base + off:base + off + 2])[0] == 4:
            sub = base + off
    seg2 = struct.unpack(">H", d[sub + 6:sub + 8])[0]
    seg = seg2 // 2
    ends = struct.unpack(f">{seg}H", d[sub + 14:sub + 14 + seg2])
    starts = struct.unpack(f">{seg}H", d[sub + 16 + seg2:sub + 16 + 2 * seg2])

    out = []
    for s, e in zip(starts, ends):
        if s == 0xFFFF:
            continue
        out += [c for c in range(s, min(e, 0xFFFF) + 1) if c >= 33]
    # U+FFFD passes as printable and the private-use block is in the cmap too.
    return [c for c in out if c != 0xFFFD and not (0xE000 <= c <= 0xF8FF)]


def main():
    for path in CANDIDATES:
        if pathlib.Path(path).expanduser().exists():
            cps = codepoints(path)
            print(" ".join(chr(PUA_BASE + c) for c in cps))
            print(f"{len(cps)} glyphs from {path}", file=sys.stderr)
            return
    sys.exit("Matrix-Code.ttf not found; install matrix-rain first")


if __name__ == "__main__":
    main()
