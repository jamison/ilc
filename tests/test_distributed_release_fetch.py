from __future__ import annotations

from typing import Any

import pytest

from ilc_core.crypto.pq_signature_verify import _MLDSA_PK_HEX_LENGTH, _MLDSA_SIG_HEX_LENGTH
from ilc_core.identity.first_run_provisioning import fetch_distributed_release_peers


MLDSA_PUBKEY_HEX = "b" * _MLDSA_PK_HEX_LENGTH


def _fetch_material() -> dict[str, Any]:
    return {
        "bootstrap_fetch_bundle_cid": "bafybootstrap",
        "bootstrap_fetch_genesis_authority_pubkey_hex": MLDSA_PUBKEY_HEX,
        "bootstrap_fetch_seed_peer_endpoint": "https://seed.ilc.example:443",
    }


def _bundle() -> dict[str, Any]:
    return {
        "bundle_cid": "bafybootstrap",
        "cdl_version": "cdl_079_bootstrap_bundle_v1",
        "genesis_cid": "bafygenesis",
        "peers": [{"endpoint": "https://peer-a.ilc.example:443", "node_id": "node-a"}],
        "schema_version": "bootstrap_bundle_v1",
        "signature": "a" * _MLDSA_SIG_HEX_LENGTH,
        "signed_by": MLDSA_PUBKEY_HEX,
    }


def test_distributed_release_fetch_skips_without_material() -> None:
    result = fetch_distributed_release_peers({}, {"known_peer_hints_verified": 0})

    assert result["bootstrap_fetch_status"] == "skipped_not_configured"
    assert result["bootstrap_fetch_peers_count"] == 0


def test_distributed_release_fetch_skips_when_known_peers_are_sufficient() -> None:
    result = fetch_distributed_release_peers(
        {},
        {"known_peer_hints_verified": 3},
    )

    assert result["bootstrap_fetch_status"] == "skipped_known_peers_sufficient"


def test_distributed_release_fetch_requires_complete_material() -> None:
    with pytest.raises(ValueError, match="bootstrap_fetch_material_incomplete"):
        fetch_distributed_release_peers(
            {"bootstrap_fetch_seed_peer_endpoint": "https://seed.ilc.example:443"},
            {"known_peer_hints_verified": 0},
        )


def test_distributed_release_fetch_rejects_bad_signature_before_extract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from ilc_core.network.d2d import bootstrap_fetch_runtime

    calls: list[str] = []
    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "fetch_bootstrap_bundle",
        lambda _seed, _cid: _bundle(),
    )

    def fake_verify(_bundle: dict[str, Any], _pubkey: str) -> bool:
        calls.append("verify")
        return False

    def fake_extract(_bundle: dict[str, Any]) -> list[str]:
        calls.append("extract")
        return ["https://peer-a.ilc.example:443"]

    monkeypatch.setattr(bootstrap_fetch_runtime, "verify_bootstrap_bundle_signature", fake_verify)
    monkeypatch.setattr(bootstrap_fetch_runtime, "extract_peer_endpoints", fake_extract)

    with pytest.raises(ValueError, match="bootstrap_fetch_bundle_signature_invalid"):
        fetch_distributed_release_peers(
            _fetch_material(),
            {"known_peer_hints_verified": 0},
        )

    assert calls == ["verify"]


def test_distributed_release_fetch_success(monkeypatch: pytest.MonkeyPatch) -> None:
    from ilc_core.network.d2d import bootstrap_fetch_runtime

    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "fetch_bootstrap_bundle",
        lambda _seed, _cid: _bundle(),
    )
    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "verify_bootstrap_bundle_signature",
        lambda _bundle, _pubkey: True,
    )
    monkeypatch.setattr(
        bootstrap_fetch_runtime,
        "extract_peer_endpoints",
        lambda _bundle: ["https://peer-a.ilc.example:443"],
    )

    result = fetch_distributed_release_peers(
        _fetch_material(),
        {"known_peer_hints_verified": 0},
    )

    assert result["bootstrap_fetch_status"] == "fetched"
    assert result["bootstrap_fetch_peers_count"] == 1
    assert result["bootstrap_fetch_peer_endpoints"] == ["https://peer-a.ilc.example:443"]
