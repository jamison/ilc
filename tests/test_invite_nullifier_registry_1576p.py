from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from ilc_core.genesis.invite_nullifier_registry import (
    _MAX_REGISTRY_SIZE,
    InviteNullifierError,
    InviteNullifierRegistry,
)
from ilc_core.sidecars.openclaw_invite_bootstrap import (
    CROSS_NODE_REPLAY_PREVENTION_GAP,
    InviteNullifierStore,
    build_synthetic_invite_bundle,
    derive_redemption_nullifier,
    verify_invite_bootstrap,
)


PROFILE = "openclaw_public_rc_bootstrap"
NULLIFIER = "a" * 64


def test_registry_accepts_new_nullifier() -> None:
    registry = InviteNullifierRegistry()
    registry.register_nullifier(NULLIFIER)
    assert len(registry) == 1


def test_registry_detects_duplicate() -> None:
    registry = InviteNullifierRegistry()
    registry.register_nullifier(NULLIFIER)
    assert registry.is_known(NULLIFIER) is True


def test_register_if_new_is_atomic_for_duplicates() -> None:
    registry = InviteNullifierRegistry()

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: registry.register_if_new(NULLIFIER), range(64)))

    assert results.count(True) == 1
    assert results.count(False) == 63
    assert len(registry) == 1


def test_registry_unknown_returns_false() -> None:
    registry = InviteNullifierRegistry()
    assert registry.is_known("b" * 64) is False


def test_registry_full_raises() -> None:
    registry = InviteNullifierRegistry()
    registry._MAX_REGISTRY_SIZE = 1
    registry.register_nullifier("a" * 64)
    with pytest.raises(InviteNullifierError, match="invite_nullifier_registry_full"):
        registry.register_nullifier("b" * 64)
    assert _MAX_REGISTRY_SIZE == 10_000


def test_registry_rejects_non_hex_nullifier() -> None:
    registry = InviteNullifierRegistry()
    with pytest.raises(InviteNullifierError, match="invite_nullifier_invalid"):
        registry.register_nullifier("z" * 64)


def test_local_double_redemption_rejected(tmp_path: Path) -> None:
    bundle = build_synthetic_invite_bundle(intended_profile=PROFILE)
    registry = InviteNullifierRegistry()
    store = InviteNullifierStore(tmp_path / "invite_nullifiers.json")
    first = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        local_nullifier_registry=registry,
        nullifier_store=store,
    )
    second = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        local_nullifier_registry=registry,
        nullifier_store=InviteNullifierStore(tmp_path / "other_invite_nullifiers.json"),
    )
    assert first.bootstrap_allowed is True
    assert second.bootstrap_allowed is False
    assert second.defect_token == "invite_nullifier_already_seen"


def test_persistent_store_replay_rejection_still_works(tmp_path: Path) -> None:
    bundle = build_synthetic_invite_bundle(intended_profile=PROFILE)
    nonce_hex = str(bundle["private_invite_nonce"])
    nullifier = derive_redemption_nullifier("openclaw-fix2d-batch", nonce_hex)
    store = InviteNullifierStore(tmp_path / "invite_nullifiers.json")
    registry = InviteNullifierRegistry()
    store.add(nullifier)
    decision = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        local_nullifier_registry=registry,
        nullifier_store=store,
    )
    assert decision.bootstrap_allowed is False
    assert decision.defect_token == "replayed_nullifier"


def test_persistent_store_write_failure_does_not_mutate_memory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    store = InviteNullifierStore(tmp_path / "invite_nullifiers.json")

    def fail_write(_path: Path, _used: dict[str, object]) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(
        "ilc_core.sidecars.openclaw_invite_bootstrap._write_nullifier_map",
        fail_write,
    )
    with pytest.raises(OSError):
        store.add(NULLIFIER)

    assert store.contains(NULLIFIER) is False


def test_openclaw_rolls_back_local_registry_on_persistence_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    bundle = build_synthetic_invite_bundle(intended_profile=PROFILE)
    nonce_hex = str(bundle["private_invite_nonce"])
    nullifier = derive_redemption_nullifier("openclaw-fix2d-batch", nonce_hex)
    registry = InviteNullifierRegistry()

    def fail_write(_path: Path, _used: dict[str, object]) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(
        "ilc_core.sidecars.openclaw_invite_bootstrap._write_nullifier_map",
        fail_write,
    )
    decision = verify_invite_bootstrap(
        bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        local_nullifier_registry=registry,
        nullifier_store=InviteNullifierStore(tmp_path / "invite_nullifiers.json"),
    )

    assert decision.bootstrap_allowed is False
    assert decision.defect_token == "malformed_invite"
    assert registry.is_known(nullifier) is False


def test_cross_node_gap_annotation_records_1576pb_closure() -> None:
    source = Path("ilc_core/sidecars/openclaw_invite_bootstrap.py").read_text(encoding="utf-8")
    assert "cross_node_replay_prevention_gap" in source
    assert "1576p-b" in source or "1576p_b" in source
    assert "local_detection_implemented_phase_1576p" in CROSS_NODE_REPLAY_PREVENTION_GAP
    assert "cross_node_replay_prevention_phase_1576pb" in CROSS_NODE_REPLAY_PREVENTION_GAP
    assert "cross_node_d2d_propagation_remains_open_phase_1576p_b" not in CROSS_NODE_REPLAY_PREVENTION_GAP


def test_invite_nullifier_gossip_file_present_after_1576pb() -> None:
    assert Path("ilc_core/network/d2d/invite_nullifier_gossip.py").exists()
