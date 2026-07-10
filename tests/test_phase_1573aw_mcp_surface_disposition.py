# SPDX-License-Identifier: AGPL-3.0-only

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN_CLI = ROOT / "ilc_core/cli/main.py"
MIRROR_SCRIPT = ROOT / "tools/scripts/generate_public_mirror.sh"
SPEC = ROOT / "docs/specs/ilc_mcp_public_rc_surface_disposition_1573aw_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"

MCP_PYTHON_FILES = (
    ROOT / "ilc_core/mcp/__init__.py",
    ROOT / "ilc_core/mcp/service.py",
    ROOT / "ilc_core/mcp/node_service.py",
    ROOT / "ilc_core/mcp/schema.py",
    ROOT / "ilc_core/mcp/schemas/__init__.py",
    ROOT / "ilc_core/cli/mcp_cli.py",
)

MCP_SCHEMA_JSON_FILES = (
    ROOT / "ilc_core/mcp/schemas/ilc_mcp_tools_mvp_schema_v0.1.json",
    ROOT / "ilc_core/mcp/schemas/mcp_tool_call_event_schema_v0.1.json",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_mcp_not_in_main_cli_dispatcher() -> None:
    source = _read(MAIN_CLI).lower()

    assert "mcp" not in source
    assert "mcptool" not in source
    assert "mcp_cli" not in source


def test_mcp_modules_carry_public_rc_exclude_header() -> None:
    for path in MCP_PYTHON_FILES:
        header = "\n".join(_read(path).splitlines()[:10])
        assert "PUBLIC_RC_EXCLUDE: mcp_runtime" in header, path
        assert "dormant reference implementation" in header, path


def test_public_mirror_excludes_mcp_runtime_subtree() -> None:
    source = _read(MIRROR_SCRIPT)

    assert '"ilc_core/mcp/"' in source
    assert '"ilc_core/cli/mcp_cli.py"' in source


def test_mcp_schema_json_files_are_excluded_by_policy_not_headers() -> None:
    script = _read(MIRROR_SCRIPT)
    assert '"ilc_core/mcp/"' in script

    for path in MCP_SCHEMA_JSON_FILES:
        source = _read(path)
        assert "PUBLIC_RC_EXCLUDE" not in source, path


def test_mcp_disposition_spec_exists_and_carries_exclude() -> None:
    source = _read(SPEC)

    assert "PUBLIC_RC_EXCLUDE: mcp_disposition_spec" in source
    assert "ilc_core/mcp/" in source
    assert "ilc_core/cli/mcp_cli.py" in source


def test_mcp_disposition_spec_records_dormant_status() -> None:
    source = _read(SPEC)

    assert "dormant reference implementation" in source
    assert "not an active public-RC product surface" in source
    assert "not deleted or permanently abandoned" in source


def test_phase_status_tokens_present() -> None:
    source = _read(STATUS)

    assert "mcp_public_rc_surface_disposition_complete_phase_1573aw" in source
    assert "mcp_excluded_from_public_rc_distribution_phase_1573aw" in source
    assert "public_path_remains_blocked_phase_1573aw" in source
