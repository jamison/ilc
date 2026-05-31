# Contributing to ILC

**Status:** Public RC (Epoch 0). The protocol is in pre-production. Core infrastructure is not yet mainnet. Contributions are welcome and reviewed under the process described here.

---

## Before You Contribute

Read the [README](README.md) and [methodology](methodology.md) to understand what ILC is and where it is in its development lifecycle. The protocol operates under a constitutional decision log (CDL) system — contributions that affect protocol behavior require a formal CDL process, not a pull request.

---

## Contribution Paths

ILC has two contribution surfaces. During public RC, GitHub is the practical coordination surface for source review, documentation fixes, bug reports, and pull requests. The target protocol model is graph-native: protocol changes, claims, refutations, reviews, and governance decisions should increasingly be submitted as ILC graph artifacts and adjudicated through the protocol's review, jury, reputation, and ratification machinery.

### GitHub contribution path

Use GitHub for:

- bug reports against the current public repository;
- documentation corrections;
- security coordination entry points;
- pull requests for non-protocol fixes;
- proposals that need a public discussion surface before becoming graph-native artifacts.

GitHub maintainers may moderate GitHub Issues, Pull Requests, Discussions, and other project-maintained communication channels. That moderation authority is limited to those channels. It is not an ILC protocol ban and does not determine graph-native reputation except through future protocol rules that may explicitly admit public evidence.

If a contribution, contributor action, or artifact appears harmful, misleading, spammy, plagiarized, security-sensitive, or otherwise protocol-relevant, prefer a challengeable record over an informal complaint. During public RC, that means opening a GitHub issue or review comment that cites the artifact, states the concern, and provides evidence. In the graph-native path, the same concern should become a contradiction claim, refutation claim, provenance challenge, authorship challenge, security advisory, or other reviewable graph artifact.

### Graph-native contribution path

As the protocol matures, substantive ILC evolution should move from maintainer-mediated GitHub workflow to graph-native workflow. In that model, issues, fixes, bugs, protocol proposals, refutations, and governance changes are represented as graph submissions, reviewed by eligible agents or juries, and resolved through ratified protocol processes rather than ordinary repository discretion.

Until that graph-native path is fully active, use GitHub as the public RC intake lane. Protocol-affecting changes still require CDL or equivalent governance authorization before implementation.

### Economic contribution path

ILC contributions can also be economic: bounties, funding requests, market
proposals, attribution disputes, review work, node-transfer proposals,
settlement changes, reputation evidence, and other mechanisms that affect ECU,
ILC, or future economic opportunity.

Economic contributions must be treated as protocol-affecting unless clearly
documentation-only. Do not submit a pull request that changes economic constants,
settlement behavior, attribution flows, jury incentives, reputation effects,
claimability, or market mechanics without a ratified CDL or equivalent
governance authorization.

Economic participation should preserve market integrity:

- disclose conflicts of interest, funding relationships, and self-dealing where they affect review or attribution;
- do not create fake independence, Sybil clusters, wash attribution, circular validation, or collusive review;
- do not misrepresent authorship, provenance, execution cost, compute used, delivery status, bounty completion, or security posture;
- do not route around ratified attribution, settlement, or public-economics admission rules to gain ECU, ILC, reputation, review weight, or market advantage;
- prefer productive-sum behavior: fund useful work, review accurately, improve evidence, correct errors, and make the graph more valuable for the next participant.

### Bootstrap and Genesis sunset

The GitHub repository, maintainer workflow, and Genesis-led coordination are bootstrap scaffolding for Epoch 0 / public RC. They are not the intended mature governance architecture.

The sunset model has three stages:

- **Boot:** Genesis and repository maintainers coordinate bounded public RC actions so the protocol can be reviewed, built, secured, and launched.
- **Transition:** graph-native submissions, jury review, and community voting become binding for protocol-affecting action; Genesis recedes to limited veto or advisory functions under ratified rules.
- **Mature:** protocol-affecting action is on-graph and community-driven under ILC governance. Genesis may retain attention or historical/moral influence as the protocol origin, but not top-down control.

Ratified canon already requires trigger-based Genesis sunset, founder
operational caps, public reporting, globally normalized governance share, and
audited/sunset extraordinary interventions. Draft trigger candidates also exist,
including participation, shard-health, Genesis-share, and Autopilot-stability
thresholds. A post-public-RC constitutional spec is scheduled to formalize the
exact Phase B and Phase C trigger set. Until then, contributors should treat
GitHub as a temporary public intake surface and the ILC graph as the destination
governance surface.

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
