from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "docs/antigravity_tasks/antigravity_prompt__phase_1513p_g9_window_coherence_capsule_update.md"
COHERENCE = ROOT / "docs/specs/ilc_window_1505p_coherence_1513p_v0.1.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.65p_private_1505p.md"
REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
SEQUENCE_LOCK = ROOT / "docs/specs/ilc_phase_1505p_1514p_sequence_lock_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1513p_window_coherence_capsule_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
AGENTS = ROOT / "AGENTS.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
DYNAMIC_RANKING = ROOT / "ilc_core/economics/dynamic_ranking_multiplier_runtime.py"
RUST_BRIDGE = ROOT / "ilc_core/network/rust_p2p_bridge.py"
JURY_FINALITY = ROOT / "ilc_core/epistemic/jury_finality_evaluator.py"
LOCAL_STORE = ROOT / "ilc_core/harness/local_immutable_store.py"


TOKENS = [
    "window_1505p_coherence_complete_phase_1513p",
    "context_capsule_v5_65p_private_1505p_committed",
    "obligation_register_sweep_complete_phase_1513p",
    "public_path_still_blocked_phase_1513p",
    "cdl_096_eligible_not_opened_phase_1513p",
]

WINDOW_OBLS = [
    "OBL-004",
    "OBL-008",
    "OBL-011",
    "OBL-012",
    "OBL-015",
    "OBL-016",
    "OBL-017",
    "OBL-018",
    "OBL-019",
    "OBL-035",
    "OBL-036",
    "OBL-037",
    "OBL-038",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _row_for(obligation_id: str) -> str:
    for line in _read(REGISTER).splitlines():
        if line.startswith(f"| {obligation_id} |"):
            return line
    raise AssertionError(f"missing row {obligation_id}")


def test_phase_1513p_docs_exist_and_have_exclusion_headers() -> None:
    for path in (PROMPT, COHERENCE, CAPSULE):
        text = _read(path)
        assert "PUBLIC_RC_EXCLUDE" in text
        assert "PUBLIC_RC_EXCLUDE_REASON" in text


def test_phase_1513p_tokens_and_frontier_are_updated() -> None:
    texts = {
        "prompt": _read(PROMPT),
        "coherence": _read(COHERENCE),
        "capsule": _read(CAPSULE),
        "register": _read(REGISTER),
        "sequence_lock": _read(SEQUENCE_LOCK),
        "walkthrough": _read(WALKTHROUGH),
        "status": _read(STATUS),
        "planning_index": _read(PLANNING_INDEX),
        "agents": _read(AGENTS),
    }

    for token in TOKENS:
        assert any(token in text for text in texts.values()), token
        assert token in texts["walkthrough"], token
        assert token in texts["status"], token

    assert "Phase 1514p remains SENSITIVE" in texts["status"]
    assert "GO Phase 1514p" in texts["coherence"]
    assert texts["planning_index"].count("⬅ CURRENT") == 1
    assert "ilc_window_1505p_coherence_1513p_v0.1.md" in texts["planning_index"]
    assert "context_capsule_v5.65p_private_1505p.md` ⬅ CURRENT" in texts[
        "planning_index"
    ]


def test_window_obligations_are_closed_and_obl026_carries_forward() -> None:
    for obligation_id in WINDOW_OBLS:
        assert "| closed |" in _row_for(obligation_id), obligation_id

    row_026 = _row_for("OBL-026")
    assert "| open |" in row_026
    assert "ADR-0009" in row_026

    register = _read(REGISTER)
    assert "OBL-002 is a permanent release-control invariant" in register


def test_coherence_records_cdl096_eligible_but_not_opened_boundary() -> None:
    cdl_register = _read(CDL_REGISTER)
    coherence = _read(COHERENCE)
    capsule = _read(CAPSULE)

    assert "| CDL-096 |" not in cdl_register
    for text in (coherence, capsule):
        assert "cdl_096_eligible_to_open_phase_1509p" in text
        assert "cdl_096_eligible_not_opened_phase_1513p" in text
        assert "Werner flow-governor runtime activation remains unauthorized" in text


def test_guard_states_remain_true_and_non_activation_floor_is_present() -> None:
    guards = {
        DYNAMIC_RANKING: "DYNAMIC_RANKING_MULTIPLIER_NOT_ACTIVATED: bool = True",
        RUST_BRIDGE: "RUST_P2P_BRIDGE_NOT_ACTIVATED: Final[bool] = True",
        JURY_FINALITY: "JURY_FINALITY_EVALUATOR_NOT_PRODUCTION: Final[bool] = True",
        LOCAL_STORE: "LOCAL_IMMUTABLE_STORE_NOT_PRODUCTION = True",
    }
    for path, phrase in guards.items():
        assert phrase in _read(path)

    assert "CDL_094_ADMISSION_WIRE_NOT_ACTIVATED: Final[bool] = True" in _read(
        RUST_BRIDGE
    )

    combined = _read(COHERENCE) + _read(CAPSULE)
    for phrase in (
        "public_path_still_blocked_phase_1513p",
        "does not authorize",
        "CDL-096 opening",
        "ECU minting",
        "ILC settlement",
        "Clearing any NOT_ACTIVATED guard",
    ):
        assert phrase in combined
