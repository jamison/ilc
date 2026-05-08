from pathlib import Path


SEQUENCE_LOCK = Path("docs/specs/ilc_phase_1241_1248_sequence_lock_v0.1.md")


def _lock_text() -> str:
    return SEQUENCE_LOCK.read_text(encoding="utf-8")


def test_phase_1241_sequence_lock_file_exists() -> None:
    assert SEQUENCE_LOCK.exists()
    assert SEQUENCE_LOCK.read_text(encoding="utf-8").strip()


def test_phase_1240_closure_verdict_recorded() -> None:
    text = _lock_text()
    assert "window_1233_1240_closed_phase_1240" in text
    assert "window_1233_1240_closure_gate_verdict=pass" in text


def test_phase_1241_sequence_lock_token_present() -> None:
    text = _lock_text()
    assert "window_1241_1248_sequence_lock_verdict=pass" in text
    assert "window_1241_1248_sequence_lock_committed" in text
    assert "GO Phase 1241" in text


def test_current_capsule_and_handoff_recorded() -> None:
    text = _lock_text()
    assert "docs/specs/ilc_antigravity_context_capsule_v5.50.md" in text
    assert "docs/specs/ilc_window_1233_1240_handoff_1240_v0.1.md" in text


def test_immutable_anchors_recorded() -> None:
    text = _lock_text()
    assert (
        "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
        in text
    )
    assert (
        "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56"
        in text
    )


def test_cdl_087_unratified_state_recorded() -> None:
    text = _lock_text()
    assert "OPEN / PRELOCKED / NOT RATIFIED" in text
    assert "cdl_087_prelock_committed_phase_1228" in text
    assert "cdl_087_candidate_envelope_identified_not_ratified_phase_1238j" in text
    assert "Phase 1238j produced SIM-FETCH-01 robustness evidence" in text


def test_public_rc_branch_posture_locked() -> None:
    text = _lock_text()
    assert "openclaw_nemoclaw_skill_first_public_rc_path_no_public_ilc_p2p_claim" in text
    assert "public_claimability_required_for_final_public_rc_profile" in text
    assert "gap_14_package_modularity_executes_before_gap_10_public_p2p" in text


def test_locked_phase_order_and_sensitive_gates_recorded() -> None:
    text = _lock_text()
    assert "| 1 | 1241 | Window sequence lock | **SENSITIVE** |" in text
    assert "| 8 | 1248 | Coherence, blocker classification, handoff, closure | **SENSITIVE** |" in text
    assert "GO Phase 1248" in text
    assert "Phase 1246 is review-only" in text


def test_gap14_before_gap10_tokens_recorded() -> None:
    text = _lock_text()
    assert "gap_14_package_modularity_first_slice_before_gap_10_transport_principal" in text
    assert "ilc_logic_pure_protocol_interfaces_required" in text
    assert "harness_adapter_transport_storage_protocols_required" in text


def test_atlas_g_first_slice_tokens_recorded() -> None:
    text = _lock_text()
    assert "atlas_g_001_graph_delta_schema_required" in text
    assert "atlas_g_002_repo_hypergraph_compiler_hardening_required" in text
    assert "atlas_g_003_package_profile_reachability_manifest_required" in text


def test_v0_2_signing_deferral_and_non_claims_recorded() -> None:
    text = _lock_text()
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text
    for phrase in (
        "CDL-087 ratification",
        "public RC claim",
        "public repository publication",
        "public P2P exposure",
        "release-key generation",
        "v0.2 signing",
    ):
        assert phrase in text


def test_next_phase_is_1242() -> None:
    assert "Phase 1242 — Roadmap v1.1 controlling public-RC reconciliation" in _lock_text()
