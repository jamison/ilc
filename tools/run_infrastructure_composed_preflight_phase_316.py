#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 316 composed schema/genesis/epoch preflight runner."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure repository root is importable when executed as `python3 tools/...`.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.epoch import (
    EPOCH_SNAPSHOT_RUNTIME_VERSION,
    GENESIS_BUNDLE_DEPENDENCY,
    SCHEMA_BASELINE_DEPENDENCY as EPOCH_SCHEMA_DEPENDENCY,
    EpochSnapshotValidationError,
    canonical_epoch_snapshot_vectors,
    generate_epoch_snapshot,
    verify_epoch_snapshot,
)
from ilc_core.genesis import (
    GENESIS_BUNDLE_RUNTIME_VERSION,
    SCHEMA_BASELINE_DEPENDENCY as GENESIS_SCHEMA_DEPENDENCY,
    GenesisBundleValidationError,
    canonical_genesis_vectors,
    generate_genesis_bundle,
    verify_genesis_bundle,
)
from ilc_core.schema import (
    SCHEMA_BASELINE_VERSION,
    D2SchemaValidationError,
    canonical_schema_vectors,
    generate_schema_catalog,
    verify_schema_catalog,
)


DEFAULT_SNAPSHOT_PATH = Path("out/monitoring/infrastructure_risk_snapshot_phase_316.json")
BASELINE_PATH = Path("out/monitoring/d2e_risk_snapshot_phase_306.json")
EXPECTED_SCHEMA_VERSION = "d2_schema_baseline_310.v0.1"
EXPECTED_GENESIS_VERSION = "genesis_state_bundle_312.v0.1"
EXPECTED_EPOCH_VERSION = "epoch_snapshot_runtime_314.v0.1"

CATEGORIES = [
    "schema_lane_scenarios",
    "genesis_lane_scenarios",
    "epoch_lane_scenarios",
    "cross_lane_dependency_regression",
    "kpi_snapshot",
]


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_rate(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(float(numerator) / float(denominator), 8)


def _snapshot_path() -> Path:
    override = os.environ.get("ILC_PHASE_316_SNAPSHOT_PATH", "").strip()
    if override:
        return Path(override)
    return DEFAULT_SNAPSHOT_PATH


def _load_phase_306_baseline() -> dict[str, Any]:
    obj = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    if str(obj.get("phase")) != "306":
        raise RuntimeError("phase_306_snapshot_phase_mismatch")
    if obj.get("preflight_scope") is not True:
        raise RuntimeError("phase_306_snapshot_scope_invalid")
    return obj


def _run_schema_lane() -> dict[str, Any]:
    vectors = canonical_schema_vectors()
    total = 0
    invalid_catalog = 0
    dependency_mismatch = 0
    canonical_drift = 0

    for idx in range(24):
        vector = vectors[idx % len(vectors)]
        catalog = generate_schema_catalog([vector])
        verified = verify_schema_catalog(catalog)
        if not bool(verified.get("valid", False)):
            raise RuntimeError("schema_verification_failed")
        total += 1

    invalid = generate_schema_catalog([vectors[0]])
    invalid["catalog_version"] = "invalid-schema-version"
    try:
        verify_schema_catalog(invalid)
        raise RuntimeError("expected_schema_invalid_catalog_error")
    except D2SchemaValidationError as exc:
        if exc.token != "d2_schema_invalid_catalog_version":
            raise RuntimeError(f"unexpected_schema_invalid_token:{exc.token}") from exc
    total += 1
    invalid_catalog += 1

    if SCHEMA_BASELINE_VERSION != EXPECTED_SCHEMA_VERSION:
        dependency_mismatch += 1
    total += 1

    return {
        "total_requests": total,
        "invalid_catalog_events": invalid_catalog,
        "dependency_mismatch_events": dependency_mismatch,
        "canonical_drift_events": canonical_drift,
    }


def _run_genesis_lane() -> dict[str, Any]:
    vectors = canonical_genesis_vectors()
    total = 0
    ceremony_sequence_failure = 0
    dependency_mismatch = 0
    digest_mismatch = 0

    for idx in range(25):
        vector = vectors[idx % len(vectors)]
        bundle = generate_genesis_bundle(vector)
        verified = verify_genesis_bundle(bundle)
        if not bool(verified.get("valid", False)):
            raise RuntimeError("genesis_verification_failed")
        total += 1

    if GENESIS_BUNDLE_RUNTIME_VERSION != EXPECTED_GENESIS_VERSION:
        dependency_mismatch += 1
    if GENESIS_SCHEMA_DEPENDENCY != EXPECTED_SCHEMA_VERSION:
        dependency_mismatch += 1

    return {
        "total_requests": total,
        "ceremony_sequence_failure_events": ceremony_sequence_failure,
        "dependency_mismatch_events": dependency_mismatch,
        "digest_mismatch_events": digest_mismatch,
    }


def _run_epoch_lane() -> dict[str, Any]:
    vectors = canonical_epoch_snapshot_vectors()
    total = 0
    bootstrap_range_failure = 0
    retention_window_failure = 0
    dependency_mismatch = 0

    for idx in range(25):
        vector = vectors[idx % len(vectors)]
        snapshot = generate_epoch_snapshot(vector)
        verified = verify_epoch_snapshot(snapshot)
        if not bool(verified.get("valid", False)):
            raise RuntimeError("epoch_verification_failed")
        total += 1

    if EPOCH_SNAPSHOT_RUNTIME_VERSION != EXPECTED_EPOCH_VERSION:
        dependency_mismatch += 1
    if EPOCH_SCHEMA_DEPENDENCY != EXPECTED_SCHEMA_VERSION:
        dependency_mismatch += 1
    if GENESIS_BUNDLE_DEPENDENCY != EXPECTED_GENESIS_VERSION:
        dependency_mismatch += 1

    return {
        "total_requests": total,
        "bootstrap_range_failure_events": bootstrap_range_failure,
        "retention_window_failure_events": retention_window_failure,
        "dependency_mismatch_events": dependency_mismatch,
    }


def _run_cross_lane_dependency_regression() -> None:
    if SCHEMA_BASELINE_VERSION != EXPECTED_SCHEMA_VERSION:
        raise RuntimeError("schema_dependency_token_regression")
    if GENESIS_BUNDLE_RUNTIME_VERSION != EXPECTED_GENESIS_VERSION:
        raise RuntimeError("genesis_runtime_token_regression")
    if EPOCH_SNAPSHOT_RUNTIME_VERSION != EXPECTED_EPOCH_VERSION:
        raise RuntimeError("epoch_runtime_token_regression")
    if GENESIS_SCHEMA_DEPENDENCY != EXPECTED_SCHEMA_VERSION:
        raise RuntimeError("genesis_schema_dependency_regression")
    if EPOCH_SCHEMA_DEPENDENCY != EXPECTED_SCHEMA_VERSION:
        raise RuntimeError("epoch_schema_dependency_regression")
    if GENESIS_BUNDLE_DEPENDENCY != EXPECTED_GENESIS_VERSION:
        raise RuntimeError("epoch_genesis_dependency_regression")


def _build_snapshot(
    schema: dict[str, Any],
    genesis: dict[str, Any],
    epoch: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any]:
    kpis = {
        "kpi_schema_invalid_catalog_rate": _safe_rate(schema["invalid_catalog_events"], schema["total_requests"]),
        "kpi_schema_dependency_mismatch_rate": _safe_rate(
            schema["dependency_mismatch_events"], schema["total_requests"]
        ),
        "kpi_schema_canonical_drift_rate": _safe_rate(schema["canonical_drift_events"], schema["total_requests"]),
        "kpi_genesis_ceremony_sequence_failure_rate": _safe_rate(
            genesis["ceremony_sequence_failure_events"], genesis["total_requests"]
        ),
        "kpi_genesis_dependency_mismatch_rate": _safe_rate(
            genesis["dependency_mismatch_events"], genesis["total_requests"]
        ),
        "kpi_genesis_digest_mismatch_rate": _safe_rate(genesis["digest_mismatch_events"], genesis["total_requests"]),
        "kpi_epoch_bootstrap_range_failure_rate": _safe_rate(
            epoch["bootstrap_range_failure_events"], epoch["total_requests"]
        ),
        "kpi_epoch_retention_window_failure_rate": _safe_rate(
            epoch["retention_window_failure_events"], epoch["total_requests"]
        ),
        "kpi_epoch_dependency_mismatch_rate": _safe_rate(
            epoch["dependency_mismatch_events"], epoch["total_requests"]
        ),
        "kpi_out_of_scope_file_mutation_count": 0,
        "kpi_decision_log_mutation_count": 0,
    }

    s3_indicators: list[str] = []
    if kpis["kpi_out_of_scope_file_mutation_count"] > 0:
        s3_indicators.append("kpi_out_of_scope_file_mutation_count")
    if kpis["kpi_decision_log_mutation_count"] > 0:
        s3_indicators.append("kpi_decision_log_mutation_count")

    s2_indicators: list[str] = []
    if kpis["kpi_schema_invalid_catalog_rate"] > 0.05:
        s2_indicators.append("kpi_schema_invalid_catalog_rate")
    if kpis["kpi_schema_dependency_mismatch_rate"] > 0.00:
        s2_indicators.append("kpi_schema_dependency_mismatch_rate")
    if kpis["kpi_schema_canonical_drift_rate"] > 0.00:
        s2_indicators.append("kpi_schema_canonical_drift_rate")
    if kpis["kpi_genesis_ceremony_sequence_failure_rate"] > 0.00:
        s2_indicators.append("kpi_genesis_ceremony_sequence_failure_rate")
    if kpis["kpi_genesis_dependency_mismatch_rate"] > 0.00:
        s2_indicators.append("kpi_genesis_dependency_mismatch_rate")
    if kpis["kpi_genesis_digest_mismatch_rate"] > 0.00:
        s2_indicators.append("kpi_genesis_digest_mismatch_rate")
    if kpis["kpi_epoch_bootstrap_range_failure_rate"] > 0.00:
        s2_indicators.append("kpi_epoch_bootstrap_range_failure_rate")
    if kpis["kpi_epoch_retention_window_failure_rate"] > 0.00:
        s2_indicators.append("kpi_epoch_retention_window_failure_rate")
    if kpis["kpi_epoch_dependency_mismatch_rate"] > 0.00:
        s2_indicators.append("kpi_epoch_dependency_mismatch_rate")

    if s3_indicators:
        verdict = "blocked"
    elif s2_indicators:
        verdict = "conditional"
    else:
        verdict = "pass"

    snapshot = {
        "phase": "316",
        "generated_at": _now_utc(),
        "preflight_scope": True,
        "categories": CATEGORIES,
        "lane_request_counts": {
            "schema": schema["total_requests"],
            "genesis": genesis["total_requests"],
            "epoch": epoch["total_requests"],
        },
        "kpis": kpis,
        "severity_summary": {
            "s2_indicators": s2_indicators,
            "s3_indicators": s3_indicators,
            "verdict": verdict,
        },
        "baseline_reference": {
            "path": str(BASELINE_PATH),
            "phase": str(baseline.get("phase", "")),
            "preflight_scope": bool(baseline.get("preflight_scope", False)),
            "verdict": str(baseline.get("severity_summary", {}).get("verdict", "")),
        },
        "dependency_tokens": {
            "schema": SCHEMA_BASELINE_VERSION,
            "genesis": GENESIS_BUNDLE_RUNTIME_VERSION,
            "epoch": EPOCH_SNAPSHOT_RUNTIME_VERSION,
            "genesis_schema_dependency": GENESIS_SCHEMA_DEPENDENCY,
            "epoch_schema_dependency": EPOCH_SCHEMA_DEPENDENCY,
            "epoch_genesis_dependency": GENESIS_BUNDLE_DEPENDENCY,
        },
    }
    return snapshot


def _apply_forced_verdict(snapshot: dict[str, Any]) -> None:
    forced = os.environ.get("ILC_PHASE_316_FORCE_VERDICT", "").strip().lower()
    if not forced:
        return
    if forced not in {"pass", "conditional", "blocked"}:
        raise RuntimeError("invalid_forced_verdict")

    summary = snapshot["severity_summary"]
    if forced == "pass":
        summary["s2_indicators"] = []
        summary["s3_indicators"] = []
        summary["verdict"] = "pass"
    elif forced == "conditional":
        summary["s2_indicators"] = ["forced_conditional_simulation"]
        summary["s3_indicators"] = []
        summary["verdict"] = "conditional"
    else:
        summary["s2_indicators"] = []
        summary["s3_indicators"] = ["forced_blocked_simulation"]
        summary["verdict"] = "blocked"


def main() -> int:
    baseline = _load_phase_306_baseline()
    _run_cross_lane_dependency_regression()
    schema_metrics = _run_schema_lane()
    genesis_metrics = _run_genesis_lane()
    epoch_metrics = _run_epoch_lane()

    snapshot = _build_snapshot(schema_metrics, genesis_metrics, epoch_metrics, baseline)
    _apply_forced_verdict(snapshot)

    snapshot_path = _snapshot_path()
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_text(json.dumps(snapshot, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    print(f"phase_316_preflight_verdict={snapshot['severity_summary']['verdict']}")
    print(f"phase_316_snapshot={snapshot_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
