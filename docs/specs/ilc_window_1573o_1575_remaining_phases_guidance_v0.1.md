# ILC Window 1565-1575 Remaining Phases Guidance (1573o–1575)

> **Note (2026-07-08):** G8 package renumbered from 1573o-z to 1573u-1573af to avoid
> collision with the G10 CCSS lane (1573o complete; 1573p-r privacy work pending;
> 1573s ContactGateNode policy and 1573t ContactGate local rehearsal required). The
> phase table below reflects the updated G8 numbering. The complete G10 CCSS lane
> (1573p through 1573t) precedes the G8 package in execution order.

Status: planning guidance addendum
Date: 2026-07-08
Sensitivity: NON-SENSITIVE (document only; individual phases have their own classifications)
Routing authority: docs/specs/ilc_phase_1565_1575_sequence_lock_v0.1.md

## 1. Baseline

Window 1565-1575 sequence lock: docs/specs/ilc_phase_1565_1575_sequence_lock_v0.1.md
Last completed main-line phase at this planning cut: 1573o privacy-claim boundary (2026-07-08)
Phase 1573n public mirror rehearsal and scanner hardening: complete, evidence-only, no public push authority
OBL register status: not all rows are closed; pre-RC blockers are closed, routed, permanently invariant, or external-gated
CDL-098 ratified: Phase 1573a
Capsule: use the current highest-version context capsule in docs/specs/
Obligation register: docs/specs/ilc_open_obligation_register_v0.1.md

## 2. Sensitivity Classification Rules for This Block

SENSITIVE (requires human GO token before execution):
- Any phase that opens or ratifies a CDL row
- Any phase that opens or accepts an ADR
- Any phase that adds binding canonical term definitions to the glossary
- Phase 1574 (readiness audit — human gate)
- Phase 1575 (Genesis signing ceremony — human GO required, never self-authorize)

NON-SENSITIVE (may proceed after prompt approval; no additional GO token):
- Spec doc creation (no CDL/ADR mutation)
- Runtime implementation phases (ilc_core/ changes)
- Simulation/SIM execution
- LMDB repair and coverage work
- CLI plumbing (no CDL opening)
- Coherence / capsule update

Pre-commit hook required for all SENSITIVE CDL mutations:
ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=<phase>

## 3. Phase Track Inventory

### G10 CCSS Lane (preceding G8 — must complete first)
- Phase 1573p: CCSS metadata leakage audit (G10)
- Phase 1573q: CCSS side-channel SIM (G10)
- Phase 1573r: CCSS cover batching design (G10)
- Phase 1573s: ContactGateNode policy spec (G10, required)
- Phase 1573t: ContactGate local evaluator/rehearsal (G10, required unless 1573s records a hard blocker)

### Track A — Governance / Canon (SENSITIVE) — G8
- Phase 1573v: Canonical glossary amendment (star map disambiguation, tier vs graph_projection, group node taxonomy)
- Phase 1573x: Multi-slice encrustation model ADR (new ADR opening)
- Phase 1573aa: CDL-029 Amendment #2 (C_max denominator constitutionalization)
- Phase 1573ad: Inviter-chaining CDL opening (TBD CDL number, separate from CDL-091 which is ratified Jury Incentive Economics)
- Phase 1573aq: Inviter-chaining CDL prelock (SENSITIVE; depends on 1573z complete and 1573ad complete)
- Phase 1574: Publication readiness audit (SENSITIVE, human gate)
- Phase 1575: Genesis signing ceremony (SENSITIVE, human GO required; deliverables include signing three AtlasSliceManifest variants — see §4 and Decision 3 note)

### Track B — Spec Documents (NON-SENSITIVE) — G8
- Phase 1573w: AtlasSliceManifest build pipeline spec + graph_projection naming policy spec
- Phase 1573u: OBL register sweep + pre-1573v coherence check
- Phase 1573an: HB-002 full bootstrap gossip protocol design spec

### Track C — Runtime Implementation (NON-SENSITIVE) — G8
- Phase 1573z: Invite token CLI plumbing (InviteBatchRecord, InviteRedemptionRecord, invite-aware identity/agent init command, three signing levels)
- Phase 1573ab: genesis_accrual_governor.py runtime fix (C_max denominator)
- Phase 1573y: Fix65a/Fix65b LMDB coverage repair (sequential Atlas writes only)
- Phase 1573ao: ADR-0009 Layer 0 bundle generator canonical test vectors + CLI wiring (pulled forward from 1576h)
- Phase 1573ap: Homoiconic build pipeline CLI (ilc atlas build-slice, sign-manifest, verify-slice) (pulled forward from 1576i)

### Track D — Simulation (NON-SENSITIVE) — G8
- Phase 1573ac: Canonical Genesis accumulation SIM (closes Phase 305 canonicalization checklist)

### Track E — LMDB Graph Enrichment (NON-SENSITIVE) — G8
- Phase 1573ae: ProjectionPolicyNode + SigningGroupRulesNode knowledge nodes in LMDB

### Track F — Closure (NON-SENSITIVE) — G8
- Phase 1573af: Mid-block coherence check + capsule snapshot (runs before security G8 package; no longer the final pre-1574 coherence)
- Phase 1573ar: Pre-1574 final coherence report + capsule update (runs after ALL of 1573ak–1573aq)

## 4. Ordered Phase Table

| Order | Phase | Topic | Sensitivity | Track |
|-------|-------|-------|-------------|-------|
| 1 | 1573p | CCSS metadata leakage audit | NON-SENSITIVE | G10 |
| 2 | 1573q | CCSS side-channel SIM | NON-SENSITIVE | G10 |
| 3 | 1573r | CCSS cover batching design | NON-SENSITIVE | G10 |
| 4 | 1573s | ContactGateNode policy spec | NON-SENSITIVE | G10 |
| 5 | 1573t | ContactGate local evaluator/rehearsal | NON-SENSITIVE | G10 |
| 6 | 1573u | OBL register sweep + coherence check | NON-SENSITIVE | B/G8 |
| 7 | 1573v | Canonical glossary amendment | SENSITIVE | A/G8 |
| 8 | 1573w | AtlasSliceManifest pipeline spec + projection naming policy | NON-SENSITIVE | B/G8 |
| 9 | 1573x | Multi-slice encrustation ADR opening | SENSITIVE | A/G8 |
| 10 | 1573y | Fix65a/b LMDB coverage repair | NON-SENSITIVE | C/G8 |
| 11 | 1573z | Invite token CLI plumbing | NON-SENSITIVE | C/G8 |
| 12 | 1573aa | CDL-029 Amendment #2 (C_max denominator) | SENSITIVE | A/G8 |
| 13 | 1573ab | genesis_accrual_governor.py runtime fix | NON-SENSITIVE | C/G8 |
| 14 | 1573ac | Canonical Genesis accumulation SIM | NON-SENSITIVE | D/G8 |
| 15 | 1573ad | Inviter-chaining CDL opening | SENSITIVE | A/G8 |
| 16 | 1573ae | ProjectionPolicyNode + SigningGroupRulesNode LMDB nodes | NON-SENSITIVE | E/G8 |
| 17 | 1573af | Mid-block coherence check + capsule snapshot | NON-SENSITIVE | F/G8 |
| 18 | 1573ak | API ingress boundary audit | NON-SENSITIVE | G8 |
| 19 | 1573al | PUBLIC_RC_EXCLUDE import closure | NON-SENSITIVE | G8 |
| 20 | 1573am | Security runtime transactionality review | NON-SENSITIVE | G8 |
| 21 | 1573an | HB-002 full bootstrap gossip protocol design spec | NON-SENSITIVE | B/G8 |
| 22 | 1573ao | ADR-0009 bundle generator test vectors + CLI wiring | NON-SENSITIVE | C/G8 |
| 23 | 1573ap | Homoiconic build pipeline CLI (ilc atlas build-slice, sign-manifest, verify-slice) | NON-SENSITIVE | C/G8 |
| 24 | 1573aq | Inviter-chaining CDL prelock | SENSITIVE | A/G8 |
| 25 | 1573ar | Pre-1574 final coherence report + capsule update | NON-SENSITIVE | F/G8 |
| 26 | 1574 | Publication readiness audit | SENSITIVE | A |
| 27 | 1575 | Genesis signing ceremony (+ sign three AtlasSliceManifest variants) | SENSITIVE | A |

## 5. Post-RC Window 1576-1584 (Planned, Not Yet Sequenced)

**Note:** 1576h (ADR-0009 bundle generator implementation) and 1576i (homoiconic build
pipeline CLI) have been pulled forward as pre-RC phases 1573ao and 1573ap respectively.
1576j (layered star maps — three AtlasSliceManifest variants) has been folded into Phase
1575 Genesis signing ceremony deliverables. The entries below reflect these removals.

| Order | Phase | Topic | Sensitivity |
|-------|-------|-------|-------------|
| 1 | 1576a | tier field elimination → graph_projection migration | NON-SENSITIVE |
| 2 | 1576b-g | Fix56–Fix65 LMDB coverage gap closure (per-node source_sha256) | NON-SENSITIVE series |
| 3 | 1576k | Group node taxonomy ADR (repo_group, jury_group, SigningGroupRulesNode, GatedShardPolicyNode) | SENSITIVE |
| 4 | 1576l | GatedShardPolicyNode + SigningGroupRulesNode runtime implementation | NON-SENSITIVE |
| 5 | 1576m | Inviter-chaining CDL ratification | SENSITIVE — Pre-RC prelock completed at Phase 1573aq; ratification requires evidence from live network invite chains (not devnet-only). |
| 6 | 1576-HB002 | HB-002 full — Full peer-to-peer bootstrap protocol implementation (new node receives signed genesis artifacts from any peer, verifies, reconstructs state). Requires: live external operators, 1573an spec compliance, serving receipt integration. | NON-SENSITIVE implementation; SENSITIVE wire protocol deployment gate |
| 7 | 1576n | Window 1576-1584 closure gate | SENSITIVE |

## 6. Critical Constraints

### No parallel LMDB writes
Atlas LMDB writes must be strictly sequential. Do not run parallel LMDB-mutating commands against the same LMDB root. (Standing rule reinforced at Phase 1573n-preflight.)

### CDL-091 disambiguation
CDL-091 is ALREADY RATIFIED as Jury Incentive Economics (Phase 1400). The inviter-chaining economics CDL is a FUTURE un-opened CDL with a TBD number. Never assign the inviter-chaining CDL as "CDL-091."

### Genesis 5% tranche — correct framing
The 5% is OBLIGATORY and GUARANTEED as a design target — Genesis receives 5% of each epoch's issuance until it has accumulated G_max = 1,296,000 ILC (theta_hard × C_max). At that point the Genesis tranche is cap-blocked and Genesis receives nothing more from new issuance. The sunset motivation is preventing Genesis dominance past the bootstrap phase. The current analysis governor (`genesis_accrual_governor.py`) uses issued_to_date denominator which immediately cap-blocks Genesis from epoch 1. Phase 1573aa (CDL) and 1573ab (analysis-runtime/conformance fix) correct the denominator to C_max. The live Decimal allocation distributor remains the monetary authority and remains default-off unless a later SENSITIVE value-path phase wires production settlement.

### star map canonical definition
"Star map" in ILC canon refers to a signed, content-addressed AtlasSliceManifest — a verifiable install/navigation guide for a specific graph projection slice. The term should NOT be used for: the ADR-0003/CDL-080 route index (call it "route index"), the genesis_core_star_map graph_projection label (call it "genesis_core projection"), or ADR-0033 navigational result nodes (call it "published navigation nodes"). The disambiguation note belongs in Phase 1573v.

### Signing levels (three)
Level 1 Autonomous: keys saved to OS keychain / machine key, zero friction, default
Level 2 Session: passphrase + in-memory cache (ssh-agent pattern), re-auth after timeout
Level 3 Manual: passphrase, never cached, sign each act individually
These are for Phase 1573z (invite + init CLI).

### InviteBatchRecord pattern
When Genesis creates a batch of N invite tokens: one InviteBatchRecord node written to graph (fields: inviter_cid, batch_id, count, nonce_merkle_root, created_epoch, inviter_sig). No per-token nodes created. Redemption must not persist raw nonces in permanent graph records. Single-use enforcement should use a deterministic redemption nullifier, e.g. `sha256("ilc-invite-nullifier-v1:" || batch_id || nonce)`, so repeat redemption produces the same public nullifier while the nonce remains private. New user's identity node is NOT pre-created — it is created at redemption when the user's public key is known. Phase 1573z implements local/default-off plumbing only; Phase 1573ad opens the separate inviter-chaining economics CDL.

### Pre-RC / post-RC split for HB-002 and inviter-chaining CDL

- Phase 1573an defines the bootstrap gossip protocol wire format spec. Phases 1573ao and 1573ap must implement to this spec. Any deviation discovered post-RC requires an amendment to 1573an, not a silent refactor.
- Phase 1573aq prelocks the inviter-chaining CDL parameters. Phase 1573z's InviteBatchRecord / InviteRedemptionRecord implementation is the implementation record for those parameters. If 1573z introduces a parameter not captured in 1573aq's prelock, that is a CDL-amendment obligation to carry forward.
- Phase 1576m CDL ratification requires: the CDL has been prelocked (1573aq token present), and at least one full invite-chain creation + redemption has been observed on the live network. Do not ratify from devnet-only evidence.
- HB-002 full implementation (post-RC) must pass: new external node bootstraps genesis artifacts from an existing peer without any out-of-band file copy or GitHub clone. Test against a real external operator node, not a local VPS.

### Phase 1575 deliverables — AtlasSliceManifest signing

Signing three AtlasSliceManifest variants is an explicit deliverable of Phase 1575 (Genesis signing ceremony). The three variants correspond to the layered star map tiers defined in 1573w and implemented in 1573ap. Do not create a separate 1576j phase for this — the Genesis signing ceremony is the correct authority gate.

### ContactGateNode pattern
Agent INIT nodes can be public, but inbound sealed-message authorization should route through a ContactGateNode/capability context rather than through a global "anyone can message any agent" rule. Contact gates support public-open, contacts-only, capability-required, private-invite-only, and closed modes. Public gate manifests may be graph-visible; private gate capabilities must remain opaque and must be committed through CCSS route-token/sealed-payload context, not relay-visible metadata. Phases 1573s and 1573t specify and rehearse this boundary before public RC.

## 7. Key Canonical Anchors for Prompt Drafting

- CDL-098 ratification evidence: docs/specs/ilc_cdl_098_genesis_graph_update_authority_ratification_evidence_1573a_v0.1.md
- CDL-029 current evidence: docs/specs/ilc_cdl_029_allocation_split_ratification_evidence_272_v0.1.md
- CDL-029 Amendment 1351a: docs/specs/ilc_cdl_029_post_theta_hard_dust_routing_amendment_1351a_v0.1.md
- Genesis accrual governor: ilc_core/analysis/genesis_accrual_governor.py
- Allocation distributor: ilc_core/epoch/allocation_distributor_runtime.py
- Genesis accumulation dynamics: docs/specs/ilc_genesis_accumulation_dynamics_analysis_298_v0.3.md
- Phase 305 canonicalization checklist: docs/specs/ilc_phase_305_genesis_accumulation_canonicalization_checklist_v0.1.md
- Private layer policy: docs/specs/ilc_private_layer_policy_v0.1.md
- Canonical glossary: docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md
- Invitation provenance: ilc_core/genesis/invitation_provenance_record.py
- Phase 1573 forward plan: docs/specs/ilc_genesis_graph_authority_and_pre_rc_completeness_forward_plan_v0.1.md

## 8. Non-Goals For This Phase Block

- Do not activate public RC, public P2P, public relay serving
- Do not write wallet, treasury, mint, settlement, or ledger state
- Do not sign out/genesis_base_graph_v0.4.json until Phase 1575 with explicit GO
- Do not open CDL-099 definition-node instances
- Do not activate ADR-0035 type registry
- Do not push public mirror until Phase 1575 authority chain is established
