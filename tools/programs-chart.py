#!/usr/bin/env python3
"""Draws the real-programs chart from tools/programs.json into index.html.

Writes an inline SVG between the markers <!-- programs-chart:start --> and <!-- programs-chart:end -->, so that the page's
light and dark tokens colour it and each row carries a hover title, followed by the table of the same numbers. Each bar is
how much faster CrucibleVM's binary ran than Oracle GraalVM's for the same program, without a profile and with one; a bar
to the left of the axis is a program where CrucibleVM was slower.

Usage: python3 tools/programs-chart.py   (from the repository root)
"""
import html
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "tools" / "programs.json").read_text())
PAGE = ROOT / "index.html"

LABEL_W = 178
PANEL_W = 262
GAP = 34
TOP = 44
ROW = 25
BAR_H = 13
LO, HI = -10.0, 70.0
TICKS = [0, 20, 40, 60]


def gain(p, k):
    """Per cent faster: Oracle's time over ours, less one."""
    return (p["or"][k] / p["cv"][k] - 1.0) * 100.0


def x_of(panel, v):
    x0 = LABEL_W + panel * (PANEL_W + GAP)
    return x0 + (max(LO, min(HI, v)) - LO) / (HI - LO) * PANEL_W


def signed(v):
    r = round(v)
    if r == 0:
        return "level"
    return ("+" if r > 0 else "−") + str(abs(r)) + "%"


def svg(programs):
    rows = sorted(programs, key=lambda p: (gain(p, 1), gain(p, 0)), reverse=True)
    height = TOP + ROW * len(rows) + 34
    width = LABEL_W + 2 * PANEL_W + GAP + 8
    out = [f'<svg class="programs-chart" viewBox="0 0 {width} {height}" role="img" aria-labelledby="programs-chart-title programs-chart-desc">',
           '<title id="programs-chart-title">How much faster CrucibleVM ran than Oracle GraalVM on 21 programs</title>',
           '<desc id="programs-chart-desc">Per cent faster for each program, without a profile on the left and with one on the right; '
           'bars to the left of the axis are programs where CrucibleVM was slower. The table below gives every time.</desc>']
    for panel, head in enumerate(("Without a profile", "With a profile")):
        x0 = LABEL_W + panel * (PANEL_W + GAP)
        out.append(f'<text class="pc-head" x="{x0}" y="16">{head}</text>')
        for t in TICKS:
            x = x_of(panel, t)
            cls = "pc-axis" if t == 0 else "pc-grid"
            out.append(f'<line class="{cls}" x1="{x:.1f}" x2="{x:.1f}" y1="{TOP - 10}" y2="{TOP + ROW * len(rows) - 4}"/>')
            label = "level" if t == 0 else f"+{t}%"
            out.append(f'<text class="pc-tick" x="{x:.1f}" y="{TOP + ROW * len(rows) + 14}" text-anchor="middle">{label}</text>')
        out.append(f'<text class="pc-tick" x="{x0}" y="{TOP - 16}">slower ←</text>')
        out.append(f'<text class="pc-tick" x="{x0 + PANEL_W}" y="{TOP - 16}" text-anchor="end">→ faster than Oracle</text>')
    for i, p in enumerate(rows):
        y = TOP + i * ROW
        tip = (f'{p["name"]}, {p["task"]}: Oracle GraalVM {p["or"][0]} s and {p["or"][1]} s with a profile, '
               f'CrucibleVM {p["cv"][0]} s and {p["cv"][1]} s')
        out.append(f'<g class="pc-row" style="--d:{i * 35}ms"><title>{html.escape(tip)}</title>')
        out.append(f'<rect class="pc-hit" x="0" y="{y - 4}" width="{width}" height="{ROW}"/>')
        out.append(f'<text class="pc-name" x="{LABEL_W - 12}" y="{y + BAR_H - 2}" text-anchor="end">{html.escape(p["name"])}</text>')
        for panel in (0, 1):
            v = gain(p, panel)
            xa, xb = x_of(panel, 0), x_of(panel, v)
            left, w = min(xa, xb), max(abs(xb - xa), 1.5)
            cls = "pc-win" if round(v) > 0 else "pc-loss" if round(v) < 0 else "pc-level"
            neg = " pc-neg" if v < 0 else ""
            out.append(f'<rect class="pc-bar {cls}{neg}" x="{left:.1f}" y="{y}" width="{w:.1f}" height="{BAR_H}" rx="3"/>')
            if v >= 0:
                out.append(f'<text class="pc-value" x="{xb + 6:.1f}" y="{y + BAR_H - 2}">{signed(v)}</text>')
            else:
                out.append(f'<text class="pc-value" x="{xb - 6:.1f}" y="{y + BAR_H - 2}" text-anchor="end">{signed(v)}</text>')
        out.append('</g>')
    out.append('</svg>')
    return "\n".join(out)


def table(programs):
    out = ['<details class="programs-table"><summary>Every time, in seconds</summary><div class="table-wrap"><table>',
           '<thead><tr><th scope="col">Program</th><th scope="col">What it does</th><th scope="col" class="num">Oracle</th>'
           '<th scope="col" class="num">CrucibleVM</th><th scope="col" class="num">Oracle, profile</th>'
           '<th scope="col" class="num">CrucibleVM, profile</th></tr></thead><tbody>']
    for p in programs:
        cells = "".join(f'<td class="num">{v}</td>' for v in (p["or"][0], p["cv"][0], p["or"][1], p["cv"][1]))
        out.append(f'<tr><td>{html.escape(p["name"])}</td><td>{html.escape(p["task"])}</td>{cells}</tr>')
    out.append('</tbody></table></div></details>')
    return "\n".join(out)


def summary(programs):
    parts = []
    for k in (0, 1):
        r = [p["or"][k] / p["cv"][k] for p in programs]
        geo = math.exp(sum(map(math.log, r)) / len(r))
        ahead = sum(round(gain(p, k)) > 0 for p in programs)
        behind = sum(round(gain(p, k)) < 0 for p in programs)
        parts.append((geo, ahead, behind))
    return parts


def main():
    programs = DATA["programs"]
    block = "\n".join(["<!-- programs-chart:start -->", '<figure class="programs-figure">', svg(programs), "</figure>", table(programs),
                       "<!-- programs-chart:end -->"])
    page = PAGE.read_text()
    pattern = re.compile(r"<!-- programs-chart:start -->.*?<!-- programs-chart:end -->", re.S)
    if not pattern.search(page):
        sys.exit("index.html has no programs-chart markers")
    PAGE.write_text(pattern.sub(lambda _: block, page))
    for label, (geo, ahead, behind) in zip(("without a profile", "with a profile"), summary(programs)):
        print(f"{label}: {geo:.3f}x Oracle's speed, ahead on {ahead}, behind on {behind} of {len(programs)}")


if __name__ == "__main__":
    main()
