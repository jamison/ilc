# ILC Jury / Epoch-Work Prompt Hardening Audit 1391-1398 v0.1

**Date:** 2026-05-19
**Status:** complete
**Scope:** prompt drafting and hardening only

## 1. Purpose

This audit records the hardening pass for the J-series jury and epoch-work
canonicalization prompt drafts mapped to future numeric phases 1391-1398.

The prompts are future-window drafts. They do not execute runtime changes,
activate public ingestion, activate reviewer payments, mutate CDLs, or assert
production jury service.

## 2. Prompt Set

| J phase | Numeric draft | Prompt |
|---------|---------------|--------|
| J-001 | 1391 | `docs/antigravity_tasks/antigravity_prompt__phase_1391_g8_jury_epoch_work_canon_map.md` |
| J-002 | 1392 | `docs/antigravity_tasks/antigravity_prompt__phase_1392_g8_jury_eligibility_assignment_adr.md` |
| J-003 | 1393 | `docs/antigravity_tasks/antigravity_prompt__phase_1393_g8_public_node_review_taxonomy.md` |
| J-004 | 1394 | `docs/antigravity_tasks/antigravity_prompt__phase_1394_g8_jury_incentive_economics_cdl_opening.md` |
| J-005 | 1395 | `docs/antigravity_tasks/antigravity_prompt__phase_1395_g8_epoch_start_capability_maintenance_contract.md` |
| J-006 | 1396 | `docs/antigravity_tasks/antigravity_prompt__phase_1396_g8_default_off_jury_assignment_quote_runtime.md` |
| J-007 | 1397 | `docs/antigravity_tasks/antigravity_prompt__phase_1397_g8_shadow_public_ingestion_jury_harness.md` |
| J-008 | 1398 | `docs/antigravity_tasks/antigravity_prompt__phase_1398_g8_production_jury_activation_gate_definition.md` |

## 3. Hardening Checks

| Check | Result |
|-------|--------|
| Numeric filename schema accepted by `tools/validate_phase_prompt.py` | PASS |
| H1 phase/group matches filename | PASS |
| Required schema sections present | PASS |
| Phase 1249+ unknown-unknown discovery subsections present | PASS |
| Exact walkthrough no-ellipsis rule present | PASS |
| `STATUS.md` update requirement present | PASS |
| Execution ordering present: tests, green confirmation, walkthrough + STATUS, re-run checks, commit, completion | PASS |
| Output tokens marked as not-preexisting in §0a | PASS |
| Future-window / human-GO execution boundary included | PASS |
| Non-obligatory jury participation boundary included | PASS |
| Runtime phases J-006/J-007 marked SENSITIVE and default-off/shadow-only | PASS |
| Reviewer payment and production jury activation non-claims preserved | PASS |

## 4. Validator Command

```bash
for f in docs/antigravity_tasks/antigravity_prompt__phase_139{1,2,3,4,5,6,7,8}_g8_*.md; do
  python3 tools/validate_phase_prompt.py "$f" || exit 1
done
```

Result: all eight prompts returned `VALID`.

## 5. Design Hardening Notes

The prompts deliberately separate four concerns:

1. **Canon recovery** before implementation.
2. **ADR/CDL decisions** before runtime activation.
3. **Default-off quote/runtime work** before shadow harness work.
4. **Production activation gate definition** before any future production jury
   service or reviewer payment activation.

The prompts also preserve these non-claims:

```text
connected_agents_are_not_obligated_to_jury_service
reviewer_payment_not_activated_by_prompt_drafting
production_jury_service_not_activated_by_prompt_drafting
public_graph_permanence_not_activated_by_prompt_drafting
```

## 6. Commit Scope

This prompt-hardening commit should include only:

- the eight future phase prompt drafts;
- `docs/specs/ilc_jury_epoch_work_canonicalization_phase_plan_v0.1.md`;
- this audit document.

Existing dirty worktree files from other work streams should not be staged.
