from __future__ import annotations

from pathlib import Path


CONTRACT_PATH = Path("docs/specs/ilc_capability_proof_activation_readiness_contract_231_v0.1.md")


def _text() -> str:
    return CONTRACT_PATH.read_text(encoding="utf-8")


def test_phase_231_contract_file_exists() -> None:
    assert CONTRACT_PATH.exists()


def test_phase_231_required_sections_present() -> None:
    text = _text()
    assert "## 1. Purpose and scope" in text
    assert "## 2. CapProof baseline lock (Gate A)" in text
    assert "## 3. Current readiness assessment (assessment values only)" in text
    assert "## 4. Explicit deferred boundaries" in text
    assert "## 5. CDL dependency statement" in text
    assert "## 6. Non-goals" in text
    assert "## 7. Canonical anchors" in text


def test_phase_231_deferred_lanes_have_named_gate_conditions() -> None:
    text = _text()
    assert "Anchored Work Proofs / Intelligent Inference Hash (AWP/IIH)" in text
    assert "must not be activated until Gate C" in text
    assert "Quality-Adjusted Tokens Per Second / Continuous Inference Token (QATPS/CIT)" in text
    assert "must not be activated until Gate E" in text
    assert "Ingenuity scoring remains research-lane only" in text
    assert "AWP pool split policy is not ratified" in text
    assert "must not be activated until Gate D" in text


def test_phase_231_gate_a_invariants_present() -> None:
    text = _text()
    assert "No-direct-ILC-reward invariant" in text
    assert "No user-supplied kernels/backend hints invariant" in text


def test_phase_231_cdl_dependency_tokens_present() -> None:
    text = _text()
    assert "`CDL-001`" in text
    assert "`CDL-002`" in text
    assert "`CDL-007`" in text


def test_phase_231_required_canonical_anchors_present() -> None:
    text = _text()
    assert "docs/specs/ilc_capability_proof_activation_readiness_gates_v0.1.md" in text
    assert "docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md" in text
    assert "docs/specs/capproof_kernels.md" in text
    assert "docs/specs/ilc_constitutional_decision_log_v0.1.md" in text
    assert "docs/specs/ilc_post_genesis_capability_proof_activation_sequence_230_239_v0.1.md" in text
