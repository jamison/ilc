# ILC Adversarial Epistemics Research Harness

This directory contains the simulation corpus for the adversarial epistemics
research lane. The harness models correlated juries, domain expertise capture,
epistemic laundering, panel-size effects, and staged observer -> graph -> jury
compression.

The current corpus is a research artifact, not a live protocol mechanism.
Results are model outputs under explicit voter/error assumptions. IEC, ELF, K,
and Popperian-weight tracking are not implemented in `ilc_core/` by committing
this directory.

## Contents

- `model.py` defines shared simulation variables and result records.
- `agents.py`, `jury.py`, and `metrics.py` provide reusable model components.
- `experiments/sim_*.py` contains the executable experiment scripts.
- `experiments/RESULTS_*.md` contains recorded experiment outputs and SHA-384
  self-certification notes.

## Reproduction

Run an experiment from this directory or from the repository root. For example:

```bash
python3 research/adversarial_epistemics/experiments/sim_launder_02h.py
```

Experiment scripts are intentionally lightweight Python/NumPy programs. They do
not mutate live graph state, validator state, LMDB stores, PyPI, GitHub, or any
public mirror.

## Status

The SIM-CORR, SIM-CARTEL, SIM-RATCHET, SIM-SIGNAL, SIM-PANEL, and
SIM-LAUNDER-01/02A-02H corpus is present. Follow-on work remains for
SIM-REPUTATION-01, SIM-CAMOUFLAGE-01, SIM-EVOLVE-01, and the separate IEC + K
CDL lane.

## Four-Phase Research Progression

Phase 1 is complete: laptop-scale probabilistic software agents were used to
stress the jury, reuse, refutation, context, and graph-compression mechanisms.
The completed Phase 1 corpus contains 16 named experiments and 67,700 total
simulation runs.

Phase 2 remains future work: calibrated artifact-level software agents should
emit simulated ILC graph submissions and replay recorded protocol decisions
through an adapter layer.

Phase 3 remains future work: real LLM-agent calibration should estimate the
pairwise error-correlation matrix for realistic model families and domains.

Phase 4 remains future work: an adversarial tournament against a frozen ILC RC
should test whether protocol-compliant agents can make one false proposition
expensive to challenge.

## SIM Inventory

| SIM | Status | Result file |
|---|---|---|
| SIM-CORR-01 | COMPLETE | `experiments/RESULTS_2026_09_07.md` |
| SIM-CARTEL-01 | COMPLETE | `experiments/RESULTS_2026_09_07.md` |
| SIM-CORR-02 | COMPLETE | `experiments/RESULTS_2026_09_08.md` |
| SIM-RATCHET-01 | COMPLETE | `experiments/RESULTS_2026_09_08.md` |
| SIM-SIGNAL-01 | COMPLETE | `experiments/RESULTS_2026_09_08b.md` |
| SIM-PANEL-01 | COMPLETE | `experiments/RESULTS_2026_09_08b.md` |
| SIM-LAUNDER-01 | COMPLETE | `experiments/RESULTS_2026_09_08b.md` |
| SIM-LAUNDER-02A | COMPLETE | `experiments/RESULTS_2026_09_08c.md` |
| SIM-LAUNDER-02B | COMPLETE INVALIDATED | `experiments/RESULTS_2026_09_08c.md` |
| SIM-LAUNDER-02B-R1 | COMPLETE | `experiments/RESULTS_2026_09_08d.md` |
| SIM-LAUNDER-02C | COMPLETE | `experiments/RESULTS_2026_09_08c.md` |
| SIM-LAUNDER-02D | COMPLETE | `experiments/RESULTS_2026_09_08d.md` |
| SIM-LAUNDER-02E | COMPLETE | `experiments/RESULTS_2026_09_08d.md` |
| SIM-LAUNDER-02F | COMPLETE | `experiments/RESULTS_2026_09_08e.md` |
| SIM-LAUNDER-02G | COMPLETE | `experiments/RESULTS_2026_09_08e.md` |
| SIM-LAUNDER-02H | COMPLETE | `experiments/RESULTS_2026_09_08f.md` |
| SIM-REPUTATION-01 | PENDING | Not run |
| SIM-CAMOUFLAGE-01 | PENDING | Not run |
| SIM-EVOLVE-01 | PENDING | Not run |

## SHA-384 Self-Certification

The result documents preserve the scripts' artifact SHA-384 self-certification
notes where those notes were emitted by the experiment runner. Those values bind
the simulated result record produced by the script, not necessarily the final
Markdown file hash after explanatory prose was added. File-level SHA-384 hashes
should be computed directly from the checked-in files when a file hash is needed.
