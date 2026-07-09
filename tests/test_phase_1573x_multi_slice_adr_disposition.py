from __future__ import annotations

from pathlib import Path


DISPOSITION = Path(
    "docs/specs/ilc_phase_1573x_multi_slice_encrustation_adr_disposition_v0.1.md"
)
ADR_0037 = Path("docs/adr/ADR_0037_Genesis_Canonical_Lineage_Contract.md")
ACCEPTANCE_REVIEW = Path("docs/adr/adr_0037_acceptance_review_1173_v0.1.md")
HANDOFF_1175 = Path("docs/specs/ilc_window_1166_1175_handoff_1175_v0.1.md")
STATUS = Path("docs/phases/STATUS.md")


def test_disposition_records_no_duplicate_adr_opened() -> None:
    text = DISPOSITION.read_text(encoding="utf-8")

    assert "Phase 1573x did not open a new ADR" in text
    assert "no new ADR number consumed" in text
    assert "no ADR status changed" in text
    assert "ADR-0037" in text


def test_adr0037_already_contains_multi_slice_encrustation_contract() -> None:
    adr = ADR_0037.read_text(encoding="utf-8")
    review = ACCEPTANCE_REVIEW.read_text(encoding="utf-8")

    assert "## 6. Multi-Slice Encrustation" in adr
    assert "A fork that cannot converge through all six slices" in adr
    assert "## 7. Fork Boundary" in adr
    assert "Criterion 3 — Multi-slice encrustation and fork boundary specified" in review
    assert "**Result: PASS.**" in review
    assert "`adr_0037_accepted_phase_1173`" in review


def test_window_1175_records_original_carry_forward_as_closed() -> None:
    handoff = HANDOFF_1175.read_text(encoding="utf-8")

    assert "Closed in Window 1166-1175:" in handoff
    assert "genesis_multi_slice_encrustation_model_required_for_lineage_contract_adr" in handoff
    assert "ADR-0037 was accepted with token `adr_0037_accepted_phase_1173`" in handoff


def test_status_tokens_record_disposition_not_adr_opening() -> None:
    status = STATUS.read_text(encoding="utf-8")

    assert "adr_multi_slice_encrustation_model_existing_adr0037_confirmed_phase_1573x" in status
    assert (
        "genesis_multi_slice_encrustation_model_required_for_lineage_contract_adr_"
        "closed_by_adr0037_confirmed_phase_1573x"
    ) in status
    assert "public_path_remains_blocked_phase_1573x" in status
    assert "adr_multi_slice_encrustation_model_opened_phase_1573x" not in status


def test_no_duplicate_multi_slice_adr_file_was_created() -> None:
    duplicate_files = [
        path
        for path in Path("docs/adr").glob("ADR_*Multi_Slice_Encrustation*.md")
        if path.name != "ADR_0037_Genesis_Canonical_Lineage_Contract.md"
    ]

    assert duplicate_files == []
