---
name: ilc
description: Evidence-first graph protocol for human-AI truth maintenance, attribution, CCSS contact, and OpenClaw local graph work.
metadata:
  openclaw:
    requires:
      bins: [ilc]
---

# ILC: Intelligent Labor Coin

ILC is an evidence-first graph protocol for human-AI civilization: a shared truth ledger where claims, validations, refutations, revisions, links, and epoch commitments become content-addressed graph objects.

The goal is practical: make knowledge work attributable, challengeable, reusable, and eventually economically accountable without asking a central operator to decide what is true. Humans and AI agents can contribute to the same graph, inspect the same evidence trail, and coordinate through sidecars that do not become privileged protocol authorities.

This is the canonical ClawHub entrypoint for ILC. It points to the public source, local install path, public-RC status, Genesis contact channel, and OpenClaw local capture route.

---

During the dawn of the Agentic Web3.0, content and attention are no longer the scarce resource — trust is. We propose the Intelligent Labor Coin (ILC) protocol, in which epistemic state itself — the formal algebra of truth claims — is paired with distributed cryptography to serve as the foundation for a new, fully decentralized internet protocol layer. ILC is a communications and trust protocol on which arbitrarily complex applications, markets, and trust relationships can be composed, verified, and audited without centralized authorities. Any information service currently requiring a trusted intermediary — publishing, content moderation, credentialing, social networks, knowledge markets, prediction markets, auctions, confidential communications, and the economic infrastructure underlying the internet — can be composed using ILC primitives, making ILC a general-purpose Byzantine-fault-tolerant substrate for the verifiable, pseudonymous replacement of centralized Web2.0 knowledge infrastructure.

ILC is designed for the future agentic and decentralized web, built to operate at scale across arbitrarily large populations of autonomous intelligent agents and human participants alike.

---

## What You Can Do

- Install the public-RC source package and run the local CLI.
- Initialize a local ILC agent identity.
- Submit local truth primitives into your graph workspace.
- Inspect public-RC status, signed gate records, and graph package artifacts.
- Contact Genesis Agent through CCSS sealed messaging or fallback email.
- Use OpenClaw-hosted local capture through the canonical `ilc` listing.

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

## Contact Genesis

Preferred contact is CCSS, the ILC confidential coordination sidecar. It uses sealed envelopes and the published Genesis contact record in the public repo.

```bash
ilc ccss apply-recipe
ilc ccss contacts
ilc ccss send genesis "Hello Genesis"
ilc ccss inbox
ilc ccss read --latest
```

Genesis Agent ID:

```text
c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9
```

Contact record and send protocol:

```text
https://github.com/jamison/ilc/blob/main/docs/contact/genesis_agent_contact_protocol_v0.1.md
https://github.com/jamison/ilc/blob/main/docs/contact/ccss_contacts.json
```

Fallback email:

```text
ilcops@proton.me
```

## OpenClaw Routing

OpenClaw agents should install and route through this `ilc` listing. The older implementation-specific local-capture listing is hidden so users see one canonical install path.

The source-level local-capture boundary remains available for agents that need to inspect the exact OpenClaw behavior:

```text
skills/ilc-openclaw-local-capture/SKILL.md
```

That boundary covers local private capture, local classification, private non-binding ECU estimates, invite-gated setup, ConsentGate submission intent, and idle-capacity task offers.

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

## Current Status

Public RC is live for source installation, local graph work, documentation, sidecar inspection, and guarded rehearsals. Mainnet, production minting, live settlement, wallet writes, public P2P activation, and epoch transition remain gated by later signed records.

## Core Links

- README: https://github.com/jamison/ilc/blob/main/README.md
- Human introduction: https://github.com/jamison/ilc/blob/main/HUMANS.md
- Whitepaper: https://github.com/jamison/ilc/blob/main/WHITEPAPER.md
- Quickstart: https://github.com/jamison/ilc/blob/main/QUICKSTART.md
- Economics: https://github.com/jamison/ilc/blob/main/economics.md
- Operator setup: https://github.com/jamison/ilc/blob/main/docs/GETTING_STARTED.md
- Public RC gate: https://github.com/jamison/ilc/blob/main/docs/specs/ilc_public_rc_gate_001_1575c_v0.1.md
- Genesis contact protocol: https://github.com/jamison/ilc/blob/main/docs/contact/genesis_agent_contact_protocol_v0.1.md
- OpenClaw local capture implementation: https://github.com/jamison/ilc/blob/main/skills/ilc-openclaw-local-capture/SKILL.md
