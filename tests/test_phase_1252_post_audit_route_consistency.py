from __future__ import annotations

import json
from pathlib import Path


FIX1_JSON = Path("docs/specs/ilc_rc_frontier_gap_audit_1250_fix1_v0.1.json")
PHASE_1251_WALKTHROUGH = Path("docs/phases/phase_1251_gap14_package_ci_profile_audit_walkthrough.md")
PHASE_1252_SPEC = Path("docs/specs/ilc_gap13_public_claimability_resolution_boundary_1252_v0.1.md")
PHASE_1253_PROMPT = Path(
    "docs/antigravity_tasks/antigravity_prompt__phase_1253_g8_transport_principal_identity_and_http_downgrade.md"
)


def _fix1_findings() -> dict[str, dict[str, object]]:
    payload = json.loads(FIX1_JSON.read_text(encoding="utf-8"))
    return {
        finding["finding_id"]: finding
        for finding in payload["findings"]
    }


def test_phase_1251_walkthrough_preserves_fix1_route_ids_after_phase_1252_audit() -> None:
    findings = _fix1_findings()
    text = PHASE_1251_WALKTHROUGH.read_text(encoding="utf-8")

    assert findings["RCGAP-1250-FIX1-002"]["route"] == (
        "Phase 1254 ATLAS-G backfill planning, not Phase 1251 package CI"
    )
    assert "| Phase 1254 | `RCGAP-1250-FIX1-002` |" in text

    assert findings["RCGAP-1250-FIX1-003"]["route"] == (
        "Phase 1252 chain/crypto dependency inventory"
    )
    assert findings["RCGAP-1250-FIX1-006"]["route"] == (
        "Phase 1252 after explicit GO Phase 1252"
    )
    assert "| Phase 1252 | `RCGAP-1250-FIX1-003`, `RCGAP-1250-FIX1-006` |" in text

    assert findings["RCGAP-1250-FIX1-004"]["route"] == (
        "Phase 1253 TransportPrincipal and public-P2P substrate audit"
    )
    assert findings["RCGAP-1250-FIX1-005"]["route"] == (
        "Phase 1253 Rust public-P2P/TransportPrincipal audit"
    )
    assert findings["RCGAP-1250-FIX1-008"]["route"] == "Phase 1253"
    assert (
        "| Phase 1253 | `RCGAP-1250-FIX1-004`, `RCGAP-1250-FIX1-005`, `RCGAP-1250-FIX1-008` |"
        in text
    )


def test_phase_1253_prompt_directly_reads_phase_1252_boundary_and_fix1_inputs() -> None:
    text = PHASE_1253_PROMPT.read_text(encoding="utf-8")

    assert str(PHASE_1252_SPEC) in text
    assert str(FIX1_JSON) in text
    assert "phase_1253_transport_digest_and_rust_m5_disposition_recorded" in text
    assert "FIXME(M-5)" in text
    assert "must not activate TransportPrincipal runtime" in text


def test_phase_1252_spec_does_not_close_phase_1253_transport_findings() -> None:
    text = PHASE_1252_SPEC.read_text(encoding="utf-8")

    assert "RCGAP-1250-FIX1-003" in text
    assert "RCGAP-1250-FIX1-006" in text
    assert "RCGAP-1250-FIX1-004" in text
    assert "ilc_core/network/d2d/gossip.py:181" in text
    assert "ilc_core/network/d2d/spectral_beacon.py:207" in text
    assert "ilc_core/network/star_map/star_map_route_index_runtime.py:120" in text
    assert "remain routed to Phase 1253" in text
