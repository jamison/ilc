"""
Tests for event log validators (lenient validators for epoch_config, task_outcome, epoch_summary).
"""

import pytest
from datetime import datetime, timezone

from ilc_core.exceptions import EventLogValidationError
from ilc_core.protocol.event_log import (
    validate_epoch_config_payload,
    validate_task_outcome_payload,
    validate_epoch_summary_payload,
    make_epoch_config_event,
    make_task_outcome_event,
    make_epoch_summary_event,
)


class TestEpochConfigValidator:
    def test_valid_epoch_config_passes(self):
        """Valid epoch_config payload should pass validation."""
        payload = {
            "epoch_index": 42,
            "benchmark_suite_id": "devnet_synthetic_v0.1",
            "created_at": "2026-02-03T08:00:00Z",
            "namespace_id": "test_namespace",
        }
        # Should not raise
        validate_epoch_config_payload(payload)

    def test_extra_keys_allowed(self):
        """Extra keys should be allowed (forward compatible)."""
        payload = {
            "epoch_index": 42,
            "benchmark_suite_id": "devnet_synthetic_v0.1",
            "created_at": "2026-02-03T08:00:00Z",
            "namespace_id": "test_namespace",
            "extra_field": "should_be_allowed",
            "another_extra": {"nested": True},
        }
        # Should not raise
        validate_epoch_config_payload(payload)

    def test_missing_required_key_fails(self):
        """Missing required key should raise ValueError."""
        payload = {
            "epoch_index": 42,
            # Missing benchmark_suite_id
            "created_at": "2026-02-03T08:00:00Z",
            "namespace_id": "test_namespace",
        }
        with pytest.raises(ValueError, match="Missing required epoch_config fields"):
            validate_epoch_config_payload(payload)

    def test_invalid_epoch_index_type_fails(self):
        """Invalid epoch_index type should raise ValueError."""
        payload = {
            "epoch_index": "not_an_int",
            "benchmark_suite_id": "test",
            "created_at": "2026-02-03T08:00:00Z",
            "namespace_id": "test",
        }
        with pytest.raises(ValueError, match="epoch_index must be a non-negative integer"):
            validate_epoch_config_payload(payload)


class TestTaskOutcomeValidator:
    def test_valid_task_outcome_passes(self):
        """Valid task_outcome payload should pass validation."""
        payload = {
            "agent_id": "agent_1",
            "epoch_index": 10,
            "namespace_id": "ns_1",
            "task_type": "reasoning",
            "reward": "5.5",
            "success": True,
        }
        validate_task_outcome_payload(payload)

    def test_extra_keys_allowed(self):
        """Extra keys should be allowed."""
        payload = {
            "agent_id": "agent_1",
            "epoch_index": 10,
            "namespace_id": "ns_1",
            "task_type": "reasoning",
            "reward": "5.5",
            "success": True,
            "node_id": "node_1",
            "problem_space": "math",
        }
        validate_task_outcome_payload(payload)

    def test_missing_required_key_fails(self):
        """Missing required key should raise ValueError."""
        payload = {
            "agent_id": "agent_1",
            # Missing epoch_index
            "namespace_id": "ns_1",
            "task_type": "reasoning",
            "reward": 5.5,
            "success": True,
        }
        with pytest.raises(ValueError, match="Missing required task_outcome fields"):
            validate_task_outcome_payload(payload)

    def test_negative_reward_fails(self):
        """Negative reward should raise ValueError."""
        payload = {
            "agent_id": "agent_1",
            "epoch_index": 10,
            "namespace_id": "ns_1",
            "task_type": "reasoning",
            "reward": -1.0,
            "success": True,
        }
        with pytest.raises(ValueError, match="reward must be a non-negative number"):
            validate_task_outcome_payload(payload)


class TestEpochSummaryValidator:
    def test_valid_epoch_summary_passes(self):
        """Valid epoch_summary payload should pass validation."""
        payload = {
            "epoch_index": 100,
            "total_tasks": 50,
            "total_reward": "250",
        }
        validate_epoch_summary_payload(payload)

    def test_extra_keys_allowed(self):
        """Extra keys should be allowed."""
        payload = {
            "epoch_index": 100,
            "total_tasks": 50,
            "total_reward": "250",
            "backlog_count": 5,
            "stress_regime": "medium",
        }
        validate_epoch_summary_payload(payload)

    def test_missing_required_key_fails(self):
        """Missing required key should raise ValueError."""
        payload = {
            "epoch_index": 100,
            # Missing total_tasks
            "total_reward": 250.0,
        }
        with pytest.raises(ValueError, match="Missing required epoch_summary fields"):
            validate_epoch_summary_payload(payload)


class TestHelperConstructors:
    def test_make_epoch_config_event(self):
        """Helper should construct valid epoch_config event."""
        evt = make_epoch_config_event(
            epoch_index=42,
            benchmark_suite_id="test_suite",
            created_at="2026-02-03T08:00:00Z",
            namespace_id="test_ns",
            extra_field="allowed",
        )
        assert evt.kind == "epoch_config"
        assert evt.payload["epoch_index"] == 42
        assert evt.payload["extra_field"] == "allowed"

    def test_make_task_outcome_event(self):
        """Helper should construct valid task_outcome event."""
        evt = make_task_outcome_event(
            agent_id="agent_1",
            epoch_index=10,
            namespace_id="ns_1",
            task_type="reasoning",
            reward=5.5,
            success=True,
            node_id="node_1",
        )
        assert evt.kind == "task_outcome"
        assert evt.payload["agent_id"] == "agent_1"
        assert evt.payload["node_id"] == "node_1"
        assert evt.payload["reward"] == "5.5"

    def test_make_epoch_summary_event(self):
        """Helper should construct valid epoch_summary event."""
        evt = make_epoch_summary_event(
            epoch_index=100,
            total_tasks=50,
            total_reward=250.0,
            backlog_count=5,
        )
        assert evt.kind == "epoch_summary"
        assert evt.payload["total_tasks"] == 50
        assert evt.payload["backlog_count"] == 5
        assert evt.payload["total_reward"] == "250"

    @pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity", float("nan"), float("inf"), float("-inf")])
    def test_non_finite_values_rejected(self, value: object):
        with pytest.raises(EventLogValidationError):
            validate_task_outcome_payload(
                {
                    "agent_id": "agent_1",
                    "epoch_index": 10,
                    "namespace_id": "ns_1",
                    "task_type": "reasoning",
                    "reward": value,
                    "success": True,
                }
            )
        with pytest.raises(EventLogValidationError):
            validate_epoch_summary_payload(
                {
                    "epoch_index": 100,
                    "total_tasks": 50,
                    "total_reward": value,
                }
            )
        with pytest.raises(EventLogValidationError):
            make_task_outcome_event(
                agent_id="agent_1",
                epoch_index=10,
                namespace_id="ns_1",
                task_type="reasoning",
                reward=value,  # type: ignore[arg-type]
                success=True,
            )
        with pytest.raises(EventLogValidationError):
            make_epoch_summary_event(
                epoch_index=100,
                total_tasks=50,
                total_reward=value,  # type: ignore[arg-type]
            )


class TestDomainExceptionTypeContracts:
    def test_epoch_config_uses_event_log_validation_error(self):
        payload = {
            "epoch_index": "not_an_int",
            "benchmark_suite_id": "suite",
            "created_at": "2026-02-03T08:00:00Z",
            "namespace_id": "ns",
        }
        with pytest.raises(EventLogValidationError):
            validate_epoch_config_payload(payload)

    def test_task_outcome_uses_event_log_validation_error(self):
        payload = {
            "agent_id": "agent_1",
            "epoch_index": 10,
            "namespace_id": "ns_1",
            "task_type": "reasoning",
            "reward": -1.0,
            "success": True,
        }
        with pytest.raises(EventLogValidationError):
            validate_task_outcome_payload(payload)

    def test_epoch_summary_uses_event_log_validation_error(self):
        payload = {
            "epoch_index": 100,
            "total_reward": 250.0,
        }
        with pytest.raises(EventLogValidationError):
            validate_epoch_summary_payload(payload)
