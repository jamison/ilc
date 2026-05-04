import subprocess
from pathlib import Path


TYPES_PATH = Path("ilc_core/types.py")


def test_cdl_085_opening_at_phase_1172() -> None:
    result = subprocess.run(
        [
            "git",
            "show",
            "ee0f6b48:docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "cdl_085_open_phase_1172" in result.stdout


def test_cdl_085_prelock_at_phase_1177() -> None:
    result = subprocess.run(
        [
            "git",
            "show",
            "509b6c6f:docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "cdl_085_prelock_committed_phase_1177" in result.stdout


def test_phi_bound_placeholder_before_ratification() -> None:
    content = TYPES_PATH.read_text(encoding="utf-8")
    assert "EDGE_MINT_PHI_BOUND" in content
    assert "EDGE_MINT_PHI_BOUND: Optional[float] = None" in content
