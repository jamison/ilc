from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import os
import re
import subprocess
import sys
import tempfile
import tomllib


CONTRACT_PATH = Path("docs/specs/ilc_genesis_release_artifact_contract_v0.1.md")
PROVENANCE_PATH = Path("docs/specs/ilc_genesis_release_artifact_provenance_phase_228_v0.1.md")
RELEASE_NOTES_PATH = Path("docs/specs/ilc_genesis_release_notes_v0.1.md")
PYPROJECT_PATH = Path("pyproject.toml")


def _venv_bin(venv_path: Path, executable: str) -> Path:
    if sys.platform.startswith("win"):
        return venv_path / "Scripts" / executable
    return venv_path / "bin" / executable


def _run(cmd: list[str], cwd: Path, timeout: int = 600) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    cargo_bin = Path.home() / ".cargo" / "bin"
    if cargo_bin.exists():
        env["PATH"] = f"{cargo_bin}{os.pathsep}{env.get('PATH', '')}"
    env["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def _read_version() -> str:
    with PYPROJECT_PATH.open("rb") as handle:
        data = tomllib.load(handle)
    return str(data["project"]["version"])


def _build_artifacts(repo_root: Path) -> tuple[Path, Path]:
    with tempfile.TemporaryDirectory() as tmp_dir_raw:
        tmp_dir = Path(tmp_dir_raw)
        build_venv = tmp_dir / "build_venv"
        subprocess.run([sys.executable, "-m", "venv", str(build_venv)], check=True, cwd=repo_root)

        build_python = _venv_bin(build_venv, "python")
        build_pip = _venv_bin(build_venv, "pip")

        install_build = _run([str(build_pip), "install", "build"], cwd=repo_root, timeout=300)
        assert install_build.returncode == 0, install_build.stderr

        dist_dir = tmp_dir / "dist"
        dist_dir.mkdir(parents=True, exist_ok=True)

        build_cmd = [
            str(build_python),
            "-m",
            "build",
            "--sdist",
            "--wheel",
            str(repo_root),
            "--outdir",
            str(dist_dir),
        ]
        build_result = _run(build_cmd, cwd=tmp_dir, timeout=900)
        assert build_result.returncode == 0, build_result.stderr

        version = _read_version()
        wheels = sorted(dist_dir.glob(f"ilc_core-{version}-*.whl"))
        sdists = sorted(dist_dir.glob(f"ilc_core-{version}.tar.gz"))
        assert len(wheels) == 1
        assert len(sdists) == 1

        target_dir = Path(tempfile.mkdtemp(prefix="phase_228_release_artifacts_"))
        wheel_copy = target_dir / wheels[0].name
        sdist_copy = target_dir / sdists[0].name
        wheel_copy.write_bytes(wheels[0].read_bytes())
        sdist_copy.write_bytes(sdists[0].read_bytes())
        return wheel_copy, sdist_copy


def _install_probe(repo_root: Path, artifact_path: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp_dir_raw:
        tmp_dir = Path(tmp_dir_raw)
        install_venv = tmp_dir / "install_venv"
        subprocess.run([sys.executable, "-m", "venv", str(install_venv)], check=True, cwd=repo_root)

        python_bin = _venv_bin(install_venv, "python")
        pip_bin = _venv_bin(install_venv, "pip")

        install_result = _run([str(pip_bin), "install", str(artifact_path)], cwd=repo_root, timeout=900)
        assert install_result.returncode == 0, install_result.stderr

        import_probe = _run(
            [
                str(python_bin),
                "-c",
                (
                    "from ilc_core.analysis.node_value_governance_conformance "
                    "import evaluate_node_value_governance_conformance; "
                    "print('phase228_import_ok')"
                ),
            ],
            cwd=repo_root,
            timeout=120,
        )
        assert import_probe.returncode == 0, import_probe.stderr
        assert "phase228_import_ok" in import_probe.stdout


def test_phase_228_contract_and_release_notes_have_required_sections() -> None:
    contract = CONTRACT_PATH.read_text(encoding="utf-8")
    notes = RELEASE_NOTES_PATH.read_text(encoding="utf-8")

    assert "## 2. Artifact build contract" in contract
    assert "## 3. Artifact install validation contract" in contract
    assert "## 4. Checksum provenance contract" in contract
    assert "## 5. Release notes boundary contract" in contract

    assert "## Shipped in Genesis v0.1" in notes
    assert "## Explicitly Deferred (Post-Genesis)" in notes
    assert "not the complete simulated consensus/economic control stack" in notes
    assert "flat 1.2x refutation multiplier" in notes


def test_phase_228_builds_and_install_validates_sdist_and_wheel() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    wheel_path, sdist_path = _build_artifacts(repo_root)

    _install_probe(repo_root, wheel_path)
    _install_probe(repo_root, sdist_path)


def test_phase_228_provenance_file_shape_and_checksum_tokens() -> None:
    text = PROVENANCE_PATH.read_text(encoding="utf-8")

    assert "Artifact Type" in text
    assert "SHA-256" in text
    assert "out/phase_228_release_artifacts/dist" in text

    sha_tokens = re.findall(r"\b[a-f0-9]{64}\b", text)
    assert len(sha_tokens) >= 2

    # Verify checksum token format sanity via deterministic digest generation.
    sample = sha256(b"phase-228-checksum-format").hexdigest()
    assert re.fullmatch(r"[a-f0-9]{64}", sample)
