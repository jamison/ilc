import json
import subprocess
import sys
from pathlib import Path

from tools.capproof.verify_gate_a import build_gate_a_evidence


def test_gate_a_evidence_builder_passes_all_invariants() -> None:
    evidence = build_gate_a_evidence()

    assert evidence["gate_verdict"] == "PASS"
    assert evidence["output_token"] == "capproof_gate_a_pass_phase_1609"
    assert set(evidence["invariants"]) == {
        "1_no_ilc_mint",
        "2_ecu_band_bounded",
        "3_5probe_suite_complete",
        "4_posk_present",
        "5_no_stacking_rule",
        "6_conservation_equation",
    }
    assert all(item["result"] == "pass" for item in evidence["invariants"].values())


def test_gate_a_script_writes_atomic_json_to_requested_output_dir(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/capproof/verify_gate_a.py",
            "--output-dir",
            str(tmp_path),
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    assert result.returncode == 0, result.stdout
    evidence_path = tmp_path / "gate_a_evidence.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["gate_verdict"] == "PASS"
    assert evidence["output_token"] == "capproof_gate_a_pass_phase_1609"
