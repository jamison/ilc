# SPDX-License-Identifier: AGPL-3.0-only
"""R5a source-freeze and guarded Sufficiency packaging regressions."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

import ilc_core
from ilc_core.sufficiency import (
    MODEL_SELECTOR_ENABLED,
    SUFFICIENCY_LOCAL_INTERP_ENABLED,
    Candidate,
    EligibilityDecision,
    InterpGuardError,
    ModelProposal,
    ModelSelectorGuardError,
    SelectionRequest,
    execute_recipe,
    select_candidate,
)


ROOT = Path(__file__).resolve().parents[1]
SUFFICIENCY_FILES = (
    ROOT / "ilc_core/sufficiency/__init__.py",
    ROOT / "ilc_core/sufficiency/local_interp.py",
    ROOT / "ilc_core/sufficiency/model_selector.py",
)


def _pyproject() -> dict[str, object]:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


def test_v0435_source_version_and_package_declaration_are_exact() -> None:
    project = _pyproject()
    assert project["project"]["version"] == "0.4.35"  # type: ignore[index]
    assert ilc_core.__version__ == "0.4.35"
    packages = project["tool"]["setuptools"]["packages"]["find"]["include"]  # type: ignore[index]
    assert packages.count("ilc_core.sufficiency") == 1


def test_sufficiency_runtime_files_are_regular_guarded_source() -> None:
    assert all(path.is_file() for path in SUFFICIENCY_FILES)
    assert all("PUBLIC_RC_EXCLUDE" not in path.read_text(encoding="utf-8") for path in SUFFICIENCY_FILES)
    assert SUFFICIENCY_LOCAL_INTERP_ENABLED is False
    assert MODEL_SELECTOR_ENABLED is False


def test_nonfixture_interpreter_store_is_denied_before_recipe_parsing() -> None:
    with pytest.raises(InterpGuardError, match="sufficiency_local_interp_not_enabled"):
        execute_recipe(
            store=object(),
            recipe={"malformed": True},
            inputs={},
            root_invocation_id="fixture:r5a:guard",
        )


def test_nonfixture_model_backend_is_denied_before_invocation() -> None:
    class ExternalBackend:
        calls = 0

        def propose(self, candidates, request):
            del candidates, request
            self.calls += 1
            return ModelProposal("candidate", "1")

    backend = ExternalBackend()
    candidate = Candidate(
        candidate_id="candidate",
        candidate_version="1",
        operation_ref="fixture:operation:r5a",
        policy_ref="fixture:policy:r5a",
    )
    request = SelectionRequest(
        request_id="fixture:request:r5a",
        operation_ref=candidate.operation_ref,
        policy_ref=candidate.policy_ref,
        current_tick=0,
    )

    def eligible(item: Candidate, selection_request: SelectionRequest) -> EligibilityDecision:
        del item, selection_request
        return EligibilityDecision(True, "fixture_eligible", (), 0)

    with pytest.raises(ModelSelectorGuardError, match="model_selector_not_enabled"):
        select_candidate(
            candidates=(candidate,),
            request=request,
            backend=backend,
            evaluate_eligibility=eligible,
        )
    assert backend.calls == 0
