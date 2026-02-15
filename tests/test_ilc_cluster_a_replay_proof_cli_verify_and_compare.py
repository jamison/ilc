import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from importlib import resources

import jsonschema

from ilc_core.cli.canon_cluster_a_replay_proof import main


OPS_FIXTURES_DIR = Path("tests/fixtures/cluster_a_replay_proof_batch_ops_v0_1")
OPS_CONTRACT_SCHEMA_NAME = "ilc_cluster_a_replay_proof_batch_ops_contract_v0.1.json"


def run_cli_command(args_list):
    with patch.object(sys, "argv", ["prog"] + args_list):
        output = StringIO()
        with patch.object(sys, "stdout", output):
            try:
                main()
                return 0, output.getvalue()
            except SystemExit as e:
                return e.code, output.getvalue()


def _load_ops_schema():
    text = resources.files("ilc_core.protocol.schemas").joinpath(OPS_CONTRACT_SCHEMA_NAME).read_text(encoding="utf-8")
    return json.loads(text)


def _parse_contract(out: str):
    assert out.strip(), "Expected stdout contract JSON but output was empty."
    return json.loads(out)


def test_verify_and_compare_success_outputs_ops_contract_and_artifacts(tmp_path):
    manifest = OPS_FIXTURES_DIR / "manifest.txt"
    expected = OPS_FIXTURES_DIR / "report_match.json"
    out_report = tmp_path / "batch_out.json"
    out_compare = tmp_path / "compare_out.json"

    code, out = run_cli_command([
        "verify-and-compare",
        "--manifest", str(manifest),
        "--expected", str(expected),
        "--out-report", str(out_report),
        "--out-compare", str(out_compare),
    ])

    contract = _parse_contract(out)
    jsonschema.validate(instance=contract, schema=_load_ops_schema())
    assert code == contract["exit_code"] == 0
    assert contract["ok"] is True
    assert contract["batch_ok"] is True
    assert contract["compare_ok"] is True
    assert contract["error_token"] is None
    assert contract["batch_report_path"] == str(out_report.resolve())
    assert contract["compare_report_path"] == str(out_compare.resolve())
    assert out_report.exists()
    assert out_compare.exists()


def test_verify_and_compare_mismatch_returns_exit_1_with_contract():
    manifest = OPS_FIXTURES_DIR / "manifest.txt"
    expected = OPS_FIXTURES_DIR / "report_mismatch.json"

    code, out = run_cli_command([
        "verify-and-compare",
        "--manifest", str(manifest),
        "--expected", str(expected),
    ])

    contract = _parse_contract(out)
    jsonschema.validate(instance=contract, schema=_load_ops_schema())
    assert code == contract["exit_code"] == 1
    assert contract["ok"] is False
    assert contract["batch_ok"] is True
    assert contract["compare_ok"] is False
    assert contract["error_token"] is None


def test_verify_and_compare_schema_invalid_expected_returns_exit_2_token():
    manifest = OPS_FIXTURES_DIR / "manifest.txt"
    expected = OPS_FIXTURES_DIR / "report_schema_invalid.json"

    code, out = run_cli_command([
        "verify-and-compare",
        "--manifest", str(manifest),
        "--expected", str(expected),
    ])

    contract = _parse_contract(out)
    jsonschema.validate(instance=contract, schema=_load_ops_schema())
    assert code == contract["exit_code"] == 2
    assert contract["ok"] is False
    assert contract["compare_ok"] is False
    assert contract["error_token"] == "expected_schema_invalid"


def test_verify_and_compare_manifest_not_found_stable_token(tmp_path):
    missing_manifest = tmp_path / "missing_manifest.txt"
    expected = OPS_FIXTURES_DIR / "report_match.json"

    code, out = run_cli_command([
        "verify-and-compare",
        "--manifest", str(missing_manifest),
        "--expected", str(expected),
    ])

    contract = _parse_contract(out)
    jsonschema.validate(instance=contract, schema=_load_ops_schema())
    assert code == contract["exit_code"] == 2
    assert contract["error_token"] == "manifest_not_found"
    assert "detail" not in contract


def test_verify_and_compare_quiet_without_output_sink_is_error():
    manifest = OPS_FIXTURES_DIR / "manifest.txt"
    expected = OPS_FIXTURES_DIR / "report_match.json"

    code, out = run_cli_command([
        "verify-and-compare",
        "--manifest", str(manifest),
        "--expected", str(expected),
        "--quiet",
    ])

    contract = _parse_contract(out)
    jsonschema.validate(instance=contract, schema=_load_ops_schema())
    assert code == contract["exit_code"] == 2
    assert contract["error_token"] == "usage_error:no_output_sink"


def test_verify_and_compare_manifest_source_id_normalization(tmp_path):
    pkg_src = OPS_FIXTURES_DIR / "pkg_valid.json"
    expected = OPS_FIXTURES_DIR / "report_match.json"
    pkg_dst = tmp_path / "pkg_valid.json"
    manifest = tmp_path / "manifest.txt"
    pkg_dst.write_text(pkg_src.read_text(encoding="utf-8"), encoding="utf-8")
    manifest.write_text("./pkg_valid.json\n", encoding="utf-8")

    code, out = run_cli_command([
        "verify-and-compare",
        "--manifest", str(manifest),
        "--expected", str(expected),
    ])

    contract = _parse_contract(out)
    jsonschema.validate(instance=contract, schema=_load_ops_schema())
    assert code == contract["exit_code"] == 0
    assert contract["ok"] is True


def test_verify_and_compare_manifest_escape_entry_is_parse_error(tmp_path):
    expected = OPS_FIXTURES_DIR / "report_match.json"
    manifest = tmp_path / "manifest_escape.txt"
    manifest.write_text("../pkg_valid.json\n", encoding="utf-8")

    code, out = run_cli_command([
        "verify-and-compare",
        "--manifest", str(manifest),
        "--expected", str(expected),
    ])

    contract = _parse_contract(out)
    jsonschema.validate(instance=contract, schema=_load_ops_schema())
    assert code == contract["exit_code"] == 2
    assert contract["error_token"] == "manifest_parse_error"


def test_verify_and_compare_manifest_absolute_entry_is_parse_error(tmp_path):
    expected = OPS_FIXTURES_DIR / "report_match.json"
    manifest = tmp_path / "manifest_absolute.txt"
    manifest.write_text("/tmp/pkg_valid.json\n", encoding="utf-8")

    code, out = run_cli_command([
        "verify-and-compare",
        "--manifest", str(manifest),
        "--expected", str(expected),
    ])

    contract = _parse_contract(out)
    jsonschema.validate(instance=contract, schema=_load_ops_schema())
    assert code == contract["exit_code"] == 2
    assert contract["error_token"] == "manifest_parse_error"


def test_verify_and_compare_manifest_effective_duplicate_is_parse_error(tmp_path):
    expected = OPS_FIXTURES_DIR / "report_match.json"
    manifest = tmp_path / "manifest_dup_norm.txt"
    manifest.write_text("pkg_valid.json\n./pkg_valid.json\n", encoding="utf-8")

    code, out = run_cli_command([
        "verify-and-compare",
        "--manifest", str(manifest),
        "--expected", str(expected),
    ])

    contract = _parse_contract(out)
    jsonschema.validate(instance=contract, schema=_load_ops_schema())
    assert code == contract["exit_code"] == 2
    assert contract["error_token"] == "manifest_parse_error"


def test_verify_and_compare_deterministic_contract_output():
    manifest = OPS_FIXTURES_DIR / "manifest.txt"
    expected = OPS_FIXTURES_DIR / "report_match.json"

    code1, out1 = run_cli_command([
        "verify-and-compare",
        "--manifest", str(manifest),
        "--expected", str(expected),
    ])
    code2, out2 = run_cli_command([
        "verify-and-compare",
        "--manifest", str(manifest),
        "--expected", str(expected),
    ])

    assert code1 == code2 == 0
    assert out1 == out2
