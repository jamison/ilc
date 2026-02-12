import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from ilc_core.cli.canon_cluster_a_replay_proof import main


def run_cli_command(args_list):
    with patch.object(sys, "argv", ["prog"] + args_list):
        output = StringIO()
        with patch.object(sys, "stdout", output):
            try:
                main()
                return 0, output.getvalue()
            except SystemExit as e:
                return e.code, output.getvalue()


def test_compare_reports_ok(tmp_path: Path):
    report = tmp_path / "valid.json"
    data = {
        "report_version": "v0.1",
        "total_packages": 0,
        "ok_count": 0,
        "fail_count": 0,
        "ok": True,
        "results": [],
        "error_token_counts": {},
        "batch_errors": [],
    }
    report.write_text(json.dumps(data), encoding="utf-8")

    code, out = run_cli_command(
        ["compare-reports", "--left", str(report), "--right", str(report)]
    )
    assert code == 0
    res = json.loads(out)
    assert res["ok"] is True
    assert res["mismatch_count"] == 0


def test_compare_reports_mismatch(tmp_path: Path):
    left_path = tmp_path / "left.json"
    right_path = tmp_path / "right.json"

    base = {
        "report_version": "v0.1",
        "total_packages": 0,
        "ok_count": 0,
        "fail_count": 0,
        "ok": True,
        "results": [],
        "error_token_counts": {},
        "batch_errors": [],
    }
    left_data = dict(base)
    right_data = dict(base)
    right_data["ok"] = False

    left_path.write_text(json.dumps(left_data), encoding="utf-8")
    right_path.write_text(json.dumps(right_data), encoding="utf-8")

    code, out = run_cli_command(
        ["compare-reports", "--left", str(left_path), "--right", str(right_path)]
    )
    assert code == 1
    res = json.loads(out)
    assert res["ok"] is False
    assert res["mismatch_count"] == 1
    assert res["mismatches"][0]["path"] == "/ok"


def test_compare_reports_schema_invalid_exit_2(tmp_path: Path):
    left_path = tmp_path / "left.json"
    right_path = tmp_path / "right.json"
    left_path.write_text(json.dumps({"foo": "bar"}), encoding="utf-8")
    right_path.write_text(
        json.dumps(
            {
                "report_version": "v0.1",
                "total_packages": 0,
                "ok_count": 0,
                "fail_count": 0,
                "ok": True,
                "results": [],
                "error_token_counts": {},
                "batch_errors": [],
            }
        ),
        encoding="utf-8",
    )

    code, out = run_cli_command(
        ["compare-reports", "--left", str(left_path), "--right", str(right_path)]
    )
    assert code == 2
    res = json.loads(out)
    assert res["ok"] is False
    assert res["mismatch_count"] == 1
    assert res["mismatches"][0]["reason"] == "schema_invalid_left"


def test_compare_reports_invalid_json(tmp_path: Path):
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")

    code, out = run_cli_command(["compare-reports", "--left", str(bad), "--right", str(bad)])
    assert code == 2
    err = json.loads(out)
    assert err["error"] == "invalid_json"


def test_compare_reports_not_found(tmp_path: Path):
    missing = tmp_path / "missing.json"
    code, out = run_cli_command(
        ["compare-reports", "--left", str(missing), "--right", str(missing)]
    )
    assert code == 2
    err = json.loads(out)
    assert err["error"] == "file_not_found"
