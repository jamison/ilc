from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CIRCUIT_SCHEMA = REPO / "docs/specs/ilc_circuit_definition_node_schema_v0.1.md"
PROOF_SCHEMA = REPO / "docs/specs/ilc_proof_receipt_node_schema_v0.1.md"
OBLIGATION_REGISTER = REPO / "docs/specs/ilc_open_obligation_register_v0.1.md"
STATUS = REPO / "docs/phases/STATUS.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_circuit_schema_declares_required_node_and_edge_types() -> None:
    text = _text(CIRCUIT_SCHEMA)
    for token in (
        "CircuitDefinitionNode",
        "CircuitParamsNode",
        "CircuitExecutionReceipt",
        "CircuitSupersedesEdge",
        "CircuitAuthorityEdge",
    ):
        assert token in text


def test_circuit_schema_declares_required_fields() -> None:
    text = _text(CIRCUIT_SCHEMA)
    for token in (
        "circuit_id",
        "circuit_version",
        "description",
        "input_schema_ref",
        "output_schema_ref",
        "cdl_authority",
        "annotation_method",
        "annotation_phase",
        "params_id",
        "params_version",
        "parameters",
        "effective_epoch",
        "receipt_id",
        "params_root",
        "input_commitment",
        "output_commitment",
        "epoch",
        "superseded_circuit_id",
        "superseding_circuit_id",
        "authority_cdl",
        "cdl_or_adr_ref",
        "ratification_epoch",
    ):
        assert f"`{token}`" in text


def test_proof_schema_declares_required_fields_and_proof_systems() -> None:
    text = _text(PROOF_SCHEMA)
    for token in (
        "ProofReceiptNode",
        "receipt_id",
        "circuit_id",
        "params_root",
        "input_commitment",
        "output_commitment",
        "cdl_authority",
        "proof_system",
        "stark",
        "supernova",
        "hypernova",
        "groth16_deferred",
    ):
        assert token in text


def test_schema_docs_require_canonical_serialization_and_float_ban() -> None:
    combined = _text(CIRCUIT_SCHEMA) + "\n" + _text(PROOF_SCHEMA)
    for token in (
        "sort_keys=True",
        'separators=(\",\", \":\")',
        "allow_nan=False",
        "Python `float`",
        "NaN",
        "Infinity",
        "Decimal values serialized as strings",
    ):
        assert token in combined


def test_schema_docs_state_cdl044_retention_exemption() -> None:
    combined = _text(CIRCUIT_SCHEMA) + "\n" + _text(PROOF_SCHEMA)
    assert "CDL-044" in combined
    assert "exempt from CDL-044 pruning" in combined
    assert "Historical proof receipts" in combined


def test_schema_docs_state_authority_and_default_off_boundary() -> None:
    combined = _text(CIRCUIT_SCHEMA) + "\n" + _text(PROOF_SCHEMA)
    for token in (
        "ADR-0035",
        "CDL-097",
        "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True",
        "schema document only",
        "does not activate the ADR-0035 type registry",
    ):
        assert token in combined


def test_schema_docs_state_non_execution_boundary() -> None:
    combined = _text(CIRCUIT_SCHEMA) + "\n" + _text(PROOF_SCHEMA)
    for token in (
        "does not execute a circuit",
        "generate a proof",
        "verify a proof",
        "write wallets",
        "write treasury state",
        "mint",
        "settle",
        "activate public RC",
    ):
        assert token in combined


def test_obl048_closed_and_status_tokens_present() -> None:
    register = _text(OBLIGATION_REGISTER)
    status = _text(STATUS)
    assert "| OBL-048 |" in register
    assert "closed - schema seams complete" in register
    for token in (
        "phase_1568_fix2x_circuit_definition_schema_seams_committed",
        "phase_1568_fix2x_proof_receipt_schema_seams_committed",
        "phase_1568_fix2x_obl_048_closed",
        "phase_1568_fix2x_no_runtime_activation",
        "public_path_remains_blocked_phase_1568_fix2x",
    ):
        assert token in status
