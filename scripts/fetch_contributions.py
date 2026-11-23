"""Fetch the public contribution calendar for one or more accounts and merge
them day by day into data/contributions.json. No token: this is the same HTML
fragment a GitHub profile page loads.

    CONTRIB_USERS="Astro-Dude,other" python scripts/fetch_contributions.py
"""
import json
import os
import re
from collections import defaultdict
from datetime import date, timedelta

import requests

from svgkit import ROOT

CELL = re.compile(r'<td[^>]*data-date="(\d{4}-\d{2}-\d{2})"[^>]*id="(contribution-day-component-[\d-]+)"')
TIP = re.compile(r'<tool-tip[^>]*for="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)</tool-tip>')


def fetch(user):
    r = requests.get(f"https://github.com/users/{user}/contributions",
                     headers={"User-Agent": "profile-art"}, timeout=30)
    r.raise_for_status()
    tips = dict(TIP.findall(r.text))
    days = {}
    for day, cid in CELL.findall(r.text):
        m = re.match(r"(\d+) contribution", tips.get(cid, ""))
        days[day] = int(m.group(1)) if m else 0
    if not days:
        raise SystemExit(f"no calendar cells found for {user}; GitHub's markup may have changed")
    return days


def streaks(days):
    longest = run = 0
    for _, n in days:
        run = run + 1 if n else 0
        longest = max(longest, run)
    current = 0
    for i, (_, n) in enumerate(reversed(days)):
        if n:
            current += 1
        elif i:  # today may simply not have started yet
            break
    return current, longest


def main():
    users = [u.strip() for u in os.environ.get("CONTRIB_USERS", "Astro-Dude").split(",") if u.strip()]
    merged = defaultdict(int)
    for user in users:
        for day, n in fetch(user).items():
            merged[day] += n
    days = sorted(merged.items())
    current, longest = streaks(days)
    best = max(days, key=lambda d: d[1])
    months = defaultdict(int)
    for day, n in days:
        months[day[:7]] += n
    out = {
        "generated": date.today().isoformat(),
        "accounts": len(users),
        "total": sum(n for _, n in days),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best[0], "count": best[1]},
        "months": dict(months),
        "days": [{"date": d, "count": n} for d, n in days],
    }
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "contributions.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"{out['total']} contributions over {len(days)} days from {len(users)} account(s); "
          f"streak {current} (longest {longest}); best {best[1]} on {best[0]}")


if __name__ == "__main__":
    main()
