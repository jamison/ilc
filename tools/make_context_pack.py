#!/usr/bin/env python3
"""
Context Pack Generator

Generates a Phase Delta Pack from the most recent walkthrough file or git history.

Usage:
    python3 tools/make_context_pack.py --phase 65D
    python3 tools/make_context_pack.py --phase 65D --walkthrough docs/phases/phase_65c_walkthrough.md

Output:
    docs/context_packs/phase_65d_delta_pack.md
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def parse_walkthrough(walkthrough_path: Path) -> dict:
    """Extract structured information from a walkthrough file."""
    info = {
        "summary": "",
        "objective": [],
        "files_changed": [],
        "next_steps": [],
    }
    
    if not walkthrough_path.exists():
        return info
    
    content = walkthrough_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    
    current_section = None
    in_files_table = False
    
    for line in lines:
        # Detect section headers
        if line.startswith("## Summary"):
            current_section = "summary"
            continue
        elif line.startswith("## Objective"):
            current_section = "objective"
            continue
        elif line.startswith("## Files Changed"):
            current_section = "files_changed"
            in_files_table = False
            continue
        elif line.startswith("## Next Steps"):
            current_section = "next_steps"
            continue
        elif line.startswith("## "):
            current_section = None
            in_files_table = False
            continue
        
        # Extract content based on section
        if current_section == "summary":
            if line.strip() and not line.startswith("---"):
                info["summary"] += line.strip() + " "
        
        elif current_section == "objective":
            match = re.match(r"^\d+\.\s+(.+)$", line.strip())
            if match:
                info["objective"].append(match.group(1))
        
        elif current_section == "files_changed":
            # Skip table header and separator
            if "|" in line and "File" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2:
                    file_path = parts[0].strip("`")
                    info["files_changed"].append(file_path)
        
        elif current_section == "next_steps":
            match = re.match(r"^\d+\.\s+(.+)$", line.strip())
            if match:
                info["next_steps"].append(match.group(1))
    
    info["summary"] = info["summary"].strip()
    return info


def get_recent_git_changes(limit: int = 10) -> list:
    """Get list of recently changed files from git (if available)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
            return files[:limit]
    except Exception:
        pass
    return []


def find_latest_walkthrough(phases_dir: Path) -> Path:
    """Find the most recently modified walkthrough file."""
    walkthroughs = list(phases_dir.glob("phase_*_walkthrough.md"))
    if not walkthroughs:
        return None
    
    # Sort by modification time, most recent first
    walkthroughs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return walkthroughs[0]


def generate_delta_pack(
    phase_id: str,
    objective: str,
    non_goals: str,
    walkthrough_path: Path,
    output_dir: Path,
) -> Path:
    """Generate a delta pack markdown file."""
    
    info = parse_walkthrough(walkthrough_path) if walkthrough_path else {}
    git_files = get_recent_git_changes()
    
    # Determine files changed (prefer walkthrough, fall back to git)
    files_changed = info.get("files_changed", []) or git_files
    
    # Generate markdown content
    phase_lower = phase_id.lower().replace(" ", "_")
    output_path = output_dir / f"phase_{phase_lower}_delta_pack.md"
    
    content = f"""# Phase {phase_id} Delta Pack

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Previous Walkthrough:** {walkthrough_path.name if walkthrough_path else "N/A"}

---

## Current Phase Objective

{objective if objective else "See walkthrough for details."}

---

## Non-Goals

{non_goals if non_goals else "No specific non-goals documented."}

---

## Files Changed in Previous Phase

"""
    
    if files_changed:
        for f in files_changed:
            content += f"- `{f}`\n"
    else:
        content += "No file changes detected.\n"
    
    content += """
---

## What to Read First

1. `docs/context_packs/context_anchor_pack.md` - Project fundamentals
2. `docs/phases/README.md` - Walkthrough format guidelines
"""
    
    if walkthrough_path and walkthrough_path.exists():
        content += f"3. `{walkthrough_path}` - Previous phase details\n"
    
    content += """
---

## Next Tasks

"""
    
    next_steps = info.get("next_steps", [])
    if next_steps:
        for step in next_steps:
            content += f"- {step}\n"
    else:
        content += "- Check walkthrough for next steps\n- Run `python3 -m pytest -q` to verify repo state\n"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate a Context Delta Pack")
    parser.add_argument(
        "--phase",
        required=True,
        help="Phase identifier (e.g., 65D)",
    )
    parser.add_argument(
        "--walkthrough",
        type=Path,
        default=None,
        help="Path to the previous phase walkthrough (auto-detected if not provided)",
    )
    parser.add_argument(
        "--objective",
        type=str,
        default="",
        help="Current phase objective (optional)",
    )
    parser.add_argument(
        "--non-goals",
        type=str,
        default="",
        help="Current phase non-goals (optional)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/context_packs"),
        help="Output directory for the delta pack",
    )
    
    args = parser.parse_args()
    
    # Auto-detect walkthrough if not provided
    walkthrough_path = args.walkthrough
    if walkthrough_path is None:
        phases_dir = Path("docs/phases")
        if phases_dir.exists():
            walkthrough_path = find_latest_walkthrough(phases_dir)
            if walkthrough_path:
                print(f"Auto-detected walkthrough: {walkthrough_path}")
    
    output_path = generate_delta_pack(
        phase_id=args.phase,
        objective=args.objective,
        non_goals=args.non_goals,
        walkthrough_path=walkthrough_path,
        output_dir=args.output_dir,
    )
    
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
