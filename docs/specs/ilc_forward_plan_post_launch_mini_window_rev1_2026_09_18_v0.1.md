# ILC Forward Plan — Post-Launch Public-User Readiness Mini-Window

**Rev 1** — 2026-09-18  
**Produced by:** Sonnet architectural review, incorporating Codex guidance  
**Frontier at time of writing:** Post `GAP-PUBLIC-RC-LAUNCH-00` COMPLETE  
**Launch anchor SHA-256:** `3fb9e56f097ef25015575330a8fb331434436d4e981bf1aaf3ceb8e534af1528`  
**Launch timestamp:** `2026-09-18T07:07:56.877692+00:00`

---

## 1. Context

The public RC is live at `ilc-core==0.4.26`. Four genesis-bound bootstrap validators are running
at `EpochSeq=1`. Issuance interval 0 is open. The `GAP-FIRST-MONTHLY-ISSUANCE-CLOSE-OBSERVE-00`
phase is time-gated: it may not run until at least 40,320 validation epochs (~28 days) have
elapsed from the launch anchor. This window (~2026-10-16 at earliest) provides 28 days to close
public-user readiness gaps.

This document defines the **mini-window phase sequence** for those 28 days, incorporating
architectural review, code verification, and Codex guidance. All phases must complete before
`GAP-FIRST-MONTHLY-ISSUANCE-CLOSE-OBSERVE-00` opens.

---

## 2. Architectural Constraints Confirmed

### 2.1 Non-Evaporation Invariant — ALREADY IMPLEMENTED

The conservation gate (`epoch_conservation_gate.py`) enforces `NO_UNSETTLED_ILC_ISSUANCE`
before any epoch commit. At first monthly close with zero public users:

- `allocatable_current_value = current_emission + remaining_fee_pool` (line 250 of
  `epoch_distribution_writer.py`) — scheduled emission is included in allocation basis
- Zero-eligible-agents: performer/auditor allocations = 0; full pools go to carry-forward
  via `_build_carry_forward_out_records()`
- Genesis overhead = 5% of allocatable_current_value, credited to `GENESIS_AGENT1_AGENT_ID`
- Conservation: `gross = current_emission = genesis_overhead + performer_cf + auditor_cf` ✓

No implementation gap. The `GAP-FIRST-ISSUANCE-DISPOSITION-POLICY-00` phase is a policy
documentation phase only — confirming the existing architecture in writing.

### 2.2 Validator Reward at Launch — ZERO BY DESIGN

CDL-054 validator reward = 2% of `write_fee_burn_pool`. At launch, write fees = 0 (no public
user submissions), so validator reward pool = 0. The distribution writer hardcodes
`validator_reward_deltas={}`. No non-evaporation gap exists at launch.

When write fees eventually arrive with CDL-054 still off: full `genesis_burn_pool` (10% of
fees) routes to `protocol_reserve_delta`. CDL-054 activation (future) will require a
distribution writer update to split `genesis_burn_pool` between reserve and validator deltas.
This is an explicit carry-forward, not a current gap.

### 2.3 64-Char AgentID Bug — LIMITED BLAST RADIUS

`ilc_core/cli/d2e_submit_cli.py:_GRAPH_SUBMIT_AGENT_ID_RE = re.compile(r"^[0-9a-f]{64}$")`
rejects all real 96-char BLS pubkey AgentIDs. This affects ONLY the `ilc submit` CLI command.

Install path (`first_run_provisioning.py`) uses `r"^[0-9a-f]{96}$"` — unaffected. Attribution
batch bridge uses `r"^[0-9a-f]{96}$"` — unaffected.

Must be fixed before any public user uses `ilc submit`.

### 2.4 PASSIVE_ECU Stale Comment

`PASSIVE_ECU_WIRING_NOT_ACTIVATED = False` at line 56 of `epoch_attribution_settle_runtime.py`.
The flag is active (passive ECU wiring is running), but a docstring at line 570 says
"while PASSIVE_ECU_WIRING_NOT_ACTIVATED remains True" — inverted and wrong. Must be corrected.

### 2.5 Hello World Submission Mechanism — CONFIRMED (assert.truth)

`T1_PUBLIC_NON_REWARD_METADATA` is a **taxonomy classification outcome**, not a submission
primitive gate. It describes how the content will be classified after ingestion, not how it
must be submitted.

`AGENT_ISSUABLE_PRIMITIVES` = `{"assert.truth", "validate.claim", "contradict.assert",
"refute.claim", "revise.assert", "link.claim"}`. `assert.truth` IS in this set and is the
correct submission primitive for `artifact:hello_world`.

The standard `ilc submit` CLI path works: Genesis Agent submits with `--primitive assert.truth`.
The taxonomy engine will automatically classify the content as `T1_PUBLIC_NON_REWARD_METADATA`
based on the content's characteristics. The taxonomy class is derived, not specified by the
submitter.

No code change needed for submission. After 0.4.27 ships the 96-char AgentID fix, Genesis
Agent can submit `artifact:hello_world` directly via `ilc submit --agent-id <GENESIS_AGENT1_AGENT_ID>
--primitive assert.truth --content <content_file>`.

No `GAP-PACKAGE-0428` is needed for the hello world submission.

### 2.6 Hello World Content — CONFIRMED

Content is fixed per Phase 1424 §6.4: dedication paragraph + "The Road Not Taken" by Robert
Frost (1916, public domain). Verbatim content is authoritative in
`docs/specs/ilc_activation_certificate_v1_design_1424_v0.1.md §6.4`.

`canonical_external_id` MUST be updated from the original Phase 1424 proposal
(activation certificate hash — superseded) to the LAUNCH-00 opening anchor SHA-256:
`3fb9e56f097ef25015575330a8fb331434436d4e981bf1aaf3ceb8e534af1528`.

---

## 3. Phase Sequence

All phases execute in strict sequential order (no parallel execution per single-execution-lane
memory constraint). The first SENSITIVE phase in each sub-sequence requires an explicit Genesis
GO.

### Phase 1: GAP-SUBMIT-CLI-AGENT-ID-FIX1-00

**Sensitivity:** NON-SENSITIVE  
**Character:** Code fix + comment cleanup  
**Codex:** YES

**Scope:**
1. Fix `_GRAPH_SUBMIT_AGENT_ID_RE = re.compile(r"^[0-9a-f]{64}$")` → `r"^[0-9a-f]{96}$"` in
   `ilc_core/cli/d2e_submit_cli.py`
2. Replace `"agent-abc"` placeholder AgentIDs in `tests/test_phase_874_d2e_submit_cli.py`
   with real-format 96-char hex strings; confirm all submit-path tests pass with real AgentIDs
3. Fix stale docstring at `epoch_attribution_settle_runtime.py:570` — change
   "while PASSIVE_ECU_WIRING_NOT_ACTIVATED remains True" to reflect that
   `PASSIVE_ECU_WIRING_NOT_ACTIVATED = False` and passive ECU wiring is active
4. Add Fix38 ledger entries for any modified files per CDL-098
5. Note: `T1_PUBLIC_NON_REWARD_METADATA` is a taxonomy classification outcome, not a
   submission primitive. Do NOT modify `AGENT_ISSUABLE_PRIMITIVES` here. The later
   `GAP-PUBLIC-RC-HELLO-WORLD-00a` phase must confirm the standard `assert.truth`
   submission route and record that no extra package lane is needed for this point.

**Output tokens:**
- `submit_cli_agent_id_fix_committed_GAP_SUBMIT_CLI_AGENT_ID_FIX1_00`
- `passive_ecu_stale_comment_fixed_GAP_SUBMIT_CLI_AGENT_ID_FIX1_00`

**Verification commands:**
- `python -c "from ilc_core.cli.d2e_submit_cli import _GRAPH_SUBMIT_AGENT_ID_RE; assert _GRAPH_SUBMIT_AGENT_ID_RE.pattern == r'^[0-9a-f]{96}$'"` → PASS
- `pytest tests/test_phase_874_d2e_submit_cli.py -q` → all pass with real-format AgentIDs
- `grep -n "PASSIVE_ECU_WIRING_NOT_ACTIVATED remains True" ilc_core/economics/epoch_attribution_settle_runtime.py` → no match

---

### Phase 2: GAP-FIRST-ISSUANCE-DISPOSITION-POLICY-00

**Sensitivity:** NON-SENSITIVE  
**Character:** Audit/policy documentation — no runtime changes  
**Codex:** YES

**Scope:**
1. Produce a policy document at
   `docs/specs/ilc_first_issuance_disposition_policy_GAP_FIRST_ISSUANCE_DISPOSITION_POLICY_00_v0.1.md`
   confirming:
   - Zero-user first monthly close behavior: scheduled emission routes deterministically to
     Genesis overhead (5%) + performer carry-forward (80%) + auditor carry-forward (15%);
     conservation gate passes; `NO_UNSETTLED_ILC_ISSUANCE` invariant satisfied
   - Validator reward at launch: fee-dependent, zero at launch, no non-evaporation gap
   - CDL-054 activation carry-forward: requires distribution writer update to split
     `genesis_burn_pool` between `protocol_reserve_delta` and `validator_reward_deltas`
   - "Uninfluenceable ILC" property: every emitted ILC quantum has a deterministic,
     non-discretionary disposition path; no operator discretion, no evaporation
2. Code-trace verification: read `epoch_distribution_writer.py` line 250 and
   `epoch_conservation_gate.py verify_epoch_conservation_before_commit()` and record the
   exact conservation identity in the doc
3. Add Fix38 ledger entry for the new doc

**Output tokens:**
- `first_issuance_disposition_policy_committed_GAP_FIRST_ISSUANCE_DISPOSITION_POLICY_00`
- `non_evaporation_invariant_documented_GAP_FIRST_ISSUANCE_DISPOSITION_POLICY_00`

**Non-claims:** No runtime code change. No CDL mutation. No distribution writer modification.

---

### Phase 3: GAP-RELEASE-PIPELINE-TEMPLATE-00

**Sensitivity:** NON-SENSITIVE  
**Character:** Spec document production  
**Codex:** YES

**Scope:**
1. Produce `docs/specs/ilc_release_pipeline_template_v0.1.md` — a reusable release prompt
   scaffold for every future `ilc-core` release, containing:

   **Track A (NON-SENSITIVE — local build and preflight):**
   - Version bump locations (pyproject.toml, `__init__.py`, etc.)
   - Build commands and artifact naming convention
   - `twine check` pass requirement
   - Outside-repo clean venv smoke (import guards, version check, key module imports)
   - Focused test slice (correction-lane slice minimum)
   - Fix38 ledger entries: every new/modified `ilc_core/`, `tests/`, `docs/specs/` file
     requires a ledger entry in the same commit (CDL-098 mandate, per-release, NOT deferred)
   - Build receipt schema (wheel SHA-256, size, sdist SHA-256, size, signing preimages)
   - Prompt validator PASS for both 00a and 00b prompts

   **HARD STOP between Track A and Track B:**
   - Genesis must confirm: (a) Ed25519 Phase 1335 private key is accessible offline;
     (b) 00a build receipt hashes match expected; (c) explicit GO phrase issued

   **Track B (SENSITIVE — publish, sign, mirror):**
   - Signing ceremony: compute preimage, sign with Phase 1335 offline key
   - PyPI upload: `twine upload` with verification that version is absent before upload
   - PyPI fetchback: wheel SHA-256 and size must match 00a build receipt exactly
   - Yank prior active version with `superseded by {VER}: <one-line reason>`
   - `tools/install.sh` retarget to new version
   - Release envelope and installable manifest file creation
   - GitHub Release helper tarball (re-tag or new, per policy)
   - Public mirror: full filtered regeneration from exact source private commit;
     append-only sync or force-with-lease with exact previous-head binding;
     denylist and PUBLIC_RC_EXCLUDE scans pass; raw-GitHub fetchback pass for
     installer, envelopes, manifest, monthly-close runner; excluded paths return 404

   **CDL-098 LMDB Atlas note (EXPLICIT):**
   CDL-098 Atlas LMDB materialization is a periodic threshold-triggered batch operation
   (run via `GAP-CDL098-GENESIS-GRAPH-MATERIALIZATION-{VER}-00a/00b`). It is NOT a
   per-release step. The per-release obligation is Fix38 ledger entries only.
   Do not conflate Fix38 per-release entries with periodic Atlas materialization.

2. Add Fix38 ledger entry for the new template doc

**Output tokens:**
- `release_pipeline_template_committed_GAP_RELEASE_PIPELINE_TEMPLATE_00`

---

### Phase 4: GAP-PACKAGE-0427-00a

**Sensitivity:** NON-SENSITIVE  
**Character:** Local build — follows Track A from new template  
**Codex:** YES  
**Prerequisite tokens:** `submit_cli_agent_id_fix_committed_GAP_SUBMIT_CLI_AGENT_ID_FIX1_00`,
`release_pipeline_template_committed_GAP_RELEASE_PIPELINE_TEMPLATE_00`

**Scope:** Bump `0.4.26` → `0.4.27`. Carries the 64-char AgentID fix and PASSIVE_ECU comment
cleanup from GAP-SUBMIT-CLI-AGENT-ID-FIX1-00. Follow Track A from the new release template.

**Key verifications:**
- `ilc_core.__version__ == "0.4.27"` from clean outside-repo venv
- `_GRAPH_SUBMIT_AGENT_ID_RE.pattern == r'^[0-9a-f]{96}$'` in installed wheel
- Focused test slice passes (include `test_phase_874_d2e_submit_cli.py`)
- Fix38 ledger entries for all modified files

**Output tokens:**
- `package_0427_local_build_complete_GAP_PACKAGE_0427_00a`

---

### Phase 5: GAP-PACKAGE-0427-00b

**Sensitivity:** SENSITIVE — explicit GO phrase required  
**GO phrase:** `GO Phase GAP-PACKAGE-0427-00b PUBLISH-AUTHORIZED`  
**Character:** PyPI publish, sign, mirror — follows Track B from new template  
**Codex:** YES after Genesis GO

**Prerequisite:** Phase 1335 Ed25519 offline key accessible. Genesis must confirm before Codex
proceeds.

**Scope:** Sign 0.4.27 preimages with Phase 1335 key, upload to PyPI, fetchback-verify, yank
0.4.26, retarget `tools/install.sh`, publish GitHub Release helper, refresh and push public mirror.

**Output tokens:**
- `package_0427_published_GAP_PACKAGE_0427_00b`

**Non-claims:** No guard flip. No validator venv sync in this phase (separate phase if needed).
No LMDB write. No ECU/ILC settlement.

---

### Phase 6: GAP-PUBLIC-RC-HELLO-WORLD-00a

**Sensitivity:** NON-SENSITIVE  
**Character:** Node spec and submission mechanism confirmation  
**Codex:** YES

**Scope:**
1. Read `docs/specs/ilc_activation_certificate_v1_design_1424_v0.1.md §6.1–6.6` verbatim
2. Confirm `canonical_external_id` update:
   - Phase 1424 original: activation certificate hash (superseded)
   - Rev 1 (this plan): LAUNCH-00 opening anchor file SHA-256:
     `3fb9e56f097ef25015575330a8fb331434436d4e981bf1aaf3ceb8e534af1528`
3. Confirm verbatim content from §6.4 (dedication + "The Road Not Taken") — do NOT alter
4. Confirm submission mechanism:
   - `T1_PUBLIC_NON_REWARD_METADATA` is a TAXONOMY CLASSIFICATION OUTCOME, not a gate
   - `assert.truth` IS in `AGENT_ISSUABLE_PRIMITIVES` — standard submission path works
   - Submission primitive: `assert.truth` via `ilc submit` after 0.4.27 ships 96-char fix
   - Read `ilc_core/epistemic/truth_primitive_submission_runtime.py` to confirm `AGENT_ISSUABLE_PRIMITIVES`
   - Read `ilc_core/epoch/genesis_settlement_destination.py` to get `GENESIS_AGENT1_AGENT_ID`
5. Produce node spec doc at
   `docs/specs/ilc_hello_world_node_spec_GAP_PUBLIC_RC_HELLO_WORLD_00a_v0.1.md` with:
   - Node name, taxonomy class, author, `canonical_external_id` (LAUNCH-00 anchor SHA)
   - Verbatim content block (copy exactly from Phase 1424 §6.4)
   - Submission primitive: `assert.truth`
   - Submission mechanism: `ilc submit --agent-id <GENESIS_AGENT1_AGENT_ID> --primitive assert.truth --content <content_file>`
   - Expected evidence fields (node_id, submission receipt, graph registration)
   - Fix38 ledger entry for the node (graph_delta=load_bearing_artifact_added)
6. Add Fix38 ledger entries for the new spec doc

**Output tokens:**
- `hello_world_node_spec_committed_GAP_PUBLIC_RC_HELLO_WORLD_00a`
- `hello_world_submission_mechanism_confirmed_GAP_PUBLIC_RC_HELLO_WORLD_00a`

No `GAP-PACKAGE-0428` is needed. Submission uses `assert.truth` which is already in
`AGENT_ISSUABLE_PRIMITIVES`. The taxonomy engine classifies the content as T1 automatically.

---

### Phase 7: GAP-PUBLIC-RC-HELLO-WORLD-00b

**Sensitivity:** SENSITIVE — explicit GO phrase required  
**GO phrase:** `GO Phase GAP-PUBLIC-RC-HELLO-WORLD-00b HELLO-WORLD-SUBMIT-AUTHORIZED`  
**Character:** Live node submission via Genesis Agent  
**Codex:** YES after Genesis GO  
**Prerequisite token:** `hello_world_submission_mechanism_confirmed_GAP_PUBLIC_RC_HELLO_WORLD_00a`

**Scope:**
1. Submit the `artifact:hello_world` node to the live network using `assert.truth` via `ilc submit` (confirmed in 00a)
2. Verify node is accepted (return code, node_id)
3. Retrieve the node and confirm content matches verbatim §6.4 content
4. Produce evidence file at `out/gap_public_rc_hello_world_00b/hello_world_submission_evidence.json`
   with: `node_id`, `canonical_external_id`, `submission_timestamp_utc`,
   `submission_mechanism`, `content_sha256`, `node_retrieval_status`, `genesis_agent_id`
5. Add Fix38 ledger entry for the submitted node (this is the live graph node, not a spec doc)

**Output tokens:**
- `hello_world_node_submitted_GAP_PUBLIC_RC_HELLO_WORLD_00b`

**Non-claims:** No claimability activation. No ECU distribution. No ILC settlement. No epoch
advance. No monthly issuance close.

---

### Phase 8: GAP-ECU-ATTRIBUTION-PIPELINE-SMOKE-00

**Sensitivity:** SENSITIVE — explicit GO phrase required  
**GO phrase:** `GO Phase GAP-ECU-ATTRIBUTION-PIPELINE-SMOKE-00 ECU-ATTRIBUTION-PIPELINE-SMOKE`  
**Character:** ECU attribution pipeline smoke test against live network  
**Codex:** YES after hello world confirmation  
**Prerequisite token:** `hello_world_node_submitted_GAP_PUBLIC_RC_HELLO_WORLD_00b`

**Scope:**
1. Construct an attribution event (REUSE or CO_AUTHORSHIP) that references the `artifact:hello_world`
   node ID from `hello_world_submission_evidence.json`
2. Call `settle_attribution_batch()` against the live node; confirm nonzero ECU payout quote
   for the attribution event
3. Exercise the ECU fast-path debit path (carry-forward from EPOCH-00d `skipped_zero_balance`):
   confirm the debit path now executes with real ECU
4. PASSIVE_ECU behavior: confirm expected result is `0` (centrality data empty at launch —
   not a bug; network has not accumulated centrality state); record the confirmation explicitly
5. Confirm `PASSIVE_ECU_WIRING_NOT_ACTIVATED = False` guard is correct and the zero result
   is due to empty centrality state, not to the flag being True
6. Verify LMDB wallet integrity: wallet rows unchanged before/after smoke (no settlement yet)
7. Produce evidence file at `out/gap_ecu_attribution_pipeline_smoke_00/ecu_attribution_smoke_evidence.json`

**Output tokens:**
- `ecu_attribution_pipeline_smoke_pass_GAP_ECU_ATTRIBUTION_PIPELINE_SMOKE_00`
- `ecu_fast_path_debit_exercised_GAP_ECU_ATTRIBUTION_PIPELINE_SMOKE_00`
- `passive_ecu_zero_centrality_confirmed_GAP_ECU_ATTRIBUTION_PIPELINE_SMOKE_00`

**Non-claims:** No monthly issuance close. No MonthlyIssuanceMaturityProof produced. No
claimability activation. No ILC settlement.

---

### Phase 9: GAP-FIRST-MONTHLY-ISSUANCE-CLOSE-OBSERVE-00

**Sensitivity:** SENSITIVE, NO-PROMPT  
**Time gate:** Run only after at least 40,320 validation epochs elapsed from launch timestamp
`2026-09-18T07:07:56.877692+00:00` (~2026-10-16 at earliest)  
**Prerequisite:** All mini-window phases 1–8 complete

This phase is defined in `ilc_comprehensive_forward_plan_post_1575c_v0.1.md` and is not
rescoped here. It must reference:
- Opening anchor file SHA-256: `3fb9e56f097ef25015575330a8fb331434436d4e981bf1aaf3ceb8e534af1528`
- Opening anchor payload SHA-256: `7ce90bd3dcac3389aada656662746974353098738aed8b3b68467bfb69f3ed4a`
- Must not hand-construct a proof or force settlement by operator action

---

## 4. Open Questions for Genesis Confirmation

Before Codex begins Phase 5 (`GAP-PACKAGE-0427-00b`), Genesis must confirm:

1. **Phase 1335 Ed25519 key accessibility**: Is the offline signing key accessible for the
   0.4.27 Track B signing ceremony?

2. **Hello world poem confirmation**: "The Road Not Taken" by Robert Frost is confirmed per
   Phase 1424. No change needed unless Genesis explicitly overrides.

3. **Hello world submission path**: RESOLVED. `T1_PUBLIC_NON_REWARD_METADATA` is a taxonomy
   classification outcome, not a submission gate. `assert.truth` is in `AGENT_ISSUABLE_PRIMITIVES`
   and is the correct primitive. No `GAP-PACKAGE-0428` is required. After 0.4.27 publishes the
   96-char AgentID fix, Genesis Agent can submit via `ilc submit --primitive assert.truth` directly.

---

## 5. What Does NOT Change

- `GAP-FIRST-MONTHLY-ISSUANCE-CLOSE-OBSERVE-00` timing gate (40,320 epochs minimum)
- The conservation invariant architecture — no runtime changes needed
- CDL-054 validator reward activation status — remains off
- Carry-forward accounts — existing architecture handles zero-user case correctly
- Genesis wallet claimability — remains `deferred` until after OBSERVE-00

---

## 6. Summary Token Table

| Phase | Token | Sensitivity |
|-------|-------|-------------|
| GAP-SUBMIT-CLI-AGENT-ID-FIX1-00 | `submit_cli_agent_id_fix_committed_...` | NON-SENSITIVE |
| GAP-FIRST-ISSUANCE-DISPOSITION-POLICY-00 | `first_issuance_disposition_policy_committed_...` | NON-SENSITIVE |
| GAP-RELEASE-PIPELINE-TEMPLATE-00 | `release_pipeline_template_committed_...` | NON-SENSITIVE |
| GAP-PACKAGE-0427-00a | `package_0427_local_build_complete_...` | NON-SENSITIVE |
| GAP-PACKAGE-0427-00b | `package_0427_published_...` | SENSITIVE |
| GAP-PUBLIC-RC-HELLO-WORLD-00a | `hello_world_node_spec_committed_...` | NON-SENSITIVE |
| GAP-PUBLIC-RC-HELLO-WORLD-00b | `hello_world_node_submitted_...` | SENSITIVE |
| GAP-ECU-ATTRIBUTION-PIPELINE-SMOKE-00 | `ecu_attribution_pipeline_smoke_pass_...` | SENSITIVE |
| GAP-FIRST-MONTHLY-ISSUANCE-CLOSE-OBSERVE-00 | (time-gated) | SENSITIVE, NO-PROMPT |
