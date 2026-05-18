from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from ilc_core.governance import fork_legitimacy_runtime as runtime


RUNTIME_PATH = Path("ilc_core/governance/fork_legitimacy_runtime.py")
SPEC_PATH = Path("docs/specs/ilc_cdl_009_fork_legitimacy_ux_1383_v0.1.md")
REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PROMPT_PATH = Path(
    "docs/antigravity_tasks/antigravity_prompt__phase_1383_g8_cdl_009_fork_legitimacy_ux.md"
)


def _badge(**overrides: object) -> dict[str, object]:
    badge: dict[str, object] = {
        "authority_scope": "fork_legitimacy",
        "badge_id": "badge:fork-legitimacy:phase-1383",
        "badge_schema_version": runtime.FORK_LEGITIMACY_BADGE_SCHEMA_VERSION,
        "canonical_genesis_root_hash": runtime.ADR0037_GENESIS_V0_1_ROOT_ENVELOPE_HASH,
        "evidence_refs": ["sha256:badge-evidence"],
        "fork_id": "fork:canonical-lineage-demo",
        "fork_root_ref": "sha256:fork-root",
        "issued_epoch": 1383,
        "lineage_proof_ref": "sha256:lineage-proof",
        "signature_algorithm": "ML-DSA-65",
        "signature_ref": "sha256:signature",
        "signature_verification_status": "verified",
        "signer_authority": "genesis_authority",
    }
    badge.update(overrides)
    return badge


def _eligibility(**overrides: object) -> dict[str, object]:
    evidence: dict[str, object] = {
        "canonical_genesis_lineage": True,
        "canonical_genesis_root_hash": runtime.ADR0037_GENESIS_V0_1_ROOT_ENVELOPE_HASH,
        "eligibility_rule_version": runtime.FORK_ELIGIBILITY_RULE_VERSION,
        "fork_root_ref": "sha256:fork-root",
        "lineage_proof_ref": "sha256:lineage-proof",
        "no_stripped_public_legitimacy_chain": True,
        "not_naming_only": True,
        "public_identity_lineage_ref": "sha256:public-identity-lineage",
        "public_legitimacy_chain": True,
        "public_quorum_lineage_ref": "sha256:public-quorum-lineage",
        "settlement_lineage_ref": "sha256:settlement-lineage",
    }
    evidence.update(overrides)
    return evidence


def _fork_signal(
    *,
    badge: dict[str, object] | None = None,
    evidence: dict[str, object] | None = None,
    fork_id: str = "fork:canonical-lineage-demo",
    fork_root_ref: str = "sha256:fork-root",
) -> dict[str, object]:
    return {
        "eligibility_evidence": evidence if evidence is not None else _eligibility(),
        "fork_id": fork_id,
        "fork_root_ref": fork_root_ref,
        "signal_schema_version": runtime.FORK_SIGNAL_SCHEMA_VERSION,
        "signature_badge": badge if badge is not None else _badge(),
    }


def test_phase_1383_required_tokens_and_public_rc_exclude_marker() -> None:
    runtime_source = RUNTIME_PATH.read_text(encoding="utf-8")
    spec = SPEC_PATH.read_text(encoding="utf-8")
    prompt = PROMPT_PATH.read_text(encoding="utf-8")

    for token in (
        "cdl_009_fork_legitimacy_ux_phase_1383.v0.1",
        "cdl_009_signature_badge_schema_implemented",
        "cdl_009_eligibility_rules_contract_committed",
    ):
        assert token in runtime_source
        assert token in spec
        assert token in prompt

    assert (
        "PUBLIC_RC_EXCLUDE: cdl_009_fork_legitimacy_ux_phase_1383.v0.1"
        in runtime_source
    )


def test_cdl_009_register_and_phase_993_record_lock_selected_model() -> None:
    register = REGISTER_PATH.read_text(encoding="utf-8")
    row = next(line for line in register.splitlines() if line.startswith("| CDL-009 |"))

    assert "| ratified |" in row
    assert "| naming-only, signature-badge, signature-badge+eligibility rules |" in row
    assert "| signature-badge+eligibility rules |" in row
    assert "`CDL-009`: selected `signature-badge+eligibility rules`" in register


def test_badge_schema_and_eligibility_contract_are_machine_readable() -> None:
    badge_schema = runtime.signature_badge_schema()
    rules = runtime.eligibility_rules_contract()
    signal_schema = runtime.fork_signal_schema()

    assert badge_schema["schema_version"] == runtime.FORK_LEGITIMACY_BADGE_SCHEMA_VERSION
    assert badge_schema["schema_token"] == runtime.CDL009_SIGNATURE_BADGE_SCHEMA_TOKEN
    assert "signature_verification_status" in badge_schema["required_fields"]
    assert "naming-only" in rules["forbidden_models"]
    assert "bare signature-badge" in rules["forbidden_models"]
    assert rules["contract_token"] == runtime.CDL009_ELIGIBILITY_RULES_CONTRACT_TOKEN
    assert signal_schema["schema_version"] == runtime.FORK_SIGNAL_SCHEMA_VERSION


def test_valid_fork_signal_passes_with_deterministic_badge_ref() -> None:
    signal = _fork_signal()

    result = runtime.inspect_fork_signal(signal)

    assert result["eligible_for_legitimacy_badge"] is True
    assert result["decision"] == "eligible"
    assert result["failed_rules"] == []
    assert result["public_api_activation"] is False
    assert result["operator_surface"] == "cli_local_only_no_public_api"

    normalized_badge = runtime.validate_signature_badge(signal["signature_badge"])
    expected_ref = "sha256:" + hashlib.sha256(
        runtime.canonical_json(normalized_badge).encode("utf-8")
    ).hexdigest()
    assert result["badge_ref"] == expected_ref
    assert runtime.signature_badge_ref(signal["signature_badge"]) == expected_ref


def test_naming_only_and_bare_signature_badge_paths_fail_closed() -> None:
    naming_only = _fork_signal(evidence=_eligibility(not_naming_only=False))
    bare_badge = _fork_signal(evidence=_eligibility(public_legitimacy_chain=False))

    naming_result = runtime.inspect_fork_signal(naming_only)
    bare_result = runtime.inspect_fork_signal(bare_badge)

    assert naming_result["eligible_for_legitimacy_badge"] is False
    assert "naming_only_signal_forbidden" in naming_result["failed_rules"]
    assert bare_result["eligible_for_legitimacy_badge"] is False
    assert "public_legitimacy_chain_missing" in bare_result["failed_rules"]

    missing_badge = _fork_signal()
    del missing_badge["signature_badge"]
    with pytest.raises(ValueError, match="fork_signal_missing_required_field:signature_badge"):
        runtime.validate_fork_signal(missing_badge)


def test_wrong_genesis_root_unverified_badge_and_stripped_chain_fail_closed() -> None:
    unverified = _fork_signal(
        badge=_badge(signature_verification_status="not_checked"),
        evidence=_eligibility(no_stripped_public_legitimacy_chain=False),
    )

    result = runtime.inspect_fork_signal(unverified)

    assert result["eligible_for_legitimacy_badge"] is False
    assert "signature_badge_not_verified" in result["failed_rules"]
    assert "stripped_public_legitimacy_chain" in result["failed_rules"]

    wrong_root_badge = _badge(canonical_genesis_root_hash="sha256:bad-root")
    with pytest.raises(ValueError, match="signature_badge_genesis_root_hash_invalid"):
        runtime.validate_signature_badge(wrong_root_badge)


def test_mismatched_lineage_and_fork_refs_fail_closed() -> None:
    signal = _fork_signal(
        badge=_badge(fork_root_ref="sha256:badge-root"),
        evidence=_eligibility(lineage_proof_ref="sha256:different-lineage"),
    )

    result = runtime.inspect_fork_signal(signal)

    assert result["eligible_for_legitimacy_badge"] is False
    assert "signal_badge_fork_root_ref_mismatch" in result["failed_rules"]
    assert "lineage_proof_ref_mismatch" in result["failed_rules"]


def test_canonical_json_is_sorted_and_rejects_non_json_constants() -> None:
    payload = {"z": 1, "a": {"b": 2}}
    assert runtime.canonical_json(payload) == json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    )

    with pytest.raises(ValueError):
        runtime.canonical_json({"bad": float("nan")})

    first = runtime.canonical_schema_bundle_json()
    second = runtime.canonical_schema_bundle_json()
    assert first == second
    assert first == json.dumps(
        json.loads(first), sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def test_cli_operator_surface_reads_local_json_and_emits_decision(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    signal_path = tmp_path / "fork_signal.json"
    signal_path.write_text(json.dumps(_fork_signal(), sort_keys=True), encoding="utf-8")

    exit_code = runtime.main([str(signal_path)])
    output = capsys.readouterr().out.strip()
    parsed = json.loads(output)

    assert exit_code == 0
    assert parsed["eligible_for_legitimacy_badge"] is True
    assert parsed["runtime_token"] == runtime.CDL009_FORK_LEGITIMACY_UX_TOKEN

    bad_path = tmp_path / "bad_fork_signal.json"
    bad_path.write_text(
        json.dumps(
            _fork_signal(badge=_badge(signature_verification_status="unverified")),
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    bad_exit_code = runtime.main([str(bad_path)])
    bad_output = capsys.readouterr().out.strip()
    bad_parsed = json.loads(bad_output)

    assert bad_exit_code == 1
    assert bad_parsed["eligible_for_legitimacy_badge"] is False
    assert "signature_badge_not_verified" in bad_parsed["failed_rules"]


def test_cli_loader_bounds_local_json_payload_size(tmp_path: Path) -> None:
    signal_path = tmp_path / "fork_signal.json"
    signal_path.write_text(json.dumps(_fork_signal(), sort_keys=True), encoding="utf-8")

    loaded = runtime.load_fork_signal_json_file(signal_path, max_bytes=4096)
    assert loaded["signal_schema_version"] == runtime.FORK_SIGNAL_SCHEMA_VERSION

    with pytest.raises(ValueError, match="fork_signal_json_file_too_large"):
        runtime.load_fork_signal_json_file(signal_path, max_bytes=1)
