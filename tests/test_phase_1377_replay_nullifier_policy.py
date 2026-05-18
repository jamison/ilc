from __future__ import annotations

from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1377_g8_replay_nullifier_policy.md"
)
POLICY = ROOT / "docs/specs/ilc_replay_nullifier_policy_1377_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1377_replay_nullifier_policy_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
FORWARD_PLAN = (
    ROOT / "docs/specs/ilc_forward_phase_windows_1303_1342_packaging_and_signing_plan_v0.2.md"
)
CLAIMABILITY_VERIFIER = ROOT / "ilc_core/sidecars/claimability_receipt_verifier.py"

REQUIRED_TOKENS = (
    "replay_nullifier_policy_committed_phase_1377",
    "nullifier_epoch_bounded_expiry_policy_defined",
    "duplicate_claim_rejection_policy_defined",
    "claim_endpoint_not_activated_phase_1377",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def phase_1377_status_section() -> str:
    status = read(STATUS)
    start = status.index("## Phase 1377")
    next_start = status.find("\n## Phase ", start + len("## Phase 1377"))
    if next_start == -1:
        return status[start:]
    return status[start:next_start]


def forward_plan_1377_row() -> str:
    rows = [
        line
        for line in read(FORWARD_PLAN).splitlines()
        if line.startswith("| 1377 |")
    ]
    assert len(rows) == 1
    return rows[0]


def test_phase_1377_prompt_remains_schema_valid() -> None:
    assert validate(PROMPT) == []


def test_policy_records_required_tokens_and_nullifier_contract() -> None:
    policy = read(POLICY)

    for token in REQUIRED_TOKENS:
        assert token in policy

    for expected in (
        "claim_nullifier_v1",
        "ilc-public-claim-nullifier-v1",
        "claim_nullifier_sha256:<64 lowercase hex sha256>",
        "claim_nullifier_registry_v1",
        "json.dumps(payload, sort_keys=True, separators=(\",\", \":\"), allow_nan=False)",
    ):
        assert expected in policy


def test_policy_uses_epoch_bounded_expiry_not_wall_clock() -> None:
    policy = read(POLICY)

    assert "issuance_epoch_cadence_cdl_027_one_month" in policy
    assert "CLAIM_NULLIFIER_POST_WINDOW_RETENTION_EPOCHS = 1" in policy
    assert "expires_at_issuance_epoch =" in policy
    assert "max(claim_window_end_epoch, conversion_deadline_epoch)" in policy
    assert "wall-clock" in policy
    assert "datetime.now" not in policy
    assert "time.time" not in policy


def test_duplicate_rejection_is_api_layer_before_processing() -> None:
    policy = read(POLICY)

    assert "Duplicate-claim rejection must happen at the public API admission layer" in policy
    assert "before deeper claim verification or economic processing" in policy
    assert "Atomically reserve the nullifier with status `pending`" in policy
    assert "Storage-only duplicate detection is insufficient" in policy
    assert "duplicate_claim_rejected_at_api_layer" in policy


def test_policy_does_not_activate_claim_endpoint_or_runtime() -> None:
    texts = (
        read(POLICY),
        read(WALKTHROUGH),
        phase_1377_status_section(),
        forward_plan_1377_row(),
    )

    for text in texts:
        assert "claim_endpoint_not_activated_phase_1377" in text
        assert "does not" in text or "no runtime" in text
        assert "result=public_claimability_activated" not in text
        assert "claim_endpoint_active" not in text
        assert "public_verifier_api_active" not in text


def test_frontier_docs_record_phase_1377_completion_and_next_phase() -> None:
    texts = (
        read(WALKTHROUGH),
        phase_1377_status_section(),
        read(PLANNING_INDEX),
        forward_plan_1377_row(),
    )

    for text in texts:
        for token in REQUIRED_TOKENS:
            assert token in text
        assert "Phase 1378" in text
        assert "Phase 1389" in text


def test_existing_claimability_verifier_remains_local_only_blocked_surface() -> None:
    verifier = read(CLAIMABILITY_VERIFIER)

    assert "replay_nullifier_policy_not_activated_phase_1305" in verifier
    assert "duplicate_claim_registry_not_activated_phase_1305" in verifier
    assert "\"public_claimability_activated\"," in verifier
    assert "\"non_loopback_claimability_api_enabled\"," in verifier
