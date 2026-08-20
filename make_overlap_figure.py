"""Gene-set overlap by pair type — does the model or the network mode decide?

Each configuration's gene set is the genes named by at least 3 of its 10 runs. Every
pair of the 6 configurations is scored by Jaccard overlap, then grouped by what the two
members share. Comparing pair types rather than absolute overlap is what makes this
readable: independent runs are not expected to name identical genes, so the baseline
is whatever "sharing nothing" scores — the question is which factor beats it.
"""

import itertools
import json

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

mpl.rcParams.update({
    "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 200, "savefig.dpi": 200,
})

EXCLUDE = {"MAP2"}          # a label the dataset sorts on, not a finding
THRESHOLD = 3               # runs out of 10 for a gene to count as part of a config's set

counts = json.load(open("gene-mentions.json"))["counts"]
sets = {k: {g for g, n in v.items() if n >= THRESHOLD and g not in EXCLUDE}
        for k, v in counts.items()}

LABELS = ["same model,\ndifferent network mode", "same network mode,\ndifferent model",
          "sharing\nneither"]
groups = {name: [] for name in LABELS}
for a, b in itertools.combinations(sets, 2):
    (model_a, mode_a), (model_b, mode_b) = (x.split("|") for x in (a, b))
    which = 0 if model_a == model_b else 1 if mode_a == mode_b else 2
    groups[LABELS[which]].append(len(sets[a] & sets[b]) / len(sets[a] | sets[b]))

fig, ax = plt.subplots(figsize=(5.6, 3.5))
means = [float(np.mean(groups[n])) for n in LABELS]
bars = ax.bar(range(3), means, 0.62, color=["#0072B2", "#BBBBBB", "#BBBBBB"],
              edgecolor="white")
for i, name in enumerate(LABELS):            # every pair, so the spread is visible
    ax.scatter([i] * len(groups[name]), groups[name], s=16, color="#333333",
               zorder=3, alpha=0.8)
for b, m in zip(bars, means):
    ax.text(b.get_x() + b.get_width() / 2, 0.022, f"{m:.2f}", ha="center", va="bottom",
            fontsize=10, color="white", fontweight="bold")

ax.set_xticks(range(3))
ax.set_xticklabels(LABELS, fontsize=8)
ax.set_ylabel("gene-set overlap (Jaccard)")
ax.set_ylim(0, 0.68)
ax.set_title("The model decides which genes get analysed;\nthe network mode does not",
             loc="left", fontweight="bold")
ax.grid(axis="y", lw=0.4, color="#DDDDDD")
ax.set_axisbelow(True)
fig.text(0.0, -0.12, "One dot per pair of configurations, all 15 shown. A configuration's gene "
         "set is the genes named by\nat least 3 of its 10 runs.", ha="left", va="top",
         fontsize=7.4, color="#555555", linespacing=1.5)

fig.savefig("gene-overlap.png", bbox_inches="tight", facecolor="white")
print({n: round(float(np.mean(groups[n])), 3) for n in LABELS},
      "pairs:", {n: len(groups[n]) for n in LABELS})
