from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.analysis.reuse_diversity_invariants import (
    compute_reuse_diversity_multiplier,
    validate_reuse_diversity_policy,
)
from ilc_core.exceptions import NodeValueKernelError


def test_phase_223_policy_rejects_non_finite_numeric_fields() -> None:
    with pytest.raises(NodeValueKernelError) as max_share_exc:
        validate_reuse_diversity_policy(
            {
                "min_distinct_agents": 2,
                "max_single_agent_share": float("inf"),
                "penalty_floor": 0.85,
            }
        )
    assert str(max_share_exc.value) == "reuse_diversity_invalid_max_single_agent_share"

    with pytest.raises(NodeValueKernelError) as floor_exc:
        validate_reuse_diversity_policy(
            {
                "min_distinct_agents": 2,
                "max_single_agent_share": 0.75,
                "penalty_floor": float("nan"),
            }
        )
    assert str(floor_exc.value) == "reuse_diversity_invalid_penalty_floor"


def test_phase_223_metrics_reject_non_finite_numeric_fields() -> None:
    with pytest.raises(NodeValueKernelError) as reuse_exc:
        compute_reuse_diversity_multiplier(
            {
                "reuse_count": float("inf"),
                "distinct_agent_count": 2.0,
                "max_agent_reuse_share": 0.5,
            }
        )
    assert str(reuse_exc.value) == "reuse_diversity_invalid_reuse_count"

    with pytest.raises(NodeValueKernelError) as distinct_exc:
        compute_reuse_diversity_multiplier(
            {
                "reuse_count": 3.0,
                "distinct_agent_count": float("nan"),
                "max_agent_reuse_share": 0.5,
            }
        )
    assert str(distinct_exc.value) == "reuse_diversity_invalid_distinct_agent_count"

    with pytest.raises(NodeValueKernelError) as share_exc:
        compute_reuse_diversity_multiplier(
            {
                "reuse_count": 3.0,
                "distinct_agent_count": 2.0,
                "max_agent_reuse_share": float("inf"),
            }
        )
    assert str(share_exc.value) == "reuse_diversity_invalid_max_agent_reuse_share"


def test_phase_223_analysis_modules_do_not_use_broad_exception_handlers() -> None:
    # Entries here must have a justification comment adjacent to the except line
    # in the source file explaining why broad exception handling is required.
    _ALLOWLIST: frozenset[str] = frozenset(
        {
            # Wraps a third-party encoder call; encoder libraries raise varied
            # exception types that cannot be enumerated without coupling to
            # specific encoder implementations.
            "ilc_core/analysis/embedding_pipeline.py:328",
        }
    )

    analysis_dir = Path("ilc_core/analysis")
    violations: list[str] = []

    for path in sorted(analysis_dir.glob("*.py")):
        for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if stripped.startswith("except Exception") or stripped == "except:":
                entry = f"{path}:{index}"
                if entry not in _ALLOWLIST:
                    violations.append(entry)

    assert violations == []
