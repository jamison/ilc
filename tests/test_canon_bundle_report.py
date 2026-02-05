
import pytest
import subprocess
import sys
from pathlib import Path
from ilc_core.ledger.canon_export_bundle_report import render_bundle_report

COMMAND = [sys.executable, "-m", "ilc_core.cli.canon_bundle_validate"]

class TestCanonBundleReport:
    
    def test_render_clean_report(self):
        """Test report rendering for a clean validation."""
        report = {"ok": True, "errors": [], "warnings": []}
        md = render_bundle_report("/path/to/bundle", report, timestamp="2026-01-01T00:00:00Z")
        
        assert "Status: **OK**" in md
        assert "Bundle: `/path/to/bundle`" in md
        assert "Timestamp: `2026-01-01T00:00:00Z`" in md
        assert "## Errors" in md
        assert "- None" in md

    def test_render_error_report(self):
        """Test report rendering with errors and warnings."""
        report = {
            "ok": False,
            "errors": ["Bad hash", "Missing file"],
            "warnings": ["Old version"]
        }
        md = render_bundle_report("/path/to/bundle", report)
        
        assert "Status: **FAIL**" in md
        assert "- Bad hash" in md
        assert "- Missing file" in md
        assert "- Old version" in md
        # Check sorting
        assert md.index("Bad hash") < md.index("Missing file")

    def test_cli_report_generation(self, tmp_path):
        """Verify CLI generates report file."""
        from ilc_core.ledger.canon_export_bundle import write_canon_export_bundle
        
        bundle_dir = tmp_path / "bundle"
        write_canon_export_bundle({"canon_hash": "h"}, {"ok": True}, bundle_dir)
        
        report_file = tmp_path / "report.md"
        
        result = subprocess.run(
            COMMAND + ["--bundle", str(bundle_dir), "--report", str(report_file)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert report_file.exists()
        content = report_file.read_text()
        assert "Status: **OK**" in content
        assert str(bundle_dir) in content

    def test_cli_report_to_directory(self, tmp_path):
        """If directory passed to --report, use default filename."""
        from ilc_core.ledger.canon_export_bundle import write_canon_export_bundle
        
        bundle_dir = tmp_path / "bundle"
        write_canon_export_bundle({"canon_hash": "h"}, {"ok": True}, bundle_dir)
        
        report_dir = tmp_path / "reports"
        report_dir.mkdir()
        
        result = subprocess.run(
            COMMAND + ["--bundle", str(bundle_dir), "--report", str(report_dir)],
            capture_output=True,
            text=True
        )
        
        expected_file = report_dir / "bundle_validation_report.md"
        assert result.returncode == 0
        assert expected_file.exists()
