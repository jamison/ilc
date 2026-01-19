"""
Test that relative markdown links in Phase 65+ docs and context packs resolve to existing files.

This guardrail prevents doc link rot by failing if linked files don't exist.
Only checks files from Phase 65+ (when hygiene initiative started) to avoid
failing on legacy docs with known stale links.
"""

import pytest
import re
from pathlib import Path


def get_phase_65_plus_walkthroughs():
    """Get walkthrough files from Phase 65B onwards."""
    phases_dir = Path(__file__).parent.parent / "docs" / "phases"
    if not phases_dir.exists():
        return []
    
    phase_65_plus = []
    for f in phases_dir.glob("*.md"):
        # Skip README
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
    """Get all context pack markdown files."""
    packs_dir = Path(__file__).parent.parent / "docs" / "context_packs"
    if not packs_dir.exists():
        return []
    return list(packs_dir.glob("*.md"))


def get_adr_files():
    """Get all ADR markdown files."""
    adr_dir = Path(__file__).parent.parent / "docs" / "adr"
    if not adr_dir.exists():
        return []
    return list(adr_dir.glob("*.md"))


def get_mcp_files():
    """Get MCP readme files."""
    mcp_dir = Path(__file__).parent.parent / "docs" / "mcp"
    if not mcp_dir.exists():
        return []
    return list(mcp_dir.glob("*.md"))


def extract_relative_links(content: str) -> list:
    """Extract relative markdown links from content.
    
    Returns list of (link_text, link_path) tuples.
    Ignores http/https URLs and mailto links.
    """
    # Match [text](path) but not [text](http...) or [text](mailto:...)
    pattern = r'\[([^\]]*)\]\(([^)]+)\)'
    matches = re.findall(pattern, content)
    
    relative_links = []
    for text, path in matches:
        # Skip external URLs
        if path.startswith(('http://', 'https://', 'mailto:')):
            continue
        # Skip pure anchors
        if path.startswith('#'):
            continue
        relative_links.append((text, path))
    
    return relative_links


def resolve_link(source_file: Path, link_path: str, repo_root: Path) -> Path:
    """Resolve a relative link to an absolute path.
    
    Handles:
    - Paths relative to the source file's directory
    - Anchor references (strips everything after #)
    """
    # Strip anchor if present
    if '#' in link_path:
        link_path = link_path.split('#')[0]
    
    # Empty path after stripping anchor means it's a same-file anchor
    if not link_path:
        return source_file
    
    # Resolve relative to source file's directory
    source_dir = source_file.parent
    resolved = (source_dir / link_path).resolve()
    
    return resolved


class TestDocsLinksResolve:
    """Ensure all relative links in Phase 65+ docs point to existing files."""

    def test_phase_65_plus_walkthrough_links_resolve(self):
        """Check Phase 65+ walkthrough links resolve to existing files."""
        repo_root = Path(__file__).parent.parent
        doc_files = get_phase_65_plus_walkthroughs()
        
        if not doc_files:
            pytest.skip("No Phase 65+ walkthrough files found")
        
        broken_links = self._find_broken_links(doc_files, repo_root)
        
        if broken_links:
            msg = "Broken links in Phase 65+ walkthroughs:\n" + "\n".join(broken_links)
            pytest.fail(msg)

    def test_context_pack_links_resolve(self):
        """Check context pack links resolve to existing files."""
        repo_root = Path(__file__).parent.parent
        doc_files = get_context_pack_files()
        
        if not doc_files:
            pytest.skip("No context pack files found")
        
        broken_links = self._find_broken_links(doc_files, repo_root)
        
        if broken_links:
            msg = "Broken links in context packs:\n" + "\n".join(broken_links)
            pytest.fail(msg)

    def test_adr_links_resolve(self):
        """Check ADR links resolve to existing files."""
        repo_root = Path(__file__).parent.parent
        doc_files = get_adr_files()
        
        if not doc_files:
            pytest.skip("No ADR files found")
        
        broken_links = self._find_broken_links(doc_files, repo_root)
        
        if broken_links:
            msg = "Broken links in ADRs:\n" + "\n".join(broken_links)
            pytest.fail(msg)

    def test_mcp_readme_links_resolve(self):
        """Check MCP readme links resolve to existing files."""
        repo_root = Path(__file__).parent.parent
        doc_files = get_mcp_files()
        
        if not doc_files:
            pytest.skip("No MCP files found")
        
        broken_links = self._find_broken_links(doc_files, repo_root)
        
        if broken_links:
            msg = "Broken links in MCP docs:\n" + "\n".join(broken_links)
            pytest.fail(msg)

    def _find_broken_links(self, doc_files: list, repo_root: Path) -> list:
        """Find broken links in a list of doc files."""
        broken_links = []
        
        for doc_file in doc_files:
            try:
                content = doc_file.read_text(encoding="utf-8")
            except Exception:
                continue
            
            links = extract_relative_links(content)
            
            for link_text, link_path in links:
                resolved = resolve_link(doc_file, link_path, repo_root)
                
                if not resolved.exists():
                    rel_doc = doc_file.relative_to(repo_root)
                    broken_links.append(
                        f"{rel_doc}: [{link_text}]({link_path})"
                    )
        
        return broken_links
