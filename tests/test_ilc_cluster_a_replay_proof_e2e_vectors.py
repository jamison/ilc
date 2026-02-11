import pytest
import json
import sys
from unittest.mock import patch
from pathlib import Path

from ilc_core.protocol.ilc_cluster_a_replay_proof_package import (
    build_cluster_a_replay_proof_package,
    verify_cluster_a_replay_proof_package,
    E_HASH_MISMATCH_PACKAGE,
    E_RECORD_HASH_MISMATCH,
    E_CONTRACT_HASH_MISMATCH,
    _canonical_package_digest
)
from ilc_core.cli.canon_cluster_a_replay_proof import main as cli_main

# Fixture Paths
FIXTURE_DIR = Path(__file__).parent / "fixtures" / "cluster_a_replay_proof_v0_1"


def load_json(filename):
    with open(FIXTURE_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


class TestReplayProofE2E:

    @pytest.fixture
    def valid_evidence(self):
        return load_json("evidence_valid.json")

    @pytest.fixture
    def valid_contract(self):
        return load_json("contract_valid.json")

    @pytest.fixture
    def valid_package(self):
        return load_json("package_valid.json")

    def test_protocol_build_determinism(self, valid_evidence, valid_contract, valid_package):
        """
        Verify that building a package from golden inputs produces byte-exact golden output.
        """
        # Extract inputs from contract
        gov_rec = valid_contract["governance_record"]
        apply_res = valid_contract["apply_result"]
        conf_res = valid_contract["conformance_result"]
        
        # Build
        built_pkg = build_cluster_a_replay_proof_package(
            evidence=valid_evidence,
            governance_record=gov_rec,
            apply_result=apply_res,
            conformance_result=conf_res
        )
        
        # 1. Structural Equality
        assert built_pkg == valid_package
        
        # 2. Hash Stability
        built_hash = built_pkg["package_hash_sha256"]
        valid_hash = valid_package["package_hash_sha256"]
        assert built_hash == valid_hash
        
        # 3. Canonical Serialization Byte Equality
        assert canonical_bytes(built_pkg) == canonical_bytes(valid_package)

        # 4. Digest Equality
        digest = _canonical_package_digest(built_pkg)
        assert digest == valid_hash

    def test_protocol_verify_valid(self, valid_package):
        """Verify valid golden package passes."""
        res = verify_cluster_a_replay_proof_package(valid_package)
        assert res["ok"] is True
        assert not res["errors"]

    def test_protocol_verify_tamper_package_hash(self):
        """Verify tampering with package hash is detected."""
        pkg = load_json("package_tampered_hash.json")
        res = verify_cluster_a_replay_proof_package(pkg)
        assert res["ok"] is False
        assert E_HASH_MISMATCH_PACKAGE in res["errors"]

    def test_protocol_verify_tamper_record_hash(self):
        """Verify tampering with record content (vs hash) is detected."""
        pkg = load_json("package_tampered_record_hash.json")
        res = verify_cluster_a_replay_proof_package(pkg)
        assert res["ok"] is False
        # Since we modified the record payload in the contract but kept the claimed hash,
        # the recomputed hash of the record will differ from the claimed hash.
        assert E_RECORD_HASH_MISMATCH in res["errors"]

    def test_protocol_verify_tamper_contract_hash(self):
        """Verify tampering with evidence contract content (vs hash) is detected."""
        pkg = load_json("package_tampered_contract_hash.json")
        res = verify_cluster_a_replay_proof_package(pkg)
        assert res["ok"] is False
        # We modified evidence content but kept claimed evidence_contract_hash.
        # So recomputed contract hash will differ.
        assert E_CONTRACT_HASH_MISMATCH in res["errors"]

    def test_cli_build_parity(self, tmp_path, valid_evidence, valid_contract, valid_package):
        """
        Verify CLI build command produces identical output to protocol.
        """
        # Prepare inputs on disk
        evidence_path = tmp_path / "evidence.json"
        with open(evidence_path, "w", encoding="utf-8") as f:
            json.dump(valid_evidence, f)

        # CLI build takes: --evidence, --contract
        # We have these in valid_evidence (needs file) and contract composition (needs file).

        out_path = tmp_path / "out_package.json"

        args = [
            "prog", "build",
            "--evidence", str(evidence_path),
            "--contract", str(FIXTURE_DIR / "contract_valid.json"),
            "--out", str(out_path)
        ]
        
        with patch.object(sys, 'argv', args):
            try:
                cli_main()
            except SystemExit as e:
                assert e.code == 0

        # Load output
        with open(out_path, "r", encoding="utf-8") as f:
            cli_pkg = json.load(f)

        # Assert semantic equality with golden package
        # The golden package was built from the same logical inputs.
        assert cli_pkg == valid_package
        assert canonical_bytes(cli_pkg) == canonical_bytes(valid_package)

    def test_cli_verify_valid(self, capsys):
        """Verify CLI accepts golden package."""
        pkg_path = FIXTURE_DIR / "package_valid.json"

        # Verify uses positional argument for package
        args = ["prog", "verify", str(pkg_path)]

        with patch.object(sys, 'argv', args):
            try:
                cli_main()
            except SystemExit as e:
                assert e.code == 0
        captured = capsys.readouterr()
        res = json.loads(captured.out)
        assert res["ok"] is True
        assert res["errors"] == []

    def test_cli_verify_tampered(self, capsys):
        """Verify CLI rejects tampered packages with exit code 1."""
        tampered_files = {
            "package_tampered_hash.json": E_HASH_MISMATCH_PACKAGE,
            "package_tampered_record_hash.json": E_RECORD_HASH_MISMATCH,
            "package_tampered_contract_hash.json": E_CONTRACT_HASH_MISMATCH,
        }

        for fname, expected_error in tampered_files.items():
            pkg_path = FIXTURE_DIR / fname
            args = ["prog", "verify", str(pkg_path)]

            with patch.object(sys, 'argv', args):
                try:
                    cli_main()
                except SystemExit as e:
                    assert e.code == 1
            captured = capsys.readouterr()
            res = json.loads(captured.out)
            assert res["ok"] is False
            assert expected_error in res["errors"]
