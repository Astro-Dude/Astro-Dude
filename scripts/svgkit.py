"""Shared bits for the profile SVGs: the terminal palette, an embedded mono
font (subset to the glyphs used, base64 WOFF2) and the window chrome."""
import base64
import io
from html import escape
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONT_PATH = ROOT / "fonts" / "JetBrainsMono-VF.ttf"
MONO = "'JBMono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

BG = "#0d1117"
BAR = "#161b22"
EDGE = "#30363d"
FG = "#c9d1d9"
DIM = "#8b949e"
GREEN = "#3fb950"
CYAN = "#56d4dd"
BLUE = "#58a6ff"
YELLOW = "#e3b341"
MAGENTA = "#d2a8ff"
RED = "#ff7b72"


def font_face(chars):
    font = TTFont(FONT_PATH)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern"]
    sub = subset.Subsetter(opts)
    sub.populate(text="".join(sorted(set(chars + " "))))
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:'JBMono';src:url(data:font/woff2;base64,{b64}) format('woff2');font-weight:100 800;}}"


def window(w, h, title, body, chars, label, extra_style=""):
    """A terminal window: rounded frame, title bar with three dots, body below."""
    chars += title
    style = font_face(chars) + "text{white-space:pre}" + extra_style
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(label)}">'
        f"<style>{style}</style>"
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="10" fill="{BG}" stroke="{EDGE}"/>'
        f'<path d="M0.5 10.5a10 10 0 0 1 10-10h{w-21}a10 10 0 0 1 10 10v20h-{w-1}z" fill="{BAR}"/>'
        f'<line x1="0.5" y1="30.5" x2="{w-0.5}" y2="30.5" stroke="{EDGE}"/>'
        f'<circle cx="18" cy="15.5" r="5" fill="#ff5f57"/><circle cx="35" cy="15.5" r="5" fill="#febc2e"/><circle cx="52" cy="15.5" r="5" fill="#28c840"/>'
        f'<text x="{w/2}" y="20" text-anchor="middle" font-family="{MONO}" font-size="11.5" fill="{DIM}">{escape(title)}</text>'
        f"{body}</svg>"
    )
