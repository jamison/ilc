"""Deterministic package-profile CI gate for Gap 14 work.

The gate measures selected OpenClaw/NemoClaw package profiles and reuses the
existing import-boundary inventory where a surface has an import contract. It is
not a package publisher and does not activate public claimability or public P2P.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from ilc_core.rc.package_boundary_inventory import (
    DEFAULT_IMPORT_BOUNDARY_SPECS,
    IMPORT_BOUNDARY_INVENTORY_VERSION,
    build_import_boundary_inventory,
)
from ilc_core.rc.package_profiles import (
    NON_EXCISABLE_COMPONENTS,
    PROFILE_OPENCLAW_SKILL_CLAIMABLE,
    PROFILE_OPENCLAW_SKILL_LOCAL,
    PROFILE_PACKAGE_SURFACES,
    PUBLIC_RC_PACKAGE_PROFILES_VERSION,
    get_package_profile,
    profile_manifest,
    validate_package_profile,
)

GAP14_PACKAGE_CI_GATE_VERSION = "gap14_package_ci_gate_phase_1251.v0.1"
PUBLIC_PACKAGE_SIZE_AUDIT_TOKEN = "public_package_size_audit_recorded_phase_1251"
PHASE_1251_GAP14_PACKAGE_CI_PROFILE_AUDIT_COMPLETE_TOKEN = (
    "phase_1251_gap14_package_ci_profile_audit_complete"
)

SELECTED_GAP14_PROFILE_IDS = (
    PROFILE_OPENCLAW_SKILL_LOCAL,
    PROFILE_OPENCLAW_SKILL_CLAIMABLE,
)

MAX_PACKAGE_PROFILE_AUDIT_FILES = 5_000
MAX_PACKAGE_PROFILE_AUDIT_FILE_BYTES = 3_000_000
PACKAGE_PROFILE_AUDIT_FILE_SUFFIXES = (".json", ".py")

PHASE_1250_FIX1_CONSUMED_FINDINGS = ("RCGAP-1250-FIX1-001",)
PHASE_1250_FIX1_CARRY_FORWARD_ROUTES = {
    "phase_1252": {
        "finding_ids": (
            "RCGAP-1250-FIX1-003",
            "RCGAP-1250-FIX1-006",
        ),
        "status": "carried_forward",
        "token": "phase_1252_digest_truncation_security_binding_classification_recorded",
    },
    "phase_1253": {
        "finding_ids": (
            "RCGAP-1250-FIX1-004",
            "RCGAP-1250-FIX1-005",
        ),
        "status": "carried_forward",
        "token": "phase_1253_transport_digest_and_rust_m5_disposition_recorded",
    },
    "phase_1254": {
        "finding_ids": ("RCGAP-1250-FIX1-002",),
        "status": "carried_forward",
        "token": "phase_1254_legacy_graph_delta_gap_disposition_recorded",
    },
}

_REPO_ROOT = Path(__file__).resolve().parents[2]

PACKAGE_SURFACE_ROOTS = {
    "ilc_logic": DEFAULT_IMPORT_BOUNDARY_SPECS["ilc_logic"].root_paths,
    "ilc_cli": DEFAULT_IMPORT_BOUNDARY_SPECS["ilc_cli"].root_paths,
    "ilc_harness_adapters": DEFAULT_IMPORT_BOUNDARY_SPECS[
        "ilc_harness_adapters"
    ].root_paths,
    "local_sidecar": (
        "ilc_core/graph/agent_graph_projection_runtime.py",
        "ilc_core/graph/sidecar_query_runtime.py",
        "ilc_core/sidecars",
    ),
    "public_claimability": (
        "ilc_core/ledger/ecu_active_layer_runtime.py",
        "ilc_core/ledger/ecu_ilc_lifecycle_runtime.py",
        "ilc_core/ledger/exact_numeric.py",
        "ilc_core/protocol/public_init_admission_runtime.py",
        "ilc_core/protocol/public_receipt_runtime.py",
        "ilc_core/protocol/public_wallet_runtime.py",
    ),
}

_BOUNDARY_SURFACES = frozenset(DEFAULT_IMPORT_BOUNDARY_SPECS)


def _repo_relative_path(path: Path) -> str:
    return path.relative_to(_REPO_ROOT).as_posix()


def _validate_surface_root(root_path: str) -> None:
    if not isinstance(root_path, str) or not root_path:
        raise ValueError("package_profile_ci_gate_invalid_surface_root")
    if "\x00" in root_path or "\n" in root_path or "\r" in root_path:
        raise ValueError("package_profile_ci_gate_invalid_surface_root")
    root = Path(root_path)
    if root.is_absolute() or ".." in root.parts:
        raise ValueError("package_profile_ci_gate_root_must_be_repo_relative")


def _iter_surface_files(surface_id: str) -> tuple[Path, ...]:
    try:
        root_paths = PACKAGE_SURFACE_ROOTS[surface_id]
    except KeyError as exc:
        raise ValueError("package_profile_ci_gate_unknown_surface") from exc

    files: list[Path] = []
    for root_path in root_paths:
        _validate_surface_root(root_path)
        root = _REPO_ROOT / root_path
        if not root.exists():
            raise ValueError("package_profile_ci_gate_surface_root_missing")
        if root.is_symlink():
            raise ValueError("package_profile_ci_gate_symlink_forbidden")
        if root.is_file():
            if root.suffix in PACKAGE_PROFILE_AUDIT_FILE_SUFFIXES:
                files.append(root)
            continue
        if root.is_dir():
            for suffix in PACKAGE_PROFILE_AUDIT_FILE_SUFFIXES:
                for path in root.rglob(f"*{suffix}"):
                    if "__pycache__" in path.parts:
                        continue
                    if path.is_symlink():
                        raise ValueError("package_profile_ci_gate_symlink_forbidden")
                    files.append(path)

    unique = tuple(sorted(set(files), key=lambda path: path.as_posix()))
    if not unique:
        raise ValueError("package_profile_ci_gate_surface_empty")
    if len(unique) > MAX_PACKAGE_PROFILE_AUDIT_FILES:
        raise ValueError("package_profile_ci_gate_file_limit_exceeded")
    return unique


def _measure_file(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise ValueError("package_profile_ci_gate_symlink_forbidden")
    file_size = path.stat().st_size
    if file_size > MAX_PACKAGE_PROFILE_AUDIT_FILE_BYTES:
        raise ValueError("package_profile_ci_gate_file_bytes_limit_exceeded")
    payload = path.read_bytes()
    if len(payload) > MAX_PACKAGE_PROFILE_AUDIT_FILE_BYTES:
        raise ValueError("package_profile_ci_gate_file_bytes_limit_exceeded")
    return {
        "bytes": len(payload),
        "lines": payload.count(b"\n") + (1 if payload and not payload.endswith(b"\n") else 0),
        "path": _repo_relative_path(path),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _summarize_file_records(file_records: tuple[dict[str, Any], ...]) -> dict[str, Any]:
    return {
        "file_count": len(file_records),
        "max_file_bytes": MAX_PACKAGE_PROFILE_AUDIT_FILE_BYTES,
        "max_files": MAX_PACKAGE_PROFILE_AUDIT_FILES,
        "total_bytes": sum(record["bytes"] for record in file_records),
        "total_lines": sum(record["lines"] for record in file_records),
    }


def _surface_measurement(surface_id: str) -> dict[str, Any]:
    files = tuple(_measure_file(path) for path in _iter_surface_files(surface_id))
    measurement = {
        "files": list(files),
        "measurement_status": "pass",
        "root_paths": list(PACKAGE_SURFACE_ROOTS[surface_id]),
        "surface_id": surface_id,
        **_summarize_file_records(files),
    }
    if surface_id in _BOUNDARY_SURFACES:
        inventory = build_import_boundary_inventory(DEFAULT_IMPORT_BOUNDARY_SPECS[surface_id])
        measurement["boundary_contract"] = {
            "import_boundary_version": IMPORT_BOUNDARY_INVENTORY_VERSION,
            "status": inventory["status"],
            "violation_count": len(inventory["violations"]),
        }
    else:
        measurement["boundary_contract"] = {
            "import_boundary_version": IMPORT_BOUNDARY_INVENTORY_VERSION,
            "status": "measurement_only",
            "violation_count": 0,
        }
    return measurement


def _profile_surface_ids(profile_id: str) -> tuple[str, ...]:
    try:
        surface_ids = PROFILE_PACKAGE_SURFACES[profile_id]
    except KeyError as exc:
        raise ValueError("package_profile_ci_gate_profile_missing_surfaces") from exc
    for surface_id in surface_ids:
        if surface_id not in PACKAGE_SURFACE_ROOTS:
            raise ValueError("package_profile_ci_gate_unknown_surface")
    return surface_ids


def _profile_gate_record(profile_id: str) -> dict[str, Any]:
    profile = get_package_profile(profile_id)
    validate_package_profile(profile)
    manifest = profile_manifest(profile)
    missing_non_excisable = sorted(NON_EXCISABLE_COMPONENTS - profile.components)
    surface_ids = _profile_surface_ids(profile_id)
    surface_measurements = {
        surface_id: _surface_measurement(surface_id) for surface_id in surface_ids
    }

    unique_files = {
        file_record["path"]: file_record
        for measurement in surface_measurements.values()
        for file_record in measurement["files"]
    }
    unique_file_records = tuple(
        unique_files[path] for path in sorted(unique_files)
    )
    failing_surfaces = [
        surface_id
        for surface_id, measurement in surface_measurements.items()
        if measurement["boundary_contract"]["status"] not in {"pass", "measurement_only"}
    ]
    status = "pass"
    if missing_non_excisable or failing_surfaces:
        status = "fail"

    return {
        "boundary_gate_failing_surfaces": sorted(failing_surfaces),
        "claim_status": {
            "package_publication": False,
            "public_claimability_declared": profile.public_claimability,
            "public_claimability_runtime_activated": False,
            "public_p2p_declared": profile.public_p2p,
            "public_rc_claimed": False,
            "public_repository_publication": False,
        },
        "manifest": manifest,
        "missing_non_excisable_components": missing_non_excisable,
        "profile_id": profile_id,
        "profile_status": status,
        "profile_unique_measurement": _summarize_file_records(unique_file_records),
        "surface_measurements": surface_measurements,
    }


def build_package_profile_ci_audit(
    profile_ids: tuple[str, ...] = SELECTED_GAP14_PROFILE_IDS,
) -> dict[str, Any]:
    if type(profile_ids) is not tuple or not profile_ids:
        raise ValueError("package_profile_ci_gate_invalid_profile_ids")
    profile_records = {
        profile_id: _profile_gate_record(profile_id) for profile_id in profile_ids
    }
    failing_profiles = [
        profile_id
        for profile_id, record in profile_records.items()
        if record["profile_status"] != "pass"
    ]
    return {
        "audit_status": "pass" if not failing_profiles else "fail",
        "failing_profiles": sorted(failing_profiles),
        "fix1_finding_scope": {
            "consumed_findings": list(PHASE_1250_FIX1_CONSUMED_FINDINGS),
            "non_package_findings_remain_routed": {
                phase: {
                    "finding_ids": list(route["finding_ids"]),
                    "status": route["status"],
                    "token": route["token"],
                }
                for phase, route in sorted(PHASE_1250_FIX1_CARRY_FORWARD_ROUTES.items())
            },
        },
        "profiles": profile_records,
        "public_package_size_audit_token": PUBLIC_PACKAGE_SIZE_AUDIT_TOKEN,
        "required_tokens": [
            GAP14_PACKAGE_CI_GATE_VERSION,
            PUBLIC_PACKAGE_SIZE_AUDIT_TOKEN,
            PHASE_1251_GAP14_PACKAGE_CI_PROFILE_AUDIT_COMPLETE_TOKEN,
        ],
        "selected_profile_ids": list(profile_ids),
        "version": GAP14_PACKAGE_CI_GATE_VERSION,
    }


def validate_package_profile_ci_audit(audit: dict[str, Any] | None = None) -> dict[str, Any]:
    active = build_package_profile_ci_audit() if audit is None else audit
    if active["audit_status"] != "pass":
        raise ValueError("package_profile_ci_gate_failed")
    return active


def export_package_profile_ci_audit_json(audit: dict[str, Any] | None = None) -> str:
    active = build_package_profile_ci_audit() if audit is None else audit
    return json.dumps(
        active,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def render_package_profile_ci_audit_markdown(audit: dict[str, Any] | None = None) -> str:
    active = build_package_profile_ci_audit() if audit is None else audit
    lines = [
        "# ILC Gap 14 Package Profile CI Audit 1251 v0.1",
        "",
        f"- Version: `{active['version']}`",
        f"- Status: `{active['audit_status']}`",
        f"- Package size token: `{active['public_package_size_audit_token']}`",
        f"- Profile contract version: `{PUBLIC_RC_PACKAGE_PROFILES_VERSION}`",
        "",
        "## Required Tokens",
        "",
    ]
    for token in active["required_tokens"]:
        lines.append(f"- `{token}`")

    lines.extend(
        [
            "",
            "## Selected Profiles",
            "",
            "| Profile | Status | Files | Bytes | Lines | Public P2P | Public claimability | Public RC claimed |",
            "| --- | --- | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )
    for profile_id in active["selected_profile_ids"]:
        record = active["profiles"][profile_id]
        measurement = record["profile_unique_measurement"]
        claim_status = record["claim_status"]
        lines.append(
            "| "
            f"`{profile_id}` | `{record['profile_status']}` | "
            f"{measurement['file_count']} | {measurement['total_bytes']} | "
            f"{measurement['total_lines']} | "
            f"`{claim_status['public_p2p_declared']}` | "
            f"`{claim_status['public_claimability_declared']}` | "
            f"`{claim_status['public_rc_claimed']}` |"
        )

    lines.extend(
        [
            "",
            "## Surface Measurements",
            "",
            "| Profile | Surface | Boundary status | Files | Bytes | Lines |",
            "| --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for profile_id in active["selected_profile_ids"]:
        surfaces = active["profiles"][profile_id]["surface_measurements"]
        for surface_id in sorted(surfaces):
            surface = surfaces[surface_id]
            lines.append(
                "| "
                f"`{profile_id}` | `{surface_id}` | "
                f"`{surface['boundary_contract']['status']}` | "
                f"{surface['file_count']} | {surface['total_bytes']} | "
                f"{surface['total_lines']} |"
            )

    lines.extend(
        [
            "",
            "## Phase 1250 Fix1 Scope Preservation",
            "",
            "Phase 1251 consumes only `RCGAP-1250-FIX1-001` as package-focus confirmation.",
            "The non-package findings remain routed as follows:",
            "",
        ]
    )
    routes = active["fix1_finding_scope"]["non_package_findings_remain_routed"]
    for phase, route in sorted(routes.items()):
        finding_ids = ", ".join(f"`{finding_id}`" for finding_id in route["finding_ids"])
        lines.append(
            f"- `{phase}`: {finding_ids}; status `{route['status']}`; token `{route['token']}`"
        )

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- No package publication was performed.",
            "- No public repository publication was performed.",
            "- No public RC claim was made.",
            "- No public claimability runtime was activated.",
            "- No public P2P exposure was introduced.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--markdown-out", type=Path)
    args = parser.parse_args(argv)

    audit = validate_package_profile_ci_audit()
    if args.json_out is not None:
        _write_text(args.json_out, export_package_profile_ci_audit_json(audit) + "\n")
    if args.markdown_out is not None:
        _write_text(args.markdown_out, render_package_profile_ci_audit_markdown(audit) + "\n")
    if args.json_out is None and args.markdown_out is None:
        print(export_package_profile_ci_audit_json(audit))
    return 0


__all__ = [
    "GAP14_PACKAGE_CI_GATE_VERSION",
    "MAX_PACKAGE_PROFILE_AUDIT_FILE_BYTES",
    "MAX_PACKAGE_PROFILE_AUDIT_FILES",
    "PACKAGE_PROFILE_AUDIT_FILE_SUFFIXES",
    "PACKAGE_SURFACE_ROOTS",
    "PHASE_1250_FIX1_CARRY_FORWARD_ROUTES",
    "PHASE_1250_FIX1_CONSUMED_FINDINGS",
    "PHASE_1251_GAP14_PACKAGE_CI_PROFILE_AUDIT_COMPLETE_TOKEN",
    "PUBLIC_PACKAGE_SIZE_AUDIT_TOKEN",
    "SELECTED_GAP14_PROFILE_IDS",
    "build_package_profile_ci_audit",
    "export_package_profile_ci_audit_json",
    "render_package_profile_ci_audit_markdown",
    "validate_package_profile_ci_audit",
]


if __name__ == "__main__":
    raise SystemExit(main())
