from pathlib import Path


SEQUENCE_SPEC = Path("docs/specs/ilc_genesis_packaging_distribution_sequence_222_229_v0.1.md")
MASTER_PLAN = Path("docs/ILC_Master_Development_Plan_v0.4.md")
TODO_PATH = Path("TODO.txt")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_222_sequence_spec_exists_and_has_locked_window() -> None:
    text = _read(SEQUENCE_SPEC)
    assert "ILC Genesis Packaging Distribution Readiness Sequence 222-229 v0.1" in text
    assert "## 4. Locked Phase Window (222-229)" in text

    expected_rows = (
        "| 1 | 222 | `spec` |",
        "| 2 | 223 | `hygiene` |",
        "| 3 | 224 | `integration` |",
        "| 4 | 226 | `triage` |",
        "| 5 | 227 | `remediation-or-noop` |",
        "| 6 | 225 | `distribution` |",
        "| 7 | 228 | `release` |",
        "| 8 | 229 | `closure` |",
    )
    for row in expected_rows:
        assert row in text


def test_phase_222_dependency_chain_and_non_numeric_order_are_locked() -> None:
    text = _read(SEQUENCE_SPEC)
    assert "## 5. Locked Dependency Chain" in text

    expected_chain = (
        "- `223` depends on `222`.",
        "- `224` depends on `223`.",
        "- `226` depends on `224`.",
        "- `227` depends on `226`.",
        "- `225` depends on `227` (or `226` when `227` is a documented no-op).",
        "- `228` depends on `225`.",
        "- `229` depends on `228`.",
    )
    for item in expected_chain:
        assert item in text

    row_227 = "| 5 | 227 | `remediation-or-noop` |"
    row_225 = "| 6 | 225 | `distribution` |"
    assert text.index(row_227) < text.index(row_225)


def test_phase_222_constraint_locks_are_explicit() -> None:
    text = _read(SEQUENCE_SPEC)

    assert "### 6.1 Phase 223 hard scope cap" in text
    assert "`ilc_core/analysis/` only" in text
    assert "Touch budget cap: no more than five files." in text

    assert "### 6.2 Phase 224 integration composition lock" in text
    assert "pip install ." in text
    assert "node_value_governance_conformance" in text

    assert "### 6.3 Phase 226 Genesis-blocker rubric lock" in text
    rubric_terms = (
        "first-run breakage",
        "key or data loss risk",
        "exploitable rollback or state-corruption risk",
        "no viable mitigation path/workaround",
    )
    for term in rubric_terms:
        assert term in text

    assert "### 6.4 Phase 227 closure artifact lock" in text
    assert "formal no-op closure with per-CDL deferral rationale" in text

    assert "### 6.5 Phase 228 release provenance lock" in text
    assert "sdist" in text
    assert "wheel" in text
    assert "checksum provenance output" in text


def test_phase_222_todo_and_master_plan_reference_sequence_spec() -> None:
    pointer = "docs/specs/ilc_genesis_packaging_distribution_sequence_222_229_v0.1.md"
    master_plan_text = _read(MASTER_PLAN)
    todo_text = _read(TODO_PATH)

    assert pointer in master_plan_text
    assert pointer in todo_text
    assert "[TODO – Genesis Packaging Distribution Readiness Sequence (222-229 Lock)]" in todo_text
