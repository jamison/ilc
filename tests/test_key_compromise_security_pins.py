from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.security.key_compromise_runtime import (
    TRIGGER_CUSTODY_LOSS,
    KeyCompromiseResponseRuntime,
)
from ilc_core.security.signer_lineage_runtime import REVOKED, SignerLineageRegistry


REPO_ROOT = Path(__file__).resolve().parents[1]


def _registry() -> SignerLineageRegistry:
    registry = SignerLineageRegistry()
    registry.register(
        lineage_id="lineage-alpha",
        canonical_root_key="root-001",
        authority_recovery_key="recovery-001",
        operational_signer_key="ops-001",
        authorizer_signer_id="root-001",
        reason_code="genesis_register",
        event_ts="2026-02-20T00:00:00Z",
    )
    return registry


def test_key_compromise_runtime_not_imported_by_public_server_surface() -> None:
    server_source = (REPO_ROOT / "ilc_core/server.py").read_text(encoding="utf-8")
    d2d_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (REPO_ROOT / "ilc_core/network/d2d").glob("*.py")
    )

    assert "key_compromise_runtime" not in server_source
    assert "KeyCompromiseResponseRuntime" not in server_source
    assert "key_compromise_runtime" not in d2d_sources
    assert "KeyCompromiseResponseRuntime" not in d2d_sources


def test_recover_failure_after_revoke_leaves_lineage_revoked_until_activation_fix(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _registry()
    runtime = KeyCompromiseResponseRuntime(registry)

    def fail_recover(**_: object) -> None:
        raise ValueError("forced_recovery_failure_phase_1573am")

    monkeypatch.setattr(registry, "recover", fail_recover)

    with pytest.raises(ValueError, match="forced_recovery_failure_phase_1573am"):
        runtime.respond_to_compromise(
            lineage_id="lineage-alpha",
            compromised_signer_id="ops-001",
            trigger_class=TRIGGER_CUSTODY_LOSS,
            event_ts="2026-02-20T00:11:00Z",
            containment_authorizer_signer_id="root-001",
            replacement_signer_id="ops-002",
            recovery_ticket_id="ticket-001",
            recovery_authorizer_signer_id="recovery-001",
        )

    assert registry.entries["lineage-alpha"].state == REVOKED
    assert runtime.incidents == ()


def test_key_compromise_runtime_records_transactionality_activation_prerequisite() -> None:
    source = (REPO_ROOT / "ilc_core/security/key_compromise_runtime.py").read_text(
        encoding="utf-8"
    )

    assert "phase_1573am_activation_prerequisite_transactional_revoke_recover" in source
    assert "If recover() raises after revoke()" in source


def test_phase_1573am_status_records_key_compromise_review_token() -> None:
    status = (REPO_ROOT / "docs/phases/STATUS.md").read_text(encoding="utf-8")

    assert "key_compromise_transactionality_reviewed_phase_1573am" in status
