from __future__ import annotations

import importlib.util
import json
from functools import lru_cache
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPO_ROOT / "tools" / "rc_frontier_gap_audit.py"
JSON_ARTIFACT = REPO_ROOT / "docs" / "specs" / "ilc_rc_frontier_gap_audit_1250_fix1_v0.1.json"
MARKDOWN_ARTIFACT = REPO_ROOT / "docs" / "specs" / "ilc_rc_frontier_gap_audit_1250_fix1_v0.1.md"


@lru_cache(maxsize=1)
def _tool():
    spec = importlib.util.spec_from_file_location("rc_frontier_gap_audit", TOOL_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def _audit() -> dict:
    return _tool().build_audit(REPO_ROOT)


def _finding(finding_id: str) -> dict:
    for item in _audit()["findings"]:
        if item["finding_id"] == finding_id:
            return item
    raise AssertionError(f"missing finding {finding_id}")


def test_phase_1250_fix1_required_tokens_present() -> None:
    audit = _audit()

    assert audit["version"] == "rc_frontier_gap_audit_1250_fix1.v0.1"
    assert "phase_1250_fix1_rc_frontier_gap_audit_complete" in audit["audit_scope"]["tokens"]
    assert "phase_1250_fix1_improved_gemini_gap_study_rerun" in audit["audit_scope"]["tokens"]


def test_current_canon_reconciles_stale_gap_claims() -> None:
    canon = _audit()["current_canon"]

    assert canon["cdl_086"]["status"] == "ratified"
    assert canon["cdl_086"]["classification"] == "resolved_stale"
    assert canon["cdl_087"]["status"] == "open_prelocked_not_ratified"
    assert canon["current_frontier"]["phase_1250_complete"] is True
    assert canon["current_frontier"]["phase_1251_next"] is True
    assert canon["current_frontier"]["phase_1252_sensitive"] is True
    assert canon["non_claims"]["v0_2_signing_deferred"] is True


def test_legacy_graph_delta_holes_are_not_current_blockers() -> None:
    legacy = _audit()["legacy_phase_scan"]
    finding = _finding("RCGAP-1250-FIX1-002")

    assert legacy["classification"] == "legacy_doc_hygiene"
    assert legacy["missing_graph_delta_closure_or_handoff_count"] > 0
    assert finding["classification"] == "legacy_doc_hygiene"
    assert finding["route"].startswith("Phase 1254")


def test_digest_truncation_candidates_are_phase_routed() -> None:
    digest_hits = _audit()["code_scans"]["digest_truncation_hits"]
    phase_1252 = _finding("RCGAP-1250-FIX1-003")
    phase_1253 = _finding("RCGAP-1250-FIX1-004")
    digest_sources = {hit["source_path"] for hit in digest_hits}

    assert digest_hits
    assert any(hit["classification"] == "route_to_phase_1252" for hit in digest_hits)
    assert any(hit["classification"] == "route_to_phase_1253" for hit in digest_hits)
    assert "ilc_core/ledger/settlement_verification.py" not in digest_sources
    assert "ilc_core/security/key_compromise_runtime.py" not in digest_sources
    assert "ilc_core/security/signer_lineage_runtime.py" not in digest_sources
    assert phase_1252["route"] == "Phase 1252 chain/crypto dependency inventory"
    assert phase_1253["route"] == "Phase 1253 TransportPrincipal and public-P2P substrate audit"


def test_rust_m5_fixme_is_preserved_as_transport_substrate_input() -> None:
    rust_hits = _audit()["code_scans"]["rust_fixme_hits"]
    finding = _finding("RCGAP-1250-FIX1-005")

    assert any("FIXME(M-5)" in hit["snippet"] for hit in rust_hits)
    assert finding["classification"] == "route_to_phase_1253"
    assert "ilc_consensus/src/node.rs" in finding["source_paths"]


def test_claimability_remains_sensitive_phase_1252_work() -> None:
    finding = _finding("RCGAP-1250-FIX1-006")

    assert finding["classification"] == "phase_1252_sensitive_gate"
    assert "Phase 1252" in finding["route"]
    assert any(
        path in finding["source_paths"]
        for path in (
            "ilc_core/ledger/ecu_ilc_lifecycle_runtime.py",
            "ilc_core/protocol/public_wallet_runtime.py",
        )
    )


def test_phase_1251_remains_recommended_next_phase() -> None:
    audit = _audit()
    finding = _finding("RCGAP-1250-FIX1-001")

    assert audit["recommended_next_phase"] == (
        "Phase 1251 - Gap 14 package CI gate, profile export audit, package-size measurement."
    )
    assert finding["classification"] == "route_to_phase_1251"


def test_export_json_is_canonical_and_historical_artifact_is_canonical() -> None:
    audit = _audit()
    exported = _tool().export_audit_json(audit)
    parsed = json.loads(exported)
    artifact = JSON_ARTIFACT.read_text(encoding="utf-8")
    artifact_parsed = json.loads(artifact)

    assert exported == json.dumps(parsed, allow_nan=False, indent=2, sort_keys=True) + "\n"
    assert artifact == json.dumps(
        artifact_parsed,
        allow_nan=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
    assert artifact_parsed["version"] == "rc_frontier_gap_audit_1250_fix1.v0.1"
    assert artifact_parsed["audit_scope"]["phase"] == "1250 Fix1"
    assert {
        finding["finding_id"] for finding in artifact_parsed["findings"]
    } == {f"RCGAP-1250-FIX1-{index:03d}" for index in range(1, 11)}


def test_markdown_artifact_records_non_claims_as_historical_snapshot() -> None:
    audit = _audit()
    markdown = _tool().export_audit_markdown(audit)
    artifact = MARKDOWN_ARTIFACT.read_text(encoding="utf-8")

    assert "# ILC RC Frontier Gap Audit 1250 Fix1 v0.1" in artifact
    assert "phase_1250_fix1_rc_frontier_gap_audit_complete" in artifact
    assert "no_public_rc_claim" in artifact
    assert "graph_delta=support_only:tools/rc_frontier_gap_audit.py -> validation" in artifact
    assert "no_public_rc_claim" in markdown
    assert "graph_delta=support_only:tools/rc_frontier_gap_audit.py -> validation" in markdown
