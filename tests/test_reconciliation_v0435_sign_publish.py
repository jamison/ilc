# SPDX-License-Identifier: AGPL-3.0-only
"""Focused security tests for the v0.4.35 reconciliation ceremony."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.error import HTTPError

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey
import pytest

from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.epistemic.truth_primitive_graph_store import node_id_from_submission
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    validate_truth_primitive_submission,
)
from ilc_core.identity.bls_backend import keypair_from_ikm_hex
from ilc_core.release import current_policy
from ilc_core.release import upgrade_check
from ilc_core.release.upgrade_check import validate_release_assertion
from tools import reconciliation_v0435_sign_publish as ceremony


BASELINE = Path(
    "docs/specs/ilc_rc_native_distribution_closure_strike_force_"
    "execution_manifest_v0.2.json"
)
AMENDMENT = Path(
    "docs/specs/ilc_rc_native_distribution_closure_strike_force_"
    "execution_manifest_v0.2_amendment_01.md"
)
RECONCILIATION = Path(
    "docs/specs/ilc_rc_native_distribution_closure_strike_force_"
    "execution_manifest_v0.2_reconciliation_00.md"
)
ATTESTATION = Path(
    "docs/specs/ilc_core_0435_unsigned_build_attestation_reconciliation_00_v0.1.json"
)
ARTIFACT_DIR = Path("out/reconciliation_r5a_final/artifacts")
PRIOR_VIEW = Path("out/gap_rc_native_distribution_vnext_sign_publish_00/current_policy_view.json")
POLICY_PUBLIC_RECORD = Path("docs/genesis/genesis_agent1_pubkey_record_838a.txt")


def _json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _write_json(path: Path, value: object) -> Path:
    path.write_text(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False),
        encoding="utf-8",
    )
    return path


def _write_secret(path: Path, value: str, mode: int = 0o600) -> Path:
    path.write_text(value + "\n", encoding="ascii")
    path.chmod(mode)
    return path


def _release_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Ed25519PrivateKey]:
    key = Ed25519PrivateKey.generate()
    path = tmp_path / "release-key.pem"
    path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    path.chmod(0o600)
    public_hex = key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    ).hex()
    monkeypatch.setattr(ceremony, "EXPECTED_RELEASE_PUBLIC_KEY_HEX", public_hex)
    monkeypatch.setattr(upgrade_check, "release_signer_public_key_hex", lambda: public_hex)
    return path, key


def _signed_envelopes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[dict, Path]:
    key_path, _key = _release_key(tmp_path, monkeypatch)
    envelopes, receipt = ceremony.sign_release(
        attestation_path=ATTESTATION,
        artifact_dir=ARTIFACT_DIR,
        release_key_path=key_path,
    )
    assert receipt["artifact_count"] == 2
    path = _write_json(tmp_path / "envelopes.json", envelopes)
    return envelopes, path


def _provider_receipt(tmp_path: Path) -> Path:
    rows = []
    for artifact_type, expected in sorted(ceremony.EXPECTED_ARTIFACTS.items()):
        rows.append(
            {
                "artifact_type": artifact_type,
                "filename": expected["filename"],
                "github_release_url": (
                    f"https://github.com/jamison/ilc/releases/download/v0.4.35/"
                    f"{expected['filename']}"
                ),
                "pypi_url": f"https://files.pythonhosted.org/test/{expected['filename']}",
                "sha256": expected["sha256"],
                "size_bytes": expected["size_bytes"],
                "github_fetchback_verified": True,
                "github_redirect_count": 1,
                "pypi_fetchback_verified": True,
                "pypi_redirect_count": 0,
                "pypi_yanked": False,
            }
        )
    return _write_json(
        tmp_path / "providers.json",
        {
            "artifacts": rows,
            "phase": ceremony.PHASE,
            "schema_version": "ilc.reconciliation.v0435.provider_fetchback.v0.1",
        },
    )


def _release_assertion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[dict, Path]:
    _envelopes, envelope_path = _signed_envelopes(tmp_path, monkeypatch)
    assertion, receipt = ceremony.finalize_release(
        attestation_path=ATTESTATION,
        artifact_dir=ARTIFACT_DIR,
        envelope_set_path=envelope_path,
        provider_receipt_path=_provider_receipt(tmp_path),
    )
    assert receipt["verified_attestation_count"] == 2
    return assertion, _write_json(tmp_path / "assertion.json", assertion)


def test_authorization_hashes_and_r5a_attestation_are_exact() -> None:
    ceremony._verify_authorization_hashes(BASELINE, AMENDMENT, RECONCILIATION)
    attestation, artifacts = ceremony.validate_r5a_attestation(
        ATTESTATION, ARTIFACT_DIR
    )
    assert attestation["source_freeze_commit"] == ceremony.EXPECTED_SOURCE_FREEZE
    assert {row["artifact_type"] for row in artifacts} == {"wheel", "sdist"}


def test_direct_script_invocation_resolves_repository_imports() -> None:
    result = subprocess.run(
        [sys.executable, "tools/reconciliation_v0435_sign_publish.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert "Bounded ceremony tooling" in result.stdout


def test_authorization_hash_substitution_fails(tmp_path: Path) -> None:
    altered = tmp_path / "reconciliation.md"
    altered.write_text("substituted\n", encoding="utf-8")
    with pytest.raises(
        ceremony.ReconciliationCeremonyError,
        match="reconciliation_manifest_sha256_mismatch",
    ):
        ceremony._verify_authorization_hashes(BASELINE, AMENDMENT, altered)


def test_json_loader_rejects_duplicate_keys_and_nonfinite(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"a":1,"a":2}', encoding="utf-8")
    with pytest.raises(ceremony.ReconciliationCeremonyError, match="json_duplicate_key"):
        ceremony._load_json(duplicate)
    nonfinite = tmp_path / "nonfinite.json"
    nonfinite.write_text('{"a":NaN}', encoding="utf-8")
    with pytest.raises(ceremony.ReconciliationCeremonyError, match="json_nonfinite_number"):
        ceremony._load_json(nonfinite)


def test_attestation_rejects_substituted_artifact_bytes(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    for expected in ceremony.EXPECTED_ARTIFACTS.values():
        source = ARTIFACT_DIR / expected["filename"]
        target = artifact_dir / expected["filename"]
        target.write_bytes(source.read_bytes())
    wheel = artifact_dir / ceremony.EXPECTED_ARTIFACTS["wheel"]["filename"]
    wheel.write_bytes(wheel.read_bytes() + b"substitution")
    with pytest.raises(ceremony.ReconciliationCeremonyError, match="artifact_bytes_mismatch"):
        ceremony.validate_r5a_attestation(ATTESTATION, artifact_dir)


def test_sign_release_is_strictly_two_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    envelopes, _path = _signed_envelopes(tmp_path, monkeypatch)
    assert envelopes["version"] == "0.4.35"
    assert set(envelopes["envelopes"]) == {
        expected["artifact_id"] for expected in ceremony.EXPECTED_ARTIFACTS.values()
    }
    assert all(
        envelope["prior_release_envelope_ref"] == ceremony.PRIOR_RELEASE_ENVELOPE_REF
        for envelope in envelopes["envelopes"].values()
    )
    assert ceremony.EXPECTED_CONSENSUS["artifact_id"] not in envelopes["envelopes"]


def test_sign_release_rejects_wrong_key_and_permissive_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    key_path, _key = _release_key(tmp_path, monkeypatch)
    monkeypatch.setattr(ceremony, "EXPECTED_RELEASE_PUBLIC_KEY_HEX", "00" * 32)
    with pytest.raises(
        ceremony.ReconciliationCeremonyError,
        match="release_private_key_authority_mismatch",
    ):
        ceremony.sign_release(
            attestation_path=ATTESTATION,
            artifact_dir=ARTIFACT_DIR,
            release_key_path=key_path,
        )
    key_path.chmod(0o644)
    with pytest.raises(
        ceremony.ReconciliationCeremonyError,
        match="release_private_key_permissions_invalid",
    ):
        ceremony._load_release_key(key_path)


def test_provider_receipt_rejects_redirect_like_unverified_state(tmp_path: Path) -> None:
    path = _provider_receipt(tmp_path)
    value = _json(path)
    value["artifacts"][0]["github_fetchback_verified"] = False
    _write_json(path, value)
    with pytest.raises(
        ceremony.ReconciliationCeremonyError, match="provider_fetchback_not_verified"
    ):
        ceremony._provider_rows(path)


def test_provider_receipt_rejects_unknown_fields(tmp_path: Path) -> None:
    path = _provider_receipt(tmp_path)
    value = _json(path)
    value["artifacts"][0]["redirect_target"] = "https://example.invalid"
    _write_json(path, value)
    with pytest.raises(
        ceremony.ReconciliationCeremonyError,
        match="provider_receipt_artifact_fields_invalid",
    ):
        ceremony._provider_rows(path)


def test_fetch_providers_recomputes_both_provider_results(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifacts = []
    for artifact_type, expected in sorted(ceremony.EXPECTED_ARTIFACTS.items()):
        artifacts.append(
            {
                "artifact_type": artifact_type,
                "filename": expected["filename"],
                "github_release_url": (
                    f"https://github.com/jamison/ilc/releases/download/v0.4.35/"
                    f"{expected['filename']}"
                ),
                "pypi_url": f"https://files.pythonhosted.org/test/{expected['filename']}",
            }
        )
    manifest = _write_json(
        tmp_path / "manifest.json",
        {
            "artifacts": artifacts,
            "phase": ceremony.PHASE,
            "schema_version": "ilc.reconciliation.v0435.provider_manifest.v0.1",
        },
    )
    calls: list[tuple[str, str]] = []

    def fake_fetch(url: str, *, expected_sha256: str, expected_size: int, provider: str) -> int:
        assert expected_sha256 in {
            value["sha256"] for value in ceremony.EXPECTED_ARTIFACTS.values()
        }
        assert expected_size > 0
        calls.append((provider, url))
        return 1 if provider == "github" else 0

    monkeypatch.setattr(ceremony, "_fetch_provider_url", fake_fetch)
    monkeypatch.setattr(
        ceremony,
        "_pypi_release_rows",
        lambda: {
            expected["filename"]: {
                "digests": {"sha256": expected["sha256"]},
                "filename": expected["filename"],
                "size": expected["size_bytes"],
                "url": f"https://files.pythonhosted.org/test/{expected['filename']}",
                "yanked": False,
            }
            for expected in ceremony.EXPECTED_ARTIFACTS.values()
        },
    )
    receipt = ceremony.fetch_providers(manifest)
    assert len(calls) == 4
    assert ceremony._provider_rows(_write_json(tmp_path / "receipt.json", receipt))


def test_fetch_providers_rejects_yanked_pypi_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifacts = [
        {
            "artifact_type": artifact_type,
            "filename": expected["filename"],
            "github_release_url": (
                f"https://github.com/jamison/ilc/releases/download/v0.4.35/"
                f"{expected['filename']}"
            ),
            "pypi_url": f"https://files.pythonhosted.org/test/{expected['filename']}",
        }
        for artifact_type, expected in sorted(ceremony.EXPECTED_ARTIFACTS.items())
    ]
    manifest = _write_json(
        tmp_path / "manifest-yanked.json",
        {
            "artifacts": artifacts,
            "phase": ceremony.PHASE,
            "schema_version": "ilc.reconciliation.v0435.provider_manifest.v0.1",
        },
    )
    monkeypatch.setattr(
        ceremony,
        "_pypi_release_rows",
        lambda: {
            expected["filename"]: {
                "digests": {"sha256": expected["sha256"]},
                "filename": expected["filename"],
                "size": expected["size_bytes"],
                "url": f"https://files.pythonhosted.org/test/{expected['filename']}",
                "yanked": artifact_type == "wheel",
            }
            for artifact_type, expected in ceremony.EXPECTED_ARTIFACTS.items()
        },
    )
    monkeypatch.setattr(ceremony, "_fetch_provider_url", lambda *a, **k: 0)
    with pytest.raises(
        ceremony.ReconciliationCeremonyError,
        match="pypi_metadata_artifact_mismatch",
    ):
        ceremony.fetch_providers(manifest)


def test_provider_fetch_rejects_insecure_and_unapproved_hosts() -> None:
    for url in (
        "http://files.pythonhosted.org/artifact.whl",
        "https://example.com/artifact.whl",
    ):
        with pytest.raises(
            ceremony.ReconciliationCeremonyError, match="provider_url_not_allowed"
        ):
            ceremony._fetch_provider_url(
                url,
                expected_sha256="00" * 32,
                expected_size=1,
                provider="pypi",
            )


def test_provider_redirect_handler_rejects_untrusted_target() -> None:
    handler = ceremony._ProviderRedirectHandler({"github.com"})

    class RequestFixture:
        full_url = "https://github.com/source"

    with pytest.raises(HTTPError, match="provider_redirect_forbidden"):
        handler.redirect_request(
            RequestFixture(),
            None,
            302,
            "redirect",
            {},
            "https://evil.example/artifact",
        )


def test_finalize_release_builds_valid_two_artifact_graph(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assertion, _path = _release_assertion(tmp_path, monkeypatch)
    validation = validate_release_assertion(assertion)
    assert validation["verified_attestation_count"] == 2
    assert assertion["software_release_node"]["version"] == "0.4.35"
    assert len(assertion["artifact_nodes"]) == 2
    assert {row["artifact_type"] for row in assertion["artifact_nodes"]} == {
        "wheel",
        "sdist",
    }
    assert all(row["package_version"] == "0.4.35" for row in assertion["artifact_nodes"])


def test_finalize_release_rejects_cross_release_envelope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    envelopes, envelope_path = _signed_envelopes(tmp_path, monkeypatch)
    envelopes["envelopes"][ceremony.EXPECTED_ARTIFACTS["wheel"]["artifact_id"]][
        "release_id"
    ] = "ilc-core-0.4.34"
    _write_json(envelope_path, envelopes)
    with pytest.raises(ValueError):
        ceremony.finalize_release(
            attestation_path=ATTESTATION,
            artifact_dir=ARTIFACT_DIR,
            envelope_set_path=envelope_path,
            provider_receipt_path=_provider_receipt(tmp_path),
        )


def test_release_native_envelope_preserves_assertion_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assertion, assertion_path = _release_assertion(tmp_path, monkeypatch)
    secret, public = keypair_from_ikm_hex("71" * 32)
    monkeypatch.setattr(ceremony, "GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX", public)
    secret_path = _write_secret(tmp_path / "submit.hex", secret)
    portable, receipt = ceremony.build_release_native_envelope(
        assertion_path=assertion_path, public_submit_secret_path=secret_path
    )
    assert portable["assertion_cid"] == assertion["assertion_cid"]
    envelope = portable["native_submit_envelope"]
    assert receipt["native_submit_node_id"] == node_id_from_submission(
        envelope, validate_truth_primitive_submission(envelope)
    )
    assert validate_release_assertion(portable)["full_release_graph_binding_verified"]


def test_bls_roles_reject_substitution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    secret, public = keypair_from_ikm_hex("72" * 32)
    _other_secret, other_public = keypair_from_ikm_hex("73" * 32)
    path = _write_secret(tmp_path / "role.hex", secret)
    with pytest.raises(
        ceremony.ReconciliationCeremonyError, match="authority_mismatch"
    ):
        ceremony._require_bls_secret(
            path, token="role_invalid", expected_public=other_public
        )
    monkeypatch.setattr(ceremony, "GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX", public)
    path.chmod(0o644)
    with pytest.raises(ceremony.ReconciliationCeremonyError, match="role_invalid"):
        ceremony._require_bls_secret(path, token="role_invalid", expected_public=public)


def test_prepare_policy_is_exact_sequence_3_successor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assertion, assertion_path = _release_assertion(tmp_path, monkeypatch)
    body, payload, receipt = ceremony.prepare_policy(
        assertion_path=assertion_path, prior_policy_view_path=PRIOR_VIEW
    )
    assert body["policy_sequence"] == 3
    assert body["previous_policy_claim_cid"] == ceremony.EXPECTED_SEQUENCE_2_CID
    assert body["selected_release_assertion_cid"] == assertion["assertion_cid"]
    assert body["selected_artifact_cids"] == sorted(
        assertion["software_release_node"]["artifact_cids"]
    )
    assert hashlib.sha256(payload).hexdigest() == receipt["payload_sha256"]


def test_prepare_policy_rejects_competing_or_substituted_head(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _assertion, assertion_path = _release_assertion(tmp_path, monkeypatch)
    prior = _json(PRIOR_VIEW)
    prior["authoritative_policy_head_cid"] = prior["policy_claims"][0]["claim_cid"]
    path = _write_json(tmp_path / "bad-prior.json", prior)
    with pytest.raises(
        ceremony.ReconciliationCeremonyError, match="sequence_2_policy_head_invalid"
    ):
        ceremony.prepare_policy(
            assertion_path=assertion_path, prior_policy_view_path=path
        )


def _finalized_policy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[dict, dict, Path, Path]:
    _assertion, assertion_path = _release_assertion(tmp_path, monkeypatch)
    body, payload, _request = ceremony.prepare_policy(
        assertion_path=assertion_path, prior_policy_view_path=PRIOR_VIEW
    )
    body_path = _write_json(tmp_path / "policy-body.json", body)
    payload_path = tmp_path / "payload.bin"
    payload_path.write_bytes(payload)

    policy_key = MLDSA65PrivateKey.generate()
    public_hex = policy_key.public_key().public_bytes_raw().hex()
    public_record = tmp_path / "policy-public.txt"
    public_record.write_text(f"mldsa_pk_hex: {public_hex}\n", encoding="ascii")
    signature_path = tmp_path / "signature.hex"
    signature_path.write_text(
        policy_key.sign(payload, ceremony.POLICY_MLDSA_SIGNING_CONTEXT).hex() + "\n",
        encoding="ascii",
    )
    monkeypatch.setattr(
        ceremony,
        "EXPECTED_POLICY_PUBLIC_KEY_SHA256",
        hashlib.sha256(bytes.fromhex(public_hex)).hexdigest(),
    )

    submit_secret, submit_public = keypair_from_ikm_hex("74" * 32)
    invite_secret, invite_public = keypair_from_ikm_hex("75" * 32)
    monkeypatch.setattr(ceremony, "GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX", submit_public)
    monkeypatch.setattr(ceremony, "GENESIS_INVITE_ISSUER_PK_HEX", invite_public)
    submit_path = _write_secret(tmp_path / "submit.hex", submit_secret)
    invite_path = _write_secret(tmp_path / "invite.hex", invite_secret)
    record, native, binding, receipt = ceremony.finalize_policy(
        policy_body_path=body_path,
        policy_payload_path=payload_path,
        policy_signature_path=signature_path,
        policy_public_key_record_path=public_record,
        prior_policy_view_path=PRIOR_VIEW,
        public_submit_secret_path=submit_path,
        invite_secret_path=invite_path,
    )
    assert receipt["policy_sequence"] == 3
    assert native["sig"]["key_ref"] == submit_public
    assert binding["shortcode_auth"]["inviting_bls_public_key_hex"] == invite_public
    return record, binding, public_record, assertion_path


def test_finalize_policy_separates_mldsa_and_bls_roles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record, binding, _public_record, _assertion = _finalized_policy(
        tmp_path, monkeypatch
    )
    assert record["payload"]["content"]["policy_body"]["policy_sequence"] == 3
    assert binding["current_policy_binding"]["policy_sequence"] == 3


def test_finalize_policy_rejects_signature_tampering(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _assertion, assertion_path = _release_assertion(tmp_path, monkeypatch)
    body, payload, _request = ceremony.prepare_policy(
        assertion_path=assertion_path, prior_policy_view_path=PRIOR_VIEW
    )
    body_path = _write_json(tmp_path / "body.json", body)
    payload_path = tmp_path / "payload.bin"
    payload_path.write_bytes(payload)
    key = MLDSA65PrivateKey.generate()
    public_hex = key.public_key().public_bytes_raw().hex()
    public_record = tmp_path / "public.txt"
    public_record.write_text(f"mldsa_pk_hex: {public_hex}\n", encoding="ascii")
    monkeypatch.setattr(
        ceremony,
        "EXPECTED_POLICY_PUBLIC_KEY_SHA256",
        hashlib.sha256(bytes.fromhex(public_hex)).hexdigest(),
    )
    signature = bytearray(key.sign(payload, ceremony.POLICY_MLDSA_SIGNING_CONTEXT))
    signature[0] ^= 1
    signature_path = tmp_path / "signature.hex"
    signature_path.write_text(signature.hex(), encoding="ascii")
    submit_secret, submit_public = keypair_from_ikm_hex("76" * 32)
    invite_secret, invite_public = keypair_from_ikm_hex("77" * 32)
    monkeypatch.setattr(ceremony, "GENESIS_PUBLIC_SUBMIT_INGRESS_BLS_PK_HEX", submit_public)
    monkeypatch.setattr(ceremony, "GENESIS_INVITE_ISSUER_PK_HEX", invite_public)
    with pytest.raises(
        ceremony.ReconciliationCeremonyError,
        match="policy_signature_verification_failed",
    ):
        ceremony.finalize_policy(
            policy_body_path=body_path,
            policy_payload_path=payload_path,
            policy_signature_path=signature_path,
            policy_public_key_record_path=public_record,
            prior_policy_view_path=PRIOR_VIEW,
            public_submit_secret_path=_write_secret(tmp_path / "submit.hex", submit_secret),
            invite_secret_path=_write_secret(tmp_path / "invite.hex", invite_secret),
        )


def test_verify_policy_view_resolves_complete_three_claim_chain(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    record, binding, public_record, assertion_path = _finalized_policy(
        tmp_path, monkeypatch
    )
    record_path = _write_json(tmp_path / "record.json", record)
    binding_path = _write_json(tmp_path / "binding.json", binding)
    public_hex = public_record.read_text(encoding="ascii").split(":", 1)[1].strip()
    monkeypatch.setattr(
        current_policy,
        "POLICY_PUBLIC_KEY_SHA256",
        hashlib.sha256(bytes.fromhex(public_hex)).hexdigest(),
    )
    monkeypatch.setattr(current_policy, "verify_mldsa65_signature", lambda *a, **k: True)
    from ilc_core.genesis import invite_issuer_authority

    monkeypatch.setattr(
        invite_issuer_authority,
        "GENESIS_INVITE_ISSUER_PK_HEX",
        ceremony.GENESIS_INVITE_ISSUER_PK_HEX,
    )
    view, receipt = ceremony.verify_policy_view(
        assertion_path=assertion_path,
        prior_policy_view_path=PRIOR_VIEW,
        policy_record_path=record_path,
        bootstrap_binding_path=binding_path,
        policy_public_key_record_path=public_record,
    )
    assert len(view["policy_claims"]) == 3
    assert receipt["status"] == "verified_current_policy"
    assert receipt["policy_sequence"] == 3


def test_tool_source_never_accepts_mldsa_secret_or_emits_secret_paths() -> None:
    source = Path("tools/reconciliation_v0435_sign_publish.py").read_text(
        encoding="utf-8"
    )
    assert "policy_seed" not in source
    assert "mldsa_secret" not in source
    assert "--policy-seed" not in source
    assert "policy_signature_path" in source
    receipt_fields = source[source.index('receipt = {', source.index("def sign_release")) :]
    receipt_fields = receipt_fields[: receipt_fields.index("return envelope_set")]
    assert '"release_key_path"' not in receipt_fields
