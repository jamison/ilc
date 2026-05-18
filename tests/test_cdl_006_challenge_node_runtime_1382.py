from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ilc_core.governance import challenge_node_runtime as runtime


RUNTIME_PATH = Path("ilc_core/governance/challenge_node_runtime.py")
PROMPT_PATH = Path(
    "docs/antigravity_tasks/antigravity_prompt__phase_1382_g8_cdl_006_challenge_node_runtime.md"
)


def _attestation(
    body_role: str,
    *,
    body_id: str | None = None,
    verdict: str = "approve_challenge",
) -> dict[str, object]:
    return {
        "attestation_ref": f"sha256:{body_role}-attestation",
        "body_id": body_id or f"{body_role}-body",
        "body_role": body_role,
        "epoch": 1382,
        "signer_agent_id": f"agent:{body_role}",
        "signature_ref": f"sha256:{body_role}-signature",
        "verdict": verdict,
    }


def _challenge_record(
    attestations: list[dict[str, object]] | None = None,
    *,
    audit_path_ref: str = "sha256:challenge-audit-genesis",
) -> dict[str, object]:
    return {
        "audit_path_ref": audit_path_ref,
        "body_attestations": attestations
        if attestations is not None
        else [
            _attestation("constitutional"),
            _attestation("technical"),
            _attestation("affected_party"),
        ],
        "challenge_id": "challenge:cdl-006:phase-1382",
        "challenged_action_ref": "sha256:challenged-action",
        "created_epoch": 1382,
        "creator_agent_id": "agent:creator",
        "evidence_refs": ["sha256:evidence-a", "sha256:evidence-b"],
        "governance_basis_ref": "CDL-006",
        "remedy_requested": "reopen",
        "schema_version": runtime.CHALLENGE_RECORD_SCHEMA_VERSION,
        "status": "under_review",
    }


def test_phase_1382_required_tokens_and_public_rc_exclude_marker() -> None:
    source = RUNTIME_PATH.read_text(encoding="utf-8")
    prompt = PROMPT_PATH.read_text(encoding="utf-8")

    for token in (
        "cdl_006_challenge_node_runtime_phase_1382.v0.1",
        "cdl_006_3_body_quorum_verification_implemented",
        "cdl_006_audit_path_record_writer_implemented",
    ):
        assert token in source
        assert token in prompt

    assert (
        "PUBLIC_RC_EXCLUDE: cdl_006_challenge_node_runtime_phase_1382.v0.1"
        in source
    )


def test_three_body_affirmative_quorum_passes_and_is_canonical() -> None:
    challenge = _challenge_record()

    assert runtime.verify_challenge_quorum(challenge) is True

    normalized = runtime.validate_challenge_record(challenge)
    assert [item["body_role"] for item in normalized["body_attestations"]] == [
        "constitutional",
        "technical",
        "affected_party",
    ]

    first_ref = runtime.challenge_record_ref(challenge)
    second_ref = runtime.challenge_record_ref(dict(reversed(list(challenge.items()))))
    assert first_ref == second_ref
    assert first_ref.startswith("sha256:")
    assert len(first_ref.removeprefix("sha256:")) == 64


def test_two_body_and_non_affirmative_quorum_do_not_pass() -> None:
    two_body = _challenge_record(
        [_attestation("constitutional"), _attestation("technical")]
    )
    abstain = _challenge_record(
        [
            _attestation("constitutional"),
            _attestation("technical", verdict="abstain"),
            _attestation("affected_party"),
        ]
    )
    reject = _challenge_record(
        [
            _attestation("constitutional"),
            _attestation("technical", verdict="reject_challenge"),
            _attestation("affected_party"),
        ]
    )

    assert runtime.verify_challenge_quorum(two_body) is False
    assert runtime.verify_challenge_quorum(abstain) is False
    assert runtime.verify_challenge_quorum(reject) is False


def test_duplicate_body_ids_and_roles_fail_closed() -> None:
    duplicate_body_id = _challenge_record(
        [
            _attestation("constitutional", body_id="same-body"),
            _attestation("technical", body_id="same-body"),
            _attestation("affected_party"),
        ]
    )
    duplicate_role = _challenge_record(
        [
            _attestation("constitutional", body_id="constitutional-a"),
            _attestation("constitutional", body_id="constitutional-b"),
            _attestation("affected_party"),
        ]
    )

    with pytest.raises(ValueError, match="challenge_quorum_duplicate_body_id_phase_1382"):
        runtime.verify_challenge_quorum(duplicate_body_id)
    with pytest.raises(ValueError, match="challenge_quorum_duplicate_body_role_phase_1382"):
        runtime.verify_challenge_quorum(duplicate_role)


def test_single_or_dual_body_required_role_override_is_rejected() -> None:
    challenge = _challenge_record()

    with pytest.raises(
        ValueError,
        match="required_body_roles_must_equal_cdl_006_3_body_set_phase_1382",
    ):
        runtime.verify_challenge_quorum(
            challenge, required_body_roles=("constitutional",)
        )
    with pytest.raises(
        ValueError,
        match="required_body_roles_must_equal_cdl_006_3_body_set_phase_1382",
    ):
        runtime.verify_challenge_quorum(
            challenge, required_body_roles=("constitutional", "technical")
        )


def test_challenge_record_schema_enforcement_rejects_invalid_records() -> None:
    missing_field = _challenge_record()
    del missing_field["governance_basis_ref"]
    invalid_epoch = _challenge_record()
    invalid_epoch["created_epoch"] = True
    invalid_schema = _challenge_record()
    invalid_schema["schema_version"] = "cdl_006_challenge_record_v0"

    with pytest.raises(ValueError, match="challenge_record_missing_required_field"):
        runtime.validate_challenge_record(missing_field)
    with pytest.raises(ValueError, match="created_epoch_must_be_non_negative_int"):
        runtime.validate_challenge_record(invalid_epoch)
    with pytest.raises(ValueError, match="challenge_record_schema_version_invalid"):
        runtime.validate_challenge_record(invalid_schema)


def test_audit_path_writer_emits_deterministic_hash_linked_record() -> None:
    challenge = _challenge_record(audit_path_ref="sha256:previous-head")
    audit_event = {
        "entry_epoch": 1382,
        "entry_type": "body_attested",
        "payload_ref": "sha256:payload",
        "writer_agent_id": "agent:writer",
    }

    first = runtime.write_challenge_audit_path_record(
        challenge, audit_event, previous_entry_ref="sha256:previous-entry"
    )
    second = runtime.write_challenge_audit_path_record(
        dict(reversed(list(challenge.items()))),
        dict(reversed(list(audit_event.items()))),
        previous_entry_ref="sha256:previous-entry",
    )

    assert first == second
    for field in runtime.REQUIRED_AUDIT_ENTRY_FIELDS:
        assert field in first

    core = {
        "challenge_id": first["challenge_id"],
        "entry_epoch": first["entry_epoch"],
        "entry_type": first["entry_type"],
        "payload_ref": first["payload_ref"],
        "previous_entry_ref": first["previous_entry_ref"],
        "schema_version": first["schema_version"],
        "writer_agent_id": first["writer_agent_id"],
    }
    expected_entry_id = "sha256:" + hashlib.sha256(
        runtime.canonical_json(core).encode("utf-8")
    ).hexdigest()
    assert first["audit_entry_id"] == expected_entry_id
    assert runtime.audit_path_entry_ref(first) == expected_entry_id
    assert first["graph_commitment_path"]["audit_path_head_ref"] == expected_entry_id
    assert first["graph_commitment_path"]["prior_challenge_audit_path_ref"] == (
        "sha256:previous-head"
    )
    assert first["writer_token"] == runtime.CDL006_AUDIT_PATH_RECORD_WRITER_TOKEN


def test_runtime_canonical_json_is_sorted_and_rejects_non_json_constants() -> None:
    payload = {"z": 1, "a": {"b": 2}}
    assert runtime.canonical_json(payload) == json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    )

    with pytest.raises(ValueError):
        runtime.canonical_json({"bad": float("nan")})
