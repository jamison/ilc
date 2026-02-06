
import pytest
import subprocess
import sys
import base64
import json
from pathlib import Path

COMMAND = [sys.executable, "-m", "ilc_core.cli.canon_bundle_replay"]

class TestCanonBundleReplayReport:
    
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

    @pytest.fixture
    def signed_bundle_with_audit(self, valid_bundle, key_file, tmp_path):
        """Run pipeline to get a signed bundle and audit artifact."""
        report_path = tmp_path / "pipeline_report.md"
        result = subprocess.run(
            [sys.executable, "-m", "ilc_core.cli.canon_bundle_pipeline",
             "--bundle", str(valid_bundle),
             "--key-file", str(key_file),
             "--report", str(report_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        audit_path = tmp_path / "bundle_pipeline_audit.json"
        assert audit_path.exists()
        return valid_bundle, audit_path

    def run_cli(self, args):
        return subprocess.run(
            COMMAND + args,
            capture_output=True,
            text=True
        )

    def test_report_file_created(self, signed_bundle_with_audit, tmp_path):
        bundle, audit_path = signed_bundle_with_audit
        report_path = tmp_path / "replay_report.md"
        result = self.run_cli([
            "--bundle", str(bundle),
            "--audit", str(audit_path),
            "--report", str(report_path)
        ])
        assert result.returncode == 0
        assert report_path.exists()
        assert report_path.stat().st_size > 0

    def test_report_contains_bundle_and_audit_path(self, signed_bundle_with_audit, tmp_path):
        bundle, audit_path = signed_bundle_with_audit
        report_path = tmp_path / "replay_report.md"
        self.run_cli([
            "--bundle", str(bundle),
            "--audit", str(audit_path),
            "--report", str(report_path)
        ])
        content = report_path.read_text()
        assert str(bundle) in content
        assert str(audit_path) in content

    def test_report_contains_mismatch_table_header(self, signed_bundle_with_audit, tmp_path):
        bundle, audit_path = signed_bundle_with_audit
        report_path = tmp_path / "replay_report.md"
        self.run_cli([
            "--bundle", str(bundle),
            "--audit", str(audit_path),
            "--report", str(report_path)
        ])
        content = report_path.read_text()
        assert "## Mismatches" in content

    def test_directory_resolves_to_filename(self, signed_bundle_with_audit, tmp_path):
        bundle, audit_path = signed_bundle_with_audit
        report_dir = tmp_path / "reports"
        report_dir.mkdir()
        self.run_cli([
            "--bundle", str(bundle),
            "--audit", str(audit_path),
            "--report", str(report_dir)
        ])
        expected_path = report_dir / "bundle_replay_report.md"
        assert expected_path.exists()

    def test_report_does_not_alter_exit_code(self, signed_bundle_with_audit, tmp_path):
        bundle, audit_path = signed_bundle_with_audit
        report_path = tmp_path / "replay_report.md"
        # Successful replay
        result = self.run_cli([
            "--bundle", str(bundle),
            "--audit", str(audit_path),
            "--report", str(report_path)
        ])
        assert result.returncode == 0
        assert report_path.exists()

    def test_report_written_on_failure(self, signed_bundle_with_audit, tmp_path):
        bundle, audit_path = signed_bundle_with_audit
        # Tamper with manifest to cause mismatch
        manifest = bundle / "manifest.json"
        manifest.write_text(manifest.read_text() + " ")
        
        report_path = tmp_path / "replay_report.md"
        result = self.run_cli([
            "--bundle", str(bundle),
            "--audit", str(audit_path),
            "--report", str(report_path)
        ])
        assert result.returncode == 1
        assert report_path.exists()

    def test_report_is_deterministic(self, signed_bundle_with_audit, tmp_path):
        bundle, audit_path = signed_bundle_with_audit
        report_path1 = tmp_path / "report1.md"
        report_path2 = tmp_path / "report2.md"
        
        # First run
        self.run_cli([
            "--bundle", str(bundle),
            "--audit", str(audit_path),
            "--report", str(report_path1)
        ])
        # Second run
        self.run_cli([
            "--bundle", str(bundle),
            "--audit", str(audit_path),
            "--report", str(report_path2)
        ])
        
        content1 = report_path1.read_text()
        content2 = report_path2.read_text()
        
        # Remove timestamp for comparison (first two lines)
        lines1 = content1.split("\n")[2:]
        lines2 = content2.split("\n")[2:]
        assert lines1 == lines2

    def test_replay_json_matches_stdout(self, signed_bundle_with_audit, tmp_path):
        bundle, audit_path = signed_bundle_with_audit
        report_path = tmp_path / "replay_report.md"
        result = self.run_cli([
            "--bundle", str(bundle),
            "--audit", str(audit_path),
            "--report", str(report_path)
        ])
        content = report_path.read_text()
        # The stdout JSON should be in the report
        assert result.stdout.strip() in content

    def test_known_limitations_section_exists(self, signed_bundle_with_audit, tmp_path):
        bundle, audit_path = signed_bundle_with_audit
        report_path = tmp_path / "replay_report.md"
        self.run_cli([
            "--bundle", str(bundle),
            "--audit", str(audit_path),
            "--report", str(report_path)
        ])
        content = report_path.read_text()
        assert "## Known Limitations" in content
        # Check for at least 2 bullets
        limitations_section = content.split("## Known Limitations")[1]
        bullet_count = limitations_section.count("- ")
        assert bullet_count >= 2

    def test_report_write_failed_warning_in_stdout(self, signed_bundle_with_audit, tmp_path):
        bundle, audit_path = signed_bundle_with_audit
        no_write_dir = tmp_path / "no_write"
        no_write_dir.mkdir()
        no_write_dir.chmod(0o500)
        report_path = no_write_dir / "replay_report.md"
        try:
            result = self.run_cli([
                "--bundle", str(bundle),
                "--audit", str(audit_path),
                "--report", str(report_path)
            ])
        finally:
            no_write_dir.chmod(0o700)
        assert "report_write_failed" in result.stdout
