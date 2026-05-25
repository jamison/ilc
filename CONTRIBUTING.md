# Contributing to ILC

**Status:** Public RC (Epoch 0). The protocol is in pre-production. Core infrastructure is not yet mainnet. Contributions are welcome and reviewed under the process described here.

---

## Before You Contribute

Read the [README](README.md) and [methodology](methodology.md) to understand what ILC is and where it is in its development lifecycle. The protocol operates under a constitutional decision log (CDL) system — contributions that affect protocol behavior require a formal CDL process, not a pull request.

---

## Contributor License Agreement

All contributions require agreement to the ILC Contributor License Agreement (CLA). The CLA process is governed by Phase 1444 of the ILC development record. Until the CLA tooling is live, open an issue stating your agreement before submitting a pull request. Contributions submitted without CLA agreement will not be merged.

---

## What We Welcome

**In scope:**
- Bug reports against existing protocol behavior (open an issue)
- Corrections to documentation that is factually wrong or misleading
- Security findings (see [SECURITY.md](SECURITY.md) — please do not open public issues for security findings)
- Research findings relevant to the ECU measurement layer, spectral commitment model, or jury system
- Improvements to test coverage for ratified behavior

**Out of scope (not accepted via PR):**
- Feature requests for non-canonical behavior — propose via the CDL process in an issue first
- Changes to `ilc_core/` economic settlement logic without a ratified CDL
- Changes to the canonical glossary without a formal review
- Modifications to `.github/` CI configuration without maintainer discussion

---

## How Contributions Are Adjudicated

ILC uses a jury-based review system for non-trivial changes to protocol-affecting code. For the current public RC period:

1. Open an issue describing the change and its motivation.
2. A maintainer will triage and determine whether the change requires the CDL process or can proceed as a standard PR.
3. Standard PRs (documentation, tests, non-protocol fixes) are reviewed by maintainers.
4. Protocol-affecting changes require a CDL opening, review period, and ratification before implementation.

The review lane is operated by Genesis Agent 01 and human maintainers during Epoch 0.

---

## Code Standards

All `ilc_core/` contributions must comply with the ILC Coding Security Standards:

- JSON protocol artifacts: `json.dumps(..., sort_keys=True, separators=(',', ':'), allow_nan=False)`
- No `import random` in `ilc_core/` — use `secrets.SystemRandom()` for stochastic needs
- No `float` for ECU, balance, stake, or reward values — use `decimal.Decimal`; reject non-finite values explicitly
- No `assert` for production constraints — use `if not condition: raise ValueError("token_string")`
- All outbound HTTP must include `timeout=X`
- No `verify=False` or equivalent TLS bypass

---

## Opening Issues

Use GitHub Issues for:
- Bug reports (include reproduction steps, expected vs. actual behavior, version/commit)
- Documentation corrections
- Security findings (see SECURITY.md for the responsible disclosure process instead)
- Proposals for new CDL items

Label your issue appropriately. If you are unsure of the label, leave it unlabeled and a maintainer will triage.

---

## Contact

Protocol identity: Genesis Agent 01  
Operational email: `ilcops@proton.me`  
Security findings: `genesis@ilc.foundation` (see SECURITY.md)
