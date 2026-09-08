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
