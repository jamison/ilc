#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "out/rc0_1_bundle_install_proof"
DEFAULT_HOSTS_PATH = REPO_ROOT / "testbed/hosts.json"


class BundleInstallProofError(RuntimeError):
    pass


def _run(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=str(cwd) if cwd is not None else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise BundleInstallProofError(
            f"command_failed:{' '.join(command)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def _load_hosts(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _remote_host_map(hosts_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["name"]: item for item in hosts_payload.get("remote_hosts", [])}


def _ssh_prefix(host_payload: dict[str, Any]) -> list[str]:
    return [
        "ssh",
        "-A",
        "-n",
        "-o",
        "BatchMode=yes",
        f"{host_payload['ssh_user']}@{host_payload['ssh_host']}",
    ]


def _scp_to_remote(host_payload: dict[str, Any], source: Path, remote_path: str) -> None:
    result = subprocess.run(
        ["scp", "-B", str(source), f"{host_payload['ssh_user']}@{host_payload['ssh_host']}:{remote_path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise BundleInstallProofError(
            f"scp_failed:{source}:{remote_path}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def _bundle_archive(bundle_root: Path) -> Path:
    archive = bundle_root / "ilc_rc0_1_bundle.tar.gz"
    if not archive.is_file():
        raise BundleInstallProofError(f"bundle_archive_missing:{archive}")
    return archive


def _local_script(bundle_root: Path, name: str) -> Path:
    path = bundle_root / "installer" / name
    if not path.is_file():
        raise BundleInstallProofError(f"bundle_installer_missing:{path}")
    return path


def _prove_local(bundle_root: Path) -> dict[str, Any]:
    proof_root = Path(_run(["mktemp", "-d", "/tmp/ilc-release-bundle-home.XXXXXX"], cwd=REPO_ROOT).stdout.strip())
    install_manifest = proof_root / "install_result.json"
    update_manifest = proof_root / "update_result.json"
    archive_path = _bundle_archive(bundle_root)
    install_script = _local_script(bundle_root, "rc_install_bundle_node.py")
    update_script = _local_script(bundle_root, "rc_update_bundle_node.py")
    try:
        _run(
            [
                "python3",
                str(install_script),
                "--bundle",
                str(archive_path),
                "--repo-path",
                str(proof_root / "current"),
                "--venv-path",
                str(proof_root / "venv"),
                "--config-source",
                str(REPO_ROOT / "testbed/configs/ilc-node-1"),
                "--config-path",
                str(proof_root / "config"),
                "--service-unit-dest",
                str(proof_root / "systemd" / "ilc-node-v1.service"),
                "--emit-path",
                str(install_manifest),
            ],
            cwd=bundle_root,
        )
        _run(
            [
                "python3",
                str(update_script),
                "--bundle",
                str(archive_path),
                "--repo-path",
                str(proof_root / "current"),
                "--venv-path",
                str(proof_root / "venv"),
                "--config-source",
                str(REPO_ROOT / "testbed/configs/ilc-node-1"),
                "--config-path",
                str(proof_root / "config"),
                "--service-unit-dest",
                str(proof_root / "systemd" / "ilc-node-v1.service"),
                "--emit-path",
                str(update_manifest),
            ],
            cwd=bundle_root,
        )
        payload = json.loads(install_manifest.read_text(encoding="utf-8"))
        payload.update(
            {
                "host": "ilc-node-1",
                "mode": "local_bundle",
                "status": "ok",
                "update_result": json.loads(update_manifest.read_text(encoding="utf-8")),
            }
        )
        return payload
    finally:
        subprocess.run(["rm", "-rf", str(proof_root)], capture_output=True, text=True, check=False)


def _prove_remote(bundle_root: Path, host_payload: dict[str, Any]) -> dict[str, Any]:
    archive_path = _bundle_archive(bundle_root)
    installer_dir = bundle_root / "installer"
    proof_root = _run(_ssh_prefix(host_payload) + ["mktemp -d /tmp/ilc-release-bundle.XXXXXX"]).stdout.strip()
    try:
        _run(_ssh_prefix(host_payload) + [f"mkdir -p {proof_root}/bundle/installer"])
        _scp_to_remote(host_payload, archive_path, f"{proof_root}/bundle/{archive_path.name}")
        for name in ("rc_bundle_runtime.py", "rc_install_bundle_node.py", "rc_update_bundle_node.py", "check_rc0_1_release_gate.py"):
            _scp_to_remote(host_payload, installer_dir / name, f"{proof_root}/bundle/installer/{name}")

        remote_install_manifest = f"{proof_root}/install_result.json"
        remote_update_manifest = f"{proof_root}/update_result.json"
        remote_install = (
            f"cd {proof_root}/bundle && "
            f"python3 installer/rc_install_bundle_node.py "
            f"--bundle {proof_root}/bundle/{archive_path.name} "
            f"--repo-path {proof_root}/current "
            f"--venv-path {proof_root}/venv "
            f"--config-source {host_payload['config_path']} "
            f"--config-path {proof_root}/config "
            f"--service-unit-dest {proof_root}/systemd/ilc-node-v1.service "
            f"--emit-path {remote_install_manifest}"
        )
        remote_update = (
            f"cd {proof_root}/bundle && "
            f"python3 installer/rc_update_bundle_node.py "
            f"--bundle {proof_root}/bundle/{archive_path.name} "
            f"--repo-path {proof_root}/current "
            f"--venv-path {proof_root}/venv "
            f"--config-source {host_payload['config_path']} "
            f"--config-path {proof_root}/config "
            f"--service-unit-dest {proof_root}/systemd/ilc-node-v1.service "
            f"--emit-path {remote_update_manifest}"
        )
        _run(_ssh_prefix(host_payload) + [remote_install])
        _run(_ssh_prefix(host_payload) + [remote_update])
        install_result = _run(_ssh_prefix(host_payload) + [f"cat {remote_install_manifest}"])
        update_result = _run(_ssh_prefix(host_payload) + [f"cat {remote_update_manifest}"])
        payload = json.loads(install_result.stdout.strip())
        payload.update(
            {
                "host": host_payload["name"],
                "mode": "remote_bundle",
                "status": "ok",
                "update_result": json.loads(update_result.stdout.strip()),
            }
        )
        return payload
    finally:
        subprocess.run(_ssh_prefix(host_payload) + [f"rm -rf '{proof_root}'"], capture_output=True, text=True, check=False)


def prove_bundle_install(*, bundle_root: Path, hosts_path: Path, output_root: Path, include_home: bool) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    hosts_payload = _load_hosts(hosts_path)
    remote_hosts = _remote_host_map(hosts_payload)
    results: list[dict[str, Any]] = []
    if include_home:
        results.append(_prove_local(bundle_root))
    for host_name in sorted(remote_hosts):
        results.append(_prove_remote(bundle_root, remote_hosts[host_name]))

    manifest = {
        "version": "rc0_1_release_bundle_install_proof_v0.1",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "bundle_root": str(bundle_root),
        "bundle_manifest_path": str(bundle_root / "manifest.json"),
        "include_home": include_home,
        "results": results,
    }
    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prove that the copied RC0.1 release bundle installer surface is runnable.")
    parser.add_argument("--bundle-root", required=True)
    parser.add_argument("--hosts", default=str(DEFAULT_HOSTS_PATH))
    parser.add_argument("--output-root")
    parser.add_argument("--include-home", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output_root = Path(args.output_root) if args.output_root else DEFAULT_OUTPUT_ROOT / datetime.now().strftime("%Y%m%d_%H%M%S")
    try:
        manifest = prove_bundle_install(
            bundle_root=Path(args.bundle_root),
            hosts_path=Path(args.hosts),
            output_root=output_root,
            include_home=args.include_home,
        )
    except (BundleInstallProofError, json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"marker": "rc0_1_release_bundle_install_proof_failed", "detail": str(exc)}, sort_keys=True, separators=(",", ":")))
        return 1
    print(json.dumps({"marker": "rc0_1_release_bundle_install_proof_ok", "manifest": manifest}, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
