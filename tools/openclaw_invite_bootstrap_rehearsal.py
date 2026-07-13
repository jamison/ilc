#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Write retained evidence for Phase 1575b-Fix2d invite-gated bootstrap."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from ilc_core.sidecars.openclaw_invite_bootstrap import (
    InviteNullifierStore,
    build_synthetic_invite_bundle,
    canonical_json_bytes,
    verify_invite_bootstrap,
)

EVIDENCE_PATH = Path("out/block6_openclaw_invite_bootstrap_fix2d/evidence_records.json")
PROFILE = "openclaw_public_rc_bootstrap"


def main() -> None:
    base_dir = Path("out/block6_openclaw_invite_bootstrap_fix2d")
    store_path = base_dir / "invite_nullifiers_fixture.json"
    store_path.unlink(missing_ok=True)

    valid_bundle = build_synthetic_invite_bundle(intended_profile=PROFILE)
    valid_store = InviteNullifierStore(store_path)
    valid_decision = verify_invite_bootstrap(
        valid_bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=valid_store,
    )

    replay_decision = verify_invite_bootstrap(
        valid_bundle,
        expected_profile=PROFILE,
        current_epoch=0,
        nullifier_store=InviteNullifierStore(store_path),
    )

    wrong_profile = build_synthetic_invite_bundle(intended_profile="wrong-profile")
    wrong_epoch = build_synthetic_invite_bundle(intended_profile=PROFILE, intended_epoch=1)
    wrong_nonce = build_synthetic_invite_bundle(intended_profile=PROFILE)
    wrong_nonce["private_invite_nonce"] = "22" * 32

    decisions = {
        "missing_invite": verify_invite_bootstrap(
            None,
            expected_profile=PROFILE,
            current_epoch=0,
            nullifier_store=InviteNullifierStore(base_dir / "missing.json"),
        ).to_dict(),
        "valid_synthetic_local": valid_decision.to_dict(),
        "wrong_nonce": verify_invite_bootstrap(
            wrong_nonce,
            expected_profile=PROFILE,
            current_epoch=0,
            nullifier_store=InviteNullifierStore(base_dir / "wrong_nonce.json"),
        ).to_dict(),
        "wrong_profile": verify_invite_bootstrap(
            wrong_profile,
            expected_profile=PROFILE,
            current_epoch=0,
            nullifier_store=InviteNullifierStore(base_dir / "wrong_profile.json"),
        ).to_dict(),
        "wrong_epoch": verify_invite_bootstrap(
            wrong_epoch,
            expected_profile=PROFILE,
            current_epoch=0,
            nullifier_store=InviteNullifierStore(base_dir / "wrong_epoch.json"),
        ).to_dict(),
        "replayed_after_restart": replay_decision.to_dict(),
        "production_required_signature_gap": verify_invite_bootstrap(
            build_synthetic_invite_bundle(intended_profile=PROFILE, batch_id="production-gap"),
            expected_profile=PROFILE,
            current_epoch=0,
            nullifier_store=InviteNullifierStore(base_dir / "production_gap.json"),
            production_required=True,
        ).to_dict(),
    }
    evidence = {
        "cross_node_replay_prevention_gap": "redeemer_key_binding_required",
        "decisions": decisions,
        "evidence_schema": "openclaw_invite_bootstrap_rehearsal_1575b_fix2d.v0.1",
        "invite_signature_authority_gap": "unverified_gap",
        "no_clawhub_listing": True,
        "no_ecu_minting": True,
        "no_openclaw_publication": True,
        "no_public_graph_write": True,
        "no_public_invite_issuance": True,
        "no_public_rc_activation": True,
        "no_wallet_write": True,
        "phase": "1575b-Fix2d",
        "valid_synthetic_local_bootstrap_allowed": valid_decision.bootstrap_allowed,
    }
    body = canonical_json_bytes(evidence)
    evidence["evidence_sha256"] = hashlib.sha256(body).hexdigest()
    _atomic_write_json(EVIDENCE_PATH, evidence)
    print(EVIDENCE_PATH)
    print(evidence["evidence_sha256"])


def _atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(body)
            handle.write(b"\n")
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


if __name__ == "__main__":
    main()
