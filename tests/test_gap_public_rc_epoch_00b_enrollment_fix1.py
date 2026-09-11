# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
from pathlib import Path

from ilc_core.epoch.genesis_settlement_destination import GENESIS_AGENT1_AGENT_ID


ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = ROOT / "out/gap_public_rc_epoch_00b/genesis_install_receipt.json"
BINDING_PATH = (
    ROOT
    / "docs/specs/ilc_genesis_validator_provenance_binding_record_GAP_GENESIS_VALIDATOR_PROVENANCE_BINDING_00_v0.1.json"
)
REPROVISION_RECEIPT_PATH = ROOT / "out/gap_vps_validator_reprovision_00/reprovision_receipt.json"
STATUS_PATH = ROOT / "docs/phases/STATUS.md"


def _receipt() -> dict[str, object]:
    return json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))


def _binding() -> dict[str, object]:
    return json.loads(BINDING_PATH.read_text(encoding="utf-8"))


def test_epoch_00b_receipt_records_path_b_enrollment_authority() -> None:
    receipt = _receipt()
    assert receipt["schema_version"] == "GAP_PUBLIC_RC_EPOCH_00b_path_b_v0.1"
    assert receipt["enrollment_method"] == "genesis_validator_provenance_binding_signed"
    assert receipt["enrollment_authority_signature_verified"] is True
    assert receipt["genesis_agent_id"] == GENESIS_AGENT1_AGENT_ID
    assert receipt["all_validators_enrolled"] is True


def test_epoch_00b_receipt_matches_signed_provenance_binding() -> None:
    receipt = _receipt()
    binding = _binding()
    assert receipt["genesis_agent_id"] == binding["genesis_agent_cid"]
    assert receipt["enrollment_authority_issued_at_epoch"] == binding["issued_at_epoch"] == 0
    assert receipt["enrollment_authority_scope"] == binding["scope"]
    assert receipt["enrollment_authority_network_id"] == binding["network_id"] == "public-rc"
    assert receipt["enrollment_authority_sig_scheme"] == binding["binding_sig_scheme"] == "mldsa"

    receipt_validators = {
        str(validator["slot"]): validator
        for validator in receipt["validators"]  # type: ignore[index]
    }
    binding_validators = {
        str(validator["slot"]): validator
        for validator in binding["bound_validators"]  # type: ignore[index]
    }
    assert set(receipt_validators) == set(binding_validators) == {
        "validator_1",
        "validator_2",
        "validator_3",
        "validator_4",
    }
    for slot, receipt_validator in receipt_validators.items():
        binding_validator = binding_validators[slot]
        assert receipt_validator["validator_agent_id"] == binding_validator["validator_agent_id"]
        assert receipt_validator["assertion_content_sha256"] == binding_validator["assertion_content_sha256"]
        assert receipt_validator["grpc_port"] == binding_validator["grpc_port"]
        assert receipt_validator["epoch_at_enrollment"] == 0
        assert receipt_validator["enrollment_status"] == "BOUND_VIA_PROVENANCE_BINDING"


def test_epoch_00b_receipt_matches_reprovisioned_validator_set() -> None:
    receipt = _receipt()
    reprovision = json.loads(REPROVISION_RECEIPT_PATH.read_text(encoding="utf-8"))
    receipt_agent_ids = {
        str(validator["slot"]): validator["validator_agent_id"]
        for validator in receipt["validators"]  # type: ignore[index]
    }
    reprovision_agent_ids = {
        str(slot["slot"]): slot["agent_id_new"]
        for slot in reprovision["slots"]
    }
    assert receipt_agent_ids == reprovision_agent_ids


def test_epoch_00b_output_token_emitted_once_as_completion() -> None:
    status = STATUS_PATH.read_text(encoding="utf-8")
    token = "genesis_agent_installed_public_rc_validators_GAP_PUBLIC_RC_EPOCH_00b"
    completion_lines = [
        line
        for line in status.splitlines()
        if line == f"**Output token:** `{token}`"
    ]
    assert completion_lines == [f"**Output token:** `{token}`"]
