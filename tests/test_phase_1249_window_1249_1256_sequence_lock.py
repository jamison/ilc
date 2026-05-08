from pathlib import Path


SEQUENCE_LOCK = Path("docs/specs/ilc_phase_1249_1256_sequence_lock_v0.1.md")


def _lock_text() -> str:
    return SEQUENCE_LOCK.read_text(encoding="utf-8")


def test_phase_1249_sequence_lock_file_exists() -> None:
    assert SEQUENCE_LOCK.exists()
    assert SEQUENCE_LOCK.read_text(encoding="utf-8").strip()


def test_phase_1248_closure_baseline_recorded() -> None:
    text = _lock_text()
    assert "window_1241_1248_closed_phase_1248" in text
    assert "window_1241_1248_closure_gate_verdict=pass" in text
    assert "docs/specs/ilc_window_1241_1248_handoff_1248_v0.1.md" in text


def test_phase_1249_sequence_lock_tokens_present() -> None:
    text = _lock_text()
    assert "GO Phase 1249" in text
    assert "window_1249_1256_sequence_lock_verdict=pass" in text
    assert "window_1249_1256_sequence_lock_committed" in text


def test_current_capsule_roadmap_and_guidance_recorded() -> None:
    text = _lock_text()
    assert "docs/specs/ilc_antigravity_context_capsule_v5.50.md" in text
    assert "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md" in text
    assert "docs/specs/ilc_window_1249_1256_candidate_phase_grouping_v0.1.md" in text
    assert "roadmap_v1_1_controlling_public_rc_roadmap_phase_1242" in text


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
    assert "41-node / 73-edge candidate; unsigned; signing deferred" in text


def test_discovery_audit_and_unknown_unknown_discipline_recorded() -> None:
    text = _lock_text()
    assert "Required-token audit" in text
    assert "Concept-discovery search" in text
    assert "Contradiction and non-claim search" in text
    assert "Source expansion" in text
    assert "unknown_unknown_discovery_required_before_phase_execution" in text
    assert "historical_retrieval_is_context_not_authority_current_canon_controls" in text
    assert "MemPalace may be used only as advisory retrieval support" in text


def test_cdl_087_and_v0_2_state_recorded_as_blocked() -> None:
    text = _lock_text()
    assert "OPEN / PRELOCKED / NOT RATIFIED" in text
    assert "cdl_087_governance_review_complete_phase_1246" in text
    assert "cdl_087_ratification_deferred_pending_production_candidate_fetch_evidence" in text
    assert "cdl_087_sensitive_ratification_phase_required_if_later_authorized" in text
    assert "CDL-088 must not be opened without explicit future authorization" in text
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text


def test_public_rc_branch_posture_locked() -> None:
    text = _lock_text()
    assert "public_rc_default_path=openclaw_skill_first_public_claimability_no_public_p2p_claim" in text
    assert "openclaw_nemoclaw_skill_first_public_rc_path_no_public_ilc_p2p_claim" in text
    assert "public_claimability_required_for_final_public_rc_profile" in text
    assert "gap_14_package_modularity_executes_before_gap_10_public_p2p" in text
    assert "gap_14_adapter_extraction_runs_before_public_rc_claim_phase_1249" in text


def test_locked_phase_order_and_sensitive_gates_recorded() -> None:
    text = _lock_text()
    assert "| 1 | 1249 | Window 1249-1256 sequence lock | **SENSITIVE** |" in text
    assert "| 2 | 1250 | Gap 14 adapter extraction for `ilc_logic` migration debt | NON-SENSITIVE |" in text
    assert "| 3 | 1251 | Gap 14 package CI gate, profile export audit, package-size measurement | NON-SENSITIVE |" in text
    assert "| 4 | 1252 | Gap 13 claimability resolution boundary and chain/crypto dependency inventory | **SENSITIVE** |" in text
    assert "| 8 | 1256 | Window coherence, blocker classification, and closure gate | **SENSITIVE** |" in text
    assert "GO Phase 1252" in text
    assert "GO Phase 1256" in text
    assert "phase_1252_gap13_claimability_boundary_requires_explicit_go" in text


def test_carry_forward_tokens_recorded() -> None:
    text = _lock_text()
    for token in (
        "gap_14_adapter_extraction_and_package_ci_gate_should_continue_before_public_rc_claim",
        "gap_13_public_claimability_runtime_should_start_before_final_public_rc_claim",
        "transport_principal_identity_required_before_public_p2p",
        "atlas_g_004_high_authority_gap_closure_required",
        "atlas_g_005_import_dependency_graph_bridge_required",
        "tla_refinement_notes_pre_rc_window_1241_plus_candidate",
        "allowlist_export_procedure_window_1241_plus_candidate",
    ):
        assert token in text


def test_non_authorization_boundary_recorded() -> None:
    text = _lock_text()
    for phrase in (
        "CDL-087 ratification",
        "CDL-088 opening",
        "CDL mutation",
        "public RC claim",
        "public repository publication",
        "public P2P exposure",
        "public sidecar/projection serving",
        "public claimability activation",
        "ECU minting authorization",
        "ILC settlement or withdrawal runtime",
        "release-key generation",
        "v0.2 signing",
    ):
        assert phrase in text


def test_graph_delta_and_next_phase_recorded() -> None:
    text = _lock_text()
    assert (
        "graph_delta=support_only:docs/specs/ilc_phase_1249_1256_sequence_lock_v0.1.md -> planning/frontier"
        in text
    )
    assert "Phase 1250 - Gap 14 adapter extraction for ilc_logic migration debt" in text
