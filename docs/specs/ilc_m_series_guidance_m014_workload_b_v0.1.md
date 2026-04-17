# ILC M-Series Guidance: M-014 — Workload B Censorship Resistance Drill

**Prepared by:** Claude Sonnet 4.6 (local reviewer)  
**Date:** 2026-04-17  
**For:** Gemini  
**Prerequisite:** M-013 COMPLETE `3c8d5590`; SEC-007 CLOSED `7f5a0cdb`

---

## 1. Phase identity

**M-014 — Phase 690 Workload B: Censorship Resistance Drill**

This phase was originally scoped as M-011 in the lane doc. When M-011 was
reassigned to keygen + testnet_client tooling, and M-012 inserted the full BFT
ECUTransfer round-trip, Workload B shifted to M-014. The status table in
`ilc_mysticeti_implementation_lane_m_series_v0.1.md` is authoritative.

> Note: The section header in the lane doc that reads `M-014 — Phase 690 Workload E:
> Validator Operability` is a stale artifact of the pre-shift numbering. Ignore
> it. M-014 is Workload B; Workload E is M-017.

---

## 2. Scope

Run Phase 690 Workload B: one or more validators configured to exclude epoch
records from a designated "censored" submission node. Observe whether the
censored epoch record achieves finality despite the censorship.

**Testnet parameters:**  
N=4, F=1 (the live testnet). This means only f=1 censoring validator is
available. The original Phase 690 Workload B spec assumed f=2 censoring
validators (larger validator set).

**Required deviation acknowledgement:** You must explicitly note in the results
doc that f=1 is a deviation from the Phase 690 f=2 spec, and explain why f=1
is still a meaningful censorship resistance test (or flag if a larger testnet
is needed for f=2).

---

## 3. Pass criteria (from Phase 690 spec)

1. Censored epoch record achieves finality within **5 epoch durations**
2. Censorship attempt is **detectable from public validator behavior record** —
   not assumed, not inferred, demonstrated via logs or measurable divergence

Both must be satisfied for a PASS verdict.

---

## 4. Deliverables

| Artifact | Path |
|---|---|
| Results doc | `docs/research/ilc_mysticeti_workload_b_results_M014_v0.1.md` |
| Test file | `tests/test_phase_M014_workload_b_results.py` |
| Walkthrough (backfill) | `docs/phases/phase_M014_workload_b_walkthrough.md` |
| STATUS.md backfill | Append M-014 line with verdict and commit hash |

---

## 5. Two-commit pattern (mandatory)

**Commit 1 (main):** Results doc + test file. No walkthrough yet.  
**Commit 2 (backfill):** Walkthrough + STATUS.md tail update.

Both commits require a commit hash reported to me for audit. Do not merge the
commits.

---

## 6. Results doc required content

The results doc must contain:

1. **Testnet configuration** — N=4, F=1, validator IDs, which validator(s) were
   configured to censor, which submission node was the target
2. **f=1 deviation note** — explicit statement that Phase 690 specified f=2;
   explanation of why f=1 is a valid (or insufficient) test
3. **Censorship mechanism** — how the censoring validator was configured to
   exclude the target's records (e.g., dropped inbound from specific ValidatorID,
   filtered at message processing layer)
4. **Finality timeline** — epoch number where censored record was submitted,
   epoch number where it achieved finality, elapsed epoch durations (must be ≤5)
5. **Detectability evidence** — literal log lines or measurable behavior showing
   the censorship attempt was visible from public validator behavior (e.g.,
   `validator_id=N dropped EpochSettlementTx from validator_id=M` log line,
   or missing AckFor from censoring validator in the certificate)
6. **TLA+ Liveness connection** — one sentence connecting the result to TLA+ Spec A
   Liveness property (censoring minority cannot block finality in BFT quorum)
7. **Explicit pass/fail verdict** against Phase 690 criteria

---

## 7. Test file requirements

`tests/test_phase_M014_workload_b_results.py` must assert:

- Results doc exists at the exact path
- Results doc contains the finality evidence (literal epoch-finality log line or
  equivalent token from the actual run output)
- Results doc contains the f=1 deviation note (search for `f=1` or `deviation`)
- Results doc contains a detectability evidence block (literal log line showing
  censorship was observable)
- Results doc contains an explicit `PASS` or `FAIL` verdict token
- Results doc contains a reference to TLA+ Spec A Liveness
- Finality-in-5-epochs claim is present (search for `≤5` or `within 5`)

Minimum 7 tests. Do not write tests that can only pass by searching for generic
words — each test must anchor to a token that only appears if the actual
experimental procedure was followed.

---

## 8. SEC-007 advisory (carry-forward from SEC-007 patch)

The `install_default().ok()` call for the rustls crypto provider is currently
placed inside both `new_server()` and `new_client()` constructors. This is
functionally correct (`.ok()` absorbs the already-installed error), but the
recommended pattern is to call it once at `main()` startup.

If you touch `network.rs` or `main.rs` for M-014 (e.g., to add censorship
logging), add this cleanup: move `rustls::crypto::ring::default_provider().install_default().ok();`
to the top of `main()` in `src/main.rs` and remove it from the two constructors.

This is advisory — do not delay M-014 for it if it complicates the scope.
If not done in M-014, flag it as a carry-forward advisory for M-015.

---

## 9. Claude audit checklist (I will verify these)

- [ ] f=1 deviation from Phase 690 f=2 is explicitly stated in the results doc
- [ ] Censorship detectability is **demonstrated** — a literal log line or
  measurable divergence is present, not a claim that it "would be" detectable
- [ ] Finality timeline shows ≤5 epoch durations (not assumed, measured)
- [ ] Explicit PASS or FAIL verdict against Phase 690 criteria
- [ ] TLA+ Spec A Liveness connection is stated
- [ ] Test file has ≥7 tests, all anchored to literal run evidence
- [ ] Both commits reported (main + backfill)
- [ ] STATUS.md tail updated with M-014 line and commit hash
- [ ] No mutation to `ilc_core/` or `ilc_consensus/` constitutionally restricted
  files beyond what is required for the censorship mechanism itself

---

## 10. What comes after M-014

M-015 = Workload C: Partition/Heal/Recovery. Prerequisite: M-014 approved.  
Do not begin M-015 until M-014 is explicitly approved by me.
