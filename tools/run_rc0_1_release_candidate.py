#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "out/rc0_1_release_candidate"


class ReleaseCandidateError(RuntimeError):
    pass


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ReleaseCandidateError(
            f"command_failed:{' '.join(command)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def run_release_candidate(
    *,
    output_root: Path,
    include_home_install_proof: bool,
    emit_release_claim: bool,
    closure_root: Path | None = None,
) -> dict[str, object]:
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    if closure_root is None:
        closure_root = output_root / "substrate"
        closure_command = [
            "python3",
            "tools/testbed/run_rc0_1_substrate_closure.py",
            "--output-root",
            str(closure_root),
        ]
        if include_home_install_proof:
            closure_command.append("--include-home-install-proof")
        closure_result = _run(closure_command)
        closure_stdout = closure_result.stdout.strip()
    else:
        closure_root = closure_root.resolve()
        closure_stdout = "reused_existing_closure_root"
    closure_manifest = json.loads((closure_root / "closure_manifest.json").read_text(encoding="utf-8"))
    economic_manifest_path = str(closure_manifest.get("economic_manifest_path", closure_root / "scenario" / "economic-state" / "manifest.json"))
    release_root = output_root / "release"
    release_result = _run(
        [
            "python3",
            "tools/run_rc0_1_release_gate.py",
            "--evidence-root",
            str(closure_root / "evidence"),
            "--output-root",
            str(release_root),
        ]
    )
    payload = {
        "version": "rc0_1_release_candidate_v0.1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "closure_manifest_path": str(closure_root / "closure_manifest.json"),
        "economic_manifest_path": economic_manifest_path,
        "release_manifest_path": str(release_root / "manifest.json"),
        "closure_stdout": closure_stdout,
        "economic_stdout": "economic_state_emitted_in_substrate_closure",
        "release_stdout": release_result.stdout.strip(),
    }
    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if emit_release_claim:
        claim_root = output_root / "claim"
        claim_result = _run(
            [
                "python3",
                "tools/run_rc0_1_release_claim.py",
                "--candidate-manifest",
                str(manifest_path),
                "--output-root",
                str(claim_root),
            ]
        )
        payload["release_claim_manifest_path"] = str(claim_root / "manifest.json")
        payload["release_claim_stdout"] = claim_result.stdout.strip()
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the full RC0.1 release-candidate flow from substrate closure through release gate.")
    parser.add_argument("--output-root")
    parser.add_argument("--include-home-install-proof", action="store_true")
    parser.add_argument("--emit-release-claim", action="store_true")
    parser.add_argument("--closure-root")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output_root = Path(args.output_root) if args.output_root else DEFAULT_OUTPUT_ROOT / datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        payload = run_release_candidate(
            output_root=output_root,
            include_home_install_proof=args.include_home_install_proof,
            emit_release_claim=args.emit_release_claim,
            closure_root=Path(args.closure_root) if args.closure_root else None,
        )
    except ReleaseCandidateError as exc:
        print(json.dumps({"marker": "rc0_1_release_candidate_failed", "detail": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 1
    print(json.dumps({"marker": "rc0_1_release_candidate_ok", "manifest": payload}, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
