# Codex Handoff: Wallet-Agnostic Signing Strategy — Documentation Amendments and Planning Updates

**Date:** 2026-02-21
**From:** Opus (strategic reviewer), incorporating Sonnet (codebase reviewer) findings
**To:** Codex (project manager / prompt drafter)
**Status:** APPROVED — Opus GO, Sonnet GO (final review complete 2026-02-21)

---

## Background

Jamie raised a strategic question about whether ILC should integrate with existing wallet ecosystems (Coinbase agentic wallets, Bitcoin wallets, MetaMask, hardware wallets) rather than building proprietary wallet infrastructure. Opus analysis concluded: **ILC co-opts existing wallet trust rather than building competing wallet infrastructure.** The ILC coin (ECU) is protocol-native. The wallet — where signing keys live — is not an ILC concern. The protocol should be wallet-agnostic.

Sonnet was tasked with validating this principle against the codebase and 45+ past chat files. Sonnet's findings:

- **CDL-001/002/007 runtime:** Already fully wallet-agnostic. All key identifiers are opaque strings. Zero key-format or key-storage assumptions in any security module.
- **SDK boundary contract (Phase 234):** Already correctly partitions signing (SDK concern) from key storage (operator concern). Gap is documentation, not architecture.
- **COSE Sign1:** Natively supports secp256k1 (Bitcoin/Ethereum key algorithm) via RFC 9053 algorithm ID `-47`. No protocol changes needed.
- **Past chats (June 2025):** Prior decision was "don't build ECU token economy on Ethereum's chain" — economic layer independence. This is orthogonal to "accept signatures from Ethereum wallets" — signing layer compatibility. Same June 2025 session explicitly noted ETH-compatible wallets as optionally supportable. No conflicts.
- **EVE agent:** Deprecated, superseded by OpenClaw (CDL-033). EVE's signing principle ("cannot sign without explicit user authorization") carries forward as a general principle. Do not carry EVE forward as a wallet or identity mechanism.

**Result: Zero code changes needed. Three documentation amendments. One planning dependency flag. One new ADM recommended.**

---

## Action Items for Codex

### Action 1: Phase 259 Handoff Amendment

The Phase 259 handoff artifact (`ilc_cdl_ratification_window_250_258_handoff_v0.1.md`) already includes a soft carry-forward section. Add the following item:

> **Signing provider interface specification** — Pre-D2e-07 planning dependency. Before D2e-07 (identity/signing subsystem implementation) is scoped, a brief specification is needed defining: (a) signing provider types (local keyfile, hardware wallet/HSM, external wallet SDK callback), (b) secp256k1-to-COSE-Sign1 bridging via RFC 9053 algorithm ID `-47`, (c) signing provider interface contract (`sign(payload_bytes) → COSE_Sign1_structure`). See: Opus wallet integration review (2026-02-21), Sonnet codebase review response (`docs/phases/sonnet_review_wallet_integration_strategy_response_2026_02_21.md`).

This ensures the wallet-agnostic signing work is formally tracked and doesn't get lost between windows.

One additional constraint must be included in this spec, identified in the Sonnet key-isolation review (2026-02-21): *"The COSE `kid` field MUST be a protocol-internal opaque identifier (such as `lineage_id`, or a domain-separated hash of it) and MUST NOT be the raw public key, public key bytes, or a direct hash of the public key. Using raw or hashed public key material as `kid` exposes the signer's public key in every protocol message, enabling trivial cross-domain correlation between ILC protocol identity and on-chain wallet activity (e.g., Base L2 USDC transactions from the same key). This is the highest-leverage privacy mitigation available without constraining algorithm choice."*

### Action 2: Three Documentation Amendments (bundle into one phase in 260+ window)

These are small, sentence-level edits. They can be bundled into a single phase or absorbed into a coherence pass. All three are HIGH priority before D2e-07 scoping, MEDIUM priority for the 250-259 window (they don't block anything in 250-259).

**Amendment 2a: SDK Boundary Contract §5 and §7**
File: `docs/specs/ilc_sdk_boundary_contract_234_v0.1.md`

- §5: Add sentence — *"The `--key` argument is the CLI interface to the signing provider; the signing provider may be a local keyfile, a hardware wallet, or an external wallet SDK callback. Selection of the signing backend is an operator/runtime concern, not an SDK concern."*
- §7: Add at least one non-local-file example alongside existing `--key ./agent.key` examples. Suggested: `--key coinbase://agent-wallet-id` or `--key hsm://slot-3` as illustrative (non-normative) examples showing that `--key` resolves to a provider, not necessarily a file path. Note for Codex: these URI scheme strings are illustrative only and do not commit ILC to a specific wallet SDK URL format — that is a D2e-07 implementation concern.

**Amendment 2b: ADM-002 v0.2 §5**
File: `docs/specs/ilc_adm_002_cli_first_agent_sdk_v0.2.md`

- §5: Change "Key path handling must avoid unsafe transcript leakage" → "Signing provider credential handling must avoid unsafe transcript leakage." Same security intent, removes implicit local-file assumption.

**Amendment 2c: Lineage Lifecycle Event Schema**
File: `docs/specs/ilc_lineage_lifecycle_event_schema_v0.1.md`

- Add new section (§10 or appendix): *"Lifecycle coordination with external signing providers: ILC's signer-lineage registry does not observe external wallet key rotation or revocation events. When an external wallet key is rotated or compromised, the agent or operator must explicitly trigger the corresponding ILC registry event (`rotate`/`revoke`). The registry maintains protocol-layer lifecycle state; it is not a proxy for the signing provider's key management system."*

### Action 3: ADM-003 — Reference Agent Architecture

A new architectural decision memo is accumulating enough content to justify creation. ADM-003 should capture agent-side design patterns that have emerged from recent strategic discussions. Four sections are proposed below; note that Sections 1, 2, and 4 are confirmed against codebase and past-chat review by Sonnet. **Section 3 (Local Semantic Indexing) is a strategic direction proposed by Opus from conversation context and has not been independently validated against codebase or past chats — Codex should confirm with Opus before drafting that section.**

**Section 1: Wallet Integration**
- Strategic principle: ILC co-opts existing wallet trust
- One key, two purposes: x402 resource payments (USDC) + ILC protocol signing (ECU)
- Supported wallet types: Coinbase agentic wallets, Bitcoin wallets (secp256k1), Ethereum wallets (MetaMask, WalletConnect), hardware wallets, local keyfiles
- Signing provider interface: `--key` resolves to provider, provider returns COSE Sign1
- Lifecycle coordination responsibility: agent/operator must propagate external wallet events to ILC registry
- Key isolation: Agents SHOULD use dedicated signing keys for ILC protocol operations, separate from keys used for external payments (x402/USDC) or other blockchain transactions. Cross-domain key reuse creates correlation risk between ILC protocol identity and on-chain transaction history, particularly if the COSE `kid` field is set to public key material. Signing provider implementations SHOULD use a protocol-internal opaque identifier (such as `lineage_id`) as the COSE `kid` value rather than raw or hashed public key material.
- Privacy model: agent anonymity/disclosure level is an informed opt-in choice, not a Genesis protocol requirement. Claims are public; agent identity linkage is optional.

**Section 2: Operational Cost Management (x402)**
- Agents use x402 (HTTP 402 micropayments) for external resource access: LLM inference, data sources, compute
- x402 operates at the agent layer, outside ILC protocol boundary
- ECU pricing governs protocol operations; USDC pricing governs agent operational costs
- No USDC-to-ECU bridge at the protocol level (L3 concern if anyone builds it)

**Section 3: Local Semantic Indexing** *(strategic direction — confirm with Opus before drafting)*
- Agents use local semantic search (Obsidian-style vault, qmd, embedding models) for cost-efficient claim assessment
- Semantic search is pre-protocol filtering: retrieve relevant knowledge locally before deciding whether to call `ilc validate` / `ilc contradict`
- Deduplication: semantic search local cache before `ilc assert` to avoid redundant protocol operations
- AMD ROCm / local GPU embedding generation as agent competitiveness factor

**Section 4: EVE Deprecation Note**
- EVE concept superseded by OpenClaw skill integration (CDL-033, D3 lane)
- Original EVE goals (non-technical user access, interactive knowledge base) achieved through OpenClaw agent ecosystem
- EVE's signing principle ("explicit user authorization required") carries forward as general agent design principle

ADM-003 does NOT belong in the 250-259 window. It should be flagged as a carry-forward item for the 260+ window or produced as standalone documentation between windows.

### Action 4: Capsule v0.5 Note (Phase 258)

If capsule v0.5 is produced in Phase 258 as planned, add a brief note in the appropriate section:

> **Wallet-agnostic signing principle adopted.** ILC protocol signing is wallet-agnostic — the signer-lineage registry (CDL-001) tracks key lifecycle by opaque identifier; key storage is an operator concern. COSE Sign1 supports secp256k1 natively (RFC 9053). External wallet compatibility (Coinbase, Bitcoin, Ethereum) confirmed architecturally viable. ADM-003 (Reference Agent Architecture) planned for 260+ window. See: signing provider interface specification (pre-D2e-07 dependency).

---

## What Does NOT Change

To be explicit about scope boundaries:

- **CDL-001/002/007 runtime code** — no changes. Now ratified in Phase 251 (2026-02-21). Any future changes go through CDL amendment process.
- **CLI command surface** — no changes. `--key` flag stays. D2e-01 is locked.
- **ECU token economics** — no changes. ILC's native coin remains independent of any blockchain. The wallet-agnostic principle is about signing keys, not token infrastructure.
- **Protocol pricing** — no changes. ECU pricing with congestion-aware governance. No USDC pricing layer.
- **250-259 phase sequence** — no changes to the locked sequence. All wallet-related work is carry-forward for 260+.

---

## Priority Summary

| Item | Priority | Window | Blocking? |
|---|---|---|---|
| Phase 259 handoff carry-forward entry | HIGH | 250-259 (Phase 259) | Blocks tracking |
| Capsule v0.5 wallet-agnostic note | MEDIUM | 250-259 (Phase 258) | No |
| Three documentation amendments (2a/2b/2c) | HIGH | 260+ | Blocks D2e-07 scoping |
| ADM-003 creation | MEDIUM | 260+ | Blocks nothing immediately |

---

## Source Documents

For Codex reference, the full analysis chain:

1. `sonnet_review_prompt_wallet_integration_strategy.md` — Opus → Sonnet review prompt (in `Downloads/`)
2. `docs/phases/sonnet_review_wallet_integration_strategy_response_2026_02_21.md` — Sonnet codebase and past-chat findings
3. Opus review of Sonnet findings (conversation, 2026-02-21) — GO verdict, priority correction (D2e-07 trigger, not D2e-02)
3a. `docs/phases/sonnet_review_key_isolation_privacy_response_2026_02_21.md` — Sonnet key isolation and privacy vector analysis (follow-up, 2026-02-21)
4. `docs/antigravity_tasks/phase_250_259_prompt_drafting_guidance.md` — Phase 250-259 guidelines (context for where carry-forward items land)

---

*Codex: Please incorporate Actions 1 and 4 into the Phase 258/259 prompts when drafting them. Actions 2 and 3 should be noted in your planning documents as 260+ scope. Do not modify the 250-259 locked sequence to absorb wallet work — it stays carry-forward.*
