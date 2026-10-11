#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Live smoke for signed release discovery through the deployed VPS peer."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

from ilc_core.release.constants import ILC_UPGRADE_CHECK_ENDPOINT_ENV
from ilc_core.release.upgrade_check import UpgradeCheckError, check_for_upgrade


PHASE = "GAP-DISTRIBUTED-RELEASE-FETCH-SMOKE-00"
OUT_DIR = Path("out/gap_distributed_release_fetch_smoke_00")
PEER_ENDPOINT = "http://164.90.201.11:8081"
EXPECTED_ASSERTION_CID = "bafyreig47oqtnwxvd6feryuaw72qximlvzqb2e4oxz4c25dscmsogrurga"
HINT_PATH = OUT_DIR / "bootstrap_fetch_peers_smoke.json"
STATE_PATH = OUT_DIR / "upgrade_state_smoke.json"
RESULT_PATH = OUT_DIR / "smoke_result.json"


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(dict(payload), sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except Exception:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def _write_smoke_hint() -> None:
    _atomic_write_json(
        HINT_PATH,
        {
            "peer_endpoints": [PEER_ENDPOINT],
            "schema_version": "bootstrap_fetch_peers.v0.1",
        },
    )


def _fail(token: str, detail: str | None = None) -> None:
    message = token if detail is None else f"{token}: {detail}"
    raise SystemExit(message)


def main() -> None:
    explicit_endpoint = os.environ.get(ILC_UPGRADE_CHECK_ENDPOINT_ENV, "").strip()
    if explicit_endpoint:
        _fail("explicit_upgrade_endpoint_env_present", ILC_UPGRADE_CHECK_ENDPOINT_ENV)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if STATE_PATH.exists():
        STATE_PATH.unlink()
    _write_smoke_hint()

    try:
        result = check_for_upgrade(
            bootstrap_peer_hints_paths=[HINT_PATH],
            state_path=STATE_PATH,
        )
    except UpgradeCheckError as exc:
        if exc.token == "upgrade_check_endpoint_unreachable":
            _fail("peer_unreachable", exc.token)
        _fail("smoke_upgrade_check_failed", exc.token)

    discovery_source = result.get("discovery_source")
    if discovery_source != "bootstrap_peer_hint":
        _fail("smoke_wrong_discovery_source", repr(discovery_source))
    if result.get("release_signature_verified") is not True:
        _fail("smoke_failed_signature_not_verified")
    attestation_count = result.get("verified_attestation_count", 0)
    if not isinstance(attestation_count, int) or attestation_count < 2:
        _fail("smoke_failed_attestation_count_too_low", repr(attestation_count))
    if result.get("assertion_cid") != EXPECTED_ASSERTION_CID:
        _fail("smoke_wrong_assertion_cid", repr(result.get("assertion_cid")))

    smoke_result: dict[str, Any] = {
        **result,
        "ambient_upgrade_endpoint_env_absent": True,
        "expected_assertion_cid": EXPECTED_ASSERTION_CID,
        "hint_path": str(HINT_PATH),
        "phase": PHASE,
        "peer_endpoint": PEER_ENDPOINT,
        "result_path": str(RESULT_PATH),
        "state_path": str(STATE_PATH),
    }
    _atomic_write_json(RESULT_PATH, smoke_result)
    print(json.dumps(smoke_result, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
