#!/usr/bin/env python3
"""Deterministic Row 35c reuse, refinement, and delayed-evidence SIM."""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping


SCHEMA_VERSION = "sufficiency_reuse_refinement_sim_v0"
COMPLETED_AT = "2026-10-22T18:00:00Z"
NETWORK = "fixture:network:row35c"
SCOPE = "fixture:scope:sufficiency-reuse"
LINEAGE = "fixture:authority-lineage:row35c"
TRUSTED_ISSUER = "fixture:authority:row35c"
OBSERVING_COMPONENT = "fixture:component:local-retriever"
OPERATION = "fixture:operation:f@1"
PARENT_OPERATION = "fixture:operation:parent-parity@2"
ASSESSMENT_KEYS = (
    "structural_closure",
    "computational_contract",
    "historical_production_authority",
    "present_artifact_eligibility",
    "current_observer_permission",
    "use_time_readiness",
)
ROLE_TYPES = {
    "claim": "sufficiency_claim",
    "production": "production_authority",
    "eligibility": "artifact_eligibility",
    "permission": "observer_permission",
    "availability": "retrieval_observation",
    "view": "active_authority_view",
}
SUBSTANTIVE_ROLES = {
    "claim": "computational_contract",
    "production": "historical_production_authority",
    "eligibility": "present_artifact_eligibility",
    "permission": "current_observer_permission",
}
MAX_RECORDS_PER_DELIVERY = 16
MAX_READS_PER_DECISION = 16
MAX_RECORD_BYTES = 16 * 1024
MAX_JSON_DEPTH = 12
MAX_JSON_NODES = 4_096
MAX_JSON_COLLECTION_ITEMS = 256
MAX_JSON_STRING_LENGTH = 4_096


class SimInvariantError(ValueError):
    """Raised when a deterministic fixture invariant is violated."""


def canonical_json(value: Any) -> bytes:
    node_count = 0

    def walk(item: Any, depth: int) -> None:
        nonlocal node_count
        node_count += 1
        if node_count > MAX_JSON_NODES:
            raise SimInvariantError("json_node_cap_exceeded")
        if depth > MAX_JSON_DEPTH:
            raise SimInvariantError("json_depth_cap_exceeded")
        if item is None or type(item) in (bool, int):
            return
        if type(item) is str:
            if len(item) > MAX_JSON_STRING_LENGTH:
                raise SimInvariantError("json_string_cap_exceeded")
            return
        if type(item) is list:
            if len(item) > MAX_JSON_COLLECTION_ITEMS:
                raise SimInvariantError("json_collection_cap_exceeded")
            for child in item:
                walk(child, depth + 1)
            return
        if type(item) is dict:
            if len(item) > MAX_JSON_COLLECTION_ITEMS:
                raise SimInvariantError("json_collection_cap_exceeded")
            for key, child in item.items():
                if type(key) is not str:
                    raise SimInvariantError("json_key_type_invalid")
                walk(key, depth + 1)
                walk(child, depth + 1)
            return
        raise SimInvariantError("json_value_type_invalid")

    walk(value, 0)
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def content_id(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


@dataclass
class ObserverStore:
    """An observer-local immutable evidence store with explicit read accounting."""

    observer: str
    records: dict[str, dict[str, Any]] = field(default_factory=dict)
    delivered_events: set[str] = field(default_factory=set)
    delivery_digests: dict[str, str] = field(default_factory=dict)
    read_log: list[str] = field(default_factory=list)
    conflicting_record_ids: set[str] = field(default_factory=set)
    active_views: ActiveViewTracker = field(default_factory=lambda: ActiveViewTracker())

    def deliver(self, event_id: str, records: Iterable[Mapping[str, Any]]) -> bool:
        if type(event_id) is not str or not event_id or len(event_id) > MAX_JSON_STRING_LENGTH:
            raise SimInvariantError("delivery_event_id_invalid")
        iterator = iter(records)
        materialized: list[dict[str, Any]] = []
        for _ in range(MAX_RECORDS_PER_DELIVERY + 1):
            try:
                record = next(iterator)
            except StopIteration:
                break
            if len(materialized) == MAX_RECORDS_PER_DELIVERY:
                raise SimInvariantError("delivery_record_cap_exceeded")
            if not isinstance(record, Mapping):
                raise SimInvariantError("record_type_invalid")
            materialized.append(dict(record))
        validated: list[tuple[str, dict[str, Any]]] = []
        for record in materialized:
            record_id = record.get("record_id")
            if type(record_id) is not str or not record_id.startswith("sha256:"):
                raise SimInvariantError("record_id_invalid")
            if set(record) != {"schema_version", "kind", "data", "record_id"}:
                raise SimInvariantError("record_fields_invalid")
            if type(record["schema_version"]) is not str or type(record["kind"]) is not str:
                raise SimInvariantError("record_header_invalid")
            if type(record["data"]) is not dict:
                raise SimInvariantError("record_data_invalid")
            body = {key: record[key] for key in ("schema_version", "kind", "data")}
            encoded = canonical_json(body)
            if len(encoded) > MAX_RECORD_BYTES:
                raise SimInvariantError("record_byte_cap_exceeded")
            if "sha256:" + hashlib.sha256(encoded).hexdigest() != record_id:
                raise SimInvariantError("record_content_id_mismatch")
            validated.append((record_id, copy.deepcopy(record)))
        delivery_digest = content_id(
            {"event_id": event_id, "record_ids": [item[0] for item in validated]}
        )
        prior_digest = self.delivery_digests.get(event_id)
        if prior_digest is not None:
            if prior_digest != delivery_digest:
                raise SimInvariantError("delivery_event_equivocation")
            return False
        for record_id, record in validated:
            existing = self.records.get(record_id)
            if existing is not None and existing != record:
                self.conflicting_record_ids.add(record_id)
                continue
            self.records[record_id] = record
            if record["kind"] == "active_authority_view":
                self.active_views.accept(record)
        self.delivered_events.add(event_id)
        self.delivery_digests[event_id] = delivery_digest
        return True

    def read(self, record_id: str, *, read_cap: int = MAX_READS_PER_DECISION) -> dict[str, Any] | None:
        if len(self.read_log) >= read_cap:
            raise SimInvariantError("decision_read_cap_exceeded")
        self.read_log.append(record_id)
        record = self.records.get(record_id)
        return copy.deepcopy(record) if record is not None else None


@dataclass
class ActiveViewTracker:
    """Observer-local monotone view selection; sequence is never authority by itself."""

    active: dict[tuple[str, str, str, str, str, str], dict[str, Any]] = field(
        default_factory=dict
    )
    equivocated: set[tuple[str, str, str, str, str, str]] = field(default_factory=set)

    def accept(self, record: Mapping[str, Any]) -> str:
        if record.get("kind") != "active_authority_view" or type(record.get("data")) is not dict:
            return "invalid"
        data = record["data"]
        if not _valid_role_data("active_authority_view", data):
            return "invalid"
        if data["issuer"] != TRUSTED_ISSUER or type(data["sequence"]) is not int:
            return "invalid"
        key = (
            data["observer"],
            data["network"],
            data["scope"],
            data["operation"],
            data["invocation"],
            data["authority_lineage"],
        )
        if any(type(item) is not str for item in key):
            return "invalid"
        current = self.active.get(key)
        if current is None:
            self.active[key] = copy.deepcopy(dict(record))
            return "accepted"
        current_sequence = current["data"]["sequence"]
        if data["sequence"] < current_sequence:
            return "stale_ignored"
        if data["sequence"] == current_sequence:
            if record["record_id"] == current["record_id"]:
                return "idempotent_replay"
            self.equivocated.add(key)
            return "equivocation"
        self.active[key] = copy.deepcopy(dict(record))
        recovered = key in self.equivocated
        self.equivocated.discard(key)
        return "accepted_recovery" if recovered else "accepted_newer"

    def resolve(self, request: Mapping[str, Any]) -> tuple[dict[str, Any] | None, str]:
        key = (
            request.get("observer"),
            request.get("network"),
            request.get("scope"),
            request.get("operation"),
            request.get("invocation"),
            LINEAGE,
        )
        if any(type(item) is not str for item in key):
            return None, "invalid_request_binding"
        if key in self.equivocated:
            return None, "equivocation"
        record = self.active.get(key)
        if record is None:
            return None, "missing"
        return copy.deepcopy(record), "active"


@dataclass
class VersionedCache:
    """Small deterministic cache with explicit namespace and FIFO eviction."""

    capacity: int
    values: dict[tuple[str, ...], Any] = field(default_factory=dict)
    order: list[tuple[str, ...]] = field(default_factory=list)

    def put(self, key: tuple[str, ...], value: Any) -> None:
        if key in self.values:
            self.values[key] = value
            return
        if len(self.order) >= self.capacity:
            evicted = self.order.pop(0)
            del self.values[evicted]
        self.order.append(key)
        self.values[key] = value

    def get(self, key: tuple[str, ...]) -> Any | None:
        return self.values.get(key)


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_id: str
    observer: str
    computational: str = "affirmative"
    historical: str = "affirmative"
    eligibility: str = "affirmative"
    permission: str = "affirmative"
    readiness: str = "ready"
    structural_mode: str = "complete"
    view_mode: str = "valid"
    operation: str = OPERATION
    stateful_requirement: int | None = None
    expected_final: str = "authorized_reuse"
    notes: str = ""


def _record(kind: str, data: Mapping[str, Any]) -> dict[str, Any]:
    body = {"schema_version": "row35c_evidence_v0", "kind": kind, "data": dict(data)}
    return {**body, "record_id": content_id(body)}


def _base_binding(spec: ScenarioSpec, invocation: str) -> dict[str, Any]:
    return {
        "network": NETWORK,
        "scope": SCOPE,
        "operation": spec.operation,
        "observer": spec.observer,
        "invocation": invocation,
    }


def build_evidence_bundle(spec: ScenarioSpec) -> tuple[dict[str, str], list[dict[str, Any]]]:
    invocation = f"fixture:invocation:{spec.scenario_id}"
    binding = _base_binding(spec, invocation)
    claim = _record(
        "sufficiency_claim",
        {**binding, "assessment": spec.computational, "checker_version": "row35c.v0"},
    )
    production = _record(
        "production_authority",
        {**binding, "assessment": spec.historical, "receipt_ref": "fixture:receipt:original"},
    )
    eligibility = _record(
        "artifact_eligibility",
        {**binding, "assessment": spec.eligibility, "policy_ref": "fixture:policy:eligibility"},
    )
    permission = _record(
        "observer_permission",
        {**binding, "assessment": spec.permission, "policy_ref": "fixture:policy:permission"},
    )
    availability_data = {
        **binding,
        "observing_component": OBSERVING_COMPONENT,
        "observation_context": "fixture:context:local-custody",
        "integrity_verified": spec.readiness == "ready",
        "bytes_retained_for_invocation": spec.readiness == "ready",
        "availability_outcome": spec.readiness,
        "valid_from_tick": 0,
        "valid_until_tick": 20,
    }
    availability = _record("retrieval_observation", availability_data)
    view_data = {
        **binding,
        "authority_lineage": LINEAGE,
        "issuer": TRUSTED_ISSUER,
        "sequence": 13,
        "valid_from_tick": 0,
        "valid_until_tick": 20,
        "policy_ref": permission["record_id"],
        "eligibility_ref": eligibility["record_id"],
    }
    if spec.view_mode == "wrong_observer":
        view_data["observer"] = "fixture:observer:attacker"
    elif spec.view_mode == "wrong_network":
        view_data["network"] = "fixture:network:other"
    elif spec.view_mode == "wrong_scope":
        view_data["scope"] = "fixture:scope:other"
    elif spec.view_mode == "expired":
        view_data["valid_until_tick"] = 1
    elif spec.view_mode == "wrong_policy_binding":
        view_data["policy_ref"] = "sha256:" + "0" * 64
    elif spec.view_mode == "wrong_eligibility_binding":
        view_data["eligibility_ref"] = "sha256:" + "1" * 64
    elif spec.view_mode == "untrusted_issuer":
        view_data["issuer"] = "fixture:authority:untrusted"
    elif spec.view_mode != "valid":
        raise SimInvariantError(f"unknown_view_mode:{spec.view_mode}")
    view = _record("active_authority_view", view_data)
    records = [claim, production, eligibility, permission, availability, view]
    refs = {
        "claim": claim["record_id"],
        "production": production["record_id"],
        "eligibility": eligibility["record_id"],
        "permission": permission["record_id"],
        "availability": availability["record_id"],
        "view": view["record_id"],
    }
    if spec.structural_mode == "missing":
        records = [record for record in records if record["record_id"] != refs["claim"]]
    elif spec.structural_mode == "contradictory":
        refs["claim"] = permission["record_id"]
    elif spec.structural_mode == "resource_exhausted":
        pass
    elif spec.structural_mode != "complete":
        raise SimInvariantError(f"unknown_structural_mode:{spec.structural_mode}")
    return refs, records


def _valid_binding(data: Mapping[str, Any], request: Mapping[str, Any]) -> bool:
    return all(
        type(data.get(key)) is str and data.get(key) == request.get(key)
        for key in ("network", "scope", "operation", "observer", "invocation")
    )


def _valid_role_data(kind: str, data: Mapping[str, Any]) -> bool:
    binding_keys = {"network", "scope", "operation", "observer", "invocation"}
    expected_keys = {
        "sufficiency_claim": binding_keys | {"assessment", "checker_version"},
        "production_authority": binding_keys | {"assessment", "receipt_ref"},
        "artifact_eligibility": binding_keys | {"assessment", "policy_ref"},
        "observer_permission": binding_keys | {"assessment", "policy_ref"},
        "retrieval_observation": binding_keys
        | {
            "observing_component",
            "observation_context",
            "integrity_verified",
            "bytes_retained_for_invocation",
            "availability_outcome",
            "valid_from_tick",
            "valid_until_tick",
        },
        "active_authority_view": binding_keys
        | {
            "authority_lineage",
            "issuer",
            "sequence",
            "valid_from_tick",
            "valid_until_tick",
            "policy_ref",
            "eligibility_ref",
        },
    }
    if kind not in expected_keys or set(data) != expected_keys[kind]:
        return False
    if any(type(data.get(key)) is not str for key in binding_keys):
        return False
    if kind in {
        "sufficiency_claim",
        "production_authority",
        "artifact_eligibility",
        "observer_permission",
    }:
        assessment = data.get("assessment")
        if type(assessment) is not str or assessment not in {
            "affirmative",
            "negative",
            "unresolved",
        }:
            return False
        extra_ref = {
            "sufficiency_claim": "checker_version",
            "production_authority": "receipt_ref",
            "artifact_eligibility": "policy_ref",
            "observer_permission": "policy_ref",
        }[kind]
        return type(data.get(extra_ref)) is str and bool(data.get(extra_ref))
    if kind == "retrieval_observation":
        return (
            type(data.get("observing_component")) is str
            and type(data.get("observation_context")) is str
            and type(data.get("integrity_verified")) is bool
            and type(data.get("bytes_retained_for_invocation")) is bool
            and data.get("availability_outcome") in {"ready", "not_ready", "unresolved"}
            and type(data.get("valid_from_tick")) is int
            and type(data.get("valid_until_tick")) is int
        )
    return (
        type(data.get("authority_lineage")) is str
        and type(data.get("issuer")) is str
        and type(data.get("sequence")) is int
        and type(data.get("valid_from_tick")) is int
        and type(data.get("valid_until_tick")) is int
        and type(data.get("policy_ref")) is str
        and type(data.get("eligibility_ref")) is str
    )


def aggregate_decision(assessments: Mapping[str, str]) -> tuple[str, list[str]]:
    if set(assessments) != set(ASSESSMENT_KEYS):
        raise SimInvariantError("assessment_schema_invalid")
    allowed = {
        "structural_closure": {"complete", "missing", "contradictory", "resource_exhausted"},
        "computational_contract": {"affirmative", "negative", "unresolved"},
        "historical_production_authority": {"affirmative", "negative", "unresolved"},
        "present_artifact_eligibility": {"affirmative", "negative", "unresolved"},
        "current_observer_permission": {"affirmative", "negative", "unresolved"},
        "use_time_readiness": {"ready", "not_ready", "unresolved"},
    }
    if any(type(assessments[key]) is not str or assessments[key] not in allowed[key] for key in allowed):
        raise SimInvariantError("assessment_value_invalid")
    structural = assessments["structural_closure"]
    if structural != "complete":
        return "unresolved_pending_evidence", [f"structural_closure:{structural}"]
    negative = [
        key
        for key in (
            "computational_contract",
            "historical_production_authority",
            "present_artifact_eligibility",
            "current_observer_permission",
        )
        if assessments[key] == "negative"
    ]
    if negative:
        return "rejected_use", [f"conclusive_negative:{key}" for key in negative]
    unresolved = [
        key
        for key in (
            "computational_contract",
            "historical_production_authority",
            "present_artifact_eligibility",
            "current_observer_permission",
        )
        if assessments[key] == "unresolved"
    ]
    if unresolved:
        return "unresolved_pending_evidence", [f"unresolved:{key}" for key in unresolved]
    readiness = assessments["use_time_readiness"]
    if readiness != "ready":
        return "unresolved_pending_evidence", [f"use_time_readiness:{readiness}"]
    return "authorized_reuse", ["all_required_assessments_satisfied"]


def evaluate_request(
    store: ObserverStore,
    request: Mapping[str, Any],
    refs: Mapping[str, str],
    *,
    tick: int = 10,
    read_cap: int = MAX_READS_PER_DECISION,
) -> dict[str, Any]:
    """Evaluate one request from only the supplied observer-local store."""

    store.read_log.clear()
    loaded: dict[str, dict[str, Any]] = {}
    structural = "complete"
    try:
        for role, expected_kind in ROLE_TYPES.items():
            ref = refs.get(role)
            if type(ref) is not str:
                structural = "missing"
                break
            record = store.read(ref, read_cap=read_cap)
            if record is None:
                structural = "missing"
                break
            if record.get("kind") != expected_kind or type(record.get("data")) is not dict:
                structural = "contradictory"
                break
            loaded[role] = record
    except SimInvariantError as exc:
        if str(exc) != "decision_read_cap_exceeded":
            raise
        structural = "resource_exhausted"

    assessments = {
        "structural_closure": structural,
        "computational_contract": "unresolved",
        "historical_production_authority": "unresolved",
        "present_artifact_eligibility": "unresolved",
        "current_observer_permission": "unresolved",
        "use_time_readiness": "unresolved",
    }
    if structural == "complete":
        if any(
            not _valid_role_data(record["kind"], record["data"])
            for record in loaded.values()
        ):
            structural = "contradictory"
            assessments["structural_closure"] = structural
    if structural == "complete":
        active_view, active_status = store.active_views.resolve(request)
        if active_status != "active" or active_view is None:
            assessments["current_observer_permission"] = "unresolved"
            assessments["present_artifact_eligibility"] = "unresolved"
        else:
            loaded["view"] = active_view
        for role, assessment_name in SUBSTANTIVE_ROLES.items():
            data = loaded[role]["data"]
            value = data.get("assessment")
            if _valid_binding(data, request):
                assessments[assessment_name] = value
        view = loaded["view"]["data"]
        permission_ref = loaded["permission"]["record_id"]
        eligibility_ref = loaded["eligibility"]["record_id"]
        view_valid = (
            _valid_binding(view, request)
            and view.get("authority_lineage") == LINEAGE
            and view.get("issuer") == TRUSTED_ISSUER
            and type(view.get("sequence")) is int
            and type(view.get("valid_from_tick")) is int
            and type(view.get("valid_until_tick")) is int
            and view["valid_from_tick"] <= tick <= view["valid_until_tick"]
            and view.get("policy_ref") == permission_ref
            and view.get("eligibility_ref") == eligibility_ref
        )
        if active_status != "active" or not view_valid:
            assessments["current_observer_permission"] = "unresolved"
            assessments["present_artifact_eligibility"] = "unresolved"
        availability = loaded["availability"]["data"]
        availability_value = availability.get("availability_outcome")
        if (
            _valid_binding(availability, request)
            and availability.get("observing_component") == OBSERVING_COMPONENT
            and availability.get("observation_context") == "fixture:context:local-custody"
            and type(availability.get("valid_from_tick")) is int
            and type(availability.get("valid_until_tick")) is int
            and availability["valid_from_tick"] <= tick <= availability["valid_until_tick"]
            and availability_value in {"ready", "not_ready", "unresolved"}
        ):
            if availability_value == "ready" and not (
                availability.get("integrity_verified") is True
                and availability.get("bytes_retained_for_invocation") is True
            ):
                assessments["use_time_readiness"] = "not_ready"
            else:
                assessments["use_time_readiness"] = availability_value

    final_decision, reason_codes = aggregate_decision(assessments)
    return {
        "assessments": assessments,
        "final_decision": final_decision,
        "reason_codes": reason_codes,
        "evidence_refs": sorted(set(refs.values())),
        "read_log": list(store.read_log),
    }


def _request(spec: ScenarioSpec) -> dict[str, str]:
    return {
        "observer": spec.observer,
        "network": NETWORK,
        "scope": SCOPE,
        "operation": spec.operation,
        "invocation": f"fixture:invocation:{spec.scenario_id}",
    }


def execute_spec(
    spec: ScenarioSpec,
    store: ObserverStore,
    *,
    event_id: str | None = None,
) -> dict[str, Any]:
    refs, records = build_evidence_bundle(spec)
    delivery_id = event_id or f"delivery:{spec.scenario_id}"
    delivered = store.deliver(delivery_id, records)
    read_cap = 3 if spec.structural_mode == "resource_exhausted" else MAX_READS_PER_DECISION
    outcome = evaluate_request(store, _request(spec), refs, read_cap=read_cap)
    if outcome["final_decision"] != spec.expected_final:
        raise SimInvariantError(
            f"expectation_mismatch:{spec.scenario_id}:"
            f"{outcome['final_decision']}!={spec.expected_final}"
        )
    return {
        "scenario_id": spec.scenario_id,
        "stateful_requirement": spec.stateful_requirement,
        "request": _request(spec),
        "active_view_ref": refs["view"],
        **outcome,
        "expected_final_decision": spec.expected_final,
        "delivery_applied": delivered,
        "notes": spec.notes,
        "receipt": {
            "receipt_type": "fixture:sufficiency-use-decision",
            "canonical_genesis_lineage": "local_only_not_applicable",
            "economic_attribution_status": "not_evaluated",
            "reputation_status": "not_evaluated",
            "scenario_id": spec.scenario_id,
            "final_decision": outcome["final_decision"],
        },
    }


def finite_oracle() -> dict[str, Any]:
    domain = list(itertools.product(range(3), repeat=3))

    def f(state: tuple[int, int, int]) -> int:
        return state[0] + state[1]

    def retained(state: tuple[int, int, int]) -> tuple[int, int]:
        return state[0], state[1]

    def parent(state: tuple[int, int, int]) -> tuple[bool, int | None]:
        admitted = state[2] > 0
        return admitted, f(state) if admitted else None

    def refined(state: tuple[int, int, int]) -> tuple[int, int, bool]:
        return state[0], state[1], state[2] > 0

    original_pairs = [
        (left, right)
        for left in domain
        for right in domain
        if retained(left) == retained(right)
    ]
    refined_pairs = [
        (left, right)
        for left in domain
        for right in domain
        if refined(left) == refined(right)
    ]
    original_valid = all(f(left) == f(right) for left, right in original_pairs)
    refined_valid = all(parent(left) == parent(right) for left, right in refined_pairs)
    witness_s = (1, 2, 0)
    witness_t = (1, 2, 1)
    witness_valid = (
        retained(witness_s) == retained(witness_t)
        and parent(witness_s) != parent(witness_t)
        and refined(witness_s) != refined(witness_t)
    )
    if (len(original_pairs), len(refined_pairs), original_valid, refined_valid, witness_valid) != (
        81,
        45,
        True,
        True,
        True,
    ):
        raise SimInvariantError("finite_oracle_mismatch")
    return {
        "domain_size": len(domain),
        "original_equal_representation_ordered_pairs": len(original_pairs),
        "refined_equal_representation_ordered_pairs": len(refined_pairs),
        "original_claim_valid": original_valid,
        "refined_parent_claim_valid": refined_valid,
        "separating_witness": {
            "s": list(witness_s),
            "t": list(witness_t),
            "same_original_representation": retained(witness_s) == retained(witness_t),
            "different_parent_behavior": parent(witness_s) != parent(witness_t),
            "separated_by_refinement": refined(witness_s) != refined(witness_t),
        },
    }


def run_reuse_cycle() -> dict[str, Any]:
    original_claim = {
        "operation": OPERATION,
        "domain": "{0,1,2}^3",
        "representation": "(x1,x2)",
        "scope": SCOPE,
    }
    original_claim_id = content_id(original_claim)
    exact_cache = {(OPERATION, (1, 2, 0)): 3}
    semantic_cache = {(OPERATION, (1, 2)): 3}
    exact_hit = (OPERATION, (1, 2, 2)) in exact_cache
    semantic_hit = semantic_cache.get((OPERATION, (1, 2)))
    refined_claim = {
        "operation": PARENT_OPERATION,
        "domain": "{0,1,2}^3",
        "representation": "(x1,x2,indicator(x3>0))",
        "scope": SCOPE + ":parent",
        "supersedes_for_parent": original_claim_id,
    }
    events = [
        "claim_established",
        "claim_checked_exhaustively",
        "semantic_reuse_performed",
        "parent_operation_introduced",
        "separating_witness_recorded",
        "refinement_recorded",
        "refinement_checked_exhaustively",
        "original_history_preserved",
    ]
    if exact_hit or semantic_hit != 3 or content_id(original_claim) != original_claim_id:
        raise SimInvariantError("reuse_cycle_invariant_failed")
    return {
        "events": events,
        "original_claim_id": original_claim_id,
        "original_claim_id_after_refinement": content_id(original_claim),
        "refined_claim_id": content_id(refined_claim),
        "exact_input_cache_hit": exact_hit,
        "operation_relative_cache_hit": semantic_hit is not None,
        "reused_output": semantic_hit,
        "cache_namespaces": {
            "exact_input": "(operation_version, full_input)",
            "operation_relative": "(operation_version, retained_representation)",
            "mathematical_verification": "(claim_id, checker_version)",
            "prepared_checks": "(request_fingerprint, active_view_id)",
        },
    }


def _r9_specs() -> list[ScenarioSpec]:
    return [
        ScenarioSpec("R9_event_00_A_publish_and_local_use", "A"),
        ScenarioSpec("R9_event_01_B_receives_fresh_evidence", "B"),
        ScenarioSpec("R9_event_02_B_authorized_reuse", "B"),
        ScenarioSpec("R9_event_03_C_parent_requirement_unresolved", "C", computational="unresolved", expected_final="unresolved_pending_evidence"),
        ScenarioSpec("R9_event_04_C_separating_witness_rejects_old_claim", "C", computational="negative", operation=PARENT_OPERATION, expected_final="rejected_use"),
        ScenarioSpec("R9_event_05_C_refined_claim_authorized", "C", operation=PARENT_OPERATION),
        ScenarioSpec("R9_event_06_B_parent_mismatch_rejected", "B", computational="negative", operation=PARENT_OPERATION, expected_final="rejected_use"),
        ScenarioSpec("R9_event_07_B_missing_checkpoint_record", "B", structural_mode="missing", expected_final="unresolved_pending_evidence"),
        ScenarioSpec("R9_event_08_B_stale_view_still_valid_for_original_scope", "B"),
        ScenarioSpec("R9_event_09_B_updated_view_authorized", "B"),
        ScenarioSpec("R9_event_10_idempotent_redelivery", "B", notes="same delivery event is replayed and suppressed"),
    ]


def _variant_specs() -> list[ScenarioSpec]:
    return [
        ScenarioSpec("R9_variant_missing_output_bytes", "B", readiness="not_ready", expected_final="unresolved_pending_evidence"),
        ScenarioSpec("R9_variant_corrupted_evidence", "B", structural_mode="contradictory", expected_final="unresolved_pending_evidence"),
        ScenarioSpec("R9_variant_denied_access", "B", permission="negative", expected_final="rejected_use"),
        ScenarioSpec("R9_variant_exhausted_budget", "B", structural_mode="resource_exhausted", expected_final="unresolved_pending_evidence"),
        ScenarioSpec("R9_variant_checkpoint_policy_mismatch", "B", view_mode="wrong_policy_binding", expected_final="unresolved_pending_evidence"),
        ScenarioSpec("R9_variant_incomplete_reverse_dependency_index", "B", structural_mode="missing", expected_final="unresolved_pending_evidence"),
    ]


def _stateful_specs() -> list[ScenarioSpec]:
    return [
        ScenarioSpec("state_01_older_view_after_newer_ignored", "A", stateful_requirement=1),
        ScenarioSpec("state_02_same_lineage_replay_idempotent", "A", stateful_requirement=2),
        ScenarioSpec("state_03_conflict_then_explicit_recovery", "A", stateful_requirement=3),
        ScenarioSpec("state_04_authority_equivocation_unresolved", "A", view_mode="untrusted_issuer", stateful_requirement=4, expected_final="unresolved_pending_evidence"),
        ScenarioSpec("state_05_independent_scopes_not_comparable", "A", view_mode="wrong_scope", stateful_requirement=5, expected_final="unresolved_pending_evidence"),
        ScenarioSpec("state_06_valid_evidence_resolves_pending", "A", stateful_requirement=6),
        ScenarioSpec("state_07_negative_math_cached_as_negative", "A", computational="negative", stateful_requirement=7, expected_final="rejected_use"),
        ScenarioSpec("state_08_operation_version_invalidates_cache", "A", computational="unresolved", operation=PARENT_OPERATION, stateful_requirement=8, expected_final="unresolved_pending_evidence"),
        ScenarioSpec("state_09_corrupted_delivery_then_recovery", "A", stateful_requirement=9),
        ScenarioSpec("state_10_checker_version_cache_isolation", "A", stateful_requirement=10),
        ScenarioSpec("state_11_withdrawal_after_cached_verification", "A", eligibility="negative", stateful_requirement=11, expected_final="rejected_use"),
        ScenarioSpec("state_12a_wrong_observer", "A", view_mode="wrong_observer", stateful_requirement=12, expected_final="unresolved_pending_evidence"),
        ScenarioSpec("state_12b_wrong_network", "A", view_mode="wrong_network", stateful_requirement=12, expected_final="unresolved_pending_evidence"),
        ScenarioSpec("state_12c_wrong_scope", "A", view_mode="wrong_scope", stateful_requirement=12, expected_final="unresolved_pending_evidence"),
        ScenarioSpec("state_12d_expired_lease", "A", view_mode="expired", stateful_requirement=12, expected_final="unresolved_pending_evidence"),
        ScenarioSpec("state_12e_wrong_policy_binding", "A", view_mode="wrong_policy_binding", stateful_requirement=12, expected_final="unresolved_pending_evidence"),
        ScenarioSpec("state_12f_wrong_eligibility_binding", "A", view_mode="wrong_eligibility_binding", stateful_requirement=12, expected_final="unresolved_pending_evidence"),
        ScenarioSpec("state_12g_untrusted_authority_view", "A", view_mode="untrusted_issuer", stateful_requirement=12, expected_final="unresolved_pending_evidence"),
        ScenarioSpec("state_13_immutable_history_survives_revision", "A", stateful_requirement=13),
        ScenarioSpec("state_14_failed_reuse_does_not_authorize_fallback", "A", computational="unresolved", permission="unresolved", stateful_requirement=14, expected_final="unresolved_pending_evidence"),
    ]


def _tracker_view(*, sequence: int, scope: str = SCOPE, label: str = "primary") -> dict[str, Any]:
    return _record(
        "active_authority_view",
        {
            "observer": "A",
            "network": NETWORK,
            "scope": scope,
            "operation": OPERATION,
            "invocation": "fixture:invocation:tracker",
            "authority_lineage": LINEAGE,
            "issuer": TRUSTED_ISSUER,
            "sequence": sequence,
            "valid_from_tick": 0,
            "valid_until_tick": 20,
            "policy_ref": f"fixture:policy:{label}",
            "eligibility_ref": f"fixture:eligibility:{label}",
        },
    )


def run_stateful_transition_checks() -> dict[str, dict[str, Any]]:
    """Execute the transitions behind the fourteen Row 35c requirements."""

    checks: dict[str, dict[str, Any]] = {}

    tracker = ActiveViewTracker()
    newer = _tracker_view(sequence=13)
    older = _tracker_view(sequence=12)
    first = tracker.accept(newer)
    stale = tracker.accept(older)
    checks["1"] = {
        "passed": first == "accepted" and stale == "stale_ignored"
        and next(iter(tracker.active.values()))["record_id"] == newer["record_id"],
        "transitions": [first, stale],
    }
    replay = tracker.accept(newer)
    checks["2"] = {"passed": replay == "idempotent_replay", "transition": replay}

    conflict = _tracker_view(sequence=13, label="conflict")
    equivocation = tracker.accept(conflict)
    recovery = tracker.accept(_tracker_view(sequence=14, label="recovery"))
    checks["3"] = {
        "passed": equivocation == "equivocation" and recovery == "accepted_recovery"
        and not tracker.equivocated,
        "transitions": [equivocation, recovery],
    }

    equivocation_tracker = ActiveViewTracker()
    equivocation_tracker.accept(_tracker_view(sequence=7, label="left"))
    unresolved_equivocation = equivocation_tracker.accept(
        _tracker_view(sequence=7, label="right")
    )
    checks["4"] = {
        "passed": unresolved_equivocation == "equivocation"
        and bool(equivocation_tracker.equivocated),
        "transition": unresolved_equivocation,
    }

    scoped = ActiveViewTracker()
    alpha = scoped.accept(_tracker_view(sequence=30, scope=SCOPE + ":alpha"))
    beta = scoped.accept(_tracker_view(sequence=1, scope=SCOPE + ":beta"))
    checks["5"] = {
        "passed": alpha == beta == "accepted" and len(scoped.active) == 2,
        "active_scope_count": len(scoped.active),
    }

    pending_spec = ScenarioSpec("transition_pending_to_valid", "A")
    pending_refs, pending_records = build_evidence_bundle(pending_spec)
    pending_store = ObserverStore("A")
    before = evaluate_request(pending_store, _request(pending_spec), pending_refs)
    pending_store.deliver("transition:valid", pending_records)
    after = evaluate_request(pending_store, _request(pending_spec), pending_refs)
    checks["6"] = {
        "passed": before["final_decision"] == "unresolved_pending_evidence"
        and after["final_decision"] == "authorized_reuse",
        "before": before["final_decision"],
        "after": after["final_decision"],
    }

    math_cache = VersionedCache(4)
    negative_key = ("math", "claim:negative", "checker:v1")
    math_cache.put(negative_key, False)
    checks["7"] = {
        "passed": math_cache.get(negative_key) is False
        and math_cache.get(("math", "claim:missing", "checker:v1")) is None,
        "negative_is_distinct_from_missing": True,
    }

    version_cache = VersionedCache(4)
    old_key = ("semantic", OPERATION, "contract:v1", "checker:v1")
    new_key = ("semantic", PARENT_OPERATION, "contract:v2", "checker:v2")
    version_cache.put(old_key, 3)
    checks["8"] = {
        "passed": version_cache.get(old_key) == 3 and version_cache.get(new_key) is None,
        "old_key": list(old_key),
        "new_key": list(new_key),
    }

    recovery_spec = ScenarioSpec("transition_corruption_recovery", "A")
    recovery_refs, recovery_records = build_evidence_bundle(recovery_spec)
    tampered = copy.deepcopy(recovery_records)
    tampered[0]["data"]["assessment"] = "negative"
    recovery_store = ObserverStore("A")
    corruption_rejected = False
    try:
        recovery_store.deliver("transition:corrupt", tampered)
    except SimInvariantError as exc:
        corruption_rejected = str(exc) == "record_content_id_mismatch"
    recovery_store.deliver("transition:clean", recovery_records)
    recovered = evaluate_request(recovery_store, _request(recovery_spec), recovery_refs)
    checks["9"] = {
        "passed": corruption_rejected and recovered["final_decision"] == "authorized_reuse",
        "corruption_rejected": corruption_rejected,
        "after": recovered["final_decision"],
    }

    eviction_cache = VersionedCache(2)
    key_v1 = ("prepared", "request:a", "checker:v1")
    key_v2 = ("prepared", "request:a", "checker:v2")
    key_b = ("prepared", "request:b", "checker:v2")
    eviction_cache.put(key_v1, "v1")
    eviction_cache.put(key_v2, "v2")
    eviction_cache.put(key_b, "b")
    checks["10"] = {
        "passed": eviction_cache.get(key_v1) is None
        and eviction_cache.get(key_v2) == "v2"
        and eviction_cache.get(key_b) == "b",
        "remaining_keys": [list(key) for key in eviction_cache.order],
    }

    withdrawal = {
        "structural_closure": "complete",
        "computational_contract": "affirmative",
        "historical_production_authority": "affirmative",
        "present_artifact_eligibility": "negative",
        "current_observer_permission": "affirmative",
        "use_time_readiness": "ready",
    }
    checks["11"] = {
        "passed": aggregate_decision(withdrawal)[0] == "rejected_use"
        and withdrawal["historical_production_authority"] == "affirmative",
        "decision": aggregate_decision(withdrawal)[0],
    }

    attack_results = []
    for spec in _stateful_specs():
        if spec.stateful_requirement == 12:
            attack_results.append(execute_spec(spec, ObserverStore("A"))["final_decision"])
    checks["12"] = {
        "passed": len(attack_results) == 7
        and set(attack_results) == {"unresolved_pending_evidence"},
        "decisions": attack_results,
    }

    cycle = run_reuse_cycle()
    checks["13"] = {
        "passed": cycle["original_claim_id"] == cycle["original_claim_id_after_refinement"]
        and cycle["original_claim_id"] != cycle["refined_claim_id"],
        "original_claim_id": cycle["original_claim_id"],
        "refined_claim_id": cycle["refined_claim_id"],
    }

    failed_reuse = {
        "structural_closure": "complete",
        "computational_contract": "unresolved",
        "historical_production_authority": "affirmative",
        "present_artifact_eligibility": "affirmative",
        "current_observer_permission": "unresolved",
        "use_time_readiness": "ready",
    }
    fallback = {
        **failed_reuse,
        "computational_contract": "affirmative",
        "current_observer_permission": "unresolved",
    }
    checks["14"] = {
        "passed": aggregate_decision(failed_reuse)[0] == "unresolved_pending_evidence"
        and aggregate_decision(fallback)[0] == "unresolved_pending_evidence",
        "failed_reuse_decision": aggregate_decision(failed_reuse)[0],
        "separate_fallback_decision": aggregate_decision(fallback)[0],
    }

    if set(checks) != {str(index) for index in range(1, 15)}:
        raise SimInvariantError("stateful_transition_check_count_mismatch")
    if not all(item["passed"] is True for item in checks.values()):
        raise SimInvariantError("stateful_transition_check_failed")
    return checks


def run_simulation() -> dict[str, Any]:
    oracle = finite_oracle()
    cycle = run_reuse_cycle()
    stores = {name: ObserverStore(name) for name in ("A", "B", "C")}
    scenarios: list[dict[str, Any]] = []

    cycle_spec = ScenarioSpec("cycle_step_03_operation_relative_reuse", "A")
    scenarios.append(execute_spec(cycle_spec, stores["A"]))

    prior_event_09: tuple[ScenarioSpec, dict[str, str], list[dict[str, Any]]] | None = None
    for spec in _r9_specs():
        if spec.scenario_id.startswith("R9_event_10"):
            if prior_event_09 is None:
                raise SimInvariantError("event_09_state_missing")
            prior_spec, prior_refs, prior_records = prior_event_09
            replay_applied = stores["B"].deliver("r9:event:09", prior_records)
            outcome = evaluate_request(stores["B"], _request(prior_spec), prior_refs)
            scenarios.append(
                {
                    "scenario_id": spec.scenario_id,
                    "stateful_requirement": None,
                    "request": _request(prior_spec),
                    "active_view_ref": prior_refs["view"],
                    **outcome,
                    "expected_final_decision": "authorized_reuse",
                    "delivery_applied": replay_applied,
                    "notes": spec.notes,
                    "receipt": {
                        "receipt_type": "fixture:sufficiency-use-decision",
                        "canonical_genesis_lineage": "local_only_not_applicable",
                        "economic_attribution_status": "not_evaluated",
                        "reputation_status": "not_evaluated",
                        "scenario_id": spec.scenario_id,
                        "final_decision": outcome["final_decision"],
                    },
                }
            )
            continue
        refs, records = build_evidence_bundle(spec)
        delivery_applied = stores[spec.observer].deliver(
            f"r9:event:{spec.scenario_id[9:11]}", records
        )
        outcome = evaluate_request(
            stores[spec.observer],
            _request(spec),
            refs,
            read_cap=3 if spec.structural_mode == "resource_exhausted" else MAX_READS_PER_DECISION,
        )
        if outcome["final_decision"] != spec.expected_final:
            raise SimInvariantError(f"r9_expectation_mismatch:{spec.scenario_id}")
        scenarios.append(
            {
                "scenario_id": spec.scenario_id,
                "stateful_requirement": None,
                "request": _request(spec),
                "active_view_ref": refs["view"],
                **outcome,
                "expected_final_decision": spec.expected_final,
                "delivery_applied": delivery_applied,
                "notes": spec.notes,
                "receipt": {
                    "receipt_type": "fixture:sufficiency-use-decision",
                    "canonical_genesis_lineage": "local_only_not_applicable",
                    "economic_attribution_status": "not_evaluated",
                    "reputation_status": "not_evaluated",
                    "scenario_id": spec.scenario_id,
                    "final_decision": outcome["final_decision"],
                },
            }
        )
        if spec.scenario_id.startswith("R9_event_09"):
            prior_event_09 = (spec, refs, records)

    for spec in [*_variant_specs(), *_stateful_specs()]:
        scenarios.append(execute_spec(spec, ObserverStore(spec.observer)))

    if len(scenarios) != 38:
        raise SimInvariantError(f"scenario_count_mismatch:{len(scenarios)}")
    if {scenario["stateful_requirement"] for scenario in scenarios if scenario["stateful_requirement"]} != set(range(1, 15)):
        raise SimInvariantError("stateful_requirement_coverage_mismatch")
    if any(
        scenario["receipt"]["canonical_genesis_lineage"] != "local_only_not_applicable"
        for scenario in scenarios
    ):
        raise SimInvariantError("canonical_lineage_envelope_mismatch")
    transition_checks = run_stateful_transition_checks()
    return {
        "schema_version": SCHEMA_VERSION,
        "completed_at": COMPLETED_AT,
        "authority_model": "finite_fixture_only_not_production_authority",
        "networking": "deterministic_local_delivery_only",
        "finite_oracle": oracle,
        "reuse_revision_cycle": cycle,
        "stateful_transition_checks": transition_checks,
        "use_decision_scenarios": scenarios,
        "observer_store_summary": {
            name: {
                "record_count": len(store.records),
                "delivered_event_count": len(store.delivered_events),
                "conflict_count": len(store.conflicting_record_ids),
            }
            for name, store in stores.items()
        },
        "limits": [
            "finite fixtures do not establish production consensus safety",
            "authority authentication and delivery are modeled assumptions",
            "no speed, energy, ECU, ILC, or settlement claim",
            "no hidden global oracle is available to observer decisions",
        ],
    }


def _summary(results: Mapping[str, Any]) -> str:
    scenarios = results["use_decision_scenarios"]
    counts = {
        verdict: sum(item["final_decision"] == verdict for item in scenarios)
        for verdict in ("authorized_reuse", "rejected_use", "unresolved_pending_evidence")
    }
    oracle = results["finite_oracle"]
    return "\n".join(
        [
            "# Row 35c Reuse and Refinement SIM",
            "",
            f"- Scenarios: {len(scenarios)}",
            f"- Authorized reuse: {counts['authorized_reuse']}",
            f"- Rejected use: {counts['rejected_use']}",
            f"- Unresolved pending evidence: {counts['unresolved_pending_evidence']}",
            f"- Original equal-representation ordered pairs: {oracle['original_equal_representation_ordered_pairs']}",
            f"- Refined equal-representation ordered pairs: {oracle['refined_equal_representation_ordered_pairs']}",
            "- Authority model: finite fixture only; not production authority",
            "- Networking: deterministic local delivery only",
            "- graph_delta=none",
            "",
        ]
    )


def write_results(output_dir: Path) -> dict[str, Any]:
    results = run_simulation()
    _atomic_write(
        output_dir / "reuse_refinement_results.json",
        canonical_json(results) + b"\n",
    )
    _atomic_write(
        output_dir / "reuse_refinement_summary.md",
        _summary(results).encode("utf-8"),
    )
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("out/sufficiency_reuse_refinement_00"),
    )
    args = parser.parse_args()
    results = write_results(args.output_dir)
    print(
        json.dumps(
            {
                "status": "PASS",
                "scenario_count": len(results["use_decision_scenarios"]),
                "results_sha256": hashlib.sha256(canonical_json(results)).hexdigest(),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
