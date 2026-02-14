from datetime import datetime, timezone
from typing import TypedDict


class BundleReportResult(TypedDict, total=False):
    ok: bool
    errors: list[str]
    warnings: list[str]


def render_bundle_report(
    bundle_path: str, report: BundleReportResult, timestamp: str | None = None
) -> str:
    """
    Render a Markdown validation report for a canon export bundle.
    
    Args:
        bundle_path: Path to the bundle being reported on.
        report: The validation report dictionary (ok, errors, warnings).
        timestamp: Optional override for generation timestamp (ISO format).
        
    Returns:
        A string containing the Markdown report.
    """
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    status = "OK" if report["ok"] else "FAIL"
    
    # Deterministic sorting
    errors = sorted(report.get("errors", []))
    warnings = sorted(report.get("warnings", []))
    
    lines = [
        "# Canon Bundle Validation Report",
        "",
        f"Bundle: `{bundle_path}`",
        f"Status: **{status}**",
        f"Timestamp: `{ts}`",
        "Report Version: v0.1",
        "",
        "## Errors",
    ]
    
    if errors:
        for err in errors:
            lines.append(f"- {err}")
    else:
        lines.append("- None")
        
    lines.extend([
        "",
        "## Warnings",
    ])
    
    if warnings:
        for warn in warnings:
            lines.append(f"- {warn}")
    else:
        lines.append("- None")
        
    lines.append("") # Trailing newline
    
    return "\n".join(lines)
