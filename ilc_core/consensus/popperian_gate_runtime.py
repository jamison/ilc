# SPDX-License-Identifier: AGPL-3.0-only
"""CDL-V7 Popperian gate runtime.

Deterministic admissibility helpers for agent-decomposition outputs under the
ratified Popperian basic-statement gate.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from ilc_core.consensus.diversity_floor_runtime import CDL_V3_DEPENDENCY

CDL_V7_RUNTIME_VERSION = "cdl_v7_popperian_gate_runtime_398.v0.1"
CDL_V7_DEPENDENCY = "cdl_v7_popperian_gate_398.v0.1"

_ADMISSIBLE_CLAIM_FORMS = {
    "singular",
    "bounded_existential",
    "falsifiable_positive",
}
_ZERO = Decimal("0")
_ONE = Decimal("1")


class PopperianGateValidationError(ValueError):
    """Deterministic validation error with machine-auditable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


def _require_string(name: str, value: str) -> str:
    if not isinstance(value, str):
        raise PopperianGateValidationError(
            "cdl_v7_popperian_invalid_string",
            f"{name} must be a string",
        )
    normalized = value.strip().lower().replace("-", "_")
    if not normalized:
        raise PopperianGateValidationError(
            "cdl_v7_popperian_empty_string",
            f"{name} must be non-empty",
        )
    return normalized


def _require_bool(name: str, value: bool) -> bool:
    if not isinstance(value, bool):
        raise PopperianGateValidationError(
            "cdl_v7_popperian_invalid_bool",
            f"{name} must be a bool",
        )
    return value


def _require_unit_interval(name: str, value: object) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float) or not isinstance(value, (Decimal, int, str)):
        raise PopperianGateValidationError(
            "cdl_v7_popperian_invalid_numeric",
            f"{name} must be an exact numeric value",
        )
    try:
        number = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise PopperianGateValidationError(
            "cdl_v7_popperian_invalid_numeric",
            f"{name} must be a finite numeric value",
        ) from exc
    if not number.is_finite():
        raise PopperianGateValidationError(
            "cdl_v7_popperian_invalid_numeric",
            f"{name} must be a finite numeric value",
        )
    if number < _ZERO or number > _ONE:
        raise PopperianGateValidationError(
            "cdl_v7_popperian_out_of_range",
            f"{name} must be in [0, 1]",
        )
    return number


def is_claim_form_admissible(*, claim_form: str) -> bool:
    """Return whether claim form is admissible under CDL-V7 form constraints."""

    normalized_form = _require_string("claim_form", claim_form)
    return normalized_form in _ADMISSIBLE_CLAIM_FORMS


def passes_falsifiability_gate(*, has_falsifiable_test: bool) -> bool:
    """Return whether a decomposition includes falsifiable test structure."""

    return _require_bool("has_falsifiable_test", has_falsifiable_test)


def reject_inadmissible_counterexample(*, is_inadmissible_counterexample: bool) -> bool:
    """Reject inadmissible counterexample outputs deterministically."""

    flagged = _require_bool("is_inadmissible_counterexample", is_inadmissible_counterexample)
    return not flagged


def meets_reproducibility_threshold(
    *,
    agreement_score: object,
    reproducibility_threshold: object = Decimal("0.85"),
) -> bool:
    """Check cross-agent reproducibility threshold compliance."""

    agreement = _require_unit_interval("agreement_score", agreement_score)
    threshold = _require_unit_interval("reproducibility_threshold", reproducibility_threshold)
    return agreement >= threshold


def evaluate_decomposition_admissibility(
    *,
    claim_form: str,
    has_falsifiable_test: bool,
    is_inadmissible_counterexample: bool,
    agreement_score: object,
    reproducibility_threshold: object = Decimal("0.85"),
) -> bool:
    """Compute deterministic top-level Popperian admissibility verdict."""

    form_ok = is_claim_form_admissible(claim_form=claim_form)
    falsifiable_ok = passes_falsifiability_gate(has_falsifiable_test=has_falsifiable_test)
    counterexample_ok = reject_inadmissible_counterexample(
        is_inadmissible_counterexample=is_inadmissible_counterexample
    )
    reproducible_ok = meets_reproducibility_threshold(
        agreement_score=agreement_score,
        reproducibility_threshold=reproducibility_threshold,
    )
    return form_ok and falsifiable_ok and counterexample_ok and reproducible_ok
