"""Per-configuration gene-mention counts across the 60 benchmark reports.

Vocabulary is the dataset's own var_names (33,091 symbols), so a token only counts
if it is a gene actually measured in the experiment. Reports are the unit: a gene
either appears in a run's final report or it does not, regardless of how often.
"""
import collections, json, pathlib, re, sys
import h5py

H5 = "data/OteroGarcia_excitatory_subset.h5ad"
LBL = {"claude-opus-4-8": "Opus 4.8", "FW-Kimi-K3": "Kimi K3", "FW-GLM-5.2": "GLM 5.2"}
# markers the dataset labels cells by; naming them is bookkeeping, not a finding
EXCLUDE = {"CUX2", "LAMP5", "COL5A2", "RORB", "THEMIS", "FEZF2", "SLC17A7", "GAD1", "GAD2"}

with h5py.File(H5, "r") as f:
    node = f["var/feature_name/categories"]  # _index holds Ensembl IDs; symbols live here
    vocab = {v.decode() if isinstance(v, bytes) else str(v) for v in node[:]}
vocab = {g for g in vocab if re.fullmatch(r"[A-Z][A-Z0-9]{1,9}(-[A-Z0-9]+)?", g)} - EXCLUDE

def load(p):
    return [json.loads(l) for l in pathlib.Path(p).read_text().splitlines() if l.strip()]

sets = {"air-gapped": load("notes/benchmark-3-agents/RUNS.jsonl"),
        "online":     load("notes/benchmark-3-agents/RUNS-online.jsonl")}

TOKEN = re.compile(r"\b[A-Z][A-Z0-9]{1,9}(?:-[A-Z0-9]+)?\b")
counts = collections.defaultdict(collections.Counter)   # (model, mode) -> gene -> n reports
n_runs = collections.Counter()

for mode, rows in sets.items():
    for r in rows:
        f = pathlib.Path("jobs") / r["job_id"] / "final_report.md"
        if not f.exists():
            continue
        key = (LBL[r["model"]], mode)
        n_runs[key] += 1
        for g in {t for t in TOKEN.findall(f.read_text(errors="ignore")) if t in vocab}:
            counts[key][g] += 1

out = {"n_runs": {f"{m}|{d}": n for (m, d), n in n_runs.items()},
       "counts": {f"{m}|{d}": dict(c) for (m, d), c in counts.items()}}
pathlib.Path("notes/benchmark-3-agents/gene-mentions.json").write_text(json.dumps(out, indent=1))
print("runs:", dict(out["n_runs"]))
print("distinct genes per config:", {k: len(v) for k, v in out["counts"].items()})
