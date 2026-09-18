#!/usr/bin/env python3
"""Compose branding/screensaver.txt: OMATRIX in Omarchy's own logo face.

Omarchy's screensaver is not a graphical program. It runs `ttfx` over
~/.config/omarchy/branding/screensaver.txt, so the wordmark IS the screensaver.

OMARCHY and OMATRIX share O, M, A and R, so those four are cut out of
/usr/share/omarchy/logo.txt rather than redrawn -- they are the original
letterforms, not an imitation of them. T, I and X do not exist there and are
drawn here to the same rules, read off the letters that do:

  * stems are three columns wide
  * a horizontal bar is a lower-half run over an upper-half run, so the bar
    straddles a row boundary rather than filling a row
  * the face has NO diagonals. The M is three verticals with a bridge, not two
    slanted strokes. The X is the one place a crossing cannot be avoided, and it
    is built from the same half-block vocabulary: stems lean in, meet at a
    waist, flare out again.

Columns are sliced but rows never are: the M's apex overshoots the cap line and
the R's leg descends below the baseline. Trimming blank rows per letter loses
both offsets and the word comes out ragged.

    tools/make-wordmark.py
"""

import pathlib
import sys

SOURCE = pathlib.Path("/usr/share/omarchy/logo.txt")
OUT = pathlib.Path(__file__).resolve().parent.parent / "branding/screensaver.txt"

# Letter spans in the source, found by looking for columns blank in every row.
# C and H touch and would need splitting by hand; neither is used here.
SPANS = {"O": (0, 10), "M": (10, 27), "A": (27, 38), "R": (38, 49)}

DRAWN = {
    "T": ([
        "▄█████████▄",
        "▀▀▀▀███▀▀▀▀",
        "    ███    ",
        "    ███    ",
        "    ███    ",
        "    ███    ",
        "    ███    ",
        "    ▀█▀    ",
    ], 11),
    "I": ([
        " ▄█▄ ",
        " ███ ",
        " ███ ",
        " ███ ",
        " ███ ",
        " ███ ",
        " ███ ",
        " ▀█▀ ",
    ], 5),
    "X": ([
        "█▄     ▄█",
        "███   ███",
        "▀███ ███▀",
        " ▀█████▀ ",
        " ▄█████▄ ",
        "▄███ ███▄",
        "███   ███",
        "█▀     ▀█",
    ], 9),
}

GAP = 2        # columns between letters, matching the source's own spacing
CAP_ROW = 1    # the row the existing letters start on


def main():
    if not SOURCE.exists():
        sys.exit(f"{SOURCE} is missing; is Omarchy installed?")
    src = SOURCE.read_text().rstrip("\n").split("\n")
    height = len(src)
    width = max(len(line) for line in src)
    src = [line.ljust(width) for line in src]

    def cut(a, b):
        return [line[a:b] for line in src]

    def drawn(rows, w):
        grid = [" " * w] * height
        for i, row in enumerate(rows):
            grid[i + CAP_ROW] = row.ljust(w)
        return grid

    letters = [cut(*SPANS[c]) if c in SPANS else drawn(*DRAWN[c]) for c in "OMATRIX"]

    out = [(" " * GAP).join(g[r] for g in letters).rstrip() for r in range(height)]
    while out and not out[-1].strip():
        out.pop()

    OUT.write_text("\n".join(out) + "\n")
    print(f"wrote {OUT}  ({len(out)} x {max(len(l) for l in out)}; "
          f"OMARCHY is {height} x {width})")


if __name__ == "__main__":
    main()
