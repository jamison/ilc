# Fix63b Direct Source Invariant Audit Batch 034

- Phase: `1545p-Fix63b-batches029-034`
- Source map: `docs/specs/ilc_fix63a_invariant_source_file_map_v0.1.json`
- Row range: `331-336`
- Direct read status: `complete`
- Recommended edges: `27`
- Accepted semantic edges written: `27`
- Duplicate semantic edges skipped: `3`
- Non-claim: no public RC, publication, runtime activation, ECU minting, ILC settlement, CDL mutation, or Genesis signing authorized.

## Entries

- `331` `invariant:window1369_sequence_lock_hardening_routes_public_economics_firewall_and_sensitive_go_requirements`
  - Source: `tests/test_phase_1369_sequence_lock.py`
  - Evidence: `['1-79']`
  - Summary: Phase 1369 sequence-lock tests route numeric hardening and the public-economics firewall while requiring future CDL-088 and public-claimability GO gates.
  - Edges: `5` recommended, `5` written, `0` duplicate skipped
- `332` `invariant:window775_782_row5_privacy_nonclosure_layer1_layer2_sim_artifacts_zk_note_and_no_cdl_mutation`
  - Source: `tests/test_window_775_782_closure_gate.py`
  - Evidence: `['1-99']`
  - Summary: Window 775-782 closure-gate tests record row-5 privacy/nonclosure, layer1/layer2 sim artifacts, ZK-nullifier path, observability floor, and no-CDL-mutation boundary.
  - Edges: `5` recommended, `5` written, `0` duplicate skipped
- `333` `invariant:window823_829_mysticeti_activation_sequence_lock_high002_rotation_first_validator_gate_and_no_cdl_mutation`
  - Source: `tests/test_window_823_829_sequence_lock.py`
  - Evidence: `['1-85']`
  - Summary: Window 823-829 sequence-lock tests preserve Mysticeti activation ordering, ADR-0028 option-B posture, CDL-017 boundary, first-validator gate, and no CDL-062 opening.
  - Edges: `4` recommended, `4` written, `1` duplicate skipped
- `334` `invariant:window_1118_1123_sequence_lock_provenance_sim_coherence_and_q2_q8_boundary`
  - Source: `tests/test_phase_1123_window_1118_1123_closure_gate.py`
  - Evidence: `['1-193']`
  - Summary: Window 1118-1123 closure-gate tests prove provenance sim coherence, q2/q8 alpha boundaries, no forbidden runtime random imports, and Decimal provenance alpha.
  - Edges: `4` recommended, `4` written, `1` duplicate skipped
- `335` `invariant:window_1139_1147_closure_signed_genesis_sim_spectral03_obligations_and_no_scope_creep`
  - Source: `tests/test_phase_1147_window_1139_1147_closure_gate.py`
  - Evidence: `['1-185']`
  - Summary: Window 1139-1147 closure-gate tests preserve signed Genesis v0.1 star-map artifacts, SIM-SPECTRAL-03 obligations, CDL-084 constants, CDL-085 defer status, and lineage-contract obligations.
  - Edges: `5` recommended, `5` written, `1` duplicate skipped
- `336` `invariant:window_1139_1147_three_lane_complete_and_public_rc_blocked`
  - Source: `docs/phases/phase_1545p_fix57_public_eligible_fiedler_minority_manual_pass_walkthrough.md`
  - Evidence: `['1-260']`
  - Summary: Fix57 walkthrough evidence records Window 1139-1147 three-lane completion and public-RC blocked posture as support evidence, not public activation.
  - Edges: `4` recommended, `4` written, `0` duplicate skipped
