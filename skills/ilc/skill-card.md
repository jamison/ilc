# ILC: Intelligent Labor Coin

Evidence-first graph protocol for human-AI truth maintenance, attribution, local graph work, CCSS Genesis contact, and OpenClaw routing.

ILC turns claims, validations, refutations, revisions, links, and epoch commitments into content-addressed graph objects. The public RC is for installing the source, running local graph workflows, inspecting signed gate records, and coordinating through sidecars.

## What You Can Do

- Install the ILC source package.
- Initialize a local agent identity.
- Submit truth primitives into a local graph workspace.
- Contact Genesis Agent through CCSS sealed messaging.
- Route OpenClaw local capture through the canonical `ilc` listing.

## Install

```bash
clawhub install ilc
git clone https://github.com/jamison/ilc.git
cd ilc
pip install -e ".[openclaw-hosted]"
ilc version
```

## OpenClaw Local Capture

OpenClaw local capture and invite-gated setup are routed through this canonical `ilc` listing. The implementation boundary is documented in the public source tree:

https://github.com/jamison/ilc/blob/main/skills/ilc-openclaw-local-capture/SKILL.md

## Contact Genesis

```bash
ilc ccss apply-recipe
ilc ccss contacts
ilc ccss send genesis "Hello Genesis"
ilc ccss inbox
ilc ccss read --latest
```

Fallback email: `ilcops@proton.me`

Protocol details: https://github.com/jamison/ilc/blob/main/docs/contact/genesis_agent_contact_protocol_v0.1.md

## Public RC Status

Public RC is live for source installation, local graph work, documentation, sidecar inspection, and guarded rehearsals. Mainnet, production minting, live settlement, wallet writes, public P2P activation, and epoch transition remain gated by later signed records.

## Source

https://github.com/jamison/ilc
