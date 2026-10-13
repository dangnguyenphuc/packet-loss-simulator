"""
Box-plot comparison of the app's own reported neteqScore, PLC-off vs
PLC-on, pooled across every network condition tested.

Each pulled result folder's .txt file now has the app's own final score
written directly as a `Neteq: X.XXXXX` line (see
task_runner.py/read_neteq_score() and ConfigAndRun.vue's retest-on-0
logic) — this script just reads that number, no reconstruction or
simulation involved (unlike neteq_eval.py, which replays per-op mode
sequences for the older log format). A score of exactly 0 is treated as
a bad pull, not a real worst-case result, and excluded here too, for the
same reason ConfigAndRun.vue now retests on it — see module docstring
there.

"Pooled across every network condition" means each box plot's population
is every (network, loss, rtt) combo tested for that PLC state, combined
into one distribution — this deliberately does NOT break results out by
condition; that's what neteq_eval.py's print_report() is for.

Usage:
    python3 boxplot_neteq.py [root_dir ...] [--out boxplot_neteq.html]

    root_dir defaults to neteq_eval.py's DEFAULT_ROOTS (both
    /home/dangnp/workspace/tmp/audio and
    frontend/loss-simulator/public/audio).
"""

import argparse
import json
import os
import sys

from neteq_eval import FOLDER_PATTERN, DEFAULT_ROOTS

MAX_SCORE = 5.0


def read_direct_score(path):
    """Parse the app's own `Neteq: X.XXXXX` line. Returns None if absent/unparseable."""
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line.lower().startswith("neteq:"):
                    return float(line.split(":", 1)[1].strip())
    except (OSError, ValueError):
        pass
    return None


def collect(roots):
    """Walk roots for result folders, returning (points, excluded_zero, excluded_missing)."""
    points = []
    excluded_zero = 0
    excluded_missing = 0

    for root in roots:
        if not os.path.isdir(root):
            continue
        for name in sorted(os.listdir(root)):
            folder = os.path.join(root, name)
            if not os.path.isdir(folder):
                continue
            match = FOLDER_PATTERN.match(name)
            if not match:
                continue

            txt_files = [f for f in os.listdir(folder) if f.endswith(".txt")]
            score = None
            for txt in txt_files:
                score = read_direct_score(os.path.join(folder, txt))
                if score is not None:
                    break

            if score is None:
                excluded_missing += 1
                continue
            if score == 0:
                excluded_zero += 1
                continue

            info = match.groupdict()
            points.append({
                "folder": name,
                "plc": match.group("plc") == "plc",
                "network": info["network"] or "",
                "loss": info["loss"] or "",
                "rtt": info["rtt"] or "",
                "score": round(score, 5),
            })

    return points, excluded_zero, excluded_missing


def box_stats(values):
    """Quartiles via linear interpolation, outliers via Tukey's 1.5*IQR rule."""
    if not values:
        return None
    xs = sorted(values)
    n = len(xs)

    def percentile(p):
        idx = p * (n - 1)
        lo = int(idx)
        hi = min(lo + 1, n - 1)
        frac = idx - lo
        return xs[lo] + (xs[hi] - xs[lo]) * frac

    q1, med, q3 = percentile(0.25), percentile(0.5), percentile(0.75)
    iqr = q3 - q1
    lo_fence, hi_fence = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    inliers = [x for x in xs if lo_fence <= x <= hi_fence]
    outliers = [x for x in xs if x < lo_fence or x > hi_fence]

    return {
        "n": n,
        "min": xs[0],
        "max": xs[-1],
        "mean": sum(xs) / n,
        "q1": q1,
        "median": med,
        "q3": q3,
        "whisker_lo": min(inliers) if inliers else xs[0],
        "whisker_hi": max(inliers) if inliers else xs[-1],
        "outliers": outliers,
    }


def generate_html(off_points, plc_points, off_stats, plc_stats, out_path):
    data = {
        "off": {"points": off_points, "stats": off_stats},
        "plc": {"points": plc_points, "stats": plc_stats},
    }
    html = _HTML_TEMPLATE.replace("__DATA_JSON__", json.dumps(data))
    with open(out_path, "w") as f:
        f.write(html)


_HTML_TEMPLATE = r"""<title>NetEq Score: Normal vs PLC</title>
<style>
  .viz-root {
    color-scheme: light;
    --surface-1:      #fcfcfb;
    --surface-2:       #f5f4f1;
    --border:          #e2e0da;
    --text-primary:    #0b0b0b;
    --text-secondary:  #52514e;
    --text-muted:      #83817a;
    --series-off:      #2a78d6;
    --series-plc:      #eb6834;
  }
  @media (prefers-color-scheme: dark) {
    :root:where(:not([data-theme="light"])) .viz-root {
      color-scheme: dark;
      --surface-1:      #1a1a19;
      --surface-2:       #232320;
      --border:          #3a3935;
      --text-primary:    #ffffff;
      --text-secondary:  #c3c2b7;
      --text-muted:      #8f8d85;
      --series-off:      #3987e5;
      --series-plc:      #d95926;
    }
  }
  :root[data-theme="dark"] .viz-root {
    color-scheme: dark;
    --surface-1:      #1a1a19;
    --surface-2:       #232320;
    --border:          #3a3935;
    --text-primary:    #ffffff;
    --text-secondary:  #c3c2b7;
    --text-muted:      #8f8d85;
    --series-off:      #3987e5;
    --series-plc:      #d95926;
  }

  .viz-root {
    background: var(--surface-1);
    color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    padding: 32px 24px 48px;
    max-width: 900px;
    margin: 0 auto;
    box-sizing: border-box;
  }
  h1 { font-size: 20px; font-weight: 650; margin: 0 0 4px; }
  .subtitle { color: var(--text-secondary); font-size: 13px; margin: 0 0 28px; }
  .empty-note {
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: 8px; padding: 16px; color: var(--text-secondary); font-size: 13px;
  }
  .legend { display: flex; gap: 20px; margin-bottom: 12px; font-size: 13px; color: var(--text-secondary); }
  .legend-item { display: flex; align-items: center; gap: 6px; }
  .legend-swatch { width: 10px; height: 10px; border-radius: 2px; }
  .chart-wrap { overflow-x: auto; }
  svg { display: block; }
  .axis-label { fill: var(--text-muted); font-size: 11px; }
  .grid-line { stroke: var(--border); stroke-width: 1; }
  .box-fill { fill-opacity: 0.18; }
  .median-line { stroke-width: 2.5; }
  .whisker { stroke-width: 1.5; }
  .outlier-dot { cursor: pointer; }
  .cat-label { fill: var(--text-primary); font-size: 13px; font-weight: 600; text-anchor: middle; }
  .n-label { fill: var(--text-muted); font-size: 11px; text-anchor: middle; }

  table.stats { width: 100%; border-collapse: collapse; margin-top: 28px; font-size: 13px; }
  table.stats th, table.stats td { text-align: right; padding: 6px 10px; border-bottom: 1px solid var(--border); }
  table.stats th:first-child, table.stats td:first-child { text-align: left; }
  table.stats th { color: var(--text-secondary); font-weight: 600; }

  #tooltip {
    position: fixed; pointer-events: none; z-index: 10;
    background: var(--surface-2); border: 1px solid var(--border); border-radius: 6px;
    padding: 8px 10px; font-size: 12px; color: var(--text-primary);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    opacity: 0; transition: opacity 0.1s;
    max-width: 240px;
  }
  #tooltip.visible { opacity: 1; }
  #tooltip .tt-row { display: flex; justify-content: space-between; gap: 12px; }
  #tooltip .tt-key { color: var(--text-muted); }
</style>

<div class="viz-root">
  <h1>NetEq score: Normal vs PLC</h1>
  <p class="subtitle">App-reported neteqScore, pooled across every network condition tested</p>
  <div id="content"></div>
  <div id="tooltip"></div>
</div>

<script>
const DATA = __DATA_JSON__;

function fmt(v) { return v === null || v === undefined ? "–" : v.toFixed(3); }

function render() {
  const content = document.getElementById("content");
  const groups = [
    { key: "off", label: "Normal (PLC off)", color: "var(--series-off)" },
    { key: "plc", label: "PLC on", color: "var(--series-plc)" },
  ];

  const hasData = groups.some(g => DATA[g.key].stats);
  if (!hasData) {
    content.innerHTML = '<div class="empty-note">No pulled results with a valid (non-zero) neteqScore found yet. Run boxplot_neteq.py again once tests have completed.</div>';
    return;
  }

  const legend = document.createElement("div");
  legend.className = "legend";
  legend.innerHTML = groups.map(g =>
    `<div class="legend-item"><span class="legend-swatch" style="background:${g.color}"></span>${g.label} (n=${DATA[g.key].stats ? DATA[g.key].stats.n : 0})</div>`
  ).join("");
  content.appendChild(legend);

  const wrap = document.createElement("div");
  wrap.className = "chart-wrap";
  content.appendChild(wrap);

  const W = 820, H = 420;
  const marginL = 50, marginR = 30, marginT = 20, marginB = 50;
  const plotW = W - marginL - marginR, plotH = H - marginT - marginB;
  const yMax = 5, yMin = 0;
  const yToPx = (v) => marginT + plotH * (1 - (v - yMin) / (yMax - yMin));

  const boxWidth = 140;
  const slotW = plotW / groups.length;

  let svg = `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" xmlns="http://www.w3.org/2000/svg">`;

  for (let t = 0; t <= 5; t++) {
    const y = yToPx(t);
    svg += `<line class="grid-line" x1="${marginL}" x2="${W - marginR}" y1="${y}" y2="${y}" />`;
    svg += `<text class="axis-label" x="${marginL - 10}" y="${y + 4}" text-anchor="end">${t}</text>`;
  }

  groups.forEach((g, i) => {
    const stats = DATA[g.key].stats;
    const cx = marginL + slotW * (i + 0.5);
    svg += `<text class="cat-label" x="${cx}" y="${H - 26}">${g.label}</text>`;
    if (!stats) {
      svg += `<text class="n-label" x="${cx}" y="${H - 10}">no data</text>`;
      return;
    }
    svg += `<text class="n-label" x="${cx}" y="${H - 10}">n=${stats.n}</text>`;

    const x0 = cx - boxWidth / 2, x1 = cx + boxWidth / 2;
    const yQ1 = yToPx(stats.q1), yQ3 = yToPx(stats.q3), yMed = yToPx(stats.median);
    const yWLo = yToPx(stats.whisker_lo), yWHi = yToPx(stats.whisker_hi);

    svg += `<line class="whisker" x1="${cx}" x2="${cx}" y1="${yWHi}" y2="${yQ3}" stroke="${g.color}" />`;
    svg += `<line class="whisker" x1="${cx}" x2="${cx}" y1="${yQ1}" y2="${yWLo}" stroke="${g.color}" />`;
    svg += `<line class="whisker" x1="${x0 + boxWidth * 0.25}" x2="${x1 - boxWidth * 0.25}" y1="${yWHi}" y2="${yWHi}" stroke="${g.color}" />`;
    svg += `<line class="whisker" x1="${x0 + boxWidth * 0.25}" x2="${x1 - boxWidth * 0.25}" y1="${yWLo}" y2="${yWLo}" stroke="${g.color}" />`;

    svg += `<rect class="box-fill" x="${x0}" y="${yQ3}" width="${boxWidth}" height="${yQ1 - yQ3}" fill="${g.color}" stroke="${g.color}" stroke-width="1.5" rx="3" data-tooltip-idx="${i}" data-tooltip-type="box" />`;
    svg += `<line class="median-line" x1="${x0}" x2="${x1}" y1="${yMed}" y2="${yMed}" stroke="${g.color}" />`;

    stats.outliers.forEach((v, oi) => {
      const jitter = ((oi % 5) - 2) * 6;
      svg += `<circle class="outlier-dot" cx="${cx + jitter}" cy="${yToPx(v)}" r="3.5" fill="${g.color}" stroke="var(--surface-1)" stroke-width="1" data-tooltip-type="outlier" data-tooltip-group="${g.key}" data-tooltip-value="${v}" />`;
    });
  });

  svg += `</svg>`;
  wrap.innerHTML = svg;

  const tooltip = document.getElementById("tooltip");
  wrap.querySelectorAll("[data-tooltip-type]").forEach(el => {
    el.addEventListener("mousemove", (e) => {
      const type = el.getAttribute("data-tooltip-type");
      let html = "";
      if (type === "box") {
        const g = groups[+el.getAttribute("data-tooltip-idx")];
        const s = DATA[g.key].stats;
        html = `<div style="font-weight:600;margin-bottom:4px">${g.label}</div>` +
          [["n", s.n], ["mean", fmt(s.mean)], ["min", fmt(s.min)], ["q1", fmt(s.q1)],
           ["median", fmt(s.median)], ["q3", fmt(s.q3)], ["max", fmt(s.max)]]
          .map(([k, v]) => `<div class="tt-row"><span class="tt-key">${k}</span><span>${v}</span></div>`).join("");
      } else {
        const groupKey = el.getAttribute("data-tooltip-group");
        const val = +el.getAttribute("data-tooltip-value");
        const pt = DATA[groupKey].points.find(p => Math.abs(p.score - val) < 1e-6);
        html = `<div style="font-weight:600;margin-bottom:4px">outlier: ${fmt(val)}</div>` +
          (pt ? [["network", pt.network || "–"], ["loss", pt.loss], ["rtt", pt.rtt]]
            .map(([k, v]) => `<div class="tt-row"><span class="tt-key">${k}</span><span>${v}</span></div>`).join("") : "");
      }
      tooltip.innerHTML = html;
      tooltip.classList.add("visible");
      tooltip.style.left = (e.clientX + 14) + "px";
      tooltip.style.top = (e.clientY + 14) + "px";
    });
    el.addEventListener("mouseleave", () => tooltip.classList.remove("visible"));
  });

  const table = document.createElement("table");
  table.className = "stats";
  table.innerHTML = `<thead><tr><th>group</th><th>n</th><th>mean</th><th>min</th><th>q1</th><th>median</th><th>q3</th><th>max</th></tr></thead>` +
    "<tbody>" + groups.map(g => {
      const s = DATA[g.key].stats;
      if (!s) return `<tr><td>${g.label}</td><td colspan="7">no data</td></tr>`;
      return `<tr><td>${g.label}</td><td>${s.n}</td><td>${fmt(s.mean)}</td><td>${fmt(s.min)}</td><td>${fmt(s.q1)}</td><td>${fmt(s.median)}</td><td>${fmt(s.q3)}</td><td>${fmt(s.max)}</td></tr>`;
    }).join("") + "</tbody>";
  content.appendChild(table);
}

render();
</script>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root_dir", nargs="*", help="Folder(s) to scan. Default: neteq_eval.py's DEFAULT_ROOTS.")
    parser.add_argument("--out", default="boxplot_neteq.html", help="Output HTML path (default: boxplot_neteq.html)")
    args = parser.parse_args()

    roots = args.root_dir if args.root_dir else DEFAULT_ROOTS
    points, excluded_zero, excluded_missing = collect(roots)

    off_points = [p for p in points if not p["plc"]]
    plc_points = [p for p in points if p["plc"]]
    off_stats = box_stats([p["score"] for p in off_points])
    plc_stats = box_stats([p["score"] for p in plc_points])

    generate_html(off_points, plc_points, off_stats, plc_stats, args.out)

    print(f"off: {len(off_points)} results" + (f", median={off_stats['median']:.3f}" if off_stats else ""))
    print(f"plc: {len(plc_points)} results" + (f", median={plc_stats['median']:.3f}" if plc_stats else ""))
    print(f"excluded: {excluded_zero} zero-score, {excluded_missing} missing/unparseable")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
