from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
ADR = REPO / "docs/adr/ADR_0039_Validator_Endpoint_Registry.md"
ADR_README = REPO / "docs/adr/README.md"
STATUS = REPO / "docs/phases/STATUS.md"
WALKTHROUGH = REPO / "docs/phases/phase_1386b_validator_endpoint_registry_adr_walkthrough.md"


def test_adr_0039_exists_and_is_indexed() -> None:
    assert ADR.exists()
    readme = ADR_README.read_text()
    assert "ADR_0039_Validator_Endpoint_Registry.md" in readme
    assert "Validator Endpoint Registry" in readme


def test_required_phase_1386b_tokens_present() -> None:
    text = ADR.read_text()
    for token in (
        "validator_endpoint_registry_adr_ratified_phase_1386b",
        "quic_endpoint_epoch_scoped_signed_edge_defined",
        "read_only_projection_contract_defined_phase_1386b",
        "no_hardcoded_peer_list_production_activation_path_phase_1386b",
    ):
        assert token in text


def test_quic_endpoint_is_epoch_scoped_signed_edge() -> None:
    text = ADR.read_text()
    assert "`QUIC_ENDPOINT` as an epoch-scoped signed edge" in text
    assert '"edge_type": "QUIC_ENDPOINT"' in text
    assert '"topology_epoch": "<cdl-068-topology-epoch>"' in text
    assert '"signature": "<signature-ref-over-canonical-payload>"' in text
    assert "ADR-0038 Agent Birth Attestation plus CDL-090 identity bootstrap" in text
    assert "CDL-088 governs public claimability authority" in text


def test_endpoint_forms_include_direct_and_relay() -> None:
    text = ADR.read_text()
    assert "endpoint_kind=direct" in text
    assert "endpoint_kind=relay" in text
    assert "relay_mode=pass_through_consensus_quic" in text
    assert "relay_incentive_ref=CDL-078" in text


def test_read_only_projection_contract_is_fail_closed() -> None:
    text = ADR.read_text()
    assert "derived from signed graph edges only" in text
    assert "bounded to the current topology epoch's validator set" in text
    assert "invalidated and rebuilt on each CDL-068 topology shuffle" in text
    assert "must never acquire write/update/set/insert/delete methods" in text
    for forbidden_method in (
        "set_endpoint",
        "update_endpoint",
        "insert_endpoint",
        "delete_endpoint",
        "write_endpoint",
    ):
        assert forbidden_method in text


def test_no_hardcoded_peer_list_production_path() -> None:
    text = ADR.read_text()
    assert "No hardcoded peer list may appear in any production activation path" in text
    assert "Hardcoded peer lists are not a fallback" in text
    assert "Allowed pre-production uses" in text


def test_no_runtime_or_cdl_mutation_authorized() -> None:
    text = ADR.read_text()
    for non_goal in (
        "mutate the CDL register",
        "mutate runtime source",
        "activate production validators",
        "activate public P2P",
        "activate CDL-078 relay service",
    ):
        assert non_goal in text


def test_status_and_walkthrough_record_phase_close() -> None:
    text = STATUS.read_text() + "\n" + WALKTHROUGH.read_text()
    assert "validator_endpoint_registry_adr_ratified_phase_1386b" in text
    assert "Phase 1386c persistent QUIC proof next" in text
    assert "graph_delta=load_bearing_artifact_added:docs/adr/ADR_0039_Validator_Endpoint_Registry.md -> validator-connectivity/endpoint-registry-adr" in text
