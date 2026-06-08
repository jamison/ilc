from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _venv_bin(venv_path: Path, executable: str) -> Path:
    if sys.platform.startswith("win"):
        return venv_path / "Scripts" / executable
    return venv_path / "bin" / executable


def _install_env() -> dict[str, str]:
    env = dict(os.environ)
    cargo_bin = Path.home() / ".cargo" / "bin"
    if cargo_bin.exists():
        env["PATH"] = f"{cargo_bin}{os.pathsep}{env.get('PATH', '')}"
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    return env


def test_phase_224_post_install_import_smoke(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    venv_dir = tmp_path / "phase_224_smoke_venv"

    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        check=True,
        cwd=repo_root,
    )

    pip_bin = _venv_bin(venv_dir, "pip")
    python_bin = _venv_bin(venv_dir, "python")

    subprocess.run(
        [
            str(pip_bin),
            "install",
            ".",
        ],
        check=True,
        cwd=repo_root,
        env=_install_env(),
    )

    import_probe = subprocess.run(
        [
            str(python_bin),
            "-c",
            (
                "from ilc_core.analysis.node_value_governance_conformance "
                "import evaluate_node_value_governance_conformance; "
                "print('phase224_import_ok')"
            ),
        ],
        check=True,
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert "phase224_import_ok" in import_probe.stdout
