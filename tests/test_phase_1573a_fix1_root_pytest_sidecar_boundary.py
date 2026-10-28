from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"


def _pytest_options() -> dict[str, object]:
    with PYPROJECT.open("rb") as handle:
        pyproject = tomllib.load(handle)
    return pyproject["tool"]["pytest"]["ini_options"]


def test_root_pytest_collects_root_tests_only_by_default() -> None:
    options = _pytest_options()

    assert options["pythonpath"] == ["."]
    assert options["testpaths"] == ["tests"]


def test_nested_sidecar_repos_are_excluded_from_root_collection() -> None:
    options = _pytest_options()
    excluded = set(options["norecursedirs"])

    assert "ilc-ccss-sidecar" in excluded
    assert "ilc-timecapsule-sidecar" in excluded


def test_sidecar_test_name_collisions_remain_outside_root_pytest_boundary() -> None:
    """The root boundary must exclude a colliding sidecar path without requiring that repo."""

    root_test = ROOT / "tests" / "test_ccss_private_comm_sidecar_audit.py"
    sidecar_relative = Path("ilc-ccss-sidecar/tests/test_ccss_private_comm_sidecar_audit.py")
    excluded = set(_pytest_options()["norecursedirs"])

    assert root_test.exists()
    assert sidecar_relative.name == root_test.name
    assert sidecar_relative.parts[0] == "ilc-ccss-sidecar"
    assert "ilc-ccss-sidecar" in excluded
