# ILC Phase 1317-1329 Sequence Lock v0.1

**Date:** 2026-05-12
**Window:** 1317-1329
**Phase:** 1317
**Status:** LOCKED THROUGH PHASE 1317 ONLY
**Human authorization:** `GO Phase 1317`
**Token:** `window_1317_1329_sequence_lock_committed`

---

## 1. Sequence Lock Verdict

Window 1317-1329 is opened after explicit human authorization:

```text
GO Phase 1317
```

Verdict:

```text
window_1317_1329_sequence_lock_committed
window_1317_1329_sequence_lock_verdict=pass
phase_1318_context_capsule_v5_54_refresh_next
window_1317_1329_no_publication_signing_or_public_activation
release_dry_run_private_only_sequence_locked_phase_1317
ccss_tail_routed_without_atlas_g_compression_phase_1317
human_question_escalation_required_for_uncertain_authority
```

This is a sequence-lock phase only. It opens the release dry-run and
Confidential Coordination Sidecar Suite window, records the locked phase order,
and consumes the draft Window 1317-1329 grouping. It does not execute Phase
1318, perform materialization rehearsal, export source, publish source or
packages, produce release artifacts, generate keys or envelopes, sign anything,
activate public claimability, activate public P2P/fetch/sidecar serving,
activate wallet-facing value actions, mint ECU, settle ILC, mutate Genesis
Atlas, sign v0.2, or claim public confidential coordination.

Phase 1318 is the next planned phase and is a non-sensitive docs/canon capsule
refresh after this lock. The user's authorization for this phase was only
`GO Phase 1317`, so execution stops after Phase 1317 unless the human reviewer
later authorizes Phase 1318 or a continue-through-non-sensitive instruction.

---

## 2. Baseline Inputs And Canon

| Input | Window-entry role |
|-------|-------------------|
| `docs/PLANNING_INDEX.md` | Current planning frontier after Phase 1316 closure and draft Window 1317-1329 guidance. |
| `docs/specs/ilc_antigravity_context_capsule_v5.53.md` | Current capsule through Window 1303-1316 closure; v5.54 is next. |
| `docs/phases/STATUS.md` | Actual status through Phase 1316 before this sequence lock. |
| `docs/specs/ilc_window_1303_1316_handoff_1316_v0.1.md` | Closed-window baseline and carry-forward blocker list. |
| `docs/specs/ilc_window_1317_1329_candidate_phase_grouping_v0.1.md` | Candidate release dry-run and CCSS guidance consumed by this lock. |
| `docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.1.md` | Forward plan for release dry-run, CCSS tail, final RC, packaging, and signing gates. |
| `docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md` | Materialized-public-tree rule and `PUBLIC_RC_EXCLUDE` disposition model. |
| `docs/architecture/ilc_graph_native_sidecar_suite_architecture_v0.1.md` | Harness-agnostic graph-native sidecar suite architecture. |
| `docs/architecture/ilc_confidential_coordination_sidecar_suite_forward_plan_v0.1.md` | Private/local confidential coordination sidecar routing. |
| `docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md` | Controlling public-RC blocker map. |
| `docs/specs/ilc_constitutional_decision_log_v0.1.md` | CDL register; CDL-087 is ratified and CDL-088 is not opened. |

Standing retrieval rule:

```text
historical_retrieval_is_context_not_authority_current_canon_controls
unknown_unknown_discovery_required_before_phase_execution
```

---

## 3. Entry Discovery Audit

| Check | Result |
|-------|--------|
| Section 0a Known-token audit | Required Phase 1317 tokens were searched before this lock. Before this packet, Phase 1317-specific tokens existed only in the Phase 1317 prompt, candidate grouping, planning index, and prompt-draft tests; they are now published in this lock, PLANNING_INDEX, STATUS, walkthrough, and focused tests. |
| Section 0b Concept-discovery search | Searched release dry run, source allowlist, materialization, release manifest, key envelope, signing rehearsal, three-machine, seven-agent, OpenClaw, NemoClaw, sidecar suite, Confidential Coordination Sidecar Suite, CCSS, Atlas-G tail, public RC, publication, and activation. |
| Section 0c Contradiction and non-claim search | Searched deferred, blocked, not authorized, not ratified, prelocked, superseded, local-only, private/local, no public, does not imply, must not, not open, carry-forward, CDL-088, v0.2 signing, source export, and public confidential coordination serving. No source granted publication, signing, public serving, public claimability, source export, release artifact, wallet/ECU/ILC economics, Genesis mutation/signing, CDL mutation, or public confidential coordination authority. |
| Section 0d Source expansion | Direct-read the current planning index, Capsule v5.53, STATUS tail, Phase 1316 handoff, Window 1317-1329 guidance, forward packaging/signing plan, public-RC packaging architecture gate, graph-native sidecar suite architecture, CCSS forward plan, roadmap, CDL register, and prompt/test scaffolding. MemPalace tier_b planning query returned historical and stale planning hits only; no returned hit superseded current repo canon. |

Exact-token `rg` remains only a schema and completion check. Future phases in
this window must also search token components, synonyms, neighboring concepts,
older names, code symbols, file/path variants, historical literature, and
denial terms before treating a blocker or implementation concept as absent.

---

## 4. Claim Verification Table

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Human authorized Phase 1317 | Current user instruction `GO Phase 1317` | confirmed |
| Phase 1316 is complete and closed Window 1303-1316 | `docs/phases/STATUS.md`, `docs/PLANNING_INDEX.md`, `docs/specs/ilc_window_1303_1316_handoff_1316_v0.1.md` | confirmed |
| Window 1317-1329 was draft guidance before this lock | `docs/specs/ilc_window_1317_1329_candidate_phase_grouping_v0.1.md`, `docs/PLANNING_INDEX.md` | confirmed |
| No superseding Phase 1317 sequence lock existed before this artifact | `rg` over `docs`, `tests`, `ilc_core`, `tools`, and `automation` | confirmed |
| CDL-087 is ratified and CDL-088 is not opened | `docs/specs/ilc_constitutional_decision_log_v0.1.md` | confirmed |
| Public RC remains blocked after Phase 1316 | Phase 1316 handoff, Capsule v5.53, Roadmap v1.1, PLANNING_INDEX | confirmed |
| Phase 1319 is rehearsal only and not source export execution | Window 1317-1329 guidance and packaging architecture gate | confirmed |
| Phases 1320-1321 are rehearsal only and produce no release keys, envelopes, artifacts, or signatures | Forward plan and Window 1317-1329 guidance | confirmed |
| OpenClaw/NemoClaw are harness/deployment targets, not protocol substrates | Graph-native sidecar architecture and CCSS forward plan | confirmed |
| CCSS phases 1324-1328 are private/local and do not replace Atlas-G tail signing prerequisites | Window 1317-1329 guidance, forward plan, CCSS forward plan | confirmed |

---

## 5. Locked Phase Order

| Order | Phase | Scope | Sensitivity | Authorization boundary |
|-------|-------|-------|-------------|------------------------|
| 1 | 1317 | Window 1317-1329 sequence lock | SENSITIVE | Executed by `GO Phase 1317`; opens no publication, signing, public-RC, public-serving, or value-path authority. |
| 2 | 1318 | Context Capsule v5.54 frontier refresh | NON-SENSITIVE docs/canon refresh after Phase 1317 | Next planned phase; not executed by this lock. |
| 3 | 1319 | Deterministic source allowlist export rehearsal | SENSITIVE | Dry-run materialization only; not source export execution or publication. |
| 4 | 1320 | Release artifact manifest instance rehearsal | SENSITIVE | Manifest shape rehearsal only; no public artifacts. |
| 5 | 1321 | Release key/envelope procedure rehearsal | SENSITIVE | Procedure rehearsal only; no real key generation, envelope production, or signing. |
| 6 | 1322 | Three-machine/seven-agent private deployment rehearsal with essential graph-native sidecar suite | SENSITIVE | Private deployment evidence only; no public serving claim. |
| 7 | 1323 | OpenClaw/NemoClaw claimable profile full dry run against graph-native sidecar suite | SENSITIVE | Profile dry run only; public claimability remains gated. |
| 8 | 1324 | CCSS-001 private/gated shard sidecar contract | SENSITIVE | Private/local contract only; no public confidential coordination serving. |
| 9 | 1325 | CCSS-002 capability, membership, grant, revocation, and optional ZK interface boundary | SENSITIVE | Private/local boundary only; no plaintext or membership disclosure claim. |
| 10 | 1326 | CCSS-003 sealed sender local delivery sidecar boundary | SENSITIVE | Local/private delivery boundary only; no public P2P activation. |
| 11 | 1327 | CCSS-004 gossip announce/pull, jitter, batching, cover-policy, and traffic-analysis tests | SENSITIVE | Privacy hardening tests only; no anonymity guarantee. |
| 12 | 1328 | CCSS-005 private OpenClaw/NemoClaw confidential coordination droplet dry run plus reproducibility pass | SENSITIVE | Private harness evidence only; no public serving claim. |
| 13 | 1329 | Window closure gate | SENSITIVE | Closure/classification only. |

---

## 6. Stop Conditions

| Stop condition | Required action |
|----------------|-----------------|
| Capsule v5.53 is missing, superseded without v5.54 routing, or contradicts the Phase 1316 handoff | Stop and ask for human review before opening the window. |
| Phase 1316 handoff is missing or does not record `window_1317_plus_sequence_lock_required_before_next_phase_assignment` | Stop and ask for human review. |
| A competing or superseding Window 1317+ sequence lock exists | Stop unless this artifact explicitly supersedes it with evidence. |
| Atlas-G tail work is hidden inside CCSS phases 1324-1328 | Stop and split the work or reroute CCSS to a later dedicated sidecar window. |
| Any phase text implies publication, signing, public serving, public claimability, source export execution, release artifact production, wallet-facing activation, ECU minting, ILC settlement, CDL-088 opening, Genesis mutation/signing, v0.2 signing, or public confidential coordination authority | Stop and narrow to no-authorization wording. |
| DigitalOcean/OpenClaw/NemoClaw dry-run plans require public inbound ports, unmanaged secrets, or public P2P | Stop and require private/loopback/Tailscale-style wiring or carry forward the blocker. |

No stop condition was triggered during Phase 1317.

---

## 7. Release Dry-Run Boundary

Phase 1319 is locked as deterministic source allowlist export rehearsal only.
It must prove zero exported `PUBLIC_RC_EXCLUDE` markers, zero stripped-helper imports,
deterministic file hashes, legacy-untagged review results, and
explicit non-claims. It is not source allowlist export execution, public source
publication, package publication, clean public tree production, or a public-RC
claim.
Phrase guard: not source allowlist export execution, public source publication, package publication.

Phases 1320 and 1321 are locked as release manifest and signing procedure
rehearsals only. They must not produce public release artifacts, release keys,
release envelopes, release signing material, or signatures.
Phrase guard: release manifest and signing procedure rehearsals only; must not produce public release artifacts, release keys, release envelopes.

---

## 8. CCSS And Atlas-G Split

The CCSS tail is routed without Atlas-G compression:

```text
ccss_tail_routed_without_atlas_g_compression_phase_1317
```

Phases 1324-1328 are private/local Confidential Coordination Sidecar Suite
phases only if later authorized. They are not substitutes for ATLAS-G-007
through ATLAS-G-010. Atlas-G tail work remains required before signing and
must be completed or explicitly carried forward before any signing gate can
pass.

OpenClaw and NemoClaw remain harness/deployment targets. They are not protocol substrates
and do not own ledger truth.

---

## 9. Human Escalation Rule

If a phase discovers a decision that cannot be resolved from committed canon and
would widen authority, mutate a CDL row, open CDL-088, enable public exposure,
enable claimability/spend semantics, publish source, produce release artifacts,
generate or sign release material, mutate or sign Genesis Atlas, sign v0.2,
activate public confidential messaging or coordination serving, or choose
between conflicting Atlas-G/CCSS priority routes, the phase must stop and prompt
the human reviewer. In shorthand for future prompt audits: the phase must stop
and prompt the human reviewer before widening authority; it must stop and prompt the human reviewer.

```text
default_to_no_authorization_when_canon_is_ambiguous
human_question_escalation_required_for_uncertain_authority
```

---

## 10. Non-Authorization Boundary

Phase 1317 does not authorize public RC claim, public launch claim, public
repository publication, public package publication, source allowlist export
execution, source publication, materialized export manifest production, clean
public export tree production, release artifact production, release artifact
manifest instance production, release-key generation, release envelope
production, release signing material generation, public claimability
activation, public claimability API activation, public verifier service
activation, public claim endpoint activation, public P2P exposure, public
fetch serving, public sidecar/projection serving, non-loopback bind, wildcard
bind, public host bind, public listener, socket listener, HTTP route
activation, peer discovery, TransportPrincipal public-path activation, public
credential issuer authority, credential lifecycle policy activation, public
revocation registry activation, public replay cache activation, admission
policy activation, ban registry activation, public rate-limit state
activation, privacy policy activation, helper promotion, marker removal,
helper stripping, CDL mutation, CDL-088 opening, Genesis Atlas mutation,
Genesis Atlas regeneration, Genesis Atlas signing, v0.2 signing, IP filing,
paper publication, patent-sensitive public disclosure, public confidential
messaging, public confidential coordination serving, wallet-facing withdrawal
request, wallet-facing transfer request, wallet-facing spend request,
wallet-provider signing authority, wallet-provider ledger-write authority,
wallet write authority, ECU minting, ILC settlement, withdrawal runtime
activation, value-path activation, immutable diagnostic mutation, or
production `commit.epoch` emission.

Exact non-authorization phrase guard:

```text
public RC claim
public claimability API activation
public verifier service activation
public P2P exposure
public fetch serving
public sidecar/projection serving
source allowlist export execution
release artifact production
release-key generation
release envelope production
release signing material generation
helper promotion
marker removal
helper stripping
Genesis Atlas mutation/regeneration/signing
v0.2 signing
CDL-088 opening
wallet-facing withdrawal request
wallet-facing transfer request
wallet-facing spend request
ECU minting
ILC settlement
public confidential messaging
public confidential coordination serving
```

---

## 11. Graph Delta

```text
graph_delta=support_only:docs/specs/ilc_phase_1317_1329_sequence_lock_v0.1.md -> planning/frontier
graph_delta=support_only:docs/specs/ilc_window_1317_1329_candidate_phase_grouping_v0.1.md -> planning/frontier
graph_delta=support_tests_added:tests/test_phase_1317_window_1317_1329_sequence_lock.py -> validation
graph_delta=support_only:docs/phases/phase_1317_window_1317_1329_sequence_lock_walkthrough.md -> planning/frontier
graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier
graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier
```

No signed Genesis artifact, Genesis Atlas artifact, CDL row, release artifact,
package export, public source tree, runtime surface, or economics surface is
mutated by this lock.

---

## 12. Verification Record

Required verification for Phase 1317:

```bash
.venv/bin/python -m pytest tests/test_phase_1317_window_1317_1329_sequence_lock.py tests/test_window_1317_1329_prompt_drafts.py
.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py
.venv/bin/python tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_1317_g8_window_1317_1329_sequence_lock.md
git diff -- docs/specs/ilc_constitutional_decision_log_v0.1.md
git diff --check -- docs/specs/ilc_phase_1317_1329_sequence_lock_v0.1.md docs/specs/ilc_window_1317_1329_candidate_phase_grouping_v0.1.md docs/PLANNING_INDEX.md docs/phases/STATUS.md docs/phases/phase_1317_window_1317_1329_sequence_lock_walkthrough.md tests/test_phase_1317_window_1317_1329_sequence_lock.py tests/test_window_1317_1329_prompt_drafts.py
```

Observed result: focused Phase 1317 and Window 1317-1329 prompt-draft tests
passed (`22 passed`), the Phase 1317 prompt validator returned `VALID`,
the sensitive-runtime guardrail returned `PASS`, the CDL register diff was
empty, and scoped `git diff --check` passed.

## 13. Next Phase

Phase 1318 is the next planned phase and is a non-sensitive capsule refresh.
It is not executed by this sequence lock.

```text
phase_1318_context_capsule_v5_54_refresh_next
```
