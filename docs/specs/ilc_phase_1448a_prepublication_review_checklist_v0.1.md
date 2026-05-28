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

### A1 — Materialized tree verification — **RESOLVED 2026-05-25**

- [x] **Re-materialize the Phase 1333 public tree** after all root-level file changes
  (README.md, methodology.md, metaphysics.md, FUNDING.md, CONTRIBUTING.md, SECURITY.md,
  CODE_OF_CONDUCT.md) are finalized. Gate ran clean: `result: executed_clean_export`.
- [x] `PUBLIC_RC_EXCLUDE` marker scan — **zero hits** (methodology.md force-included with
  `marker_status: hit_force_included`; not counted as an exported marker hit)
- [x] Dependency scan — zero stripped-helper hits
- [x] Legacy untagged review — zero blocked ambiguities
- [x] `tree_sha256` recorded: **`925d6399399c7f82f52cf17318687a9d625d7e64ef2b0e2fc6586fd15c036361`**

### A2 — File list walkthrough

- [x] Walk through the top-level file list: decisions recorded below
- [x] `README.md` — **SHIPS** (corrected: "Werner productive-credit anti-hoarding" replaces "Inverted ECU"; "Genesis Agent" replaces "Genesis Agent 01"; `genesis_agent_confidential_sidecar` replaces `jamison_confidential_sidecar`; nav block updated 2026-05-28)
- [x] `metaphysics.md` — **SHIPS** ("Genesis Agent" pseudonym applied 2026-05-25)
- [x] `economics.md` — **EXCLUDED** (`PUBLIC_RC_EXCLUDE` header present). Future intent: scientifically tighten and ship a TOON-format version for digital agents; deferred to a future phase.
- [x] `methodology.md` — **SHIPS** (force-included in `DEFAULT_FORCE_INCLUDE_PATHS` 2026-05-25)
- [x] `MANIFESTO.md` — **EXCLUDED** (`PUBLIC_RC_EXCLUDE` marker added 2026-05-28; too hand-wavy for public RC; may be revised and shipped post-RC)
- [x] `CONTRIBUTING.md` — **SHIPS** (in `DEFAULT_INCLUDE_ROOTS` 2026-05-25)
- [x] `CODE_OF_CONDUCT.md` — **SHIPS** (in `DEFAULT_INCLUDE_ROOTS` 2026-05-25)
- [x] `SECURITY.md` — **SHIPS** (in `DEFAULT_INCLUDE_ROOTS` 2026-05-25)

### A3 — Identity manifest check — **RESOLVED 2026-05-28**

- [x] Read `docs/specs/ilc_rehearsal_agent_identity_manifest_1431_v0.1.md` — header: "public fields only"; no personal email, phone, address, or location hits confirmed by grep
- [x] Contains seven public identity records (M1: Genesis Agent, Reviewer-1, Reviewer-2; M2: Validator-A1, Validator-A2; M3: Validator-B1, Validator-B2) — public key material only; private key material off-machine
- [x] **Decision: SHIPS in public tree.** Shipping the manifest is useful for community — it documents the rehearsal ceremony, provides the public identity anchors, and demonstrates the CDL-069 derivation in practice. No private information present.

### A4 — Git commit author metadata — **RESOLVED 2026-05-28**

- [x] Run `git log --format="%an <%ae>" | sort -u` — result: **one author: `Genesis Agent <ilcops@proton.me>`** across all commits
- [x] **Decision: Option A — Fresh mirror.** The public repo (`ILC-Foundation/ilc`) will be seeded from the materialized tree as a single squashed commit authored as `Genesis Agent <ilcops@proton.me>`. The private repo retains the full development history. Personal name and email will NOT appear in the public commit history.

**Rationale for community/long-term governance:** A fresh mirror is also the better choice for protocol longevity — when Genesis steps back and the community self-governs, the entire visible public commit history is protocol work, not private development iterations linked to the founder's personal email. This is cleaner for external contributors and preserves the pseudonymous Genesis Agent model throughout.

**A4 push instructions (confirmed):**
```bash
cd /tmp/ilc-public
git init
git config user.name "Genesis Agent"
git config user.email "ilcops@proton.me"
cp -r /tmp/ilc_rc_export_<hash>/. .
git add -A
git commit -m "ILC v0.3 Public RC — Epoch 0"
git remote add origin git@github.com:ILC-Foundation/ilc.git
git push -u origin main
```

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

### B3 — First release tag — **RESOLVED 2026-05-28**

- [x] Release tag name: **`v0.3-public-rc`** (confirmed)
- [x] Release title: **"ILC Public RC v0.3 — Epoch 0"** (confirmed)
- [x] Release notes: drafted at `docs/specs/ilc_v03_public_rc_release_notes_draft_v0.1.md` — covers epoch 0 state, what is and is not live, ECU analysis-grade note, local run instructions, patent status note. Requires human review before Phase 1448b GO.

**Note on repo "go live" decision point:** The `ILC-Foundation/ilc` repo is currently private. Flipping it to public is the Phase 1448b action — not before. Branch protection on `main` (require PR, no force push) should be configured at the moment of flip, not before, since push of the initial squashed commit requires a direct push to main. Configure branch protection immediately after the initial push completes.

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
- [ ] **Agentic function endpoints and graph-native agent trust-state neighborhoods** —
  identity-seed-derived agent identities instantiating sidecar-bounded function endpoints,
  query-response/co-attested inference artifacts, processing-capacity tier declarations,
  and invitation/provenance chains without executable payloads in core graph nodes.

**Decision required before 1448b (choose one path):**
- [ ] **Path 1 — Obtained:** Record counsel disposition summary and any provisional application reference
- [ ] **Path 2 — Deferred:** Record explicit rationale and human authorization for deferred counsel
- [ ] If provisional filing is indicated under Path 1, file before 1448b executes (not after)
- [ ] Record outcome in `docs/specs/ilc_prepublication_review_gate_record_1448a_v0.1.md`

**2026-05-27 rehydration note:** `docs/research/patent_pending/` now contains a
five-provisional draft package, Filing 5 guidance/spec materials, figure SVGs,
figure traceability audit, `NOTICE.md`, `LICENSE.txt`, and a five-provisional
filing checklist. No actual application has been filed by this repo update.
This remains the highest-priority blocking item before 1448b unless the human
records explicit deferred-risk authorization.

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

- [ ] **`publication_target`** (exact repository URL): `https://github.com/ILC-Foundation/ilc`
  (confirmed — `ILC-Foundation` org created 2026-05-25; repo exists private)
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
| A2 | File list walkthrough | RESOLVED — MANIFESTO.md excluded; economics.md excluded (future TOON rewrite); all others decided | 2026-05-28 |
| A3 | Identity manifest ships? | RESOLVED — ships; public fields only confirmed | 2026-05-28 |
| A4 | Git author metadata | RESOLVED — Option A (fresh mirror); `Genesis Agent <ilcops@proton.me>`; no personal name/email in public history | 2026-05-28 |
| CDL-095 | Jury verdict finality ratification | RESOLVED — ratified Phase 1448c; token `cdl_095_ratified_phase_1448c` | 2026-05-25 |
| B1 | Org creation | RESOLVED — `ILC-Foundation` org created; description, topics, issues configured 2026-05-28; website pending domain registration | 2026-05-28 |
| B2 | Repo name | RESOLVED — `ilc` (clean); private repo `ILC-Foundation/ilc` configured | 2026-05-28 |
| B3 | Release notes draft | RESOLVED — drafted at `docs/specs/ilc_v03_public_rc_release_notes_draft_v0.1.md`; branch-protection timing noted | 2026-05-28 |
| C3 | "Inverted ECU" terminology in README | RESOLVED — changed to "Werner productive-credit anti-hoarding" | 2026-05-28 |
| A1 | Public tree re-materialization | RESOLVED — `tree_sha256: 925d6399...` | 2026-05-25 |
| D1 | methodology.md ships? | RESOLVED — ships; force-included in DEFAULT_FORCE_INCLUDE_PATHS | 2026-05-25 |
| D2 | metaphysics.md ships? | RESOLVED — ships; "Genesis Agent" pseudonym applied | 2026-05-25 |
| D3 | FUNDING.md ships? | RESOLVED — ships; added to DEFAULT_INCLUDE_ROOTS | 2026-05-25 |
| E1 | Patent counsel disposition (Path 1: obtained OR Path 2: deferred with rationale) | PENDING — BLOCKING | — |
| F1 | CONTRIBUTING.md | RESOLVED — ships; in DEFAULT_INCLUDE_ROOTS | 2026-05-25 |
| F2 | SECURITY.md | RESOLVED — ships; in DEFAULT_INCLUDE_ROOTS | 2026-05-25 |
| G | publication_target + publication_tag | RESOLVED — `https://github.com/ILC-Foundation/ilc`, tag `v0.3-public-rc` | 2026-05-25 |

**Blocking items** (must resolve before Phase 1448b can execute):
- A1 — **RESOLVED 2026-05-25** — `tree_sha256: 925d6399399c7f82f52cf17318687a9d625d7e64ef2b0e2fc6586fd15c036361`
- A4 — **RESOLVED 2026-05-28** — Option A (fresh mirror); `Genesis Agent <ilcops@proton.me>`; push instructions recorded above
- CDL-095 — **RESOLVED 2026-05-25** — `cdl_095_ratified_phase_1448c` token emitted (Phase 1448c)
- E1 — **PENDING — BLOCKING** — patent counsel disposition: file 5 provisionals at USPTO (awaiting id.me / myUSPTO account access) OR record explicit deferred-risk authorization; token `patent_counsel_disposition_recorded_phase_1448a`
- G — **RESOLVED 2026-05-25** — `publication_target: https://github.com/ILC-Foundation/ilc`, `publication_tag: v0.3-public-rc`

**Summary:** One blocker remains — E1 (patent filing). All other pre-publication review items are resolved.
