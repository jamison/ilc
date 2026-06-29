# ILC Harness Sidecar — Forward Planning Specification

**Version:** 0.1
**Date:** 2026-06-29
**Author:** Genesis Agent + Sonnet
**Status:** Forward planning — phase numbers TBD pending sequence lock. Not an
executable phase prompt and not public-RC activation authority.
**Whitepaper reference:** Section E.12 (`docs/specs/ilc_whitepaper_satoshi_mirror_v0.1.md`).
Implementation gaps are tracked separately in
`docs/specs/ilc_whitepaper_to_implementation_gap_register_v0.1.md`.

---

## 0. Purpose and Scope

This document specifies the forward planning for the ILC Harness Sidecar layer: a composable,
recipe-driven CLI integration layer that solves the "last mile" AI deployment problem for
enterprises, governments, and operators who lack AI engineering capability but need auditable,
compliance-ready, economically-accountable AI output pipelines.

The harness layer is explicitly designed to:

1. Operate independently of the ILC protocol graph (Stage 1: audit only)
2. Optionally coordinate multiple model providers for multi-model endorsement (Stage 2)
3. Submit quality-gated work to the ILC protocol graph to earn ECU (Stage 3)
4. Adapt to EU Sovereign AI infrastructure via GAIA-X endpoint class and sovereign cluster
   attestation (Stage 4)

**What already exists (`ilc_core/harness/`, currently `PUBLIC_RC_EXCLUDE`):**

| Module | File | Status |
|--------|------|--------|
| `consent-gate` | `harness/consent_gate.py` | EXISTS, needs CLI surface |
| `capture-node` | `harness/local_node_capture.py` | EXISTS, needs CLI surface |
| `immutable-store` | `harness/local_immutable_store.py` | EXISTS, needs export CLI |
| `provider-adapter` | `harness/provider_usage_adapter.py` | EXISTS, needs config format |
| `idle-scheduler` | `harness/idle_capacity_scheduler.py` | EXISTS, needs recipe wiring |
| `co-attest` | `harness/co_attestation_receipt.py` | EXISTS, needs orchestration wrapper |
| `agent-id` | `identity/agent_id_runtime.py` | EXISTS, needs harness wrapper |
| `sybil-guard` | `identity/sybil_resistance_runtime.py` | EXISTS, needs harness wrapper |
| `novelty-check` | `epistemic/novelty_check_runtime.py` | EXISTS, needs harness wrapper |
| `review-lane` | `epistemic/review_lane_admission_runtime.py` | EXISTS, needs harness wrapper |
| `popperian-gate` | `consensus/diversity_floor_runtime.py` | EXISTS, needs harness wrapper |
| `node-submit` | `epistemic/node_submission_runtime.py` | EXISTS, production gate |
| `reputation-feed` | `reputation/temporal_decay_runtime.py` | EXISTS, needs read CLI |
| `ecu-balance` | `ledger/ecu_active_layer_runtime.py` | EXISTS, needs read CLI |

**What does NOT exist and must be built:**

| Module | Description | Blocking dependency |
|--------|-------------|---------------------|
| `model-router` | Provider-agnostic inference router | Fix-H1 |
| `werner-credit` | Werner flow-governor ECU credit bridge | Fix2b-3 (rust bridge) |
| GAIA-X adapter | EU sovereign AI endpoint class | Fix-H2 |
| Sovereign cluster attestation | Multi-level diversity gate | Fix-H2 |
| CLI surfaces for all existing modules | `ilc sidecar <recipe>` commands | Fix-H1 |
| Recipe YAML config format | Declarative endpoint/consent config | Fix-H1 |

**Prompt draft status:** the Fix-H1/Fix-H2 drafts are preserved as planning
drafts at:

- `docs/specs/ilc_harness_sidecar_fix_h1_model_router_prompt_draft_v0.1.md`
- `docs/specs/ilc_harness_sidecar_fix_h2_multi_model_endorsement_prompt_draft_v0.1.md`

They are intentionally not in `docs/antigravity_tasks/` until a valid phase
number, sequence-lock slot, and prompt validation pass exist.

---

## 1. Phase Architecture

Three phases are required. They are sequenced by dependency:

```
  Fix-H1 (NON-SENSITIVE)
    model-router module
    CLI surfaces for all 12 existing harness modules
    Recipe YAML config format
    compliance-capture recipe end-to-end
    ilc sidecar <recipe> command surface
    Tests: ≥ 20 unit tests across new and wired modules
    Gate: ilc sidecar compliance-capture run works with
          at least 2 provider classes (openai-compat + ollama)

  Fix-H2 (NON-SENSITIVE)
    multi-model-endorsement recipe (depends on model-router)
    co-attest orchestration wrapper (multi-call)
    GAIA-X endpoint adapter
    Sovereign cluster attestation module
    EU harness extension recipe
    Tests: ≥ 15 additional tests
    Gate: multi-model-endorsement run with 2-of-3 threshold
          and --layer4-independence passes with mocked endpoints

  Fix-H3 (SENSITIVE — touches protocol submission path)
    ilc-submit recipe (full pipeline to protocol graph)
    werner-credit module (depends on Fix2b-3 rust bridge)
    idle-scheduler recipe wiring
    ecu-balance + reputation-feed CLI surfaces
    Tests: ≥ 10 additional tests; regression against all Fix-H1/H2 tests
    Gate: ilc sidecar ilc-submit run (testnet) submits a node
          and returns a valid node CID
    Requires: human GO token (touches live protocol submission)
```

**Fix-H1 and Fix-H2 are independent of the protocol graph and may run before
Fix2b-3 only after they receive a valid sequence-lock slot.**
**Fix-H3 must wait for Fix2b-3 (rust bridge for ECU credit path) and requires explicit GO.**

---

## 2. Fix-H1 Detailed Scope

### 2.1 model-router Module

**File:** `ilc_core/harness/model_router.py`

**Core data structures:**

```python
@dataclass(frozen=True)
class EndpointRecord:
    endpoint_id: str
    provider_id: str
    endpoint_url: str
    protocol_class: str  # openai-compat | anthropic | huggingface | ollama | mcp | gaia-x-sovereign
    capability_tags: frozenset[str]
    arch_class: str      # transformer | world_model | hybrid | unknown
    budget_remaining: int | None   # from provider-adapter, updated live
    latency_p50_ms: Decimal        # observed; Decimal, never float

@dataclass(frozen=True)
class RouterRequest:
    capability: str
    budget_max_tokens: int
    layer4_independence_required: bool = False
    exclude_provider_ids: frozenset[str] = frozenset()
    min_budget_headroom: int = 0

@dataclass(frozen=True)
class RouterResult:
    endpoint: EndpointRecord
    estimated_cost_tokens: int
    selection_reason: str   # e.g. "lowest_latency_eligible"
```

**Routing algorithm:**

```python
def route(self, request: RouterRequest) -> RouterResult:
    eligible = [
        e for e in self._endpoints
        if (request.capability in e.capability_tags
            and e.provider_id not in request.exclude_provider_ids
            and (e.budget_remaining is None
                 or e.budget_remaining >= request.min_budget_headroom)
            and (not request.layer4_independence_required
                 or e.arch_class in {"world_model", "hybrid"}))
    ]
    if not eligible:
        raise ValueError("model_router_no_eligible_endpoint")
    return min(eligible, key=lambda e: e.latency_p50_ms)
```

**Endpoint config format (YAML):**

```yaml
# ilc-harness-endpoints.yaml
endpoints:
  - id: mistral-local
    provider: mistral-local
    url: http://localhost:11434/v1
    protocol: openai-compat
    capability_tags: [objective-review, summarization, code-audit]
    arch_class: transformer
  - id: anthropic-claude
    provider: anthropic
    url: https://api.anthropic.com
    protocol: anthropic
    capability_tags: [objective-review, reasoning, refutation]
    arch_class: transformer
  - id: ami-jepa-endpoint
    provider: ami-labs
    url: https://api.ami.ai/v1
    protocol: openai-compat
    capability_tags: [objective-review, physical-reasoning]
    arch_class: world_model
```

**Supported protocol adapter classes (Fix-H1 scope):**

| Protocol class | Adapter | Key normalization |
|----------------|---------|-------------------|
| `openai-compat` | `OpenAICompatAdapter` | Standard Chat Completions API |
| `anthropic` | `AnthropicAdapter` | Messages API; maps to chat format |
| `ollama-native` | `OllamaAdapter` | `/api/generate`; streams normalized |
| `mcp-tool` | `MCPToolAdapter` | MCP tool call → text result |

**MCP adapter note:** The MCP adapter wraps any MCP tool server as an inference endpoint for
harness purposes. The tool's `content` return value is treated as the model output Y. This allows
operators to use MCP tools (filesystem readers, search tools, code executors) as model-router
endpoints, enabling hybrid harnesses where some "model calls" are actually deterministic tool
executions — still captured, consent-gated, and attestation-eligible.

### 2.2 CLI Surface Design

All harness sidecars follow the ILC CLI naming convention (CLAUDE.md):

```
  ilc sidecar list                          # lists all available sidecars
  ilc sidecar <recipe-id> --help            # shows recipe flags
  ilc sidecar <recipe-id> run [flags]       # executes recipe
  ilc sidecar <recipe-id> config validate   # validates endpoint YAML
  ilc sidecar <recipe-id> config show       # shows active config
```

**compliance-capture flags:**

```
  --subject-id     STR    Data subject identifier (for consent gate)
  --purpose        STR    Processing purpose (for consent gate)
  --capability     STR    Capability tag for model-router
  --budget-max     INT    Max tokens for this call
  --prompt-file    PATH   Input prompt file (or - for stdin)
  --endpoint-config PATH  Endpoint YAML (default: ./ilc-harness-endpoints.yaml)
  --output         PATH   Output file for ledger entry (default: stdout NDJSON)
  --dry-run               Validate config and consent without calling model
```

### 2.3 Recipe YAML Config Format

```yaml
# ilc-compliance-capture.yaml
recipe: compliance-capture
version: "1.0"
consent:
  default_purpose: "ai-output-audit"
  allowed_subjects: ["*"]   # or list of specific subject IDs
capture:
  max_fields: 64
  include_prompt_hash: true  # SHA-256 of input in ledger record
provider:
  capability: objective-review
  budget_max_tokens: 4096
  min_budget_headroom: 512
store:
  path: ./ilc-audit-ledger.ndjson
  export_format: ndjson-signed
endpoints_config: ./ilc-harness-endpoints.yaml
```

### 2.4 Test Gate for Fix-H1

- `test_model_router_eligible_set_empty_raises()`
- `test_model_router_layer4_excludes_transformer()`
- `test_model_router_provider_exclusion_chain()`
- `test_model_router_latency_selection()`
- `test_openai_compat_adapter_normalizes_response()`
- `test_anthropic_adapter_normalizes_response()`
- `test_ollama_adapter_normalizes_response()`
- `test_mcp_tool_adapter_wraps_tool_result()`
- `test_compliance_capture_recipe_end_to_end_mocked()`
- `test_compliance_capture_consent_denied_raises()`
- `test_compliance_capture_float_in_output_raises()`
- `test_recipe_yaml_validates_endpoint_config()`
- `test_capture_node_idempotent_sha256()`
- `test_immutable_store_export_ndjson()`
- `test_cli_sidecar_list_shows_compliance_capture()`
- `test_cli_compliance_capture_dry_run()`
- `test_cli_help_three_level_hierarchy()`
- ≥ 3 additional edge cases identified during implementation

---

## 3. Fix-H2 Detailed Scope

### 3.1 Multi-Model Endorsement Orchestrator

**File:** `ilc_core/harness/multi_model_endorsement.py`

The endorsement orchestrator wraps the model-router to call N distinct providers in sequence,
capturing each output, verifying content-hash agreement, and building the CoAttestationReceipt:

```python
@dataclass(frozen=True)
class EndorsementResult:
    consensus_sha256: str          # all signers agreed on this hash
    receipt: CoAttestationReceipt  # multi-signature receipt
    per_model_captures: tuple[LocalNodeSnapshot, ...]
    layer4_satisfied: bool         # at least 1 world_model signer
    divergent_models: tuple[str, ...]  # models that disagreed (if any)
    consensus_threshold_met: bool

def run_endorsement(
    prompt: str,
    *,
    n_models: int,
    threshold: int,            # must be ≤ n_models
    layer4_required: bool,
    router: ModelRouter,
    consent_gate: ConsentGate,
    store: LocalImmutableStore,
) -> EndorsementResult:
    ...
```

**Hash disagreement handling:** If two models return outputs with different SHA-256 hashes, the
endorsement logs the divergence as a `divergent_models` field in the result. A divergence on
factual content is itself an epistemic signal — it is not an error, but it means the
`consensus_threshold_met` flag will be False if fewer than `threshold` models agree.

### 3.2 GAIA-X Endpoint Adapter

**File:** `ilc_core/harness/gaia_x_adapter.py`

Extends `OpenAICompatAdapter` with GAIA-X compliance header reading:

```python
GAIA_X_COMPLIANCE_HEADER     = "x-gaia-x-compliance-level"
GAIA_X_NATIONAL_OPERATOR_HEADER = "x-gaia-x-national-operator-id"
GAIA_X_POOL_CUSTODY_HEADER   = "x-gaia-x-pool-custody-type"

@dataclass(frozen=True)
class GaiaXAttestationFields:
    compliance_level: str          # basic | substantial | high
    national_operator_id: str      # ISO 3166-1 alpha-2
    pool_custody_attestation: str  # "third_party:<national_id>_sovereign_ai_v<N>"
    gaia_x_certified: bool
```

If GAIA-X headers are absent, the adapter sets `gaia_x_certified=False` and
`pool_custody_attestation="unknown"`. This is not an error — non-GAIA-X endpoints
can still participate; they simply do not contribute to the sovereign cluster attestation gate.

### 3.3 Sovereign Cluster Attestation Module

**File:** `ilc_core/harness/sovereign_cluster_attestation.py`

```python
@dataclass(frozen=True)
class SovereignClusterAttestationResult:
    passed: bool
    national_clusters_present: frozenset[str]
    self_custody_count: int
    layer4_present: bool
    failure_reason: str | None

def verify_sovereign_cluster_attestation(
    endorsement_result: EndorsementResult,
    *,
    min_national_clusters: int = 2,
    min_self_custody: int = 1,
    layer4_required: bool = False,
) -> SovereignClusterAttestationResult:
    ...
```

### 3.4 Test Gate for Fix-H2

- `test_multi_model_endorsement_2of3_consensus()`
- `test_multi_model_endorsement_divergence_logged()`
- `test_multi_model_endorsement_layer4_enforced()`
- `test_multi_model_endorsement_provider_diversity()`
- `test_gaia_x_adapter_reads_compliance_headers()`
- `test_gaia_x_adapter_absent_headers_graceful()`
- `test_sovereign_cluster_attestation_passes()`
- `test_sovereign_cluster_attestation_fails_single_cluster()`
- `test_sovereign_cluster_attestation_fails_no_self_custody()`
- `test_cli_multi_model_endorsement_2of3()`
- `test_cli_multi_model_endorsement_layer4()`
- `test_eu_harness_recipe_end_to_end_mocked()`
- ≥ 3 additional edge cases

---

## 4. Fix-H3 Detailed Scope (SENSITIVE — requires GO token)

### 4.1 ilc-submit Recipe Wiring

Wires the full submission pipeline using existing epistemic modules that currently have no
harness-layer CLI surface:

- `novelty-check`: wrapper around `novelty_check_runtime.py`
- `review-lane`: wrapper around `review_lane_admission_runtime.py`
- `popperian-gate`: wrapper around CDL-V7 falsifiability runtime
- `node-submit`: wrapper around `node_submission_runtime.py` + D2D gossip

Each wrapper module adds:
- A harness-layer input type adapter (Ŷ* → module-specific input format)
- A harness-layer output type adapter (module output → Ŷ* or Σ)
- CLI flag surface
- Error translation to machine-readable token strings

### 4.2 werner-credit Module

**File:** `ilc_core/harness/werner_credit.py`

**Dependency:** Fix2b-3 (Python → Rust AttributionBatch / ECU credit ingestion bridge) must
exist before this module can mint real ECU credit. Until then, `werner-credit` operates in
`dry_run=True` mode, computing η_W (Werner efficiency ratio) without submitting credit claims.

```python
WERNER_CREDIT_NOT_ACTIVATED = True  # until Fix2b-3 bridge is live

@dataclass(frozen=True)
class WernerCreditRecord:
    task_id: str
    agent_id: str
    epoch: int
    provider_cost_tokens: int
    ecu_earned: Decimal            # Decimal, never float
    efficiency_ratio: Decimal      # ecu_earned / cost_proxy
    dry_run: bool = True           # True until Fix2b-3

def record_werner_credit(
    task_result: MaintenanceTaskResult,
    *,
    agent_id: str,
    epoch: int,
    provider_snapshot: ProviderBudgetSnapshot,
    dry_run: bool = True,
) -> WernerCreditRecord:
    ...
```

### 4.3 Test Gate for Fix-H3

- `test_ilc_submit_novelty_check_rejects_restatement()`
- `test_ilc_submit_popperian_gate_rejects_nonfalsifiable()`
- `test_ilc_submit_sybil_guard_blocks_failing_agent()`
- `test_ilc_submit_full_pipeline_mocked_network()`
- `test_ilc_submit_returns_node_cid()`
- `test_werner_credit_dry_run_computes_efficiency()`
- `test_werner_credit_decimal_not_float()`
- `test_idle_scheduler_routes_to_ilc_submit()`
- `test_ecu_balance_cli_reads_ledger()`
- `test_reputation_feed_cli_reads_decay_score()`
- ≥ 5 regression tests against all Fix-H1/H2 test cases
- **Integration gate (testnet):** `ilc sidecar ilc-submit run` submits to testnet
  and returns a valid 64-char hex node CID within 30 seconds

---

## 5. MCP Connectivity Design

Model Context Protocol (MCP) connectivity is supported in Fix-H1 via the `mcp-tool` endpoint
protocol class. The `MCPToolAdapter` implements the harness-layer normalization:

```
  MCP TOOL → HARNESS NORMALIZATION

  MCP tool call format:
    { "name": "<tool>", "arguments": { ... } }

  Harness sends via MCP client:
    tool_result = client.call_tool(name, arguments)

  Normalization:
    if tool_result.content is list:
        y = " ".join(item.text for item in tool_result.content
                     if hasattr(item, 'text'))
    else:
        y = str(tool_result.content)

  Token cost approximation (MCP has no standard token header):
    input_tokens  = len(json.dumps(arguments)) // 4   (approx)
    output_tokens = len(y) // 4                       (approx)
    cost_proxy    = Decimal("0")                       (unknown)
```

MCP tools that are useful as harness endpoints in the enterprise/government last-mile context:

| MCP tool class | Harness use case | Example |
|----------------|-----------------|---------|
| Filesystem reader | Document ingestion before inference | `@modelcontextprotocol/server-filesystem` |
| Web search | Live knowledge retrieval for review tasks | Brave Search MCP |
| Code executor | Automated test execution as review step | `@modelcontextprotocol/server-bash` |
| Database reader | Structured data retrieval for provenance | SQL MCP servers |
| EU regulatory DB | GAIA-X, AI Act compliance lookups | Custom EU regulatory MCP |

The MCP adapter allows a harness recipe to include a web-search tool call as a preliminary step
before model inference — the search results are captured as a `LocalNodeSnapshot` alongside the
inference output, providing provenance for the model's factual premises. This directly addresses
the last-mile governance requirement of documenting what information the AI had access to when
it produced its output.

---

## 6. Open Questions Requiring Resolution Before Implementation

1. **model-router latency measurement:** How is `latency_p50_ms` measured and updated?
   Options: (a) exponential moving average of observed call latencies (updated each call);
   (b) static from endpoint config; (c) periodic health-check ping. Recommend (a) for Fix-H1.

2. **Endorsement output hash when models diverge:** If models A and B return different text
   but encode the same semantic claim (paraphrase), their SHA-256 hashes will differ and the
   endorsement will record a divergence. Should the harness include an optional semantic
   similarity gate (cosine similarity of embeddings > θ) as an alternative to exact hash match?
   Recommend: exact hash match for Fix-H2 (simpler, more conservative); semantic gate deferred.

3. **GAIA-X header availability:** GAIA-X compliance headers may not be present on all
   sovereign AI endpoints immediately. The adapter must gracefully handle absent headers.
   Confirmed design: absent headers → `gaia_x_certified=False`, not an error.

4. **werner-credit activation gating:** `WERNER_CREDIT_NOT_ACTIVATED = True` must remain
   until Fix2b-3 is committed and the rust bridge is verified. The flag must not be flipped
   in Fix-H3 without a separate human GO token specifically for credit activation.

5. **Public RC inclusion of harness modules:** The harness modules are currently
   `PUBLIC_RC_EXCLUDE`. Fix-H1 completion is not sufficient to remove this
   exclusion from any module. Removal requires a later publication/activation
   gate that reviews public surface area, sidecar packaging, privacy, endpoint
   exposure, and non-authority-by-default behavior. The higher-sensitivity
   modules (`node-submit`, `werner-credit`) additionally require the J-008 /
   production-path authority chain and an explicit human GO.

---

## 7. Graph Delta

```text
graph_delta=load_bearing_artifact_added:docs/specs/ilc_harness_sidecar_forward_planning_v0.1.md -> harness_sidecar_module_design
```
