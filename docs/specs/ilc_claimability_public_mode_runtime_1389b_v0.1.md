# ILC Claimability Public-Mode Runtime 1389b v0.1

**Phase:** 1389b
**Date:** 2026-05-19
**Status:** COMPLETE - runtime blockers implemented; public serving still inactive
**Sensitivity:** SENSITIVE runtime phase
**Runtime commit:** `aed33474`

```text
claimability_public_mode_runtime_phase_1389b
claim_nullifier_registry_v1_active_phase_1389b
duplicate_claim_registry_active_phase_1389b
claimability_verifier_public_mode_ready_phase_1389b
public_mode_blockers_empty_phase_1389b
```

## 1. Authorization

Phase 1389b executed after explicit human authorization:

```text
GO Phase 1389b
```

The earlier message that routed Phase 1389b after Phase 1397a was corrected by
the user as a fat-finger. The controlling authorization is same-day Phase 1389b
after Phase 1389a completed.

## 2. Verdict

Runtime commit `aed33474` implements the two runtime blockers preserved by
Phase 1389a:

```text
replay_nullifier_policy_not_activated_phase_1305
duplicate_claim_registry_not_activated_phase_1305
```

`ilc_core/sidecars/claimability_receipt_verifier.py` now has:

```text
_PUBLIC_MODE_BLOCKERS: tuple[str, ...] = ()
```

Verifier decisions therefore produce:

```text
public_mode_blockers=[]
```

This means the claimability verifier is public-mode-ready as an in-process
admission/verifier runtime. It does not mean public HTTP serving, public socket
serving, wallet actions, ECU minting, ILC settlement, public RC publication, or
mainnet launch are active.

## 3. Claim Verification

| Claim | File or symbol checked | Result |
|-------|------------------------|--------|
| Phase 1389a closed governance blockers and preserved runtime blockers | `docs/specs/ilc_claimability_public_mode_governance_decisions_1389a_v0.1.md` | confirmed |
| Phase 1377 defines `claim_nullifier_v1` and `claim_nullifier_registry_v1` policy | `docs/specs/ilc_replay_nullifier_policy_1377_v0.1.md` | confirmed |
| Verifier previously hardcoded five public-mode blockers | pre-1389b `ilc_core/sidecars/claimability_receipt_verifier.py` | confirmed by Phase 1389 report and 1389a disposition |
| Runtime commit adds an in-process nullifier registry | `ilc_core/sidecars/claim_nullifier_registry_v1.py` | confirmed |
| Runtime commit empties `_PUBLIC_MODE_BLOCKERS` | `ilc_core/sidecars/claimability_receipt_verifier.py` | confirmed |
| Public/wallet/economic activation flags remain false | `claimability_receipt_verifier.py`; Phase 1389b tests | confirmed |
| Phase 1389 gate has not been rerun | `docs/specs/ilc_public_claimability_activation_gate_report_1389_v0.1.md`; STATUS | confirmed |

## 4. Runtime Changes

Runtime commit `aed33474` adds:

| File | Change |
|------|--------|
| `ilc_core/sidecars/claim_nullifier_registry_v1.py` | New in-process `ClaimNullifierRegistry`; derives `claim_nullifier_v1`; tracks active nullifier, presentation, proof, conversion receipt, and conversion lot conflicts. |
| `ilc_core/sidecars/claimability_receipt_verifier.py` | Adds optional `claim_registry` admission path; rejects replay/duplicate claims before verifier processing; marks invalid reserved claims `rejected_nonblocking`; adds Phase 1389a/1389b tokens; empties `_PUBLIC_MODE_BLOCKERS`. |
| `ilc_core/sidecars/__init__.py` | Exports `claim_nullifier_registry_v1`. |
| tests | Adds Phase 1389b focused tests and updates affected historical claimability tests. |

## 5. Nullifier Construction

The registry implements Phase 1377's domain-separated canonical construction:

```text
version = claim_nullifier_registry_v1
domain = ilc-public-claim-nullifier-v1
claim_nullifier_ref = claim_nullifier_sha256:<64 lowercase hex>
```

Hashing uses deterministic JSON:

```text
json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
```

No wall-clock time is used. Admission uses issuance epochs. Claims before the
claim window are rejected with:

```text
claim_window_not_open_phase_1389b
```

Claims after the deadline epoch are rejected with:

```text
claim_window_closed_phase_1389b
```

## 6. Admission Semantics

When a `ClaimNullifierRegistry` is passed to
`verify_claimability_receipt_presentation(...)`, the verifier now performs:

1. Atomic in-process reservation attempt.
2. Active nullifier replay check.
3. Active duplicate checks for presentation id, canonical presentation hash,
   claimability proof ref, conversion receipt, and conversion lot.
4. Verifier normalization and decision construction.
5. Accepted claims marked `accepted` with a decision ref.
6. Invalid reserved claims marked `rejected_nonblocking` so invalid garbage does
   not permanently block a later valid claim.

Replay rejection token:

```text
claim_nullifier_replay_rejected_phase_1389b
```

Duplicate claim rejection token:

```text
duplicate_claim_rejected_at_api_layer
```

## 7. Tests

Focused runtime tests prove:

| Test surface | Result |
|--------------|--------|
| Public-mode blockers empty in produced decision | PASS |
| Phase 1389a/1389b verifier tokens present | PASS |
| Replayed presentation rejected by active nullifier | PASS |
| Duplicate material with different presentation id rejected at API layer | PASS |
| Invalid reserved presentation becomes nonblocking and does not block later valid claim | PASS |
| Closed and premature claim windows rejected by issuance epoch | PASS |

Verification commands passed:

```text
.venv/bin/python -m pytest tests/test_phase_1389b_claimability_public_mode_runtime.py -q
.venv/bin/python -m pytest tests/test_phase_1305_offline_claimability_receipt_verifier_sidecar_library.py tests/test_phase_1306_proof_binding_canonical_hash_negative_path_tests.py tests/test_phase_1389_public_claimability_activation_gate.py tests/test_phase_1389a_claimability_public_mode_governance_decisions.py tests/test_sensitive_runtime_coding_taboos.py -q
.venv/bin/python -m py_compile ilc_core/sidecars/claim_nullifier_registry_v1.py ilc_core/sidecars/claimability_receipt_verifier.py
```

## 8. Non-Authorizations

Phase 1389b does not:

- rerun Phase 1389;
- activate public claimability;
- activate public verifier API serving;
- activate public claim endpoint serving;
- add a public HTTP route;
- add a socket listener;
- enable wallet withdrawal, transfer, or spend;
- authorize ECU minting;
- authorize ILC settlement;
- authorize public RC publication;
- authorize mainnet launch;
- mutate the CDL register;
- claim external legal advice, counsel approval by external counsel, or legal conclusion.

## 9. Handoff

The next public-claimability step is a Phase 1389 gate rerun or successor gate
that direct-reads the Phase 1389b runtime evidence and confirms the verifier no
longer carries public-mode blockers. Until that rerun occurs, the historical
Phase 1389 failed-closed report remains the last public claimability gate
verdict.

## 10. Graph Delta

```text
graph_delta=load_bearing_artifact_changed:ilc_core/sidecars/claimability_receipt_verifier.py,ilc_core/sidecars/claim_nullifier_registry_v1.py -> public-claimability/runtime-admission
```
