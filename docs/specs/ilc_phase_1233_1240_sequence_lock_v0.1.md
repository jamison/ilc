# ILC Phase 1233-1240 Sequence Lock v0.1

**Date:** 2026-05-06
**Window:** 1233-1240
**Phase:** 1233
**Status:** LOCKED
**Human authorization:** `GO Phase 1233`
**Token:** `window_1233_1240_sequence_lock_committed`

---

## 1. Sequence Lock Verdict

Window 1233-1240 is opened after explicit human authorization token:

```text
GO Phase 1233
```

Verdict:

```text
window_1233_1240_sequence_lock_verdict=pass
window_1233_1240_sequence_lock_committed
```

This phase locks the Window 1233-1240 order, sensitive gates, carry-forward
tokens, and entry-state anchors. It does not mutate the CDL register, runtime
code, signed Genesis v0.1, the Genesis Atlas, release keys, or any public release
artifact.

---

## 2. Baseline Commits

| Commit | Role |
|--------|------|
| `e1ce3aa1` | Window 1225-1232 closure gate PASS |
| `ec0485dd` | Corrected Window 1233-1240 guidance and prompt set |
| `1ae47087` | Claim-verification controls and superseded `commit.epoch` draft tombstones |

Window 1225-1232 is CLOSED through Phase 1232 with:

```text
window_1225_1232_closed_phase_1232
window_1225_1232_closure_gate_verdict=pass
```

Current capsule entering this window:

```text
docs/specs/ilc_antigravity_context_capsule_v5.49.md
```

Current handoff:

```text
docs/specs/ilc_window_1225_1232_handoff_1232_v0.1.md
```

Capsule v5.49 was produced before Phase 1232 closure. The Phase 1232 handoff and
this sequence lock govern the closure delta until capsule v5.50 is published in
Phase 1239.

---

## 3. Immutable Anchors

| Anchor | Value |
|--------|-------|
| Genesis v0.1 signed root envelope | `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Immutable diagnostic SHA | `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56` |
| Genesis v0.2 candidate | 41-node / 73-edge candidate; unsigned; signing deferred |
| Capsule | v5.49 |

Preflight confirmed the immutable diagnostic working-tree file matches the
recorded SHA at sequence-lock entry.

---

## 4. Entry Preflight

Phase 1233 preflight confirmed:

```text
tests/test_phase_1232_window_1225_1232_closure_gate.py: 16 passed, 1 skipped
tools/check_sensitive_runtime_coding_taboos.py: PASS
out/genesis_compile_coverage_diagnostic_v0.1.json: 5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56
git diff --exit-code -- ilc_core/: clean
```

The system `python3` points to an interpreter without pytest in this environment;
the project `.venv/bin/python` is the verified test runner for this lock.

---

## 5. CDL and Signing State at Window Entry

CDL-087:

```text
OPEN / PRELOCKED / NOT RATIFIED
cdl_087_canonical_fetch_distribution_policy_opened_phase_1227
cdl_087_prelock_committed_phase_1228
cdl_087_not_ratified_phase_1228
```

CDL-087 ratification remains gated by SIM-FETCH-01 and all six Phase 1228
ratification conditions. No phantom ratification occurred.

Next fresh CDL number:

```text
CDL-088
```

CDL-088 must not be opened without explicit future authorization.

v0.2 signing remains deferred:

```text
v0_2_signing_ceremony_deferred_pending_signing_authorization
```

No signing ceremony executed, no release key was generated or registered, and no
release envelope was produced.

---

## 6. Locked Phase Order

| Order | Phase | Topic | Sensitivity | Gate |
|-------|-------|-------|-------------|------|
| 1 | 1233 | Window sequence lock | **SENSITIVE** | `GO Phase 1233` consumed |
| 2 | 1234 | `commit.epoch` audit: call-site inventory + `vote_weight` scope + mutation plan | NON-SENSITIVE | May proceed after this lock |
| 3 | 1235 | `commit.epoch` canonical runtime mutation | **SENSITIVE** | Requires `GO Phase 1235` |
| 4 | 1236 | `commit.epoch` emission connector spec/stub | **SENSITIVE** | Requires `GO Phase 1236` |
| 5 | 1237 | L3 sidecar infrastructure spec | NON-SENSITIVE | After Phase 1236 disposition |
| 6 | 1238 | SIM-FETCH-01 harness and design | NON-SENSITIVE | After Phase 1237 |
| 7 | 1239 | Coherence report + capsule v5.50 | NON-SENSITIVE | After Phase 1238 |
| 8 | 1240 | Window closure gate | **SENSITIVE** | Requires `GO Phase 1240` |

Sensitive phases require separate explicit human authorization even if adjacent
non-sensitive phases are executed in sequence.

---

## 7. Sensitive Gate Rules

### Phase 1235 canonical runtime mutation

Phase 1235 mutates active `commit.epoch` finality-surface runtime and requires:

```text
GO Phase 1235
```

### Phase 1236 emission connector

Phase 1236 creates finality-surface connector infrastructure and requires:

```text
GO Phase 1236
```

Production `commit.epoch` emission remains separately gated after Phase 1236.

### Phase 1240 closure gate

Phase 1240 is SENSITIVE and requires:

```text
GO Phase 1240
```

---

## 8. Active Carry-Forward Tokens

| Token | Window 1233-1240 routing |
|-------|--------------------------|
| `commit_epoch_projection_runtime_required_before_production_emission` | Phases 1234-1236 |
| `l3_sidecar_infrastructure_spec_required_window_1225_plus` | Phase 1237 |
| `cdl_087_ratification_deferred_pending_sim_fetch_01` | Phase 1238 harness/design only; ratification deferred |
| `v0_2_signing_ceremony_deferred_pending_signing_authorization` | Carries forward; no signing this window |
| `allowlist_export_procedure_defined_required_before_public_repo_publication` | Deferred to Window 1241+ |
| `genesis_canonical_lineage_contract_required_before_public_rc` | Deferred; not satisfied by this window |
| `counsel_license_instrument_selection_required_before_public_rc` | Parallel counsel lane |
| `counsel_cla_text_approved_required_before_external_contributors` | Parallel counsel lane |
| `counsel_trademark_policy_published_required_before_public_launch` | Parallel counsel lane |

---

## 9. Non-Authorization Boundary

This sequence lock does not authorize:

- CDL-087 ratification;
- CDL-077 amendment;
- CDL-088 opening;
- reciprocal scoring CDL opening;
- v0.2 signing;
- public launch;
- public RC claim;
- public repository publication;
- public release artifact distribution;
- external contributor onboarding;
- external operator bootstrap;
- release-key generation;
- release envelope production;
- signed Genesis v0.1 mutation;
- Genesis Atlas mutation;
- immutable diagnostic mutation;
- production `commit.epoch` emission authorization;
- lineage receipt / allowlist export tooling implementation.

---

## 10. Next Phase

Next planned phase:

```text
Phase 1234 — commit.epoch audit: call-site inventory + vote_weight scope + mutation plan
```

Phase 1234 is NON-SENSITIVE and may proceed after this sequence lock under the
locked ordering. It is audit-only and must not mutate `ilc_core/`.
