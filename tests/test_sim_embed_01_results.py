"""
Gate test: SIM-EMBED-01 research artifact verification.
"""

from pathlib import Path


RESULTS_PATH = Path("docs/research/ilc_sim_embed_01_results_v0.1.md")
SCRIPT_PATH = Path("tools/sim/sim_embed_01_model_calibration.py")


def _read() -> str:
    return RESULTS_PATH.read_text(encoding="utf-8")


def test_results_and_script_exist() -> None:
    assert RESULTS_PATH.is_file()
    assert SCRIPT_PATH.is_file()


def test_required_tokens_present() -> None:
    text = _read()
    assert "sim_embed_01_recommended_model_per_content_type=" in text
    assert "`run_h002_sim_embed_01_verdict=pass`" in text


def test_scope_correction_is_explicit() -> None:
    text = _read()
    assert "payload-modality families" in text
    assert "does **not** amend ADR-0030" in text


def test_text_recommendations_select_minilm() -> None:
    text = _read()
    assert "`text/plain` | `sentence-transformers/all-MiniLM-L6-v2`" in text
    assert "`text/markdown` | `sentence-transformers/all-MiniLM-L6-v2`" in text
    assert "`application/json` | `sentence-transformers/all-MiniLM-L6-v2` with canonical JSON" in text


def test_image_recommendation_selects_clip_baseline() -> None:
    text = _read()
    assert "`image/*` | `openai/clip-vit-base-patch32`" in text
    assert "diagram / screenshot-like imagery" in text


def test_openai_candidate_is_honestly_marked_unexecuted() -> None:
    text = _read()
    assert "OPENAI_API_KEY" in text
    assert "was not benchmarked" in text


def test_staleness_thresholds_are_explicit() -> None:
    text = _read()
    for token in ("`32` epochs", "`16` epochs", "`48` epochs", "`4` epochs"):
        assert token in text


def test_raw_numeric_markers_are_present() -> None:
    text = _read()
    for marker in ("0.2501", "12.23", "0.1961", "40.87", "0.2323", "173.07"):
        assert marker in text
