from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ilc_core.identity.agent_id_runtime import derive_agent_id
from ilc_core.protocol.public_init_admission_runtime import issue_public_init_admission_receipt
from ilc_core.protocol.public_receipt_runtime import (
    RECEIPT_CLASS_FIELDS,
    PublicReceiptRuntimeError,
    issue_public_receipt,
    query_public_receipts,
)
from ilc_core.server import create_app

DOC_PATH = Path("docs/specs/ilc_public_receipt_runtime_651_v0.1.md")
TEST_PATH = Path("tests/test_phase_651_public_receipt_runtime.py")
WALKTHROUGH_PATH = Path("docs/phases/phase_651_g8_public_receipt_runtime_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_651_SUBJECT_TOKEN = "phase 651 public receipt runtime"
PHASE_651_BACKFILL_SUBJECT_TOKEN = "phase 651 walkthrough and status backfill"
ALLOWED_MAIN_PREFIXES = {
    str(DOC_PATH),
    str(TEST_PATH),
    "ilc_core/server.py",
    "ilc_core/storage/lmdb_public_runtime.py",
    "ilc_core/protocol/public_receipt_runtime.py",
}
REQUIRED_HEADINGS = (
    "## 1. Runtime target and inherited schema discipline",
    "## 2. Receipt issuance and persistence contract",
    "## 3. Read-only query modes and indexing",
    "## 4. Verification, failure tokens, and fail-closed behavior",
    "## 5. Explicit exclusions and preserved boundaries",
)
REQUIRED_TOKENS = (
    "public_receipt_runtime_651_live",
    "exactly_four_public_receipt_classes_supported_in_runtime",
    "receipt_query_read_only_runtime_live",
    "receipt_query_fails_closed_with_machine_tokens",
    "receipt_runtime_preserves_phase_586_schema_discipline",
    "no_revocation_or_wallet_write_widening_in_651",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _find_commit_ref(*, subject_token: str) -> str | None:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject_token in subject.lower():
            return commit_hash
    return None


def _require_commit_or_skip(subject_token: str) -> None:
    if _find_commit_ref(subject_token=subject_token) is None:
        pytest.skip(f"commit_not_yet_present:{subject_token}")


def _derived_agent_id() -> str:
    return derive_agent_id(bytes.fromhex("00112233445566778899aabbccddeeff"))


def _valid_namespace_receipt_payload() -> dict[str, object]:
    signer_agent_id = _derived_agent_id()
    return {
        "artifact_kind": "public_namespace_authority_receipt",
        "schema_version": "v0.1",
        "signer_agent_id": signer_agent_id,
        "authority_scope": "public_namespace_authority",
        "lineage_ref": "receipt:activation:0001",
        "epoch_id": "public-init-admission::0",
        "issued_at": 1700000000,
        "verification_material_ref": "sigref:namespace:0001",
        "verification_status": "valid",
        "namespace_label": "alice",
        "bound_agent_id": signer_agent_id,
        "activation_receipt_ref": "receipt:activation:0001",
    }


def _valid_admission_payload() -> dict[str, object]:
    return {
        "agent_id": _derived_agent_id(),
        "canonical_root_key_hex": "00112233445566778899aabbccddeeff",
        "authority_scope": "public_init_admission",
        "lineage_ref": "receipt:bootstrap:activation:0001",
        "verification_material_ref": "sigref:bootstrap:0001",
        "stake_binding_ref_or_null": None,
    }


def test_runtime_doc_exists_and_contains_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_runtime_doc_contains_required_tokens_and_phase_586_to_616_lineage() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text
    assert "Phase 586 remains the governing receipt representation cluster." in text
    assert "Phase 616 is the concrete schema/query contract derived from that cluster" in text


def test_runtime_supports_exactly_four_locked_receipt_classes() -> None:
    assert len(RECEIPT_CLASS_FIELDS) == 4
    assert set(RECEIPT_CLASS_FIELDS) == {
        "public_identity_activation_receipt",
        "public_namespace_authority_receipt",
        "public_quorum_eligibility_receipt",
        "settlement_linked_public_legitimacy_receipt",
    }


def test_receipt_query_modes_are_read_only_and_bounded() -> None:
    app = create_app()
    with TestClient(app):
        issued_receipt = issue_public_receipt(
            payload=_valid_namespace_receipt_payload(),
            store=app.state.public_receipt_store,
        )["receipt"]

        by_id = query_public_receipts(
            store=app.state.public_receipt_store,
            receipt_id=issued_receipt["receipt_id"],
        )
        assert by_id["token"] == "receipt_query_result"
        assert by_id["receipts"][0]["receipt_id"] == issued_receipt["receipt_id"]

        by_signer = query_public_receipts(
            store=app.state.public_receipt_store,
            signer_agent_id=issued_receipt["signer_agent_id"],
        )
        assert len(by_signer["receipts"]) == 1

        by_artifact_epoch = query_public_receipts(
            store=app.state.public_receipt_store,
            artifact_kind=issued_receipt["artifact_kind"],
            epoch_id=issued_receipt["epoch_id"],
        )
        assert len(by_artifact_epoch["receipts"]) == 1


def test_phase_650_admission_receipts_are_queryable_through_phase_651_surface() -> None:
    app = create_app()
    with TestClient(app):
        receipt = issue_public_init_admission_receipt(
            payload=_valid_admission_payload(),
            epoch_id=f"public-init-admission::{app.state.consensus.epoch_index}",
            store=app.state.public_receipt_store,
        )["receipt"]
        queried = query_public_receipts(
            store=app.state.public_receipt_store,
            receipt_id=receipt["receipt_id"],
        )["receipts"][0]
        assert queried == receipt


def test_verification_and_query_fail_closed_with_machine_tokens() -> None:
    app = create_app()
    with TestClient(app):
        unsupported_payload = _valid_namespace_receipt_payload()
        unsupported_payload["artifact_kind"] = "fifth_receipt_class"
        with pytest.raises(PublicReceiptRuntimeError) as exc_info:
            issue_public_receipt(
                payload=unsupported_payload,
                store=app.state.public_receipt_store,
            )
        assert exc_info.value.token == "unsupported_receipt_class"

        missing_scope_payload = _valid_namespace_receipt_payload()
        missing_scope_payload["authority_scope"] = ""
        with pytest.raises(PublicReceiptRuntimeError) as exc_info:
            issue_public_receipt(
                payload=missing_scope_payload,
                store=app.state.public_receipt_store,
            )
        assert exc_info.value.token == "missing_scope"

        with pytest.raises(PublicReceiptRuntimeError) as exc_info:
            query_public_receipts(store=app.state.public_receipt_store)
        assert exc_info.value.token == "invalid_query_mode"

        with pytest.raises(PublicReceiptRuntimeError) as exc_info:
            query_public_receipts(
                store=app.state.public_receipt_store,
                artifact_kind="public_namespace_authority_receipt",
            )
        assert exc_info.value.token == "epoch_id_required"

        with pytest.raises(PublicReceiptRuntimeError) as exc_info:
            query_public_receipts(
                store=app.state.public_receipt_store,
                receipt_id="does-not-exist",
            )
        assert exc_info.value.token == "receipt_not_found"


def test_phase_1378_closes_public_receipt_http_routes() -> None:
    app = create_app()
    with TestClient(app) as client:
        assert client.post("/v1/public/receipt", json=_valid_namespace_receipt_payload()).status_code == 404
        assert client.get("/v1/public/receipt/does-not-exist").status_code == 404
        assert client.get("/v1/public/receipts").status_code == 404


def test_no_wallet_widening_or_revocation_opening_is_claimed() -> None:
    text = _read(DOC_PATH)
    assert "no revocation or succession policy opening" in text
    assert "no wallet write, transfer, withdrawal, or spend authority" in text


def test_main_commit_touches_expected_runtime_scope_without_decision_log_mutation() -> None:
    _require_commit_or_skip(PHASE_651_SUBJECT_TOKEN)
    commit_ref = _find_commit_ref(subject_token=PHASE_651_SUBJECT_TOKEN)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DOC_PATH) in changed_paths
    assert str(TEST_PATH) in changed_paths
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    unexpected = {path for path in changed_paths if path not in ALLOWED_MAIN_PREFIXES}
    assert not unexpected


def test_backfill_commit_touches_walkthrough_and_status_only() -> None:
    _require_commit_or_skip(PHASE_651_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _find_commit_ref(subject_token=PHASE_651_BACKFILL_SUBJECT_TOKEN)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == {str(WALKTHROUGH_PATH), str(STATUS_PATH)}


def test_phase_651_phase_test_passes_post_commit() -> None:
    _require_commit_or_skip(PHASE_651_SUBJECT_TOKEN)
    result = subprocess.run(
        [
            "bash",
            "-lc",
            "PATH=.venv/bin:$PATH .venv/bin/pytest "
            "tests/test_phase_651_public_receipt_runtime.py "
            "-q -k 'not test_phase_651_phase_test_passes_post_commit'",
        ],
        capture_output=True,
        check=True,
        text=True,
    )
    assert "passed" in result.stdout
