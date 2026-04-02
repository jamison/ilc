#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import prove_rc0_1_economic_state
from tools.testbed.run_economic_negative_path_drills import EconomicNegativePathError, run_drills
from tools.testbed.run_economic_replay_drills import EconomicReplayDrillError, run_replay_drills

DEFAULT_OUTPUT_ROOT = REPO_ROOT / "out/rc0_1_economic_proof_runner"


class EconomicProofRunnerError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_economic_proof(*, manifest_path: Path, output_root: Path) -> dict[str, object]:
    output_root.mkdir(parents=True, exist_ok=True)
    manifest = _load_json(manifest_path)
    scenario_root_value = manifest.get("scenario_root")
    if not isinstance(scenario_root_value, str) or not scenario_root_value:
        raise EconomicProofRunnerError("economic_scenario_root_missing")

    proof_started = time.perf_counter()
    proof_manifest = prove_rc0_1_economic_state.prove_economic_state(
        manifest_path=manifest_path,
        output_root=output_root / "proof",
    )
    proof_duration_ms = round((time.perf_counter() - proof_started) * 1000.0, 6)

    negative_started = time.perf_counter()
    negative_manifest = run_drills(manifest_path=manifest_path)
    negative_duration_ms = round((time.perf_counter() - negative_started) * 1000.0, 6)
    negative_path_manifest_path = output_root / "negative-path" / "manifest.json"
    negative_path_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    negative_path_manifest_path.write_text(json.dumps(negative_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    replay_started = time.perf_counter()
    replay_manifest = run_replay_drills(
        scenario_root=Path(scenario_root_value),
        output_root=output_root / "replay-drill",
    )
    replay_duration_ms = round((time.perf_counter() - replay_started) * 1000.0, 6)
    replay_manifest_path = output_root / "replay-drill" / "manifest.json"
    replay_manifest_path.write_text(json.dumps(replay_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    runner_manifest = {
        "version": "rc0_1_economic_proof_runner_v0.1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "manifest_path": str(manifest_path),
        "scenario_root": scenario_root_value,
        "proof_runner_manifest_path": str(output_root / "manifest.json"),
        "proof_manifest_path": proof_manifest["proof_manifest_path"],
        "comparison": proof_manifest["comparison"],
        "invariant_summary": proof_manifest["invariant_summary"],
        "query_payloads": proof_manifest["query_payloads"],
        "query_timings_ms": proof_manifest.get("query_timings_ms", {}),
        "runtime_store": proof_manifest["runtime_store"],
        "replay_runtime_store": proof_manifest["replay_runtime_store"],
        "negative_path_manifest_path": str(negative_path_manifest_path),
        "negative_path_verdict": "pass",
        "negative_path_tokens": negative_manifest["tokens"],
        "replay_manifest_path": str(replay_manifest_path),
        "replay_verdict": "pass",
        "replay_settlement_status": replay_manifest.get("settlement_status"),
        "proof_duration_ms": proof_duration_ms,
        "negative_path_duration_ms": negative_duration_ms,
        "replay_duration_ms": replay_duration_ms,
    }
    runner_manifest_path = output_root / "manifest.json"
    runner_manifest_path.write_text(json.dumps(runner_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return runner_manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the full RC0.1 economic proof suite over a persisted economic manifest.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output-root")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output_root = Path(args.output_root) if args.output_root else DEFAULT_OUTPUT_ROOT / datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        payload = run_economic_proof(manifest_path=Path(args.manifest), output_root=output_root)
    except (
        EconomicProofRunnerError,
        prove_rc0_1_economic_state.EconomicProofError,
        EconomicNegativePathError,
        EconomicReplayDrillError,
        OSError,
        json.JSONDecodeError,
    ) as exc:
        print(json.dumps({"marker": "rc0_1_economic_proof_runner_failed", "detail": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 1
    print(json.dumps({"marker": "rc0_1_economic_proof_runner_ok", "manifest": payload}, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
