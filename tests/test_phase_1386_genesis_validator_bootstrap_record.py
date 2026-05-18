from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

PROMPT = REPO / "docs/antigravity_tasks/antigravity_prompt__phase_1386_g8_multi_operator_genesis_key_ceremony.md"
RECORD = REPO / "docs/specs/ilc_genesis_validator_bootstrap_record_1386_v0.1.md"
WALKTHROUGH = REPO / "docs/phases/phase_1386_genesis_validator_bootstrap_record_walkthrough.md"
STATUS = REPO / "docs/phases/STATUS.md"
PLANNING_INDEX = REPO / "docs/PLANNING_INDEX.md"
SEQUENCE_LOCK = REPO / "docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md"
CANDIDATE_GROUPING = REPO / "docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md"


REQUIRED_TOKENS = [
    "genesis_validator_bootstrap_record_committed_phase_1386",
    "genesis_controlled_single_custodian_bootstrap_exception_phase_1386",
    "single_operator_compromise_resistance_not_confirmed_phase_1386",
    "production_split_custody_ceremony_required_before_mainnet_launch",
]

FALSE_COMPLETION_TOKENS = [
    "multi_operator_genesis_key_ceremony_complete_phase_1386",
    "genesis_key_multi_operator_distribution_verified",
]


def read(path: Path) -> str:
    assert path.exists(), f"missing expected Phase 1386 artifact: {path}"
    return path.read_text()


def test_phase_1386_artifacts_exist():
    for path in (PROMPT, RECORD, WALKTHROUGH, STATUS, PLANNING_INDEX, SEQUENCE_LOCK, CANDIDATE_GROUPING):
        assert path.exists(), f"missing artifact: {path}"


def test_required_tokens_are_recorded_in_bootstrap_record():
    text = read(RECORD)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_required_tokens_are_recorded_in_prompt_and_walkthrough():
    combined = read(PROMPT) + "\n" + read(WALKTHROUGH)
    for token in REQUIRED_TOKENS:
        assert token in combined


def test_bootstrap_record_is_explicit_single_custodian_exception():
    text = read(RECORD)
    assert "Genesis-controlled single-custodian pre-RC/testnet exception" in text
    assert "not a completed multi-operator split-custody ceremony" in text
    assert "single_operator_compromise_resistance_not_confirmed_phase_1386" in text


def test_bootstrap_record_carries_no_activation_claims():
    text = read(RECORD)
    required_non_authorizations = [
        "public RC graph permanence",
        "production genesis-signed artifacts",
        "production validator deployment",
        "live ECU/ILC value-path activation",
        "public claimability activation",
    ]
    for phrase in required_non_authorizations:
        assert phrase in text


def test_bootstrap_record_private_key_material_non_authorized_only():
    text = read(RECORD)
    assert "Private validator keys must not be committed" in text
    assert "does not itself generate, distribute, copy, escrow, or publish" in text
    assert "No private key material" not in text.split("## 4. Validator Key Handling Rule", 1)[0]


def test_false_completion_tokens_not_recorded_as_outputs():
    docs = [RECORD, WALKTHROUGH, STATUS, PLANNING_INDEX, SEQUENCE_LOCK, CANDIDATE_GROUPING]
    combined = "\n".join(read(path) for path in docs)
    for token in FALSE_COMPLETION_TOKENS:
        assert token not in combined


def test_confirmed_compromise_resistance_not_recorded_as_result():
    docs = [RECORD, WALKTHROUGH, STATUS, PLANNING_INDEX, SEQUENCE_LOCK, CANDIDATE_GROUPING]
    combined = "\n".join(read(path) for path in docs)
    assert "single_operator_compromise_resistance_confirmed" not in combined
    assert "single_operator_compromise_resistance_not_confirmed_phase_1386" in combined


def test_downstream_routing_scope_is_mainnet_not_current_public_rc_gate():
    text = read(RECORD) + "\n" + read(WALKTHROUGH)
    assert "not a current Window 1369-1390 public-RC gate" in text
    assert "before mainnet launch" in text
    assert "not inserted as a new hard gate" in text
    for phase in ("Phase 1387", "Phase 1388", "Phase 1389"):
        assert phase in text


def test_planning_docs_mark_phase_1386_complete_exception():
    combined = read(STATUS) + "\n" + read(PLANNING_INDEX) + "\n" + read(SEQUENCE_LOCK) + "\n" + read(CANDIDATE_GROUPING)
    assert "Phase 1386" in combined
    assert "Genesis-controlled single-custodian" in combined
    assert "single-operator-compromise resistance is not confirmed" in combined
    assert "Phase 1386a production TLS gRPC" in combined


def test_graph_delta_declared():
    text = read(RECORD) + "\n" + read(WALKTHROUGH) + "\n" + read(STATUS)
    assert (
        "graph_delta=load_bearing_artifact_added:docs/specs/"
        "ilc_genesis_validator_bootstrap_record_1386_v0.1.md -> genesis-validator/bootstrap-exception"
    ) in text


def test_walkthrough_has_no_ellipses():
    assert "..." not in read(WALKTHROUGH)
