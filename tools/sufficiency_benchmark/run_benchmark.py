#!/usr/bin/env python3
"""Bounded comparative benchmark for local operation-relative sufficiency.

This tool measures local fixtures only. It does not fetch from a network,
resolve production authority, write the ILC graph, or make an energy claim.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import platform
import statistics
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, MutableMapping, Sequence


SCHEMA_VERSION = "sufficiency_benchmark_v0"
BENCHMARK_VERSION = "1"
CONTRACT_VERSION = "sufficiency_contract_v1"
CHECKER_VERSION = "sufficiency_checker_v2"
OPERATION_ID = "fixture:add-first-two"
OPERATION_VERSION = "1"

REUSE_MODES = (
    "direct_computation",
    "ordinary_exact_input_cache",
    "sufficiency_semantic_reuse",
)
RETRIEVAL_STRATEGIES = (
    "full_bounded_store",
    "literal_all_reference_traversal",
    "generic_dependency_aware",
    "typed_mandatory_evidence_closure",
)
PATHS = ("cold", "warm")
WORKLOAD_IDS = (
    "identical_inputs",
    "different_inputs_equivalent_operation",
    "low_reuse",
    "changed_dependencies",
    "changed_operation_scope",
    "invalid_sufficiency_claim",
    "noninterference",
)
PHASES = (
    "preparation",
    "representation_guard",
    "retrieval",
    "integrity",
    "authentication",
    "freshness",
    "cache_lookup_maintenance",
    "execution",
    "correction",
)

MIN_WARMUPS = 2
MIN_SAMPLES = 9
DEFAULT_KERNEL_ROUNDS = 96
MAX_KERNEL_ROUNDS = 10_000
MAX_STORE_OBJECTS = 64
MAX_OBJECT_BYTES = 16_384
MAX_REFERENCES_PER_OBJECT = 32
MAX_RETRIEVAL_DEPTH = 16
MAX_OBJECT_READS = 64
MAX_CACHE_ENTRIES = 32
MAX_OUTPUT_BYTES = 8 * 1024 * 1024


class BenchmarkError(ValueError):
    """Stable benchmark failure."""


class ResourceLimitError(BenchmarkError):
    """A bounded fixture or retrieval limit was exceeded."""

    def __init__(
        self,
        code: str,
        *,
        object_reads: int = 0,
        bytes_acquired: int = 0,
    ) -> None:
        super().__init__(code)
        self.code = code
        self.object_reads = object_reads
        self.bytes_acquired = bytes_acquired


@dataclass(frozen=True)
class Workload:
    workload_id: str
    prime_input: tuple[int, int, int]
    target_input: tuple[int, int, int]
    prime_dependency: str = "dependency:v1"
    target_dependency: str = "dependency:v1"
    prime_scope: str = "scope:local-a"
    target_scope: str = "scope:local-a"
    claim_valid: bool = True
    include_unrelated: bool = False


WORKLOADS = (
    Workload("identical_inputs", (1, 2, 0), (1, 2, 0)),
    Workload("different_inputs_equivalent_operation", (1, 2, 0), (1, 2, 2)),
    Workload("low_reuse", (0, 0, 0), (2, 1, 2)),
    Workload(
        "changed_dependencies",
        (1, 2, 0),
        (1, 2, 0),
        prime_dependency="dependency:v1",
        target_dependency="dependency:v2",
    ),
    Workload(
        "changed_operation_scope",
        (1, 2, 0),
        (1, 2, 0),
        prime_scope="scope:local-a",
        target_scope="scope:local-b",
    ),
    Workload("invalid_sufficiency_claim", (1, 2, 0), (1, 2, 2), claim_valid=False),
    Workload(
        "noninterference",
        (1, 2, 0),
        (1, 2, 0),
        include_unrelated=True,
    ),
)


def canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _content_id(body: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(
        b"ilc.sufficiency.benchmark-object.v0\x00" + canonical_json(body)
    ).hexdigest()


def _record(
    object_type: str,
    data: Mapping[str, Any],
    refs: Sequence[tuple[str, str, bool]] = (),
) -> dict[str, Any]:
    body = {
        "object_type": object_type,
        "data": copy.deepcopy(dict(data)),
        "refs": [
            {"role": role, "target": target, "required": required}
            for role, target, required in refs
        ],
    }
    return {"object_id": _content_id(body), **body}


def _verify_record(record: Mapping[str, Any]) -> bool:
    if type(record) is not dict or set(record) != {"object_id", "object_type", "data", "refs"}:
        return False
    body = {key: record[key] for key in ("object_type", "data", "refs")}
    return type(record["object_id"]) is str and record["object_id"] == _content_id(body)


class FixtureStore:
    """Immutable bounded content-addressed fixture store."""

    def __init__(self, records: Iterable[Mapping[str, Any]]) -> None:
        iterator = iter(records)
        materialized: list[dict[str, Any]] = []
        for _ in range(MAX_STORE_OBJECTS + 1):
            try:
                item = next(iterator)
            except StopIteration:
                break
            if len(materialized) == MAX_STORE_OBJECTS:
                raise ResourceLimitError("store_object_limit_exceeded")
            if not isinstance(item, Mapping):
                raise BenchmarkError("store_record_type_invalid")
            materialized.append(dict(item))
        if not materialized:
            raise ResourceLimitError("store_object_limit_exceeded")
        by_id: dict[str, dict[str, Any]] = {}
        for record in materialized:
            if not _verify_record(record):
                raise BenchmarkError("store_record_integrity_invalid")
            encoded = canonical_json(record)
            if len(encoded) > MAX_OBJECT_BYTES:
                raise ResourceLimitError("store_object_bytes_limit_exceeded")
            refs = record["refs"]
            if type(refs) is not list or len(refs) > MAX_REFERENCES_PER_OBJECT:
                raise ResourceLimitError("store_reference_limit_exceeded")
            if record["object_id"] in by_id:
                raise BenchmarkError("store_object_id_duplicate")
            by_id[record["object_id"]] = copy.deepcopy(record)
        self._records = by_id

    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._records))

    def get(self, object_id: str) -> tuple[dict[str, Any], int]:
        record = self._records.get(object_id)
        if record is None:
            raise BenchmarkError("referenced_object_missing")
        return copy.deepcopy(record), len(canonical_json(record))


ROLE_TYPES: dict[tuple[str, str], frozenset[str]] = {
    ("use_request", "claim"): frozenset({"sufficiency_claim"}),
    ("use_request", "authority_view"): frozenset({"authority_view"}),
    ("use_request", "input"): frozenset({"input_state"}),
    ("use_request", "availability"): frozenset({"retrieval_observation"}),
    ("sufficiency_claim", "evidence"): frozenset({"finite_evidence"}),
    ("authority_view", "permission"): frozenset({"permission"}),
    ("authority_view", "policy"): frozenset({"policy"}),
}
MANDATORY_ROLES: dict[str, frozenset[str]] = {
    "use_request": frozenset({"claim", "authority_view", "input", "availability"}),
    "sufficiency_claim": frozenset({"evidence"}),
    "authority_view": frozenset({"permission", "policy"}),
}


def build_fixture(workload: Workload) -> tuple[FixtureStore, str, dict[str, str]]:
    evidence = _record(
        "finite_evidence",
        {"checker_version": CHECKER_VERSION, "domain": "{0,1,2}^3", "verified": True},
    )
    claim = _record(
        "sufficiency_claim",
        {
            "operation_id": OPERATION_ID,
            "operation_version": OPERATION_VERSION,
            "contract_version": CONTRACT_VERSION,
            "claim_valid": workload.claim_valid,
        },
        (("evidence", evidence["object_id"], True),),
    )
    permission = _record(
        "permission",
        {"observer": "observer:benchmark", "scope": workload.target_scope, "assessment": "affirmative"},
    )
    policy = _record(
        "policy",
        {"policy_ref": "policy:fixture:v1", "scope": workload.target_scope, "fresh_through_tick": 10},
    )
    view = _record(
        "authority_view",
        {"observer": "observer:benchmark", "scope": workload.target_scope, "tick": 5},
        (
            ("permission", permission["object_id"], True),
            ("policy", policy["object_id"], True),
        ),
    )
    input_record = _record(
        "input_state",
        {"input": list(workload.target_input), "dependency_version": workload.target_dependency},
    )
    availability = _record(
        "retrieval_observation",
        {
            "observer": "observer:benchmark",
            "scope": workload.target_scope,
            "integrity_verified": True,
            "retained_for_invocation": True,
        },
    )
    audit_leaf = _record("audit_note", {"note": "generic dependency metadata"})
    audit = _record(
        "audit_bundle",
        {"status": "support_only"},
        (("audit_note", audit_leaf["object_id"], True),),
    )
    diagnostic = _record("diagnostic", {"message": "non-authoritative trace"})
    unrelated_leaf = _record("unrelated_leaf", {"value": "unrelated"})
    unrelated = _record(
        "unrelated_bundle",
        {"purpose": "noninterference"},
        (("unrelated_leaf", unrelated_leaf["object_id"], False),),
    )
    root_refs = [
        ("claim", claim["object_id"], True),
        ("authority_view", view["object_id"], True),
        ("input", input_record["object_id"], True),
        ("availability", availability["object_id"], True),
        ("audit", audit["object_id"], True),
        ("diagnostic", diagnostic["object_id"], False),
    ]
    if workload.include_unrelated:
        root_refs.append(("unrelated", unrelated["object_id"], False))
    root = _record(
        "use_request",
        {
            "invocation": "invocation:benchmark",
            "operation_id": OPERATION_ID,
            "scope": workload.target_scope,
        },
        root_refs,
    )
    records = [
        evidence,
        claim,
        permission,
        policy,
        view,
        input_record,
        availability,
        audit_leaf,
        audit,
        diagnostic,
        root,
    ]
    if workload.include_unrelated:
        records.extend((unrelated_leaf, unrelated))
    store = FixtureStore(records)
    named = {
        "claim": claim["object_id"],
        "evidence": evidence["object_id"],
        "view": view["object_id"],
        "permission": permission["object_id"],
        "policy": policy["object_id"],
        "input": input_record["object_id"],
        "availability": availability["object_id"],
    }
    return store, root["object_id"], named


def _follow_refs(record: Mapping[str, Any], *, required_only: bool) -> list[str]:
    refs = record["refs"]
    return [
        item["target"]
        for item in refs
        if not required_only or item["required"] is True
    ]


def acquire_objects(
    store: FixtureStore,
    root_id: str,
    strategy: str,
    *,
    read_cap: int = MAX_OBJECT_READS,
) -> dict[str, Any]:
    if strategy not in RETRIEVAL_STRATEGIES:
        raise BenchmarkError("retrieval_strategy_invalid")
    if type(read_cap) is not int or read_cap <= 0 or read_cap > MAX_OBJECT_READS:
        raise ResourceLimitError("retrieval_read_cap_invalid")
    queue: list[tuple[str, int, str | None, str | None]]
    if strategy == "full_bounded_store":
        queue = [(object_id, 0, None, None) for object_id in store.ids()]
    else:
        queue = [(root_id, 0, None, None)]
    acquired: dict[str, dict[str, Any]] = {}
    bytes_acquired = 0
    while queue:
        object_id, depth, parent_type, parent_role = queue.pop(0)
        if object_id in acquired:
            if strategy == "typed_mandatory_evidence_closure" and parent_type is not None:
                permitted = ROLE_TYPES.get((parent_type, str(parent_role)))
                if permitted is None or acquired[object_id]["object_type"] not in permitted:
                    raise BenchmarkError("typed_role_target_invalid")
            continue
        if depth > MAX_RETRIEVAL_DEPTH:
            raise ResourceLimitError(
                "retrieval_depth_limit_exceeded",
                object_reads=len(acquired),
                bytes_acquired=bytes_acquired,
            )
        if len(acquired) >= read_cap:
            raise ResourceLimitError(
                "retrieval_read_limit_exceeded",
                object_reads=len(acquired),
                bytes_acquired=bytes_acquired,
            )
        record, encoded_len = store.get(object_id)
        if (
            strategy == "typed_mandatory_evidence_closure"
            and parent_type is None
            and not acquired
            and record["object_type"] != "use_request"
        ):
            raise BenchmarkError("typed_root_type_invalid")
        if strategy == "typed_mandatory_evidence_closure" and parent_type is not None:
            permitted = ROLE_TYPES.get((parent_type, str(parent_role)))
            if permitted is None or record["object_type"] not in permitted:
                raise BenchmarkError("typed_role_target_invalid")
        acquired[object_id] = record
        bytes_acquired += encoded_len
        if strategy == "full_bounded_store":
            continue
        if strategy == "literal_all_reference_traversal":
            for target in _follow_refs(record, required_only=False):
                queue.append((target, depth + 1, None, None))
        elif strategy == "generic_dependency_aware":
            for target in _follow_refs(record, required_only=True):
                queue.append((target, depth + 1, None, None))
        else:
            mandatory = MANDATORY_ROLES.get(record["object_type"], frozenset())
            refs_by_role: dict[str, dict[str, Any]] = {}
            for item in record["refs"]:
                if type(item) is not dict or set(item) != {"role", "target", "required"}:
                    raise BenchmarkError("typed_reference_shape_invalid")
                role = item["role"]
                if type(role) is not str or role in refs_by_role:
                    raise BenchmarkError("typed_reference_role_duplicate")
                if type(item["target"]) is not str or type(item["required"]) is not bool:
                    raise BenchmarkError("typed_reference_value_invalid")
                refs_by_role[role] = item
            if not mandatory.issubset(refs_by_role):
                raise BenchmarkError("typed_mandatory_role_missing")
            for role in sorted(mandatory):
                target = refs_by_role[role]["target"]
                queue.append((target, depth + 1, record["object_type"], role))
    return {
        "records": acquired,
        "object_reads": len(acquired),
        "bytes_acquired": bytes_acquired,
        "typed_contract_used": strategy == "typed_mandatory_evidence_closure",
    }


class BoundedCache:
    def __init__(self) -> None:
        self._values: dict[tuple[Any, ...], int] = {}

    def get(self, key: tuple[Any, ...]) -> int | None:
        return self._values.get(key)

    def put(self, key: tuple[Any, ...], value: int) -> None:
        if key not in self._values and len(self._values) >= MAX_CACHE_ENTRIES:
            raise ResourceLimitError("cache_entry_limit_exceeded")
        self._values[key] = value

    def retained_bytes(self) -> int:
        return sum(len(canonical_json({"key": list(key), "value": value})) for key, value in self._values.items())

    def __len__(self) -> int:
        return len(self._values)


def exact_cache_key(workload: Workload, value: tuple[int, int, int], *, prime: bool) -> tuple[Any, ...]:
    dependency = workload.prime_dependency if prime else workload.target_dependency
    scope = workload.prime_scope if prime else workload.target_scope
    return (
        OPERATION_ID,
        OPERATION_VERSION,
        CONTRACT_VERSION,
        CHECKER_VERSION,
        scope,
        dependency,
        *value,
    )


def semantic_cache_key(workload: Workload, value: tuple[int, int, int], *, prime: bool) -> tuple[Any, ...]:
    dependency = workload.prime_dependency if prime else workload.target_dependency
    scope = workload.prime_scope if prime else workload.target_scope
    return (
        OPERATION_ID,
        OPERATION_VERSION,
        CONTRACT_VERSION,
        CHECKER_VERSION,
        scope,
        dependency,
        value[0],
        value[1],
    )


def independent_expected_output(value: tuple[int, int, int]) -> int:
    if len(value) != 3 or any(type(item) is not int for item in value):
        raise BenchmarkError("oracle_input_invalid")
    return value[0] + value[1]


def _kernel(value: tuple[int, int, int], rounds: int) -> int:
    seed = canonical_json(list(value))
    digest = seed
    for _ in range(rounds):
        digest = hashlib.sha256(digest).digest()
    if len(digest) != 32:
        raise BenchmarkError("kernel_digest_invalid")
    return value[0] + value[1]


def _timed(function: Callable[[], Any]) -> tuple[Any, int]:
    started = time.perf_counter_ns()
    result = function()
    ended = time.perf_counter_ns()
    return result, ended - started


def _prime(
    workload: Workload,
    mode: str,
    exact_cache: BoundedCache,
    semantic_cache: BoundedCache,
    rounds: int,
) -> dict[str, Any]:
    started = time.perf_counter_ns()
    value = _kernel(workload.prime_input, rounds)
    if mode == "ordinary_exact_input_cache":
        exact_cache.put(exact_cache_key(workload, workload.prime_input, prime=True), value)
        kind = "exact_cache_prime"
    elif mode == "sufficiency_semantic_reuse":
        semantic_cache.put(semantic_cache_key(workload, workload.prime_input, prime=True), value)
        kind = "semantic_cache_prime"
    else:
        kind = "runtime_warmup_without_cache"
    return {
        "performed": True,
        "kind": kind,
        "operation_calls": 1,
        "duration_ns": time.perf_counter_ns() - started,
        "input": list(workload.prime_input),
    }


def _verify_acquired(
    acquired: Mapping[str, Mapping[str, Any]],
    named: Mapping[str, str],
    workload: Workload,
) -> dict[str, Any]:
    base = {
        "closure": "complete",
        "claim_valid": False,
        "original_execution_eligible": False,
        "exact_reuse_eligible": False,
        "sufficiency_reuse_eligible": False,
        "authentication_checks": 0,
    }
    missing = [name for name, object_id in named.items() if object_id not in acquired]
    if missing:
        return {**base, "closure": "missing", "reason": "mandatory_evidence_missing"}
    expected_types = {
        "claim": "sufficiency_claim",
        "evidence": "finite_evidence",
        "view": "authority_view",
        "permission": "permission",
        "policy": "policy",
        "input": "input_state",
        "availability": "retrieval_observation",
    }
    for name, expected_type in expected_types.items():
        if acquired[named[name]]["object_type"] != expected_type:
            return {**base, "closure": "contradictory", "reason": "mandatory_type_invalid"}
    claim = acquired[named["claim"]]
    evidence = acquired[named["evidence"]]
    view = acquired[named["view"]]
    permission = acquired[named["permission"]]
    policy = acquired[named["policy"]]
    input_record = acquired[named["input"]]
    availability = acquired[named["availability"]]
    claim_valid = claim["data"].get("claim_valid") is True
    evidence_valid = evidence["data"].get("verified") is True
    authentication_checks = 1
    authority_valid = not (
        view["data"].get("observer") != "observer:benchmark"
        or view["data"].get("scope") != workload.target_scope
        or permission["data"].get("assessment") != "affirmative"
        or permission["data"].get("scope") != workload.target_scope
        or policy["data"].get("scope") != workload.target_scope
    )
    authentication_checks += 1
    readiness_valid = not (
        availability["data"].get("observer") != "observer:benchmark"
        or availability["data"].get("scope") != workload.target_scope
        or availability["data"].get("integrity_verified") is not True
        or availability["data"].get("retained_for_invocation") is not True
    )
    input_valid = tuple(input_record["data"].get("input", ())) == workload.target_input
    if not input_valid:
        return {
            **base,
            "closure": "contradictory",
            "authentication_checks": authentication_checks,
            "reason": "input_binding_invalid",
        }
    base_eligible = authority_valid and readiness_valid
    if not authority_valid:
        reason = "authority_binding_invalid"
    elif not readiness_valid:
        reason = "readiness_invalid"
    elif not claim_valid:
        reason = "sufficiency_claim_rejected"
    elif not evidence_valid:
        reason = "evidence_not_verified"
    else:
        reason = "verified"
    sufficiency_valid = base_eligible and claim_valid and evidence_valid
    return {
        **base,
        "claim_valid": claim_valid and evidence_valid,
        "original_execution_eligible": base_eligible,
        "exact_reuse_eligible": base_eligible,
        "sufficiency_reuse_eligible": sufficiency_valid,
        "authentication_checks": authentication_checks,
        "reason": reason,
    }


def execute_target(
    workload: Workload,
    mode: str,
    strategy: str,
    *,
    path: str,
    rounds: int,
    read_cap: int = MAX_OBJECT_READS,
) -> dict[str, Any]:
    if mode not in REUSE_MODES or strategy not in RETRIEVAL_STRATEGIES or path not in PATHS:
        raise BenchmarkError("run_coordinate_invalid")
    exact_cache = BoundedCache()
    semantic_cache = BoundedCache()
    priming = {
        "performed": False,
        "kind": "none",
        "operation_calls": 0,
        "duration_ns": 0,
        "input": None,
    }
    if path == "warm":
        priming = _prime(workload, mode, exact_cache, semantic_cache, rounds)

    phase_ns = {name: 0 for name in PHASES}
    prepared, phase_ns["preparation"] = _timed(lambda: build_fixture(workload))
    store, root_id, named = prepared
    representation, phase_ns["representation_guard"] = _timed(
        lambda: (workload.target_input[0], workload.target_input[1])
    )
    retrieval_started = time.perf_counter_ns()
    try:
        retrieval = acquire_objects(store, root_id, strategy, read_cap=read_cap)
        phase_ns["retrieval"] = time.perf_counter_ns() - retrieval_started
    except ResourceLimitError as exc:
        phase_ns["retrieval"] = time.perf_counter_ns() - retrieval_started
        return {
            "verdict": "resource_exhausted",
            "output": None,
            "representation": list(representation),
            "phase_ns": phase_ns,
            "priming": priming,
            "counters": {
                "operation_calls": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "cache_lookups": 0,
                "invalidations": 0,
                "object_reads": exc.object_reads,
                "bytes_acquired": exc.bytes_acquired,
                "integrity_checks": exc.object_reads,
                "authentication_checks": 0,
                "freshness_checks": 0,
                "authority_view_deliveries": 0,
                "correction_calls": 0,
                "cache_entries": len(exact_cache) + len(semantic_cache),
                "retained_cache_bytes": exact_cache.retained_bytes() + semantic_cache.retained_bytes(),
            },
            "closure": "resource_exhausted",
            "typed_contract_used": strategy == "typed_mandatory_evidence_closure",
        }

    acquired = retrieval["records"]
    integrity_ok, phase_ns["integrity"] = _timed(
        lambda: all(_verify_record(record) for record in acquired.values())
    )
    if not integrity_ok:
        raise BenchmarkError("acquired_integrity_invalid")
    verification, phase_ns["authentication"] = _timed(
        lambda: _verify_acquired(acquired, named, workload)
    )
    freshness_ok, phase_ns["freshness"] = _timed(
        lambda: acquired.get(named["view"], {}).get("data", {}).get("tick") == 5
    )
    cache_hits = 0
    cache_misses = 0
    cache_lookups = 0
    invalidations = 0
    result: int | None = None
    hit = False
    route_eligible = {
        "direct_computation": verification["original_execution_eligible"],
        "ordinary_exact_input_cache": verification["exact_reuse_eligible"],
        "sufficiency_semantic_reuse": verification["sufficiency_reuse_eligible"],
    }[mode]

    def cache_phase() -> None:
        nonlocal result, hit, cache_hits, cache_misses, cache_lookups, invalidations
        if not route_eligible or not freshness_ok or mode == "direct_computation":
            return
        cache_lookups = 1
        if mode == "ordinary_exact_input_cache":
            key = exact_cache_key(workload, workload.target_input, prime=False)
            result = exact_cache.get(key)
        else:
            key = semantic_cache_key(workload, workload.target_input, prime=False)
            result = semantic_cache.get(key)
        if result is None:
            cache_misses = 1
            if path == "warm" and workload.workload_id in {
                "changed_dependencies",
                "changed_operation_scope",
            }:
                invalidations = 1
        else:
            cache_hits = 1
            hit = True

    _, phase_ns["cache_lookup_maintenance"] = _timed(cache_phase)
    operation_calls = 0

    def execution_phase() -> None:
        nonlocal result, operation_calls
        if not verification["original_execution_eligible"] or not freshness_ok or hit:
            return
        result = _kernel(workload.target_input, rounds)
        operation_calls = 1
        if mode == "ordinary_exact_input_cache":
            exact_cache.put(exact_cache_key(workload, workload.target_input, prime=False), result)
        elif mode == "sufficiency_semantic_reuse" and verification[
            "sufficiency_reuse_eligible"
        ]:
            semantic_cache.put(semantic_cache_key(workload, workload.target_input, prime=False), result)

    _, phase_ns["execution"] = _timed(execution_phase)

    def correction_phase() -> None:
        if result is not None and result != independent_expected_output(workload.target_input):
            raise BenchmarkError("operation_output_mismatch")

    _, phase_ns["correction"] = _timed(correction_phase)
    if not verification["original_execution_eligible"]:
        verdict = "rejected_use"
    elif not freshness_ok:
        verdict = "unresolved_pending_evidence"
    elif hit:
        verdict = "authorized_reuse"
    else:
        verdict = "authorized_direct_computation"
    return {
        "verdict": verdict,
        "output": result,
        "representation": list(representation),
        "phase_ns": phase_ns,
        "priming": priming,
        "counters": {
            "operation_calls": operation_calls,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "cache_lookups": cache_lookups,
            "invalidations": invalidations,
            "object_reads": retrieval["object_reads"],
            "bytes_acquired": retrieval["bytes_acquired"],
            "integrity_checks": retrieval["object_reads"],
            "authentication_checks": verification["authentication_checks"],
            "freshness_checks": 1,
            "authority_view_deliveries": int(named["view"] in acquired),
            "correction_calls": int(result is not None),
            "cache_entries": len(exact_cache) + len(semantic_cache),
            "retained_cache_bytes": exact_cache.retained_bytes() + semantic_cache.retained_bytes(),
        },
        "closure": verification["closure"],
        "typed_contract_used": retrieval["typed_contract_used"],
    }


def expected_behavior(workload: Workload, mode: str, path: str) -> dict[str, Any]:
    semantic_hit = workload.workload_id in {
        "identical_inputs",
        "different_inputs_equivalent_operation",
        "noninterference",
    } and workload.claim_valid
    exact_hit = workload.workload_id in {"identical_inputs", "noninterference"}
    hit = path == "warm" and (
        (mode == "ordinary_exact_input_cache" and exact_hit)
        or (mode == "sufficiency_semantic_reuse" and semantic_hit)
    )
    return {
        "verdict": "authorized_reuse" if hit else "authorized_direct_computation",
        "output": independent_expected_output(workload.target_input),
        "cache_hits": int(hit),
        "operation_calls": 0 if hit else 1,
    }


def _statistics(samples: Sequence[int]) -> dict[str, int]:
    if len(samples) < MIN_SAMPLES or any(type(item) is not int or item < 0 for item in samples):
        raise BenchmarkError("timing_samples_invalid")
    return {
        "min": min(samples),
        "median": int(statistics.median(samples)),
        "max": max(samples),
    }


def _new_accumulator(workload: Workload, mode: str, strategy: str, path: str) -> dict[str, Any]:
    return {
        "workload_id": workload.workload_id,
        "reuse_mode": mode,
        "retrieval_strategy": strategy,
        "path": path,
        "duration_samples_ns": [],
        "phase_duration_samples_ns": {phase: [] for phase in PHASES},
        "priming_duration_samples_ns": [],
        "sample_order_indices": [],
        "observations": [],
    }


def _finalize_run(accumulator: Mapping[str, Any]) -> dict[str, Any]:
    observations = accumulator["observations"]
    if len(observations) != MIN_SAMPLES:
        raise BenchmarkError("observation_count_invalid")
    first = observations[0]
    stable_fields = ("verdict", "output", "representation", "counters", "closure", "typed_contract_used")
    for observation in observations[1:]:
        if any(observation[field] != first[field] for field in stable_fields):
            raise BenchmarkError("nondeterministic_non_timing_result")
    run = {
        "reuse_mode": accumulator["reuse_mode"],
        "retrieval_strategy": accumulator["retrieval_strategy"],
        "path": accumulator["path"],
        "verdict": first["verdict"],
        "output": first["output"],
        "closure": first["closure"],
        "typed_contract_used": first["typed_contract_used"],
        **first["counters"],
        "counter_units": {
            "bytes_acquired": "canonical_local_fixture_bytes",
            "retained_cache_bytes": "canonical_cache_entry_bytes",
            "operation_calls": "calls",
            "object_reads": "objects",
        },
        "duration_samples_ns": list(accumulator["duration_samples_ns"]),
        "duration_statistics_ns": _statistics(accumulator["duration_samples_ns"]),
        "phase_duration_samples_ns": copy.deepcopy(accumulator["phase_duration_samples_ns"]),
        "phase_statistics_ns": {
            phase: _statistics(samples)
            for phase, samples in accumulator["phase_duration_samples_ns"].items()
        },
        "priming_action": {
            "performed": first["priming"]["performed"],
            "kind": first["priming"]["kind"],
            "operation_calls_per_sample": first["priming"]["operation_calls"],
            "input": first["priming"]["input"],
            "duration_samples_ns": list(accumulator["priming_duration_samples_ns"]),
        },
        "sample_order_indices": list(accumulator["sample_order_indices"]),
    }
    return run


def run_matrix(*, warmups: int, samples: int, kernel_rounds: int) -> list[dict[str, Any]]:
    if warmups < MIN_WARMUPS or samples != MIN_SAMPLES:
        raise BenchmarkError("measurement_repetition_contract_invalid")
    if kernel_rounds <= 0 or kernel_rounds > MAX_KERNEL_ROUNDS:
        raise BenchmarkError("kernel_rounds_invalid")
    cells = [
        (workload, mode, strategy)
        for workload in WORKLOADS
        for mode in REUSE_MODES
        for strategy in RETRIEVAL_STRATEGIES
    ]
    if len(cells) != 84:
        raise BenchmarkError("matrix_cell_count_invalid")
    accumulators = {
        (workload.workload_id, mode, strategy, path): _new_accumulator(workload, mode, strategy, path)
        for workload, mode, strategy in cells
        for path in PATHS
    }
    total_rounds = warmups + samples
    for round_index in range(total_rounds):
        rotation = (round_index * 17) % len(cells)
        ordered = cells[rotation:] + cells[:rotation]
        order_counter = 0
        for cell_index, (workload, mode, strategy) in enumerate(ordered):
            paths = PATHS if (round_index + cell_index) % 2 == 0 else tuple(reversed(PATHS))
            for path in paths:
                observation = execute_target(
                    workload,
                    mode,
                    strategy,
                    path=path,
                    rounds=kernel_rounds,
                )
                expected = expected_behavior(workload, mode, path)
                for field in ("verdict", "output"):
                    if observation[field] != expected[field]:
                        raise BenchmarkError(
                            f"expected_outcome_mismatch:{workload.workload_id}:{mode}:{strategy}:{path}:{field}"
                        )
                if observation["counters"]["cache_hits"] != expected["cache_hits"]:
                    raise BenchmarkError("expected_cache_hit_mismatch")
                if observation["counters"]["operation_calls"] != expected["operation_calls"]:
                    raise BenchmarkError("expected_operation_call_mismatch")
                total_ns = sum(observation["phase_ns"].values())
                if round_index >= warmups:
                    key = (workload.workload_id, mode, strategy, path)
                    accumulator = accumulators[key]
                    accumulator["duration_samples_ns"].append(total_ns)
                    for phase in PHASES:
                        accumulator["phase_duration_samples_ns"][phase].append(
                            observation["phase_ns"][phase]
                        )
                    accumulator["priming_duration_samples_ns"].append(
                        observation["priming"]["duration_ns"]
                    )
                    accumulator["sample_order_indices"].append(order_counter)
                    accumulator["observations"].append(observation)
                order_counter += 1
    workload_results: list[dict[str, Any]] = []
    for workload in WORKLOADS:
        runs = [
            _finalize_run(accumulators[(workload.workload_id, mode, strategy, path)])
            for mode in REUSE_MODES
            for strategy in RETRIEVAL_STRATEGIES
            for path in PATHS
        ]
        workload_result = {
            "workload_id": workload.workload_id,
            "expected_oracle": {
                "target_input": list(workload.target_input),
                "expected_output": None if not workload.claim_valid else independent_expected_output(workload.target_input),
                "claim_valid": workload.claim_valid,
            },
            "runs": runs,
        }
        if workload.workload_id == "noninterference":
            verdicts = {run["verdict"] for run in runs}
            outputs = {run["output"] for run in runs}
            workload_result["noninterference_invariant_holds"] = verdicts.issubset(
                {"authorized_direct_computation", "authorized_reuse"}
            ) and outputs == {3}
        workload_results.append(workload_result)
    return workload_results


def resource_cap_probe(kernel_rounds: int) -> dict[str, Any]:
    workload = next(item for item in WORKLOADS if item.workload_id == "noninterference")
    full = execute_target(
        workload,
        "direct_computation",
        "full_bounded_store",
        path="cold",
        rounds=kernel_rounds,
        read_cap=8,
    )
    typed = execute_target(
        workload,
        "direct_computation",
        "typed_mandatory_evidence_closure",
        path="cold",
        rounds=kernel_rounds,
        read_cap=8,
    )
    if full["verdict"] != "resource_exhausted" or typed["verdict"] != "authorized_direct_computation":
        raise BenchmarkError("resource_cap_probe_invalid")
    return {
        "read_cap": 8,
        "full_bounded_store": full["verdict"],
        "typed_mandatory_evidence_closure": typed["verdict"],
        "underlying_claim_refuted": False,
    }


def model_selector_accounting() -> dict[str, Any]:
    try:
        from ilc_core.sufficiency.model_selector import (
            Candidate,
            EligibilityDecision,
            LocalFixtureModelBackend,
            ModelProposal,
            SelectionRequest,
            select_candidate,
        )
    except ImportError:
        return {"included": False, "reason": "model_selector_unavailable"}
    candidate = Candidate(
        "candidate:benchmark",
        "1",
        OPERATION_ID,
        "policy:fixture:v1",
        ("evidence:fixture",),
    )
    request = SelectionRequest(
        "request:benchmark",
        OPERATION_ID,
        "policy:fixture:v1",
        5,
    )
    backend = LocalFixtureModelBackend(
        ModelProposal("candidate:benchmark", "1", {"confidence": 0.5}, 7, 11)
    )

    def eligible(_candidate: Candidate, _request: SelectionRequest) -> EligibilityDecision:
        return EligibilityDecision(True, "fixture_eligible", ("evidence:fixture",), 3)

    started = time.perf_counter_ns()
    result = select_candidate(
        candidates=(candidate,),
        request=request,
        backend=backend,
        evaluate_eligibility=eligible,
    )
    return {
        "included": True,
        "separate_from_matrix": True,
        "outcome": result["outcome"],
        "duration_ns": time.perf_counter_ns() - started,
        "overhead": result["overhead"],
    }


def build_results(*, warmups: int, samples: int, kernel_rounds: int) -> dict[str, Any]:
    workload_results = run_matrix(
        warmups=warmups,
        samples=samples,
        kernel_rounds=kernel_rounds,
    )
    run_count = sum(len(workload["runs"]) for workload in workload_results)
    if run_count != 168:
        raise BenchmarkError("run_record_count_invalid")
    return {
        "schema_version": SCHEMA_VERSION,
        "benchmark_version": BENCHMARK_VERSION,
        "scope": "bounded_local_fixture_only",
        "matrix": {
            "workloads": len(WORKLOADS),
            "reuse_modes": list(REUSE_MODES),
            "retrieval_strategies": list(RETRIEVAL_STRATEGIES),
            "logical_cells": 84,
            "paths_per_cell": 2,
            "run_records": run_count,
        },
        "measurement_protocol": {
            "clock": "time.perf_counter_ns",
            "warmups_discarded": warmups,
            "measured_samples_per_path": samples,
            "cell_rotation_stride": 17,
            "path_order_alternates": True,
            "phase_intervals_exclusive": True,
            "kernel_rounds": kernel_rounds,
            "timing_interpretation": "descriptive_for_this_host_and_run_only",
        },
        "environment": {
            "python": sys.version.split()[0],
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "instrumentation_boundaries": {
            "bytes_acquired": "canonical JSON bytes of locally acquired fixture objects",
            "retained_cache_bytes": "canonical JSON bytes of retained key/value cache entries",
            "process_memory_measured": False,
            "network_bytes_measured": False,
            "energy_measured": False,
            "priming_excluded_from_target_duration": True,
        },
        "resource_limits": {
            "max_store_objects": MAX_STORE_OBJECTS,
            "max_object_bytes": MAX_OBJECT_BYTES,
            "max_references_per_object": MAX_REFERENCES_PER_OBJECT,
            "max_retrieval_depth": MAX_RETRIEVAL_DEPTH,
            "max_object_reads": MAX_OBJECT_READS,
            "max_cache_entries": MAX_CACHE_ENTRIES,
            "max_output_bytes": MAX_OUTPUT_BYTES,
        },
        "workloads": workload_results,
        "resource_cap_probe": resource_cap_probe(kernel_rounds),
        "model_selector_fixture": model_selector_accounting(),
        "non_claims": [
            "no_network_performance_claim",
            "no_process_memory_claim",
            "no_energy_claim",
            "no_distributed_safety_claim",
            "no_production_authority_claim",
            "no_transferable_speedup_claim",
        ],
    }


def _find_run(
    results: Mapping[str, Any],
    workload_id: str,
    mode: str,
    strategy: str,
    path: str,
) -> Mapping[str, Any]:
    workload = next(item for item in results["workloads"] if item["workload_id"] == workload_id)
    return next(
        item
        for item in workload["runs"]
        if item["reuse_mode"] == mode
        and item["retrieval_strategy"] == strategy
        and item["path"] == path
    )


def build_summary(results: Mapping[str, Any]) -> str:
    strategy = "typed_mandatory_evidence_closure"
    direct = _find_run(
        results,
        "different_inputs_equivalent_operation",
        "direct_computation",
        strategy,
        "warm",
    )
    exact = _find_run(
        results,
        "different_inputs_equivalent_operation",
        "ordinary_exact_input_cache",
        strategy,
        "warm",
    )
    semantic = _find_run(
        results,
        "different_inputs_equivalent_operation",
        "sufficiency_semantic_reuse",
        strategy,
        "warm",
    )
    local_timing_advantage = (
        semantic["duration_statistics_ns"]["median"] < direct["duration_statistics_ns"]["median"]
    )
    return "\n".join(
        [
            "# Sufficiency Benchmark 00 Summary",
            "",
            "This is a bounded local-fixture benchmark. Exact counters are the primary result; timing is descriptive for this host and run only.",
            "",
            "## Different inputs, equivalent operation",
            "",
            f"- Direct operation calls: {direct['operation_calls']}",
            f"- Exact-input cache hits / operation calls: {exact['cache_hits']} / {exact['operation_calls']}",
            f"- Semantic cache hits / operation calls: {semantic['cache_hits']} / {semantic['operation_calls']}",
            f"- Local median timing advantage observed: {str(local_timing_advantage).lower()}",
            "",
            "## Noninterference",
            "",
            "Unrelated content did not change the sufficient-resource substantive result. Under a low read cap, bulk acquisition exhausted its budget while typed closure completed; this is a resource outcome, not claim refutation.",
            "",
            "## Negative and bounded results",
            "",
            "- Low-reuse and invalid-claim workloads do not promise a reuse advantage.",
            "- Process memory, network traffic, and energy were not measured.",
            "- No transferable ILC, distributed-system, GPU, or large-model speedup is claimed.",
            "",
        ]
    )


def _atomic_write(path: Path, payload: bytes) -> None:
    if len(payload) > MAX_OUTPUT_BYTES:
        raise ResourceLimitError("output_bytes_limit_exceeded")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def write_outputs(results: Mapping[str, Any], output_dir: Path) -> tuple[Path, Path]:
    results_path = output_dir / "benchmark_results.json"
    summary_path = output_dir / "benchmark_summary.md"
    encoded = canonical_json(results) + b"\n"
    _atomic_write(results_path, encoded)
    _atomic_write(summary_path, build_summary(results).encode("utf-8"))
    return results_path, summary_path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--warmups", type=int, default=MIN_WARMUPS)
    parser.add_argument("--samples", type=int, default=MIN_SAMPLES)
    parser.add_argument("--kernel-rounds", type=int, default=DEFAULT_KERNEL_ROUNDS)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    results = build_results(
        warmups=args.warmups,
        samples=args.samples,
        kernel_rounds=args.kernel_rounds,
    )
    results_path, summary_path = write_outputs(results, args.output_dir)
    print(f"workloads={len(results['workloads'])}")
    print(f"logical_cells={results['matrix']['logical_cells']}")
    print(f"run_records={results['matrix']['run_records']}")
    print(f"results={results_path}")
    print(f"summary={summary_path}")
    print("sufficiency_benchmark_verdict=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
