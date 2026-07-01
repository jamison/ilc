from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

import ilc_core.identity.pq_agent_sign_bridge as pq_agent_sign_bridge
from ilc_core.identity.pq_agent_sign_bridge import sign_agent_submission
from tests.test_phase_1568_fix2l_rehearsal_economics_record import (
    _accepted_submissions,
    _panel_payload,
)
from tools.testbed.rehearsal_economics import (
    build_rehearsal_economics_record,
    verify_rehearsal_economics_record,
)


PHASE_1431_MANIFEST = Path("docs/specs/ilc_rehearsal_agent_identity_manifest_1431_v0.1.md")
PHASE_1431_AGENT_IDS = [
    "c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9",
    "09feeae6017ac091f6cf8dc410f6814bbfe018843ac76dffb835e5c44f18e2823daf4922c1be03ee87a4d9e70d4971e5",
    "5d7e8e092f42722dd7f92a504e29ed88c72ae44323d8786025fb3a380f841d6c2a448e9426ac3460bae3abb33881b6fc",
    "d6592166bf9c15841e8c249007f261760b9808b5a85f3c0ebb8b7cd3527155cca279870dca142eb3bc9f42eb2f20b36c",
    "bfc75431f3941080d4723063b17c6c7086f5b010952b5273839d250b30d70ab0f1799c0831a4ba6b1ad7ea8f09793c74",
    "4842b1bee669793b03e7cfbb01f3b5ae7e54a34a093bd7c88f95539d67ce973c084029e00abc79e4410398f6f712dec1",
    "dc6f1d4775c9c0a6c40ec57dd81c1fc0741d924013060ad0c9323099f12196ddabe007e0f4ba3fd89aed0e397c622ad7",
]


def test_fix2o_stress_uses_phase_1431_public_agent_ids() -> None:
    manifest_text = PHASE_1431_MANIFEST.read_text(encoding="utf-8")

    for agent_id in PHASE_1431_AGENT_IDS:
        assert f"agent_id:                 {agent_id}" in manifest_text


def test_fix2o_process_seed_cache_scales_to_many_signatures(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    pq_agent_sign_bridge.clear_process_seed_cache()
    monkeypatch.setenv("ILC_PQ_AGENT_SIGN_PROCESS_SEED_CACHE", "1")
    fake_binary = tmp_path / "pq-agent-sign"
    fake_binary.write_text("#!/bin/sh\n", encoding="utf-8")
    fake_manifest = tmp_path / "manifest.md"
    fake_manifest.write_text("# manifest\n", encoding="utf-8")
    prompts_by_agent: dict[str, int] = {agent_id: 0 for agent_id in PHASE_1431_AGENT_IDS}
    run_count = 0

    class Tty:
        def isatty(self) -> bool:
            return True

    def fake_getpass(*, prompt: str, stream: object) -> str:
        for agent_id in PHASE_1431_AGENT_IDS:
            if agent_id[:8] in prompt:
                prompts_by_agent[agent_id] += 1
                break
        return "abandon " * 23 + "about"

    def fake_run(command: list[str], **kwargs: object) -> SimpleNamespace:
        nonlocal run_count
        run_count += 1
        return SimpleNamespace(returncode=0, stdout="34" * 3309, stderr="")

    monkeypatch.setattr(pq_agent_sign_bridge.sys, "stdin", Tty())
    monkeypatch.setattr(pq_agent_sign_bridge.getpass, "getpass", fake_getpass)
    monkeypatch.setattr(pq_agent_sign_bridge.subprocess, "run", fake_run)

    for index in range(100):
        agent_id = PHASE_1431_AGENT_IDS[index % len(PHASE_1431_AGENT_IDS)]
        signature = sign_agent_submission(
            agent_id_hex=agent_id,
            payload_bytes=f'{{"submission":{index}}}'.encode("ascii"),
            binary_path=str(fake_binary),
            manifest_path=str(fake_manifest),
        )
        assert signature == "34" * 3309

    assert run_count == 100
    assert prompts_by_agent == {agent_id: 1 for agent_id in PHASE_1431_AGENT_IDS}
    pq_agent_sign_bridge.clear_process_seed_cache()


def test_fix2o_rehearsal_economics_many_accelerated_epochs() -> None:
    base_claims = _panel_payload()["ecu_claim_batch"]["claims"]
    accepted_submissions = _accepted_submissions()
    settlement_roots: set[str] = set()
    total_epoch_count = 48

    for epoch in range(total_epoch_count):
        claims = []
        for claim in base_claims:
            next_claim = dict(claim)
            next_claim["claim_id"] = f"{claim['claim_id']}::epoch::{epoch:03d}"
            next_claim["epoch"] = epoch
            next_claim["amount"] = str(Decimal(str(claim["amount"])))
            claims.append(next_claim)

        record = build_rehearsal_economics_record(
            namespace_id=f"phase1568-fix2o-stress-epoch-{epoch:03d}",
            accepted_submissions=accepted_submissions,
            ecu_claims=claims,
            rehearsal_epoch=epoch,
            cumulative_issued_before_epoch_ilc=str(epoch),
            total_epoch_fees_ilc="0",
        )
        verification = verify_rehearsal_economics_record(record)
        coverage = record["cdl048_per_agent_lot_coverage"]

        assert verification["settlement_root_verified"] is True
        assert verification["cdl048_per_agent_lot_coverage_verified"] is True
        assert coverage["issuance_epoch_sequence"] == [epoch, epoch + 1, epoch + 2, epoch + 3, epoch + 4]
        assert coverage["four_issuance_epoch_intervals_covered"] == 4
        assert coverage["lot_count"] == coverage["positive_claim_count"]
        assert coverage["wallet_write_authorized"] is False
        assert coverage["ledger_write_authorized"] is False
        settlement_roots.add(record["settlement_root_hex"])

    assert len(settlement_roots) == total_epoch_count
