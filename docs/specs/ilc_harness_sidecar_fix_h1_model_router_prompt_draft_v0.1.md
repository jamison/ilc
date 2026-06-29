# Fix-H1: model-router Module, Harness CLI Surfaces, and compliance-capture Recipe

**Prompt draft only:** This file is not an executable Antigravity phase prompt.
It is intentionally stored under `docs/specs/` until a valid sequence-lock slot,
phase number, filename, and `tools/validate_phase_prompt.py` pass exist.

**Phase:** TBD (pending sequence lock; fix-h1 designation)
**Window:** 1565–1575 (Block 6) or successor window
**Date:** 2026-06-29
**Status:** prompt draft — not executable
**Owner lane:** Codex (implementation)
**Sensitivity:** NON-SENSITIVE
**Whitepaper reference:** E.12 (ilc_whitepaper_satoshi_mirror_v0.1.md)
**Forward plan reference:** docs/specs/ilc_harness_sidecar_forward_planning_v0.1.md

**Gap-register reference:** E.12 describes the target harness architecture.
Implementation gaps are tracked in
`docs/specs/ilc_whitepaper_to_implementation_gap_register_v0.1.md`. This phase
draft implements only local/default-off harness machinery and must not be used
to claim public-RC harness activation.

---

## §0a — Known-Token Audit

### Input tokens (must exist before execution)

| Token | Path | Verified by |
|-------|------|-------------|
| `ConsentGate` | `ilc_core/harness/consent_gate.py` | §0b search |
| `LocalNodeCapture` / `LocalNodeSnapshot` | `ilc_core/harness/local_node_capture.py` | §0b search |
| `LocalImmutableStore` | `ilc_core/harness/local_immutable_store.py` | §0b search |
| `ProviderUsageAdapter` / `ProviderBudgetSnapshot` | `ilc_core/harness/provider_usage_adapter.py` | §0b search |
| `CoAttestationReceipt` | `ilc_core/harness/co_attestation_receipt.py` | §0b search |
| `IdleCapacityScheduler` | `ilc_core/harness/idle_capacity_scheduler.py` | §0b search |
| `SIDECAR_CLI_VERSION` | `ilc_core/cli/sidecar_cli.py` | §0b search |
| `_EXTERNAL_SIDECARS` | `ilc_core/cli/sidecar_cli.py` | §0b search |
| `build_sidecar_registry_manifest` | `ilc_core/sidecars/registry_manifest.py` | §0b search |
| `PUBLIC_RC_EXCLUDE_PRIVATE_AGENTIC_HARNESS` | `ilc_core/harness/__init__.py` | §0b search |
| `canonical_json` / `reject_float` | `ilc_core/private_json_guardrails.py` | §0b search |
| `MAX_USAGE_RECORDS = 256` | `ilc_core/harness/provider_usage_adapter.py:11` | §0b search |
| `MAX_CAPTURE_FIELDS = 64` | `ilc_core/harness/local_node_capture.py:14` | §0b search |
| `IDLE_CAPACITY_SCHEDULER_NOT_ACTIVATED` | `ilc_core/harness/idle_capacity_scheduler.py:16` | §0b search |

### Output tokens (must NOT exist before execution — new files)

| Token | Path | Why new |
|-------|------|---------|
| `ModelRouter` | `ilc_core/harness/model_router.py` | New module — core of Fix-H1 |
| `EndpointRecord` | `ilc_core/harness/model_router.py` | New dataclass |
| `RouterRequest` | `ilc_core/harness/model_router.py` | New dataclass |
| `RouterResult` | `ilc_core/harness/model_router.py` | New dataclass |
| `OpenAICompatAdapter` | `ilc_core/harness/adapters/openai_compat.py` | New adapter module |
| `AnthropicAdapter` | `ilc_core/harness/adapters/anthropic.py` | New adapter module |
| `OllamaAdapter` | `ilc_core/harness/adapters/ollama.py` | New adapter module |
| `MCPToolAdapter` | `ilc_core/harness/adapters/mcp_tool.py` | New adapter module |
| `ComplianceCaptureRecipe` | `ilc_core/harness/recipes/compliance_capture.py` | New recipe module |
| `MODEL_ROUTER_VERSION` | `ilc_core/harness/model_router.py` | Version token |

### Canonical term bindings

| Term used in this phase | Canonical meaning | Do NOT use to mean |
|-------------------------|------------------|--------------------|
| "node" | Graph Node (content-addressed epistemic object) | serving peer, host, operator instance |
| "capture" | `LocalNodeSnapshot` — SHA-256-committed local artifact, `production_graph_write=False` | protocol graph write |
| "model" | AI inference model at a provider endpoint | ILC protocol object |
| "recipe" | Named composition of harness modules invokable via `ilc sidecar <recipe-id>` | protocol phase or CDL |
| "endpoint" | `EndpointRecord` — a registered provider URL with capability tags | ILC network peer |
| "protocol class" | The HTTP/API dialect the adapter normalizes (openai-compat, anthropic, etc.) | ILC protocol |

---

## §0b — Concept-Discovery Search

Codex must run these searches before committing any code:

1. `grep -r "PUBLIC_RC_EXCLUDE" ilc_core/harness/` — confirm current exclusion scope of all harness modules
2. `grep -r "sidecar_cli\|sidecar_registry" ilc_core/cli/` — confirm current sidecar CLI structure
3. `grep -r "ModelRouter\|model_router" ilc_core/` — confirm no prior model-router module exists
4. `grep -r "openai_compat\|anthropic\|ollama" ilc_core/harness/` — confirm no prior adapters exist
5. `grep -r "timeout" ilc_core/harness/` — check existing timeout handling in harness layer
6. `grep -r "ILC_CLI_NAMING\|kebab.case" CLAUDE.md` — confirm CLI naming convention

### Pre-execution claim table

| Claim | File:line to verify | Expected result |
|-------|---------------------|-----------------|
| `ConsentGate.require_allowed()` exists | `ilc_core/harness/consent_gate.py:84` | method present |
| `LocalNodeCapture.capture()` returns `LocalNodeSnapshot` | `ilc_core/harness/local_node_capture.py:38` | method present, returns snapshot |
| `ProviderUsageAdapter.record_usage()` enforces `MAX_RECORDS=256` cap | `ilc_core/harness/provider_usage_adapter.py:73-76` | cap check present |
| `sidecar_cli.py` `_RECIPES` dict exists and uses `recipe_id` key | `ilc_core/cli/sidecar_cli.py:14` | dict present |
| `harness/__init__.py` has `PUBLIC_RC_EXCLUDE` header | `ilc_core/harness/__init__.py:1-3` | header present |
| No float in `ProviderBudgetSnapshot.total_cost_proxy` (uses Decimal) | `ilc_core/harness/provider_usage_adapter.py:146` | `Decimal("0")` as sum start |

---

## §0c — Contradiction and Non-Claim Search

Search for these before any implementation:

1. `grep -r "model_router\|ModelRouter" docs/adr/` — any ADR blocking model-router?
2. `grep -r "harness.*not.*authorized\|harness.*deferred\|harness.*blocked" docs/` — check for deferred status
3. `grep -r "PUBLIC_RC_EXCLUDE_PRIVATE_AGENTIC_HARNESS" ilc_core/` — scope of current exclusion
4. `grep -r "IDLE_CAPACITY_SCHEDULER_NOT_ACTIVATED\|WERNER_CREDIT_NOT_ACTIVATED" ilc_core/harness/` — active NOT_ACTIVATED flags
5. Check `docs/PLANNING_INDEX.md` for any Fix-H or harness sidecar conflict with current window

**Known non-authorization:** `IDLE_CAPACITY_SCHEDULER_NOT_ACTIVATED = True` in `idle_capacity_scheduler.py` must remain True in Fix-H1. Do not flip this flag without a separate GO token. The idle-scheduler recipe wiring in Fix-H1 must wrap the scheduler in a read-only mode that uses the scheduler's task selection logic without activating credit minting.

---

## §0d — Source Expansion and Newly Discovered Tokens

For every relevant search hit: direct-read the source file. Specifically:

1. Direct-read `ilc_core/cli/sidecar_cli.py` in full — understand the current recipe registration pattern before adding to it
2. Direct-read `ilc_core/harness/local_node_capture.py` in full — understand the exact field structure of `LocalNodeSnapshot` before building CLI surfaces over it
3. Direct-read `ilc_core/harness/consent_gate.py` in full — understand `ConsentGate.from_fixture()` and how decisions are recorded
4. Direct-read `ilc_core/private_json_guardrails.py` — understand `canonical_json` and `reject_float` before using them in new modules
5. Direct-read `ilc_core/harness/__init__.py` — confirm the `PUBLIC_RC_EXCLUDE` scope before deciding which new files should carry the header

**If MemPalace is used, direct-read every returned path.**

---

## 1. Scope

Fix-H1 delivers:

1. **`ilc_core/harness/model_router.py`** — the `ModelRouter` class with `EndpointRecord`, `RouterRequest`, `RouterResult`; routing algorithm; Decimal-only latency and cost; `model_router_no_eligible_endpoint` error token
2. **`ilc_core/harness/adapters/`** — four adapter modules: `openai_compat.py`, `anthropic.py`, `ollama.py`, `mcp_tool.py`; each normalizes provider-specific HTTP/SDK calls to a common `(output_text: str, input_tokens: int, output_tokens: int, cost_proxy: Decimal)` tuple
3. **`ilc_core/harness/recipes/compliance_capture.py`** — `ComplianceCaptureRecipe` composing `ConsentGate → ModelRouter → ProviderUsageAdapter → LocalNodeCapture → LocalImmutableStore`
4. **CLI surface extensions to `ilc_core/cli/sidecar_cli.py`** — `compliance-capture` recipe registered in `_RECIPES`; `ilc sidecar compliance-capture run [flags]` command; `config validate` and `config show` subcommands; three-level `--help`
5. **Recipe YAML config format** — validated by `ilc_core/harness/config/recipe_config_loader.py`
6. **`tests/test_fix_h1_model_router_compliance_capture.py`** — ≥ 18 tests covering all new modules

## 2. Security Requirements (from CLAUDE.md)

- ALL cost and latency values must use `decimal.Decimal`, never Python `float`
- ALL HTTP calls from adapters must include `timeout=X` (mandatory socket timeout, Security Standard §6)
- ALL provider API keys must be read from environment variables, never from config files or code
- `tls_verify=False` is banned in all adapters (Security Standard §8)
- Remote response bodies must be read with a byte-count cap before parsing (Security Standard §10): `max_response_bytes = 4 * 1024 * 1024` (4MB default, configurable)
- New harness modules must carry `PUBLIC_RC_EXCLUDE` headers until Fix-H3 gate review

## 3. CLI Naming Requirements (from CLAUDE.md)

- All multi-word flags: kebab-case (`--budget-max`, not `--budget_max`)
- All multi-word subcommand names: kebab-case (`compliance-capture`, not `complianceCapture`)
- Three-level help hierarchy enforced: `ilc --help` → `ilc sidecar --help` → `ilc sidecar compliance-capture --help`
- Discovery via `ilc sidecar list`, not via `--help` subcommand enumeration
- `--layer4-independence` not `--layer4Independence` or `--layer_4_independence`

## 4. Model Router Version Token

```python
MODEL_ROUTER_VERSION = "model_router_fix_h1.v0.1"
```

## 5. Walkthrough Requirements

The Fix-H1 walkthrough must include:
- Summary table of all new files created with line counts
- Confirmation that all 4 adapter classes have socket timeout enforcement
- Confirmation that `Decimal` is used for all cost/latency values (grep evidence)
- Test pass count and list of test names
- `graph_delta=load_bearing_artifact_added:ilc_core/harness/model_router.py -> harness_sidecar_module_design`
- `graph_delta=support_only:` for adapter files and recipe config loader

## 6. Non-Authorizations

This phase does NOT:
- Activate `IDLE_CAPACITY_SCHEDULER_NOT_ACTIVATED` or `WERNER_CREDIT_NOT_ACTIVATED`
- Remove `PUBLIC_RC_EXCLUDE` headers from any harness module
- Implement the `multi-model-endorsement` recipe (Fix-H2)
- Implement the `ilc-submit` recipe (Fix-H3)
- Add GAIA-X adapter or sovereign cluster attestation (Fix-H2)
- Touch any epistemic, consensus, or ledger module
- Create any CDL, ADR, or governance document
- Require a GO token (NON-SENSITIVE implementation phase)
