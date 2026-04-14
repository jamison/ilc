from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ilc_core.identity.agent_id_runtime import derive_agent_id
from ilc_core.server import create_app

DOC_PATH = Path("docs/specs/ilc_public_init_admission_runtime_650_v0.1.md")
TEST_PATH = Path("tests/test_phase_650_public_init_admission_runtime.py")
WALKTHROUGH_PATH = Path("docs/phases/phase_650_g8_public_init_admission_runtime_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_650_SUBJECT_TOKEN = "phase 650 public init/admission runtime"
PHASE_650_BACKFILL_SUBJECT_TOKEN = "phase 650 walkthrough and status backfill"
ALLOWED_MAIN_PREFIXES = {
    str(DOC_PATH),
    str(TEST_PATH),
    "ilc_core/server.py",
    "ilc_core/storage/lmdb_public_runtime.py",
    "ilc_core/protocol/public_init_admission_runtime.py",
}
REQUIRED_HEADINGS = (
    "## 1. Runtime target and inherited contract",
    "## 2. Bounded request and response contract",
    "## 3. Admission receipt issuance and persistence",
    "## 4. Failure-token and fail-closed discipline",
    "## 5. Explicit exclusions and preserved boundaries",
)
REQUIRED_TOKENS = (
    "public_init_admission_runtime_650_live",
    "init_request_requires_canonical_agent_id_and_lineage_inputs",
    "bounded_admission_receipt_runtime_issued_and_persisted",
    "init_admission_runtime_fails_closed_with_machine_tokens",
    "wallet_boundary_576_581_preserved_in_650",
    "no_chain_side_or_permissionless_admission_in_650",
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


def _valid_payload() -> dict[str, str | None]:
    root_key_hex = "00112233445566778899aabbccddeeff"
    agent_id = derive_agent_id(bytes.fromhex(root_key_hex))
    return {
        "agent_id": agent_id,
        "canonical_root_key_hex": root_key_hex,
        "authority_scope": "public_init_admission",
        "lineage_ref": "receipt:bootstrap:activation:0001",
        "verification_material_ref": "sigref:bootstrap:0001",
        "stake_binding_ref_or_null": None,
    }


def test_runtime_doc_exists_and_contains_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_runtime_doc_contains_required_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_init_admission_runtime_requires_canonical_key_derived_identity_and_persists_receipt() -> None:
    app = create_app()
    with TestClient(app) as client:
        response = client.post("/v1/public/init/admission", json=_valid_payload())
        assert response.status_code == 200
        payload = response.json()
        assert payload["ok"] is True
        assert payload["token"] == "admission_receipt_issued"
        assert payload["persisted"] is True
        receipt = payload["receipt"]
        assert receipt["artifact_kind"] == "public_identity_activation_receipt"
        assert receipt["authority_scope"] == "public_init_admission"
        assert receipt["signer_agent_id"] == _valid_payload()["agent_id"]
        assert receipt["issued_at"] == 0
        persisted = app.state.public_admission_store.get_admission_receipt(receipt["receipt_id"])
        assert persisted == receipt


def test_same_epoch_same_payload_produces_deterministic_receipt_id() -> None:
    app = create_app()
    with TestClient(app) as client:
        first = client.post("/v1/public/init/admission", json=_valid_payload())
        second = client.post("/v1/public/init/admission", json=_valid_payload())
        assert first.status_code == 200
        assert second.status_code == 200
        assert first.json()["receipt"]["receipt_id"] == second.json()["receipt"]["receipt_id"]


def test_missing_lineage_scope_and_attestation_fail_closed_with_machine_tokens() -> None:
    app = create_app()
    with TestClient(app) as client:
        base = _valid_payload()
        for field_name, expected_token in (
            ("lineage_ref", "missing_lineage"),
            ("authority_scope", "missing_scope"),
            ("verification_material_ref", "missing_attestation"),
        ):
            payload = dict(base)
            payload[field_name] = ""
            response = client.post("/v1/public/init/admission", json=payload)
            assert response.status_code == 400
            assert response.json() == {"ok": False, "token": expected_token}


def test_canonical_root_key_mismatch_fails_closed() -> None:
    app = create_app()
    with TestClient(app) as client:
        payload = _valid_payload()
        payload["canonical_root_key_hex"] = "ffeeddccbbaa99887766554433221100"
        response = client.post("/v1/public/init/admission", json=payload)
        assert response.status_code == 400
        assert response.json() == {"ok": False, "token": "canonical_agent_id_mismatch"}


def test_wallet_boundary_is_preserved_in_receipt_surface() -> None:
    app = create_app()
    with TestClient(app) as client:
        response = client.post("/v1/public/init/admission", json=_valid_payload())
        receipt = response.json()["receipt"]
        for forbidden_field in (
            "spend_authority",
            "withdrawal_authority",
            "claimability_state",
            "wallet_balance",
        ):
            assert forbidden_field not in receipt


def test_forbidden_scope_fails_closed() -> None:
    app = create_app()
    with TestClient(app) as client:
        payload = _valid_payload()
        payload["authority_scope"] = "permissionless_admission"
        response = client.post("/v1/public/init/admission", json=payload)
        assert response.status_code == 400
        assert response.json() == {"ok": False, "token": "authority_scope_forbidden"}


def test_main_commit_touches_expected_runtime_scope_without_decision_log_mutation() -> None:
    _require_commit_or_skip(PHASE_650_SUBJECT_TOKEN)
    commit_ref = _find_commit_ref(subject_token=PHASE_650_SUBJECT_TOKEN)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DOC_PATH) in changed_paths
    assert str(TEST_PATH) in changed_paths
    assert str(DECISION_LOG_PATH) not in changed_paths
    assert not any(path.startswith("docs/adr/") for path in changed_paths)
    unexpected = {path for path in changed_paths if path not in ALLOWED_MAIN_PREFIXES}
    assert not unexpected


def test_backfill_commit_touches_walkthrough_and_status_only() -> None:
    _require_commit_or_skip(PHASE_650_BACKFILL_SUBJECT_TOKEN)
    commit_ref = _find_commit_ref(subject_token=PHASE_650_BACKFILL_SUBJECT_TOKEN)
    assert commit_ref is not None
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == {str(WALKTHROUGH_PATH), str(STATUS_PATH)}


def test_phase_650_phase_test_passes_post_commit() -> None:
    _require_commit_or_skip(PHASE_650_SUBJECT_TOKEN)
    result = subprocess.run(
        [
            "bash",
            "-lc",
            "PATH=.venv/bin:$PATH .venv/bin/pytest "
            "tests/test_phase_650_public_init_admission_runtime.py "
            "-q -k 'not test_phase_650_phase_test_passes_post_commit'",
        ],
        capture_output=True,
        check=True,
        text=True,
    )
    assert "passed" in result.stdout
