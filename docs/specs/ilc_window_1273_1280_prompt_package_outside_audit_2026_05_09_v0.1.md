# ILC Window 1273-1280 Prompt Package Outside Audit v0.1

Status: audit and hardening record
Date: 2026-05-09
Scope: Window 1273-1280 guidance docs and Phase 1273-1280 prompt drafts
Baseline commit audited: `aadeb055`

```text
window_1273_1280_prompt_package_outside_audit_2026_05_09.v0.1
planning_index_session_start_frontier_hardened_after_audit
window_1273_1280_audit_no_authority_expansion
```

## 1. Audit Scope

This audit reviewed the planning package committed at `aadeb055`:

- `docs/specs/ilc_window_1273_1280_candidate_phase_grouping_v0.1.md`
- `docs/antigravity_tasks/antigravity_prompt__phase_1273_g8_window_1273_1280_sequence_lock.md`
- `docs/antigravity_tasks/antigravity_prompt__phase_1274_g8_cdl048_conversion_sweeper_runtime_skeleton.md`
- `docs/antigravity_tasks/antigravity_prompt__phase_1275_g8_claimability_proof_binding_runtime_boundary.md`
- `docs/antigravity_tasks/antigravity_prompt__phase_1276_g8_cdl087_ratification_authorization_preflight.md`
- `docs/antigravity_tasks/antigravity_prompt__phase_1277_g8_transport_principal_public_path_adr_runtime_integration.md`
- `docs/antigravity_tasks/antigravity_prompt__phase_1278_g8_sidecar_non_loopback_public_path_preflight.md`
- `docs/antigravity_tasks/antigravity_prompt__phase_1279_g8_release_manifest_allowlist_prepublication_preflight.md`
- `docs/antigravity_tasks/antigravity_prompt__phase_1280_g8_window_1273_1280_closure_gate.md`
- `tests/test_window_1273_1280_prompt_drafts.py`
- `docs/PLANNING_INDEX.md`

The audit is outside-in relative to the package: it checks whether a cold
session or future executor would be routed correctly, whether prompt schemas are
valid, and whether the package accidentally widens authority.

## 2. Deterministic Checks

Checks performed:

- Re-read `docs/PLANNING_INDEX.md`, `docs/phases/STATUS.md`, the Phase 1272
  handoff, and the new Window 1273-1280 guidance.
- Re-validated every Phase 1273-1280 prompt with
  `tools/validate_phase_prompt.py`.
- Re-ran the prior Window 1265-1272 prompt regression to catch cross-window
  breakage.
- Rechecked CDL register diff.
- Rechecked sensitive-runtime guardrails.
- Rechecked whitespace/diff integrity for touched files.
- Manually reviewed guidance/prompt authority boundaries for ratification,
  public claimability, public serving, publication, release artifacts, Genesis
  mutation, and v0.2 signing.

## 3. Finding And Fix

Finding:

```text
planning_index_session_start_canon_stale_after_window_1273_1280_prompt_draft
```

The top of `docs/PLANNING_INDEX.md` and the Quick Reference already pointed to
the Window 1273-1280 planning draft, but the `## 1. Session-Start Canon` section
still marked the Window 1249-1256 handoff as current. That was a context-drift
risk because repo-local guidance tells new sessions to read Session-Start Canon
before phase work.

Fix:

```text
planning_index_session_start_frontier_hardened_after_audit
```

The Session-Start Canon now routes to:

- Window 1273-1280 planning-only guidance as the current planning draft.
- Window 1265-1272 handoff as the current closed-window handoff.
- Window 1265-1272 sequence lock and guidance as closed references.
- Older windows as closed references only.

A regression test now verifies that Session-Start Canon includes the current
planning draft and current handoff and no longer labels Window 1249-1256 as
current.

## 4. No-Authority-Expansion Result

This audit and hardening pass does not open Window 1273-1280, assign Phase
1273, authorize CDL-087 ratification, mutate any CDL row, activate public
claimability, enable wallet withdrawal/transfer/spend, expose public
sidecar/projection serving, publish source, produce release artifacts, mutate
Genesis, regenerate/sign Genesis Atlas, or authorize v0.2 signing.

```text
window_1273_1280_audit_no_authority_expansion
```

The next executable step remains a future Phase 1273 sequence lock after
explicit human `GO Phase 1273`.

## 5. Verification Commands

```text
.venv/bin/python -m pytest tests/test_window_1265_1272_prompt_drafts.py tests/test_window_1273_1280_prompt_drafts.py -q
.venv/bin/python tools/check_sensitive_runtime_coding_taboos.py
git diff -- docs/specs/ilc_constitutional_decision_log_v0.1.md
git diff --check -- docs/PLANNING_INDEX.md docs/specs/ilc_window_1273_1280_candidate_phase_grouping_v0.1.md docs/specs/ilc_window_1273_1280_prompt_package_outside_audit_2026_05_09_v0.1.md docs/antigravity_tasks/antigravity_prompt__phase_1273_g8_window_1273_1280_sequence_lock.md docs/antigravity_tasks/antigravity_prompt__phase_1274_g8_cdl048_conversion_sweeper_runtime_skeleton.md docs/antigravity_tasks/antigravity_prompt__phase_1275_g8_claimability_proof_binding_runtime_boundary.md docs/antigravity_tasks/antigravity_prompt__phase_1276_g8_cdl087_ratification_authorization_preflight.md docs/antigravity_tasks/antigravity_prompt__phase_1277_g8_transport_principal_public_path_adr_runtime_integration.md docs/antigravity_tasks/antigravity_prompt__phase_1278_g8_sidecar_non_loopback_public_path_preflight.md docs/antigravity_tasks/antigravity_prompt__phase_1279_g8_release_manifest_allowlist_prepublication_preflight.md docs/antigravity_tasks/antigravity_prompt__phase_1280_g8_window_1273_1280_closure_gate.md tests/test_window_1273_1280_prompt_drafts.py
```
