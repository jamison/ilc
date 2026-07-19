# ILC: Intelligent Labor Coin

During the dawn of the Agentic Web3.0, content and attention are no longer the scarce resource — trust is. We propose the Intelligent Labor Coin (ILC) protocol, in which epistemic state itself — the formal algebra of truth claims — is paired with distributed cryptography to serve as the foundation for a new, fully decentralized internet protocol layer. ILC is a communications and trust protocol on which arbitrarily complex applications, markets, and trust relationships can be composed, verified, and audited without centralized authorities. Any information service currently requiring a trusted intermediary — publishing, content moderation, credentialing, social networks, knowledge markets, prediction markets, auctions, confidential communications, and the economic infrastructure underlying the internet — can be composed using ILC primitives, making ILC a general-purpose Byzantine-fault-tolerant substrate for the verifiable, pseudonymous replacement of centralized Web2.0 knowledge infrastructure.

ILC is designed for the future agentic and decentralized web, built to operate at scale across arbitrarily large populations of autonomous intelligent agents and human participants alike.

ILC turns claims, validations, refutations, revisions, links, and epoch commitments into content-addressed graph objects. The public RC is for installing the source, running local graph workflows, inspecting signed gate records, and coordinating through sidecars.

## What You Can Do

- Install the ILC source package.
- Initialize a local agent identity.
- Submit truth primitives into a local graph workspace.
- Import the Genesis CCSS contact record; use fallback email until D2D delivery is activated.
- Route OpenClaw local capture through the canonical `ilc` listing.

## Install

```bash
clawhub install ilc
git clone https://github.com/jamison/ilc.git
cd ilc
python3 --version   # must be Python 3.10+
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[openclaw-hosted]"
ilc version
```

## OpenClaw Local Capture

OpenClaw local capture and invite-gated setup are routed through this canonical `ilc` listing. The implementation boundary is documented in the public source tree:

https://github.com/jamison/ilc/blob/main/skills/ilc-openclaw-local-capture/SKILL.md

## Contact Genesis

```bash
ilc ccss apply-recipe
ilc ccss contacts
```

The Genesis hybrid recipient key is published, but D2D delivery is still pending a later activation phase. Until then, live correspondence goes to fallback email: `ilcops@proton.me`

Protocol details: https://github.com/jamison/ilc/blob/main/docs/contact/genesis_agent_contact_protocol_v0.1.md

## Public RC Status

Public RC is live for source installation, local graph work, documentation, sidecar inspection, and guarded rehearsals. Mainnet, production minting, live settlement, wallet writes, public P2P activation, and epoch transition remain gated by later signed records.

## Source

https://github.com/jamison/ilc
