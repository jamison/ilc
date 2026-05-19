from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

REPORT = REPO / "docs/specs/ilc_public_claimability_activation_gate_report_1389_v0.1.md"
WALKTHROUGH = REPO / "docs/phases/phase_1389_public_claimability_activation_gate_walkthrough.md"
VERIFIER = REPO / "ilc_core/sidecars/claimability_receipt_verifier.py"
POLICY_1377 = REPO / "docs/specs/ilc_replay_nullifier_policy_1377_v0.1.md"
PHASE_1336 = REPO / "docs/specs/ilc_public_claimability_api_activation_or_carry_forward_gate_1336_v0.1.md"
PHASE_1389_PROMPT = (
    REPO / "docs/antigravity_tasks/antigravity_prompt__phase_1389_g8_public_claimability_activation_gate.md"
)
STATUS = REPO / "docs/phases/STATUS.md"
PLANNING_INDEX = REPO / "docs/PLANNING_INDEX.md"
SEQUENCE_LOCK = REPO / "docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md"
WINDOW_GROUPING = REPO / "docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md"

REQUIRED_TOKENS = (
    "public_claimability_gate_phase_1389_executed",
    "public_claimability_gate_failed_phase_1389",
    "gate_failed_reason=claimability_runtime_public_mode_blockers_still_active",
    "claimability_runtime_public_mode_blockers_still_active_phase_1389",
)

BLOCKER_TOKENS = (
    "cdl_088_ratified_phase_1376",
    "agent_birth_attestation_adr_0038_committed_phase_1370",
    "cdl_090_ratified_phase_1373",
    "replay_nullifier_policy_committed_phase_1377",
    "legacy_public_labeled_fastapi_routes_cleaned_phase_1378",
    "counsel_clearance_public_verifier_api_phase_1388",
    "cdl_048_activated_phase_1388",
    "pre_activation_hardening_gate_pass_phase_1387",
    "accepted_adr_cdl_runtime_coverage_matrix_phase_1387a",
    "public_economics_requires_public_node_admission_verified_phase_1387a",
    "private_visibility_excluded_from_public_economics_phase_1387a",
    "no_unrouted_accepted_cdl_adr_functionality_before_public_rc_phase_1387a",
)

PUBLIC_MODE_BLOCKERS = (
    "public_claimability_api_authority_missing_phase_1305",
    "replay_nullifier_policy_not_activated_phase_1305",
    "duplicate_claim_registry_not_activated_phase_1305",
    "public_safe_disclosure_schema_not_final_phase_1305",
    "transport_principal_public_path_not_activated_phase_1305",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1389_report_records_failed_closed_verdict() -> None:
    text = _read(REPORT)
    for token in REQUIRED_TOKENS:
        assert token in text
    assert "Status:** FAILED CLOSED" in text


def test_phase_1389_report_lists_all_prerequisite_tokens() -> None:
    text = _read(REPORT) + "\n" + _read(WALKTHROUGH)
    for token in BLOCKER_TOKENS:
        assert token in text


def test_phase_1389_report_does_not_record_activation_result_token() -> None:
    text = _read(REPORT) + "\n" + _read(WALKTHROUGH)
    activation_result_token = "result=" + "public_claimability_activated"
    assert activation_result_token not in text


def test_phase_1389_report_records_historical_public_mode_blockers() -> None:
    text = _read(REPORT)
    for token in PUBLIC_MODE_BLOCKERS:
        assert token in text


def test_claimability_verifier_public_mode_blockers_resolved_after_1389b() -> None:
    text = _read(VERIFIER)
    assert "_PUBLIC_MODE_BLOCKERS: tuple[str, ...] = ()" in text
    assert "CLAIMABILITY_VERIFIER_PUBLIC_MODE_READY_TOKEN" in text


def test_phase_1377_policy_is_policy_only_not_runtime_activation() -> None:
    text = _read(POLICY_1377)
    assert "replay_nullifier_policy_committed_phase_1377" in text
    assert "duplicate_claim_rejection_policy_defined" in text
    assert "does not implement a nullifier runtime" in text
    assert "open a public claim endpoint" in text
    assert "does not enable a public verifier API" in text


def test_phase_1336_source_blockers_include_duplicate_claim_registry() -> None:
    text = _read(PHASE_1336)
    assert "Replay/nullifier policy not activated" in text
    assert "Duplicate-claim registry not activated" in text


def test_phase_1389_prompt_remains_validated_by_schema_contract() -> None:
    text = _read(PHASE_1389_PROMPT)
    assert "public_claimability_gate_phase_1389_executed" in text
    assert "public_claimability_gate_failed_phase_1389" in text


def test_planning_surfaces_record_phase_1389_failed_closed() -> None:
    combined = "\n".join(
        _read(path)
        for path in (
            STATUS,
            PLANNING_INDEX,
            SEQUENCE_LOCK,
            WINDOW_GROUPING,
        )
    )
    for token in REQUIRED_TOKENS:
        assert token in combined
    assert "Phase 1390 window closure" in combined
