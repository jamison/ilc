from __future__ import annotations

from pathlib import Path
import re
import subprocess


CDL_001_SPEC = Path("docs/specs/ilc_cdl_001_signer_lineage_trust_root_contract_v0.1.md")
CDL_002_SPEC = Path("docs/specs/ilc_cdl_002_key_compromise_response_contract_v0.1.md")
CDL_007_SPEC = Path("docs/specs/ilc_cdl_007_rollback_resistance_baseline_contract_v0.1.md")
PACKAGE_SPEC = Path("docs/specs/ilc_phase_227_blocker_remediation_package_v0.1.md")
DECISION_LOG = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
BACKLOG_QUEUE = Path("docs/specs/ilc_phase_226_decision_log_backlog_queue_v0.1.md")
GATE_SCRIPT = Path("tools/check_phase_227_blocker_remediation_package.sh")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_227_specs_exist_and_cross_linked() -> None:
    for path in (CDL_001_SPEC, CDL_002_SPEC, CDL_007_SPEC, PACKAGE_SPEC):
        assert path.exists()

    package_text = _read(PACKAGE_SPEC)
    assert str(CDL_001_SPEC) in package_text
    assert str(CDL_002_SPEC) in package_text
    assert str(CDL_007_SPEC) in package_text

    cdl_001_text = _read(CDL_001_SPEC)
    cdl_002_text = _read(CDL_002_SPEC)
    cdl_007_text = _read(CDL_007_SPEC)
    assert str(PACKAGE_SPEC) in cdl_001_text
    assert str(PACKAGE_SPEC) in cdl_002_text
    assert str(PACKAGE_SPEC) in cdl_007_text


def test_phase_227_package_has_required_tokens_and_bounded_outcomes() -> None:
    text = _read(PACKAGE_SPEC)

    assert "bounded_for_genesis_packaging: yes" in text
    assert text.count("bounded_for_genesis_packaging: yes") == 3

    assert "phase_227_package_verdict: bounded" in text
    assert "backlog_candidate_disposition_complete: yes" in text

    required_count_tokens = (
        "genesis_blocker_candidate_total:",
        "subsumed_by_cdl_001_002_007:",
        "additional_blockers_requiring_followup:",
    )
    for token in required_count_tokens:
        assert token in text


def test_phase_227_backlog_disposition_counts_match_phase_226_queue() -> None:
    package_text = _read(PACKAGE_SPEC)
    queue_text = _read(BACKLOG_QUEUE)

    package_total = int(re.search(r"genesis_blocker_candidate_total:\s*(\d+)", package_text).group(1))
    package_subsumed = int(re.search(r"subsumed_by_cdl_001_002_007:\s*(\d+)", package_text).group(1))
    package_additional = int(re.search(r"additional_blockers_requiring_followup:\s*(\d+)", package_text).group(1))

    queue_total = int(re.search(r"genesis_blocker_candidate=(\d+)", queue_text).group(1))

    assert package_total == queue_total
    assert package_subsumed + package_additional == package_total


def test_phase_227_decision_log_notes_scoped_and_open_status_preserved() -> None:
    text = _read(DECISION_LOG)

    scoped_section_match = re.search(
        r"## Scoped Remediation Record \(Phase 227\)(.*?)## Conflict Notes",
        text,
        flags=re.DOTALL,
    )
    assert scoped_section_match is not None
    scoped_text = scoped_section_match.group(1)

    assert "`CDL-001`" in scoped_text
    assert "`CDL-002`" in scoped_text
    assert "`CDL-007`" in scoped_text
    assert "`CDL-003`" not in scoped_text
    assert "`CDL-011`" not in scoped_text

    register_rows = {
        "CDL-001": re.search(r"\| CDL-001 \|[^\n]*\| (open|ratified) \|", text),
        "CDL-002": re.search(r"\| CDL-002 \|[^\n]*\| (open|ratified) \|", text),
        "CDL-007": re.search(r"\| CDL-007 \|[^\n]*\| (open|ratified) \|", text),
    }
    for match in register_rows.values():
        assert match is not None
        assert match.group(1) == "open"


def test_phase_227_gate_script_contracts() -> None:
    help_run = subprocess.run(
        [str(GATE_SCRIPT), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert help_run.returncode == 0
    assert "Usage: check_phase_227_blocker_remediation_package.sh" in help_run.stdout

    dry_run = subprocess.run(
        [str(GATE_SCRIPT), "--dry-run"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert dry_run.returncode == 0
    assert "Dry run: phase-227 blocker remediation package commands" in dry_run.stdout

    unknown = subprocess.run(
        [str(GATE_SCRIPT), "--unknown-arg"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert unknown.returncode == 2
    assert "Unknown argument: --unknown-arg" in unknown.stderr


