from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_ccss_contact_gate_policy_spec_1573s_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1573s_g10_ccss_contact_gate_policy_spec.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_contact_gate_policy_spec_exists() -> None:
    assert SPEC.exists()
    text = _text(SPEC)
    assert "ContactGateNode" in text
    assert "schema\": \"ilc_ccss_contact_gate_node_v1" in text


def test_all_six_admission_modes_are_defined() -> None:
    text = _text(SPEC)
    for mode in (
        "public_open",
        "contacts_only",
        "capability_required",
        "stake_or_rate_limited_open",
        "private_invite_only",
        "closed",
    ):
        assert f"`{mode}`" in text


def test_relay_visible_boundary_forbids_private_gate_material() -> None:
    text = _text(SPEC)
    assert "Relays must not see private gate rules" in text
    assert "recipient identity" in text
    assert "sender identity" in text
    assert "raw capability IDs" in text
    assert "allowlists" in text
    assert "denylists" in text
    assert "lambda_local" in text
    assert "noise_sigma" in text


def test_no_public_serving_or_economic_activation_is_recorded() -> None:
    text = _text(SPEC)
    assert "does not activate public relay serving" in text
    assert "public transport" in text
    assert "economics/stake anti-spam" in text
    assert "wallet writes" in text
    assert "settlement" in text


def test_spec_references_required_canon() -> None:
    text = _text(SPEC)
    for required in (
        "ADR_0014_Identity_Sybil_and_Admission_Control_Envelope.md",
        "ADR_0041_Agent_INIT_and_Ingestion_Protocol.md",
        "ilc_ccss_004_public_activation_boundary_spec_v0.1.md",
        "SpectralRouteToken",
        "ccss_pre_rc_cover_batch_profile_v1_candidate",
    ):
        assert required in text


def test_capability_commitment_and_nullifier_shapes_are_defined() -> None:
    text = _text(SPEC)
    assert "make_capability_context_commitment(raw_capability_id, epoch)" in text
    assert "contact_gate_nullifier" in text
    assert "ilc-contact-gate-nullifier-v1" in text
    assert "The raw capability ID is never relay-visible" in text


def test_status_tokens_present_and_prompt_paths_are_current() -> None:
    status = _text(STATUS)
    for token in (
        "ccss_contact_gate_policy_spec_committed_phase_1573s",
        "contact_gate_node_schema_defined_phase_1573s",
        "contact_gate_private_capability_boundary_recorded_phase_1573s",
        "ccss_contact_gate_no_public_serving_phase_1573s",
        "public_path_remains_blocked_phase_1573s",
    ):
        assert token in status

    prompt = _text(PROMPT)
    assert "ilc_ccss_public_rc_privacy_claim_boundary_1573o_v0.1.md" in prompt
    assert "ilc_core/network/d2d/spectral_route_token.py" in prompt
    assert "ccss_side_channel_sim_committed_phase_1573q" in prompt
    assert "ilc_core/ccss/spectral_route_token.py" not in prompt
    assert "ccss_side_channel_sim_complete_phase_1573q" not in prompt
