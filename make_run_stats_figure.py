"""Run-statistics figure for the OpenScientist air-gap benchmark site.

Six metrics span very different scales (11 literature searches vs 191 tool calls),
so this is small multiples with a per-panel axis rather than one grouped chart on a
shared or log axis — the comparison that matters is within a metric, across configs.

Colour encodes the config (Okabe-Ito, colourblind-safe, fixed order). Fill encodes the
network mode: solid = online, hatched = air-gapped. Colour is never used for mode, so
the two encodings cannot be confused.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

mpl.rcParams.update({
    "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 200, "savefig.dpi": 200,
})

CONFIGS = ["Claude Code\n+ Opus 4.8", "omp\n+ Kimi K3", "omp\n+ GLM 5.2"]
COLOR = ["#0072B2", "#E69F00", "#009E73"]

# (title, unit, online triple, air-gapped triple) — means over 10 runs each
PANELS = [
    ("Runtime",             "minutes", [35.5, 48.2, 80.5], [33.9, 42.1, 67.6]),
    ("Tool calls",          "per run", [83.7, 130.0, 191.0], [81.7, 106.2, 142.6]),
    ("execute_code calls",  "per run", [28.4, 37.0, 57.5], [29.1, 32.8, 48.4]),
    ("Literature searches", "per run", [11.0, 17.8, 36.7], [11.0, 12.9, 22.0]),
    ("Papers cited",        "per run", [7.3, 14.5, 31.9], [7.8, 18.6, 26.9]),
    ("Findings recorded",   "per run", [12.4, 16.8, 24.2], [12.4, 15.2, 19.2]),
]

fig, axes = plt.subplots(2, 3, figsize=(11.5, 6.2))
x = np.arange(3)
w = 0.38

for ax, (title, unit, online, air) in zip(axes.ravel(), PANELS):
    ax.bar(x - w / 2, online, w, color=COLOR, edgecolor="white", linewidth=0.6)
    ax.bar(x + w / 2, air, w, color="white", edgecolor=COLOR, linewidth=1.4, hatch="///")
    for xi, (o, a) in enumerate(zip(online, air)):
        ax.text(xi - w / 2, o, f"{o:g}", ha="center", va="bottom", fontsize=7.5)
        ax.text(xi + w / 2, a, f"{a:g}", ha="center", va="bottom", fontsize=7.5)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_ylabel(unit)
    ax.set_xticks(x)
    ax.set_xticklabels(CONFIGS, fontsize=7.8)
    ax.set_ylim(0, max(max(online), max(air)) * 1.22)
    ax.grid(axis="y", lw=0.4, color="#DDDDDD")
    ax.set_axisbelow(True)

fig.legend(handles=[Patch(facecolor="#888888", edgecolor="white", label="online"),
                    Patch(facecolor="white", edgecolor="#888888", hatch="///",
                          label="air-gapped")],
           frameon=False, ncol=2, loc="upper right", bbox_to_anchor=(0.995, 1.045),
           fontsize=9)
fig.suptitle("Per-run means over 10 runs per configuration",
             x=0.008, ha="left", fontsize=11, fontweight="bold", y=1.03)
fig.tight_layout(rect=[0, 0, 1, 0.98])
fig.savefig("run-statistics.png", bbox_inches="tight", facecolor="white")
print("wrote run-statistics.png")
