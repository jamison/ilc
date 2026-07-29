from pathlib import Path


SPEC = Path(
    "docs/specs/ilc_cdl_106_agent_reputation_record_opening_GAP_REPUTATION_01_v0.1.md"
)
REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
STATUS = Path("docs/phases/STATUS.md")


def test_cdl_106_opening_doc_declares_exact_agent_reputation_fields() -> None:
    text = SPEC.read_text()

    required_fields = (
        "agent_id",
        "epoch",
        "graph_snapshot_root",
        "lifecycle_event_root",
        "attribution_root",
        "liveness_root",
        "equivocation_root",
        "sybil_risk_root",
        "reputation_score",
        "eligibility_flags",
        "previous_reputation_record_root",
    )
    for field in required_fields:
        assert f"`{field}`" in text


def test_cdl_106_opening_preserves_non_activation_boundaries() -> None:
    text = SPEC.read_text()

    assert "The scoring formula is not locked" in text
    assert "Production reputation scoring is not activated" in text
    assert "Validator admission is not activated" in text
    assert "No runtime code is created or changed" in text
    assert "not ECU and not ILC" in text


def test_agent_reputation_root_uses_canonical_json_and_decimal_strings() -> None:
    text = SPEC.read_text()

    assert "sort_keys=True" in text
    assert "separators=(\",\", \":\")" in text
    assert "allow_nan=False" in text
    assert "Decimal fields must be serialized as strings" in text


def test_cdl_106_register_row_is_opened_not_ratified() -> None:
    row = next(
        line
        for line in REGISTER.read_text().splitlines()
        if line.startswith("| CDL-106 |")
    )

    assert "| opened |" in row
    assert "opened_phase: GAP-REPUTATION-01 / 1589b" in row
    assert "opening_token: reputation_record_cdl_106_opened_GAP_REPUTATION_01" in row
    assert "runtime_activation_status: not_authorized" in row
    assert "validator_admission_binding_status: deferred_to_CDL-107" in row


def test_status_records_cdl_106_opening_token() -> None:
    text = STATUS.read_text()

    assert "reputation_record_cdl_106_opened_GAP_REPUTATION_01" in text
