from __future__ import annotations

import copy
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from ilc_core.sidecars.openclaw_invite_bootstrap import (
    BLOCKED_ACTIONS,
    InviteNullifierStore,
    build_synthetic_invite_bundle,
    canonical_json_bytes,
    derive_redemption_nullifier,
    verify_invite_bootstrap,
)

PROFILE = "openclaw_public_rc_bootstrap"


def _store(tmp_path: Path, name: str = "invite_nullifiers.json") -> InviteNullifierStore:
    return InviteNullifierStore(tmp_path / name)


def _bundle(**overrides: object) -> dict[str, object]:
    bundle = build_synthetic_invite_bundle(intended_profile=PROFILE)
    for key, value in overrides.items():
        if key.startswith("batch__"):
            assert isinstance(bundle["invite_batch_record"], dict)
            bundle["invite_batch_record"][key.removeprefix("batch__")] = value
        else:
            bundle[key] = value
    return bundle


def test_missing_invite_denies_bootstrap_and_allows_help_only(tmp_path: Path) -> None:
    decision = verify_invite_bootstrap(
        None,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=_store(tmp_path),
    )
    assert decision.bootstrap_allowed is False
    assert decision.defect_token == "missing_invite"
    assert set(decision.allowed_actions) == {"docs", "status", "request_invite", "local_help"}


def test_malformed_invite_denies_bootstrap(tmp_path: Path) -> None:
    decision = verify_invite_bootstrap(
        {"invite_batch_record": "not-a-record"},
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=_store(tmp_path),
    )
    assert decision.bootstrap_allowed is False
    assert decision.defect_token == "malformed_invite"


def test_wrong_nonce_denies_bootstrap(tmp_path: Path) -> None:
    bundle = _bundle(private_invite_nonce="22" * 32)
    decision = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=_store(tmp_path),
    )
    assert decision.bootstrap_allowed is False
    assert decision.defect_token == "nonce_membership_mismatch"


def test_replayed_nullifier_denies_bootstrap(tmp_path: Path) -> None:
    bundle = _bundle()
    first = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=_store(tmp_path),
    )
    second = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=_store(tmp_path),
    )
    assert first.bootstrap_allowed is True
    assert second.bootstrap_allowed is False
    assert second.defect_token == "replayed_nullifier"


def test_wrong_profile_denies_bootstrap(tmp_path: Path) -> None:
    decision = verify_invite_bootstrap(
        _bundle(intended_profile="wrong-profile"),
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=_store(tmp_path),
    )
    assert decision.bootstrap_allowed is False
    assert decision.defect_token == "wrong_profile"


def test_wrong_epoch_window_denies_bootstrap(tmp_path: Path) -> None:
    decision = verify_invite_bootstrap(
        _bundle(intended_epoch=1, batch__created_epoch=1),
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=_store(tmp_path),
    )
    assert decision.bootstrap_allowed is False
    assert decision.defect_token == "wrong_epoch_window"


def test_missing_or_unverifiable_inviter_signature_denies_production_bootstrap(tmp_path: Path) -> None:
    decision = verify_invite_bootstrap(
        _bundle(),
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=_store(tmp_path),
        production_required=True,
    )
    assert decision.bootstrap_allowed is False
    assert decision.defect_token == "invite_signature_authority_unverified"
    assert decision.signature_authority_status == "unverified_gap"


def test_valid_synthetic_invite_permits_only_local_bootstrap_actions(tmp_path: Path) -> None:
    decision = verify_invite_bootstrap(
        _bundle(),
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=_store(tmp_path),
    )
    assert decision.bootstrap_allowed is True
    assert "install_ilc_core" in decision.allowed_actions
    assert "run_local_setup" in decision.allowed_actions
    for forbidden in (
        "mint_ecu",
        "publish_nodes",
        "public_graph_write",
        "settle_ilc",
        "wallet_write",
    ):
        assert forbidden in decision.blocked_actions
        assert forbidden not in decision.allowed_actions
    assert set(BLOCKED_ACTIONS).issuperset(decision.blocked_actions)


def test_decision_object_is_deterministic_for_equivalent_input_ordering(tmp_path: Path) -> None:
    bundle = _bundle()
    reordered = {
        "private_invite_nonce": bundle["private_invite_nonce"],
        "intended_profile": bundle["intended_profile"],
        "invite_batch_record": dict(reversed(list(bundle["invite_batch_record"].items()))),  # type: ignore[union-attr]
        "intended_epoch": bundle["intended_epoch"],
    }
    first = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=_store(tmp_path, "one.json"),
        persist_nullifier=False,
    ).to_dict()
    second = verify_invite_bootstrap(
        reordered,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=_store(tmp_path, "two.json"),
        persist_nullifier=False,
    ).to_dict()
    assert canonical_json_bytes(first) == canonical_json_bytes(second)


@pytest.mark.parametrize(
    "bad_value",
    [1.5, math.nan, math.inf, True],
)
def test_float_nan_infinity_bool_as_int_inputs_are_rejected(tmp_path: Path, bad_value: object) -> None:
    bundle = _bundle(intended_epoch=bad_value)
    decision = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=_store(tmp_path),
    )
    assert decision.bootstrap_allowed is False
    assert decision.defect_token == "malformed_invite"


def test_skill_text_requires_invite_before_setup() -> None:
    text = Path("skills/ilc-openclaw-local-capture/SKILL.md").read_text(encoding="utf-8")
    assert "Setup is invite-gated" in text
    assert "ilc verify-invite" in text
    assert "may not bypass" in text
    assert "No invite" in text


def test_session_restart_replay_rejection_from_persisted_nullifier(tmp_path: Path) -> None:
    path = tmp_path / "invite_nullifiers.json"
    bundle = _bundle()
    first = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=InviteNullifierStore(path),
    )
    restarted_store = InviteNullifierStore(path)
    second = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=restarted_store,
    )
    assert first.bootstrap_allowed is True
    assert second.bootstrap_allowed is False
    assert second.defect_token == "replayed_nullifier"


def test_public_safe_helper_has_no_top_level_private_invite_runtime_import() -> None:
    source = Path("ilc_core/sidecars/openclaw_invite_bootstrap.py").read_text(encoding="utf-8")
    assert "ilc_core.genesis.invitation_provenance_record" not in source
    assert "PUBLIC_RC_EXCLUDE" not in source


def test_import_closure_remains_clean_for_public_rc_source_export() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/check_public_rc_exclude_imports.py",
            "ilc_core/",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    assert data["top_level_violation_count"] == 0


def test_nullifier_derivation_matches_locked_domain() -> None:
    nullifier = derive_redemption_nullifier("batch", "11" * 32)
    assert nullifier == derive_redemption_nullifier("batch", "11" * 32)
    assert len(nullifier) == 64


def test_malformed_hex_nonce_denies_bootstrap(tmp_path: Path) -> None:
    bundle = copy.deepcopy(_bundle())
    bundle["private_invite_nonce"] = "zz" * 32
    decision = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=_store(tmp_path),
    )
    assert decision.bootstrap_allowed is False
    assert decision.defect_token == "malformed_invite"
