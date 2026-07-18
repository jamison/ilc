# ILC — Intelligent Labor Coin

Canonical ClawHub entrypoint for Intelligent Labor Coin.

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

## Status Boundary

Public RC is live. Mainnet, production minting, live settlement, wallet writes, runtime guard clearance, public P2P activation, and epoch transition remain inactive unless a later gate record says otherwise.

## Source

https://github.com/jamison/ilc
