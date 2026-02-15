import json
from pathlib import Path
from importlib import resources

import jsonschema

from ilc_core.protocol.ilc_cluster_a_replay_proof_batch_compare import (
    _escape_path_token,
    compare_cluster_a_replay_proof_batch_reports,
)


FIXTURES_DIR = Path("tests/fixtures/cluster_a_replay_proof_batch_compare_v0_1")
COMPARE_SCHEMA_NAME = "ilc_cluster_a_replay_proof_batch_compare_v0.1.json"


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _load_packaged_schema(name: str) -> dict[str, object]:
    text = resources.files("ilc_core.protocol.schemas").joinpath(name).read_text(encoding="utf-8")
    return json.loads(text)


VALID_REPORT = {
    "report_version": "v0.1",
    "total_packages": 1,
    "ok_count": 1,
    "fail_count": 0,
    "ok": True,
    "results": [],
    "error_token_counts": {},
    "batch_errors": [],
}


def test_escape_path_token():
    assert _escape_path_token("foo") == "foo"
    assert _escape_path_token("foo/bar") == "foo~1bar"
    assert _escape_path_token("foo~bar") == "foo~0bar"
    assert _escape_path_token("~/") == "~0~1"


def test_identical_reports_and_schema_valid():
    schema = _load_packaged_schema(COMPARE_SCHEMA_NAME)
    res = compare_cluster_a_replay_proof_batch_reports(VALID_REPORT, VALID_REPORT)
    assert res["ok"] is True
    assert res["mismatch_count"] == 0
    assert res["mismatches"] == []
    jsonschema.validate(instance=res, schema=schema)


def test_fixture_mismatch_report_matches_expected():
    left = _load_json(FIXTURES_DIR / "report_left.json")
    right = _load_json(FIXTURES_DIR / "report_right.json")
    expected = _load_json(FIXTURES_DIR / "compare_expected.json")
    actual = compare_cluster_a_replay_proof_batch_reports(left, right)
    assert actual == expected


def test_schema_invalid_left():
    invalid = {"foo": "bar"}
    res = compare_cluster_a_replay_proof_batch_reports(invalid, VALID_REPORT)
    assert res["ok"] is False
    assert res["mismatch_count"] == 1
    m = res["mismatches"][0]
    assert m["reason"] == "schema_invalid_left"
    assert m["path"] == "/"
    assert m["left"] is None
    assert m["right"] is None
    assert "detail" in m


def test_schema_invalid_right():
    invalid = {"foo": "bar"}
    res = compare_cluster_a_replay_proof_batch_reports(VALID_REPORT, invalid)
    assert res["ok"] is False
    assert res["mismatch_count"] == 1
    m = res["mismatches"][0]
    assert m["reason"] == "schema_invalid_right"
    assert m["path"] == "/"
    assert m["left"] is None
    assert m["right"] is None
    assert "detail" in m


def test_json_pointer_escaping_in_path():
    left = dict(VALID_REPORT)
    right = dict(VALID_REPORT)
    left["error_token_counts"] = {"a/b~c": 1}
    right["error_token_counts"] = {"a/b~c": 2}

    res = compare_cluster_a_replay_proof_batch_reports(left, right)
    assert res["ok"] is False
    assert res["mismatch_count"] == 1
    assert res["mismatches"][0]["path"] == "/error_token_counts/a~1b~0c"


def test_mismatch_ordering_is_deterministic():
    left = dict(VALID_REPORT)
    right = dict(VALID_REPORT)
    left["ok"] = True
    right["ok"] = False
    left["batch_errors"] = ["a"]
    right["batch_errors"] = ["b"]

    res = compare_cluster_a_replay_proof_batch_reports(left, right)
    paths = [m["path"] for m in res["mismatches"]]
    assert paths == sorted(paths)
