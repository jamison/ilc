
import pytest
import subprocess
import sys
import base64
import json
from pathlib import Path

COMMAND = [sys.executable, "-m", "ilc_core.cli.canon_bundle_pipeline"]

class TestCanonBundlePipelineReport:
    
    @pytest.fixture
    def valid_bundle(self, tmp_path):
        from ilc_core.ledger.canon_export_bundle import write_canon_export_bundle
        bundle = tmp_path / "bundle"
        export = {"canon_hash": "abc123", "canon_export_format": "v0.1"}
        validation = {"ok": True, "errors": [], "warnings": []}
        write_canon_export_bundle(export, validation, bundle)
        return bundle

    @pytest.fixture
    def key_file(self, tmp_path):
        p = tmp_path / "key.txt"
        p.write_text(base64.b64encode(b"secret").decode())
        return p

    def run_cli(self, args):
        return subprocess.run(
            COMMAND + args,
            capture_output=True,
            text=True
        )

    def test_report_file_created(self, valid_bundle, key_file, tmp_path):
        report_path = tmp_path / "report.md"
        result = self.run_cli([
            "--bundle", str(valid_bundle),
            "--key-file", str(key_file),
            "--report", str(report_path)
        ])
        assert result.returncode == 0
        assert report_path.exists()
        content = report_path.read_text()
        assert len(content) > 0
        assert result.stderr == ""

    def test_report_contains_bundle_path(self, valid_bundle, key_file, tmp_path):
        report_path = tmp_path / "report.md"
        self.run_cli([
            "--bundle", str(valid_bundle),
            "--key-file", str(key_file),
            "--report", str(report_path)
        ])
        content = report_path.read_text()
        assert str(valid_bundle) in content

    def test_report_contains_steps_table(self, valid_bundle, key_file, tmp_path):
        report_path = tmp_path / "report.md"
        self.run_cli([
            "--bundle", str(valid_bundle),
            "--key-file", str(key_file),
            "--report", str(report_path)
        ])
        content = report_path.read_text()
        assert "| validate |" in content
        assert "| sign |" in content
        assert "| verify |" in content
        assert "| report |" in content

    def test_report_contains_json_output(self, valid_bundle, key_file, tmp_path):
        report_path = tmp_path / "report.md"
        result = self.run_cli([
            "--bundle", str(valid_bundle),
            "--key-file", str(key_file),
            "--report", str(report_path)
        ])
        content = report_path.read_text()
        assert "```json" in content
        assert '"ok":true' in content

    def test_directory_resolves_to_filename(self, valid_bundle, key_file, tmp_path):
        report_dir = tmp_path / "reports"
        report_dir.mkdir()
        result = self.run_cli([
            "--bundle", str(valid_bundle),
            "--key-file", str(key_file),
            "--report", str(report_dir)
        ])
        assert result.returncode == 0
        expected_path = report_dir / "bundle_pipeline_report.md"
        assert expected_path.exists()

    def test_report_does_not_alter_exit_code(self, valid_bundle, key_file, tmp_path):
        report_path = tmp_path / "report.md"
        result = self.run_cli([
            "--bundle", str(valid_bundle),
            "--key-file", str(key_file),
            "--report", str(report_path)
        ])
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["ok"] is True

    def test_report_written_on_failure(self, tmp_path, key_file):
        report_path = tmp_path / "report.md"
        result = self.run_cli([
            "--bundle", str(tmp_path / "missing"),
            "--key-file", str(key_file),
            "--report", str(report_path)
        ])
        assert result.returncode == 1
        # Report should still be written even on failure
        assert report_path.exists()
        content = report_path.read_text()
        assert "bundle_missing" in content

    def test_render_pipeline_report_unit(self):
        from ilc_core.ledger.canon_bundle_pipeline_report import render_pipeline_report
        report = {
            "ok": True,
            "errors": [],
            "warnings": [],
            "steps": {"validate": True, "sign": True, "verify": True, "report": False},
            "bundle_path": "/test/bundle"
        }
        md = render_pipeline_report("/test/bundle", report, timestamp="2026-02-05 00:00:00 UTC")
        assert "Bundle: `/test/bundle`" in md
        assert "Status: **OK**" in md
        assert "| validate | True |" in md
        assert "| sign | True |" in md
        assert "```json" in md
