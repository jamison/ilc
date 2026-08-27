from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from ilc_core.genesis.invitation_provenance_record import build_invite_batch_record
from ilc_core.sidecars.openclaw_invite_bootstrap import verify_invite_bootstrap


ROOT = Path(__file__).resolve().parents[1]


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ilc_core.cli.main", *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _write_batch(path: Path) -> None:
    record, nonces = build_invite_batch_record(
        inviter_cid="genesis_agent:01",
        batch_id="public-rc-vps-validator-bootstrap-00",
        count=4,
        created_epoch=0,
        inviter_sig="genesis",
    )
    path.write_text(
        json.dumps(
            {
                "invite_batch_record": record.to_dict(),
                "private_invite_nonces": list(nonces),
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def test_invite_bundle_cli_builds_count_four_verifier_valid_bundle(tmp_path: Path) -> None:
    batch_path = tmp_path / "batch.json"
    bundle_path = tmp_path / "bundle.json"
    _write_batch(batch_path)

    result = _run_cli(
        "identity",
        "invite",
        "bundle",
        str(batch_path),
        "--nonce-index",
        "2",
        "--output",
        str(bundle_path),
        "--enable-invites",
    )

    assert result.returncode == 0, result.stderr
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    assert bundle["intended_epoch"] == 0
    assert bundle["intended_profile"] == "public_rc_validator_bootstrap"
    assert len(bundle["nonce_membership_proof"]) == 2
    assert all(set(item) == {"position", "sibling"} for item in bundle["nonce_membership_proof"])
    assert "atlas_slice_manifest_witness" in bundle
    assert "starmap_manifest_payload" in bundle

    decision = verify_invite_bootstrap(
        bundle,
        expected_profile="public_rc_validator_bootstrap",
        current_epoch=0,
        persist_nullifier=False,
        register_nullifier=False,
        production_required=False,
    )
    assert decision.bootstrap_allowed is True
    assert decision.nonce_membership_status == "verified"


def test_invite_bundle_cli_rejects_out_of_range_nonce_index(tmp_path: Path) -> None:
    batch_path = tmp_path / "batch.json"
    _write_batch(batch_path)

    result = _run_cli(
        "identity",
        "invite",
        "bundle",
        str(batch_path),
        "--nonce-index",
        "4",
        "--enable-invites",
    )

    assert result.returncode != 0
    assert "invite_bundle_nonce_index_invalid" in result.stderr


def test_invite_bundle_cli_requires_enable_invites(tmp_path: Path) -> None:
    batch_path = tmp_path / "batch.json"
    _write_batch(batch_path)

    result = _run_cli(
        "identity",
        "invite",
        "bundle",
        str(batch_path),
        "--nonce-index",
        "0",
    )

    assert result.returncode != 0
    assert "invite_cli_not_enabled_use_enable_invites" in result.stderr
