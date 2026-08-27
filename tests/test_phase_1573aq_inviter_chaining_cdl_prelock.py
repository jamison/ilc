from __future__ import annotations

from pathlib import Path

from ilc_core.genesis.invitation_provenance_record import (
    InviteBatchRecord,
    InviteRedemptionRecord,
    build_invite_batch_record,
    build_invite_redemption_record,
    derive_invite_redemption_nullifier,
)


CDL = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PRELOCK = Path("docs/specs/ilc_cdl_102_inviter_chaining_economics_prelock_1573aq_v0.1.md")
OPENING = Path("docs/specs/ilc_cdl_102_inviter_chaining_economics_opening_1573ad_v0.1.md")
STATUS = Path("docs/phases/STATUS.md")
PROMPT = Path(
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1573aq_g8_inviter_chaining_cdl_prelock.md"
)


def test_cdl_102_prelock_artifact_is_preserved_after_ratification() -> None:
    text = CDL.read_text(encoding="utf-8")
    row = next(line for line in text.splitlines() if line.startswith("| CDL-102 |"))

    assert " | ratified | " in row
    assert "prelock_phase: 1573aq" in row
    assert "prelock_token: inviter_chaining_cdl_prelocked_phase_1573aq" in row
    assert "ratified_phase: 1576m" in row
    assert "ratification_token: cdl_102_ratified_phase_1576m" in row
    assert "cdl_091_status: unchanged" in row
    assert "invite_credit_model: organic_cdl_108_backward_attribution" in row


def test_prelock_doc_records_exact_runtime_fields_and_deferred_depth() -> None:
    text = PRELOCK.read_text(encoding="utf-8")

    assert "Decision ID:** CDL-102" in text
    assert "InviteBatchRecord.inviter_cid" in text
    assert "InviteBatchRecord.batch_id" in text
    assert "InviteBatchRecord.count" in text
    assert "InviteBatchRecord.nonce_merkle_root" in text
    assert "InviteBatchRecord.created_epoch" in text
    assert "InviteBatchRecord.inviter_sig" in text
    assert "InviteRedemptionRecord.redemption_nullifier" in text
    assert "InviteRedemptionRecord.redeemer_agent_id" in text
    assert "invite_chain_max_depth_parameter_deferred_to_1576m" in text


def test_nullifier_construction_is_the_prelocked_runtime_construction() -> None:
    nonce = bytes.fromhex("11" * 32)
    nullifier = derive_invite_redemption_nullifier("batch-aq", nonce)

    assert len(nullifier) == 64
    assert (
        nullifier
        == "01e06da55c3ba960ad9cee33f761e952811bb779aa50769b6a3114a3635b9747"
    )
    assert (
        derive_invite_redemption_nullifier("batch-aq", nonce.hex())
        == nullifier
    )


def test_raw_nonce_is_not_stored_in_permanent_records() -> None:
    batch, nonce_hexes = build_invite_batch_record(
        inviter_cid="agent:inviter",
        batch_id="batch-aq",
        count=1,
        created_epoch=0,
        inviter_sig="sig",
        nonces=(bytes.fromhex("22" * 32),),
    )
    redemption = build_invite_redemption_record(
        batch=batch,
        nonce=nonce_hexes[0],
        nonce_membership_proof=(),
        redeemer_pubkey_cid="cid:redeemer",
        identity_seed=bytes.fromhex("33" * 32),
        redemption_epoch=0,
    )

    batch_payload = batch.to_dict()
    redemption_payload = redemption.to_dict()
    assert "nonce" not in batch_payload
    assert "nonce" not in redemption_payload
    assert nonce_hexes[0] not in str(batch_payload)
    assert nonce_hexes[0] not in str(redemption_payload)
    assert "redemption_nullifier" in redemption_payload


def test_runtime_record_dataclass_fields_match_prelock_doc() -> None:
    assert tuple(InviteBatchRecord.__dataclass_fields__) == (
        "inviter_cid",
        "batch_id",
        "count",
        "nonce_merkle_root",
        "created_epoch",
        "inviter_sig",
    )
    assert tuple(InviteRedemptionRecord.__dataclass_fields__) == (
        "batch_id",
        "redemption_nullifier",
        "nonce_membership_proof",
        "redeemer_pubkey_cid",
        "redeemer_agent_id",
        "redemption_epoch",
        "inviter_cid",
        "invite_id",
        "redeemer_key_binding",
    )


def test_phase_1573aq_status_tokens_present() -> None:
    status = STATUS.read_text(encoding="utf-8")

    assert "inviter_chaining_cdl_prelocked_phase_1573aq" in status
    assert "invite_chain_max_depth_parameter_deferred_to_1576m" in status
    assert "public_path_remains_blocked_phase_1573aq" in status


def test_opening_remains_non_activation_and_prompt_is_hardened() -> None:
    opening = OPENING.read_text(encoding="utf-8")
    prompt = PROMPT.read_text(encoding="utf-8")
    prelock = PRELOCK.read_text(encoding="utf-8")

    assert "- activate inviter credit;" in opening
    assert "invite_cli_plumbing_committed_phase_1573z" in prompt
    assert "Required precondition tokens" in prompt
    assert "- ratify CDL-102;" in prelock
    assert "does not" in prelock and "mint ECU or settle ILC" in prelock
