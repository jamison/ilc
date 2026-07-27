from __future__ import annotations

import copy
import json
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.economics.onboarding import OnboardingVault
from ilc_core.economics import passive_ecu_attribution_runtime as passive_ecu
from ilc_core.ledger import lmdb_backend
from ilc_core.node import (
    canonical_node_dissemination_vectors,
    canonical_node_schema_core_vectors,
    canonical_validation_lifecycle_vectors,
    generate_node_dissemination_record,
    generate_node_schema_core_record,
    generate_validation_lifecycle_record,
)


CLASSIFICATION_PATH = Path("docs/specs/ilc_fix75_numeric_determinism_classification_v0.1.json")


def test_fix75_classification_receipt_covers_all_p2_rows() -> None:
    payload = json.loads(CLASSIFICATION_PATH.read_text(encoding="utf-8"))

    assert payload["row_count"] == 149
    assert len(payload["entries"]) == 149
    assert payload["classification_counts"]["protocol-forbidden"] == 11
    assert payload["code_change_required_count"] == 11


def test_node_schema_core_rejects_non_finite_before_digest() -> None:
    vector = copy.deepcopy(canonical_node_schema_core_vectors()[0])
    vector["authored_payload"]["payload"]["bad_numeric"] = float("nan")

    with pytest.raises(ValueError):
        generate_node_schema_core_record(vector)


def test_validation_lifecycle_rejects_non_finite_before_digest() -> None:
    vector = copy.deepcopy(canonical_validation_lifecycle_vectors()[0])
    vector["authored_payload"]["payload"]["bad_numeric"] = float("nan")

    with pytest.raises(ValueError):
        generate_validation_lifecycle_record(vector)


def test_node_dissemination_rejects_non_finite_before_digest() -> None:
    vector = copy.deepcopy(canonical_node_dissemination_vectors()[0])
    vector["authored_payload"]["payload"]["bad_numeric"] = float("nan")

    with pytest.raises(ValueError):
        generate_node_dissemination_record(vector)


def test_passive_ecu_decimal_runtime_rejects_finite_float_ingress() -> None:
    with pytest.raises(ValueError, match="base_reward_must_be_non_negative_decimal"):
        passive_ecu.compute_passive_ecu(1.0, Decimal("0.5"), Decimal("0.5"))  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="centrality_score_must_be_non_negative_decimal"):
        passive_ecu.compute_passive_ecu(Decimal("1"), 0.5, Decimal("0.5"))  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="q_i_must_be_decimal_in_unit_interval"):
        passive_ecu.compute_passive_ecu(Decimal("1"), Decimal("0.5"), 0.5)  # type: ignore[arg-type]


def test_onboarding_repayment_rejects_finite_float_ingress() -> None:
    vault = OnboardingVault()
    vault.request_starter_credit("agent:fix75")

    with pytest.raises(ValueError, match="onboarding_earnings_invalid"):
        vault.process_repayment("agent:fix75", 0.5)  # type: ignore[arg-type]


def test_lmdb_backend_json_encoder_rejects_non_finite_payloads() -> None:
    with pytest.raises(ValueError):
        lmdb_backend._encode_json({"bad_numeric": float("nan")})
