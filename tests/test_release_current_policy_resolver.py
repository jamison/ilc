# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import replace
import hashlib
import json

import pytest
from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey

from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.identity.bls_backend import keypair_from_ikm_hex
from ilc_core.network.relay.relay_server import attach_shortcode_invite_bundle_auth
from ilc_core.release import current_policy
from ilc_core.release.current_policy import (
    CurrentPolicyEvaluationInput,
    GraphCurrentPolicyResolver,
    PolicyClaimEvidence,
)
from ilc_core.release.upgrade_state import (
    advance_current_policy_high_water_mark,
    read_current_policy_high_water_mark,
)


_INVITE_SECRET_KEY_HEX, _INVITE_PUBLIC_KEY_HEX = keypair_from_ikm_hex("51" * 32)
_OTHER_INVITE_SECRET_KEY_HEX, _OTHER_INVITE_PUBLIC_KEY_HEX = keypair_from_ikm_hex(
    "52" * 32
)


def _cid(label: str) -> str:
    return node_id_from_obj({"fixture": label})


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _signed_binding_bundle(
    *,
    policy_head_cid: str,
    policy_sequence: int = 1,
    validation_epoch: int = 0,
    policy_id: str = current_policy.POLICY_ID,
    network_id: str = current_policy.POLICY_NETWORK_ID,
    channel: str = current_policy.POLICY_CHANNEL,
    secret_key_hex: str = _INVITE_SECRET_KEY_HEX,
    public_key_hex: str = _INVITE_PUBLIC_KEY_HEX,
) -> dict[str, object]:
    return attach_shortcode_invite_bundle_auth(
        {
            "current_policy_binding": {
                "channel": channel,
                "network_id": network_id,
                "policy_head_cid": policy_head_cid,
                "policy_id": policy_id,
                "policy_sequence": policy_sequence,
                "schema_version": current_policy.BOOTSTRAP_BINDING_SCHEMA_VERSION,
                "validation_epoch": validation_epoch,
            }
        },
        inviting_agent_id=public_key_hex,
        inviting_bls_public_key_hex=public_key_hex,
        inviting_bls_secret_key_hex=secret_key_hex,
    )


@pytest.fixture
def policy_key(monkeypatch: pytest.MonkeyPatch) -> MLDSA65PrivateKey:
    key = MLDSA65PrivateKey.generate()
    public_hex = key.public_key().public_bytes_raw().hex()
    monkeypatch.setattr(
        current_policy,
        "POLICY_PUBLIC_KEY_SHA256",
        hashlib.sha256(bytes.fromhex(public_hex)).hexdigest(),
    )
    monkeypatch.setattr(
        "ilc_core.genesis.invite_issuer_authority.GENESIS_INVITE_ISSUER_PK_HEX",
        _INVITE_PUBLIC_KEY_HEX,
    )
    return key


def _claim(
    key: MLDSA65PrivateKey,
    *,
    sequence: int = 1,
    previous: str | None = None,
    action: str = "select",
    assertion_cid: str | None = None,
    software_cid: str | None = None,
    artifact_cids: tuple[str, ...] | None = None,
    withdrawn: tuple[str, ...] = (),
    rejected: tuple[str, ...] = (),
    effective_epoch: int = 0,
    through_epoch: int = 0,
    max_lag: int = 0,
) -> PolicyClaimEvidence:
    assertion_cid = assertion_cid or _cid("release")
    software_cid = software_cid or _cid("software")
    artifact_cids = artifact_cids or (_cid("artifact"),)
    body = {
        "action": action,
        "authority_basis": "CDL-122",
        "channel": current_policy.POLICY_CHANNEL,
        "effective_validation_epoch": effective_epoch,
        "genesis_lineage_ref": current_policy.GENESIS_LINEAGE_REF,
        "max_observer_lag_epochs": max_lag,
        "network_id": current_policy.POLICY_NETWORK_ID,
        "policy_id": current_policy.POLICY_ID,
        "policy_sequence": sequence,
        "previous_policy_claim_cid": previous,
        "rejected_release_assertion_cids": sorted(rejected),
        "release_signer_profile": "ed25519_phase_1335",
        "release_signer_public_key_hex": current_policy.RELEASE_SIGNER_PUBLIC_KEY_HEX,
        "selected_artifact_cids": sorted(artifact_cids),
        "selected_release_assertion_cid": assertion_cid,
        "selected_software_release_cid": software_cid,
        "valid_through_validation_epoch": through_epoch,
        "withdrawn_release_assertion_cids": sorted(withdrawn),
    }
    preimage = (
        current_policy.POLICY_SIGNATURE_DOMAIN.encode("ascii")
        + b"\0"
        + _canonical(body)
    )
    content = {
        "policy_authorization": {
            "domain_separator": current_policy.POLICY_SIGNATURE_DOMAIN,
            "public_key_ref": current_policy.POLICY_PUBLIC_KEY_REF,
            "signature_hex": key.sign(
                preimage, current_policy.POLICY_MLDSA_SIGNING_CONTEXT
            ).hex(),
            "signature_scheme": current_policy.POLICY_SIGNATURE_SCHEME,
        },
        "policy_body": body,
        "schema_version": current_policy.POLICY_SCHEMA_VERSION,
    }
    record = {
        "agent_id": "a" * 96,
        "cdl_version": "cdl_075.v0.1",
        "epoch": 0,
        "payload": {
            "content": content,
            "epistemic_type": "normative",
            "parent_node_ids": [] if previous is None else [previous],
            "primitive_type": "knowledge_claim",
        },
        "primitive": "assert.truth",
        "primitive_type": "knowledge_claim",
    }
    return PolicyClaimEvidence(node_id_from_obj(record), _canonical(record))


def _request(
    key: MLDSA65PrivateKey,
    claims: tuple[PolicyClaimEvidence, ...] | None = None,
    **changes: object,
) -> CurrentPolicyEvaluationInput:
    assertion = _cid("release")
    software = _cid("software")
    artifacts = (_cid("artifact"),)
    claims = claims or (_claim(
        key, assertion_cid=assertion, software_cid=software, artifact_cids=artifacts
    ),)
    authoritative_head = str(changes.get("authoritative_policy_head_cid", claims[-1].claim_cid))
    authoritative_epoch = int(changes.get("authoritative_validation_epoch", 0))
    head_record = json.loads(next(
        claim.node_record_json
        for claim in claims
        if claim.claim_cid == authoritative_head
    ))
    try:
        policy_sequence = head_record["payload"]["content"]["policy_body"]["policy_sequence"]
    except (KeyError, TypeError):
        policy_sequence = 1
    binding_bundle = _signed_binding_bundle(
        policy_head_cid=authoritative_head,
        policy_sequence=policy_sequence,
        validation_epoch=authoritative_epoch,
    )
    values: dict[str, object] = {
        "release_assertion_cid": assertion,
        "software_release_cid": software,
        "artifact_cids": artifacts,
        "network_id": current_policy.POLICY_NETWORK_ID,
        "channel": current_policy.POLICY_CHANNEL,
        "policy_id": current_policy.POLICY_ID,
        "policy_public_key_hex": key.public_key().public_bytes_raw().hex(),
        "policy_claims": claims,
        "authoritative_policy_head_cid": authoritative_head,
        "authoritative_validation_epoch": authoritative_epoch,
        "observer_validation_epoch": 0,
        "observer_highest_seen_sequence": 0,
        "bootstrap_policy_head_cid": authoritative_head,
        "bootstrap_binding_evidence_cid": node_id_from_obj(binding_bundle),
        "bootstrap_binding_bundle_json": _canonical(binding_bundle),
    }
    values.update(changes)
    return CurrentPolicyEvaluationInput(**values)  # type: ignore[arg-type]


def test_valid_policy_view_is_verified(policy_key: MLDSA65PrivateKey) -> None:
    result = GraphCurrentPolicyResolver().resolve(_request(policy_key))
    assert result.status == "verified_current_policy"
    assert result.evidence_receipt["withdrawal_resolver_available"] is True


def test_production_entry_point_resolves_verified_policy(
    policy_key: MLDSA65PrivateKey,
) -> None:
    result = current_policy.resolve_current_policy(_request(policy_key))
    assert current_policy.CURRENT_POLICY_RESOLVER_NOT_ACTIVATED is False
    assert result.status == "verified_current_policy"
    assert result.reason == "verified_current_policy"


def test_production_entry_point_rejects_policy_rollback(
    policy_key: MLDSA65PrivateKey,
) -> None:
    result = current_policy.resolve_current_policy(
        _request(policy_key, observer_highest_seen_sequence=2)
    )
    assert result.status == "unresolved"
    assert result.reason == "policy_rollback_detected"


def test_permuted_chain_is_deterministic(policy_key: MLDSA65PrivateKey) -> None:
    first = _claim(policy_key, through_epoch=1, max_lag=1)
    second = _claim(
        policy_key, sequence=2, previous=first.claim_cid,
        effective_epoch=1, through_epoch=1, max_lag=0,
    )
    expected = _request(
        policy_key, (first, second), authoritative_validation_epoch=1,
        observer_validation_epoch=1, authoritative_policy_head_cid=second.claim_cid,
        bootstrap_policy_head_cid=second.claim_cid,
    )
    permuted = replace(expected, policy_claims=(second, first))
    assert GraphCurrentPolicyResolver().resolve(expected) == GraphCurrentPolicyResolver().resolve(permuted)


def test_competing_heads_are_unresolved(policy_key: MLDSA65PrivateKey) -> None:
    first = _claim(policy_key)
    left = _claim(policy_key, sequence=2, previous=first.claim_cid)
    right = _claim(
        policy_key, sequence=2, previous=first.claim_cid,
        software_cid=_cid("other-software"),
    )
    result = GraphCurrentPolicyResolver().resolve(
        _request(policy_key, (first, left, right), authoritative_policy_head_cid=left.claim_cid)
    )
    assert (result.status, result.reason) == ("unresolved", "unresolved_policy_head")


def test_missing_predecessor_is_unresolved(policy_key: MLDSA65PrivateKey) -> None:
    second = _claim(policy_key, sequence=2, previous=_cid("missing"))
    result = GraphCurrentPolicyResolver().resolve(_request(policy_key, (second,)))
    assert result.reason == "policy_predecessor_missing"


def test_rollback_is_unresolved(policy_key: MLDSA65PrivateKey) -> None:
    result = GraphCurrentPolicyResolver().resolve(
        _request(policy_key, observer_highest_seen_sequence=2)
    )
    assert result.reason == "policy_rollback_detected"


def test_stale_checkpoint_is_unresolved(policy_key: MLDSA65PrivateKey) -> None:
    result = GraphCurrentPolicyResolver().resolve(
        _request(policy_key, authoritative_validation_epoch=1, observer_validation_epoch=1)
    )
    assert result.reason == "policy_authoritative_checkpoint_stale"


def test_wrong_bootstrap_head_is_unresolved(policy_key: MLDSA65PrivateKey) -> None:
    result = GraphCurrentPolicyResolver().resolve(
        _request(policy_key, bootstrap_policy_head_cid=_cid("other-head"))
    )
    assert result.reason == "policy_bootstrap_binding_mismatch"


def test_unsigned_bootstrap_binding_is_unresolved(policy_key: MLDSA65PrivateKey) -> None:
    request = _request(policy_key)
    bundle = json.loads(request.bootstrap_binding_bundle_json)
    bundle.pop("shortcode_auth")
    result = GraphCurrentPolicyResolver().resolve(
        replace(
            request,
            bootstrap_binding_evidence_cid=node_id_from_obj(bundle),
            bootstrap_binding_bundle_json=_canonical(bundle),
        )
    )
    assert result.reason == "policy_bootstrap_binding_signature_invalid"


def test_bootstrap_binding_must_name_exact_head(policy_key: MLDSA65PrivateKey) -> None:
    request = _request(policy_key)
    bundle = _signed_binding_bundle(policy_head_cid=_cid("wrong-head"))
    result = GraphCurrentPolicyResolver().resolve(
        replace(
            request,
            bootstrap_binding_evidence_cid=node_id_from_obj(bundle),
            bootstrap_binding_bundle_json=_canonical(bundle),
        )
    )
    assert result.reason == "policy_bootstrap_binding_mismatch"


@pytest.mark.parametrize(
    ("binding_change", "value"),
    [
        ("policy_id", "wrong-policy"),
        ("network_id", "wrong-network"),
        ("channel", "wrong-channel"),
        ("policy_sequence", 2),
        ("validation_epoch", 1),
    ],
)
def test_bootstrap_binding_must_match_every_policy_axis(
    policy_key: MLDSA65PrivateKey,
    binding_change: str,
    value: object,
) -> None:
    request = _request(policy_key)
    changes = {binding_change: value}
    bundle = _signed_binding_bundle(
        policy_head_cid=request.authoritative_policy_head_cid,
        **changes,  # type: ignore[arg-type]
    )
    result = GraphCurrentPolicyResolver().resolve(
        replace(
            request,
            bootstrap_binding_evidence_cid=node_id_from_obj(bundle),
            bootstrap_binding_bundle_json=_canonical(bundle),
        )
    )
    assert result.reason == "policy_bootstrap_binding_mismatch"


def test_bootstrap_binding_cid_is_recomputed(policy_key: MLDSA65PrivateKey) -> None:
    request = _request(policy_key)
    result = GraphCurrentPolicyResolver().resolve(
        replace(request, bootstrap_binding_evidence_cid=_cid("wrong-binding-cid"))
    )
    assert result.reason == "policy_bootstrap_binding_cid_mismatch"


def test_bootstrap_binding_rejects_untrusted_invite_issuer(
    policy_key: MLDSA65PrivateKey,
) -> None:
    request = _request(policy_key)
    bundle = _signed_binding_bundle(
        policy_head_cid=request.authoritative_policy_head_cid,
        secret_key_hex=_OTHER_INVITE_SECRET_KEY_HEX,
        public_key_hex=_OTHER_INVITE_PUBLIC_KEY_HEX,
    )
    result = GraphCurrentPolicyResolver().resolve(
        replace(
            request,
            bootstrap_binding_evidence_cid=node_id_from_obj(bundle),
            bootstrap_binding_bundle_json=_canonical(bundle),
        )
    )
    assert result.reason == "policy_bootstrap_binding_signature_invalid"


def test_withdrawal_is_rejected(policy_key: MLDSA65PrivateKey) -> None:
    assertion = _cid("release")
    claim = _claim(
        policy_key, action="withdraw", assertion_cid=_cid("replacement-release"),
        withdrawn=(assertion,),
    )
    result = GraphCurrentPolicyResolver().resolve(_request(policy_key, (claim,)))
    assert (result.status, result.reason) == ("rejected_by_current_policy", "release_withdrawn")


@pytest.mark.parametrize(
    ("negative_field", "reason"),
    [
        ("withdrawn", "policy_withdrawal_history_removed"),
        ("rejected", "policy_rejection_history_removed"),
    ],
)
def test_successor_cannot_remove_append_only_negative_history(
    policy_key: MLDSA65PrivateKey,
    negative_field: str,
    reason: str,
) -> None:
    target = _cid("historically-negative-release")
    first = _claim(policy_key, **{negative_field: (target,)})
    second = _claim(policy_key, sequence=2, previous=first.claim_cid)
    request = _request(
        policy_key,
        (first, second),
        authoritative_policy_head_cid=second.claim_cid,
        bootstrap_policy_head_cid=second.claim_cid,
    )
    result = GraphCurrentPolicyResolver().resolve(request)
    assert (result.status, result.reason) == ("unresolved", reason)


def test_wrong_selected_artifact_is_rejected(policy_key: MLDSA65PrivateKey) -> None:
    claim = _claim(policy_key, artifact_cids=(_cid("different-artifact"),))
    result = GraphCurrentPolicyResolver().resolve(_request(policy_key, (claim,)))
    assert result.status == "rejected_by_current_policy"
    assert result.reason == "release_not_selected_by_policy_head"


def test_invalid_signature_is_unresolved(policy_key: MLDSA65PrivateKey) -> None:
    claim = _claim(policy_key)
    record = json.loads(claim.node_record_json)
    record["payload"]["content"]["policy_authorization"]["signature_hex"] = "00" * 3309
    broken = PolicyClaimEvidence(node_id_from_obj(record), _canonical(record))
    result = GraphCurrentPolicyResolver().resolve(_request(policy_key, (broken,)))
    assert result.reason == "policy_signature_invalid"


def test_wrong_policy_key_is_unresolved(
    policy_key: MLDSA65PrivateKey, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = _request(policy_key)
    other_key = MLDSA65PrivateKey.generate().public_key().public_bytes_raw().hex()
    monkeypatch.setattr(
        current_policy, "POLICY_PUBLIC_KEY_SHA256",
        hashlib.sha256(bytes.fromhex(other_key)).hexdigest(),
    )
    result = GraphCurrentPolicyResolver().resolve(
        replace(request, policy_public_key_hex=other_key)
    )
    assert result.reason == "policy_signature_invalid"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("network_id", "wrong-network"),
        ("channel", "wrong-channel"),
        ("policy_id", "wrong-policy"),
    ],
)
def test_wrong_request_scope_is_unresolved(
    policy_key: MLDSA65PrivateKey, field: str, value: str
) -> None:
    result = GraphCurrentPolicyResolver().resolve(
        _request(policy_key, **{field: value})
    )
    assert result.reason == "policy_request_scope_invalid"


def test_unknown_policy_body_field_is_unresolved(policy_key: MLDSA65PrivateKey) -> None:
    claim = _claim(policy_key)
    record = json.loads(claim.node_record_json)
    record["payload"]["content"]["policy_body"]["unknown"] = "forbidden"
    broken = PolicyClaimEvidence(node_id_from_obj(record), _canonical(record))
    result = GraphCurrentPolicyResolver().resolve(_request(policy_key, (broken,)))
    assert result.reason == "policy_body_fields_invalid"


def test_optional_native_submit_provenance_is_verified(
    policy_key: MLDSA65PrivateKey, monkeypatch: pytest.MonkeyPatch
) -> None:
    claim = _claim(policy_key)
    record = json.loads(claim.node_record_json)
    record["v"] = 1
    record["native_submit_sig"] = {"fixture": "signature"}
    monkeypatch.setattr(current_policy, "verify_native_submit_sig_envelope", lambda _: None)
    wrapped = PolicyClaimEvidence(node_id_from_obj(record), _canonical(record))
    request = _request(
        policy_key, (wrapped,), authoritative_policy_head_cid=wrapped.claim_cid,
        bootstrap_policy_head_cid=wrapped.claim_cid,
    )
    result = GraphCurrentPolicyResolver().resolve(request)
    assert result.status == "verified_current_policy"
    assert result.evidence_receipt["native_submit_provenance_verified_claims"] == 1


def test_duplicate_json_key_is_unresolved(policy_key: MLDSA65PrivateKey) -> None:
    claim = _claim(policy_key)
    raw = claim.node_record_json.replace(b'{"agent_id":', b'{"agent_id":"duplicate","agent_id":', 1)
    broken = PolicyClaimEvidence(claim.claim_cid, raw)
    result = GraphCurrentPolicyResolver().resolve(_request(policy_key, (broken,)))
    assert result.reason == "policy_json_duplicate_key"


def test_oversized_claim_is_unresolved(policy_key: MLDSA65PrivateKey) -> None:
    claim = _claim(policy_key)
    broken = PolicyClaimEvidence(claim.claim_cid, b"{" + b" " * current_policy.MAX_POLICY_CLAIM_BYTES + b"}")
    result = GraphCurrentPolicyResolver().resolve(_request(policy_key, (broken,)))
    assert result.reason == "policy_claim_size_invalid"


def test_malformed_request_types_fail_closed(policy_key: MLDSA65PrivateKey) -> None:
    request = replace(_request(policy_key), artifact_cids=(1,))  # type: ignore[arg-type]
    result = GraphCurrentPolicyResolver().resolve(request)
    assert (result.status, result.reason) == (
        "unresolved",
        "policy_request_artifact_cids_invalid",
    )


def test_malformed_public_key_type_fails_closed(policy_key: MLDSA65PrivateKey) -> None:
    request = replace(_request(policy_key), policy_public_key_hex=1)  # type: ignore[arg-type]
    result = GraphCurrentPolicyResolver().resolve(request)
    assert (result.status, result.reason) == (
        "unresolved",
        "policy_public_key_invalid",
    )


def test_non_request_object_fails_closed() -> None:
    result = GraphCurrentPolicyResolver().resolve(object())  # type: ignore[arg-type]
    assert (result.status, result.reason) == (
        "unresolved",
        "policy_evaluation_input_invalid",
    )


def test_high_water_mark_is_monotonic() -> None:
    scope = dict(policy_id="p", network_id="n", channel="c")
    state = advance_current_policy_high_water_mark({}, **scope, accepted_sequence=3)
    assert read_current_policy_high_water_mark(state, **scope) == 3
    with pytest.raises(ValueError, match="current_policy_sequence_rollback"):
        advance_current_policy_high_water_mark(state, **scope, accepted_sequence=2)


def test_resolver_source_has_no_io_primitives() -> None:
    source = __import__("inspect").getsource(current_policy)
    for forbidden in ("urllib", "requests", "socket", "Path(", "open(", "datetime.now"):
        assert forbidden not in source
