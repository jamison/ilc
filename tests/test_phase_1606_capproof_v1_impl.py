# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import ast
from decimal import Decimal, localcontext
from pathlib import Path

import pytest

from ilc_core.capproof import (
    CAPPROOF_MAX_METRIC_VALUE,
    CAPPROOF_V1_NO_ILC_MINT,
    CAPPROOF_DETERMINISM_PROBE_PRODUCTION_ACTIVATED,
    BandwidthProbe,
    CapabilityVector,
    CapProofValidationError,
    DeterminismProbe,
    GEMMProbe,
    GraphProbe,
    InferProbe,
    compute_capproof_multiplier,
)
from ilc_core.capproof import probe_runner
from ilc_core.capproof.probe_runner import _derive_metric

_SALT = "ab" * 32
_AGENT_ID = "a" * 96
_CAP_DIR = Path(__file__).resolve().parents[1] / "ilc_core" / "capproof"


def test_capproof_no_ilc_mint_constant_is_true() -> None:
    assert CAPPROOF_V1_NO_ILC_MINT is True


def test_determinism_probe_is_marked_scaffold_only_until_guard_clearance() -> None:
    assert CAPPROOF_DETERMINISM_PROBE_PRODUCTION_ACTIVATED is False


def test_all_probe_stubs_return_expected_field_types() -> None:
    assert isinstance(GEMMProbe().run(_SALT).gemm_gops, Decimal)
    assert isinstance(InferProbe().run(_SALT).infer_tps, Decimal)
    assert isinstance(GraphProbe().run(_SALT).graph_mteps, Decimal)
    assert isinstance(BandwidthProbe().run(_SALT).bw_gbps, Decimal)
    assert DeterminismProbe().run(_SALT).det_pass is True


def test_determinism_probe_result_depends_on_repeat_hash_consistency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    def _drifting_digest(_salt: str) -> str:
        nonlocal calls
        calls += 1
        return f"{calls:064x}"

    monkeypatch.setattr(probe_runner, "_determinism_digest", _drifting_digest)

    result = DeterminismProbe().run(_SALT)

    assert result.det_pass is False
    assert calls == 3


def test_probe_stubs_reject_mismatched_epoch_salt() -> None:
    with pytest.raises(CapProofValidationError) as exc:
        GEMMProbe().run("not-hex")
    assert exc.value.token == "capproof_epoch_salt_must_be_64_to_128_lower_hex"


def test_probe_stubs_are_epoch_salted() -> None:
    first = GEMMProbe().run(_SALT)
    second = GEMMProbe().run("cd" * 32)
    assert first.gemm_gops != second.gemm_gops


def test_capability_vector_rejects_non_decimal_metric() -> None:
    with pytest.raises(CapProofValidationError) as exc:
        CapabilityVector(
            gemm_gops="1",
            infer_tps=Decimal("1"),
            bw_gbps=Decimal("1"),
            graph_mteps=Decimal("1"),
            det_pass=True,
            epoch=1,
            agent_id=_AGENT_ID,
        )
    assert exc.value.token == "capproof_gemm_gops_must_be_decimal"


def test_capability_vector_rejects_non_finite_metric() -> None:
    with pytest.raises(CapProofValidationError) as exc:
        CapabilityVector(
            gemm_gops=Decimal("NaN"),
            infer_tps=Decimal("1"),
            bw_gbps=Decimal("1"),
            graph_mteps=Decimal("1"),
            det_pass=True,
            epoch=1,
            agent_id=_AGENT_ID,
        )
    assert exc.value.token == "capproof_gemm_gops_must_be_finite"


def test_capability_vector_rejects_negative_metric() -> None:
    with pytest.raises(CapProofValidationError) as exc:
        CapabilityVector(
            gemm_gops=Decimal("-1"),
            infer_tps=Decimal("1"),
            bw_gbps=Decimal("1"),
            graph_mteps=Decimal("1"),
            det_pass=True,
            epoch=1,
            agent_id=_AGENT_ID,
        )
    assert exc.value.token == "capproof_gemm_gops_must_be_nonnegative"


def test_capability_vector_rejects_unbounded_metric() -> None:
    with pytest.raises(CapProofValidationError) as exc:
        CapabilityVector(
            gemm_gops=CAPPROOF_MAX_METRIC_VALUE + Decimal("1"),
            infer_tps=Decimal("1"),
            bw_gbps=Decimal("1"),
            graph_mteps=Decimal("1"),
            det_pass=True,
            epoch=1,
            agent_id=_AGENT_ID,
        )
    assert exc.value.token == "capproof_gemm_gops_exceeds_maximum"


def test_capability_vector_rejects_non_bool_det_pass() -> None:
    with pytest.raises(CapProofValidationError) as exc:
        CapabilityVector(
            gemm_gops=Decimal("1"),
            infer_tps=Decimal("1"),
            bw_gbps=Decimal("1"),
            graph_mteps=Decimal("1"),
            det_pass=1,
            epoch=1,
            agent_id=_AGENT_ID,
        )
    assert exc.value.token == "capproof_det_pass_must_be_bool"


def test_capability_vector_rejects_invalid_agent_id() -> None:
    with pytest.raises(CapProofValidationError) as exc:
        CapabilityVector(
            gemm_gops=Decimal("1"),
            infer_tps=Decimal("1"),
            bw_gbps=Decimal("1"),
            graph_mteps=Decimal("1"),
            det_pass=True,
            epoch=1,
            agent_id="agent:alpha",
        )
    assert exc.value.token == "capproof_agent_id_must_be_96_lower_hex"


def test_capability_vector_json_is_deterministic_and_decimal_strings() -> None:
    cv = CapabilityVector(
        gemm_gops=Decimal("2.5"),
        infer_tps=Decimal("3.5"),
        bw_gbps=Decimal("4.5"),
        graph_mteps=Decimal("5.5"),
        det_pass=True,
        epoch=7,
        agent_id=_AGENT_ID,
    )
    assert cv.to_json() == (
        '{"agent_id":"'
        + _AGENT_ID
        + '","bw_gbps":"4.5","det_pass":true,"epoch":7,'
        + '"gemm_gops":"2.5","graph_mteps":"5.5","infer_tps":"3.5"}'
    )
    assert CapabilityVector.from_dict(cv.to_dict()) == cv
    assert CapabilityVector.from_json(cv.to_json()) == cv


def test_capability_vector_from_dict_rejects_scientific_decimal_string() -> None:
    cv = CapabilityVector(
        gemm_gops=Decimal("2.5"),
        infer_tps=Decimal("3.5"),
        bw_gbps=Decimal("4.5"),
        graph_mteps=Decimal("5.5"),
        det_pass=True,
        epoch=7,
        agent_id=_AGENT_ID,
    )
    payload = cv.to_dict()
    payload["gemm_gops"] = "1E+2"

    with pytest.raises(CapProofValidationError) as exc:
        CapabilityVector.from_dict(payload)

    assert exc.value.token == "capproof_gemm_gops_must_be_canonical_decimal_string"


def test_probe_metric_derivation_ignores_ambient_decimal_precision() -> None:
    with localcontext() as ctx:
        ctx.prec = 6
        low_precision = _derive_metric(_SALT, "gemm", Decimal("100000"), Decimal("1000"))
    with localcontext() as ctx:
        ctx.prec = 50
        high_precision = _derive_metric(_SALT, "gemm", Decimal("100000"), Decimal("1000"))

    assert low_precision == high_precision


def test_multiplier_clamps_at_lower_bound() -> None:
    cv = CapabilityVector(
        gemm_gops=Decimal("0"),
        infer_tps=Decimal("0"),
        bw_gbps=Decimal("0"),
        graph_mteps=Decimal("0"),
        det_pass=True,
        epoch=1,
        agent_id=_AGENT_ID,
    )
    assert compute_capproof_multiplier(cv) == Decimal("0.85")


def test_multiplier_clamps_at_upper_bound_for_extreme_cv() -> None:
    cv = CapabilityVector(
        gemm_gops=CAPPROOF_MAX_METRIC_VALUE,
        infer_tps=CAPPROOF_MAX_METRIC_VALUE,
        bw_gbps=CAPPROOF_MAX_METRIC_VALUE,
        graph_mteps=CAPPROOF_MAX_METRIC_VALUE,
        det_pass=True,
        epoch=1,
        agent_id=_AGENT_ID,
    )
    assert Decimal("1.149999999999") < compute_capproof_multiplier(cv) <= Decimal("1.15")


def test_multiplier_det_pass_false_preserves_lower_bound() -> None:
    cv = CapabilityVector(
        gemm_gops=CAPPROOF_MAX_METRIC_VALUE,
        infer_tps=CAPPROOF_MAX_METRIC_VALUE,
        bw_gbps=CAPPROOF_MAX_METRIC_VALUE,
        graph_mteps=CAPPROOF_MAX_METRIC_VALUE,
        det_pass=False,
        epoch=1,
        agent_id=_AGENT_ID,
    )
    assert compute_capproof_multiplier(cv) == Decimal("0.85")


def test_capproof_runtime_has_no_real_number_literals() -> None:
    for path in _CAP_DIR.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            assert not isinstance(node, ast.Constant) or not isinstance(node.value, float)


def test_multiplier_has_no_settlement_or_stacking_imports() -> None:
    tree = ast.parse((_CAP_DIR / "multiplier.py").read_text(encoding="utf-8"))
    forbidden = {"wallet", "settlement", "emission", "werner", "reputation", "reward"}
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert not any(any(term in module for term in forbidden) for module in imported)
