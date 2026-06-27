from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_fix2b_prompt_preserves_public_firewall_without_private_bypass() -> None:
    prompt = _read(
        "docs/antigravity_tasks/antigravity_prompt__phase_1568_fix2b_g10_runtime_identity_economics_hardening.md"
    )
    required = [
        "disposable rehearsal public-admission records",
        "public economics firewall",
        "Do not implement a private economics bypass",
        "initialized-agent identity binding",
        "real signing boundary",
        "SimpleEpochLedger",
        "must not be represented as the authoritative ECU or ILC path",
    ]
    for term in required:
        assert term in prompt


def test_fix2c_prompt_is_d2d_readiness_not_value_settlement() -> None:
    prompt = _read(
        "docs/antigravity_tasks/antigravity_prompt__phase_1568_fix2c_g10_four_machine_d2d_readiness.md"
    )
    required = [
        "four-machine",
        "D2D",
        "production TLS semantics",
        "Fix2d cannot start unless every host is green",
        "Do not emit Fix2d live-rerun pass tokens",
    ]
    for term in required:
        assert term in prompt


def test_fix2d_prompt_maps_full_ecu_poil_production_path() -> None:
    prompt = _read(
        "docs/antigravity_tasks/antigravity_prompt__phase_1568_fix2d_g10_live_production_path_soft_rc.md"
    )
    required = [
        "node submission",
        "review/jury acceptance",
        "ECU lot creation",
        "CDL-048 conversion",
        "ILC allocation event",
        "settlement root verification",
        "SimpleEpochLedger",
        "cannot be the authoritative result",
        "four issuance epochs",
        "forward trace",
        "backward trace",
    ]
    for term in required:
        assert term in prompt


def test_fix2e_prompt_treats_boolean_tokens_as_attack_surface_without_flipping() -> None:
    prompt = _read(
        "docs/antigravity_tasks/antigravity_prompt__phase_1568_fix2e_g10_pre_signing_guard_attack_surface.md"
    )
    required = [
        "Do not flip committed guards",
        "permanent_fail_closed",
        "authority_proof_activation_receipt",
        "post_rc_deferred",
        "human_escalation",
        "one-line production activation booleans",
    ]
    for term in required:
        assert term in prompt


def test_ecu_poil_audit_records_known_blockers_and_boundaries() -> None:
    report = _read("docs/specs/ilc_phase_1568_fix2d_ecu_poil_production_path_audit_v0.1.md")
    required = [
        "`epoch_emission_production_path.py` computes epoch-level ILC pool quotes",
        "not the node-level ECU earning path",
        "No private economics bypass",
        "SimpleEpochLedger",
        "telemetry but insufficient as the authoritative soft-RC value path",
        "Agent IDs derive from identity seed",
        "CDL-048 uses a **four issuance epoch** conversion deadline",
        "Merkle-Laplacian",
        "Do not claim Laplacian reputation is the active ECU issuer",
    ]
    for term in required:
        assert term in report
