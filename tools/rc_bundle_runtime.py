#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tarfile
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class RcBundleRuntimeError(RuntimeError):
    pass


@dataclass(frozen=True)
class BundleInstallResult:
    version: str
    generated_at: str
    mode: str
    bundle_path: str
    repo_path: str
    venv_path: str
    config_path: str | None
    service_unit_dest: str | None
    replace_existing: bool
    config_files: list[str]
    service_unit_present: bool
    pip_executable: str
    python_executable: str


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RcBundleRuntimeError(
            f"command_failed:{' '.join(command)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def sync_tree(source_dir: Path, dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    for child in source_dir.iterdir():
        target = dest_dir / child.name
        if child.is_dir():
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(child, target)
        else:
            shutil.copy2(child, target)


def _stage_bundle(bundle_path: Path) -> Path:
    stage_root = Path(tempfile.mkdtemp(prefix='ilc-rc-bundle-stage-'))
    stage_repo = stage_root / 'repo'
    stage_repo.mkdir(parents=True, exist_ok=True)
    with tarfile.open(bundle_path, 'r:gz') as archive:
        archive.extractall(stage_repo)
    return stage_root


def _create_or_refresh_venv(*, venv_path: Path, recreate: bool) -> None:
    if recreate and venv_path.exists():
        shutil.rmtree(venv_path)
    if not (venv_path / 'bin/python').exists():
        venv_path.parent.mkdir(parents=True, exist_ok=True)
        run_command(['python3', '-m', 'venv', str(venv_path)])


def install_bundle(
    *,
    bundle_path: Path,
    repo_path: Path,
    venv_path: Path,
    config_source: Path | None,
    config_path: Path | None,
    service_unit_name: str,
    service_unit_dest: Path | None,
    replace_existing: bool,
    recreate_venv: bool,
) -> BundleInstallResult:
    bundle_path = bundle_path.resolve()
    if not bundle_path.is_file():
        raise RcBundleRuntimeError(f'bundle_missing:{bundle_path}')
    if config_source is not None and config_path is None:
        raise RcBundleRuntimeError('config_path_required_when_config_source_present')

    stage_root = _stage_bundle(bundle_path)
    stage_repo = stage_root / 'repo'
    backup_path: Path | None = None
    try:
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        if repo_path.exists():
            if not replace_existing:
                raise RcBundleRuntimeError(f'repo_path_exists:{repo_path}')
            backup_path = repo_path.parent / f"{repo_path.name}.backup.{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            if backup_path.exists():
                raise RcBundleRuntimeError(f'backup_path_exists:{backup_path}')
            repo_path.rename(backup_path)
        shutil.move(str(stage_repo), str(repo_path))

        if config_source is not None and config_path is not None:
            sync_tree(config_source, config_path)

        _create_or_refresh_venv(venv_path=venv_path, recreate=recreate_venv)
        python_executable = venv_path / 'bin/python'
        run_command([str(python_executable), '-m', 'pip', 'install', '--upgrade', 'pip'])
        run_command([str(python_executable), '-m', 'pip', 'install', '-e', str(repo_path)])

        unit_source = repo_path / 'deploy/systemd' / service_unit_name
        if not unit_source.is_file():
            raise RcBundleRuntimeError(f'service_unit_missing:{unit_source}')
        if service_unit_dest is not None:
            service_unit_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(unit_source, service_unit_dest)

        config_files: list[str] = []
        if config_path is not None and config_path.exists():
            config_files = sorted(path.name for path in config_path.iterdir())
        result = BundleInstallResult(
            version='rc_bundle_install_runtime_v0.1',
            generated_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
            mode='install',
            bundle_path=str(bundle_path),
            repo_path=str(repo_path),
            venv_path=str(venv_path),
            config_path=str(config_path) if config_path is not None else None,
            service_unit_dest=str(service_unit_dest) if service_unit_dest is not None else None,
            replace_existing=replace_existing,
            config_files=config_files,
            service_unit_present=unit_source.is_file(),
            pip_executable=str(python_executable),
            python_executable=str(python_executable),
        )
        if backup_path is not None and backup_path.exists():
            shutil.rmtree(backup_path)
        return result
    except Exception:
        if repo_path.exists() and backup_path is not None and backup_path.exists():
            shutil.rmtree(repo_path, ignore_errors=True)
            backup_path.rename(repo_path)
        raise
    finally:
        shutil.rmtree(stage_root, ignore_errors=True)


def update_bundle(
    *,
    bundle_path: Path,
    repo_path: Path,
    venv_path: Path,
    config_source: Path | None,
    config_path: Path | None,
    service_unit_name: str,
    service_unit_dest: Path | None,
) -> BundleInstallResult:
    result = install_bundle(
        bundle_path=bundle_path,
        repo_path=repo_path,
        venv_path=venv_path,
        config_source=config_source,
        config_path=config_path,
        service_unit_name=service_unit_name,
        service_unit_dest=service_unit_dest,
        replace_existing=True,
        recreate_venv=False,
    )
    return BundleInstallResult(
        version=result.version,
        generated_at=result.generated_at,
        mode='update',
        bundle_path=result.bundle_path,
        repo_path=result.repo_path,
        venv_path=result.venv_path,
        config_path=result.config_path,
        service_unit_dest=result.service_unit_dest,
        replace_existing=result.replace_existing,
        config_files=result.config_files,
        service_unit_present=result.service_unit_present,
        pip_executable=result.pip_executable,
        python_executable=result.python_executable,
    )


def write_result(path: Path, result: BundleInstallResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(result), indent=2, sort_keys=True) + '\n', encoding='utf-8')
