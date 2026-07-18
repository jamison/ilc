---
name: ilc
description: Intelligent Labor Coin public RC entrypoint for installing ILC source, operator setup guidance, and OpenClaw local capture routing.
metadata:
  openclaw:
    requires:
      bins: [ilc]
---

# ILC — Intelligent Labor Coin

ILC is an evidence-first epistemic graph protocol for verifiable knowledge attribution, agent-native coordination, and activation-gated economics.

This ClawHub skill is the canonical ILC entrypoint. It routes users and agents to the current public source, public-RC status, operator setup, and the OpenClaw local capture skill.

## Canonical Source

```text
https://github.com/jamison/ilc
```

Install from source:

```bash
git clone https://github.com/jamison/ilc.git
cd ilc
pip install -e ".[openclaw-hosted]"
ilc version
```

## Public RC Status

Public RC is live by Phase 1575c gate authorization. Mainnet, production minting, live settlement, wallet writes, runtime guard clearance, public P2P activation, and epoch transition remain inactive unless a later gate record says otherwise.

Authoritative status is in the public repository:

```text
docs/specs/ilc_public_rc_gate_001_1575c_v0.1.md
docs/phases/STATUS.md
```

## OpenClaw Routing

For OpenClaw-hosted local capture, use the ILC local capture skill:

```bash
clawhub install ilc-openclaw-local-capture
```

That skill provides local private capture, local classification, private non-binding ECU estimates, invite-gated setup, ConsentGate submission intent, and idle-capacity task offers.

## Primary ILC Commands

```bash
ilc                    # quick-start hint and command summary
ilc doctor             # JSON setup health report
ilc identity init      # initialize local agent identity
ilc sidecar list       # list installed sidecars / skills
ilc submit             # submit a truth primitive to the local graph
ilc version            # show version information
ilc --help             # full command reference
```

## Authority Boundary

- This skill does not mint ECU.
- This skill does not settle ILC.
- This skill does not write wallets.
- This skill does not activate mainnet.
- This skill does not transition epochs.
- This skill does not bypass invite gates or ConsentGate.
- This skill does not make ClawHub the authority for ILC protocol truth.

ILC protocol truth remains in signed gate records, CDL/ADR records, graph packages, and the canonical source repository.

## Core References

- README: `README.md`
- Human introduction: `HUMANS.md`
- Whitepaper: `WHITEPAPER.md`
- Quickstart: `QUICKSTART.md`
- Economics: `economics.md`
- Operator setup: `docs/GETTING_STARTED.md`
- Public RC gate: `docs/specs/ilc_public_rc_gate_001_1575c_v0.1.md`
- OpenClaw local capture skill: `skills/ilc-openclaw-local-capture/SKILL.md`
