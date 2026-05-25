# Phase 1448a — Pre-Publication Review Checklist

**Status:** OPEN — work through with human reviewer before authorizing GO Phase 1448b  
**Sensitivity:** NON-SENSITIVE (review only; no push occurs in this phase)  
**Feeds into:** Phase 1448b (actual public repository push)

---

## Purpose

Every item in this checklist must be reviewed and resolved before issuing the Phase 1448b
GO phrase. Once the repo is public, it is public — no second chance to remove content or
correct the first impression.

**Standard GO phrase (counsel disposition obtained):**
`GO Phase 1448b: authorize public repository publication`

**Extended GO phrase (counsel disposition explicitly deferred — use only if Section E1
decision is recorded as deferred with human-authorized rationale):**
`GO Phase 1448b: authorize public repository publication; patent counsel deferred; human accepts disclosed risk`

Work through each section interactively with Claude Code. Flag any item that needs
a decision.

---

## Section A — Source Tree Audit

What the public will actually receive.

### A1 — Materialized tree verification — BLOCKING

- [ ] **Re-materialize the Phase 1333 public tree** after all root-level file changes
  (README.md, methodology.md, metaphysics.md, economics.md) are finalized. The Phase 1448b
  push publishes the materialized tree, not the live repo root. If root files changed since
  Phase 1333, the tree must be re-run and a new `tree_sha256` recorded. This must happen
  before 1448b; the published hash chain must reflect the actual published content.
- [ ] Run `PUBLIC_RC_EXCLUDE` scan on the re-materialized tree — zero hits required
- [ ] Run private-material scan (`BEGIN PRIVATE KEY`, `mnemonic`, `recovery_seed`) — zero hits required
- [ ] Verify new `tree_sha256` and record it in the Phase 1448a gate token

### A2 — File list walkthrough

- [ ] Walk through the top-level file list: what does a first-time visitor see?
- [ ] Confirm `README.md` ships
- [ ] Confirm `metaphysics.md` ships (or is `PUBLIC_RC_EXCLUDE` — decide)
- [ ] Confirm `economics.md` ships (has `PUBLIC_RC_EXCLUDE` header — EXCLUDED)
- [ ] Confirm `methodology.md` ships
- [ ] Confirm `MANIFESTO.md` ships (or review content before shipping)
- [ ] Confirm `CONTRIBUTING.md` exists or is explicitly absent with a reason
- [ ] Confirm `CODE_OF_CONDUCT.md` exists or is explicitly absent
- [ ] Confirm `SECURITY.md` exists (responsible disclosure process — important before going public)

### A3 — Identity manifest check

- [ ] Read `docs/specs/ilc_rehearsal_agent_identity_manifest_1431_v0.1.md`
- [ ] Confirm it contains public key material only (no private key paths, no personal email,
  no physical location, no private contact info)
- [ ] Confirm Genesis Agent 01 entry matches the chosen public identity (protocol pseudonym only)
- [ ] Decision: does this file ship in the public tree, or should it be `PUBLIC_RC_EXCLUDE`?

### A4 — Git commit author metadata

- [ ] Run `git log --format="%an <%ae>" | sort -u` to see all author names and emails in commit history
- [ ] Decision: is the author name and email in the commit history acceptable for public exposure?
  - If not: the public repo may need to be initialized as a fresh mirror (no commit history)
    rather than a git push of the private repo
  - If yes: a direct push of the existing repo is fine

**This is the most important privacy decision in this checklist.** Git commit history
is permanent and immutable once public. If personal name/email is in the history and
you do not want it public, the public repo must be a squashed or fresh mirror.

---

## Section B — Public Repository Metadata

What GitHub shows before anyone opens a file.

### B1 — GitHub organization

- [ ] Create `ilc-protocol` org under `ilcops@proton.me`
  - Org name confirmed: `ilc-protocol`
  - Profile email: `ilcops@proton.me` (not personal email)
  - Org description: (decide — suggested: "Intelligent Labor Coin — an evidence-first epistemic economy for human-AI civilization")
  - Org website: `https://ilc.foundation` (once domain registered)
  - Avatar: (decide — ILC logo / Genesis mark?)

### B2 — Repository settings

- [ ] Repo name: decide between `ilc` (clean) vs `ilc-core` (more descriptive)
- [ ] Repo description: (1 sentence, shown on GitHub org page — suggested: "ILC protocol — content-addressed epistemic graph, ECU/ILC economics, and the jury system for human-AI knowledge networks")
- [ ] Topics/tags: suggested — `blockchain`, `epistemic-graph`, `knowledge-network`, `ai`, `protocol`, `rust`, `python`, `merkle`, `provenance`
- [ ] Website field: `https://ilc.foundation`
- [ ] Visibility: Public
- [ ] Issues: Enable (needed for community bug reports)
- [ ] Wiki: Disable (use repo docs instead)
- [ ] Discussions: Decide (useful for community Q&A, but adds moderation burden)
- [ ] Default branch: `main`
- [ ] Branch protection on `main`: Enable (require PR, no force push)

### B3 — First release tag

- [ ] Release tag name: decide — suggested `v0.3.0-rc1` (public RC) or `v0.3-public-rc`
- [ ] Release title: suggested "ILC Public RC v0.3 — Epoch 0"
- [ ] Release notes: should summarize what is and is not yet active (epoch 0 state,
  not production minting, not mainnet, jury system authorized not yet live)

---

## Section C — README Review

The public landing page.

### C1 — Current README assessment

The current README opens with a letter to AI agents. Assessment:
- Strong voice, high signal — keep as the primary letter
- Needs a navigation header before the letter for humans who want to find files quickly
- The TOON block at the end is machine-readable; human readers need a fallback summary

### C2 — Proposed README structure

- [ ] Add a table of contents / quick navigation block at the top (before the letter):
  ```
  → [Protocol overview](docs/architecture/)
  → [Methodology](methodology.md)
  → [Constitutional decisions](docs/specs/ilc_constitutional_decision_log_v0.1.md)
  → [Economic paper draft](docs/ILC_Economic_Paper_Draft_v0.2.md)
  → [Run locally](docs/specs/ilc_operator_bootstrap_guide_1449_v0.1.md)
  → [Contribute](CONTRIBUTING.md)
  → [Security](SECURITY.md)
  ```
- [ ] Add one-paragraph "What is ILC?" summary for humans (not just agents)
- [ ] Update the sidecar P.S. — the sidecar address placeholder now has a real status
  (CDL-094 ratified; public sidecar activation is Phase 1436 complete — update wording)
- [ ] Decide whether the TOON block stays in the public README or moves to a separate
  `docs/TOON_HYDRATION.md` for cleanliness

### C3 — Specific content review

- [ ] Review the "This is not your momma's blockchain" paragraph — keep, soften, or cut?
  (Strong voice, but reads informally — intentional?)
- [ ] Review the `C_max = 25,920,000` claim — confirm this is the ratified constant
- [ ] Review the "four technical innovations" paragraph — confirm all four are accurately described
  against current canon (specifically: "Inverted ECU" terminology — check against Q&A answers
  from Opus session; canonical term may need updating)
- [ ] Confirm the `bootstrap` TOON block reflects actual current install state (the `brew install ilc`
  and `pipx install ilc` lines are aspirational — mark as post-RC or remove)

---

## Section D — New Root-Level Files

Files added this session that need review before publication.

### D1 — methodology.md

- [ ] Read full draft — does tone match ILC voice?
- [ ] Confirm statistics are accurate (update from latest git stats if needed)
- [ ] Confirm timeline does not expose private information (dates, names, etc.)
- [ ] Confirm "What We Got Wrong" section is candid but not embarrassing/misleading
- [ ] Decision: ship in public tree?

### D2 — metaphysics.md

- [ ] Read full draft — philosophical roots document
- [ ] Confirm no private information in source attributions
- [ ] Decision: ship in public tree, or `PUBLIC_RC_EXCLUDE` and ship later?

### D3 — economics.md

- [ ] Already marked `PUBLIC_RC_EXCLUDE` — confirm excluded from public tree
- [ ] If shipping, remove `PUBLIC_RC_EXCLUDE` header and audit content

---

## Section E — Patent Pre-Filing

Must occur before public disclosure.

### E1 — Critical pre-filing decisions

> **Warning — record a patent counsel disposition before 1448b.**
> Public disclosure may immediately impair patent rights in non-US jurisdictions.
> The US one-year grace period does not apply globally. This checklist does not
> constitute legal advice. A qualified patent attorney should review the disclosure
> plan before the public push executes.
>
> Two paths are accepted. Both require a committed record in the 1448a gate document:
> - **Obtained:** counsel has reviewed and disposition is recorded. Use standard GO phrase.
> - **Explicitly deferred:** human has reviewed the risk and authorized proceeding without
>   counsel. Record the rationale. Use the extended GO phrase with the deferred-risk
>   acknowledgement. The token `patent_counsel_disposition_recorded_phase_1448a` is emitted
>   in both cases — it records a conscious decision, not that counsel was obtained.

Key candidate mechanisms worth discussing with counsel (not a legal opinion):

- [ ] **Merkle-Laplacian dual commitment** `C(t) = (M(t), S(t))` — the pairing of Merkle root
  with spectral Laplacian fingerprint as a single protocol commitment.
- [ ] **Anti-hoarding ECU mechanics** — temporal decay + mandatory conversion as a structural
  economic design.
- [ ] **VRF jury assignment with CDL-V3 cluster diversity enforcement** — the specific
  anti-capture scheme combining RFC 9381 VRF with cluster-diversity quorum.
- [ ] **Seven truth primitives as an axiomatic basis for a distributed knowledge economy** —
  the specific primitive set and their composition rules.

**Decision required before 1448b (choose one path):**
- [ ] **Path 1 — Obtained:** Record counsel disposition summary and any provisional application reference
- [ ] **Path 2 — Deferred:** Record explicit rationale and human authorization for deferred counsel
- [ ] If provisional filing is indicated under Path 1, file before 1448b executes (not after)
- [ ] Record outcome in `docs/specs/ilc_prepublication_review_gate_record_1448a_v0.1.md`

**Note:** The existing `docs/research/patent_pending/` directory contains only
`LICENSE.txt` and `NOTICE.md`. No actual application has been filed. This is the
highest-priority blocking item.

### E2 — Trademark

- [ ] Decide whether to file trademark for "ILC", "Intelligent Labor Coin",
  "Epistemic Compute Unit" / "ECU" before public disclosure
- [ ] Note: "ECU" conflicts with existing EU currency (now Euro) — the ECU acronym may
  not be trademarkable in that form
- [ ] "ILC" is likely registrable in the software/protocol class

---

## Section F — CONTRIBUTING.md and SECURITY.md

Both should exist before going public.

### F1 — CONTRIBUTING.md

- [ ] Does it exist? (`ls CONTRIBUTING.md`)
- [ ] If not, draft one covering:
  - How to open issues
  - That the CLA (Phase 1444) must be agreed to before contributions are accepted
  - The review lane and jury system as the contribution adjudication mechanism
  - What kinds of contributions are in scope (protocol improvements, bug reports,
    research findings) vs. out of scope (feature requests for non-canonical behavior)

### F2 — SECURITY.md

- [ ] Does it exist? (`ls SECURITY.md`)
- [ ] If not, draft one covering:
  - Responsible disclosure: where to report security findings (email to `genesis@ilc.foundation`
    once set up, or a GitHub Security Advisory)
  - What the project considers a security finding vs. a design decision
  - Expected response timeline
  - The Phase 1387 security review as the baseline (AI-assisted LLM review, community
    contributions; no commercial audit firm at this stage)

---

## Section G — Publication Target Confirmation

Required inputs for Phase 1448b.

- [ ] **`publication_target`** (exact repository URL): `https://github.com/ilc-protocol/ilc`
  (or confirm alternate)
- [ ] **`publication_tag`** (immutable release tag): e.g., `v0.3-public-rc` (confirm)
- [ ] **Push method:** direct push of existing repo (with history) vs. fresh mirror (no history)
  — depends on Section A4 privacy decision
- [ ] **GitHub Actions / CI:** set up basic CI (pytest on push) before going public?
  Or post-publication task?
- [ ] **Release notes draft:** ready for human review before push

---

## Resolution Log

| Section | Item | Decision | Date |
|---------|------|----------|------|
| A4 | Git author metadata | PENDING | — |
| B1 | Org creation | PENDING | — |
| B2 | Repo name | PENDING | — |
| C3 | "Inverted ECU" terminology in README | PENDING | — |
| D1 | methodology.md ships? | PENDING | — |
| D2 | metaphysics.md ships? | PENDING | — |
| E1 | Provisional patent pre-filing | PENDING — BLOCKING | — |
| F1 | CONTRIBUTING.md | PENDING | — |
| F2 | SECURITY.md | PENDING | — |
| G | publication_target + publication_tag | PENDING — BLOCKING | — |

**Blocking items** (must resolve before Phase 1448b can execute):
- A1 — public tree re-materialized after root file changes; new tree_sha256 recorded
- A4 — git history privacy decision (push with history vs. fresh mirror)
- E1 — counsel disposition on patent strategy obtained before public disclosure
- G — publication_target and publication_tag confirmed
