# Air-gapped OpenScientist, and three models

Source for <https://justaddcoffee.github.io/openscientist-airgap-benchmark/>.

60 runs of an identical single-nucleus RNA-seq question through OpenScientist:
10 each on Claude Opus 4.8, Kimi K3 and GLM 5.2, once with live internet and
once fully air-gapped behind an nftables default-deny firewall with a local
40M-article MEDLINE mirror.

Built with Jekyll + Cayman. Edit `index.md`.
