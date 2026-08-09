# SPDX-License-Identifier: AGPL-3.0-only
"""Tests for GAP-PUBLIC-NODE-FIREWALL-01 DigitalOcean apply helper."""

from __future__ import annotations

import json
from pathlib import Path

from tools.testbed.phase_gap_public_node_firewall_01_apply_do_rules import (
    build_evidence,
    missing_rules,
    rule_is_covered,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "out/phase_gap_public_node_firewall_01/firewall_application_evidence.json"
COMPLETION_EVIDENCE = ROOT / "out/phase_gap_public_node_firewall_01/firewall_application_completion_evidence.json"
STATUS = ROOT / "docs/phases/STATUS.md"


def test_do_firewall_range_rule_covers_single_port_with_same_sources() -> None:
    existing = {
        "ports": "51262-51265",
        "protocol": "tcp",
        "sources": {"addresses": ["139.47.123.233/32", "164.90.201.11/32"]},
    }
    desired = {
        "ports": "51265",
        "protocol": "tcp",
        "sources": {"addresses": ["139.47.123.233/32"]},
    }

    assert rule_is_covered(existing, desired) is True
    assert missing_rules([existing], [desired]) == []


def test_do_firewall_bare_ip_matches_cidr_source() -> None:
    existing = {
        "ports": "51252-51255",
        "protocol": "udp",
        "sources": {"addresses": ["139.47.123.233/32"]},
    }
    desired = {
        "ports": "51255",
        "protocol": "udp",
        "sources": {"addresses": ["139.47.123.233"]},
    }

    assert rule_is_covered(existing, desired) is True


def test_do_firewall_range_rule_does_not_cover_wrong_protocol_or_source() -> None:
    existing = {
        "ports": "51262-51265",
        "protocol": "tcp",
        "sources": {"addresses": ["164.90.201.11/32"]},
    }
    desired_udp = {
        "ports": "51265",
        "protocol": "udp",
        "sources": {"addresses": ["164.90.201.11/32"]},
    }
    desired_source = {
        "ports": "51265",
        "protocol": "tcp",
        "sources": {"addresses": ["139.47.123.233/32"]},
    }

    assert rule_is_covered(existing, desired_udp) is False
    assert rule_is_covered(existing, desired_source) is False
    assert missing_rules([existing], [desired_udp, desired_source]) == [desired_udp, desired_source]


def test_rollback_payload_empty_when_rules_already_present(tmp_path) -> None:
    desired = [{"ports": "51265", "protocol": "tcp", "sources": {"addresses": ["127.0.0.1/32"]}}]
    evidence = build_evidence(
        firewall_id="fw-123",
        before={"firewall": {"inbound_rules": desired}},
        after={"firewall": {"name": "fw", "status": "succeeded", "inbound_rules": desired}},
        desired_rules=desired,
        missing_before_apply=[],
        post_status_code=None,
        plan_payload={"inbound_rules": desired},
        evidence_path=tmp_path / "evidence.json",
    )

    assert evidence["rules_already_present"] is True
    assert evidence["rules_applied"] == []
    assert evidence["rollback_required"] is False
    assert evidence["rollback_payload"] == {"inbound_rules": []}
    assert "No rollback required" in evidence["rollback_scope_note"]


def test_rollback_payload_contains_only_rules_added_by_phase(tmp_path) -> None:
    existing = [{"ports": "51265", "protocol": "tcp", "sources": {"addresses": ["127.0.0.1/32"]}}]
    added = [{"ports": "51255", "protocol": "udp", "sources": {"addresses": ["127.0.0.1/32"]}}]
    desired = existing + added
    evidence = build_evidence(
        firewall_id="fw-123",
        before={"firewall": {"inbound_rules": existing}},
        after={"firewall": {"name": "fw", "status": "succeeded", "inbound_rules": desired}},
        desired_rules=desired,
        missing_before_apply=added,
        post_status_code=204,
        plan_payload={"inbound_rules": desired},
        evidence_path=tmp_path / "evidence.json",
    )

    assert evidence["rules_already_present"] is False
    assert evidence["rules_applied"] == added
    assert evidence["rollback_required"] is True
    assert evidence["rollback_payload"] == {"inbound_rules": added}
    assert "newly added" in evidence["rollback_scope_note"]


def test_live_evidence_never_contains_api_token_or_broad_rollback() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    assert evidence["api_token_used"] == "REDACTED"
    assert evidence["missing_before_apply_count"] == 0
    assert evidence["rules_already_present"] is True
    assert evidence["rules_applied"] == []
    assert evidence["rollback_required"] is False
    assert evidence["rollback_payload"] == {"inbound_rules": []}
    assert evidence["rules_required"]


def test_live_evidence_does_not_claim_grpc_reachability_when_listener_absent() -> None:
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    probes = evidence["probe_results"]

    assert evidence["phase_status"] == "PARTIAL_BLOCKED_ACTIVE_LISTENER_ABSENT"
    assert probes["grpc_tcp_reachable"] is False
    assert probes["grpc_tcp_error"] == "network_grpc_tcp_connection_refused"
    assert "listener absence" in probes["active_listener_diagnosis"]


def test_completion_evidence_emits_withheld_grpc_reachability_token() -> None:
    evidence = json.loads(COMPLETION_EVIDENCE.read_text(encoding="utf-8"))
    status = STATUS.read_text(encoding="utf-8")
    token = "external_grpc_tcp_reachable_verified_GAP_PUBLIC_NODE_FIREWALL_01"

    assert evidence["completion_status"] == "COMPLETE"
    assert evidence["external_grpc_tcp_reachable_verified"] is True
    assert evidence["probe_results"]["readiness"]["network_grpc_tcp_reachable"] is True
    assert all(
        probe["exit_code"] == 0
        for probe in evidence["probe_results"]["all_public_grpc_tcp_socket_probes"]
    )
    assert evidence["token_emitted"] == token
    assert token in status
