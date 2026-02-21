# ILC Phase 251-253 Post-Review Errata v0.1

Status: Active audit-trace artifact
Date: 2026-02-21
Scope: Post-execution corrections after deep review of Phase 251, 252, and 253 walkthroughs, decision-log mutations, and tests.

## 1. Purpose

Record the specific discrepancies found after Phase 251-253 execution, the applied fixes, and the verification evidence proving closure.

## 2. Issues identified

1. Legacy test expectation drift:
   - `tests/test_cdl_011_015_ratification_evidence_phase_215.py` still expected `CDL-001`, `CDL-002`, and `CDL-007` to be `open`.
   - After Phase 251, those rows are `ratified`.

2. Phase-253 decision-log mutation scope drift:
   - CDL-032 row included an extra `current_candidate` normalization beyond the prompt's intended mutation surface.

3. Ratification evidence provenance anchor weakness:
   - `docs/specs/ilc_cdl_032_cli_first_sdk_ratification_evidence_253_v0.1.md` referenced non-tracked source docs in narrative provenance.

4. Walkthrough touched-file underreporting:
   - Phase 252 walkthrough did not list a walkthrough file that was modified in the Phase 252 commit.

## 3. Remediation applied

Applied in commit: `d9f14aa`

Changed files:
- `tests/test_cdl_011_015_ratification_evidence_phase_215.py`
  - Updated expected statuses for `CDL-001/002/007` from `open` to `ratified`.
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
  - Restored CDL-032 `current_candidate` wording to preserve mutation-scope discipline.
- `docs/specs/ilc_cdl_032_cli_first_sdk_ratification_evidence_253_v0.1.md`
  - Replaced non-tracked provenance phrasing with tracked/canonical anchors.
- `docs/phases/phase_252_g8_constitution_cluster_a_security_cdl_ratification_verification_gate_walkthrough.md`
  - Added the missing modified-file disclosure.
- `docs/phases/phase_253_g8_constitution_cluster_a_cdl_032_ratification_and_d2e_01_cli_surface_lock_walkthrough.md`
  - Synced before/after row evidence to corrected decision-log content.
- `tests/test_cdl_032_ratification_253.py`
  - Added an assertion that guards CDL-032 candidate text from accidental drift.

## 4. Verification evidence

All checks passed after patch:

```bash
python3 -m pytest tests/test_cdl_011_015_ratification_evidence_phase_215.py -q
python3 -m pytest tests/test_security_cdl_ratification_251.py -q
python3 -m pytest tests/test_cdl_032_ratification_253.py -q
python3 -m pytest tests/test_security_ratification_gate_252.py -q
python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q
```

Additionally, full verification command stacks for Phase 251, Phase 252, and Phase 253 were re-executed and passed.

## 5. Outcome

The Phase 251-253 governance and documentation trail is now internally consistent:
- decision-log mutations align with prompt mutation boundaries,
- ratification evidence references tracked anchors,
- regression tests reflect current CDL state,
- walkthrough file-ledger accuracy is restored.
