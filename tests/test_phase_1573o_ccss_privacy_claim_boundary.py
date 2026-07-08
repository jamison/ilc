from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_ccss_public_rc_privacy_claim_boundary_1573o_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1573o_ccss_privacy_claim_boundary_walkthrough.md"
PROMPT_1574 = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1574_g10_block6_publication_readiness_audit.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase1573o_prompt_validates() -> None:
    result = subprocess.run(
        [
            ".venv/bin/python",
            "tools/validate_phase_prompt.py",
            "docs/antigravity_tasks/antigravity_prompt__phase_1573o_g10_ccss_privacy_claim_boundary.md",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_privacy_claim_matrix_separates_allowed_and_forbidden_claims() -> None:
    text = _read(SPEC)

    assert "Raw/noisy eigenvalue non-disclosure to relays | Allowed" in text
    assert "Opaque SpectralRouteToken relay view | Allowed" in text
    assert "Passive relay route-token SIM evidence | Allowed as SIM evidence only" in text
    assert "Formal `(epsilon, delta)` differential privacy | Forbidden / non-claim" in text
    assert "Network anonymity | Forbidden / non-claim" in text
    assert "Signal-equivalent sealed sender | Forbidden / non-claim" in text
    assert "Full unlinkability against global observers | Forbidden / non-claim" in text
    assert "Cover traffic | Not implemented by this phase" in text
    assert "Batching / mixing | Not implemented by this phase" in text
    assert "Relay-path hiding | Not implemented by this phase" in text


def test_forbidden_public_rc_wording_is_explicit() -> None:
    text = _read(SPEC)

    assert "CCSS-SPECTRAL provides differential privacy." in text
    assert "CCSS-SPECTRAL provides network anonymity." in text
    assert "CCSS-SPECTRAL is Signal-equivalent." in text
    assert "must not say" in text
    assert "Those claims require later formal definitions" in text


def test_phase1574_requires_claim_boundary_before_readiness_audit() -> None:
    text = _read(PROMPT_1574)

    assert "ccss_privacy_claim_boundary_committed_phase_1573o" in text
    assert "ccss_formal_dp_nonclaim_recorded_phase_1573o" in text
    assert "ccss_network_anonymity_nonclaim_recorded_phase_1573o" in text
    assert "CCSS privacy claim boundary" in text


def test_status_tokens_and_no_positive_privacy_authorization() -> None:
    text = _read(STATUS)

    for token in (
        "ccss_privacy_claim_boundary_committed_phase_1573o",
        "ccss_formal_dp_nonclaim_recorded_phase_1573o",
        "ccss_network_anonymity_nonclaim_recorded_phase_1573o",
        "ccss_route_token_non_disclosure_claim_allowed_phase_1573o",
        "public_path_remains_blocked_phase_1573o",
    ):
        assert token in text

    assert "ccss_formal_dp_claim_authorized" not in text
    assert "ccss_network_anonymity_claim_authorized" not in text


def test_walkthrough_records_prompt_path_defect_and_non_activation() -> None:
    text = _read(WALKTHROUGH)

    assert "No ellipses in walkthrough." in text
    assert "prompt-path defect" in text
    assert "No runtime files were modified" in text
    assert "No public RC, public P2P, public relay serving" in text
