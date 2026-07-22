# ILC CCSS HyperNova/Folding Feasibility Memo 1576f v0.1

**Phase:** 1576f
**Window:** 1576+
**Date:** 2026-07-22
**Status:** committed
**Sensitivity:** NON-SENSITIVE

## 1. Purpose and Scope

This memo evaluates whether HyperNova-style folding is a practical future proof
compression layer for CCSS privacy-compliance evidence. The relevant CCSS
surfaces are PrivacyChart membership, productive-cover validity, batch
composition compliance, and threshold-envelope metadata compliance.

This is not a commitment to implement HyperNova. It is not a first-runtime
dependency for Phases 1576b-1576e, and it does not activate any proof system.

Output token: `hypernova_ccss_feasibility_memo_complete_phase_1576f`.

## 2. Direct Evidence and Literature

| Source | Finding Used Here |
| --- | --- |
| `docs/specs/ilc_ccss_privacy_chart_manifest_and_productive_cover_design_1576b_v0.1.md` | Defines `folded_proof_step` as a productive cover class and defines batch/cell compliance targets. |
| `docs/specs/ilc_ccss_graph_diffused_threshold_envelope_design_1576c_v0.1.md` | Defines fixed-size threshold envelopes, `m=3,n=7`, share unlinkability, and relay cheap-check boundary. |
| `docs/specs/ilc_ccss_multi_trapdoor_and_contact_gate_integration_1576e_v0.1.md` | Defines fit-tag, trapdoor, and ContactGate fields that future compliance proofs would need to bind. |
| IACR ePrint 2023/573, HyperNova | HyperNova is a recursive argument for incremental computations expressed in CCS; CCS generalizes Plonkish, R1CS, and AIR. The abstract describes folding multiple instances and an a-la-carte cost profile for stateful machine steps. |
| USENIX Security 2017, Loopix | Loopix uses cover traffic and Poisson mixing/delays for traffic-analysis resistance, including against strong passive adversaries; this supports ILC's conclusion that folding proves compliance, not timing unlinkability. |

Repository search found no HyperNova, Nova, SNARK, STARK, Plonk, or IVC runtime
implementation in `ilc_core`. Existing proof-adjacent machinery is hash,
commitment, Merkle, signature, replay-proof, capability-proof, and
Merkle-Laplacian scaffolding. Those are appropriate first-runtime building
blocks.

## 3. What Needs to Be Proved

| Claim | Proof Would Attest | Prover | Verifier |
| --- | --- | --- | --- |
| PrivacyChart membership | Sender is in a cell whose `member_count >= k_min`. | Sender or chart issuer. | Relay or auditor. |
| Productive cover validity | Cover envelope carries an approved real ILC operation. | Sender or relay. | Auditor. |
| Batch composition compliance | Released batch has fixed-size envelopes, enough envelopes, and required cover ratio. | Relay. | Auditor. |
| Threshold-envelope metadata compliance | Relay-visible fields omit share index, `m`, `n`, raw capability id, recipient identity, and role structure. | Sender or relay. | Relay or auditor. |
| Fit-tag compliance | Fit-tag is epoch-bound, nonce-bound, constant-size, and cheap to reject. | Sender. | Relay. |

Share unlinkability cannot be proved by folding alone. Folding can prove that a
batch obeyed declared metadata constraints; it cannot prove global network
unlinkability or defeat a GPO timing adversary.

## 4. HyperNova Primer for This Use Case

HyperNova is relevant because CCSS compliance is naturally incremental:
validate one envelope, fold it into an accumulator, and eventually publish one
epoch-level aggregate proof for a cell/window.

| Property | Practical Meaning for CCSS |
| --- | --- |
| Customizable constraint systems | A single framework can encode hash checks, Merkle membership checks, fixed-size checks, and batch counters. |
| Folding / IVC | Many per-envelope checks can be accumulated into one proof object. |
| Transparent posture | The literature presents HyperNova as avoiding a trusted setup, which fits ILC's no-new-trusted-party preference. |
| Off-critical-path suitability | Epoch proof generation can happen after release as audit evidence instead of blocking relay release. |

Cost boundary: this repo has not benchmarked HyperNova. Any concrete prover
latency estimate is therefore a planning placeholder, not ILC evidence. Before
implementation, a dedicated benchmark phase must measure prover time, verifier
time, memory, proof size, and hardware variance on the target VPS class.

## 5. Feasibility Verdict

| Candidate Proof | Verdict | Reason |
| --- | --- | --- |
| PrivacyChart membership | Feasible later; use Merkle first. | Merkle paths give a cheap first implementation. Folding may compress many checks later. |
| Batch composition compliance | Feasible off critical path. | Relay can publish hash/Merkle receipts first, then fold audit checks after release. |
| Productive cover validity | Feasible but expensive/late. | Cover ratio 8 means many proof generations per logical message; this should wait for benchmark evidence. |
| Threshold-envelope metadata compliance | Feasible as audit proof. | Fixed-size/forbidden-field compliance is constraint-friendly. |
| GPO resistance | Not a folding problem. | Requires L6 relay shuffle/mix and timing analysis. |

Output token: `ccss_proof_compression_path_documented_phase_1576f`.

## 6. Recommended Path

First implementation:

- use hash commitments for batch composition receipts;
- use Merkle paths for PrivacyChart membership;
- use fit-tag verification for relay routing;
- keep all CCSS privacy runtime default-off until a later implementation phase.

Second phase, Window 1577+:

- introduce HyperNova-style folding for epoch-level batch-compliance audit
  receipts;
- fold post-release relay evidence off the critical path;
- benchmark prover/verifier costs before any runtime dependency is created.

Third phase, long range:

- evaluate productive-cover validity folding only after sender-side prover cost
  is demonstrated low enough for ordinary nodes;
- treat `folded_proof_step` as productive cover only after that evidence exists.

HyperNova folding is a viable long-term proof compression layer for CCSS batch
compliance and PrivacyChart membership. It is not a first-runtime dependency
for Phases 1576b-1576e. The first implementation uses hash-based commitment
and Merkle-path membership proofs.

Folding proves compliance, not unlinkability. GPO resistance still requires L6
relay shuffle.

## 7. Literature Comparison

| System | Mechanism | ILC Similarity | ILC Difference |
| --- | --- | --- | --- |
| Chaum mixnet | Fixed-size re-encryption shuffle. | ILC future L6 needs shuffle/mix behavior. | ILC adds graph-native PrivacyChart cohorts and productive cover. |
| Loopix | Cover traffic plus stochastic delay/mixing. | ILC also needs cover and timing defenses for GPO resistance. | ILC cover is intended to carry useful graph work, not only dummy loops. |
| Riffle | Verifiable shuffle and PIR-style ideas. | ILC can learn from verifiable shuffle audit patterns. | ILC threshold envelopes are graph-cell routed and not currently PIR-based. |
| HyperNova | Folding for customizable constraint systems. | Candidate epoch proof compressor for compliance evidence. | Not a first-runtime privacy mechanism and not a mixnet. |

## 8. Non-Claims

This memo does not:

- implement HyperNova;
- activate any proof runtime;
- clear any CCSS, D2D, ContactGate, cover, batching, or trapdoor guard;
- claim folding provides anonymity or GPO resistance;
- claim a measured HyperNova cost for ILC;
- claim productive-cover proof generation is affordable today;
- block first-runtime CCSS implementation from using hash/Merkle evidence.

## 9. Completion Tokens

```text
hypernova_ccss_feasibility_memo_complete_phase_1576f
ccss_proof_compression_path_documented_phase_1576f
```
