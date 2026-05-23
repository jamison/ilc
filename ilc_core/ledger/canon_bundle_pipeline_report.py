# SPDX-License-Identifier: AGPL-3.0-or-later
import json
from datetime import datetime, timezone
from typing import TypedDict


class PipelineSteps(TypedDict, total=False):
    validate: bool
    sign: bool
    verify: bool
    report: bool


class PipelineReport(TypedDict, total=False):
    ok: bool
    errors: list[str]
    warnings: list[str]
    steps: PipelineSteps


class SignatureMetadata(TypedDict, total=False):
    key_id: str
    sig_alg: str
    signed_at: str
    key_status: str

def render_pipeline_report(
    bundle_path: str, 
    report: PipelineReport, 
    timestamp: str | None = None,
    json_output: str | None = None,
    key_metadata: SignatureMetadata | None = None,
) -> str:
    """
    Render a Markdown report for the canon bundle pipeline.
    
    Args:
        bundle_path: Path to the bundle being processed.
        report: The pipeline result dictionary (ok, errors, warnings, steps).
        timestamp: Optional override for generation timestamp (ISO format).
        key_metadata: Optional dict with key_id, sig_alg, signed_at.
        
    Returns:
        A string containing the Markdown report.
    """
    ts = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    status = "OK" if report.get("ok", False) else "FAIL"
    
    # Build steps table
    steps = report.get("steps", {})
    step_rows = []
    for step_name in ["validate", "sign", "verify", "report"]:
        step_status = steps.get(step_name, False)
        step_rows.append(f"| {step_name} | {step_status} |")
    
    # Errors and warnings
    errors = report.get("errors", [])
    warnings = report.get("warnings", [])
    
    # JSON output (single-line, verbatim)
    json_output = json_output or json.dumps(
        report,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )
    
    lines = [
        "# Canon Bundle Pipeline Report",
        "",
        f"Bundle: `{bundle_path}`",
        f"Status: **{status}**",
        f"Timestamp: `{ts}`",
        "Report Version: v0.1",
        "",
        "## Summary",
        f"- ok: {report.get('ok', False)}",
        f"- errors: {errors}",
        f"- warnings: {warnings}",
        "",
        "## Steps",
        "| step | status |",
        "|---|---|",
    ]
    lines.extend(step_rows)
    
    # Add signature metadata section if present
    if key_metadata:
        lines.extend([
            "",
            "## Signature Metadata",
            f"- key_id: {key_metadata.get('key_id', 'N/A')}",
            f"- sig_alg: {key_metadata.get('sig_alg', 'N/A')}",
            f"- signed_at: {key_metadata.get('signed_at', 'N/A')}",
            f"- key_status: {key_metadata.get('key_status', 'N/A')}",
        ])
    
    lines.extend([
        "",
        "## JSON Output",
        "```json",
        json_output,
        "```",
        "",
    ])
    
    return "\n".join(lines)
