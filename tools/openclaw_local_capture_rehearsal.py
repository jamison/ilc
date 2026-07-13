#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Run the Phase 1575b-Fix2a local OpenClaw capture rehearsal."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.sidecars.openclaw_local_capture import (
    OPENCLAW_LOCAL_CAPTURE_VERSION,
    build_capture_envelope,
    build_estimate_record,
    build_status_record,
    evaluate_consent_gate,
)

OUT_PATH = Path("out/block6_openclaw_local_capture_fix2a/evidence_records.json")


def build_evidence() -> dict[str, object]:
    fixture_payloads = [
        {
            "payload_kind": "reply",
            "raw_payload": {
                "text": "A bounded OpenClaw response can become a local ILC claim candidate.",
                "candidate_node_type": "claim_candidate",
            },
        },
        {
            "payload_kind": "tool_result",
            "raw_payload": {
                "tool": "pytest",
                "result": "pass",
                "summary": "Focused local capture tests passed.",
                "candidate_node_type": "test_result_candidate",
            },
        },
    ]
    envelopes = [
        build_capture_envelope(
            raw_payload=item["raw_payload"],
            payload_kind=str(item["payload_kind"]),
            operator_agent_id="operator:genesis_local",
            local_agent_id=f"local_agent:openclaw_fixture_{idx}",
            provider_id="synthetic_provider",
            session_id="phase_1575b_fix2a_session",
            created_epoch=0,
            consent_state="needs_review" if idx == 0 else "approved_for_public_submission",
            candidate_edges=(
                {"edge_type": "EVIDENCES", "target": "phase:1575b_fix2a_synthetic_fixture"},
            ),
        )
        for idx, item in enumerate(fixture_payloads, start=1)
    ]
    return {
        "captures": [env.to_dict() for env in envelopes],
        "created_epoch": 0,
        "estimates": [build_estimate_record(env) for env in envelopes],
        "no_clawhub_listing_performed": True,
        "no_ecu_minting": True,
        "no_epoch_transition": True,
        "no_ilc_settlement": True,
        "no_openclaw_publication_performed": True,
        "no_public_graph_submission": True,
        "no_publication_performed": True,
        "no_public_rc_activation": True,
        "no_wallet_write": True,
        "phase": "1575b-Fix2a",
        "schema_version": "ilc_openclaw_local_capture_evidence_1575b_fix2a.v0.1",
        "status": build_status_record(envelopes),
        "submit_decisions": [evaluate_consent_gate(env, action="submit") for env in envelopes],
        "version": OPENCLAW_LOCAL_CAPTURE_VERSION,
    }


def atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(text)
        handle.write("\n")
        tmp_name = handle.name
    os.replace(tmp_name, path)


def main() -> None:
    atomic_write_json(OUT_PATH, build_evidence())
    print(str(OUT_PATH))


if __name__ == "__main__":
    main()
