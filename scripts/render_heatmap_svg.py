"""Render data/contributions.json as contrib-heatmap.svg: a 53-week grid that
drops in diagonally, line by line, then holds; a Less/More legend; and a
stats footer. 860px wide, the portrait and card's combined width.

    python scripts/render_heatmap_svg.py
"""
import json
from datetime import date, timedelta

from svgkit import CYAN, DIM, FG, GREEN, MONO, ROOT, window

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
W = 860
LEFT, RIGHT, TOP = 58, 26, 30 + 40
WEEKS = 53
PITCH = (W - LEFT - RIGHT) / WEEKS
CELL = PITCH - 3.2


def levels(counts):
    """GitHub-style: quantiles of the non-zero days, so one huge day can't wash out the rest."""
    nz = sorted(c for c in counts if c)
    if not nz:
        return lambda c: 0
    cuts = [nz[int(len(nz) * q)] for q in (0.25, 0.5, 0.75, 0.93)]
    return lambda c: 0 if c == 0 else 1 + sum(c > t for t in cuts)


def main():
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    days = [(date.fromisoformat(d["date"]), d["count"]) for d in data["days"]]
    end = days[-1][0]
    start = end - timedelta(days=end.isoweekday() % 7 + 7 * (WEEKS - 1))  # a Sunday, 53 columns back
    counts = {d: n for d, n in days if d >= start}
    level = levels(counts.values())

    cells, months, chars = [], [], ""
    last_month = None
    d = start
    while d <= end:
        week, dow = (d - start).days // 7, d.isoweekday() % 7
        x, y = LEFT + week * PITCH, TOP + dow * PITCH
        delay = (week + dow) * 0.017
        lv = level(counts.get(d, 0))
        cells.append(f'<rect class="c" x="{x:.1f}" y="{y:.1f}" width="{CELL:.1f}" height="{CELL:.1f}" rx="2.5" '
                     f'fill="{PALETTE[lv]}" style="animation-delay:{delay:.3f}s"><title>{counts.get(d, 0)} on {d:%b %d}</title></rect>')
        if dow == 0 and d.month != last_month and week < WEEKS - 2:
            last_month = d.month
            if week == 0 and d.day > 10:  # a stub of a month at the left edge: leave unlabelled
                d += timedelta(days=1)
                continue
            label = d.strftime("%b")
            chars += label
            months.append(f'<text x="{x:.1f}" y="{TOP - 10}" fill="{DIM}">{label}</text>')
        d += timedelta(days=1)

    for dow, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        chars += label
        months.append(f'<text x="{LEFT - 10}" y="{TOP + dow * PITCH + CELL - 1.5:.1f}" text-anchor="end" fill="{DIM}">{label}</text>')

    grid_bottom = TOP + 7 * PITCH
    legend_y = grid_bottom + 14
    lx = W - RIGHT - 5 * PITCH - 40
    legend = [f'<text x="{lx - 8:.1f}" y="{legend_y + CELL - 1.5:.1f}" text-anchor="end" fill="{DIM}">Less</text>']
    for i, c in enumerate(PALETTE[1:]):
        legend.append(f'<rect x="{lx + i * PITCH:.1f}" y="{legend_y:.1f}" width="{CELL:.1f}" height="{CELL:.1f}" rx="2.5" fill="{c}"/>')
    legend.append(f'<text x="{lx + 5 * PITCH + 4:.1f}" y="{legend_y + CELL - 1.5:.1f}" fill="{DIM}">More</text>')
    chars += "LessMore"

    best = data["best_day"]
    best_d = date.fromisoformat(best["date"])
    total = f'{data["total"]:,}'
    stats = [("contributions in the last year", total), ("longest streak", f'{data["longest_streak"]} days'),
             ("current streak", f'{data["current_streak"]} days'), ("best day", f'{best["count"]} · {best_d:%b %d}')]
    sy = legend_y + CELL - 1.5
    footer = (f'<text x="{LEFT}" y="{sy:.1f}"><tspan fill="{GREEN}" font-weight="700">{total}</tspan>'
              f'<tspan fill="{FG}"> contributions in the last year</tspan></text>')
    line2 = "   ".join(f"{k} {v}" for k, v in stats[1:])
    footer += (f'<text x="{LEFT}" y="{sy + 22:.1f}" xml:space="preserve">' +
               "<tspan>   </tspan>".join(f'<tspan fill="{DIM}">{k} </tspan><tspan fill="{CYAN}">{v}</tspan>' for k, v in stats[1:]) +
               "</text>")
    chars += total + " contributions in the last year" + line2

    h = round(sy + 22 + 22)
    style = ("@keyframes drop{from{opacity:0;transform:translateY(-7px)}to{opacity:1;transform:translateY(0)}}"
             ".c{opacity:0;animation:drop .45s ease-out forwards;transform-box:fill-box}")
    body = (f'<g font-family="{MONO}" font-size="10.5">{"".join(months)}</g>'
            f'<g>{"".join(cells)}</g>'
            f'<g font-family="{MONO}" font-size="10.5">{"".join(legend)}</g>'
            f'<g font-family="{MONO}" font-size="12">{footer}</g>')
    svg = window(W, h, "~/contributions --last-year", body, chars,
                 f"{total} contributions in the last year; longest streak {data['longest_streak']} days", style)
    (ROOT / "contrib-heatmap.svg").write_text(svg)
    print(f"wrote contrib-heatmap.svg  {W}x{h}px, {len(svg)/1024:.0f} KB")


if __name__ == "__main__":
    main()
