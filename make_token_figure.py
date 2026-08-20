"""Token-usage figure for the OpenScientist air-gap benchmark site.

Four buckets spanning five orders of magnitude (469 input vs 19.3M cache read), so
small multiples with a per-panel axis again, matching the run-statistics figure.

Online figures come from the app's cost_records table. Air-gapped figures were recovered
from agent container logs: in air-gapped mode the usage row is written alongside a cost
estimate that fetches a pricing table over the network, the firewall blocks it, and the
whole record fails to write.

Colour encodes config, fill encodes network mode — same scheme as the other figure.
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

# per run, mean of 10.  (title, online triple, air-gapped triple)
PANELS = [
    ("Input *",      [481, 322_518, 780_949],        [469, 380_144, 796_482]),
    ("Output",       [115_079, 113_776, 222_867],    [111_778, 109_177, 163_352]),
    ("Cache read",   [19_352_234, 5_949_713, 10_954_975],
                     [18_309_951, 5_324_243, 7_992_347]),
    ("Cache write *", [884_136, 0, 0],               [874_857, 0, 0]),
]


def fmt(v):
    if v == 0:
        return "0"
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v/1_000:.0f}k"
    return f"{v:g}"


fig, axes = plt.subplots(1, 4, figsize=(13.5, 3.9))
x = np.arange(3)
w = 0.38

for ax, (title, online, air) in zip(axes, PANELS):
    ax.bar(x - w/2, online, w, color=COLOR, edgecolor="white", linewidth=0.6)
    ax.bar(x + w/2, air, w, color="white", edgecolor=COLOR, linewidth=1.4, hatch="///")
    top = max(max(online), max(air))
    for xi, (o, a) in enumerate(zip(online, air)):
        ax.text(xi - w/2, o + top*0.02, fmt(o), ha="center", va="bottom", fontsize=7.2)
        ax.text(xi + w/2, a + top*0.02, fmt(a), ha="center", va="bottom", fontsize=7.2)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(CONFIGS, fontsize=7.4)
    ax.set_ylim(0, top * 1.25)
    ax.grid(axis="y", lw=0.4, color="#DDDDDD")
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", labelsize=7.5)

axes[0].set_ylabel("tokens per run")

fig.legend(handles=[Patch(facecolor="#888888", edgecolor="white", label="online"),
                    Patch(facecolor="white", edgecolor="#888888", hatch="///",
                          label="air-gapped")],
           frameon=False, ncol=2, loc="upper right", bbox_to_anchor=(0.995, 1.08),
           fontsize=9)
fig.suptitle("Token use per run, mean of 10 — note each panel has its own scale",
             x=0.008, ha="left", fontsize=11, fontweight="bold", y=1.06)
fig.text(0.008, -0.10,
         "* Input and cache write are not comparable across providers. Anthropic books first-occurrence prompt tokens as cache write; Fireworks has no cache-write meter and books the same tokens as input.\n"
         "Only the sum is comparable: 875k / 380k / 796k air-gapped. Token counts are also not comparable across models, which use different tokenizers.",
         ha="left", va="top", fontsize=7.3, color="#555555", linespacing=1.5)
fig.tight_layout()
fig.savefig("token-usage.png", bbox_inches="tight", facecolor="white")
print("wrote token-usage.png")
