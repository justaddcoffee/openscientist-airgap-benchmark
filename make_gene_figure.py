"""Gene-convergence figure for the OpenScientist air-gap benchmark site.

Source: gene-mentions.json, one entry per configuration, counting how many of that
configuration's 10 reports name each gene. Vocabulary is the dataset's own 33,091
gene symbols, so only genes actually measured in the experiment can be counted.
Regenerate with extract_gene_mentions.py against the run directories.

Columns are ordered model-major (each model's online and air-gapped columns adjacent)
so that mode-invariance is legible without reading the statistics: the two columns of
a pair look alike, while the pairs differ from each other.
"""

import collections
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

# label genes the dataset sorts cells by — naming them is bookkeeping, not a finding
EXCLUDE = {"MAP2"}
NTOP = 26
ORDER = [("Opus 4.8", "online"), ("Opus 4.8", "air-gapped"),
         ("Kimi K3", "online"), ("Kimi K3", "air-gapped"),
         ("GLM 5.2", "online"), ("GLM 5.2", "air-gapped")]

counts = json.load(open("gene-mentions.json"))["counts"]
cols = [counts[f"{m}|{d}"] for m, d in ORDER]

total = collections.Counter()
for c in cols:
    for g, n in c.items():
        if g not in EXCLUDE:
            total[g] += n
genes = [g for g, _ in total.most_common(NTOP)]
M = np.array([[c.get(g, 0) for c in cols] for g in genes], dtype=float)

fig = plt.figure(figsize=(11.5, 8.0))
gs = fig.add_gridspec(2, 2, width_ratios=[1.35, 1], height_ratios=[1, 1],
                      wspace=0.30, hspace=0.42)
ax = fig.add_subplot(gs[:, 0])

im = ax.imshow(M, cmap="Blues", vmin=0, vmax=10, aspect="auto")
for i, j in itertools.product(range(len(genes)), range(6)):
    v = int(M[i, j])
    ax.text(j, i, v, ha="center", va="center", fontsize=7.2,
            color="white" if v >= 7 else "#333333")
ax.set_yticks(range(len(genes)))
ax.set_yticklabels(genes, fontsize=7.8)
ax.set_xticks(range(6))
ax.set_xticklabels(["on", "air", "on", "air", "on", "air"], fontsize=7.8)
for k, (m, x) in enumerate([("Claude Code\n+ Opus 4.8", 0.5), ("omp\n+ Kimi K3", 2.5),
                            ("omp\n+ GLM 5.2", 4.5)]):
    ax.text(x, -0.85, m, ha="center", va="bottom", fontsize=8.2, fontweight="bold")
for x in (1.5, 3.5):                       # separate the model blocks
    ax.axvline(x, color="white", lw=3)
ax.set_title("Reports naming each gene, out of 10 per configuration",
             loc="left", fontweight="bold", pad=42)
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
cb.set_label("reports / 10", fontsize=8)
cb.ax.tick_params(labelsize=7.5)

# --- how widely is each gene shared? ------------------------------------------
ax2 = fig.add_subplot(gs[0, 1])
sets = {k: {g for g, n in v.items() if n >= 3 and g not in EXCLUDE} for k, v in counts.items()}
deg = collections.Counter(sum(g in s for s in sets.values())
                          for g in set().union(*sets.values()))
xs = list(range(1, 7))
ys = [deg[n] for n in xs]
bars = ax2.bar(xs, ys, 0.66, color=["#C6DBEF"] * 5 + ["#0072B2"], edgecolor="white")
for b, y in zip(bars, ys):
    ax2.text(b.get_x() + b.get_width() / 2, y, str(y), ha="center", va="bottom", fontsize=7.5)
ax2.set_xlabel("named by this many of the 6 configurations")
ax2.set_ylabel("genes")
ax2.set_ylim(0, max(ys) * 1.20)
ax2.set_title("Most genes are named by one configuration, not all six",
              loc="left", fontweight="bold")
ax2.grid(axis="y", lw=0.4, color="#DDDDDD")
ax2.set_axisbelow(True)

# --- what drives two configurations to agree? ---------------------------------
ax3 = fig.add_subplot(gs[1, 1])
groups = {"same model,\ndifferent mode": [], "same mode,\ndifferent model": [], "sharing\nneither": []}
for a, b in itertools.combinations(sets, 2):
    ma, da = a.split("|")
    mb, db = b.split("|")
    j = len(sets[a] & sets[b]) / len(sets[a] | sets[b])
    groups[list(groups)[0 if ma == mb else 1 if da == db else 2]].append(j)
names = list(groups)
means = [float(np.mean(groups[n])) for n in names]
bars = ax3.bar(range(3), means, 0.6, color=["#0072B2", "#BBBBBB", "#BBBBBB"], edgecolor="white")
for i, n in enumerate(names):                   # every pair, so the spread is visible
    ax3.scatter([i] * len(groups[n]), groups[n], s=13, color="#333333", zorder=3, alpha=0.75)
for b, m in zip(bars, means):
    ax3.text(b.get_x() + b.get_width() / 2, 0.02, f"{m:.2f}", ha="center", va="bottom",
             fontsize=8.5, color="white", fontweight="bold")
ax3.set_xticks(range(3))
ax3.set_xticklabels(names, fontsize=7.8)
ax3.set_ylabel("gene-set overlap (Jaccard)")
ax3.set_ylim(0, 0.68)
ax3.set_title("The model decides which genes; the network mode does not",
              loc="left", fontweight="bold")
ax3.grid(axis="y", lw=0.4, color="#DDDDDD")
ax3.set_axisbelow(True)

fig.savefig("gene-convergence.png", bbox_inches="tight", facecolor="white")
print(f"wrote gene-convergence.png — {len(genes)} genes, degree {dict(sorted(deg.items()))}")
print("jaccard:", {n: round(float(np.mean(groups[n])), 3) for n in names})
