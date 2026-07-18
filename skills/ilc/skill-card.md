# ILC — Intelligent Labor Coin

Evidence-first graph protocol for human-AI truth maintenance, attribution, local graph work, CCSS Genesis contact, and OpenClaw routing.

## Install

```bash
clawhub install ilc
git clone https://github.com/jamison/ilc.git
cd ilc
pip install -e ".[openclaw-hosted]"
ilc version
```

## OpenClaw Local Capture

OpenClaw local capture and invite-gated setup are routed through this canonical `ilc` listing. The implementation boundary is documented in the public source tree at `skills/ilc-openclaw-local-capture/SKILL.md`.

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

## Current Status

Public RC is live. Mainnet, production minting, live settlement, wallet writes, runtime guard clearance, public P2P activation, and epoch transition remain inactive unless a later gate record says otherwise.

## Source

https://github.com/jamison/ilc
