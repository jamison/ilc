"""Regression tests for Phase 1436a Gap 14 package profile definition."""

from __future__ import annotations

from pathlib import Path
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib

from ilc_core.distribution.package_profiles import (
    DEFINED_PROFILES,
    GAP_14_PHASE_1_TOKEN,
    PACKAGE_PROFILES_VERSION,
    PHASE_1436_NOT_ACTIVATED,
    PROFILE_DEV,
    PROFILE_OPENCLAW_HOSTED,
    PROFILE_OPERATOR_NODE,
    PROFILE_PROTOCOL_CORE,
    PUBLIC_RC_NOT_ACTIVATED,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = REPO_ROOT / "pyproject.toml"
SPEC_DOC = REPO_ROOT / "docs/specs/ilc_modular_package_profile_definition_1436a_v0.1.md"


def _pyproject_extras() -> dict[str, list[str]]:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"][
        "optional-dependencies"
    ]


def _normalized_deps(profile: str) -> set[str]:
    deps = _pyproject_extras()[profile]
    return {dep.split(">=")[0].split("==")[0].lower() for dep in deps}


def test_package_profiles_version_token() -> None:
    assert PACKAGE_PROFILES_VERSION in {
        "package_profiles_1436a.v0.1",
        "package_profiles_1436b.v0.1",
    }


def test_gap_14_phase_1_token_present() -> None:
    assert (
        GAP_14_PHASE_1_TOKEN
        == "gap_14_phase_1_package_profile_definition_complete_phase_1436a"
    )


def test_defined_profiles_all_present() -> None:
    assert {
        PROFILE_PROTOCOL_CORE,
        PROFILE_OPERATOR_NODE,
        PROFILE_OPENCLAW_HOSTED,
        PROFILE_DEV,
    }.issubset(set(DEFINED_PROFILES))


def test_profile_names_are_strings() -> None:
    assert all(isinstance(profile, str) and profile for profile in DEFINED_PROFILES)


def test_non_activation_flags() -> None:
    assert PHASE_1436_NOT_ACTIVATED is True
    assert PUBLIC_RC_NOT_ACTIVATED is True


def test_pyproject_has_protocol_core_extra() -> None:
    assert "protocol-core" in _pyproject_extras()


def test_pyproject_has_operator_node_extra() -> None:
    assert "operator-node" in _pyproject_extras()


def test_pyproject_has_openclaw_hosted_extra() -> None:
    assert "openclaw-hosted" in _pyproject_extras()


def test_pyproject_protocol_core_no_network_stack() -> None:
    deps = _normalized_deps("protocol-core")

    assert "fastapi" not in deps
    assert "uvicorn" not in deps
    assert "requests" not in deps
    assert "httpx" not in deps


def test_pyproject_openclaw_hosted_no_lmdb() -> None:
    assert "lmdb" not in _normalized_deps("openclaw-hosted")


def test_pyproject_openclaw_hosted_no_grpcio() -> None:
    assert "grpcio" not in _normalized_deps("openclaw-hosted")


def test_spec_doc_exists() -> None:
    assert SPEC_DOC.exists()


def test_spec_doc_phase_token() -> None:
    text = SPEC_DOC.read_text(encoding="utf-8")

    assert "gap_14_phase_1_package_profile_definition_complete_phase_1436a" in text


def test_spec_doc_adr_0009_non_claim() -> None:
    text = SPEC_DOC.read_text(encoding="utf-8")

    assert "ADR-0009" in text
    assert "not ADR-0009 protocol-native distribution layers" in text
    assert "post-public-RC work" in text
