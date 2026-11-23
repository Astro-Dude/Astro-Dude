"""Write info-card.svg: a neofetch-style card whose lines fade and slide in,
staggered, beside the portrait. Sized to match ascii-portrait.svg's height
at the widths the README shows them (400 + 460 = 860).

    python scripts/make_info_card.py
"""
import re
from html import escape

from svgkit import BLUE, CYAN, DIM, FG, GREEN, MAGENTA, MONO, RED, ROOT, YELLOW, window

W = 460
FONT, LH = 11.5, 23
KEY_W = 11  # characters

LINES = [
    ("title", "shaurya", "arcfront"),
    ("rule",),
    ("kv", "Role", "Founding MTS Intern @ Arcfront"),
    ("kv", "Leading", "the Multi-RL vertical"),
    ("kv", "Platform", "internal tooling for Multi-RL worlds"),
    ("kv", "Shipped", "1 world / 1.5 weeks  ->  3 a day"),
    ("kv", "Before", "coding RL envs, real-app replicas"),
    ("kv", "Education", "B.Sc. CS, Birla Inst. of Technology"),
    ("kv", "Location", "Bengaluru, IN"),
    ("gap",),
    ("kv", "Projects", "BYOS · DOM Heist · Vector"),
    ("kv", "DOM Heist", "600+ installs, 200+ devs at Arcfront"),
    ("kv", "Vector", "400+ students"),
    ("kv", "Awards", "Top 100, Meta PyTorch OpenEnv"),
    ("kv", "", "CodeChef 3★, max rating 1649"),
    ("kv", "", "Finalist, Shaastra, IIT Madras"),
    ("kv", "Off-clock", "astronomy at 3 am, Dostoevsky"),
    ("gap",),
    ("swatches",),
]
SWATCHES = ["#484f58", RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, FG]


def portrait_height():
    svg = (ROOT / "ascii-portrait.svg").read_text()
    w, h = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups())
    return round(h * 400 / w * W / 460)


def main():
    h = portrait_height()
    x, y0 = 24, 30 + 30
    body, chars = [], ""
    y = y0
    for i, line in enumerate(LINES):
        begin = f"{0.5 + i * 0.11:.2f}s"
        anim = (f'<animate attributeName="opacity" from="0" to="1" begin="{begin}" dur="0.45s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" from="-10 0" to="0 0" begin="{begin}" dur="0.45s" fill="freeze"/>')
        kind = line[0]
        if kind == "gap":
            y += LH * 0.55
            continue
        if kind == "title":
            _, user, host = line
            chars += user + "@" + host
            inner = (f'<text x="{x}" y="{y}" font-weight="700"><tspan fill="{GREEN}">{user}</tspan>'
                     f'<tspan fill="{FG}">@</tspan><tspan fill="{GREEN}">{host}</tspan></text>')
        elif kind == "rule":
            dashes = "-" * len("shaurya@arcfront")
            chars += dashes
            inner = f'<text x="{x}" y="{y}" fill="{DIM}">{dashes}</text>'
        elif kind == "kv":
            _, key, val = line
            chars += key + val
            inner = (f'<text x="{x}" y="{y}" xml:space="preserve"><tspan fill="{CYAN}" font-weight="700">{escape(key.ljust(KEY_W))}</tspan>'
                     f'<tspan fill="{FG}">{escape(val)}</tspan></text>')
        else:  # swatches
            cw = 26
            inner = "".join(f'<rect x="{x + j * cw}" y="{y - 13}" width="{cw}" height="16" fill="{c}"/>' for j, c in enumerate(SWATCHES))
        body.append(f'<g opacity="0">{anim}{inner}</g>')
        y += LH
    content = f'<g font-family="{MONO}" font-size="{FONT}">{"".join(body)}</g>'
    svg = window(W, h, "neofetch", content, chars, "Shaurya Verma: Founding MTS Intern at Arcfront, leading Multi-RL. BYOS, DOM Heist (600+ installs), Vector (400+ students).")
    (ROOT / "info-card.svg").write_text(svg)
    print(f"wrote info-card.svg  {W}x{h}px, content ends at y={y:.0f}, {len(svg)/1024:.0f} KB")


if __name__ == "__main__":
    main()
