# SPDX-License-Identifier: AGPL-3.0-only
"""Bounded CapProof v1 multiplier from CDL-092 and CDL-115."""

from __future__ import annotations

from decimal import Decimal, localcontext

from .capability_vector import CapabilityVector

CAPPROOF_MULTIPLIER_MIN = Decimal("0.85")
CAPPROOF_MULTIPLIER_BASELINE = Decimal("1.00")
CAPPROOF_MULTIPLIER_MAX = Decimal("1.15")
CAPPROOF_MULTIPLIER_DECIMAL_PRECISION = 50

_BAND_WIDTH = CAPPROOF_MULTIPLIER_MAX - CAPPROOF_MULTIPLIER_MIN
_PROBE_COUNT = Decimal("4")
_GEMM_SCALE = Decimal("100000")
_INFER_SCALE = Decimal("10000")
_BANDWIDTH_SCALE = Decimal("1000")
_GRAPH_SCALE = Decimal("10000")


def compute_capproof_multiplier(cv: CapabilityVector) -> Decimal:
    """Return one bounded high-precision Decimal multiplier for one capability vector."""

    if cv.det_pass is False:
        # CDL-115-DELIBERATION-Q3: det_pass=False behavior remains open.
        return CAPPROOF_MULTIPLIER_MIN

    with localcontext() as ctx:
        ctx.prec = CAPPROOF_MULTIPLIER_DECIMAL_PRECISION
        score = (
            _unit_interval(cv.gemm_gops, _GEMM_SCALE)
            + _unit_interval(cv.infer_tps, _INFER_SCALE)
            + _unit_interval(cv.bw_gbps, _BANDWIDTH_SCALE)
            + _unit_interval(cv.graph_mteps, _GRAPH_SCALE)
        ) / _PROBE_COUNT
        candidate = CAPPROOF_MULTIPLIER_MIN + (_BAND_WIDTH * score)

    return _clamp(candidate)


def _unit_interval(value: Decimal, scale: Decimal) -> Decimal:
    if value <= Decimal("0"):
        return Decimal("0")
    return value / (value + scale)


def _clamp(value: Decimal) -> Decimal:
    if value < CAPPROOF_MULTIPLIER_MIN:
        return CAPPROOF_MULTIPLIER_MIN
    if value > CAPPROOF_MULTIPLIER_MAX:
        return CAPPROOF_MULTIPLIER_MAX
    return value
