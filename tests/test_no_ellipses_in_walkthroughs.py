"""
Test that walkthrough files do not contain ellipsis characters.

This guardrail ensures all walkthroughs are complete and untruncated.
"""

import pytest
from pathlib import Path
import re


def get_walkthrough_files():
    """Get walkthrough files subject to the no-ellipsis rule.
    
    Only checks files from Phase 65B onwards (when the hygiene initiative started).
    Legacy walkthroughs (pre-65B) are grandfathered and not checked.
    """
    phases_dir = Path(__file__).parent.parent / "docs" / "phases"
    if not phases_dir.exists():
        return []
    
    # Only check files from Phase 65B onwards (hygiene initiative started with 65B)
    # Also include README.md format guide
    phase_65_plus = []
    for f in phases_dir.glob("*.md"):
        # Skip README which documents the rules
        if f.name == "README.md":
            continue
        # Check if file is phase 65+ by examining filename
        match = re.match(r"phase_(\d+)", f.name)
        if match:
            phase_num = int(match.group(1))
            if phase_num >= 65:
                phase_65_plus.append(f)
    
    return phase_65_plus


def get_context_pack_files():
    """Get all context pack markdown files in docs/context_packs/."""
    packs_dir = Path(__file__).parent.parent / "docs" / "context_packs"
    if not packs_dir.exists():
        return []
    return list(packs_dir.glob("*.md"))


def find_ellipses(content: str) -> list:
    """Find all ellipsis occurrences in content.
    
    Returns list of (line_number, line_content) tuples.
    """
    findings = []
    lines = content.split("\n")
    for i, line in enumerate(lines, start=1):
        # Check for ASCII ellipsis (three dots)
        if "..." in line:
            findings.append((i, line.strip()))
        # Check for Unicode ellipsis (U+2026)
        elif "\u2026" in line:
            findings.append((i, line.strip()))
    return findings


class TestNoEllipsesInWalkthroughs:
    """Ensure no ellipses appear in walkthrough documents."""

    def test_no_ellipses_in_phase_walkthroughs(self):
        """Check docs/phases/*.md for ellipses."""
        files = get_walkthrough_files()
        
        # We expect at least some walkthrough files to exist
        assert len(files) > 0, "No walkthrough files found in docs/phases/"
        
        all_findings = []
        for filepath in files:
            content = filepath.read_text(encoding="utf-8")
            findings = find_ellipses(content)
            if findings:
                for line_num, line_content in findings:
                    all_findings.append(
                        f"{filepath.name}:{line_num}: {line_content[:80]}"
                    )
        
        if all_findings:
            msg = "Ellipses found in walkthrough files:\n" + "\n".join(all_findings)
            pytest.fail(msg)

    def test_no_ellipses_in_context_packs(self):
        """Check docs/context_packs/*.md for ellipses."""
        files = get_context_pack_files()
        
        if not files:
            pytest.skip("No context pack files found yet")
        
        all_findings = []
        for filepath in files:
            content = filepath.read_text(encoding="utf-8")
            findings = find_ellipses(content)
            if findings:
                for line_num, line_content in findings:
                    all_findings.append(
                        f"{filepath.name}:{line_num}: {line_content[:80]}"
                    )
        
        if all_findings:
            msg = "Ellipses found in context pack files:\n" + "\n".join(all_findings)
            pytest.fail(msg)
