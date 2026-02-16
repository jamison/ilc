from ilc_core.analysis.node_value_conformance import (
    build_node_value_conformance_report,
    verify_node_value_challenge,
)


def _events_with_low_diversity_reuse() -> list[dict[str, object]]:
    return [
        {
            "kind": "claim",
            "payload": {
                "id": "node-a",
                "agent_id": "agent-1",
                "timestamp": "2026-02-16T00:00:00Z",
                "net_stake": 5.0,
                "parent_ids": ["root"],
                "target_id": "genesis-node",
            },
        },
        {
            "kind": "claim",
            "payload": {
                "id": "node-b",
                "agent_id": "agent-1",
                "timestamp": "2026-02-16T00:01:00Z",
                "net_stake": 3.0,
                "parent_ids": ["node-a"],
                "target_id": "genesis-node",
            },
        },
        {
            "kind": "refutation",
            "payload": {
                "id": "ref-1",
                "agent_id": "agent-1",
                "timestamp": "2026-02-16T00:02:00Z",
                "target_id": "genesis-node",
                "net_stake": 1.0,
            },
        },
    ]


def test_conformance_report_emits_deterministic_hash_and_sybil_flags() -> None:
    report_a = build_node_value_conformance_report(_events_with_low_diversity_reuse())
    report_b = build_node_value_conformance_report(_events_with_low_diversity_reuse())

    assert report_a["score_rows_sha256"] == report_b["score_rows_sha256"]
    assert report_a["score_rows"] == report_b["score_rows"]
    assert report_a["anti_sybil_ok"] is False
    assert any(
        token.startswith("sybil_low_diversity_reuse:")
        for token in report_a["anti_sybil_flags"]
    )


def test_challenge_verification_accepts_matching_claim() -> None:
    report = build_node_value_conformance_report(_events_with_low_diversity_reuse())

    verification = verify_node_value_challenge(
        _events_with_low_diversity_reuse(),
        claimed_sha256=report["score_rows_sha256"],
        claimed_row_count=len(report["score_rows"]),
    )

    assert verification["ok"] is True
    assert verification["errors"] == []


def test_challenge_verification_detects_hash_and_row_count_mismatch() -> None:
    verification = verify_node_value_challenge(
        _events_with_low_diversity_reuse(),
        claimed_sha256="0" * 64,
        claimed_row_count=999,
    )

    assert verification["ok"] is False
    assert set(verification["errors"]) == {
        "challenge_hash_mismatch",
        "challenge_row_count_mismatch",
    }
