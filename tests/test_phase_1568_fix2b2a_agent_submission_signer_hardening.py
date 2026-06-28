from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_fix2b2a_prompt_records_signer_hardening_contract() -> None:
    prompt = _read(
        "docs/antigravity_tasks/antigravity_prompt__phase_1568_fix2f_g10_agent_submission_signer_hardening.md"
    )
    required = [
        "ILC_AGENT_SUBMISSION_V1",
        "ILC_GENESIS_ROOT_ENVELOPE_V1",
        "stale prebuilt binaries",
        "duplicate `agent_id` records are rejected",
        "--envelope-json",
        "phase_1568_fix2b2a_live_rerun_remains_blocked_pending_fix2b3",
        "does not run the live soft-RC",
    ]
    for term in required:
        assert term in prompt


def test_fix2b2a_report_records_closed_findings_and_remaining_blocker() -> None:
    report = _read(
        "docs/specs/ilc_phase_1568_fix2b2a_agent_submission_signer_hardening_v0.1.md"
    )
    required = [
        "Stale-binary test risk",
        "No successful sign/verify proof",
        "Non-ASCII `agent_id` panic risk",
        "Duplicate manifest records",
        "JSON Envelope",
        "phase_1568_fix2b3_attribution_batch_ingestion_required",
        "No live rehearsal was run",
    ]
    for term in required:
        assert term in report


def test_fix2b2a_status_tokens_present() -> None:
    status = _read("docs/phases/STATUS.md")
    required = [
        "phase_1568_fix2b2a_agent_submission_signer_hardened",
        "phase_1568_fix2b2a_manifest_validation_hardened",
        "phase_1568_fix2b2a_hermetic_sign_verify_tests_added",
        "phase_1568_fix2b2_agent_submission_signer_complete",
        "phase_1568_fix2b2a_live_rerun_remains_blocked_pending_fix2b3",
        "public_path_remains_blocked_phase_1568_fix2b2a",
    ]
    for token in required:
        assert token in status
