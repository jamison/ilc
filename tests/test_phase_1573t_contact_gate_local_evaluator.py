import pytest
from pathlib import Path

from ilc_core import ccss
from ilc_core.ccss.contact_gate import (
    CONTACT_GATE_ADMISSION_MODES,
    CONTACT_GATE_PUBLIC_SERVING_NOT_ACTIVATED,
    ContactGateError,
    assert_no_private_gate_fields,
    evaluate_contact_gate,
    make_contact_gate_nullifier,
)


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs/phases/STATUS.md"


def _policy(mode: str, **extra: object) -> dict[str, object]:
    return {
        "admission_mode": mode,
        "gate_id": f"gate:{mode}",
        **extra,
    }


def test_public_open_accepts_without_private_capability() -> None:
    verdict = evaluate_contact_gate(_policy("public_open"), {})
    assert verdict["accepted"] is True
    assert verdict["verdict_token"] == "ccss_contact_gate_accept_public_open"
    assert verdict["public_serving_activated"] is False
    assert_no_private_gate_fields(verdict)


def test_contacts_only_accepts_known_contact_and_rejects_unknown_sender() -> None:
    policy = _policy("contacts_only", known_contact_ids=["alice", "bob"])
    accepted = evaluate_contact_gate(policy, {"sender_contact_id": "alice"})
    rejected = evaluate_contact_gate(policy, {"sender_contact_id": "mallory"})

    assert accepted["accepted"] is True
    assert accepted["verdict_token"] == "ccss_contact_gate_accept_known_contact"
    assert rejected["accepted"] is False
    assert rejected["verdict_token"] == "ccss_contact_gate_reject_unknown_contact"
    assert "known_contact_ids" not in accepted
    assert_no_private_gate_fields(accepted)
    assert_no_private_gate_fields(rejected)


def test_capability_required_uses_constant_time_opaque_commitment_match() -> None:
    capability = "aabbccdd" * 8
    policy = _policy("capability_required", capability_context_commitment=capability)

    accepted = evaluate_contact_gate(
        policy,
        {"capability_context_commitment": capability},
    )
    rejected = evaluate_contact_gate(
        policy,
        {"capability_context_commitment": "ddccbbaa" * 8},
    )

    assert accepted["accepted"] is True
    assert accepted["verdict_token"] == "ccss_contact_gate_accept_capability"
    assert rejected["accepted"] is False
    assert rejected["verdict_token"] == "ccss_contact_gate_reject_capability_mismatch"
    assert "capability_context_commitment" not in accepted
    assert_no_private_gate_fields(accepted)


def test_private_invite_only_requires_invite_or_capability_context() -> None:
    invite = b"private-invite-context"
    policy = _policy("private_invite_only", expected_invite_context_commitment=invite)

    accepted = evaluate_contact_gate(
        policy,
        {"invite_context_commitment": invite},
    )
    rejected = evaluate_contact_gate(
        policy,
        {"invite_context_commitment": b"wrong-context"},
    )

    assert accepted["accepted"] is True
    assert accepted["verdict_token"] == "ccss_contact_gate_accept_private_invite"
    assert rejected["accepted"] is False
    assert rejected["verdict_token"] == "ccss_contact_gate_reject_private_invite_mismatch"


def test_closed_rejects_all_inbound_attempts() -> None:
    verdict = evaluate_contact_gate(
        _policy("closed", known_contact_ids=["alice"], capability_context_commitment="aa"),
        {"sender_contact_id": "alice", "capability_context_commitment": "aa"},
    )
    assert verdict["accepted"] is False
    assert verdict["verdict_token"] == "ccss_contact_gate_reject_closed"
    assert_no_private_gate_fields(verdict)


def test_stake_or_rate_limited_open_fails_closed_before_public_rc() -> None:
    verdict = evaluate_contact_gate(
        _policy("stake_or_rate_limited_open"),
        {"stake_receipt": "not_authorized"},
    )
    assert verdict["accepted"] is False
    assert verdict["verdict_token"] == (
        "ccss_contact_gate_stake_rate_limited_not_activated_phase_1573t"
    )


def test_public_serving_guard_remains_true_and_all_modes_are_known() -> None:
    assert CONTACT_GATE_PUBLIC_SERVING_NOT_ACTIVATED is True
    assert ccss.CONTACT_GATE_PUBLIC_SERVING_NOT_ACTIVATED is True
    assert ccss.evaluate_contact_gate is evaluate_contact_gate
    assert CONTACT_GATE_ADMISSION_MODES == {
        "public_open",
        "contacts_only",
        "capability_required",
        "stake_or_rate_limited_open",
        "private_invite_only",
        "closed",
    }


def test_evaluator_outputs_do_not_emit_private_gate_rules() -> None:
    verdict = evaluate_contact_gate(
        _policy(
            "capability_required",
            known_contact_ids=["alice"],
            capability_context_commitment="ab" * 32,
            raw_capability_id="secret",
        ),
        {"capability_context_commitment": "ab" * 32, "sender_contact_id": "alice"},
    )
    for forbidden in (
        "known_contact_ids",
        "allowed_contact_ids",
        "allowlist",
        "denylist",
        "raw_capability_id",
        "private_invite_secret",
        "expected_invite_context_commitment",
        "capability_context_commitment",
        "sender_contact_id",
        "recipient_agent_id",
    ):
        assert forbidden not in verdict
    assert verdict["relay_visible_fields"] == ["opaque_bundle_metadata_only"]
    assert verdict["private_rule_disclosed"] is False


def test_local_nullifier_is_deterministic_and_secret_free() -> None:
    first = make_contact_gate_nullifier(
        gate_id="gate:cap",
        sender_context_commitment="11" * 32,
        sealed_nonce="22" * 12,
    )
    second = make_contact_gate_nullifier(
        gate_id="gate:cap",
        sender_context_commitment="11" * 32,
        sealed_nonce="22" * 12,
    )
    other = make_contact_gate_nullifier(
        gate_id="gate:cap",
        sender_context_commitment="33" * 32,
        sealed_nonce="22" * 12,
    )
    assert first == second
    assert first != other
    assert len(first) == 64


def test_invalid_policy_mode_raises_stable_token() -> None:
    with pytest.raises(ContactGateError, match="ccss_contact_gate_admission_mode_invalid"):
        evaluate_contact_gate(_policy("not-a-mode"), {})


def test_phase_status_tokens_are_present() -> None:
    status = STATUS.read_text(encoding="utf-8")
    for token in (
        "ccss_contact_gate_local_evaluator_committed_phase_1573t",
        "ccss_contact_gate_private_modes_tested_phase_1573t",
        "ccss_contact_gate_public_serving_not_activated_phase_1573t",
        "public_path_remains_blocked_phase_1573t",
    ):
        assert token in status
