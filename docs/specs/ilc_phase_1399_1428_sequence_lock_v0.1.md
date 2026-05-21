# ILC Phase 1399-1428 Sequence Lock v0.1

**Status:** Active sequence lock - Window 1399-1428 is OPEN; Phase 1427 J-008 gate re-run complete; Phase 1428 window closure gate is next and SENSITIVE
**Date:** 2026-05-20
**Owner lane:** G8 Jury Economy / Launch Readiness
**GO authority:** Human reviewer (explicit `GO` received 2026-05-20)

```text
window_1399_1428_sequence_lock_committed_phase_1399_entry
go_window_1399_1428_authorized_2026_05_20
phase_1399_is_first_phase
```

**Phase 1399 completion addendum:** CDL-091 formal opening C1 committed as
`06993864`; prelock C2 committed as `d2b4181d`. CDL-091 is now `open`
and prelocked, not ratified. Phase 1400 is the next phase and remains
SENSITIVE.

**Phase 1400 completion addendum:** CDL-091 ratification evidence C1 committed
as `577c8ad5`; CDL register mutation C2 committed as `694d7779`. CDL-091 is now
`ratified`. Reviewer payment remains inactive. Phase 1401 CDL-091 runtime stub
is next and NON-SENSITIVE.

**Phase 1401 completion addendum:** CDL-091 runtime stub committed as
`9bd4918f`. Reviewer payment remains inactive. Phase 1402
CDL-092 CapProof opening is next and SENSITIVE.

**Phase 1402 completion addendum:** CDL-092 CapProof opening scope C1 committed
as `79675d68`; CDL register opening C2 committed as `5d3ef87d`. CDL-092 is now
`open` and unratified. CapProof pricing, production probe execution, direct ILC
reward, and J-008 gate verdict changes remain unauthorized. Phase 1403 CDL-092
deliberation is next and NON-SENSITIVE.

**Phase 1403 completion addendum:** CDL-092 CapProof deliberation committed as
`e3a5a0a9`. Q1-Q4 are resolved into candidate prelock constants for
Phase 1404. CDL-092 remains open and unratified. No CDL mutation, CapProof
pricing activation, production probe execution, direct ILC reward, or J-008 gate
verdict change occurred. Phase 1404 CDL-092 prelock is next and NON-SENSITIVE.

**Phase 1404 completion addendum:** CDL-092 CapProof prelock committed as
`608096a3`. The Phase 1403 content-address carry-forward is resolved
to the accepted ADR-0001 NodeID profile
`adr_0001_nodeid_cidv1_dag_cbor_sha2_256_multihash`. CDL-092 remains open and
unratified. No CDL mutation, CapProof pricing activation, production probe
execution, direct ILC reward, or J-008 gate verdict change occurred. Phase 1405
CDL-092 ratification is next and SENSITIVE.

**Phase 1405 completion addendum:** CDL-092 CapProof ratification evidence C1
committed as `046045b6`; CDL register mutation C2 committed as `e97d9e4b`.
CDL-092 is now `ratified`. CapProof pricing, production probe execution, direct
ILC reward, runtime activation, and J-008 gate verdict changes remain
unauthorized. Phase 1406 CDL-093 maintenance lottery pool opening is next and
SENSITIVE.

**Phase 1406 completion addendum:** CDL-093 maintenance lottery pool opening C1
committed as `67a14d0d`; CDL register opening C2 committed as `15992abe`.
CDL-093 is now `open` and unratified. Maintenance lottery distribution, live
draws, ECU settlement, runtime activation, and J-008 gate verdict changes remain
unauthorized. Phase 1407 CDL-093 deliberation/prelock is next and NON-SENSITIVE.

**Phase 1407 completion addendum:** CDL-093 maintenance lottery pool
deliberation/prelock committed as `9eaffd74`. Production draw requires VRF
or a later-ratified randomness source; epoch-hash is shadow quote only. Funding
source is the CDL-047 treasury-governance quote family, but nonzero funding
fraction is SIM-pending and the live fraction defaults to `Decimal("0.00")`.
CDL-093 remains open and unratified. No CDL mutation, maintenance lottery
distribution, live draw, ECU settlement, runtime activation, or J-008 gate
verdict change occurred. Phase 1408 CDL-093 ratification is next and SENSITIVE.

**Phase 1407-Fix0 completion addendum:** CDL-053 Werner local productive-credit
opening document/tests C1 committed as `b5c638bc`; CDL register opening mutation
C2 committed as `36d3b698` with
`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1407_fix0`. CDL-053 is now
`open` and unratified. The opened scope is maintenance-equivalent reviewed
productive work only, local non-settlement credit eligibility only, with Phase
1263 direct-Werner-ECU rejection preserved. Phase 1407-Fix1 CDL-053 prelock is
next and NON-SENSITIVE.

**Phase 1407-Fix1 completion addendum:** CDL-053 Werner local productive-credit
prelock committed as `d302544b`. Scope constants lock productive credit to
review-lane-passed maintenance tasks only, local non-settlement/non-wallet
credit only, CDL-085 phi-bound inheritance only for provenance-equivalent
edge-mint outputs, and no direct Werner ECU creation. CDL-053 remains open and
unratified. No CDL mutation, CDL-093 mutation, runtime activation, settlement,
wallet behavior, live distribution, or J-008 gate verdict change occurred.
Phase 1407-Fix2 CDL-053 ratification is next and SENSITIVE.

**Phase 1407-Fix2 completion addendum:** CDL-053 ratification evidence C1
committed as `aa8e7e9a`; CDL register mutation C2 committed as `f654bacc` with
`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1407_fix2`. CDL-053 is now
`ratified`. The ratified scope is narrow Werner local productive credit for
review-lane-passed maintenance work only; no direct Werner ECU creation, runtime
activation, wallet mutation, settlement, live distribution, or J-008 gate verdict
change occurred. Phase 1407-Fix3 CDL-093 prelock amendment and Q2 SIM is next
and NON-SENSITIVE.

**Phase 1407-Fix3 completion addendum:** CDL-093 prelock amendment and Q2 SIM
committed as `33cf09da`. The Q2 source is amended from CDL-047 treasury
candidate to ratified CDL-053 Werner local productive credit; distribution path
is amended to the CDL-053 default-off runtime-stub path; SIM pending is resolved
to `false`; and the recommended funding fraction is `Decimal("0.10")`. CDL-093
remains open and unratified. No CDL mutation, runtime activation, live
distribution, settlement, wallet behavior, or J-008 gate verdict change
occurred. Phase 1408 CDL-093 ratification is next and SENSITIVE.

**Phase 1408 completion addendum:** CDL-093 maintenance lottery pool
ratification evidence C1 committed as `851e8e8b`; CDL register mutation C2
committed as `86e84c9f` with
`ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1408`. CDL-093 is now
`ratified`. Ratification uses the Phase 1407-Fix3 Werner source and
`MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION = Decimal("0.10")`; maintenance
lottery distribution, live draws, ECU settlement, runtime activation, wallet
behavior, and J-008 gate verdict changes remain unauthorized. Phase 1409
CDL-093 maintenance lottery runtime stub is next and NON-SENSITIVE.

**Phase 1409 completion addendum:** CDL-093 maintenance lottery runtime stub
committed in this phase. `ilc_core/epistemic/maintenance_lottery_runtime.py`
records `maintenance_lottery_runtime_stub_committed_phase_1409`,
`maintenance_lottery_not_activated_phase_1409`, and
`MAINTENANCE_LOTTERY_CDL_RATIFIED_TOKEN = "cdl_093_ratified_phase_1408"`.
The stub wires the ratified Werner source and
`MAINTENANCE_LOTTERY_POOL_FUNDING_FRACTION = Decimal("0.10")` while keeping
`MAINTENANCE_LOTTERY_NOT_ACTIVATED = True`. No live draw, ECU distribution,
ledger write, treasury write, wallet behavior, runtime activation, or J-008
gate verdict change occurred. Phase 1410 VRF proof verifier ADR is next and
NON-SENSITIVE.

**Phase 1410 completion addendum:** ADR-0042 VRF proof verifier specification
committed in this phase. `docs/adr/ADR_0042_VRF_Proof_Verifier.md` records
`vrf_proof_verifier_adr_accepted_phase_1410` and
`vrf_proof_verifier_not_activated_phase_1410`, selects RFC 9381
`ECVRF-EDWARDS25519-SHA512-ELL2`, pins `PyNaCl==1.6.2` as the support library
for Phase 1411, and defines the proof format, alpha canonicalization,
verification API, and Phase 1412 integration contract. No VRF runtime,
assignment runtime mutation, proof generation, production activation, or J-008
gate verdict change occurred. Phase 1411 VRF proof verifier implementation is
next and NON-SENSITIVE.

**Phase 1410-Fix1 completion addendum:** Pre-VRF hardening committed in this
phase. The phase fixes six Phase 1410 audit findings: epoch-zero claimability
validation, duplicate eligible-agent rejection in jury assignment, typed claim
nullifier canonical-JSON errors, ejected-stake residual quantization,
treasury remaining-budget quantization, and ingestion lifecycle `from_state`
trace accuracy. ADR-0042 now records
`vrf_pynacl_api_gap_documented_phase_1410_fix1`, requiring Phase 1411 to validate
PyNaCl low-level Ed25519 binding use against RFC 9381 Appendix B.4 before any
integration claim. No CDL mutation, VRF implementation, production activation,
or J-008 gate verdict change occurred. Phase 1411 remains next and
NON-SENSITIVE.

**Phase 1411 completion addendum:** VRF proof verifier implementation committed
in this phase. `ilc_core/epistemic/vrf_proof_verifier.py` records
`vrf_proof_verifier_implemented_phase_1411`,
`vrf_proof_verifier_phase_1411.v0.1`, and
`vrf_proof_verifier_not_activated_phase_1410`; `PyNaCl==1.6.2` is pinned in
dependency files. Official RFC 9381 Appendix B.4 examples 19, 20, and 21 verify
successfully, including hash-to-curve `H` and `beta` output checks. No proof
generation, jury-assignment integration, production activation, J-008 gate
verdict change, ledger/treasury/wallet mutation, graph mutation, or CDL
mutation occurred. Phase 1412 VRF jury-assignment integration is next and
NON-SENSITIVE.

**Phase 1412 completion addendum:** VRF jury-assignment integration committed in
this phase. `ilc_core/epistemic/jury_assignment_runtime.py` records
`vrf_verifier_integrated_jury_assignment_phase_1412` and adds a high-value
audit-only VRF ordering path using externally supplied proof material verified
by the Phase 1411 verifier. Epoch-hash shadow assignment remains the default
non-high-value path; candidate ordering for high-value audit quotes is
`(beta_bytes, agent_id)` ascending; missing or invalid proof material excludes
the candidate with visible audit reasons. `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED`
remains `True`; non-audit high-value assignment fails closed, and no proof
generation, private-key handling, production activation, J-008 gate verdict
change, ledger/treasury/wallet mutation, graph mutation, or CDL mutation
occurred. Phase 1413 VRF integration tests and security review is next and
NON-SENSITIVE.

**Phase 1413 completion addendum:** VRF integration tests and security review
committed in this phase. `tests/test_phase_1413_vrf_integration.py` records
`vrf_integration_tests_complete_phase_1413` and verifies Phase 1411 verifier
behavior, Phase 1412 audit-only high-value VRF jury ordering, invalid-candidate
exclusion reporting, unchanged epoch-hash shadow assignment, runtime no-PRNG and
no-production-assert hygiene, no private-key or proof-generation paths across
Phase 1411-1413 verifier/integration/test files, and J-008
`VRF_VERIFIER_IMPLEMENTED` still `NOT_MET`. The VRF track is complete at ADR,
verifier, integration, and focused test layers; no runtime source mutation,
production activation, J-008 gate verdict change, ledger/treasury/wallet
mutation, graph mutation, or CDL mutation occurred. Phase 1414 review lane wiring
ADR is next and NON-SENSITIVE.

**Phase 1414 completion addendum:** Review lane wiring ADR committed in this
phase. `docs/adr/ADR_0043_Review_Lane_T0_5_To_T1_Promotion.md` records
`review_lane_wiring_adr_accepted_phase_1414`,
`t0_5_to_t1_plus_admission_contract_defined_phase_1414`,
`reviewer_payment_settlement_stub_contract_defined_phase_1414`,
`review_lane_runtime_not_implemented_phase_1414`, and
`review_lane_wiring_not_complete_phase_1414`. The ADR defines the Phase 1415
admission runtime target, gate constants, external-ID-first dedup contract, and
default-off reviewer-payment settlement-stub contract. No runtime source
mutation, J-008 gate verdict change, public graph admission activation, reviewer
payment activation, ECU distribution, ledger/treasury/wallet mutation, graph
mutation, or CDL mutation occurred. Phase 1415 review lane admission runtime is
next and NON-SENSITIVE.

**Phase 1415 completion addendum:** Review lane admission runtime committed in
this phase. `ilc_core/epistemic/review_lane_admission_runtime.py` records
`review_lane_admission_runtime_committed_phase_1415`,
`review_lane_admission_runtime_phase_1415.v0.1`,
`review_lane_production_not_activated_phase_1415`, and
`review_lane_wiring_not_complete_phase_1415`. The runtime implements pure
T0.5 -> T1+ admission quote/evaluation with reviewer quorum, approval quorum,
high-value outsider approval, dedup-state checks, public-economics firewall
checks, and deterministic canonical decision JSON. No graph write, registry
write, reviewer payment, public serving, J-008 gate verdict change,
ledger/treasury/wallet mutation, graph mutation, or CDL mutation occurred.
Phase 1416 dedup enforcement and reviewer-payment settlement stub is next and
NON-SENSITIVE.

**Phase 1416 completion addendum:** Review lane dedup and payment-stub wiring
committed in this phase. `ilc_core/epistemic/review_lane_admission_runtime.py`
now records `review_lane_dedup_enforcement_stub_phase_1416`,
`review_lane_payment_settlement_stub_phase_1416`,
`review_lane_payment_not_activated_phase_1416`, and
`review_lane_wiring_not_complete_phase_1416`. Dedup resolution is
canonical-external-ID-first, content-hash fallback only, read-only, and bounded.
Payment-stub quotes call the Phase 1401 default-off reviewer payment stub only
for successful admissions and approving reviewers. No graph write, registry
write, reviewer payment execution, public serving, J-008 gate verdict change,
ledger/treasury/wallet mutation, graph mutation, or CDL mutation occurred.
Phase 1417 review lane integration tests is next and NON-SENSITIVE.

**Phase 1417 completion addendum:** Review lane integration tests committed in
this phase. `tests/test_phase_1417_review_lane_integration.py` records
`review_lane_wiring_complete_phase_1417`,
`review_lane_integration_tests_complete_phase_1417`,
`review_lane_production_not_activated_phase_1417`, and
`j008_review_lane_condition_evidence_phase_1417`. The tests cover the full
Phase 1415+1416 review-lane stack while confirming `jury_activation_gate.py`
still reports `REVIEW_LANE_WIRING_COMPLETE` as `NOT_MET`. No runtime source
mutation, J-008 gate verdict change, public serving, reviewer payment execution,
ledger/treasury/wallet mutation, graph mutation, or CDL mutation occurred.
Phase 1418 anti-capture diversity design is next and NON-SENSITIVE.

**Phase 1418 completion addendum:** Anti-capture diversity ADR committed in this
phase. `docs/adr/ADR_0044_Anti_Capture_Diversity_Verification.md` records
`anti_capture_diversity_adr_accepted_phase_1418`,
`cdl_v3_jury_assignment_wiring_defined_phase_1418`,
`vrf_outsider_selection_contract_defined_phase_1418`, and
`anti_capture_diversity_not_verified_phase_1418`. The ADR distinguishes
already-wired operator-domain independence and high-value audit VRF ordering
from the remaining CDL-V3 selected-panel cluster-diversity wiring required in
Phase 1419. No runtime source mutation, J-008 gate verdict change, production
jury activation, public graph admission activation, reviewer payment, ECU
distribution, ledger/treasury/wallet mutation, graph mutation, or CDL mutation
occurred. Phase 1419 anti-capture diversity verification is next and
NON-SENSITIVE.

**Phase 1419 completion addendum:** Anti-capture diversity verification
committed in this phase. `ilc_core/epistemic/jury_assignment_runtime.py` now
records `anti_capture_diversity_verified_phase_1419`,
`cdl_v3_cluster_diversity_wired_jury_assignment_phase_1419`,
`vrf_outsider_selection_verified_phase_1419`,
`same_operator_domain_independence_verified_phase_1419`, and
`anti_capture_production_not_activated_phase_1419`. Selected panels now expose
CDL-V3 cluster-diversity evidence and fail closed if fewer than four clusters
are selected or if one cluster exceeds the `0.40` max-share ceiling.
`PRODUCTION_ASSIGNMENT_NOT_ACTIVATED` remains `True`; `jury_activation_gate.py`
was not patched and still reports `ANTI_CAPTURE_DIVERSITY_VERIFIED` as
`NOT_MET` until Phase 1425. No production jury activation, public graph
admission activation, reviewer payment, ECU distribution,
ledger/treasury/wallet mutation, graph mutation, or CDL mutation occurred.
Phase 1420 copyright counsel disposition followed as the next SENSITIVE phase.

**Phase 1420 completion addendum:** Copyright counsel disposition committed in
this phase after explicit `GO Phase 1420`. The committed disposition artifact is
`docs/specs/ilc_copyright_counsel_disposition_1420_v0.1.md` and records
`copyright_counsel_disposition_complete_phase_1420`,
`self_counsel_verbatim_storage_boundary_phase_1420`,
`self_counsel_d2d_distribution_boundary_phase_1420`,
`copyright_counsel_not_external_legal_opinion_phase_1420`, and
`license_not_public_before_repo_authorized_public_phase_1420`. The disposition
is Genesis-authority self-counsel only, not an external legal opinion, not
attorney sign-off, and not commercial legal advice. It does not authorize
default verbatim full-text storage of third-party copyrighted artifacts,
verbatim D2D distribution of copyrighted material, public repo publication,
public package publication, or public license publication before repo-public
authorization. `COPYRIGHT_COUNSEL_DISPOSITION` evidence is recorded, but
`jury_activation_gate.py` remains unpatched and still reports the condition as
`NOT_MET` until Phase 1425. No production activation, public ingestion, public
serving, ECU distribution, ledger/treasury/wallet mutation, graph mutation,
registry mutation, CDL mutation, or J-008 gate flip occurred. Phase 1421 window
coherence and capsule update is next and NON-SENSITIVE.

**Phase 1421 completion addendum:** Window coherence and capsule update
committed in this phase. `docs/specs/ilc_window_1399_1428_coherence_report_phase_1421_v0.1.md`
records `window_1399_1428_coherence_report_phase_1421`, and
`docs/specs/ilc_antigravity_context_capsule_v5.59.md` records
`context_capsule_updated_phase_1421` and supersedes v5.58. The coherence report
confirms CDL-091, CDL-092, CDL-053, and CDL-093 ratifications; delivered
default-off and audit-only runtime surfaces; accepted ADR-0042, ADR-0043, and
ADR-0044; and J-008 evidence recorded for Phase 1425 static source
verification/patch. The report explicitly does not claim the static
`jury_activation_gate.py` source reports those evidence-backed conditions as
`MET`; the source remains unpatched until Phase 1425. No runtime source
mutation, J-008 gate flip, public activation, graph/registry/ledger/treasury/
wallet mutation, or CDL mutation occurred. Phase 1422 launch readiness manifest
schema is next and NON-SENSITIVE.

**Phase 1422 completion addendum:** Launch readiness manifest schema committed
in this phase. `docs/specs/ilc_launch_readiness_manifest_schema_1422_v0.1.md`
records `launch_readiness_manifest_schema_defined_phase_1422`,
`public_rc_launch_readiness_manifest_v1`,
`launch_readiness_manifest_not_signed_phase_1422`, and
`public_rc_not_activated_phase_1422`. The schema defines the future
Genesis-signable aggregate manifest, including Phase 1387, Phase 1389, Phase
1427, and Phase 1426 verdict fields; Genesis signing authority reference;
epoch 0->1 authorization; protocol activation epoch; canonical content hash;
and signature envelope. The unsigned template keeps
`epoch_0_to_1_transition_authorized=false`, `manifest_content_hash=null`, and
`manifest_signature=null`. No manifest signing, public RC activation, epoch
transition authorization, runtime source mutation, J-008 gate flip,
graph/registry/ledger/treasury/wallet mutation, or CDL mutation occurred. Phase
1423 private soft-RC rehearsal entry criteria is next and NON-SENSITIVE.

**Phase 1423 completion addendum:** Private soft-RC rehearsal entry criteria
committed in this phase. `docs/specs/ilc_private_soft_rc_rehearsal_criteria_1423_v0.1.md`
records `private_soft_rc_rehearsal_entry_criteria_defined_phase_1423`,
`three_machine_seven_agent_topology_spec_defined_phase_1423`,
`rehearsal_not_activated_phase_1423`, and
`no_live_llm_calls_in_rehearsal_spec_phase_1423`. The spec defines entry
criteria, M1/M2/M3 topology with seven scripted agents, ADR-0038/ADR-0041
identity init, synthetic and Lean Mathlib dataset constraints, wipe/reset
rights, and deterministic scripted-agent behavior. No rehearsal activation, VPS
provisioning, live LLM calls, public serving, production graph writes, ECU
distribution, wallet/ledger/treasury/registry mutation, CDL mutation, or J-008
gate flip occurred. Phase 1424 public RC activation certificate design is next
and NON-SENSITIVE, but execution is paused for human feedback per user
instruction.

**Phase 1425 completion addendum:** Pre-gate verification committed in this
phase. `ilc_core/epistemic/jury_activation_gate.py` patched: all 7 J-008
blocking conditions changed from `NOT_MET` to `MET` with updated
`evidence_ref` and `routing="ALREADY MET -- evidence: <token>"`. Historical
NOT_MET tokens (`vrf_verifier_required_not_implemented_phase_j008`,
`capproof_cdl_not_opened_phase_j008`,
`maintenance_lottery_cdl_not_opened_phase_j008`,
`jury_incentive_cdl_not_ratified_phase_j008`, `j008_gate_verdict_incomplete`)
are retained in `phase_tokens` as archived evidence.
`PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED` remains `True`.
`evaluate_jury_activation_gate()` now returns `verdict="PASS"` and
`blocking_not_met=[]` dynamically. Token
`j008_gate_verdict_still_incomplete_pending_production_go_phase_1425` is
recorded: the dynamic PASS reflects all-conditions-MET pre-gate state, not
a production authorization. 64 new tests (Phase 1425) + 61 updated tests
(Phase 1398) = 125 combined PASS. No production activation, CDL mutation,
graph/ledger/treasury/wallet mutation occurred. Phase 1426 soft-RC gate
re-run is next and SENSITIVE.

**Phase 1426 completion addendum:** Soft RC gate re-run committed in this
phase. `docs/specs/ilc_soft_rc_gate_rerun_1426_v0.1.md` records
`soft_rc_gate_rerun_phase_1426`, `soft_rc_eligible=true_phase_1426`,
`phase_1366_soft_rc_deferred_gate_now_closed_phase_1426`, and
`soft_rc_eligible_true_not_public_rc_activated_phase_1426`. The current
soft-RC routing verdict is now `soft_rc_eligible=true`. The Phase 1366
historical false-with-one-blocker report remains unchanged; Phase 1426 confirms
the blocker closed through Phase 1367 evidence
`phase_1366_treasury_epoch_budget_binding_verified`. No public RC publication,
release signing, activation-certificate signing, epoch 0-to-1 transition,
production jury activation, graph/ledger/treasury/wallet/registry mutation,
CDL mutation, Genesis signing, production minting, production mining, or
production validator deployment occurred. Phase 1427 J-008 gate re-run is next
and SENSITIVE.

**Phase 1427 completion addendum:** J-008 gate re-run committed in this phase.
`docs/specs/ilc_production_jury_activation_gate_pass_1427_v0.1.md` records
`production_jury_activation_gate_pass_phase_1427`, `j008_gate_rerun_phase_1427`,
`production_jury_activation_authorized_phase_1427`, and
`all_10_conditions_met_phase_1427`. `ilc_core/epistemic/jury_activation_gate.py`
now has `PRODUCTION_JURY_ACTIVATION_NOT_AUTHORIZED=False`. The gate report
returns `verdict="PASS"`, `blocking_not_met=[]`, and `production_activated=True`.
Phase 1427 authorizes production jury activation machinery only; it does not
execute assignment, reviewer payment, ingestion, ECU distribution, settlement,
graph/ledger/treasury/wallet/registry writes, public RC publication, signing,
epoch 0-to-1 transition, CDL mutation, Genesis signing, production minting,
production mining, or production validator deployment. Phase 1428 window
closure gate is next and SENSITIVE.

**Phase 1424 completion addendum:** Public RC activation certificate design
committed in this phase. `docs/specs/ilc_activation_certificate_v1_design_1424_v0.1.md`
records `activation_certificate_v1_schema_defined_phase_1424`,
`genesis_signing_ceremony_procedure_defined_phase_1424`,
`epoch_0_to_1_transition_trigger_defined_phase_1424`,
`artifact_hello_world_design_defined_phase_1424`, and
`public_rc_not_activated_phase_1424`. The design defines the 8-field
`activation_certificate_v1` schema, signing ceremony procedure (prerequisite
checklist, ADR-0036 key custody, two-person rule, ceremony transcript format,
environment controls), epoch 0->1 trigger statement (certificate signature is
the sole authorized trigger), and `artifact:hello_world` design
(T1_PUBLIC_NON_REWARD_METADATA, Genesis Agent 01 author, verbatim content fixed
by human decision, does NOT trigger epoch start). 60 tests pass. No signing
ceremony execution, no public RC activation, no `ilc_core/` mutation, no CDL
mutation, no graph/ledger/treasury/wallet/registry mutation, and no J-008 gate
flip occurred. Phase 1425 pre-gate re-run verification is next and NON-SENSITIVE.

---

## 1. Window Identity and Scope

Window 1399-1428 closes all 7 blocking conditions from the J-008 production jury
activation gate (Phase 1398 verdict INCOMPLETE) and produces the architectural
specifications required for the private soft-RC rehearsal and public RC activation.

**Baseline at lock time:**
- Window 1391-1398 (J-series) COMPLETE; 163 tests passing
- J-008 gate verdict: INCOMPLETE — 7 of 10 blocking conditions NOT_MET
- Last ratified CDL: CDL-090 (Phase 1373)
- Active capsule: v5.58
- Current commit: `ec475d48`

**Three tracks:**
1. **Jury Economy CDL track (Phases 1399-1420):** CDL-091/092/093 opening and ratification,
   VRF verifier, review lane wiring, anti-capture verification, copyright counsel disposition.
2. **Launch Readiness Design track (Phases 1422-1424):** Launch Readiness Manifest schema,
   private soft-RC rehearsal entry criteria, public RC activation certificate design.
3. **Gate closure tail (Phases 1425-1428):** Pre-gate verification, soft RC re-run, J-008
   gate re-run expecting `verdict="PASS"`, window closure.

---

## 2. Inputs and Closure Inheritance

Inherited from Window 1391-1398 (J-series):

| Item | State |
|------|-------|
| `jury_activation_gate_phase_j008.v0.1` | Active gate module; 7 blocking conditions NOT_MET |
| `ingestion_shadow_harness_phase_j007.v0.1` | MET (J007_HARNESS_PASS) |
| `public_economics_firewall_condition_met_phase_j008` | MET (PUBLIC_ECONOMICS_FIREWALL) |
| `epoch_hash_shadow_assignment_only_phase_j006` | MET (NO_EPOCH_HASH_PRODUCTION_PRIVACY_CLAIM) |
| CDL-090 | Ratified Phase 1373 (last ratified CDL) |
| CDL-091 | Lane opened Phase 1394 (J-004 spec); NOT yet registered in CDL log |
| CDL-092, CDL-093 | Not yet opened |
| Window 1369-1390 closure | `43401835` |

---

## 3. Locked Phase Table (1399-1428)

| Order | Phase | Scope | Character | Sensitivity |
|-------|-------|-------|-----------|-------------|
| 1 | 1399 | CDL-091 jury incentive economics — register opening + prelock | Constitutional | **SENSITIVE** |
| 2 | 1400 | CDL-091 ratification | Constitutional | **SENSITIVE** |
| 3 | 1401 | CDL-091 jury incentive runtime stub | Runtime | NON-SENSITIVE |
| 4 | 1402 | CDL-092 CapProof — opening | Constitutional | **SENSITIVE** |
| 5 | 1403 | CDL-092 CapProof — deliberation | Spec | NON-SENSITIVE |
| 6 | 1404 | CDL-092 CapProof — prelock | Constitutional | NON-SENSITIVE |
| 7 | 1405 | CDL-092 CapProof — ratification | Constitutional | **SENSITIVE** |
| 8 | 1406 | CDL-093 maintenance lottery pool — opening | Constitutional | **SENSITIVE** |
| 9 | 1407 | CDL-093 maintenance lottery pool — deliberation/prelock | Constitutional | NON-SENSITIVE |
| 10 | 1408 | CDL-093 maintenance lottery pool — ratification | Constitutional | **SENSITIVE** |
| 11 | 1409 | CDL-093 maintenance lottery pool runtime stub | Runtime | NON-SENSITIVE |
| 12 | 1410 | VRF proof verifier ADR | Spec/ADR | NON-SENSITIVE |
| 13 | 1411 | VRF proof verifier implementation | Runtime | NON-SENSITIVE |
| 14 | 1412 | VRF integration with jury_assignment_runtime.py | Runtime | NON-SENSITIVE |
| 15 | 1413 | VRF integration tests and security review | Testing | NON-SENSITIVE |
| 16 | 1414 | Review lane wiring — T0.5→T1+ ADR | Spec/ADR | NON-SENSITIVE |
| 17 | 1415 | Review lane wiring — admission runtime | Runtime | NON-SENSITIVE |
| 18 | 1416 | Review lane wiring — dedup + payment settlement stub | Runtime | NON-SENSITIVE |
| 19 | 1417 | Review lane wiring — integration tests; `REVIEW_LANE_WIRING_COMPLETE` token | Testing | NON-SENSITIVE |
| 20 | 1418 | Anti-capture diversity — CDL-V3 + VRF wiring design | Spec | NON-SENSITIVE |
| 21 | 1419 | Anti-capture diversity — production verification | Audit | NON-SENSITIVE |
| 22 | 1420 | Copyright counsel disposition — ADR-0041 §5 | Governance | **SENSITIVE** |
| 23 | 1421 | Window coherence and capsule update | Synthesis | NON-SENSITIVE |
| 24 | 1422 | Launch Readiness Manifest schema | Spec | NON-SENSITIVE |
| 25 | 1423 | Private soft-RC rehearsal entry criteria | Spec | NON-SENSITIVE |
| 26 | 1424 | Public RC activation certificate design | Spec | NON-SENSITIVE |
| 27 | 1425 | Pre-gate re-run verification | Gate prep | NON-SENSITIVE |
| 28 | 1426 | Soft RC gate re-run — `soft_rc_eligible=true` | Gate | **SENSITIVE** |
| 29 | 1427 | J-008 gate re-run — `verdict="PASS"` | Gate | **SENSITIVE** |
| 30 | 1428 | Window 1399-1428 closure gate | Gate | **SENSITIVE** |

---

## 4. Sequencing Constraints

| Constraint | Rule |
|-----------|------|
| 1400 requires 1399 C1 complete | Historical hardening references Phase 1399 register-opening commit |
| 1405 requires 1402-1404 complete | CDL-092 must be prelocked before ratification |
| 1408 requires 1406-1407 complete | CDL-093 must be prelocked before ratification |
| 1412 requires 1411 complete | VRF integration requires verifier implementation |
| 1415-1416 require 1414 ADR accepted | Admission runtime builds on ADR-defined contract |
| 1419 requires 1412 AND 1417 complete | Anti-capture needs both VRF and review lane |
| 1425 must clear all 7 blocking conditions before 1427 | Gate re-run cannot proceed with known NOT_MET |
| 1426 must precede 1427 | `soft_rc_eligible=true` is an input to the Phase 1427 gate aggregate |
| 1427 must precede 1428 | Closure gate requires gate PASS recorded |

CDL-091/092/093 tracks are largely independent and may be interleaved at Codex's
discretion within their intra-track ordering constraints.

---

## 5. CDL Register Gap — Phase 1399

Phase 1394 (J-004) produced `docs/specs/ilc_cdl_jury_incentive_economics_opening_v0.1.md`
but did NOT add a CDL-091 row to `docs/specs/ilc_constitutional_decision_log_v0.1.md`.
CDL-090 is the last registered CDL at this sequence lock.

Phase 1399 therefore has two commits:
- **C1 (CDL mutation):** Adds CDL-091 row with `status: open`, `opened_phase: 1399`,
  `opening_token: cdl_091_jury_incentive_economics_opened_phase_1399`.
  Requires `ILC_CDL_MUTATION_AUTHORIZED=1 ILC_CDL_MUTATION_PHASE=1399`.
  Completed in commit `06993864`.
- **C2 (prelock):** Adds `docs/specs/ilc_cdl_091_jury_incentive_economics_prelock_1399_v0.1.md`
  and tests. No CDL mutation env required. Completed in commit `d2b4181d`.

Phase 1400 historical hardening must reference the Phase 1399 C1 commit hash, not Phase 1394.

---

## 6. Gate Module Static-Status Note

`ilc_core/epistemic/jury_activation_gate.py` encodes Phase 1398 NOT_MET conditions as
hardcoded literals. The gate does not dynamically detect new completion evidence.

Phase 1425 must verify whether the gate module needs source changes before Phase 1427 can
produce `verdict="PASS"`. If updates are required, Phase 1425a gates the Phase 1427 re-run.

---

## 7. CDL Number Assignments

| CDL | Scope | Register opening | Ratification |
|-----|-------|-----------------|--------------|
| CDL-091 | Jury incentive economics | Phase 1399 C1 | Phase 1400 |
| CDL-092 | CapProof content-addressing, CV signing, ±15% band | Phase 1402 | Phase 1405 |
| CDL-093 | Maintenance lottery pool distribution | Phase 1406 | Phase 1408 |

Next fresh CDL number after this window: **CDL-094**

---

## 8. Non-Authorizations

This sequence lock does not authorize:

- Reviewer payment activation or live ECU distribution via jury/maintenance lane
- Production jury assignment activation
- VRF production deployment
- Review lane production serving
- Maintenance lottery live distribution
- Public RC publication or release signing
- Any CDL mutation beyond those enumerated in §7
- Production minting, ILC settlement, public claimability activation
- Soft-RC rehearsal start (requires separate operational GO)

---

## 9. Canonical Anchors

- `docs/specs/ilc_window_1399_1428_candidate_phase_grouping_v0.1.md` — guidance doc (`ec475d48`)
- `docs/specs/ilc_production_jury_activation_gate_j008_v0.1.md` — J-008 gate spec
- `ilc_core/epistemic/jury_activation_gate.py` — gate source (7 hardcoded NOT_MET conditions)
- `docs/specs/ilc_cdl_jury_incentive_economics_opening_v0.1.md` — CDL-091 lane opening (Phase 1394)
- `docs/specs/ilc_epoch_start_capability_maintenance_contract_v0.1.md` — CDL-092/093 design basis
- `docs/adr/ADR_0040_Jury_Eligibility_Assignment.md` — VRF production boundary
- `docs/adr/ADR_0041_Agent_INIT_and_Ingestion_Protocol.md` — copyright boundary (§5), T0.5 review lane
- `docs/specs/ilc_antigravity_context_capsule_v5.58.md` — active capsule

---

## 10. Prompt Files Available

| Phase | Prompt file | Status |
|-------|-------------|--------|
| 1399 | `docs/antigravity_tasks/antigravity_prompt__phase_1399_g8_cdl_091_jury_incentive_economics_prelock.md` | Committed `5e5043ea` |
| 1400 | `docs/antigravity_tasks/antigravity_prompt__phase_1400_g8_cdl_091_jury_incentive_economics_ratification.md` | Committed `5e5043ea` |
| 1401 | `docs/antigravity_tasks/antigravity_prompt__phase_1401_g8_cdl_091_jury_incentive_runtime_stub.md` | Committed `5e5043ea` |
| 1402 | `docs/antigravity_tasks/antigravity_prompt__phase_1402_g8_cdl_092_capproof_opening.md` | Committed `5e5043ea` |
| 1403 | `docs/antigravity_tasks/antigravity_prompt__phase_1403_g8_cdl_092_capproof_deliberation.md` | Committed `5e5043ea` |
| 1404-1428 | Pending — to be drafted per window progress | Not yet committed |
