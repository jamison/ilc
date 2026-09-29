#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1609 CapProof Gate-A invariant verifier."""

from __future__ import annotations

import argparse
import ast
import json
import os
import random
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "out" / "phase_1609_capproof_gate_a"

OUTPUT_TOKEN = "capproof_gate_a_pass_phase_1609"
RUNTIME_VERSION = "capproof_gate_a_verify_phase_1609.v0.1"

PHASE_TESTS = {
    "phase_1606": "tests/test_phase_1606_capproof_v1_impl.py",
    "phase_1607": "tests/test_phase_1607_capproof_epoch_wiring.py",
    "phase_1608": "tests/test_phase_1608_capproof_posk.py",
}

FORBIDDEN_CAP_IMPORT_TERMS = (
    "wallet",
    "settlement",
    "emission",
    "werner",
    "validator",
    "reward",
)


@dataclass(frozen=True)
class InvariantResult:
    result: str
    evidence: dict[str, Any]


class GateAFailure(RuntimeError):
    pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory for gate_a_evidence.json",
    )
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    evidence = build_gate_a_evidence()
    output_path = output_dir / "gate_a_evidence.json"
    _atomic_write_json(output_path, evidence)

    for name, result in evidence["invariants"].items():
        print(f"{name}: {result['result'].upper()}")
    print(f"gate_verdict: {evidence['gate_verdict']}")
    print(f"evidence_path: {output_path}")
    if evidence["gate_verdict"] != "PASS":
        return 1
    return 0


def build_gate_a_evidence() -> dict[str, Any]:
    test_counts, test_outputs = _run_phase_tests()
    invariants = {
        "1_no_ilc_mint": _invariant_no_ilc_mint(),
        "2_ecu_band_bounded": _invariant_band_bounded(),
        "3_5probe_suite_complete": _invariant_probe_suite(test_counts["phase_1606"]),
        "4_posk_present": _invariant_posk_present(test_counts["phase_1608"]),
        "5_no_stacking_rule": _invariant_no_stacking(),
        "6_conservation_equation": _invariant_conservation(test_counts, test_outputs),
    }
    normalized = {name: _result_to_json(result) for name, result in invariants.items()}
    verdict = "PASS" if all(item["result"] == "pass" for item in normalized.values()) else "FAIL"
    return {
        "gate": "capproof_gate_a",
        "phase": 1609,
        "runtime_version": RUNTIME_VERSION,
        "invariants": normalized,
        "gate_verdict": verdict,
        "output_token": OUTPUT_TOKEN if verdict == "PASS" else None,
    }


def _invariant_no_ilc_mint() -> InvariantResult:
    from ilc_core.capproof.probe_runner import CAPPROOF_V1_NO_ILC_MINT
    from ilc_core.epoch import capproof_epoch_init_wiring as wiring

    probe_runner_path = REPO_ROOT / "ilc_core" / "capproof" / "probe_runner.py"
    wiring_path = REPO_ROOT / "ilc_core" / "epoch" / "capproof_epoch_init_wiring.py"
    no_mint_source = probe_runner_path.read_text(encoding="utf-8")
    wiring_source = wiring_path.read_text(encoding="utf-8")
    capproof_paths = [
        REPO_ROOT / "ilc_core" / "capproof" / "__init__.py",
        REPO_ROOT / "ilc_core" / "capproof" / "capability_vector.py",
        REPO_ROOT / "ilc_core" / "capproof" / "graph_probe_posk.py",
        REPO_ROOT / "ilc_core" / "capproof" / "multiplier.py",
        REPO_ROOT / "ilc_core" / "capproof" / "probe_runner.py",
        wiring_path,
    ]
    forbidden_imports = _forbidden_imports(capproof_paths)
    ok = (
        CAPPROOF_V1_NO_ILC_MINT is True
        and wiring.CAPPROOF_V1_NO_ILC_MINT_WIRING_CONFIRMED is True
        and "CAPPROOF_V1_NO_ILC_MINT = True" in no_mint_source
        and "CAPPROOF_V1_NO_ILC_MINT" in wiring_source
        and not forbidden_imports
    )
    return InvariantResult(
        "pass" if ok else "fail",
        {
            "probe_runner_constant": CAPPROOF_V1_NO_ILC_MINT is True,
            "wiring_reassertion": wiring.CAPPROOF_V1_NO_ILC_MINT_WIRING_CONFIRMED is True,
            "forbidden_imports": forbidden_imports,
            "source_files_checked": [str(path.relative_to(REPO_ROOT)) for path in capproof_paths],
        },
    )


def _invariant_band_bounded() -> InvariantResult:
    from ilc_core.capproof.capability_vector import CapabilityVector
    from ilc_core.capproof.multiplier import (
        CAPPROOF_MULTIPLIER_MAX,
        CAPPROOF_MULTIPLIER_MIN,
        compute_capproof_multiplier,
    )

    rng = random.Random(1609)
    agent_id = "a" * 96
    failures: list[str] = []
    for index in range(10_000):
        cv = CapabilityVector(
            gemm_gops=_sample_decimal(rng, index, "gemm"),
            infer_tps=_sample_decimal(rng, index, "infer"),
            bw_gbps=_sample_decimal(rng, index, "bw"),
            graph_mteps=_sample_decimal(rng, index, "graph"),
            det_pass=(index % 17 != 0),
            epoch=index,
            agent_id=agent_id,
        )
        value = compute_capproof_multiplier(cv)
        if not (CAPPROOF_MULTIPLIER_MIN <= value <= CAPPROOF_MULTIPLIER_MAX):
            failures.append(f"{index}:{value}")
            break
    lower = compute_capproof_multiplier(
        CapabilityVector(
            gemm_gops=Decimal("1E+999"),
            infer_tps=Decimal("1E+999"),
            bw_gbps=Decimal("1E+999"),
            graph_mteps=Decimal("1E+999"),
            det_pass=False,
            epoch=1,
            agent_id=agent_id,
        )
    )
    ok = not failures and lower == Decimal("0.85")
    return InvariantResult(
        "pass" if ok else "fail",
        {
            "band_floor": str(CAPPROOF_MULTIPLIER_MIN),
            "band_ceil": str(CAPPROOF_MULTIPLIER_MAX),
            "det_pass_false_multiplier": str(lower),
            "deterministic_fuzz_samples": 10_000,
            "failures": failures,
        },
    )


def _invariant_probe_suite(phase_1606_test_count: int) -> InvariantResult:
    from decimal import Decimal

    from ilc_core.capproof.probe_runner import (
        BandwidthProbe,
        BandwidthProbeResult,
        DeterminismProbe,
        DeterminismProbeResult,
        GEMMProbe,
        GEMMProbeResult,
        GraphProbe,
        GraphProbeResult,
        InferProbe,
        InferProbeResult,
    )

    salt = "ab" * 32
    probes = {
        "GEMMProbeResult": isinstance(GEMMProbe().run(salt), GEMMProbeResult),
        "InferProbeResult": isinstance(InferProbe().run(salt), InferProbeResult),
        "GraphProbeResult": isinstance(GraphProbe().run(salt), GraphProbeResult),
        "BandwidthProbeResult": isinstance(BandwidthProbe().run(salt), BandwidthProbeResult),
        "DeterminismProbeResult": isinstance(DeterminismProbe().run(salt), DeterminismProbeResult),
    }
    graph_metric_decimal = isinstance(GraphProbe().run(salt).graph_mteps, Decimal)
    ok = all(probes.values()) and graph_metric_decimal
    return InvariantResult(
        "pass" if ok else "fail",
        {
            "probe_count": len(probes),
            "probes": probes,
            "graph_metric_decimal": graph_metric_decimal,
            "phase_1606_test_count": phase_1606_test_count,
        },
    )


def _invariant_posk_present(phase_1608_test_count: int) -> InvariantResult:
    from dataclasses import replace

    from ilc_core.capproof.graph_probe_posk import (
        POSK_CONSENSUS_BINDING,
        POSK_SPECTRAL_NOT_ACTIVATED,
        PoSKError,
        PoSKInput,
        build_posk_proof,
        verify_posk_proof,
    )

    module_path = REPO_ROOT / "ilc_core" / "capproof" / "graph_probe_posk.py"
    inp = PoSKInput(
        graph_root_hash="a" * 64,
        epoch_salt="b" * 64,
        epoch=7,
        visited_node_ids=(
            "bafybeiaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "bafybeibbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        ),
        traversal_edges=(
            (
                "bafybeiaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "bafybeibbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            ),
        ),
    )
    proof = build_posk_proof(inp)
    tamper_rejected = False
    try:
        verify_posk_proof(replace(proof, proof_commitment="0" * 64))
    except PoSKError as exc:
        tamper_rejected = exc.token == "posk_commitment_mismatch"
    ok = (
        module_path.exists()
        and POSK_SPECTRAL_NOT_ACTIVATED is True
        and POSK_CONSENSUS_BINDING is False
        and verify_posk_proof(proof) is True
        and tamper_rejected
    )
    return InvariantResult(
        "pass" if ok else "fail",
        {
            "posk_module": str(module_path.relative_to(REPO_ROOT)),
            "spectral_not_activated": POSK_SPECTRAL_NOT_ACTIVATED is True,
            "consensus_binding": POSK_CONSENSUS_BINDING,
            "tamper_rejected": tamper_rejected,
            "phase_1608_test_count": phase_1608_test_count,
        },
    )


def _invariant_no_stacking() -> InvariantResult:
    from ilc_core.epoch import capproof_epoch_init_wiring as wiring

    source = (REPO_ROOT / "ilc_core" / "epoch" / "capproof_epoch_init_wiring.py").read_text(
        encoding="utf-8"
    )
    step4_source = _function_source(source, "step4_compute_band_multiplier")
    forbidden_terms = [
        term
        for term in ("werner", "passive", "provenance", "reputation", "reward", "settlement")
        if term in step4_source.lower()
    ]
    sample = wiring.process_capproof_epoch_init(
        _sample_cv(det_pass=True),
        7,
        Decimal("100"),
    )
    ok = (
        "does NOT compound" in step4_source
        and not forbidden_terms
        and sample.protocol_executed is False
        and sample.cap_adjusted_base_ecu_amount == Decimal("100")
    )
    return InvariantResult(
        "pass" if ok else "fail",
        {
            "no_stacking_docstring_present": "does NOT compound" in step4_source,
            "forbidden_terms_in_step4": forbidden_terms,
            "guarded_default_protocol_executed": sample.protocol_executed,
            "guarded_default_adjusted_amount": str(sample.cap_adjusted_base_ecu_amount),
        },
    )


def _invariant_conservation(
    test_counts: dict[str, int],
    test_outputs: dict[str, str],
) -> InvariantResult:
    from ilc_core.epoch import capproof_epoch_init_wiring as wiring

    cv = _sample_cv(det_pass=True)
    band = wiring.step4_compute_band_multiplier(cv)
    base = Decimal("123.456")
    adjusted = base * band
    conservation = wiring.step5_conservation_check(base, adjusted, band)
    all_tests_passed = all("failed" not in output.lower() and "error" not in output.lower() for output in test_outputs.values())
    ok = conservation is True and all_tests_passed
    return InvariantResult(
        "pass" if ok else "fail",
        {
            "band_multiplier": str(band),
            "base_ecu_amount": str(base),
            "cap_adjusted_base_ecu_amount": str(adjusted),
            "conservation_check": conservation,
            "test_counts": test_counts,
            "failures": 0 if all_tests_passed else "see pytest_output",
        },
    )


def _run_phase_tests() -> tuple[dict[str, int], dict[str, str]]:
    counts: dict[str, int] = {}
    outputs: dict[str, str] = {}
    for phase, rel_path in PHASE_TESTS.items():
        result = subprocess.run(
            [sys.executable, "-m", "pytest", rel_path, "-q"],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        outputs[phase] = result.stdout
        if result.returncode != 0:
            raise GateAFailure(f"{phase}_tests_failed\n{result.stdout}")
        counts[phase] = _parse_passed_count(result.stdout)
    return counts, outputs


def _sample_cv(*, det_pass: bool) -> Any:
    from ilc_core.capproof.capability_vector import CapabilityVector

    return CapabilityVector(
        gemm_gops=Decimal("100000"),
        infer_tps=Decimal("10000"),
        bw_gbps=Decimal("1000"),
        graph_mteps=Decimal("10000"),
        det_pass=det_pass,
        epoch=7,
        agent_id="a" * 96,
    )


def _sample_decimal(rng: random.Random, index: int, domain: str) -> Decimal:
    if index in (0, 1, 2, 3):
        return (Decimal("0"), Decimal("1E-9"), Decimal("1E+6"), Decimal("1E+999"))[index]
    raw = rng.randrange(0, 10**12)
    return Decimal(raw) / Decimal("1000")


def _forbidden_imports(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            module = None
            if isinstance(node, ast.ImportFrom):
                module = node.module
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name
                    if module and any(term in module.lower() for term in FORBIDDEN_CAP_IMPORT_TERMS):
                        findings.append(f"{path.relative_to(REPO_ROOT)}:{module}")
                continue
            if module and any(term in module.lower() for term in FORBIDDEN_CAP_IMPORT_TERMS):
                findings.append(f"{path.relative_to(REPO_ROOT)}:{module}")
    return findings


def _function_source(source: str, function_name: str) -> str:
    tree = ast.parse(source)
    lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return "\n".join(lines[node.lineno - 1 : node.end_lineno])
    raise GateAFailure(f"function_missing:{function_name}")


def _parse_passed_count(output: str) -> int:
    match = re.search(r"(\d+) passed", output)
    if match is None:
        raise GateAFailure(f"pytest_pass_count_missing\n{output}")
    return int(match.group(1))


def _result_to_json(result: InvariantResult) -> dict[str, Any]:
    return {"result": result.result, **result.evidence}


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True, indent=2)
            handle.write("\n")
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


if __name__ == "__main__":
    raise SystemExit(main())
