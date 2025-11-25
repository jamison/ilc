import subprocess
import sys
import os
from pathlib import Path


def test_ballast_controller_runs_and_is_not_worse():
    """
    Black-box test: run the data_center_ballast simulation as a subprocess,
    parse utilization metrics, and assert the controller does not degrade
    average utilization compared to baseline.

    This is intentionally loose: we assert non-degradation, not optimality.
    """
    root = Path(__file__).resolve().parents[1]
    script = root / "simulations" / "data_center_ballast.py"

    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    out = proc.stdout

    base = None
    ctrl = None

    for line in out.splitlines():
        line = line.strip()
        if line.startswith("Baseline avg utilization:"):
            try:
                base = float(line.split(":")[1].strip())
            except ValueError:
                pass
        elif line.startswith("With ILC avg utilization:"):
            try:
                ctrl = float(line.split(":")[1].strip())
            except ValueError:
                pass

    # Ensure both metrics were printed
    assert base is not None
    assert ctrl is not None

    # Controller should not do worse than baseline on average.
    assert ctrl >= base
