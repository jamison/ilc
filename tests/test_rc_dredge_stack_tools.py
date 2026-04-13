from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cmd(args, cwd: Path | None = None):
    result = subprocess.run(
        [sys.executable, *args],
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    return result


def test_rc_dredge_preserves_relative_source_path_and_exact_text_dedup(tmp_path: Path):
    corpus = tmp_path / "corpus"
    docs = corpus / "docs" / "specs"
    docs.mkdir(parents=True)

    shared_prefix = (
        "Wallet transfer authority must be explicit in public release contracts and escrow "
        "write authority must be deterministic across the settlement path for"
    )
    text = (
        f"{shared_prefix} bounty escrow lanes. Additional suffix one for uniqueness.\n\n"
        f"{shared_prefix} node-transfer settlement lanes. Additional suffix two for uniqueness.\n"
    )
    source = docs / "example.md"
    source.write_text(text, encoding="utf-8")

    output_dir = tmp_path / "out"
    run_cmd(
        [
            "tools/rc_dredge_v2.py",
            str(docs),
            "--output",
            str(output_dir),
            "--topic-profile",
            "post_605",
            "--min-chars",
            "60",
        ]
    )

    rows = [json.loads(line) for line in (output_dir / "rc_gap_dredge_raw_v0.2.jsonl").open()]
    assert len(rows) == 2
    assert all(row["source_path"].endswith("example.md") for row in rows)
    assert all(row["topic"] == "wallet_authority" for row in rows)


def test_rc_gap_triage_supports_g1_mode_off_and_dynamic_input_count(tmp_path: Path):
    raw_path = tmp_path / "raw.jsonl"
    rows = [
        {
            "id": "cap-1",
            "topic": "wallet_authority",
            "strength": "must",
            "claim": "Transfer authority must be explicit.",
            "source": "docs/specs/a.md:1",
            "source_path": "docs/specs/a.md",
            "mainnet_req": "Review",
            "testnet_req": "Review",
        },
        {
            "id": "cap-2",
            "topic": "wallet_authority",
            "strength": "must",
            "claim": "Escrow authority must be explicit.",
            "source": "docs/specs/b.md:1",
            "source_path": "docs/specs/b.md",
            "mainnet_req": "No",
            "testnet_req": "Yes",
        },
    ]
    with raw_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")

    off_output = tmp_path / "triage_off.md"
    run_cmd(["tools/rc_gap_triage_v2.py", "--input", str(raw_path), "--output", str(off_output), "--g1-mode", "off"])
    off_text = off_output.read_text(encoding="utf-8")
    assert "(2 raw entries)" in off_text
    assert "Surviving G1/G2 Cut: 2 entries" in off_text

    strict_output = tmp_path / "triage_strict.md"
    run_cmd(["tools/rc_gap_triage_v2.py", "--input", str(raw_path), "--output", str(strict_output), "--g1-mode", "strict"])
    strict_text = strict_output.read_text(encoding="utf-8")
    assert "Surviving G1/G2 Cut: 0 entries" in strict_text


def test_rc_suite_generator_uses_output_dir_and_marks_review_placeholders(tmp_path: Path):
    source_doc = tmp_path / "docs" / "specs" / "wallet.md"
    source_doc.parent.mkdir(parents=True)
    source_doc.write_text(
        "Wallet transfer authority must be explicit in public release contracts.",
        encoding="utf-8",
    )

    raw_path = tmp_path / "rc_gap_dredge_raw_v0.2.jsonl"
    row = {
        "id": "cap-1",
        "topic": "wallet_authority",
        "strength": "must",
        "claim": "Wallet transfer authority must be explicit in public release contracts.",
        "source": f"{source_doc.as_posix()}:0",
        "source_path": source_doc.as_posix(),
        "source_file": source_doc.name,
        "mainnet_req": "Yes",
        "testnet_req": "No",
    }
    raw_path.write_text(json.dumps(row) + "\n", encoding="utf-8")

    matrix_path = tmp_path / "rc_gap_matrix_v0.2.md"
    matrix_path.write_text("# placeholder\n", encoding="utf-8")

    output_dir = tmp_path / "suite"
    run_cmd(
        [
            "tools/rc_dredge_formal_suite_generator.py",
            "--input",
            str(raw_path),
            "--matrix",
            str(matrix_path),
            "--output-dir",
            str(output_dir),
            "--g1-mode",
            "off",
        ]
    )

    inventory = (output_dir / "ilc_rc_dredge_inventory_v0.1.md").read_text(encoding="utf-8")
    assert source_doc.as_posix() in inventory

    clause_triage = (output_dir / "ilc_rc_clause_triage_v0.1.md").read_text(encoding="utf-8")
    assert "needs_review" in clause_triage
