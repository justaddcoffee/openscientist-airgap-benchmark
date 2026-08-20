"""Gene-convergence figure for the OpenScientist air-gap benchmark site.

Source: gene-mentions.json — for each configuration, how many of its 10 reports name
each gene. Vocabulary is the dataset's own 33,091 gene symbols, so only genes actually
measured in the experiment can be counted. Regenerate the JSON with
extract_gene_mentions.py against the run directories.

Rows are grouped by function rather than ranked by frequency, so the block structure of
the acidification machinery is visible. Columns are model-major, each model's online and
air-gapped columns adjacent.
"""

import itertools
import json

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

mpl.rcParams.update({
    "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "figure.dpi": 200, "savefig.dpi": 200,
})

ORDER = [("Opus 4.8", "online"), ("Opus 4.8", "air-gapped"),
         ("Kimi K3", "online"), ("Kimi K3", "air-gapped"),
         ("GLM 5.2", "online"), ("GLM 5.2", "air-gapped")]

# Genes named by at least half the runs overall, grouped by the part of the machinery
# they belong to. Within a group, ordered by how many of the 60 reports name them.
GROUPS = [
    ("V-ATPase V1 sector",   ["ATP6V1B2", "ATP6V1G1", "ATP6V1C1", "ATP6V1H", "ATP6V1F", "ATP6V1E1"]),
    ("V-ATPase V0 sector",   ["ATP6V0B", "ATP6V0D1"]),
    ("V-ATPase assembly",    ["ATP6AP1", "ATP6AP2", "VMA21", "TMEM199"]),
    ("Ion channels",         ["CLCN7", "OSTM1", "TMEM175", "MCOLN1"]),
    ("Transcriptional\ncontrol", ["TFEB", "TFE3", "NFE2L2"]),
    ("Stress response",      ["ATF4", "DDIT3", "XBP1", "HSPA5"]),
    ("Lysosomal hydrolases\n+ membrane", ["LAMP1", "CTSB", "PSAP", "CTSD", "NPC1", "CTSF"]),
    ("Autophagy",            ["SQSTM1", "STX17", "MAP1LC3B", "SNAP29", "VAMP8", "GABARAP", "GABARAPL1"]),
    ("mTORC1 platform",      ["RRAGC", "RRAGA"]),
    ("Chaperone / ubiquitin", ["HSP90AA1", "UBC"]),
    ("Tau",                  ["MAPT"]),
]

counts = json.load(open("gene-mentions.json"))["counts"]
cols = [counts[f"{m}|{d}"] for m, d in ORDER]

genes = [g for _, gs in GROUPS for g in gs]
M = np.array([[c.get(g, 0) for c in cols] for g in genes], dtype=float)

fig, ax = plt.subplots(figsize=(6.4, 11.2))
im = ax.imshow(M, cmap="Blues", vmin=0, vmax=10, aspect="auto")
for i, j in itertools.product(range(len(genes)), range(6)):
    v = int(M[i, j])
    ax.text(j, i, v, ha="center", va="center", fontsize=7.4,
            color="white" if v >= 7 else "#333333")

ax.set_yticks(range(len(genes)))
ax.set_yticklabels(genes, fontsize=8)
ax.set_xticks(range(6))
ax.set_xticklabels(["on", "air", "on", "air", "on", "air"], fontsize=8)
for m, x in [("Claude Code\n+ Opus 4.8", 0.5), ("omp\n+ Kimi K3", 2.5), ("omp\n+ GLM 5.2", 4.5)]:
    ax.text(x, -0.85, m, ha="center", va="bottom", fontsize=8.4, fontweight="bold")
for x in (1.5, 3.5):                                   # separate the model blocks
    ax.axvline(x, color="white", lw=3.5)

row = 0                                                # group labels and separators
for name, gs in GROUPS:
    if row:
        ax.axhline(row - 0.5, color="white", lw=3.5)
    ax.text(-0.20, row + (len(gs) - 1) / 2, name, ha="right", va="center",
            fontsize=8.2, fontweight="bold", color="#222222", linespacing=1.25,
            transform=ax.get_yaxis_transform())   # x in axes fraction, clear of gene names
    row += len(gs)

ax.set_title("Reports naming each gene, out of 10 per configuration",
             loc="left", fontweight="bold", pad=44, x=-0.62)
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)

cb = fig.colorbar(im, ax=ax, fraction=0.030, pad=0.03)
cb.set_label("reports / 10", fontsize=8)
cb.ax.tick_params(labelsize=7.5)

fig.savefig("gene-convergence.png", bbox_inches="tight", facecolor="white")
print(f"wrote gene-convergence.png — {len(genes)} genes in {len(GROUPS)} groups")
