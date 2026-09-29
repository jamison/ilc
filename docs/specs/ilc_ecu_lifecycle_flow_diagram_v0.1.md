# ILC ECU Lifecycle Flow Diagram — v0.1

**Status:** Reference artifact — v0.1 with Codex corrections applied as annotations  
**Produced:** 2026-09-25  
**Author:** Sonnet (original diagram + thinking notes)  
**Corrections:** Codex (see §3 below)  
**Superseded by:** `docs/specs/ilc_ecu_lifecycle_flow_diagram_v0.2.md`

---

## §1 — Sonnet Thinking Notes (verbatim)

> The user wants me to produce the ECU lifecycle ASCII diagram. Let me construct it based on what I know from the session summary and the codebase.
>
> Key elements to show:
>
> All ECU types: ECU^X, ECU^Q, ECU^A⊕, ECU^A⊖, ECU^C, ECU^L, ECU^T, Ω (Werner signal, not ECU)
> Full lifecycle flow: agent work → attribution events → Rust BalanceStore → monthly close → ILC
> Status indicators: ✓ complete / ◑ partial / ✗ open / ⏳ time-gated / [BLOCKED]
> Current blockers, diagnostic-only paths, the CDL-114 Sybil guard, and Werner/Ω as governor signal
> I'm now drafting the diagram as a top-down flow, starting with content submission into the truth graph store, then branching into ECU^X capacity tracking, noting its spec is done but the runtime bridge is still open.
>
> Continuing the flow, ECU^X isn't claim-bearing itself but feeds a centrality/reach score into attribution events (co-authorship, refutation, provenance), where event capture and the Sybil guard are done, co-authorship is wired, but the refutation and provenance bridges are still post-RC, with a backward beta coefficient of 0.10 branching off from there.
>
> Below that, I'm mapping the split between direct attribution (ECU^A⊕) and backward attribution (ECU^A⊖), both monthly-close-bearing but with the live attribution bridge still unfinished post-RC, feeding into an attribution batch ingest process handled by a Rust binary.
>
> From there I'm tracing into CDL-114's Sybil Guard requiring at least three distinct creators, which is already specced and running, and then down to the Rust BalanceStore built on LMDB as the consensus store holding the committed ECU^C aggregate balance -- that gap is fully closed per the completed commit. I'm noting this is exactly where the ilc ecu status command reads its balance from, sourced from the Rust balance store.
>
> Downstream, I'm mapping the time-gated Monthly Close (OBSERVE-00), which still needs GO approval around mid-October 2026 and requires an attribution-origin evidence chain before ECU^C can flow into the close pool. From there I'm checking eligibility for ECU^L lots, which depend on OBSERVE-00 completing and are limited to conversion-claim-bearing cases under CDL-048.
>
> I'm continuing the flow into ILC Settlement, where the conversion claim gets committed to the LMDB wallet store via commit_settled_epoch(), and I still need to add ECU^Q, ECU^T, the Werner signal, and the diagnostic/fallback paths like the local wallet store read model that pulls the ILC balance.
>
> I also want to track the current packaging blockers — Phase 1603 is blocked pending the GAP-PACKAGE-0430 dependencies, OBSERVE-00 is time-gated, and the attribution bridges are deferred post-RC. Now I'm laying out the ECU lanes in the diagram, starting with the agent work lane going from submission to exposure capacity.
>
> Building the diagram now, with a legend marking complete, partial, and open items, plus time-gated and blocked statuses...
>
> Adding agent work section: content submission to the truth graph store, noting it's locally ready but blocked on package release for the Phase 1603 smoke test...
>
> Still mapping the diagram...
>
> Still writing diagram nodes...
>
> After that, the Rust BalanceStore represents the committed aggregate — ECU^C — which isn't close-bearing by default; it needs an attribution-origin evidence chain tracing back to ECU^A before the monthly close can actually consume it.
>
> That ECU^C close-eligibility is blocked until the attribution-origin bridge is wired post-RC, which then feeds into CDL-048's fixed-schedule ECU^L conversion lots -- these are committed at emission with no activation flag and follow a fixed tranche draw schedule rather than a sweeper pattern.
>
> I'm mapping out how lot eligibility ties to the monthly close: this status gate depends on OBSERVE-00, a time-gated, sensitive process requiring GO approval around mid-October 2026, which draws on ECU^C aggregate inputs.
>
> OBSERVE-00 consumes attribution events and lot eligibility data to adjudicate the close pool, producing ILC settlement credits through commit calls, while CDL-028 burns act as a permanent deflationary sink rather than a spendable reserve. This feeds forward into the ILC settlement stage.
>
> The wallet store tracks settled ILC balance separately from the ECU accrual path, and the ilc ecu status command reads committed ECU from the Rust balance store alongside settled ILC from the wallet store -- the runtime side looks complete, though something else still needs finishing.
>
> I'm also noting ECU^T (Transferred) as a narrow-scope, spec-only piece not yet implemented, and flagging that certain paths like the local wallet store read model are diagnostic fallbacks rather than actual completion markers.
>
> Good, that forbidden token doesn't appear anywhere. Taking stock now: the Rust BalanceStore wiring, Sybil guard, ECU^Q visibility, lifecycle runtime, and LMDB settlement are all complete, while Phase 1603's smoke path works locally but still needs packaging.
>
> Still open before RC: the passive centrality bridge and live attribution event ingestion. Post-RC items include the refutation/provenance bridges, attribution-origin evidence chain, transfer mechanics, and Werner parameterization, while OBSERVE-00's first monthly close and lot eligibility remain time-gated pending the October 2026 window.
>
> I'm reconsidering ECU^Q's placement — it represents the quoted, pre-adjudication in-flight state before events get committed to the Rust BalanceStore as ECU^C. So the sequence runs: attribution events accumulate as ECU^Q, batch ingest adjudicates them into ECU^C, and monthly close settles the origin-chained ECU^C into ILC. I also need to reconsider where ECU^X fits, since it doesn't actually sit on the ILC close path at all.
>
> I'm realizing the diagram really has two separate rails: the attribution rail running from agent work through events, ECU^A⊕/⊖, batch ingest, ECU^C, and monthly close into ILC; and a separate CDL-048 rail where genesis fixed-schedule emission produces ECU^L lots that convert into ILC. ECU^X sits outside both rails as a capacity/score metric rather than a flow, while the Werner/Ω signal acts as a governor modulating the attribution pipeline rather than a direct input.
>
> I want to redo the layout more compactly with clearer flow arrows, so let me put together a cleaner final version.

---

## §2 — Original Diagram (verbatim, as produced)

```
═══════════════════════════════════════════════════════════════════════════════════════
                 ILC  ECU  LIFECYCLE  FLOW  —  STATUS  2026-09-24
═══════════════════════════════════════════════════════════════════════════════════════

  LEGEND:  ✓ COMPLETE  ◑ LOCAL-ONLY/PARTIAL  ✗ OPEN  ⏳ TIME-GATED
           [PKG] blocked on package  [PRC] post-RC  [FRBN] forbidden token

───────────────────────────────────────────────────────────────────────────────────────
  AGENT WORK
───────────────────────────────────────────────────────────────────────────────────────

  Agent submits content node
  (ILC_TRUTH_GRAPH_STORE_PATH / CIDv1)
         │
         │  ◑ [PKG] local path ready; Phase 1603 smoke blocked on
         │          GAP-PACKAGE-0430-00a/b before SENSITIVE retry
         │
         ├──────────────────────────────────────────────────────────────┐
         │                                                              │
         ▼                                                              ▼
  ┌──────────────────────┐                               ┌─────────────────────────┐
  │  ECU^X               │                               │  Ω  Werner Signal       │
  │  Exposure Capacity   │                               │  Dimensionless governor │
  │  (centrality score)  │                               │  NOT an ECU type        │
  │                      │                               │  Modulates attrib weight│
  │  NOT claim-bearing   │                               │  CDL-096 parameterized  │
  │  NOT close-eligible  │                               │                         │
  │                      │                               │  Status: ✗ OPEN [PRC]  │
  │  Status: ✗ OPEN      │                               │  Werner CDL post-RC     │
  │  [GAP-PASSIVE-ECU-   │                               └─────────────────────────┘
  │   CENTRALITY-00]      │
  └──────────┬───────────┘
             │ informs attribution weight (non-linear)
             ▼

───────────────────────────────────────────────────────────────────────────────────────
  ATTRIBUTION EVENT PROCESSING
───────────────────────────────────────────────────────────────────────────────────────

  ┌───────────────────────────────────────────────────────────────────────────┐
  │  Graph Events                                                             │
  │  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐        │
  │  │ CO_AUTHORSHIP   │   │ REFUTATION      │   │ PROVENANCE      │        │
  │  │ ✓ Wired         │   │ ✗ [PRC] bridge  │   │ ✗ [PRC] bridge  │        │
  │  │ (Phase 1601)    │   │   post-RC only  │   │   post-RC only  │        │
  │  └─────────────────┘   └─────────────────┘   └─────────────────┘        │
  │                                                                           │
  │  CDL-114 Sybil Guard: N≥3 distinct creators per event  ✓ Phase 1601     │
  └───────────────────────────────────┬───────────────────────────────────────┘
                                      │
                    ┌─────────────────┴──────────────────┐
                    │  CDL-108  β_bwd = 0.10             │
                    │  (BACKWARD_ATTRIBUTION_POOL_SHARE) │
                    ▼                                    ▼
  ┌─────────────────────────┐          ┌─────────────────────────┐
  │  ECU^A⊕                 │          │  ECU^A⊖                 │
  │  Direct Attribution     │          │  Backward Attribution   │
  │  monthly-close-bearing  │          │  monthly-close-bearing  │
  │  (90% pool share)       │          │  (β_bwd = 10% share)    │
  │                         │          │                         │
  │  Status: ✗ OPEN [PRC]  │          │  Status: ✗ OPEN [PRC]  │
  │  live ingestion bridge  │          │  live ingestion bridge  │
  │  not yet wired          │          │  not yet wired          │
  └───────────┬─────────────┘          └────────────┬────────────┘
              └──────────────────┬──────────────────┘
                                 │
                                 │  in-flight / pre-adjudication state
                                 ▼
              ┌──────────────────────────────────────┐
              │  ECU^Q  (Quoted / Pre-adjudication)  │
              │  NOT claim-bearing                   │
              │  Visible as pending_attribution_quote│
              │  in `ilc ecu status` output          │
              │                                      │
              │  Status: ✓ Field wired in CLI        │
              │           ✗ Live event feed [PRC]    │
              └──────────────────┬───────────────────┘
                                 │
                                 │  Attribution Batch Ingest
                                 │  (Rust binary: attribution_batch_ingest)
                                 │  resolved via resolve_attribution_batch_ingest_binary()
                                 │  explicit cfg → ilc_core/bin/ → shutil.which() → fallback
                                 ▼

───────────────────────────────────────────────────────────────────────────────────────
  RUST BALANCE STORE  (ECU^C)
───────────────────────────────────────────────────────────────────────────────────────

  ┌───────────────────────────────────────────────────────────────────────────┐
  │  Rust BalanceStore  (ILC_CONSENSUS_LMDB_PATH)                            │
  │  ECU^C  —  committed aggregate                                           │
  │                                                                           │
  │  NOT close-bearing by default.                                           │
  │  ECU^C requires attribution-origin evidence chain proving descent from   │
  │  ECU^A before monthly-close can consume it.                              │
  │  Aggregate alone does NOT grant close-eligibility.                       │
  │                                                                           │
  │  ✓ COMPLETE  GAP-ECU-STATUS-LOCAL-PATH-00  (commit c8b346e82)           │
  │                                                                           │
  │  `ilc ecu status` reads:                                                 │
  │    committed_ecu_balance  ← ECU^C aggregate (zero until ingestion)       │
  │    balance_ecu_source     = "rust_balance_store_committed_aggregate"     │
  │    balance_ecu_pending    ← ECU^Q (in-flight, not yet committed)         │
  │                                                                           │
  │  [FRBN] "python_in_memory_ecu_python_rust_balance_bridge_missing_        │
  │          phase_1597"  must NOT appear — tests assert absence             │
  └────────────────────────┬──────────────────────────────────────────────────┘
                           │
              ┌────────────┴──────────────────────────────────────┐
              │                                                   │
              │  Attribution-origin evidence chain                │
              │  (ECU^C is ECU^A-descended)                       │
              │  Status: ✗ OPEN [PRC]                             │
              │  Blocks close-eligibility for ECU^C               │
              │                                                   │
              ▼                                                   ▼
   [CLOSE-ELIGIBILITY GATE]                        CDL-048 Fixed-Schedule Lots
   ECU^C not close-eligible                        (hardcoded emission, no flag,
   until origin chain wired                         CDL-029 pattern)
   [PRC blocker]                                         │
                                                         ▼
                                          ┌─────────────────────────────┐
                                          │  ECU^L  (CDL-048 lot)       │
                                          │  Conversion-claim-bearing   │
                                          │  ONLY — not attribution-    │
                                          │  bearing                    │
                                          │                             │
                                          │  Status: ⏳ POST-OBSERVE-00 │
                                          │  lot eligibility requires   │
                                          │  monthly close gate first   │
                                          └──────────────┬──────────────┘
                                                         │
                                                         │  conversion claim
                                                         ▼

───────────────────────────────────────────────────────────────────────────────────────
  MONTHLY CLOSE  (OBSERVE-00)
───────────────────────────────────────────────────────────────────────────────────────

  ┌───────────────────────────────────────────────────────────────────────────┐
  │  OBSERVE-00   ⏳ TIME-GATED  ~2026-10-16   SENSITIVE — GO required       │
  │                                                                           │
  │  Inputs required:                                                        │
  │    · ECU^C aggregate  +  attribution-origin evidence chain  [PRC gate]  │
  │    · ECU^L lot eligibility schedule                                      │
  │    · CDL-028 burn sink allocation (permanent deflationary — NOT reserve) │
  │                                                                           │
  │  Produces: ILC settlement credits via commit_settled_epoch()             │
  └────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼

───────────────────────────────────────────────────────────────────────────────────────
  ILC SETTLEMENT
───────────────────────────────────────────────────────────────────────────────────────

  ┌───────────────────────────────────────────────────────────────────────────┐
  │  LMDB Wallet Store  (commit_settled_epoch())                             │
  │  balance_ilc       ← settled ILC balance                                │
  │                                                                           │
  │  `ilc ecu status` wallet-mode reads:                                    │
  │    committed_ecu_balance  = ECU^C accrual (ecu_accrual field, zero path)│
  │    settled_ilc_balance    = ILC settled balance                          │
  │                                                                           │
  │  Status: ✓ Runtime COMPLETE  /  ⏳ no live monthly close yet             │
  └───────────────────────────────────────────────────────────────────────────┘

  ECU^T  (Transferred)  — narrow scope, spec-only [PRC]
  ─────────────────────────────────────────────────────
  Transfer mechanics not wired. Spec references CDL-restricted conditions.
  Diagram position: post-settlement, agent-to-agent narrow path.
  Status: ✗ OPEN [PRC]

───────────────────────────────────────────────────────────────────────────────────────
  DIAGNOSTIC / FALLBACK PATHS  (NON-COMPLETION — never close-eligible)
───────────────────────────────────────────────────────────────────────────────────────

  balance_ecu_source = "local_wallet_store_read_model"
    Reads ILC balance + ECU accrual from LMDB wallet store only.
    committed_ecu_balance reflects ecu_accrual (not Rust BalanceStore ECU^C).
    settled_ilc_balance reflects ILC from commit_settled_epoch().
    Used when ILC_CONSENSUS_LMDB_PATH not configured.
    Status: ✓ Wired; NOT a close-completion path.

  balance_ecu_source = "local_zero_state_no_source_configured"
    No BalanceStore, no wallet configured. Returns zeros.
    Status: ✓ Wired; diagnostic only.

───────────────────────────────────────────────────────────────────────────────────────
  CURRENT BLOCKER SUMMARY
───────────────────────────────────────────────────────────────────────────────────────

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  NEXT FRONTIER (NON-SENSITIVE, no GO needed)                           │
  │  GAP-PACKAGE-0430-00a  —  local build of 0.4.30 with ECU status wiring │
  ├─────────────────────────────────────────────────────────────────────────┤
  │  THEN (SENSITIVE, GO required):                                         │
  │  GAP-PACKAGE-0430-00b  —  PyPI publish + Ed25519 sign + mirror         │
  │  Phase 1603 retry      —  clean pip-install smoke (Rust-backed ECU)    │
  │    GO phrase: "GO Phase 1603 ECU-PUBLIC-USER-SMOKE-AUTHORIZED"          │
  ├─────────────────────────────────────────────────────────────────────────┤
  │  INDEPENDENT NON-SENSITIVE:                                             │
  │  GAP-PASSIVE-ECU-CENTRALITY-POPULATION-SMOKE-00  (ECU^X bridge)        │
  ├─────────────────────────────────────────────────────────────────────────┤
  │  TIME-GATED:                                                            │
  │  OBSERVE-00  first monthly close  ~2026-10-16  (SENSITIVE)             │
  │  ECU^L conversion eligibility     post-OBSERVE-00                       │
  ├─────────────────────────────────────────────────────────────────────────┤
  │  POST-RC (non-blocking for launch):                                     │
  │  · ECU^C attribution-origin evidence chain                              │
  │  · REFUTATION / PROVENANCE attribution bridges                          │
  │  · ECU^T transfer mechanics                                             │
  │  · CDL-096 Werner / Ω full parameterization                             │
  └─────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════════

The critical path gap is the ECU^C close-eligibility gate in the middle — the Rust
BalanceStore aggregate is wired and readable (✓ complete), but the attribution-origin
evidence chain that proves ECU^C descends from ECU^A is a post-RC deliverable. That
means OBSERVE-00 on 2026-10-16 can proceed with the structural close machinery, but
the close-pool adjudication will only have meaningful ECU^C inputs once the live
attribution bridge is wired post-RC.
```

---

## §3 — Codex Corrections (verbatim, 2026-09-25)

> Broadly: Sonnet's planning is conceptually useful, but I would not treat it as
> canonical without corrections. The best part is the decomposition of ECU into
> distinct lifecycle/type lanes instead of pretending "ECU" is one thing. That is
> exactly the right move for the gap matrix.
>
> **My main pushback:**
>
> **The frontier is stale.**
> Sonic says the next frontier is GAP-PACKAGE-0430-00a, but that phase is already
> complete. Current frontier should be GAP-PACKAGE-0430-00b publish, then validator
> sync, then Phase 1603 retry.
>
> **Do not mark CO_AUTHORSHIP as wired by Phase 1601.**
> Phase 1601 is CDL-114 Sybil diversity governance. It does not wire CO_AUTHORSHIP
> attribution. Current state is:
> - Phase 1599 verified settlement math for all edge types.
> - Phase 1602 wired source_refs into REUSE attribution.
> - Dedicated CO_AUTHORSHIP / REFUTATION / PROVENANCE bridge paths remain
>   open/post-RC unless separately implemented.
>
> **Do not say ECU^A live ingestion is wholly open.**
> Better framing:
> - REUSE/source_refs local bridge exists and is implemented.
> - Public clean-install visibility is still being proven through package/sync/Phase 1603.
> - Non-REUSE attribution ingestion remains open.
> - Organic live topology evidence remains open until OBSERVE/live smokes.
>
> **The evidence chain is not absent anymore.**
> The accrual evidence source bridge exists. The remaining gap is proving that
> OBSERVE-00/monthly close consumes the attribution-origin evidence correctly in the
> live/public-RC setting. So the matrix should distinguish:
> - implemented source/evidence bridge,
> - packaged/synced validator availability,
> - live monthly-close consumption.
>
> **ECU^C should stay non-claim-bearing by default.**
> Sonic gets this mostly right. The Rust BalanceStore aggregate is a balance/readback
> fact, not sufficient close eligibility by itself. Monthly close needs
> attribution-origin evidence proving the balance descends from claim-bearing
> attribution events.
>
> **Be careful with ECU^X and Ω.**
> ECU^X as exposure capacity and Ω as Werner/pressure/governor signal are good
> conceptual lanes, but current runtime should not be overclaimed. If the diagram
> says ECU^X "informs attribution weight," mark that as planned/spec/sim-derived
> unless the code path is present.
>
> **ECU^T should not be described like generalized transferability.**
> It is a narrow, bounded transfer/disposition state. It is not free money transfer,
> not ILC settlement, and not monthly-close-bearing by default.
>
> **CDL-048 / burn-pool wording needs caution.**
> Avoid saying fixed-schedule emission "produces ECU^L lots" too casually. Better:
> CDL-048 governs lotized conversion claims or eligibility windows, subject to the
> relevant rules. Also avoid hard "burn sink" language unless the current spec
> confirms that exact accounting semantics.
>
> **What I would tell Sonic to change:**
>
> Replace:
> `CO_AUTHORSHIP ✓ wired Phase 1601`
> With:
> `CO_AUTHORSHIP quote/math verified Phase 1599; dedicated bridge path not yet implemented.`
> `Phase 1601 only ratifies CDL-114 Sybil diversity guard.`
>
> Replace:
> `ECU^A live ingestion bridge not yet wired`
> With:
> `REUSE/source_refs attribution bridge is locally implemented; public clean-install proof pending.`
> `CO_AUTHORSHIP/REFUTATION/PROVENANCE dedicated bridge routes remain post-RC/open.`
>
> Replace:
> `ECU^C cannot close because evidence bridge missing`
> With:
> `ECU^C aggregate is readable from Rust BalanceStore, but monthly-close eligibility`
> `requires attribution-origin evidence consumption in OBSERVE-00/live close.`
>
> The gap matrix in `docs/specs/ilc_ecu_confidence_matrix_and_validation_lane_v0.1.md`
> is more accurate than the diagram text right now. I would use the matrix as the
> authority, then revise the diagram to match it.
>
> **Bottom line:** Sonic's diagram is a strong explanatory artifact, but it needs
> stale frontier fixes and sharper separation between "math verified," "bridge wired,"
> "packaged/synced," and "live close proven." That distinction is the whole game for
> ECU now.

---

## §4 — Correction Summary Table (for v0.2 drafting)

| Diagram cell (v0.1)                         | Correction                                                                                        |
|---------------------------------------------|---------------------------------------------------------------------------------------------------|
| Frontier: GAP-PACKAGE-0430-00a next         | **STALE** — 00a complete; frontier is 00b publish → validator sync (mandatory, homogeneity policy) → Phase 1603 retry |
| Validator sync shown as conditional         | **RESOLVED (Rev 142, 2026-09-25)** — Option A adopted: GAP-VALIDATOR-SYNC-0430-00 is mandatory before Phase 1603 by public-RC validator homogeneity policy. Not because Phase 1603 requires validator acceptance (it does not — it is a local clean-install smoke). Reason: public-RC validator venvs must not lag the published RC package. Remove "if retained" language everywhere. |
| CO_AUTHORSHIP ✓ wired (Phase 1601)          | **WRONG** — Phase 1601 = CDL-114 Sybil guard only; CO_AUTHORSHIP math verified Phase 1599; dedicated bridge not yet implemented |
| ECU^A live ingestion bridge wholly open     | **IMPRECISE** — REUSE/source_refs bridge locally implemented (Phase 1602); non-REUSE routes open; public-install proof pending |
| ECU^C evidence chain absent / [PRC]         | **IMPRECISE** — accrual evidence source bridge exists; gap is live OBSERVE-00 consumption, not raw absence |
| ECU^X "informs attribution weight"          | Mark as **planned/spec/sim-derived** unless runtime code path confirmed                          |
| ECU^T described as post-settlement transfer | Clarify: narrow bounded disposition state; NOT generalized transfer; NOT monthly-close-bearing   |
| CDL-048 "produces ECU^L lots"               | Use: governs lotized conversion claims / eligibility windows; avoid casual "lot production" framing |
| CDL-028 "burn sink"                         | Verify exact accounting semantics before asserting; "permanent deflationary sink" needs spec confirmation |
| Validator sync check on binary              | **v0.2 operational note**: Step 8 in sync prompt now requires `resolved.is_file()` + `os.access(X_OK)` — mere importability of `resolve_attribution_batch_ingest_binary` is not sufficient; the packaged binary must be present and executable |

---

*v0.2 has been produced after Phase 1603 completion and verified against
`docs/specs/ilc_ecu_confidence_matrix_and_validation_lane_v0.1.md` as the
authoritative source for this planning lane.*
