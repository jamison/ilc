from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tomllib


CONTRACT_PATH = Path("docs/specs/ilc_genesis_distribution_surface_contract_v0.1.md")
PYPROJECT_PATH = Path("pyproject.toml")

REQUIRED_SCRIPTS = [
    "ilc-mcp",
    "ilc-canon-verify",
    "ilc-canon-summary",
    "ilc-canon-export",
    "ilc-canon-bundle-validate",
    "ilc-canon-bundle-sign",
    "ilc-canon-bundle-pipeline",
    "ilc-canon-bundle-replay",
    "ilc-canon-cluster-a-replay-proof",
]


def _venv_bin(venv_path: Path, executable: str) -> Path:
    if sys.platform.startswith("win"):
        return venv_path / "Scripts" / executable
    return venv_path / "bin" / executable


def _run(cmd: list[str], cwd: Path, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_phase_225_contract_artifact_sections_present() -> None:
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    assert "## 2. Contract checks" in text
    assert "### 2.1 Packaging metadata and entry-point contract" in text
    assert "### 2.2 Clean-venv install contract" in text
    assert "### 2.3 Post-install import contract" in text
    assert "### 2.4 Console entry-point operability contract" in text
    assert "### 2.5 Operator tooling script smoke contract" in text
    assert "## 4. Explicit boundary to Phase 228" in text


def test_phase_225_pyproject_has_required_scripts_and_metadata() -> None:
    with PYPROJECT_PATH.open("rb") as handle:
        data = tomllib.load(handle)

    project = data["project"]
    assert project["name"]
    assert project["version"]
    assert project["requires-python"]
    assert project["dependencies"]

    scripts = project["scripts"]
    for script in REQUIRED_SCRIPTS:
        assert script in scripts
        assert isinstance(scripts[script], str)
        assert scripts[script]


def test_phase_225_clean_venv_install_import_and_entrypoints(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    venv_dir = tmp_path / "phase_225_distribution_venv"

    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        check=True,
        cwd=repo_root,
    )

    python_bin = _venv_bin(venv_dir, "python")
    pip_bin = _venv_bin(venv_dir, "pip")

    install = _run([str(pip_bin), "install", "."], cwd=repo_root, timeout=240)
    assert install.returncode == 0, install.stderr

    import_probe = _run(
        [str(python_bin), "-c", "import ilc_core; print('phase225_import_ok')"],
        cwd=repo_root,
    )
    assert import_probe.returncode == 0, import_probe.stderr
    assert "phase225_import_ok" in import_probe.stdout

    conformance_probe = _run(
        [
            str(python_bin),
            "-c",
            (
                "from ilc_core.analysis.node_value_governance_conformance "
                "import evaluate_node_value_governance_conformance; "
                "print('phase225_conformance_import_ok')"
            ),
        ],
        cwd=repo_root,
    )
    assert conformance_probe.returncode == 0, conformance_probe.stderr
    assert "phase225_conformance_import_ok" in conformance_probe.stdout

    for entrypoint in REQUIRED_SCRIPTS:
        entrypoint_bin = _venv_bin(venv_dir, entrypoint)
        cmd = [str(entrypoint_bin), "--help"]
        help_result = _run(cmd, cwd=repo_root)
        assert help_result.returncode == 0, (
            f"Entry point {entrypoint} failed\n"
            f"stdout:\n{help_result.stdout}\n"
            f"stderr:\n{help_result.stderr}"
        )
        combined = (help_result.stdout + "\n" + help_result.stderr).lower()
        assert "usage" in combined


def test_phase_225_operator_tooling_scripts_run_successfully() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    genesis_boot = _run([sys.executable, "tools/genesis_boot.py"], cwd=repo_root, timeout=30)
    assert genesis_boot.returncode == 0, genesis_boot.stderr
    assert "STATUS:  SUCCESS" in genesis_boot.stdout

    demo_walkthrough = _run([sys.executable, "tools/demo_walkthrough.py"], cwd=repo_root, timeout=60)
    assert demo_walkthrough.returncode == 0, demo_walkthrough.stderr
    assert "DEMO COMPLETE: SYSTEM IS LIVE" in demo_walkthrough.stdout
    assert "!!! DEMO FAILED" not in demo_walkthrough.stdout

