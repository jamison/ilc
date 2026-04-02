#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "out/rc0_1_release_claim"


class ReleaseClaimError(RuntimeError):
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
        raise ReleaseClaimError(
            f"command_failed:{' '.join(command)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_candidate_manifest() -> Path:
    candidates = sorted((REPO_ROOT / "out/rc0_1_release_candidate").glob("*/manifest.json"))
    if not candidates:
        raise ReleaseClaimError("release_candidate_manifest_missing")
    return candidates[-1]


def _write_release_notes_input(*, delta_manifest: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# ILC RC0.1 Release Notes Input",
        "",
        "## Candidate summary",
        f"- repo_head: `{delta_manifest['repo_head']}`",
        f"- release_candidate_ready: `{delta_manifest['release_candidate_ready']}`",
        f"- closure_pass: `{delta_manifest['closure_pass']}`",
        f"- release_pass: `{delta_manifest['release_pass']}`",
        f"- scenario_pass: `{delta_manifest['scenario_pass']}`",
        f"- scenario_replay_pass: `{delta_manifest['scenario_replay_pass']}`",
        f"- bundle_install_proof_pass: `{delta_manifest['bundle_install_proof_pass']}`",
        f"- economic_proof_pass: `{delta_manifest['economic_proof_pass']}`",
        "",
        "## Shipped surface in this candidate",
        "- three-node substrate closure with deterministic install-shape proof",
        "- curated bootstrap inventory and GitHub-distributed bootstrap payload",
        "- bidirectional CDL-061 exchange across the home node and two VPS nodes",
        "- bounded seven-agent scenario with deterministic panel replay",
        "- persisted economic-cycle projection with graph state, settled balances, and wallet export",
        "- RC bundle archive plus copied-bundle installer/update proof on home and both VPS nodes",
        "",
        "## Economic-cycle visibility",
        f"- economic_state_present: `{delta_manifest.get('economic_state_present')}`",
        f"- economic_reward_total: `{(delta_manifest.get('economic_summary') or {}).get('reward_total')}`",
        f"- economic_wallet_count: `{(delta_manifest.get('economic_summary') or {}).get('wallet_count')}`",
        f"- economic_node_count: `{(delta_manifest.get('economic_summary') or {}).get('node_count')}`",
        f"- economic_runtime_store_kind: `{(delta_manifest.get('economic_claim_summary') or {}).get('runtime_store_kind')}`",
        f"- economic_settlement_status: `{(delta_manifest.get('economic_claim_summary') or {}).get('settlement_status')}`",
        f"- economic_rewarded_wallet_count: `{(delta_manifest.get('economic_claim_summary') or {}).get('rewarded_wallet_count')}`",
        f"- economic_epoch_record_count: `{(delta_manifest.get('economic_claim_summary') or {}).get('epoch_record_count')}`",
        "",
        "## Publication steps still pending",
    ]
    lines.extend(f"- {item}" for item in delta_manifest["publication_pending_items"])
    lines.extend(
        [
            "",
            "## Explicitly deferred beyond RC0.1",
        ]
    )
    lines.extend(
        f"- {item['item']}: {item['reason']}"
        for item in delta_manifest["post_rc_deferred_scope"]
    )
    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def run_release_claim(*, candidate_manifest_path: Path, output_root: Path) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    delta_manifest_path = output_root / "readiness_delta.json"
    delta_result = _run(
        [
            "python3",
            "tools/render_rc0_1_readiness_delta.py",
            "--candidate-manifest",
            str(candidate_manifest_path),
            "--output-path",
            str(delta_manifest_path),
        ]
    )
    delta_manifest = _load_json(delta_manifest_path)
    notes_input_path = output_root / "release_notes_input.md"
    _write_release_notes_input(delta_manifest=delta_manifest, output_path=notes_input_path)

    claim_manifest = {
        "version": "rc0_1_release_claim_v0.1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "candidate_manifest_path": str(candidate_manifest_path),
        "closure_manifest_path": delta_manifest["closure_manifest_path"],
        "release_manifest_path": delta_manifest["release_manifest_path"],
        "evidence_manifest_path": delta_manifest["evidence_manifest_path"],
        "economic_manifest_path": delta_manifest.get("economic_manifest_path"),
        "bundle_manifest_path": delta_manifest["bundle_manifest_path"],
        "bundle_install_proof_manifest_path": delta_manifest["bundle_install_proof_manifest_path"],
        "economic_proof_manifest_path": delta_manifest.get("economic_proof_manifest_path"),
        "economic_claim_summary": delta_manifest.get("economic_claim_summary"),
        "release_notes_input_path": str(notes_input_path),
        "delta_manifest_path": str(delta_manifest_path),
        "delta_stdout": delta_result.stdout.strip(),
    }
    claim_manifest_path = output_root / "manifest.json"
    claim_manifest_path.write_text(json.dumps(claim_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    verdict_result = _run(
        [
            "python3",
            "tools/check_rc0_1_release_claim.py",
            "--claim-manifest",
            str(claim_manifest_path),
            "--delta-manifest",
            str(delta_manifest_path),
        ]
    )
    claim_manifest["claim_verdict_stdout"] = verdict_result.stdout.strip()
    claim_manifest_path.write_text(json.dumps(claim_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return claim_manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render the final RC0.1 release-claim package over a successful release-candidate run.")
    parser.add_argument("--candidate-manifest")
    parser.add_argument("--output-root")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    candidate_manifest_path = Path(args.candidate_manifest) if args.candidate_manifest else _latest_candidate_manifest()
    output_root = Path(args.output_root) if args.output_root else DEFAULT_OUTPUT_ROOT / datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        payload = run_release_claim(candidate_manifest_path=candidate_manifest_path, output_root=output_root)
    except ReleaseClaimError as exc:
        print(json.dumps({"marker": "rc0_1_release_claim_failed", "detail": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 1
    print(json.dumps({"marker": "rc0_1_release_claim_ok", "manifest": payload}, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
