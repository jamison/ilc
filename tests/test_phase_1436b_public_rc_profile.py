"""Regression tests for Phase 1436b public-RC package profile closure."""

from __future__ import annotations

from pathlib import Path
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover - Python 3.10 fallback
    import tomli as tomllib

from ilc_core.distribution.package_profiles import (
    DEFINED_PROFILES,
    GAP_14_CLOSED_TOKEN,
    GAP_14_PHASE_2_TOKEN,
    PACKAGE_PROFILES_VERSION,
    PHASE_1436_NOT_ACTIVATED,
    PROFILE_PUBLIC_RC,
    PUBLIC_RC_NOT_ACTIVATED,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = REPO_ROOT / "pyproject.toml"
SPEC_DOC = REPO_ROOT / "docs/specs/ilc_public_rc_distribution_profile_1436b_v0.1.md"
SEQUENCE_LOCK = REPO_ROOT / "docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md"


def _pyproject_extras() -> dict[str, list[str]]:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"][
        "optional-dependencies"
    ]


def _normalized_deps(profile: str) -> set[str]:
    deps = _pyproject_extras()[profile]
    return {dep.split(">=")[0].split("==")[0].lower() for dep in deps}


def test_package_profiles_version_is_1436b() -> None:
    assert "1436b" in PACKAGE_PROFILES_VERSION


def test_gap_14_phase_2_token() -> None:
    assert (
        GAP_14_PHASE_2_TOKEN
        == "gap_14_phase_2_public_rc_profile_complete_phase_1436b"
    )


def test_gap_14_closed_token() -> None:
    assert GAP_14_CLOSED_TOKEN == "gap_14_closed_phase_1436b"


def test_public_rc_profile_in_defined_profiles() -> None:
    assert PROFILE_PUBLIC_RC in DEFINED_PROFILES


def test_all_five_profiles_defined() -> None:
    assert len(DEFINED_PROFILES) == 5


def test_non_activation_flags() -> None:
    assert PHASE_1436_NOT_ACTIVATED is True
    assert PUBLIC_RC_NOT_ACTIVATED is True


def test_pyproject_has_public_rc_extra() -> None:
    assert "public-rc" in _pyproject_extras()


def test_public_rc_profile_has_lmdb() -> None:
    assert "lmdb" in _normalized_deps("public-rc")


def test_public_rc_profile_has_grpcio() -> None:
    assert "grpcio" in _normalized_deps("public-rc")


def test_openclaw_hosted_still_no_lmdb() -> None:
    assert "lmdb" not in _normalized_deps("openclaw-hosted")


def test_spec_doc_exists() -> None:
    assert SPEC_DOC.exists()


def test_spec_doc_gap_14_closed_token() -> None:
    text = SPEC_DOC.read_text(encoding="utf-8")

    assert "gap_14_closed_phase_1436b" in text


def test_spec_doc_adr_0009_non_claim() -> None:
    text = SPEC_DOC.read_text(encoding="utf-8")

    assert "ADR-0009" in text
    assert "post-public-RC" in text


def test_spec_doc_phase_1436_non_activation() -> None:
    text = SPEC_DOC.read_text(encoding="utf-8")

    assert "Phase 1436 remains SENSITIVE" in text
    assert "GO Phase 1436" in text


def test_sequence_lock_gap_14_closed_token() -> None:
    text = SEQUENCE_LOCK.read_text(encoding="utf-8")

    assert "gap_14_closed_phase_1436b" in text
