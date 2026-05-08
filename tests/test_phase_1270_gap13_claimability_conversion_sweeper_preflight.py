from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from ilc_core.ledger.ecu_ilc_lifecycle_runtime import EcuIlcLifecycleRuntime
from ilc_core.protocol.public_wallet_runtime import PublicWalletRuntime
from ilc_core.rc.local_skill_preview import build_local_skill_preview_manifest
from ilc_core.rc.package_profile_ci_gate import build_package_profile_ci_audit
from ilc_core.rc.package_profiles import PROFILE_OPENCLAW_SKILL_CLAIMABLE


SPEC_PATH = Path("docs/specs/ilc_gap13_claimability_conversion_sweeper_preflight_1270_v0.1.md")
WALKTHROUGH_PATH = Path(
    "docs/phases/phase_1270_gap13_claimability_conversion_sweeper_preflight_walkthrough.md"
)
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
LIFECYCLE_RUNTIME_PATH = Path("ilc_core/ledger/ecu_ilc_lifecycle_runtime.py")
PUBLIC_WALLET_RUNTIME_PATH = Path("ilc_core/protocol/public_wallet_runtime.py")

REQUIRED_TOKENS = (
    "gap13_claimability_conversion_sweeper_preflight_phase_1270.v0.1",
    "public_claimability_runtime_not_activated_phase_1270",
    "cdl_048_conversion_sweeper_requirements_recorded_phase_1270",
    "wallet_withdrawal_transfer_spend_not_enabled_phase_1270",
)


class _WalletStore:
    def __init__(self) -> None:
        self.wallets: dict[str, dict[str, object]] = {}
        self.histories: dict[str, dict[str, object]] = {}

    def get_wallet(self, agent_id: str) -> dict[str, object] | None:
        return self.wallets.get(agent_id)

    def put_wallet(self, agent_id: str, wallet: dict[str, object]) -> None:
        self.wallets[agent_id] = wallet

    def get_wallet_history(self, agent_id: str) -> dict[str, object] | None:
        return self.histories.get(agent_id)

    def put_wallet_history(self, agent_id: str, history: dict[str, object]) -> None:
        self.histories[agent_id] = history


class _EcuRuntime:
    def __init__(self) -> None:
        self.accrued = {"agent:alpha": "7.5"}

    def get_accrued_ecu(self, agent_id: str) -> str:
        return self.accrued.get(agent_id, "0")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1270_required_tokens_are_recorded_everywhere() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)
    planning = _read(PLANNING_INDEX_PATH)
    roadmap = _read(ROADMAP_PATH)

    for text in (spec, walkthrough, status, planning, roadmap):
        for token in REQUIRED_TOKENS:
            assert token in text

    assert "Window 1265-1272 OPEN / PASS through Phase 1270" in planning
    assert "public_rc_remains_blocked_after_phase_1270" in roadmap
    assert "Phase 1271 - ATLAS-G-006 public-RC graph reachability gate" in status
    assert "phase_1271_atlas_g_006_public_rc_graph_reachability_gate_next" in status


def test_phase_1270_records_broad_discovery_and_source_expansion() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)

    for text in (spec, walkthrough):
        assert "Exact-token" in text
        assert "Concept discovery" in text
        assert "Contradiction" in text
        assert "Source expansion" in text
        assert "public claimability" in text
        assert "wallet withdrawal" in text
        assert "wallet transfer" in text
        assert "wallet spend" in text
        assert "conversion sweeper" in text
        assert "CDL-048" in text
        assert "four issuance epoch" in text
        assert "TransportPrincipal" in text


def test_phase_1270_lifecycle_and_public_wallet_remain_deferred_read_only() -> None:
    wallet_store = _WalletStore()
    lifecycle = EcuIlcLifecycleRuntime(
        wallet_store=wallet_store,
        ecu_runtime=_EcuRuntime(),
    )
    commit = lifecycle.commit_settled_epoch(
        agent_id="agent:alpha",
        epoch_id="epoch:0004",
        reward_delta_ilc=Decimal("1.25"),
    )
    wallet_runtime = PublicWalletRuntime(
        wallet_store=wallet_store,
        lifecycle_runtime=lifecycle,
    )

    assert commit["data"]["claimability_state"] == "deferred"
    assert wallet_runtime.wallet_status(agent_id="agent:alpha")["data"]["claimability_state"] == "deferred"
    assert wallet_runtime.wallet_history(agent_id="agent:alpha")["data"]["claimability_state"] == "deferred"
    assert wallet_runtime.wallet_export(agent_id="agent:alpha")["data"]["claimability_state"] == "deferred"
    assert wallet_runtime.ledger_summary(agent_id="agent:alpha")["data"]["claimability_state"] == "deferred"

    source = _read(PUBLIC_WALLET_RUNTIME_PATH)
    for forbidden in ("def withdraw", "def transfer", "def spend", "def sign", "mint_ecu", "settle_ilc"):
        assert forbidden not in source


def test_phase_1270_runtime_sources_preserve_canonical_json_and_finite_decimal_boundary() -> None:
    lifecycle_source = _read(LIFECYCLE_RUNTIME_PATH)
    wallet_source = _read(PUBLIC_WALLET_RUNTIME_PATH)

    assert "parse_non_negative_decimal" in lifecycle_source
    assert "to_decimal" in lifecycle_source
    assert "claimability_state\": \"deferred\"" in lifecycle_source
    assert "sort_keys=True" in lifecycle_source
    assert "allow_nan=False" in lifecycle_source
    assert "sort_keys=True" in wallet_source
    assert "allow_nan=False" in wallet_source
    assert "wallet_state_sha256" in wallet_source
    assert "balance_receipt_sha256" in wallet_source


def test_phase_1270_package_profile_claimability_is_declared_not_activated() -> None:
    audit = build_package_profile_ci_audit()
    claimable = audit["profiles"][PROFILE_OPENCLAW_SKILL_CLAIMABLE]["claim_status"]
    manifest = build_local_skill_preview_manifest()

    assert claimable["public_claimability_declared"] is True
    assert claimable["public_claimability_runtime_activated"] is False
    assert claimable["public_rc_claimed"] is False
    assert claimable["public_p2p_declared"] is False
    assert manifest["public_claimability_enabled"] is False
    assert manifest["public_p2p_enabled"] is False
    assert manifest["final_public_rc_claim"] is False
    assert manifest["transport_principal_required_for_non_loopback"] is True


def test_phase_1270_cdl048_ratified_but_sweeper_runtime_remains_future_requirement() -> None:
    register = _read(CDL_REGISTER_PATH)
    spec = _read(SPEC_PATH)
    roadmap = _read(ROADMAP_PATH)

    cdl048_rows = [line for line in register.splitlines() if line.startswith("| CDL-048 |")]
    assert len(cdl048_rows) == 1
    assert "| ratified |" in cdl048_rows[0]
    assert "ratified_phase: 419" in cdl048_rows[0]

    assert "CDL-048 is already ratified" in spec
    assert "ecu_conversion_deadline = 4 issuance epochs" in spec
    assert "It does not mark" in spec
    assert "the conversion sweeper complete" in spec
    assert "mandatory_conversion_sweeper_required_for_cdl_048_runtime" in roadmap
    assert "public_rc_remains_blocked_after_phase_1270" in roadmap


def test_phase_1270_spec_records_future_claimability_proof_requirements_and_non_claims() -> None:
    spec = _read(SPEC_PATH)

    for phrase in (
        "settled runtime root proof",
        "wallet-state root",
        "latest balance receipt",
        "history digest",
        "epoch identifier",
        "canonical agent identity",
        "full SHA-256",
        "replay and double-claim prevention",
        "non-loopback public API",
        "public claimability runtime activation",
        "wallet withdrawal",
        "wallet transfer",
        "wallet spend",
        "ECU minting",
        "ILC settlement or withdrawal runtime activation",
        "public P2P exposure",
        "v0.2 signing",
    ):
        assert phrase in spec


def test_phase_1270_graph_delta_is_recorded() -> None:
    spec = _read(SPEC_PATH)
    walkthrough = _read(WALKTHROUGH_PATH)
    status = _read(STATUS_PATH)

    expected = (
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_gap13_claimability_conversion_sweeper_preflight_1270_v0.1.md -> ecu/ilc/public_rc",
        "graph_delta=support_tests_added:tests/test_phase_1270_gap13_claimability_conversion_sweeper_preflight.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1270_gap13_claimability_conversion_sweeper_preflight_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in spec
        assert graph_delta in walkthrough
        assert graph_delta in status


def test_phase_1270_canonical_json_export_still_deterministic_for_wallet_refs() -> None:
    wallet_store = _WalletStore()
    lifecycle = EcuIlcLifecycleRuntime(
        wallet_store=wallet_store,
        ecu_runtime=_EcuRuntime(),
    )
    lifecycle.commit_settled_epoch(
        agent_id="agent:alpha",
        epoch_id="epoch:0004",
        reward_delta_ilc="1.25",
    )
    wallet_runtime = PublicWalletRuntime(
        wallet_store=wallet_store,
        lifecycle_runtime=lifecycle,
    )
    exported = wallet_runtime.wallet_export(agent_id="agent:alpha")
    encoded = json.dumps(exported, allow_nan=False, separators=(",", ":"), sort_keys=True)

    assert json.loads(encoded) == exported
    assert exported["data"]["settled_runtime_root_ref"].startswith("wallet_state_sha256:")
    assert exported["data"]["latest_balance_receipt_ref"].startswith("balance_receipt_sha256:")
