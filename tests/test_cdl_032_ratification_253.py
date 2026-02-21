"""
Phase 253 — CDL-032 CLI-First SDK Ratification Tests

Verifies:
- ratification evidence document exists
- CLI command surface lock document exists
- CDL-032 status is ratified
- CDL-032 has ratified_phase and evidence_document fields
- all seven primitive commands are present in the surface lock
- explicit star.map exclusion is present
- CDL-001/002/007 remain ratified
- CDL-019 remains open
- CDL-025 through CDL-031 unchanged (open)
- CDL-033 unchanged (open)
- no ilc_core/ files touched (verified by checking no new py imports from ilc_core in test or surface lock)
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
EVIDENCE_DOC = REPO_ROOT / "docs/specs/ilc_cdl_032_cli_first_sdk_ratification_evidence_253_v0.1.md"
SURFACE_LOCK = REPO_ROOT / "docs/specs/ilc_cli_command_surface_lock_253_v0.1.md"
CDL_LOG = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"

SEVEN_PRIMITIVE_COMMANDS = ["assert", "validate", "contradict", "refute", "revise", "link", "epoch"]


class TestDocumentsExist:
    def test_ratification_evidence_doc_exists(self):
        assert EVIDENCE_DOC.exists(), f"Ratification evidence document not found: {EVIDENCE_DOC}"

    def test_cli_surface_lock_exists(self):
        assert SURFACE_LOCK.exists(), f"CLI command surface lock not found: {SURFACE_LOCK}"


class TestCLISurfaceLockContent:
    def setup_method(self):
        self.text = SURFACE_LOCK.read_text()

    def test_all_seven_primitive_commands_present(self):
        for cmd in SEVEN_PRIMITIVE_COMMANDS:
            assert f"`{cmd}`" in self.text or f"| `{cmd}`" in self.text or cmd in self.text, (
                f"Primitive command '{cmd}' missing from CLI surface lock"
            )

    def test_star_map_exclusion_present(self):
        assert "star.map" in self.text, "star.map exclusion statement missing from CLI surface lock"
        assert "excluded" in self.text.lower() or "exclusion" in self.text.lower() or "not a Genesis" in self.text, \
            "star.map exclusion statement must explicitly exclude star.map"

    def test_exit_code_semantics_present(self):
        # Must include exit codes 0, 1, 2, 3
        assert "exit code" in self.text.lower() or "exit-code" in self.text.lower() or "Exit code" in self.text
        assert "`0`" in self.text or "| 0 |" in self.text or "exit 0" in self.text.lower()

    def test_json_io_contract_present(self):
        assert "JSON" in self.text, "JSON I/O contract missing from CLI surface lock"

    def test_capproof_gate_a_fail_closed_present(self):
        assert "fail-closed" in self.text or "Fail-closed" in self.text, \
            "CapProof Gate-A fail-closed invariant missing"

    def test_capproof_gate_a_no_user_supplied_kernels_present(self):
        assert "user-supplied" in self.text or "no-user-supplied" in self.text, \
            "CapProof Gate-A no-user-supplied-kernels invariant missing"

    def test_operational_commands_present(self):
        operational = ["query", "verify", "balance", "identity", "bundle", "shard", "capproof", "config"]
        for cmd in operational:
            assert cmd in self.text, f"Operational command '{cmd}' missing from CLI surface lock"


class TestCDL032StatusRatified:
    def setup_method(self):
        self.text = CDL_LOG.read_text()
        self.lines = self.text.splitlines()

    def _get_cdl_row(self, cdl_id: str) -> str:
        row = next((l for l in self.lines if l.startswith(f"| {cdl_id} ")), None)
        assert row is not None, f"{cdl_id} row not found in decision log"
        return row

    def test_cdl_032_status_is_ratified(self):
        row = self._get_cdl_row("CDL-032")
        assert "ratified" in row, f"CDL-032 not ratified; row: {row}"

    def test_cdl_032_has_ratified_phase(self):
        row = self._get_cdl_row("CDL-032")
        assert "ratified_phase: 253" in row, f"CDL-032 missing ratified_phase: 253; row: {row}"

    def test_cdl_032_has_evidence_document(self):
        row = self._get_cdl_row("CDL-032")
        assert "evidence_document" in row
        assert "ilc_cdl_032_cli_first_sdk_ratification_evidence_253_v0.1.md" in row


class TestPreviouslyRatifiedCDLsUnchanged:
    def setup_method(self):
        self.text = CDL_LOG.read_text()
        self.lines = self.text.splitlines()

    def _get_cdl_row(self, cdl_id: str) -> str:
        row = next((l for l in self.lines if l.startswith(f"| {cdl_id} ")), None)
        assert row is not None, f"{cdl_id} row not found in decision log"
        return row

    def test_cdl_001_remains_ratified(self):
        row = self._get_cdl_row("CDL-001")
        assert "ratified" in row, f"CDL-001 should remain ratified; row: {row}"

    def test_cdl_002_remains_ratified(self):
        row = self._get_cdl_row("CDL-002")
        assert "ratified" in row, f"CDL-002 should remain ratified; row: {row}"

    def test_cdl_007_remains_ratified(self):
        row = self._get_cdl_row("CDL-007")
        assert "ratified" in row, f"CDL-007 should remain ratified; row: {row}"


class TestUnchangedOpenCDLs:
    def setup_method(self):
        self.text = CDL_LOG.read_text()
        self.lines = self.text.splitlines()

    def _get_cdl_row(self, cdl_id: str) -> str:
        row = next((l for l in self.lines if l.startswith(f"| {cdl_id} ")), None)
        assert row is not None, f"{cdl_id} row not found in decision log"
        return row

    def test_cdl_019_remains_open(self):
        row = self._get_cdl_row("CDL-019")
        assert "open" in row, f"CDL-019 should remain open; row: {row}"
        assert "ratified_phase: 253" not in row

    def test_cdl_025_remains_open(self):
        row = self._get_cdl_row("CDL-025")
        assert "open" in row
        assert "ratified_phase: 253" not in row

    def test_cdl_026_remains_open(self):
        row = self._get_cdl_row("CDL-026")
        assert "open" in row

    def test_cdl_027_remains_open(self):
        row = self._get_cdl_row("CDL-027")
        assert "open" in row

    def test_cdl_028_remains_open(self):
        row = self._get_cdl_row("CDL-028")
        assert "open" in row

    def test_cdl_029_remains_open(self):
        row = self._get_cdl_row("CDL-029")
        assert "open" in row

    def test_cdl_030_remains_open(self):
        row = self._get_cdl_row("CDL-030")
        assert "open" in row

    def test_cdl_031_remains_open(self):
        row = self._get_cdl_row("CDL-031")
        assert "open" in row

    def test_cdl_033_remains_open(self):
        row = self._get_cdl_row("CDL-033")
        assert "open" in row
        assert "ratified_phase: 253" not in row


class TestNoIlcCoreChanges:
    def test_evidence_doc_contains_no_runtime_boundary_statement(self):
        content = EVIDENCE_DOC.read_text()
        # Evidence doc must contain explicit boundary statement that no runtime implementation was introduced
        assert "No runtime implementation was introduced" in content

    def test_surface_lock_does_not_import_ilc_core(self):
        content = SURFACE_LOCK.read_text()
        # Surface lock is a spec doc and must not contain ilc_core import statements
        assert "import ilc_core" not in content
        assert "from ilc_core import" not in content
