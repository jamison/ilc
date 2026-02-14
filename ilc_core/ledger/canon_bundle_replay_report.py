import json
from datetime import datetime, timezone
from typing import TypeAlias, TypedDict

REPORT_VERSION = "canon_bundle_replay_report_v0.1"


class ReplayMismatchEntry(TypedDict, total=False):
    expected: object
    actual: object


ReplayMismatchMap: TypeAlias = dict[str, ReplayMismatchEntry]


class ReplayJsonPayload(TypedDict, total=False):
    ok: bool
    pipeline_ok: bool
    replay_matches: bool


def severity_for_field(field: str) -> str:
    """Determine severity based on field name."""
    if field in ("manifest_hash", "signature_hash", "pipeline_ok"):
        return "high"
    elif field.startswith("steps."):
        return "medium"
    else:
        return "low"

def render_replay_report(
    *,
    bundle_path: str,
    audit_path: str,
    export_root: str | None,
    replay_json: ReplayJsonPayload,
    mismatches: ReplayMismatchMap,
    warnings: list[str],
    errors: list[str],
    created_at: str | None = None,
) -> str:
    """
    Render a Markdown report for canon bundle replay verification.
    
    Args:
        bundle_path: Path to the bundle directory.
        audit_path: Path to the audit JSON file.
        export_root: Optional export root path.
        replay_json: The replay verification result dictionary.
        mismatches: Dict of field mismatches with expected/actual values.
        warnings: List of warning strings.
        errors: List of error strings.
        created_at: Optional override for generation timestamp (RFC3339 UTC).
        
    Returns:
        A Markdown report string.
    """
    ts = created_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    pipeline_ok = replay_json.get("pipeline_ok", replay_json.get("ok", False))
    replay_matches = replay_json.get("replay_matches", False)
    mismatch_count = len(mismatches)
    warning_count = len(warnings)
    error_count = len(errors)
    
    # Build mismatch list with severity
    mismatch_list = []
    for field, values in mismatches.items():
        mismatch_list.append({
            "field": field,
            "expected": values.get("expected"),
            "actual": values.get("actual"),
            "severity": severity_for_field(field)
        })
    
    # JSON output (single-line, verbatim)
    json_output = json.dumps(replay_json, separators=(",", ":"), sort_keys=False)
    
    lines = [
        f"# Canon Bundle Replay Report ({REPORT_VERSION})",
        f"created_at: {ts}",
        "",
        f"bundle_path: `{bundle_path}`",
        f"audit_path: `{audit_path}`",
        f"export_root: `{export_root or 'N/A'}`",
        f"pipeline_ok: {pipeline_ok}",
        f"replay_matches: {replay_matches}",
        f"mismatch_count: {mismatch_count}",
        f"warning_count: {warning_count}",
        f"error_count: {error_count}",
        "",
        "## Summary",
        f"- pipeline_ok: {pipeline_ok}",
        f"- replay_matches: {replay_matches}",
        f"- errors: {errors}",
        f"- warnings: {warnings}",
        "",
    ]
    
    # Mismatches table
    lines.append("## Mismatches")
    if mismatch_list:
        lines.append("| field | expected | actual | severity |")
        lines.append("|---|---|---|---|")
        for m in mismatch_list:
            lines.append(f"| {m['field']} | {m['expected']} | {m['actual']} | {m['severity']} |")
    else:
        lines.append("No mismatches detected.")
    lines.append("")
    
    # Errors
    lines.append("## Errors")
    if errors:
        for e in errors:
            lines.append(f"- {e}")
    else:
        lines.append("None.")
    lines.append("")
    
    # Warnings
    lines.append("## Warnings")
    if warnings:
        for w in warnings:
            lines.append(f"- {w}")
    else:
        lines.append("None.")
    lines.append("")
    
    # Replay JSON
    lines.append("## Replay JSON (verbatim)")
    lines.append("```json")
    lines.append(json_output)
    lines.append("```")
    lines.append("")
    
    # Known Limitations
    lines.append("## Known Limitations")
    lines.append("- Replay does not re-sign the bundle; signature verification is hash-based only.")
    lines.append("- Bundle path mismatch yields a warning but does not cause failure.")
    lines.append("- Report does not include raw keys or signature contents for security.")
    lines.append("")
    
    return "\n".join(lines)
