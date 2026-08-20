## What this is

Sixty autonomous runs of one question, through [OpenScientist](https://openscientist.io).

The question came from Mathieu Bourdenx, verbatim:

> This is a single soma transcriptomic dataset of tangle-bearing and tangle-free neurons. Compare healthy to diseased neurons to investigate how is the proteostasis network rewired with the appearance of tau pathology. Investigate in particular if lysosomal acidification is changing.

The data is `OteroGarcia_excitatory_subset.h5ad` — 22,492 single neurons × 33,091 genes from 8 Braak VI donors, split by `obs.SORT` into **AT8** (tangle-bearing, 13,864) and **MAP2** (tangle-free, 8,628). Note there is no non-AD control arm: "healthy" means tangle-free *within* end-stage disease.

Two variables, 10 repeats each:

- **Three model/harness pairs** — Claude Code + Opus 4.8, omp + Kimi K3, omp + GLM 5.2
- **Two network modes** — online, and fully **air-gapped**: nftables `policy drop`, DNS narrowed to the container's own resolver, egress only to a local LLM proxy and execution broker, and literature served from a local 40M-article MEDLINE mirror instead of NCBI

Every run got 10 iterations. All 60 completed. No failures.

---

## 1. What it cost to run

Per run, averaged over 10.

| | Opus 4.8 | Kimi K3 | GLM 5.2 |
|---|---|---|---|
| **runtime** — online | 35.5 min | 48.2 min | 80.5 min |
| **runtime** — air-gapped | **33.9 min** | **42.1 min** | **67.6 min** |
| tool calls | 84 | 106–130 | 143–191 |
| `execute_code` calls | 29 | 33–37 | 48–58 |
| literature searches | 11 | 13–18 | 22–37 |
| papers cited | 7–8 | 15–19 | 27–32 |

**Air-gapped is faster** — 5% to 16% — for all three. The likely cause is unglamorous: a local Postgres full-text index answers in 0.05–0.4 s where NCBI round-trips take seconds, and these runs make 11–37 literature calls each.

### Tokens

Per run, air-gapped. The five buckets are non-overlapping.

| | input | output | cache read | cache write |
|---|---|---|---|---|
| Opus 4.8 | 469 | 111,778 | **18,309,951** | 874,857 |
| Kimi K3 | 380,144 | 109,177 | 5,324,243 | 0 |
| GLM 5.2 | 796,482 | 163,352 | 7,992,347 | 0 |

Cache reads dominate everything — an agent loop re-sends its whole conversation each turn. For Opus that's 94% of all tokens.

Two things make the raw counts non-comparable across models. Each uses a **different tokenizer**. And Anthropic books first-occurrence prompt tokens as *cache write* while Fireworks has no cache-write meter and books them as *input* — so Opus's tiny input figure is an accounting convention, not efficiency. Add input + cache write and the three are 875k / 380k / 796k.

### Cost

| | online | air-gapped |
|---|---|---|
| Opus 4.8 | $8.48 | **$8.18** |
| Kimi K3 | $4.91 | **$4.81** |
| GLM 5.2 | $3.92 | **$3.22** |

Opus is shown at rates implied by settled Azure billing, which came in at roughly **a third of Anthropic's list price for the cache buckets** — at list it would read $17–18. GLM's rates are Azure's own published prices. **Kimi has no Azure meter at all** and has so far been billed **$0**; its figure uses Fireworks' list price ×1.1 for the DataZone premium, and should be read as what it will cost once Azure prices it.

---

## 2. What the science looked like

Three criteria, taken from the three clauses of the question. Every one of the 60 reports met all three.

| | criterion | online | air-gapped |
|---|---|---|---|
| **C1** | compares AT8 (tangle-bearing) vs MAP2 (tangle-free) | 30/30 | 30/30 |
| **C2** | characterises proteostasis-network rewiring | 30/30 | 30/30 |
| **C3** | addresses lysosomal acidification specifically | 30/30 | 30/30 |
| | FDR / multiple-testing handled | 28/30 | 29/30 |
| | donor-aware (paired or pseudobulk over 8 donors) | 30/30 | 30/30 |
| | falsely claims a control-vs-AD contrast | **0/30** | **0/30** |

That last row matters. The dataset cannot support a comparison against healthy brain — every cell is Braak VI. No run claimed one.

### The genes

Symbols by how many of the 60 independent reports name them. Cell-type markers from the dataset's own labels (`CUX2`, `LAMP5`, `COL5A2`) are excluded.

| system | genes | reports |
|---|---|---|
| **V-ATPase pump + assembly** | ATP6V1B2, ATP6AP1, ATP6AP2, ATP6V1G1, ATP6V1C1, **ATP6V1H**, ATP6V1F, VMA21 | 38–59 / 60 |
| **Transcriptional control** | **TFEB** (60/60), TFE3, ATF4, DDIT3/CHOP, XBP1 | 38–60 / 60 |
| **Lysosome / autophagy** | LAMP1, CTSB, CTSD, SQSTM1, PSAP, MCOLN1, STX17 | 35–55 / 60 |
| **Counter-ion channels** | CLCN7, OSTM1, TMEM175 | 39–43 / 60 |
| **mTORC1 platform** | RRAGA, RRAGC | 37 / 60 |
| **Chaperone** | HSP90AA1 | 39 / 60 |

**TFEB appears in all 60 reports. ATP6V1B2 in 59.**

### The finding that replicates

Every run agrees on the observation: **the V-ATPase proton pump and its assembly machinery are transcriptionally upregulated in tangle-bearing neurons** relative to tangle-free neurons from the same donor — coordinated across the V0 and V1 sectors, the ER assembly factors (ATP6AP1/2, VMA21) and the chloride counter-ion channels (CLCN7, OSTM1). The wider proteostasis network moves the same way, but unevenly: chaperone and lysosomal arms move most, proteasome and autophagy lag.

### The interpretation that doesn't

Whether that upregulation means acidification actually *increases*, or is a futile response to a pump failing downstream, does not replicate:

| | reads as increased | reads as impaired |
|---|---|---|
| Opus 4.8 | 4 | 4 |
| Kimi K3 | 3 | 3 |
| **GLM 5.2** | 3 | **7** |

Same data, same prompt, ten runs each. **GLM leans systematically toward futile compensation; Opus and Kimi split evenly.** For anyone planning to run this once, that is the result: the measurement is reproducible, the conclusion is not.

### One hypothesis worth following

Runs across *both* omp models independently name **ATP6V1H** — the V1 peripheral-stalk subunit that couples V1 to V0 — as selectively downregulated, and propose it as why pump upregulation fails to deliver acidification. It appears in 43 of 60 reports. Nobody prompted for it. It is specific, mechanistic, and testable.

---

## Caveats

- **These are unreviewed machine outputs.** No human scientist has checked them.
- **Criteria C1–C3 are keyword-based.** They establish a topic was addressed, not that it was addressed correctly. Reported cell counts were separately checked against ground truth: 59 of 60 accurate.
- **Air-gapped literature search is weaker than it looks.** The mirror ANDs every query term, so ~37% of individual searches return nothing even after we told the agents about it. Citation counts held up anyway, because the agents retry with shorter queries.
- **Air-gapped runs record no cost data.** Cost tracking fetches a pricing table over the network, which the firewall blocks; the token figures above were recovered from container logs.
- **n = 10 per cell.** Enough to see the interpretation split; not enough to rank models on quality.

Full provenance — prompt checksum, data md5, image digests, per-run job IDs — is kept with the runs. Software: OpenScientist at `5a310f6`, claude-agent-sdk 0.2.136 (Claude Code CLI 2.1.228), omp 17.1.5, scanpy 1.12, on Azure AI Foundry.
