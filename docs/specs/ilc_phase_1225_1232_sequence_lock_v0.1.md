# ILC Phase 1225-1232 Sequence Lock v0.1

**Date:** 2026-05-06
**Window:** 1225-1232
**Phase:** 1225
**Status:** LOCKED
**Human authorization:** `GO Phase 1225`
**Token:** `window_1225_1232_sequence_lock_committed`

---

## 1. Sequence Lock Verdict

Window 1225-1232 is opened after explicit human authorization token
`GO Phase 1225`.

Verdict:

```text
window_1225_1232_sequence_lock_verdict=pass
window_1225_1232_sequence_lock_committed
```

This phase locks the Window 1225-1232 order, sensitive gates, carry-forward
tokens, and entry-state anchors. It does not mutate the CDL register, runtime
code, signed Genesis v0.1, the Genesis Atlas, any release key, or any public
release artifact.

---

## 2. Baseline Commits

| Commit | Role |
|--------|------|
| `71a6d168` | Window 1218-1224 closure gate PASS |
| `052d62b5` | Phase 1224 Fix1 post-closure code-audit hardening |
| `21a5ad86` | `canon_bundle_key_registry.py` dirty-file disposition resolved before this lock |
| `e9548664` | Window 1225-1232 candidate guidance draft |
| `e4486d9a` | Window 1225-1232 guidance corrections and open-decision resolution |

Capsule v5.48 remains the current capsule entering this window. Phase 1224
handoff and Phase 1224 Fix1 are newer than the capsule and govern closure/audit
delta until capsule v5.49 is published in Phase 1231.

---

## 3. Immutable Anchors

| Anchor | Value |
|--------|-------|
| Genesis v0.1 signed root envelope | `ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c` |
| Immutable diagnostic SHA | `5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56` |
| Genesis v0.2 candidate | 41-node / 73-edge candidate; unsigned; signing deferred by default |
| Capsule | v5.48 |

Preflight check confirmed the immutable diagnostic working-tree file matches the
recorded SHA at sequence-lock entry.

---

## 4. RC Gate State at Window Entry

RC2 is effectively complete except v0.2 signing:

| Gate | State |
|------|-------|
| Gate 1 — CDL-085 / φ-bound | SATISFIED |
| Gate 2 — v0.2 signing | OPEN / deferred |
| Gate 3 — Tier-3 runtime linkage | SATISFIED |
| Gate 4 — public-launch packaging blocker | RATIFIED; public-launch acts still separately blocked |
| Gate 5 — fetch/rate-limiter boundary | WIRED + audit-hardened + fetch distribution reframed |
| Gate 6 — truth-primitive permanence | Genesis-attested |

Window 1225-1232 is RC3-adjacent implementation work, not a public launch or
public repository publication window.

---

## 5. Locked Phase Order

| Order | Phase | Topic | Sensitivity | Gate |
|-------|-------|-------|-------------|------|
| 1 | 1225 | Window sequence lock | SENSITIVE | `GO Phase 1225` consumed |
| 2 | 1226 | `commit.epoch` causal frontier mapping spec | NON-SENSITIVE | May proceed after this lock |
| 3 | 1227 | CDL-087 opening — canonical fetch distribution policy | SENSITIVE | Requires `GO Phase 1227` and CDL mutation env |
| 4 | 1228 | CDL-087 prelock + fetch distribution spec hardening | SENSITIVE | Requires `GO Phase 1228`; no CDL mutation env |
| 5 | 1229 | Agent graph projection interface runtime implementation | NON-SENSITIVE | Runtime-only; no CDL mutation |
| 6 | 1230 | v0.2 signing ceremony | conditional | Skip-default unless signing token + `GO Phase 1230` |
| 7 | 1231 | Coherence report + capsule v5.49 | NON-SENSITIVE | After 1229 / 1230 disposition |
| 8 | 1232 | Window closure gate | SENSITIVE | Requires `GO Phase 1232` |

Sensitive phases require separate explicit human authorization even if adjacent
non-sensitive phases are executed in sequence.

---

## 6. Sensitive Gate Rules

### Phase 1227 CDL mutation

Phase 1227 opens CDL-087 and requires:

```text
GO Phase 1227
ILC_CDL_MUTATION_AUTHORIZED=1
ILC_CDL_MUTATION_PHASE=1227
```

### Phase 1228 prelock sensitivity

Phase 1228 resolves Q1-Q5 and locks the CDL-087 ratification path. It is
SENSITIVE even without a CDL register mutation. It requires:

```text
GO Phase 1228
```

No CDL mutation environment variable is required for Phase 1228.

### Phase 1230 signing slot

Phase 1230 is skip-default. It executes as a signing ceremony only if both are
present:

```text
v0_2_signing_ceremony_authorized_phase_1230
GO Phase 1230
```

If either is absent, Phase 1230 records:

```text
v0_2_signing_ceremony_deferred_pending_signing_authorization
```

---

## 7. Carry-Forward Tokens

| Token | Window 1225-1232 routing |
|-------|--------------------------|
| `commit_epoch_causal_frontier_mapping_spec_required` | Phase 1226 |
| `fetch_distribution_architecture_reframed_phase_1222` | Phase 1227 / Phase 1228 |
| `agent_graph_projection_interface_implementation_required_window_1225_plus` | Phase 1229 |
| `l3_sidecar_infrastructure_spec_required_window_1225_plus` | Deferred to Window 1233+ |
| `v0_2_signing_ceremony_deferred_pending_signing_authorization` | Phase 1230 skip-default |
| `genesis_canonical_lineage_contract_required_before_public_rc` | Deferred; not satisfied by this window |
| `counsel_license_instrument_selection_required_before_public_rc` | Parallel counsel lane |
| `counsel_cla_text_approved_required_before_external_contributors` | Parallel counsel lane |
| `counsel_trademark_policy_published_required_before_public_launch` | Parallel counsel lane |
| `allowlist_export_procedure_defined_required_before_public_repo_publication` | Deferred public-repo-publication precondition |

---

## 8. Resolved Open Decisions

| Decision | Resolution |
|----------|------------|
| v0.2 signing | Deferred by default; Phase 1230 is skip-default |
| `canon_bundle_key_registry.py` dirty file | Resolved before sequence lock in `21a5ad86` |
| `ilc_core/graph/` location | Approved for Phase 1229 as `ilc_core/graph/__init__.py` and `ilc_core/graph/agent_graph_projection_runtime.py` |
| L3 visualization sidecar | Deferred to Window 1233+; Phase 1229 is machine-native projection substrate only |

---

## 9. CDL Number Lock

The CDL register contains CDL-086 as ratified. No CDL-087 row exists at window
entry. The next fresh CDL number is:

```text
CDL-087
```

Window 1225-1232 assigns CDL-087 to:

```text
Canonical fetch distribution policy
```

CDL-087 opens in Phase 1227 and prelocks in Phase 1228. Ratification is not
assigned to this window and remains gated behind SIM-FETCH-01 in Window 1233+.

---

## 10. Non-Authorization Boundary

This sequence lock does not authorize:

- public launch
- public RC claim
- public repository publication
- public release artifact distribution
- external contributor onboarding
- external operator bootstrap
- v0.2 signing
- release-key generation
- release envelope production
- signed Genesis v0.1 mutation
- Genesis Atlas mutation
- CDL-087 opening without `GO Phase 1227`
- CDL-087 prelock without `GO Phase 1228`
- CDL-087 ratification

---

## 11. Next Phase

Next planned phase:

```text
Phase 1226 — commit.epoch causal frontier mapping spec
```

Phase 1226 is NON-SENSITIVE and may proceed after this sequence lock under the
locked ordering.
