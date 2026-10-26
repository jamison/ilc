# SPDX-License-Identifier: AGPL-3.0-only
"""Pure CDL-122 release current-policy verification.

The resolver consumes an immutable, caller-supplied policy view.  It performs
no discovery, persistence, clock reads, or network I/O.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Any, Final, Mapping

from ilc_core.crypto.pq_signature_verify import verify_mldsa65_signature
from ilc_core.encoding.cidv1 import is_nodeid, node_id_from_obj
from ilc_core.epistemic.node_submission_runtime import EpistemicSubmissionError
from ilc_core.epistemic.truth_primitive_submission_runtime import (
    verify_native_submit_sig_envelope,
)


CURRENT_POLICY_RESOLVER_NOT_ACTIVATED = False

POLICY_SCHEMA_VERSION: Final[str] = "release_current_policy_claim.v0.1"
POLICY_ID: Final[str] = "ilc-public-rc-current-policy-v1"
POLICY_NETWORK_ID: Final[str] = "ilc-public-rc-01-testnet-harness"
POLICY_CHANNEL: Final[str] = "public_rc"
POLICY_SIGNATURE_DOMAIN: Final[str] = "ILC_RELEASE_CURRENT_POLICY_CLAIM_V1"
POLICY_SIGNATURE_SCHEME: Final[str] = "mldsa65_genesis_agent1_838a"
POLICY_MLDSA_SIGNING_CONTEXT: Final[bytes] = b"ILC_GENESIS_ROOT_ENVELOPE_V1"
POLICY_PUBLIC_KEY_REF: Final[str] = "docs/genesis/genesis_agent1_pubkey_record_838a.txt"
POLICY_PUBLIC_KEY_SHA256: Final[str] = (
    "228a9d27ef0fa1dcb0607ca06a157733ff3f3a821304687670af9b0775deefd8"
)
RELEASE_SIGNER_PUBLIC_KEY_HEX: Final[str] = (
    "5bf71c1e0ac93f2d7414b0dc315161fc4a57462c198ba1618e2890ec89a5b15a"
)
GENESIS_LINEAGE_REF: Final[str] = "artifact:genesis_agent1_pubkey_record_838a"

MAX_POLICY_CLAIMS = 64
MAX_POLICY_CLAIM_BYTES = 131_072
MAX_POLICY_VIEW_BYTES = 1_048_576
MAX_BOOTSTRAP_BINDING_BYTES = 32_768
MAX_JSON_DEPTH = 16
MAX_JSON_NODES = 20_000
MAX_STRING_BYTES = 16_384
MAX_LIST_ITEMS = 256
MAX_MAP_ITEMS = 128
MAX_EPOCH = 2**63 - 1
_LOWER_HEX_RE = re.compile(r"^[0-9a-f]+$")

_NODE_REQUIRED = {
    "agent_id", "cdl_version", "epoch", "payload", "primitive", "primitive_type"
}
_NODE_OPTIONAL = {"v", "native_submit_sig"}
_PAYLOAD_FIELDS = {"content", "epistemic_type", "parent_node_ids", "primitive_type"}
_CONTENT_FIELDS = {"schema_version", "policy_body", "policy_authorization"}
_BODY_FIELDS = {
    "policy_id", "network_id", "channel", "policy_sequence",
    "previous_policy_claim_cid", "action", "selected_release_assertion_cid",
    "selected_software_release_cid", "selected_artifact_cids",
    "withdrawn_release_assertion_cids", "rejected_release_assertion_cids",
    "effective_validation_epoch", "valid_through_validation_epoch",
    "max_observer_lag_epochs", "release_signer_profile",
    "release_signer_public_key_hex", "genesis_lineage_ref", "authority_basis",
}
_AUTH_FIELDS = {
    "signature_scheme", "domain_separator", "public_key_ref", "signature_hex"
}
_BOOTSTRAP_BINDING_FIELDS = {
    "schema_version", "policy_id", "network_id", "channel", "policy_head_cid",
    "policy_sequence", "validation_epoch",
}
BOOTSTRAP_BINDING_SCHEMA_VERSION: Final[str] = (
    "release_current_policy_bootstrap_binding.v0.1"
)


@dataclass(frozen=True)
class PolicyClaimEvidence:
    claim_cid: str
    node_record_json: bytes

    def __post_init__(self) -> None:
        if not isinstance(self.claim_cid, str):
            raise TypeError("policy_claim_cid_not_string")
        if not isinstance(self.node_record_json, bytes):
            raise TypeError("policy_claim_json_not_bytes")


@dataclass(frozen=True)
class CurrentPolicyEvaluationInput:
    release_assertion_cid: str
    software_release_cid: str
    artifact_cids: tuple[str, ...]
    network_id: str
    channel: str
    policy_id: str
    policy_public_key_hex: str
    policy_claims: tuple[PolicyClaimEvidence, ...]
    authoritative_policy_head_cid: str
    authoritative_validation_epoch: int
    observer_validation_epoch: int
    observer_highest_seen_sequence: int
    bootstrap_policy_head_cid: str
    bootstrap_binding_evidence_cid: str
    bootstrap_binding_bundle_json: bytes


@dataclass(frozen=True)
class CurrentPolicyResult:
    status: str
    reason: str
    evidence_receipt: Mapping[str, Any]


class CurrentPolicyEvidenceError(ValueError):
    """Expected hostile or incomplete policy evidence."""

    def __init__(self, token: str) -> None:
        super().__init__(token)
        self.token = token


@dataclass(frozen=True)
class _ValidatedClaim:
    cid: str
    body: Mapping[str, Any]
    native_submit_verified: bool


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CurrentPolicyEvidenceError("policy_json_duplicate_key")
        result[key] = value
    return result


def _reject_constant(_: str) -> None:
    raise CurrentPolicyEvidenceError("policy_json_non_finite_number")


def _walk_json(value: Any, *, depth: int = 0, counter: list[int] | None = None) -> None:
    if counter is None:
        counter = [0]
    counter[0] += 1
    if counter[0] > MAX_JSON_NODES or depth > MAX_JSON_DEPTH:
        raise CurrentPolicyEvidenceError("policy_json_structure_limit")
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if value < -(2**63) or value > MAX_EPOCH:
            raise CurrentPolicyEvidenceError("policy_json_integer_out_of_range")
        return
    if isinstance(value, float):
        raise CurrentPolicyEvidenceError("policy_json_float_forbidden")
    if isinstance(value, str):
        if len(value.encode("utf-8")) > MAX_STRING_BYTES:
            raise CurrentPolicyEvidenceError("policy_json_string_too_large")
        return
    if isinstance(value, list):
        if len(value) > MAX_LIST_ITEMS:
            raise CurrentPolicyEvidenceError("policy_json_list_too_large")
        for item in value:
            _walk_json(item, depth=depth + 1, counter=counter)
        return
    if isinstance(value, dict):
        if len(value) > MAX_MAP_ITEMS:
            raise CurrentPolicyEvidenceError("policy_json_map_too_large")
        for key, item in value.items():
            if not isinstance(key, str):
                raise CurrentPolicyEvidenceError("policy_json_key_invalid")
            _walk_json(key, depth=depth + 1, counter=counter)
            _walk_json(item, depth=depth + 1, counter=counter)
        return
    raise CurrentPolicyEvidenceError("policy_json_type_forbidden")


def _decode_record(raw: bytes) -> dict[str, Any]:
    if not raw or len(raw) > MAX_POLICY_CLAIM_BYTES:
        raise CurrentPolicyEvidenceError("policy_claim_size_invalid")
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CurrentPolicyEvidenceError("policy_claim_json_invalid") from exc
    _walk_json(value)
    if not isinstance(value, dict):
        raise CurrentPolicyEvidenceError("policy_claim_not_object")
    return value


def _decode_bootstrap_binding_bundle(raw: bytes) -> dict[str, Any]:
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_BOOTSTRAP_BINDING_BYTES:
        raise CurrentPolicyEvidenceError("policy_bootstrap_binding_size_invalid")
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CurrentPolicyEvidenceError("policy_bootstrap_binding_json_invalid") from exc
    _walk_json(value)
    if not isinstance(value, dict):
        raise CurrentPolicyEvidenceError("policy_bootstrap_binding_not_object")
    return value


def _exact(value: Mapping[str, Any], expected: set[str], token: str) -> None:
    if set(value) != expected:
        raise CurrentPolicyEvidenceError(token)


def _uint(value: Any, token: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= MAX_EPOCH:
        raise CurrentPolicyEvidenceError(token)
    return value


def _cid(value: Any, token: str) -> str:
    if not isinstance(value, str) or not is_nodeid(value):
        raise CurrentPolicyEvidenceError(token)
    return value


def _cid_list(value: Any, token: str, *, allow_empty: bool) -> tuple[str, ...]:
    if not isinstance(value, list) or len(value) > MAX_LIST_ITEMS or (not value and not allow_empty):
        raise CurrentPolicyEvidenceError(token)
    result = tuple(_cid(item, token) for item in value)
    if len(set(result)) != len(result) or list(result) != sorted(result):
        raise CurrentPolicyEvidenceError(token)
    return result


def _canonical_body(body: Mapping[str, Any]) -> bytes:
    return json.dumps(
        dict(body), sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _validate_claim(evidence: PolicyClaimEvidence, public_key_hex: str) -> _ValidatedClaim:
    record = _decode_record(evidence.node_record_json)
    _exact(record, _NODE_REQUIRED | (set(record) & _NODE_OPTIONAL), "policy_node_fields_invalid")
    if set(record) - (_NODE_REQUIRED | _NODE_OPTIONAL):
        raise CurrentPolicyEvidenceError("policy_node_fields_invalid")
    if node_id_from_obj(record) != evidence.claim_cid:
        raise CurrentPolicyEvidenceError("policy_claim_cid_mismatch")
    if (
        record.get("primitive") != "assert.truth"
        or record.get("primitive_type") != "knowledge_claim"
        or record.get("cdl_version") != "cdl_075.v0.1"
    ):
        raise CurrentPolicyEvidenceError("policy_carrier_invalid")
    _uint(record.get("epoch"), "policy_node_epoch_invalid")
    agent_id = record.get("agent_id")
    if not isinstance(agent_id, str) or len(agent_id) != 96 or not _LOWER_HEX_RE.fullmatch(agent_id):
        raise CurrentPolicyEvidenceError("policy_node_agent_id_invalid")
    payload = record.get("payload")
    if not isinstance(payload, dict):
        raise CurrentPolicyEvidenceError("policy_payload_invalid")
    _exact(payload, _PAYLOAD_FIELDS, "policy_payload_fields_invalid")
    if payload.get("primitive_type") != "knowledge_claim" or payload.get("epistemic_type") != "normative":
        raise CurrentPolicyEvidenceError("policy_payload_type_invalid")
    parents = payload.get("parent_node_ids")
    if not isinstance(parents, list) or any(not isinstance(item, str) for item in parents):
        raise CurrentPolicyEvidenceError("policy_parent_ids_invalid")
    content = payload.get("content")
    if not isinstance(content, dict):
        raise CurrentPolicyEvidenceError("policy_content_invalid")
    _exact(content, _CONTENT_FIELDS, "policy_content_fields_invalid")
    if content.get("schema_version") != POLICY_SCHEMA_VERSION:
        raise CurrentPolicyEvidenceError("policy_schema_version_invalid")
    body = content.get("policy_body")
    auth = content.get("policy_authorization")
    if not isinstance(body, dict) or not isinstance(auth, dict):
        raise CurrentPolicyEvidenceError("policy_content_invalid")
    _exact(body, _BODY_FIELDS, "policy_body_fields_invalid")
    _exact(auth, _AUTH_FIELDS, "policy_authorization_fields_invalid")
    if (
        auth.get("signature_scheme") != POLICY_SIGNATURE_SCHEME
        or auth.get("domain_separator") != POLICY_SIGNATURE_DOMAIN
        or auth.get("public_key_ref") != POLICY_PUBLIC_KEY_REF
    ):
        raise CurrentPolicyEvidenceError("policy_authorization_profile_invalid")
    signature_hex = auth.get("signature_hex")
    if not isinstance(signature_hex, str):
        raise CurrentPolicyEvidenceError("policy_signature_invalid")
    preimage = POLICY_SIGNATURE_DOMAIN.encode("ascii") + b"\0" + _canonical_body(body)
    if not verify_mldsa65_signature(
        preimage,
        signature_hex,
        public_key_hex,
        context=POLICY_MLDSA_SIGNING_CONTEXT,
    ):
        raise CurrentPolicyEvidenceError("policy_signature_invalid")

    if body.get("policy_id") != POLICY_ID or body.get("authority_basis") != "CDL-122":
        raise CurrentPolicyEvidenceError("policy_authority_scope_invalid")
    if body.get("network_id") != POLICY_NETWORK_ID or body.get("channel") != POLICY_CHANNEL:
        raise CurrentPolicyEvidenceError("policy_scope_invalid")
    if body.get("release_signer_profile") != "ed25519_phase_1335":
        raise CurrentPolicyEvidenceError("policy_release_signer_profile_invalid")
    if body.get("release_signer_public_key_hex") != RELEASE_SIGNER_PUBLIC_KEY_HEX:
        raise CurrentPolicyEvidenceError("policy_release_signer_key_invalid")
    if body.get("genesis_lineage_ref") != GENESIS_LINEAGE_REF:
        raise CurrentPolicyEvidenceError("policy_genesis_lineage_invalid")
    sequence = _uint(body.get("policy_sequence"), "policy_sequence_invalid", minimum=1)
    previous = body.get("previous_policy_claim_cid")
    if previous is not None:
        _cid(previous, "policy_previous_cid_invalid")
    if (sequence == 1) != (previous is None):
        raise CurrentPolicyEvidenceError("policy_predecessor_boundary_invalid")
    expected_parents = [] if previous is None else [previous]
    if parents != expected_parents:
        raise CurrentPolicyEvidenceError("policy_parent_predecessor_mismatch")
    if body.get("action") not in {"select", "withdraw", "reject"}:
        raise CurrentPolicyEvidenceError("policy_action_invalid")
    selected_assertion = _cid(body.get("selected_release_assertion_cid"), "policy_release_cid_invalid")
    _cid(body.get("selected_software_release_cid"), "policy_software_cid_invalid")
    selected_artifacts = _cid_list(body.get("selected_artifact_cids"), "policy_artifact_cids_invalid", allow_empty=False)
    withdrawn = _cid_list(body.get("withdrawn_release_assertion_cids"), "policy_withdrawn_cids_invalid", allow_empty=True)
    rejected = _cid_list(body.get("rejected_release_assertion_cids"), "policy_rejected_cids_invalid", allow_empty=True)
    if selected_assertion in withdrawn or selected_assertion in rejected or set(withdrawn) & set(rejected):
        raise CurrentPolicyEvidenceError("policy_selection_negative_conflict")
    effective = _uint(body.get("effective_validation_epoch"), "policy_effective_epoch_invalid")
    through = _uint(body.get("valid_through_validation_epoch"), "policy_valid_through_epoch_invalid")
    _uint(body.get("max_observer_lag_epochs"), "policy_max_lag_invalid")
    if effective > through:
        raise CurrentPolicyEvidenceError("policy_epoch_range_invalid")

    native_verified = False
    native_sig = record.get("native_submit_sig")
    if native_sig is not None:
        if record.get("v") != 1:
            raise CurrentPolicyEvidenceError("policy_native_submit_version_invalid")
        envelope = {
            "v": 1, "primitive": record["primitive"], "agent_id": record["agent_id"],
            "epoch": record["epoch"], "payload": record["payload"], "sig": native_sig,
        }
        try:
            verify_native_submit_sig_envelope(envelope)
        except EpistemicSubmissionError as exc:
            raise CurrentPolicyEvidenceError("policy_native_submit_signature_invalid") from exc
        native_verified = True
    return _ValidatedClaim(evidence.claim_cid, body, native_verified)


def _base_receipt(request: CurrentPolicyEvaluationInput, reason: str) -> dict[str, Any]:
    return {
        "policy_ref": request.authoritative_policy_head_cid,
        "policy_version": POLICY_SCHEMA_VERSION,
        "policy_id": request.policy_id,
        "network_id": request.network_id,
        "channel": request.channel,
        "release_assertion_cid": request.release_assertion_cid,
        "software_release_cid": request.software_release_cid,
        "artifact_cids": list(request.artifact_cids),
        "authoritative_epoch_or_snapshot": f"validation_epoch:{request.authoritative_validation_epoch}",
        "observer_validation_epoch": request.observer_validation_epoch,
        "eligibility_evidence_refs": [],
        "freshness_rule": "authenticated_validation_epoch_max_lag",
        "evaluated_at": f"validation_epoch:{request.observer_validation_epoch}",
        "withdrawal_resolver_available": False,
        "reason": reason,
    }


def _verify_bootstrap_binding(
    request: CurrentPolicyEvaluationInput,
    *,
    policy_head_cid: str,
    policy_sequence: int,
) -> str:
    from ilc_core.genesis.invite_issuer_authority import GENESIS_INVITE_ISSUER_PK_HEX
    from ilc_core.network.relay.relay_server import verify_shortcode_invite_bundle

    bundle = _decode_bootstrap_binding_bundle(request.bootstrap_binding_bundle_json)
    if not verify_shortcode_invite_bundle(
        bundle,
        inviting_agent_id=GENESIS_INVITE_ISSUER_PK_HEX,
        inviting_bls_public_key_hex=GENESIS_INVITE_ISSUER_PK_HEX,
    ):
        raise CurrentPolicyEvidenceError("policy_bootstrap_binding_signature_invalid")
    binding = bundle.get("current_policy_binding")
    if not isinstance(binding, dict):
        raise CurrentPolicyEvidenceError("policy_bootstrap_binding_missing")
    _exact(binding, _BOOTSTRAP_BINDING_FIELDS, "policy_bootstrap_binding_fields_invalid")
    if (
        binding.get("schema_version") != BOOTSTRAP_BINDING_SCHEMA_VERSION
        or binding.get("policy_id") != request.policy_id
        or binding.get("network_id") != request.network_id
        or binding.get("channel") != request.channel
        or binding.get("policy_head_cid") != policy_head_cid
        or _uint(binding.get("policy_sequence"), "policy_bootstrap_binding_sequence_invalid", minimum=1)
        != policy_sequence
        or _uint(binding.get("validation_epoch"), "policy_bootstrap_binding_epoch_invalid")
        != request.authoritative_validation_epoch
    ):
        raise CurrentPolicyEvidenceError("policy_bootstrap_binding_mismatch")
    evidence_cid = node_id_from_obj(bundle)
    if evidence_cid != request.bootstrap_binding_evidence_cid:
        raise CurrentPolicyEvidenceError("policy_bootstrap_binding_cid_mismatch")
    return evidence_cid


class GraphCurrentPolicyResolver:
    """Deterministically evaluate one immutable policy view."""

    def resolve(self, request: CurrentPolicyEvaluationInput) -> CurrentPolicyResult:
        if not isinstance(request, CurrentPolicyEvaluationInput):
            return CurrentPolicyResult(
                "unresolved",
                "policy_evaluation_input_invalid",
                {"reason": "policy_evaluation_input_invalid"},
            )
        if type(request.artifact_cids) is not tuple or type(request.policy_claims) is not tuple:
            return CurrentPolicyResult(
                "unresolved",
                "policy_evaluation_input_not_immutable",
                {"reason": "policy_evaluation_input_not_immutable"},
            )
        receipt = _base_receipt(request, "policy_evidence_not_evaluated")
        try:
            return self._resolve(request, receipt)
        except CurrentPolicyEvidenceError as exc:
            receipt["reason"] = exc.token
            return CurrentPolicyResult("unresolved", exc.token, receipt)

    def _resolve(
        self, request: CurrentPolicyEvaluationInput, receipt: dict[str, Any]
    ) -> CurrentPolicyResult:
        if any(type(item) is not PolicyClaimEvidence for item in request.policy_claims):
            raise CurrentPolicyEvidenceError("policy_claim_evidence_type_invalid")
        for value, token in (
            (request.release_assertion_cid, "policy_request_release_cid_invalid"),
            (request.software_release_cid, "policy_request_software_cid_invalid"),
            (request.authoritative_policy_head_cid, "policy_head_cid_invalid"),
            (request.bootstrap_policy_head_cid, "policy_bootstrap_head_cid_invalid"),
            (request.bootstrap_binding_evidence_cid, "policy_bootstrap_binding_cid_invalid"),
        ):
            _cid(value, token)
        if (
            not request.artifact_cids
            or any(not isinstance(cid, str) for cid in request.artifact_cids)
            or tuple(sorted(request.artifact_cids)) != request.artifact_cids
        ):
            raise CurrentPolicyEvidenceError("policy_request_artifact_cids_invalid")
        if len(set(request.artifact_cids)) != len(request.artifact_cids):
            raise CurrentPolicyEvidenceError("policy_request_artifact_cids_invalid")
        for cid in request.artifact_cids:
            _cid(cid, "policy_request_artifact_cids_invalid")
        if (
            request.policy_id != POLICY_ID or request.network_id != POLICY_NETWORK_ID
            or request.channel != POLICY_CHANNEL
        ):
            raise CurrentPolicyEvidenceError("policy_request_scope_invalid")
        for epoch, token in (
            (request.authoritative_validation_epoch, "policy_authoritative_epoch_invalid"),
            (request.observer_validation_epoch, "policy_observer_epoch_invalid"),
            (request.observer_highest_seen_sequence, "policy_highest_seen_invalid"),
        ):
            _uint(epoch, token)
        if request.observer_validation_epoch > request.authoritative_validation_epoch:
            raise CurrentPolicyEvidenceError("policy_observer_checkpoint_ahead")
        if (
            len(request.policy_claims) == 0 or len(request.policy_claims) > MAX_POLICY_CLAIMS
            or sum(len(item.node_record_json) for item in request.policy_claims) > MAX_POLICY_VIEW_BYTES
        ):
            raise CurrentPolicyEvidenceError("policy_claim_view_size_invalid")
        if (
            not isinstance(request.policy_public_key_hex, str)
            or len(request.policy_public_key_hex) != 3904
            or not _LOWER_HEX_RE.fullmatch(request.policy_public_key_hex)
        ):
            raise CurrentPolicyEvidenceError("policy_public_key_invalid")
        if hashlib.sha256(bytes.fromhex(request.policy_public_key_hex)).hexdigest() != POLICY_PUBLIC_KEY_SHA256:
            raise CurrentPolicyEvidenceError("policy_public_key_untrusted")

        claims = [_validate_claim(item, request.policy_public_key_hex) for item in request.policy_claims]
        by_cid = {claim.cid: claim for claim in claims}
        if len(by_cid) != len(claims):
            raise CurrentPolicyEvidenceError("policy_claim_duplicate")
        referenced = {claim.body["previous_policy_claim_cid"] for claim in claims if claim.body["previous_policy_claim_cid"]}
        heads = sorted(set(by_cid) - referenced)
        if len(heads) != 1 or heads[0] != request.authoritative_policy_head_cid:
            raise CurrentPolicyEvidenceError("unresolved_policy_head")
        head = by_cid[heads[0]]
        chain: list[_ValidatedClaim] = []
        seen: set[str] = set()
        cursor = head
        while True:
            if cursor.cid in seen:
                raise CurrentPolicyEvidenceError("policy_predecessor_cycle")
            seen.add(cursor.cid)
            chain.append(cursor)
            previous = cursor.body["previous_policy_claim_cid"]
            if previous is None:
                break
            predecessor = by_cid.get(previous)
            if predecessor is None:
                raise CurrentPolicyEvidenceError("policy_predecessor_missing")
            if predecessor.body["policy_sequence"] + 1 != cursor.body["policy_sequence"]:
                raise CurrentPolicyEvidenceError("policy_sequence_gap")
            if not set(predecessor.body["withdrawn_release_assertion_cids"]).issubset(
                cursor.body["withdrawn_release_assertion_cids"]
            ):
                raise CurrentPolicyEvidenceError("policy_withdrawal_history_removed")
            if not set(predecessor.body["rejected_release_assertion_cids"]).issubset(
                cursor.body["rejected_release_assertion_cids"]
            ):
                raise CurrentPolicyEvidenceError("policy_rejection_history_removed")
            cursor = predecessor
        if len(chain) != len(claims) or chain[-1].body["policy_sequence"] != 1:
            raise CurrentPolicyEvidenceError("unresolved_policy_head")
        sequence = head.body["policy_sequence"]
        if sequence < request.observer_highest_seen_sequence:
            raise CurrentPolicyEvidenceError("policy_rollback_detected")
        authoritative = request.authoritative_validation_epoch
        observer = request.observer_validation_epoch
        if not head.body["effective_validation_epoch"] <= authoritative <= head.body["valid_through_validation_epoch"]:
            raise CurrentPolicyEvidenceError("policy_authoritative_checkpoint_stale")
        if authoritative - observer > head.body["max_observer_lag_epochs"]:
            raise CurrentPolicyEvidenceError("policy_observer_lag_exceeded")
        if authoritative == 0:
            if head.body["max_observer_lag_epochs"] != 0 or request.bootstrap_policy_head_cid != head.cid:
                raise CurrentPolicyEvidenceError("policy_bootstrap_binding_mismatch")
        binding_evidence_cid = _verify_bootstrap_binding(
            request,
            policy_head_cid=head.cid,
            policy_sequence=sequence,
        )

        receipt.update(
            {
                "policy_sequence": sequence,
                "eligibility_evidence_refs": [item.cid for item in reversed(chain)]
                + [binding_evidence_cid],
                "withdrawal_resolver_available": True,
                "native_submit_provenance_verified_claims": sum(
                    1 for item in chain if item.native_submit_verified
                ),
            }
        )
        target = request.release_assertion_cid
        withdrawn = set(head.body["withdrawn_release_assertion_cids"])
        rejected = set(head.body["rejected_release_assertion_cids"])
        if target in withdrawn or target in rejected:
            reason = "release_withdrawn" if target in withdrawn else "release_rejected"
            receipt["reason"] = reason
            return CurrentPolicyResult("rejected_by_current_policy", reason, receipt)
        exact_selection = (
            head.body["action"] == "select"
            and head.body["selected_release_assertion_cid"] == target
            and head.body["selected_software_release_cid"] == request.software_release_cid
            and tuple(head.body["selected_artifact_cids"]) == request.artifact_cids
        )
        if not exact_selection:
            receipt["reason"] = "release_not_selected_by_policy_head"
            return CurrentPolicyResult(
                "rejected_by_current_policy", "release_not_selected_by_policy_head", receipt
            )
        receipt["reason"] = "verified_current_policy"
        return CurrentPolicyResult("verified_current_policy", "verified_current_policy", receipt)


def resolve_current_policy(request: CurrentPolicyEvaluationInput) -> CurrentPolicyResult:
    """Production entry point, fail-closed until the publication phase activates it."""

    if CURRENT_POLICY_RESOLVER_NOT_ACTIVATED:
        receipt = _base_receipt(request, "current_policy_resolver_not_activated")
        return CurrentPolicyResult("unresolved", "current_policy_resolver_not_activated", receipt)
    return GraphCurrentPolicyResolver().resolve(request)


__all__ = [
    "CURRENT_POLICY_RESOLVER_NOT_ACTIVATED",
    "BOOTSTRAP_BINDING_SCHEMA_VERSION",
    "POLICY_MLDSA_SIGNING_CONTEXT",
    "CurrentPolicyEvaluationInput",
    "CurrentPolicyResult",
    "GraphCurrentPolicyResolver",
    "PolicyClaimEvidence",
    "resolve_current_policy",
]
