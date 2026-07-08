# ILC Window 1565-1575 Remaining Phases Guidance (1573o–1575)

Status: planning guidance addendum
Date: 2026-07-08
Sensitivity: NON-SENSITIVE (document only; individual phases have their own classifications)
Routing authority: docs/specs/ilc_phase_1565_1575_sequence_lock_v0.1.md

## 1. Baseline

Window 1565-1575 sequence lock: docs/specs/ilc_phase_1565_1575_sequence_lock_v0.1.md
Last completed phase: 1573n (public mirror scanner hardening, 2026-07-08)
All OBL-001 through OBL-048: closed as of 2026-07-08
CDL-098 ratified: Phase 1573a
Capsule: docs/specs/ilc_antigravity_context_capsule_v5.41.md (or current at session)
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

### Track A — Governance / Canon (SENSITIVE)
- Phase 1573p: Canonical glossary amendment (star map disambiguation, tier vs graph_projection, group node taxonomy)
- Phase 1573r: Multi-slice encrustation model ADR (new ADR opening)
- Phase 1573u: CDL-029 Amendment #2 (C_max denominator constitutionalization)
- Phase 1573x: Inviter-chaining CDL opening (TBD CDL number, separate from CDL-091 which is ratified Jury Incentive Economics)
- Phase 1574: Publication readiness audit (SENSITIVE, human gate)
- Phase 1575: Genesis signing ceremony (SENSITIVE, human GO required)

### Track B — Spec Documents (NON-SENSITIVE)
- Phase 1573q: AtlasSliceManifest build pipeline spec + graph_projection naming policy spec
- Phase 1573o: OBL register sweep + pre-1573p coherence check

### Track C — Runtime Implementation (NON-SENSITIVE)
- Phase 1573t: Invite token CLI plumbing (InviteBatchRecord, InviteRedemptionRecord, ilc init --invite, three signing levels)
- Phase 1573v: genesis_accrual_governor.py runtime fix (C_max denominator)
- Phase 1573s: Fix65a/Fix65b LMDB coverage repair (sequential Atlas writes only)

### Track D — Simulation (NON-SENSITIVE)
- Phase 1573w: Canonical Genesis accumulation SIM (closes Phase 305 canonicalization checklist)

### Track E — LMDB Graph Enrichment (NON-SENSITIVE)
- Phase 1573y: ProjectionPolicyNode + SigningGroupRulesNode knowledge nodes in LMDB

### Track F — Closure (NON-SENSITIVE)
- Phase 1573z: Pre-1574 coherence report + capsule update

## 4. Ordered Phase Table

| Order | Phase | Topic | Sensitivity | Track |
|-------|-------|-------|-------------|-------|
| 1 | 1573o | OBL register sweep + coherence check | NON-SENSITIVE | B |
| 2 | 1573p | Canonical glossary amendment | SENSITIVE | A |
| 3 | 1573q | AtlasSliceManifest pipeline spec + projection naming policy | NON-SENSITIVE | B |
| 4 | 1573r | Multi-slice encrustation ADR opening | SENSITIVE | A |
| 5 | 1573s | Fix65a/b LMDB coverage repair | NON-SENSITIVE | C |
| 6 | 1573t | Invite token CLI plumbing | NON-SENSITIVE | C |
| 7 | 1573u | CDL-029 Amendment #2 (C_max denominator) | SENSITIVE | A |
| 8 | 1573v | genesis_accrual_governor.py runtime fix | NON-SENSITIVE | C |
| 9 | 1573w | Canonical Genesis accumulation SIM | NON-SENSITIVE | D |
| 10 | 1573x | Inviter-chaining CDL opening | SENSITIVE | A |
| 11 | 1573y | ProjectionPolicyNode + SigningGroupRulesNode LMDB nodes | NON-SENSITIVE | E |
| 12 | 1573z | Pre-1574 coherence + capsule | NON-SENSITIVE | F |
| 13 | 1574 | Publication readiness audit | SENSITIVE | A |
| 14 | 1575 | Genesis signing ceremony | SENSITIVE | A |

## 5. Post-RC Window 1576-1584 (Planned, Not Yet Sequenced)

| Order | Phase | Topic | Sensitivity |
|-------|-------|-------|-------------|
| 1 | 1576a | tier field elimination → graph_projection migration | NON-SENSITIVE |
| 2 | 1576b-g | Fix56–Fix65 LMDB coverage gap closure (per-node source_sha256) | NON-SENSITIVE series |
| 3 | 1576h | ADR-0009 Layer 0 bundle generator implementation | NON-SENSITIVE |
| 4 | 1576i | Homoiconic build pipeline CLI (ilc atlas build-slice, sign-manifest, verify-slice) | NON-SENSITIVE |
| 5 | 1576j | Layered star maps production (three AtlasSliceManifest variants signed by Genesis) | SENSITIVE |
| 6 | 1576k | Group node taxonomy ADR (repo_group, jury_group, SigningGroupRulesNode, GatedShardPolicyNode) | SENSITIVE |
| 7 | 1576l | GatedShardPolicyNode + SigningGroupRulesNode runtime implementation | NON-SENSITIVE |
| 8 | 1576m | Inviter-chaining CDL ratification | SENSITIVE |
| 9 | 1576n | Window 1576-1584 closure gate | SENSITIVE |

## 6. Critical Constraints

### No parallel LMDB writes
Atlas LMDB writes must be strictly sequential. Do not run parallel LMDB-mutating commands against the same LMDB root. (Standing rule reinforced at Phase 1573n-preflight.)

### CDL-091 disambiguation
CDL-091 is ALREADY RATIFIED as Jury Incentive Economics (Phase 1400). The inviter-chaining economics CDL is a FUTURE un-opened CDL with a TBD number. Never assign the inviter-chaining CDL as "CDL-091."

### Genesis 5% tranche — correct framing
The 5% is OBLIGATORY and GUARANTEED — Genesis receives 5% of each epoch's issuance until it has accumulated G_max = 1,296,000 ILC (theta_hard × C_max). At that point the Genesis tranche is cap-blocked and Genesis receives nothing more from new issuance. The sunset motivation is preventing Genesis dominance past the bootstrap phase. The current runtime (genesis_accrual_governor.py) uses issued_to_date denominator which immediately cap-blocks Genesis from epoch 1. Phase 1573u (CDL) and 1573v (runtime) fix this to use C_max as the denominator.

### star map canonical definition
"Star map" in ILC canon refers to a signed, content-addressed AtlasSliceManifest — a verifiable install/navigation guide for a specific graph projection slice. The term should NOT be used for: the ADR-0003/CDL-080 route index (call it "route index"), the genesis_core_star_map graph_projection label (call it "genesis_core projection"), or ADR-0033 navigational result nodes (call it "published navigation nodes"). The disambiguation note belongs in Phase 1573p.

### Signing levels (three)
Level 1 Autonomous: keys saved to OS keychain / machine key, zero friction, default
Level 2 Session: passphrase + in-memory cache (ssh-agent pattern), re-auth after timeout
Level 3 Manual: passphrase, never cached, sign each act individually
These are for Phase 1573t (invite + init CLI).

### InviteBatchRecord pattern
When Genesis creates a batch of N invite tokens: one InviteBatchRecord node written to graph (fields: inviter_cid, batch_id, count, nonce_merkle_root, created_epoch, inviter_sig). No per-token nodes created. Single-use enforcement: same nonce at redemption → same CID → graph rejects as duplicate. New user's identity node is NOT pre-created — it's created at redemption when the user's public key is known. Phase 1573t implements this.

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
