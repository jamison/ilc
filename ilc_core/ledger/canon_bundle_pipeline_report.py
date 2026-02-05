
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

def render_pipeline_report(
    bundle_path: str, 
    report: Dict[str, Any], 
    timestamp: Optional[str] = None,
    json_output: Optional[str] = None,
) -> str:
    """
    Render a Markdown report for the canon bundle pipeline.
    
    Args:
        bundle_path: Path to the bundle being processed.
        report: The pipeline result dictionary (ok, errors, warnings, steps).
        timestamp: Optional override for generation timestamp (ISO format).
        
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
    json_output = json_output or json.dumps(report, separators=(",", ":"), sort_keys=False)
    
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
    lines.extend([
        "",
        "## JSON Output",
        "```json",
        json_output,
        "```",
        "",
    ])
    
    return "\n".join(lines)
