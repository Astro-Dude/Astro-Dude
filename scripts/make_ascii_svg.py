"""Turn source-prepped.png into ascii-portrait.svg: one light glyph colour on
the dark terminal, each row typed out left to right with a cursor riding the
wipe, top to bottom, printed once and then frozen.

    python scripts/make_ascii_svg.py
"""
from html import escape

import numpy as np
from PIL import Image

from svgkit import FG, GREEN, MONO, ROOT, window

RAMP = " .`:-=+*cs#%@"   # dark (empty) -> bright (dense), for light glyphs on black
COLS = 104
FONT = 6.4
CW = FONT * 0.6          # JetBrains Mono advance is 600/1000 em
LH = FONT * 1.2
PAD_X, PAD_TOP, PAD_BOTTOM = 18, 30 + 16, 16
ROW_STEP, ROW_DUR = 0.035, 0.3


def ascii_rows():
    img = Image.open(ROOT / "source-prepped.png").convert("L")
    rows = round(COLS * img.height / img.width * CW / LH)
    small = np.asarray(img.resize((COLS, rows), Image.LANCZOS), dtype=np.float32) / 255
    small = small ** 1.35
    idx = np.clip((small * (len(RAMP) - 1)).round().astype(int), 0, len(RAMP) - 1)
    lines = ["".join(RAMP[i] for i in row).rstrip() for row in idx]
    while lines and not lines[0]:
        lines.pop(0)
    return lines


def main():
    lines = ascii_rows()
    width = round(PAD_X * 2 + COLS * CW)
    height = round(PAD_TOP + len(lines) * LH + PAD_BOTTOM)
    full = COLS * CW
    defs, body = [], []
    for i, line in enumerate(lines):
        y = PAD_TOP + i * LH
        begin = f"{0.3 + i * ROW_STEP:.3f}s"
        span = len(line) * CW if line else 0
        defs.append(
            f'<clipPath id="r{i}"><rect x="{PAD_X}" y="{y - 1:.1f}" width="0" height="{LH + 2:.1f}">'
            f'<animate attributeName="width" from="0" to="{full:.1f}" begin="{begin}" dur="{ROW_DUR}s" fill="freeze"/></rect></clipPath>'
        )
        if line:
            body.append(f'<text x="{PAD_X}" y="{y + FONT:.1f}" clip-path="url(#r{i})" xml:space="preserve">{escape(line)}</text>')
            body.append(
                f'<rect x="{PAD_X}" y="{y + 0.5:.1f}" width="{CW:.1f}" height="{LH - 1:.1f}" fill="{GREEN}" opacity="0">'
                f'<set attributeName="opacity" to="0.9" begin="{begin}"/>'
                f'<animate attributeName="x" from="{PAD_X}" to="{PAD_X + span:.1f}" begin="{begin}" dur="{ROW_DUR * span / full if span else 0.01:.3f}s" fill="freeze"/>'
                f'<set attributeName="opacity" to="0" begin="{0.3 + i * ROW_STEP + ROW_DUR:.3f}s"/></rect>'
            )
    content = (f'<defs>{"".join(defs)}</defs>'
               f'<g font-family="{MONO}" font-size="{FONT}" fill="{FG}">{"".join(body)}</g>')
    svg = window(width, height, "~/portrait.txt", content, "".join(lines), "ASCII portrait of Shaurya Verma")
    (ROOT / "ascii-portrait.svg").write_text(svg)
    print(f"wrote ascii-portrait.svg  {COLS}x{len(lines)} chars, {width}x{height}px, {len(svg)/1024:.0f} KB")


if __name__ == "__main__":
    main()
