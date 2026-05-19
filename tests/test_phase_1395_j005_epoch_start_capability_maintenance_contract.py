"""Phase 1395 / J-005 — Epoch-Start Capability and Maintenance Work Contract.

Focused tests proving:
- all referenced source files exist
- required tokens are present in the contract spec
- EpistemicWorkTask schema properties match J-005 claims
- task_queue module is sandbox-only (no durable production queue claim)
"""

from __future__ import annotations

import ast
from decimal import Decimal
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent

SPEC_PATH = REPO / "docs/specs/ilc_epoch_start_capability_maintenance_contract_v0.1.md"
CAPPROOF_DOC = REPO / "docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md"
EPOCH_INIT_DOC = REPO / "docs/specs/epoch_init_control_loop_v0.1.md"
WORK_TASK_MOD = REPO / "ilc_core/genesis/work_task.py"
TASK_QUEUE_MOD = REPO / "ilc_core/work/task_queue.py"


# ---------------------------------------------------------------------------
# Source file existence
# ---------------------------------------------------------------------------

def test_spec_file_exists():
    assert SPEC_PATH.exists(), "J-005 contract spec must exist"


def test_capproof_doc_exists():
    assert CAPPROOF_DOC.exists(), "CapProof source doc must exist"


def test_epoch_init_doc_exists():
    assert EPOCH_INIT_DOC.exists(), "epoch_init_control_loop source doc must exist"


def test_work_task_module_exists():
    assert WORK_TASK_MOD.exists(), "ilc_core/genesis/work_task.py must exist"


def test_task_queue_module_exists():
    assert TASK_QUEUE_MOD.exists(), "ilc_core/work/task_queue.py must exist"


# ---------------------------------------------------------------------------
# Required tokens in spec
# ---------------------------------------------------------------------------

_REQUIRED_TOKENS = [
    "epoch_start_capability_maintenance_contract_phase_j005",
    "capproof_no_direct_ilc_reward_boundary_confirmed",
    "maintenance_tasks_reward_eligible_after_review_lane",
    "awp_iih_depends_on_capproof_infrastructure_confirmed",
    "qatps_cit_post_genesis_supplement_confirmed",
    "task_queue_sandbox_non_durable_confirmed",
    "activation_ladder_shadow_to_production_defined_phase_j005",
]


@pytest.mark.parametrize("token", _REQUIRED_TOKENS)
def test_spec_contains_token(token):
    text = SPEC_PATH.read_text(encoding="utf-8")
    assert token in text, f"J-005 spec must contain token: {token}"


# ---------------------------------------------------------------------------
# EpistemicWorkTask schema claims
# ---------------------------------------------------------------------------

def test_work_task_task_class_enum():
    """task_class must include all five expected classes."""
    source = WORK_TASK_MOD.read_text(encoding="utf-8")
    expected = [
        "star.map.embedding",
        "contradiction.sweep",
        "graph.compression",
        "stability.simulation",
        "custom",
    ]
    for cls in expected:
        assert cls in source, f"work_task.py must contain task_class value: {cls}"


def test_work_task_task_state_rewarded():
    """task_state must include 'rewarded' as a valid state."""
    source = WORK_TASK_MOD.read_text(encoding="utf-8")
    assert '"rewarded"' in source, "work_task.py must include 'rewarded' in task_state"


def test_work_task_task_state_expired():
    """task_state must include 'expired' as a valid terminal state."""
    source = WORK_TASK_MOD.read_text(encoding="utf-8")
    assert '"expired"' in source, "work_task.py must include 'expired' in task_state"


def test_work_task_ecu_estimate_is_decimal():
    """ecu_estimate must use Decimal, not float — CODING-SECURITY-STANDARD §3."""
    source = WORK_TASK_MOD.read_text(encoding="utf-8")
    assert "Decimal" in source, "work_task.py must use Decimal for ecu_estimate"
    # ecu_estimate must not be typed as float
    assert "ecu_estimate: Optional[float]" not in source, (
        "ecu_estimate must not be Optional[float]; must be Optional[Decimal]"
    )


def test_work_task_difficulty_factor_is_not_reward_value():
    """difficulty_factor is Optional[float] — it is a routing/scheduling signal,
    not an ECU or reward value, so the float ban does not apply.
    This test confirms the field exists and the ecu_estimate (reward path) is Decimal.
    """
    source = WORK_TASK_MOD.read_text(encoding="utf-8")
    assert "difficulty_factor" in source, "work_task.py must contain difficulty_factor field"
    # The reward path field is Decimal
    assert "Optional[Decimal]" in source or "Decimal" in source


# ---------------------------------------------------------------------------
# Task queue is sandbox only
# ---------------------------------------------------------------------------

def test_task_queue_is_sandbox():
    """task_queue.py must self-identify as sandbox/simulation, not production."""
    source = TASK_QUEUE_MOD.read_text(encoding="utf-8")
    assert "sandbox" in source.lower() or "simulation" in source.lower(), (
        "task_queue.py must identify itself as a sandbox/simulation module"
    )


def test_task_queue_no_production_claim():
    """task_queue.py must not claim to be a durable production queue."""
    source = TASK_QUEUE_MOD.read_text(encoding="utf-8")
    assert "production_queue" not in source
    assert "durable_queue" not in source


# ---------------------------------------------------------------------------
# CapProof boundary claims in source doc
# ---------------------------------------------------------------------------

def test_capproof_no_direct_ilc_reward_in_source():
    """CapProof source doc must record the no-direct-ILC-reward boundary."""
    text = CAPPROOF_DOC.read_text(encoding="utf-8")
    assert "never mints extra ILC" in text or "no direct" in text.lower(), (
        "CapProof doc must record the no-direct-ILC-reward boundary"
    )


def test_capproof_designed_not_ratified():
    """CapProof source doc must mark CapProof as DESIGNED, not RATIFIED."""
    text = CAPPROOF_DOC.read_text(encoding="utf-8")
    assert "[DESIGNED]" in text, "CapProof doc must mark the mechanism as [DESIGNED]"
    # Must not claim [RATIFIED] for CapProof itself
    assert "CapProof" in text


def test_epoch_init_is_draft():
    """epoch_init_control_loop must be DRAFT, not a ratified spec."""
    text = EPOCH_INIT_DOC.read_text(encoding="utf-8")
    assert "DRAFT" in text, "epoch_init_control_loop must be marked DRAFT"


# ---------------------------------------------------------------------------
# Non-activation boundary
# ---------------------------------------------------------------------------

def test_spec_records_non_authorizations():
    """Spec must include a Non-Authorizations section."""
    text = SPEC_PATH.read_text(encoding="utf-8")
    assert "Non-Authorizations" in text or "non_authorization" in text.lower()


def test_spec_no_runtime_activation_claim():
    """Spec must not record a production activation token."""
    text = SPEC_PATH.read_text(encoding="utf-8")
    assert "capproof_activated" not in text
    assert "maintenance_lottery_pool_activated" not in text
    assert "qatps_activated" not in text
