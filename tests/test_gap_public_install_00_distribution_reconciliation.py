# SPDX-License-Identifier: AGPL-3.0-only
"""GAP-PUBLIC-INSTALL-00 release distribution reconciliation tests."""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
RECONCILIATION_DOC = (
    ROOT
    / "docs"
    / "specs"
    / "ilc_public_install_distribution_reconciliation_GAP_PUBLIC_INSTALL_00_v0.1.md"
)
SCHEMA_1213 = ROOT / "docs" / "specs" / "ilc_release_artifact_manifest_schema_1213_v0.1.md"


def _pyproject() -> dict[str, object]:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def test_pyproject_version_is_0_2_0() -> None:
    assert _pyproject()["project"]["version"] == "0.2.0"


def test_pyproject_name_is_ilc_core() -> None:
    assert _pyproject()["project"]["name"] == "ilc-core"


def test_ilc_core_version_constant_matches_pyproject() -> None:
    init_path = ROOT / "ilc_core" / "__init__.py"
    if not init_path.exists():
        assert "no_version_constant"
        return
    content = init_path.read_text(encoding="utf-8")
    if "__version__" not in content:
        assert "no_version_constant"
        return
    namespace: dict[str, object] = {}
    exec(compile(content, str(init_path), "exec"), namespace)
    assert namespace.get("__version__") == "0.2.0"


def test_install_from_invite_rejects_http_url() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ilc_core.cli.main",
            "install",
            "--from-invite",
            "http://example.com/invite.json",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode != 0
    assert "install_invite_url_fetch_not_supported" in result.stderr


def test_install_from_invite_rejects_https_url() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ilc_core.cli.main",
            "install",
            "--from-invite",
            "https://example.com/invite.json",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode != 0
    assert "install_invite_url_fetch_not_supported" in result.stderr


def test_reconciliation_doc_exists_and_has_required_sections() -> None:
    content = RECONCILIATION_DOC.read_text(encoding="utf-8")
    required = [
        "## 1. Distribution Inventory",
        "## 2. Package Name Fact",
        "## 3. Version State",
        "## 4. Two-Layer Separation",
        "## 5. Platform Priority",
        "## 6. Release Manifest Gap Inventory",
        "## 7. Existing Release Manifest Lineage Summary",
        "## 9. Non-Claims",
    ]

    for heading in required:
        assert heading in content


def test_reconciliation_doc_records_two_install_layers_and_boundaries() -> None:
    content = RECONCILIATION_DOC.read_text(encoding="utf-8")

    assert "Software delivery" in content
    assert "Graph onboarding" in content
    assert "`install.sh` is not `ilc install`" in content
    assert "ilc install --from-invite` is not a software" in content


def test_release_manifest_gap_inventory_records_missing_installable_fields() -> None:
    content = RECONCILIATION_DOC.read_text(encoding="utf-8")
    for missing in (
        "`platform`",
        "`arch`",
        "`channel`",
        "`size_bytes`",
        "`download_url`",
        "`min_python_version`",
        "`python_wheel` | No",
        "`install_script` | No",
    ):
        assert missing in content


def test_1213_schema_lacks_installable_artifact_types() -> None:
    schema = SCHEMA_1213.read_text(encoding="utf-8")

    assert "source_release_tarball" in schema
    assert "cli_binary" in schema
    assert "python_wheel" not in schema
    assert "install_script" not in schema


def test_phase_00_recorded_root_public_install_script_absent_then() -> None:
    content = RECONCILIATION_DOC.read_text(encoding="utf-8")
    assert "Root ILC `install.sh` software-delivery script | Not present" in content
    assert not (ROOT / "ilc_core" / "cli" / "install.sh").exists()
    assert (ROOT / "ilc-graphics-sidecar" / "install.sh").exists()


def test_console_script_inventory_matches_phase_1575o_fix1_count() -> None:
    scripts = _pyproject()["project"]["scripts"]
    assert sorted(scripts) == [
        "ilc",
        "ilc-canon-bundle-pipeline",
        "ilc-canon-bundle-replay",
        "ilc-canon-bundle-sign",
        "ilc-canon-bundle-validate",
        "ilc-canon-cluster-a-replay-proof",
        "ilc-canon-export",
        "ilc-canon-summary",
        "ilc-canon-verify",
    ]
