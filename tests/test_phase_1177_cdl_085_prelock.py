import subprocess
from pathlib import Path

from ilc_core.types import EDGE_MINT_PHI_BOUND


ROOT = Path(__file__).resolve().parents[1]
PRELOCK = ROOT / "docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md"


def test_phase_1177_prelock_spec_exists():
    assert PRELOCK.exists()


def test_phase_1177_prelock_token_present():
    text = PRELOCK.read_text(encoding="utf-8")
    assert "cdl_085_prelock_committed_phase_1177" in text


def test_phase_1177_all_five_q_resolutions_present():
    text = PRELOCK.read_text(encoding="utf-8")
    for q in ["Q1 Resolution", "Q2 Resolution", "Q3 Resolution", "Q4 Resolution", "Q5 Resolution"]:
        assert q in text


def test_phase_1177_cdl_085_historical_opening_state():
    result = subprocess.run(
        [
            "git",
            "show",
            "ee0f6b48:docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md",
        ],
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0
    assert "**Status:** OPEN" in result.stdout
    assert "cdl_085_open_phase_1172" in result.stdout


def test_phase_1177_phi_bound_not_locked_in_runtime():
    assert EDGE_MINT_PHI_BOUND is None
    runtime_types = (ROOT / "ilc_core/types.py").read_text(encoding="utf-8")
    assert 'EDGE_MINT_PHI_BOUND = Decimal("0.60")' not in runtime_types
    assert 'EDGE_MINT_PHI_BOUND: Decimal = Decimal("0.60")' not in runtime_types
