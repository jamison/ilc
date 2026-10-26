# SPDX-License-Identifier: AGPL-3.0-only
"""Bounded loading for portable release current-policy evidence views."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ilc_core.release.current_policy import CurrentPolicyEvaluationInput, PolicyClaimEvidence


POLICY_VIEW_SCHEMA_VERSION = "release_current_policy_view.v0.1"
MAX_POLICY_VIEW_FILE_BYTES = 1_048_576
MAX_POLICY_VIEW_DEPTH = 18
MAX_POLICY_VIEW_NODES = 24_000
MAX_POLICY_VIEW_STRING_BYTES = 16_384
MAX_POLICY_VIEW_LIST_ITEMS = 256
MAX_POLICY_VIEW_MAP_ITEMS = 128
MAX_POLICY_VIEW_INTEGER = 2**63 - 1

_ROOT_FIELDS = {
    "schema_version",
    "release_assertion_cid",
    "software_release_cid",
    "artifact_cids",
    "network_id",
    "channel",
    "policy_id",
    "policy_public_key_hex",
    "policy_claims",
    "authoritative_policy_head_cid",
    "authoritative_validation_epoch",
    "observer_validation_epoch",
    "bootstrap_policy_head_cid",
    "bootstrap_binding_evidence_cid",
    "bootstrap_binding_bundle",
}
_CLAIM_FIELDS = {"claim_cid", "node_record"}


class CurrentPolicyViewError(ValueError):
    """Stable-token error for malformed or unavailable policy-view bytes."""

    def __init__(self, token: str) -> None:
        super().__init__(token)
        self.token = token


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CurrentPolicyViewError("current_policy_view_duplicate_key")
        result[key] = value
    return result


def _reject_number(_: str) -> None:
    raise CurrentPolicyViewError("current_policy_view_number_invalid")


def _walk(value: Any, *, depth: int = 0, counter: list[int] | None = None) -> None:
    if counter is None:
        counter = [0]
    counter[0] += 1
    if counter[0] > MAX_POLICY_VIEW_NODES or depth > MAX_POLICY_VIEW_DEPTH:
        raise CurrentPolicyViewError("current_policy_view_bounds_exceeded")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if abs(value) > MAX_POLICY_VIEW_INTEGER:
            raise CurrentPolicyViewError("current_policy_view_integer_invalid")
        return
    if type(value) is str:
        if len(value.encode("utf-8")) > MAX_POLICY_VIEW_STRING_BYTES:
            raise CurrentPolicyViewError("current_policy_view_string_too_large")
        return
    if type(value) is list:
        if len(value) > MAX_POLICY_VIEW_LIST_ITEMS:
            raise CurrentPolicyViewError("current_policy_view_list_too_large")
        for item in value:
            _walk(item, depth=depth + 1, counter=counter)
        return
    if type(value) is dict:
        if len(value) > MAX_POLICY_VIEW_MAP_ITEMS:
            raise CurrentPolicyViewError("current_policy_view_map_too_large")
        for key, item in value.items():
            if type(key) is not str:
                raise CurrentPolicyViewError("current_policy_view_key_invalid")
            _walk(key, depth=depth + 1, counter=counter)
            _walk(item, depth=depth + 1, counter=counter)
        return
    raise CurrentPolicyViewError("current_policy_view_value_type_invalid")


def _decode(raw: bytes) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_float=_reject_number,
            parse_constant=_reject_number,
        )
    except CurrentPolicyViewError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CurrentPolicyViewError("current_policy_view_json_invalid") from exc
    _walk(value)
    if type(value) is not dict:
        raise CurrentPolicyViewError("current_policy_view_root_invalid")
    if set(value) != _ROOT_FIELDS:
        raise CurrentPolicyViewError("current_policy_view_fields_invalid")
    if value.get("schema_version") != POLICY_VIEW_SCHEMA_VERSION:
        raise CurrentPolicyViewError("current_policy_view_schema_invalid")
    return value


def _string(value: Any, token: str) -> str:
    if type(value) is not str or not value:
        raise CurrentPolicyViewError(token)
    return value


def _uint(value: Any, token: str) -> int:
    if type(value) is not int or value < 0 or value > MAX_POLICY_VIEW_INTEGER:
        raise CurrentPolicyViewError(token)
    return value


def _canonical_json_bytes(value: dict[str, Any]) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise CurrentPolicyViewError("current_policy_view_nested_json_invalid") from exc


def load_current_policy_evaluation_input(
    path: Path,
    *,
    observer_highest_seen_sequence: int,
) -> CurrentPolicyEvaluationInput:
    """Load untrusted local bytes into the concrete immutable resolver input."""

    highest_seen = _uint(
        observer_highest_seen_sequence,
        "current_policy_view_highest_seen_invalid",
    )
    try:
        with path.expanduser().open("rb") as handle:
            raw = handle.read(MAX_POLICY_VIEW_FILE_BYTES + 1)
    except OSError as exc:
        raise CurrentPolicyViewError("current_policy_view_unavailable") from exc
    if len(raw) > MAX_POLICY_VIEW_FILE_BYTES:
        raise CurrentPolicyViewError("current_policy_view_too_large")
    view = _decode(raw)

    raw_artifacts = view.get("artifact_cids")
    if type(raw_artifacts) is not list or not raw_artifacts:
        raise CurrentPolicyViewError("current_policy_view_artifact_cids_invalid")
    artifact_cids = tuple(
        _string(value, "current_policy_view_artifact_cids_invalid")
        for value in raw_artifacts
    )

    raw_claims = view.get("policy_claims")
    if type(raw_claims) is not list or not raw_claims:
        raise CurrentPolicyViewError("current_policy_view_claims_invalid")
    claims: list[PolicyClaimEvidence] = []
    for raw_claim in raw_claims:
        if type(raw_claim) is not dict or set(raw_claim) != _CLAIM_FIELDS:
            raise CurrentPolicyViewError("current_policy_view_claim_fields_invalid")
        node_record = raw_claim.get("node_record")
        if type(node_record) is not dict:
            raise CurrentPolicyViewError("current_policy_view_claim_record_invalid")
        claims.append(
            PolicyClaimEvidence(
                claim_cid=_string(
                    raw_claim.get("claim_cid"),
                    "current_policy_view_claim_cid_invalid",
                ),
                node_record_json=_canonical_json_bytes(node_record),
            )
        )

    bootstrap_bundle = view.get("bootstrap_binding_bundle")
    if type(bootstrap_bundle) is not dict:
        raise CurrentPolicyViewError("current_policy_view_bootstrap_bundle_invalid")

    return CurrentPolicyEvaluationInput(
        release_assertion_cid=_string(
            view.get("release_assertion_cid"),
            "current_policy_view_release_cid_invalid",
        ),
        software_release_cid=_string(
            view.get("software_release_cid"),
            "current_policy_view_software_cid_invalid",
        ),
        artifact_cids=artifact_cids,
        network_id=_string(view.get("network_id"), "current_policy_view_network_invalid"),
        channel=_string(view.get("channel"), "current_policy_view_channel_invalid"),
        policy_id=_string(view.get("policy_id"), "current_policy_view_policy_id_invalid"),
        policy_public_key_hex=_string(
            view.get("policy_public_key_hex"),
            "current_policy_view_public_key_invalid",
        ),
        policy_claims=tuple(claims),
        authoritative_policy_head_cid=_string(
            view.get("authoritative_policy_head_cid"),
            "current_policy_view_head_cid_invalid",
        ),
        authoritative_validation_epoch=_uint(
            view.get("authoritative_validation_epoch"),
            "current_policy_view_authoritative_epoch_invalid",
        ),
        observer_validation_epoch=_uint(
            view.get("observer_validation_epoch"),
            "current_policy_view_observer_epoch_invalid",
        ),
        observer_highest_seen_sequence=highest_seen,
        bootstrap_policy_head_cid=_string(
            view.get("bootstrap_policy_head_cid"),
            "current_policy_view_bootstrap_head_invalid",
        ),
        bootstrap_binding_evidence_cid=_string(
            view.get("bootstrap_binding_evidence_cid"),
            "current_policy_view_bootstrap_evidence_invalid",
        ),
        bootstrap_binding_bundle_json=_canonical_json_bytes(bootstrap_bundle),
    )


__all__ = [
    "CurrentPolicyViewError",
    "MAX_POLICY_VIEW_FILE_BYTES",
    "POLICY_VIEW_SCHEMA_VERSION",
    "load_current_policy_evaluation_input",
]
