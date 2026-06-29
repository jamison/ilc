# Fix-H2: Multi-Model Endorsement, GAIA-X Adapter, and EU Sovereign Harness Recipe

**Prompt draft only:** This file is not an executable Antigravity phase prompt.
It is intentionally stored under `docs/specs/` until a valid sequence-lock slot,
phase number, filename, and `tools/validate_phase_prompt.py` pass exist.

**Phase:** TBD (pending sequence lock; fix-h2 designation)
**Window:** 1565–1575 (Block 6) or successor window
**Date:** 2026-06-29
**Status:** prompt draft — not executable; requires Fix-H1 complete after
sequence-lock assignment
**Owner lane:** Codex (implementation)
**Sensitivity:** NON-SENSITIVE
**Whitepaper reference:** E.12.4 (multi-model-endorsement), E.12.7 (EU sovereign extension)
**Forward plan reference:** docs/specs/ilc_harness_sidecar_forward_planning_v0.1.md §3

**Gap-register reference:** E.12 describes the target sovereign and multi-model
endorsement architecture. Implementation gaps are tracked in
`docs/specs/ilc_whitepaper_to_implementation_gap_register_v0.1.md`. This draft
implements only local/default-off harness machinery and must not claim GAIA-X
compliance, public serving, public-RC activation, or production jury
independence.

---

## §0a — Known-Token Audit

### Input tokens (must exist — Fix-H1 outputs become Fix-H2 inputs)

| Token | Path | Source |
|-------|------|--------|
| `ModelRouter` / `RouterRequest` / `RouterResult` | `ilc_core/harness/model_router.py` | Fix-H1 output |
| `EndpointRecord.arch_class` | `ilc_core/harness/model_router.py` | Fix-H1 output |
| `EndpointRecord.provider_id` | `ilc_core/harness/model_router.py` | Fix-H1 output |
| `OpenAICompatAdapter` | `ilc_core/harness/adapters/openai_compat.py` | Fix-H1 output |
| `ComplianceCaptureRecipe` | `ilc_core/harness/recipes/compliance_capture.py` | Fix-H1 output |
| `CoAttestationReceipt` | `ilc_core/harness/co_attestation_receipt.py` | Existing |
| `build_co_attestation_receipt` | `ilc_core/harness/co_attestation_receipt.py` | Existing |
| `LocalNodeSnapshot` | `ilc_core/harness/local_node_capture.py` | Existing |
| `LocalImmutableStore` | `ilc_core/harness/local_immutable_store.py` | Existing |
| `MODEL_ROUTER_VERSION` | `ilc_core/harness/model_router.py` | Fix-H1 output |

### Output tokens (must NOT exist before execution — new files)

| Token | Path | Why new |
|-------|------|---------|
| `MultiModelEndorsementOrchestrator` | `ilc_core/harness/multi_model_endorsement.py` | New orchestration module |
| `EndorsementResult` | `ilc_core/harness/multi_model_endorsement.py` | New dataclass |
| `GaiaXAdapter` | `ilc_core/harness/adapters/gaia_x.py` | New adapter |
| `GaiaXAttestationFields` | `ilc_core/harness/adapters/gaia_x.py` | New dataclass |
| `SovereignClusterAttestationGate` | `ilc_core/harness/sovereign_cluster_attestation.py` | New gate module |
| `SovereignClusterAttestationResult` | `ilc_core/harness/sovereign_cluster_attestation.py` | New dataclass |
| `MultiModelEndorsementRecipe` | `ilc_core/harness/recipes/multi_model_endorsement.py` | New recipe |
| `EUSovereignHarnessRecipe` | `ilc_core/harness/recipes/eu_sovereign_harness.py` | New recipe |
| `MULTI_MODEL_ENDORSEMENT_VERSION` | `ilc_core/harness/multi_model_endorsement.py` | Version token |
| `GAIA_X_ADAPTER_VERSION` | `ilc_core/harness/adapters/gaia_x.py` | Version token |

### Canonical term bindings

| Term used in this phase | Canonical meaning | Do NOT use to mean |
|-------------------------|------------------|--------------------|
| "node" | Graph Node (content-addressed epistemic object) | serving peer, network node |
| "endorsement" | `CoAttestationReceipt` — multi-signature proof of output agreement | jury verdict or protocol consensus |
| "sovereign cluster" | A GAIA-X certified national sovereign AI cluster identified by `national_operator_id` (ISO 3166-1) | any generic cluster or Fiedler partition |
| "layer4 independence" | Representational architecture independence (E.11.9.3) — at least 1 world_model arch class | L4 TCP/IP network layer |
| "divergence" | Hash mismatch between model outputs in endorsement orchestration — not an error, an epistemic signal | protocol fork or consensus failure |

---

## §0b — Concept-Discovery Search

Codex must run before committing:

1. `grep -r "MODEL_ROUTER_VERSION\|model_router_fix_h1" ilc_core/harness/` — confirm Fix-H1 is committed and version token present
2. `grep -r "GaiaX\|gaia_x\|gaia-x" ilc_core/` — confirm no prior GAIA-X adapter exists
3. `grep -r "MultiModelEndorsement\|multi_model_endorsement" ilc_core/` — confirm no prior module
4. `grep -r "SovereignCluster\|sovereign_cluster" ilc_core/` — confirm no prior module
5. `grep -r "national_operator_id\|pool_custody" ilc_core/` — check if any prior pool custody concept exists
6. `grep -r "arch_class\|world_model\|jepa" ilc_core/harness/` — confirm Fix-H1 arch_class field is present on EndpointRecord

### Pre-execution claim table

| Claim | File:line to verify | Expected result |
|-------|---------------------|-----------------|
| `EndpointRecord.arch_class` field exists on Fix-H1 output | `ilc_core/harness/model_router.py` | field: str with values transformer/world_model/hybrid/unknown |
| `build_co_attestation_receipt` accepts list of `{agent_id, signature}` | `ilc_core/harness/co_attestation_receipt.py:31` | function accepts attestation_signatures list |
| `CoAttestationReceipt.receipt_sha256` is a SHA-256 hex string | `ilc_core/harness/co_attestation_receipt.py:28` | field present |
| `OpenAICompatAdapter` exists from Fix-H1 | `ilc_core/harness/adapters/openai_compat.py` | file present |
| Compliance-capture recipe registered in sidecar_cli.py | `ilc_core/cli/sidecar_cli.py` | `"compliance-capture"` in `_RECIPES` |

---

## §0c — Contradiction and Non-Claim Search

1. `grep -r "GAIA.X.*not.*authorized\|gaia_x.*blocked\|gaia_x.*deferred" docs/` — any block on GAIA-X work?
2. `grep -r "eu.*sovereign.*deferred\|sovereign.*harness.*blocked" docs/` — any deferred flag?
3. `grep -r "multi.model.*not.*authorized\|co_attest.*blocked" docs/adr/` — any ADR blocking?
4. Check `docs/PLANNING_INDEX.md` for any conflict with active window

**Known non-authorizations carried forward:**
- `IDLE_CAPACITY_SCHEDULER_NOT_ACTIVATED = True` — must remain True in Fix-H2
- `PUBLIC_RC_EXCLUDE` headers — must remain on all harness modules in Fix-H2
- No ECU credit minting in Fix-H2

---

## §0d — Source Expansion

1. Direct-read `ilc_core/harness/co_attestation_receipt.py` in full — understand the exact `build_co_attestation_receipt` API before building the orchestrator over it
2. Direct-read `ilc_core/harness/model_router.py` (Fix-H1 output) in full — confirm `RouterRequest.exclude_provider_ids` and `EndpointRecord.arch_class` shape exactly
3. Direct-read `ilc_core/harness/adapters/openai_compat.py` (Fix-H1 output) — use as template for GAIA-X adapter extension pattern
4. Direct-read E.11.9.3 in whitepaper for the four-layer independence formal definition this phase must implement at the harness level

**If MemPalace is used, direct-read every returned path.**

---

## 1. Scope

Fix-H2 delivers:

### 1.1 Multi-Model Endorsement Orchestrator

**File:** `ilc_core/harness/multi_model_endorsement.py`

The orchestrator executes N model calls with provider diversity enforcement, compares content
hashes, and builds a `CoAttestationReceipt`:

```python
MULTI_MODEL_ENDORSEMENT_VERSION = "multi_model_endorsement_fix_h2.v0.1"

@dataclass(frozen=True)
class EndorsementResult:
    consensus_sha256: str | None    # None if no threshold was reached
    receipt: CoAttestationReceipt | None
    per_model_captures: tuple[LocalNodeSnapshot, ...]
    agreeing_models: tuple[str, ...]   # agent_ids that agreed on consensus_sha256
    divergent_models: tuple[str, ...]  # agent_ids that disagreed
    layer4_satisfied: bool
    consensus_threshold_met: bool
    endorsement_version: str = MULTI_MODEL_ENDORSEMENT_VERSION
```

**Hash agreement protocol:**
1. Run N model calls via `model_router.route()` with monotonically growing `exclude_provider_ids`
2. Capture each output via `LocalNodeCapture.capture()` → `LocalNodeSnapshot.sha256`
3. Find the modal SHA-256 value (most common hash): `consensus_sha256`
4. Split models into `agreeing_models` (match consensus) and `divergent_models` (differ)
5. If `len(agreeing_models) >= threshold`: build `CoAttestationReceipt` over `consensus_sha256`
6. If `layer4_required` and no agreeing model has `arch_class ∈ {world_model, hybrid}`:
   → set `layer4_satisfied = False`; recipe raises `ValueError("endorsement_layer4_not_satisfied")`

**Divergence is not an error:** A divergence in model outputs is logged to the `LocalImmutableStore`
as an `endorsement_divergence_event` record. This is epistemic signal — models disagree on facts —
and the harness preserves it rather than hiding it. An operator can inspect the ledger to see which
models disagreed and on what content.

### 1.2 GAIA-X Endpoint Adapter

**File:** `ilc_core/harness/adapters/gaia_x.py`

Extends `OpenAICompatAdapter`. The GAIA-X adapter reads three additional response headers and
attaches them to the provider usage record:

```python
GAIA_X_ADAPTER_VERSION = "gaia_x_adapter_fix_h2.v0.1"

GAIA_X_COMPLIANCE_HEADER     = "x-gaia-x-compliance-level"     # basic|substantial|high
GAIA_X_NATIONAL_OP_HEADER    = "x-gaia-x-national-operator-id"  # ISO 3166-1 alpha-2
GAIA_X_POOL_CUSTODY_HEADER   = "x-gaia-x-pool-custody-type"     # self|third_party:<id>

@dataclass(frozen=True)
class GaiaXAttestationFields:
    compliance_level: str               # "basic"|"substantial"|"high"|"unknown"
    national_operator_id: str           # e.g. "DE", "FR", "PL", or ""
    pool_custody_attestation: str       # "self"|"third_party:<national_id>_sovereign_ai_v<N>"|"unknown"
    gaia_x_certified: bool              # True only if all three headers present and valid
```

Absent headers → `gaia_x_certified=False`, all fields = `"unknown"`. Not an error. The GAIA-X
attestation fields propagate through the capture envelope as additional metadata on the
`LocalNodeSnapshot`, accessible to the sovereign cluster attestation gate.

**New endpoint config field:**

```yaml
endpoints:
  - id: fr-mistral-sovereign
    provider: mistral-sovereign-fr
    url: https://sovereign.mistral.ai/v1
    protocol: gaia-x-sovereign     # ← new protocol class, uses GaiaXAdapter
    capability_tags: [objective-review, summarization]
    arch_class: transformer
    gaia_x_national_operator_id: FR  # static config if headers are not present
```

### 1.3 Sovereign Cluster Attestation Gate

**File:** `ilc_core/harness/sovereign_cluster_attestation.py`

Verifies that an endorsement set satisfies the EU multi-level diversity requirements from
E.11.9.6 before committing the result to the immutable store or the protocol graph:

```python
@dataclass(frozen=True)
class SovereignClusterAttestationResult:
    passed: bool
    national_clusters_present: frozenset[str]   # set of national_operator_ids
    self_custody_count: int
    layer4_present: bool
    failure_reason: str | None

def verify_sovereign_cluster_attestation(
    endorsement_result: EndorsementResult,
    gaia_x_fields_per_model: dict[str, GaiaXAttestationFields],
    *,
    min_national_clusters: int = 2,
    min_self_custody: int = 1,
    layer4_required: bool = False,
) -> SovereignClusterAttestationResult:
    national_clusters = {
        f.national_operator_id
        for f in gaia_x_fields_per_model.values()
        if f.national_operator_id != ""
    }
    self_custody_count = sum(
        1 for f in gaia_x_fields_per_model.values()
        if f.pool_custody_attestation == "self"
    )
    layer4_present = endorsement_result.layer4_satisfied

    if len(national_clusters) < min_national_clusters:
        return SovereignClusterAttestationResult(
            passed=False,
            national_clusters_present=frozenset(national_clusters),
            self_custody_count=self_custody_count,
            layer4_present=layer4_present,
            failure_reason=f"sovereign_cluster_min_national_clusters_not_met:"
                           f"got {len(national_clusters)},required {min_national_clusters}"
        )
    if self_custody_count < min_self_custody:
        return SovereignClusterAttestationResult(
            passed=False, ...,
            failure_reason="sovereign_cluster_self_custody_floor_not_met"
        )
    if layer4_required and not layer4_present:
        return SovereignClusterAttestationResult(
            passed=False, ...,
            failure_reason="sovereign_cluster_layer4_independence_not_met"
        )
    return SovereignClusterAttestationResult(passed=True, ...)
```

### 1.4 Two New Recipes

**`multi-model-endorsement`** (`ilc_core/harness/recipes/multi_model_endorsement.py`):

```
Pipeline:  consent-gate →
           model-router(×N, exclude_provider_ids growing) →
           provider-adapter(×N) →
           capture-node(×N) →
           [hash agreement protocol] →
           co-attest(t-of-N) →
           immutable-store

CLI:
  ilc sidecar multi-model-endorsement run \
    --subject-id <id> \
    --models 3 \
    --threshold 2 \
    --layer4-independence \
    --prompt-file <path>
```

**`eu-sovereign-harness`** (`ilc_core/harness/recipes/eu_sovereign_harness.py`):

Extends `multi-model-endorsement` with GAIA-X adapter class enforcement and sovereign cluster
attestation gate:

```
Pipeline:  same as multi-model-endorsement PLUS:
           gaia-x-attestation-read (per model response) →
           sovereign-cluster-gate (before receipt commit)

CLI:
  ilc sidecar eu-sovereign-harness run \
    --subject-id <id> \
    --models 3 \
    --threshold 2 \
    --min-national-clusters 2 \
    --layer4-independence \
    --prompt-file <path>
```

### 1.5 sidecar_cli.py Extension

Register both new recipes in `_RECIPES` dict:

```python
"multi-model-endorsement": {
    "recipe_id": "multi-model-endorsement",
    "description": (
        "Run N models on same input; require t-of-N hash agreement. "
        "Produces CoAttestationReceipt. Optional --layer4-independence "
        "enforces world-model architecture in endorsement set (E.11.9.3)."
    ),
    "modules": (
        "consent_gate", "model_router", "provider_adapter",
        "capture_node", "multi_model_endorsement", "co_attest",
        "immutable_store",
    ),
    "status": "available",
},
"eu-sovereign-harness": {
    "recipe_id": "eu-sovereign-harness",
    "description": (
        "Multi-model endorsement with GAIA-X endpoint class and EU "
        "sovereign cluster attestation (E.12.7). Enforces national cluster "
        "diversity and pool custody attestation for EU AI Act compliance."
    ),
    "modules": (
        "consent_gate", "model_router", "gaia_x_adapter",
        "provider_adapter", "capture_node", "multi_model_endorsement",
        "co_attest", "sovereign_cluster_attestation", "immutable_store",
    ),
    "status": "available",
},
```

## 2. Security Requirements

- All adapter calls: `timeout=X` mandatory (Security Standard §6); default 30 seconds
- `gaia_x_certified=False` on absent headers is graceful — must NOT raise; must NOT assume certification
- GAIA-X compliance level values other than `basic|substantial|high` → log warning, set `compliance_level="unknown"`, continue
- Pool custody attestation value `"self"` must only be set if `pool_custody_attestation` header explicitly says `"self"` — no inference
- Endorsement divergence must be written to immutable store BEFORE raising any threshold error — the record of disagreement is itself valuable

## 3. Test Gate for Fix-H2

- `test_endorsement_2of3_consensus_produces_receipt()`
- `test_endorsement_divergence_logged_to_store()`
- `test_endorsement_threshold_not_met_no_receipt()`
- `test_endorsement_layer4_required_fails_all_transformer()`
- `test_endorsement_layer4_satisfied_with_world_model()`
- `test_endorsement_provider_diversity_excludes_used_providers()`
- `test_gaia_x_adapter_reads_all_three_headers()`
- `test_gaia_x_adapter_absent_headers_sets_unknown_gracefully()`
- `test_gaia_x_adapter_invalid_compliance_level_logs_warning()`
- `test_sovereign_cluster_attestation_passes_two_clusters()`
- `test_sovereign_cluster_attestation_fails_single_cluster()`
- `test_sovereign_cluster_attestation_fails_no_self_custody()`
- `test_sovereign_cluster_attestation_fails_layer4_not_met()`
- `test_eu_sovereign_harness_recipe_end_to_end_mocked()`
- `test_cli_multi_model_endorsement_flags()`
- `test_cli_eu_sovereign_harness_flags()`
- ≥ 3 regression tests against Fix-H1 test suite

## 4. Walkthrough Requirements

- Summary table of new files with line counts
- Confirm endorsement divergence is written to store even when threshold fails
- Confirm GAIA-X absent headers are graceful (test evidence)
- Confirm `SovereignClusterAttestationResult.failure_reason` is machine-readable token
- `graph_delta=load_bearing_artifact_added:ilc_core/harness/multi_model_endorsement.py -> harness_sidecar_module_design`
- `graph_delta=load_bearing_artifact_added:ilc_core/harness/sovereign_cluster_attestation.py -> harness_sidecar_module_design`
- `graph_delta=support_only:` for recipe files and GAIA-X adapter

## 5. Non-Authorizations

This phase does NOT:
- Activate `IDLE_CAPACITY_SCHEDULER_NOT_ACTIVATED`
- Remove `PUBLIC_RC_EXCLUDE` from any harness module
- Implement the `ilc-submit` recipe (Fix-H3)
- Implement `werner-credit` (Fix-H3, depends on Fix2b-3)
- Write to the ILC protocol graph or D2D gossip layer
- Create CDL, ADR, or governance document
- Require a GO token (NON-SENSITIVE)
