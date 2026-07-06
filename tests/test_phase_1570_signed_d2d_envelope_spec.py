from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = REPO_ROOT / "docs/specs/ilc_d2d_signed_gossip_envelope_cdl101_v0.1.md"
CDL_LOG = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
STATUS = REPO_ROOT / "docs/phases/STATUS.md"
PROMPT_1570 = (
    REPO_ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1570_g10_block6_defect_fix_tranche1.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_signed_envelope_spec_locks_cdl101_and_canonical_json_v1() -> None:
    text = _read(SPEC)

    assert "CDL: CDL-101" in text
    assert "cdl_101_d2d_signed_gossip_envelope_phase_1570.v0.1" in text
    assert "governance_form: cdl061bis_successor  # CDL-101" in text
    assert "envelope_signing_scheme: canonical_json_v1" in text
    assert (
        'json.dumps(context, sort_keys=True, separators=(",", ":"), '
        'allow_nan=False).encode("utf-8")'
    ) in text
    assert "COSE/ML-DSA" in text
    assert "future v2 design lane" in text


def test_signed_context_binds_peer_key_payload_and_routing_fields() -> None:
    text = _read(SPEC)
    for field in (
        '"channel"',
        '"content_type"',
        '"domain"',
        '"envelope_version"',
        '"epoch"',
        '"gossip_type"',
        '"hop_count"',
        '"key_id"',
        '"payload_sha256"',
        '"peer_id"',
        '"signature_alg"',
    ):
        assert field in text

    assert '"domain": "ILC-D2D-GossipEnvelope-v1"' in text
    assert '"signature_alg": "ML-DSA-65"' in text
    assert "`ILC-Sender-Peer-Id`" in text
    assert "`ILC-Key-Id`" in text
    assert "routing hints until signature verification succeeds" in text


def test_replay_and_actor_binding_rules_are_machine_readable() -> None:
    text = _read(SPEC)

    assert "(peer_id, key_id, epoch, gossip_type, channel, payload_sha256)" in text
    assert "HTTP 409" in text
    assert "Cache TTL is 2 validation epochs" in text
    assert "signature_sha256" in text
    assert "audit metadata only" in text
    assert "actor_binding_rule: peer_id_maps_to_authorized_actor_ids" in text
    assert "claimed_actor in registry[peer_id].authorized_actor_ids" in text
    assert "d2d_actor_binding_mismatch" in text
    assert "tla_plus_obligation_delegation_key_rotation_safety" in text


def test_cdl039_forbidden_identity_headers_remain_forbidden() -> None:
    text = _read(SPEC)

    for forbidden in (
        "ILC-Creator-Agent-Id",
        "ILC-Node-Id",
        "creator_agent_id",
        "node_id",
    ):
        assert forbidden in text

    assert "Do not infer graph authorship from `ILC-Sender-Peer-Id`" in text
    assert "It is not the v1 default" in text


def test_cdl101_register_row_is_opened_not_ratified() -> None:
    text = _read(CDL_LOG)

    assert "| CDL-101 | CDL-061 / CDL-039 / Block 6 deep audit 086bfd81 |" in text
    assert "D2D Signed Gossip Envelope" in text
    assert "| opened |" in text
    assert "opening_token: cdl_101_opened" in text
    assert "opened_phase: 1570" in text
    assert "pending_ratification" in text
    assert "runtime_activation_status: not_authorized" in text
    assert "public_path_status: blocked" in text
    assert "ratification_token: cdl_101_ratified" not in text


def test_status_records_phase1570_tokens_and_no_activation_claim() -> None:
    text = _read(STATUS)

    for token in (
        "cdl_101_opened",
        "signed_d2d_envelope_spec_committed_phase_1570",
        "d2d_envelope_decisions_locked_phase_1570",
        "public_path_remains_blocked_phase_1570",
    ):
        assert token in text

    assert "No runtime file was modified" in text
    assert "no receiver-side verification was activated" in text
    assert "public RC activation occurred" in text


def test_phase1570_prompt_records_live_cdl_numbering_reroute() -> None:
    text = _read(PROMPT_1570)

    assert "CDL-099 and CDL-100 are" in text
    assert "already planned/reserved" in text
    assert "CDL-101 is available" in text
    assert "docs/specs/ilc_d2d_signed_gossip_envelope_cdl101_v0.1.md" in text
