#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]

import sys

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.rc import materialize_economic_cycle
from ilc_core.rc.economic_cycle_runtime import EconomicCycleRuntimeError

DEFAULT_OUTPUT_ROOT = REPO_ROOT / "out/rc0_1_economic_cycle"


class EconomicCycleToolError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_release_candidate_scenario_root() -> Path:
    candidates = sorted((REPO_ROOT / "out/rc0_1_release_candidate").glob("*/manifest.json"))
    if not candidates:
        raise EconomicCycleToolError("release_candidate_manifest_missing")
    candidate_manifest = _load_json(candidates[-1])
    closure_manifest_path = Path(str(candidate_manifest.get("closure_manifest_path", "")))
    if not closure_manifest_path.is_file():
        raise EconomicCycleToolError("closure_manifest_missing")
    closure_manifest = _load_json(closure_manifest_path)
    scenario_root = closure_manifest_path.parent / "scenario"
    if not scenario_root.is_dir():
        scenario_root = Path(str(closure_manifest.get("scenario_root", "")))
    if not scenario_root.is_dir():
        raise EconomicCycleToolError(f"scenario_root_missing:{scenario_root}")
    return scenario_root


def run_economic_cycle(*, scenario_root: Path, output_root: Path) -> dict[str, Any]:
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    return materialize_economic_cycle(scenario_root=scenario_root, output_root=output_root)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Materialize graph state, settled balances, and wallet state from a bounded RC0.1 seven-agent scenario.")
    parser.add_argument("--scenario-root")
    parser.add_argument("--output-root")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    scenario_root = Path(args.scenario_root) if args.scenario_root else _latest_release_candidate_scenario_root()
    if args.output_root:
        output_root = Path(args.output_root)
    else:
        output_root = DEFAULT_OUTPUT_ROOT / datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        manifest = run_economic_cycle(scenario_root=scenario_root, output_root=output_root)
    except (EconomicCycleRuntimeError, EconomicCycleToolError, OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"marker": "rc0_1_economic_cycle_failed", "detail": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 1
    print(
        json.dumps(
            {
                "marker": "rc0_1_economic_cycle_ok",
                "manifest_path": str(output_root / "manifest.json"),
                "manifest": manifest,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
