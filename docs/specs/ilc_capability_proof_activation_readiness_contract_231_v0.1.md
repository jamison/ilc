# ILC Capability-Proof Activation Readiness Contract (Phase 231) v0.1

Status: Phase-231 readiness contract lock
Date: 2026-02-20
Owner lane: G8 Constitution Cluster A

## 1. Purpose and scope

Lock Gate A (CapProof Contract Freeze: Design -> Build) as deterministic, testable contract statements and preserve explicit deferred boundaries for Gates B-E.

This artifact is a readiness contract. It is not economic-policy ratification and it does not implement runtime behavior.

## 2. CapProof baseline lock (Gate A)

Gate A is PASS only when all criteria are satisfied:

1. Probe schemas are fixed and documented as canonical contract fields.
2. Tolerance rules are fixed and fail-closed for out-of-range or malformed values.
3. Validation behavior is fail-closed for malformed payloads, signature failures, or non-deterministic outputs.
4. No-direct-ILC-reward invariant is explicit: capability probes must not mint or allocate direct ILC rewards in this phase window.
5. No user-supplied kernels/backend hints invariant is explicit: payloads must not accept user-supplied kernel selectors, backend hints, or execution-engine override fields.
6. Canonical serialization and signing contract is fixed for CapProof payloads and attestations.

Normalization rule for this lock:
- Gate A wording from planning artifacts may be normalized only to improve specificity/testability.
- No normalization may relax any criterion or introduce policy content.

## 3. Current readiness assessment (assessment values only)

Values below are copied as current assessment values from the readiness-gates planning artifact and are not ratified targets.

| Surface | Implementation confidence (today) | Activation confidence (today) |
|---|---:|---:|
| CapProof (pricing/scheduling only) | 0.80 | 0.65 |
| Anchored Work Proofs / Intelligent Inference Hash (AWP/IIH) proof pipeline | 0.60 | 0.45 |
| AWP pool split (20%) policy coupling | 0.70 | 0.40 |
| Quality-Adjusted Tokens Per Second / Continuous Inference Token (QATPS/CIT) runtime reward coupling | 0.50 | 0.35 |
| Ingenuity scoring (barrier-mode) | 0.35 | 0.25 |

## 4. Explicit deferred boundaries

### 4.1 Anchored Work Proofs / Intelligent Inference Hash (AWP/IIH)
AWP/IIH must not be activated until Gate C pass criteria are satisfied (challenge-set generation unpredictability pre-epoch with reproducibility post-epoch, deterministic IIH bundle schema/hashing/signature verification, successful spot-audit recomputation, and fraud-detection/penalty signaling coverage).

### 4.2 Quality-Adjusted Tokens Per Second / Continuous Inference Token (QATPS/CIT)
QATPS/CIT runtime reward coupling must not be activated until Gate E pass criteria are satisfied, including adversarial throughput-validation coverage. Gaming surface is explicitly high-risk in this phase window.

### 4.3 Ingenuity scoring
Ingenuity scoring remains research-lane only in this window and must not be economically coupled in this phase.

### 4.4 AWP pool split (20%)
AWP pool split policy is not ratified in this window and must not be activated until Gate D economic-coupling decision criteria are satisfied.

## 5. CDL dependency statement

For production-grade activation, the following remain hard dependencies and unresolved open-CDL surfaces:
- `CDL-001`
- `CDL-002`
- `CDL-007`

No production-grade capability-proof economic activation is allowed before these dependency lanes are resolved through their required constitutional process.

## 6. Non-goals

This contract does not:
- ratify pool splits, thresholds, payout formulas, or tokenomics policy;
- implement any `ilc_core/` runtime behavior;
- advance or implement Gates B, C, D, or E;
- mutate CDL status fields.

## 7. Canonical anchors

- `docs/specs/ilc_capability_proof_activation_readiness_gates_v0.1.md`
- `docs/specs/ilc_pre_epoch_capability_proofs_v0.1.md`
- `docs/specs/capproof_kernels.md`
- `docs/specs/ilc_constitutional_decision_log_v0.1.md`
- `docs/specs/ilc_post_genesis_capability_proof_activation_sequence_230_239_v0.1.md`

## 8. Glossary

- Anchored Work Proofs (AWP): planned capability-proof lane for anchored challenge evidence.
- Intelligent Inference Hash (IIH): deterministic proof-bundle hashing lane paired with AWP.
- Quality-Adjusted Tokens Per Second (QATPS): throughput-quality metric lane for potential economic coupling.
- Continuous Inference Token (CIT): throughput-coupled tokenization lane referenced with QATPS.
