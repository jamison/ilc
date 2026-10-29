# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import base64
import csv
import hashlib
import io
import tomllib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from tools.check_public_rc_package_boundary import BoundaryError, build_report

import ilc_core


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _record_digest(payload: bytes) -> str:
    value = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).rstrip(b"=")
    return "sha256=" + value.decode("ascii")


def _wheel(path: Path, members: dict[str, bytes]) -> None:
    record_path = "ilc_core-0.0.0.dist-info/RECORD"
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    for name, payload in sorted(members.items()):
        writer.writerow((name, _record_digest(payload), str(len(payload))))
    writer.writerow((record_path, "", ""))
    complete = {**members, record_path: output.getvalue().encode("utf-8")}
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        for name, payload in sorted(complete.items()):
            archive.writestr(name, payload)


def test_v0436_live_package_versions_and_capproof_declaration_match() -> None:
    with Path("pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)

    packages = project["tool"]["setuptools"]["packages"]["find"]["include"]
    assert project["project"]["version"] == "0.4.36"
    assert ilc_core.__version__ == "0.4.36"
    assert packages.count("ilc_core.capproof") == 1


def test_source_tree_accepts_relative_and_literal_dynamic_imports(tmp_path: Path) -> None:
    _write(tmp_path / "ilc_core/__init__.py", "")
    _write(tmp_path / "ilc_core/capproof/__init__.py", "from .worker import VALUE\n")
    _write(tmp_path / "ilc_core/capproof/worker.py", "VALUE = 1\n")
    _write(
        tmp_path / "ilc_core/loader.py",
        "import importlib\nVALUE = importlib.import_module('ilc_core.capproof.worker').VALUE\n",
    )

    report = build_report(
        source_root=tmp_path,
        wheel=None,
        required_packages=["ilc_core.capproof"],
    )

    assert report["verdict"] == "pass"
    assert report["surfaces"][0]["missing_internal_edges"] == []


def test_source_tree_rejects_missing_internal_import(tmp_path: Path) -> None:
    _write(tmp_path / "ilc_core/__init__.py", "")
    _write(tmp_path / "ilc_core/consumer.py", "from ilc_core.missing import VALUE\n")

    report = build_report(source_root=tmp_path, wheel=None, required_packages=[])

    assert report["verdict"] == "fail_closed"
    assert report["surfaces"][0]["missing_internal_edges"] == [
        {
            "source_module": "ilc_core.consumer",
            "source_path": "ilc_core/consumer.py",
            "target": "ilc_core.missing",
        }
    ]


def test_reference_tree_detects_stripped_from_import(tmp_path: Path) -> None:
    public = tmp_path / "public"
    private = tmp_path / "private"
    _write(public / "ilc_core/__init__.py", "")
    _write(public / "ilc_core/consumer.py", "from ilc_core.private import helper\n")
    _write(public / "ilc_core/private/__init__.py", "VALUE = 1\n")
    _write(private / "ilc_core/__init__.py", "")
    _write(private / "ilc_core/consumer.py", "from ilc_core.private import helper\n")
    _write(private / "ilc_core/private/__init__.py", "VALUE = 1\n")
    _write(private / "ilc_core/private/helper.py", "VALUE = 1\n")

    report = build_report(
        source_root=public,
        wheel=None,
        required_packages=[],
        reference_source_root=private,
    )

    assert report["verdict"] == "fail_closed"
    assert report["surfaces"][0]["missing_internal_edges"] == [
        {
            "source_module": "ilc_core.consumer",
            "source_path": "ilc_core/consumer.py",
            "target": "ilc_core.private.helper",
        }
    ]


def test_wheel_rejects_marker_and_missing_required_package(tmp_path: Path) -> None:
    wheel = tmp_path / "ilc_core-0.0.0-py3-none-any.whl"
    _wheel(
        wheel,
        {
            "ilc_core/__init__.py": b"",
            "ilc_core/internal.py": b"# PUBLIC_RC_EXCLUDE: private\nVALUE = 1\n",
        },
    )

    report = build_report(
        source_root=None,
        wheel=wheel,
        required_packages=["ilc_core.capproof"],
    )

    surface = report["surfaces"][0]
    assert report["verdict"] == "fail_closed"
    assert surface["marker_paths"] == ["ilc_core/internal.py"]
    assert surface["required_packages"] == [
        {"package": "ilc_core.capproof", "present": False}
    ]


def test_wheel_rejects_record_digest_mismatch(tmp_path: Path) -> None:
    wheel = tmp_path / "ilc_core-0.0.0-py3-none-any.whl"
    _wheel(wheel, {"ilc_core/__init__.py": b""})
    rewritten = tmp_path / "rewritten.whl"
    with ZipFile(wheel) as source, ZipFile(rewritten, "w", compression=ZIP_DEFLATED) as target:
        for info in source.infolist():
            payload = source.read(info)
            if info.filename == "ilc_core/__init__.py":
                payload = b"changed"
            target.writestr(info.filename, payload)
    rewritten.replace(wheel)

    with pytest.raises(BoundaryError, match="wheel_record_digest_mismatch"):
        build_report(source_root=None, wheel=wheel, required_packages=[])


def test_wheel_accepts_complete_boundary(tmp_path: Path) -> None:
    wheel = tmp_path / "ilc_core-0.0.0-py3-none-any.whl"
    _wheel(
        wheel,
        {
            "ilc_core/__init__.py": b"",
            "ilc_core/capproof/__init__.py": b"from .worker import VALUE\n",
            "ilc_core/capproof/worker.py": b"VALUE = 1\n",
        },
    )

    report = build_report(
        source_root=None,
        wheel=wheel,
        required_packages=["ilc_core.capproof"],
    )

    assert report["verdict"] == "pass"
    assert report["surfaces"][0]["record_verification"]["checked_member_count"] == 3
