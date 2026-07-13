#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Run the Phase 1575b-Fix2b local OpenClaw idle-capacity rehearsal."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.sidecars.openclaw_idle_mining import (
    OPENCLAW_IDLE_CAPACITY_VERSION,
    evaluate_task_offer,
    execute_fixture_task,
    parse_provider_usage,
)

OUT_PATH = Path("out/block6_openclaw_idle_mining_fix2b/evidence_records.json")


def _input(label: str) -> dict[str, object]:
    return {"fixture": label, "phase": "1575b-Fix2b"}


def _offer(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "task_type": "candidate_review",
        "input_payload": _input("default"),
        "operator_agent_id": "operator:genesis_local",
        "local_agent_id": "local_agent:openclaw_idle",
        "autonomy_level": "maintenance_idle",
        "resource_policy_profile": "api_metered",
        "contribution_mode": "paid_api_budget_recovery",
        "provider_usage": parse_provider_usage(
            provider_id="anthropic",
            headers={"anthropic-ratelimit-tokens-remaining": "2000"},
        ),
        "min_remaining_tokens": 500,
        "session_consent": True,
        "hour_utc": 23,
        "user_active": False,
        "system_load_percent": 15,
        "max_system_load_percent": 40,
        "idle_window_id": "fix2b_window",
    }
    base.update(overrides)
    return evaluate_task_offer(**base)


def build_evidence() -> dict[str, object]:
    successful_offers: list[dict[str, object]] = []
    results: list[dict[str, object]] = []

    task_specs = [
        ("candidate_review", "api_metered", "paid_api_budget_recovery", "api_review_1"),
        ("exact_dedup_check", "api_metered", "paid_api_budget_recovery", "api_review_2"),
        ("star.map.embedding", "local_compute", "local_idle_compute_contribution", "local_graph_1"),
        ("contradiction.sweep", "local_compute", "local_idle_compute_contribution", "local_graph_2"),
        ("graph.compression", "local_compute", "local_idle_compute_contribution", "local_graph_3"),
        ("stability.simulation", "local_compute", "local_idle_compute_contribution", "local_graph_4"),
    ]
    for task_type, profile, mode, label in task_specs:
        offer = _offer(
            task_type=task_type,
            input_payload=_input(label),
            resource_policy_profile=profile,
            contribution_mode=mode,
            provider_usage=(
                parse_provider_usage(
                    provider_id="openai",
                    headers={"x-ratelimit-remaining-tokens": "1800"},
                )
                if profile == "api_metered"
                else None
            ),
            session_consent=profile == "api_metered",
            local_agent_id=f"local_agent:{label}",
        )
        if not offer["allowed"]:
            raise RuntimeError(f"fixture unexpectedly blocked: {offer}")
        successful_offers.append(offer)
        results.append(execute_fixture_task(offer["task_envelope"]))

    hybrid_offer = _offer(
        task_type="stale_node_triage",
        input_payload=_input("hybrid_local_first"),
        resource_policy_profile="hybrid",
        contribution_mode="local_idle_compute_contribution",
        provider_usage=parse_provider_usage(provider_id="gemini", local_remaining_tokens=1200),
        session_consent=True,
        local_agent_id="local_agent:hybrid",
        allow_api_escalation=False,
    )
    if not hybrid_offer["allowed"] or hybrid_offer["resource_used"] != "local_compute":
        raise RuntimeError(f"hybrid fixture did not use local compute first: {hybrid_offer}")
    successful_offers.append(hybrid_offer)
    results.append(execute_fixture_task(hybrid_offer["task_envelope"]))

    no_offer_cases = [
        _offer(autonomy_level="bounded_autonomy"),
        _offer(
            provider_usage=parse_provider_usage(
                provider_id="anthropic",
                headers={"anthropic-ratelimit-tokens-remaining": "100"},
            ),
            min_remaining_tokens=500,
        ),
        _offer(
            resource_policy_profile="local_compute",
            contribution_mode="local_idle_compute_contribution",
            provider_usage=None,
            session_consent=False,
            hour_utc=12,
        ),
        _offer(
            resource_policy_profile="hybrid",
            contribution_mode="local_idle_compute_contribution",
            provider_usage=parse_provider_usage(provider_id="gemini", local_remaining_tokens=1200),
            session_consent=True,
            hour_utc=12,
            allow_api_escalation=False,
        ),
    ]

    return {
        "credit_minted": False,
        "evidence_records": results,
        "mode_counts": {
            "local_idle_compute_contribution": sum(
                1
                for offer in successful_offers
                if offer["contribution_mode"] == "local_idle_compute_contribution"
            ),
            "paid_api_budget_recovery": sum(
                1
                for offer in successful_offers
                if offer["contribution_mode"] == "paid_api_budget_recovery"
            ),
        },
        "no_clawhub_listing_performed": True,
        "no_distributed_task_reservation": True,
        "no_ecu_minting": True,
        "no_epoch_transition": True,
        "no_ilc_settlement": True,
        "no_offer_cases": no_offer_cases,
        "no_openclaw_publication_performed": True,
        "no_public_graph_submission": True,
        "no_public_rc_activation": True,
        "no_wallet_write": True,
        "phase": "1575b-Fix2b",
        "profile_counts": {
            "api_metered": sum(
                1 for offer in successful_offers if offer["resource_policy_profile"] == "api_metered"
            ),
            "hybrid": sum(1 for offer in successful_offers if offer["resource_policy_profile"] == "hybrid"),
            "local_compute": sum(
                1 for offer in successful_offers if offer["resource_policy_profile"] == "local_compute"
            ),
        },
        "schema_version": "ilc_openclaw_idle_capacity_evidence_1575b_fix2b.v0.1",
        "successful_offers": successful_offers,
        "version": OPENCLAW_IDLE_CAPACITY_VERSION,
        "wallet_write": False,
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
