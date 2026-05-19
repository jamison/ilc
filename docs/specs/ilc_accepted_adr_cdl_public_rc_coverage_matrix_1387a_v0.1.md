# ILC Accepted ADR/CDL Public-RC Coverage Matrix 1387a v0.1

**Phase:** 1387a
**Date:** 2026-05-19
**Status:** PASS — no unknown rows and no public-RC blocking rows
**Scope:** accepted ADR corpus plus ratified CDL register through CDL-090

```text
accepted_adr_cdl_coverage_phase_1387a_executed
accepted_adr_cdl_runtime_coverage_matrix_phase_1387a
public_economics_requires_public_node_admission_verified_phase_1387a
private_visibility_excluded_from_public_economics_phase_1387a
no_unrouted_accepted_cdl_adr_functionality_before_public_rc_phase_1387a
```

## 1. Summary

| Corpus | Count | Result |
| --- | ---: | --- |
| Accepted ADR files in `docs/adr/` | 36 | all routed |
| Ratified CDL rows in `docs/specs/ilc_constitutional_decision_log_v0.1.md` | 84 | all routed |
| Unknown rows | 0 | pass |
| Public-RC blocking rows | 0 | pass |

Disposition vocabulary:

- `implemented_or_verified_for_public_rc`: runtime/spec/test coverage exists for the public-RC claim.
- `governance_or_documentation_only`: no runtime obligation is created before public RC.
- `explicitly_deferred_outside_public_rc`: accepted canon exists, but activation remains behind a later explicit gate.
- `covered_by_phase_1387a_firewall`: public economics admission is handled by `ilc_core/ledger/public_economics_admission_firewall.py`.

## 2. Named Gap Dispositions

### Gap A — Private Commitment Retroactive Priority

**Disposition:** covered by Phase 1387a firewall; not a public-RC blocker.

The following invariants are now explicit in the Phase 1387a matrix and runtime guard:

```text
private_or_opaque_commitments_do_not_create_retroactive_public_priority
independent_public_connection_credit_not_clawed_back_by_later_private_promotion
private_promotion_does_not_rewrite_existing_public_reward_history
```

The quantum hedge pattern is explicitly rejected: an agent that privately signs
multiple sides of a hypothesis and later reveals only the winning side receives
zero public priority advantage over an agent who publicly contributed the same
claim. Private timestamp, private hash, opaque commitment, or private shard
anchor is not a public priority date.

Runtime binding:
`ilc_core/ledger/public_economics_admission_firewall.py` rejects private
priority fields (`private_priority_claim`, `private_timestamp`,
`private_commitment_ref`, `opaque_commitment_priority_ref`,
`quantum_hedge_private_sides`) before any public economic event is constructed.

### Gap B — Submission-Race / Front-Running

**Disposition:** named and routed outside this public-RC blocker; not closed.

The front-running / submission-race gap is not solved by CDL-038 and not solved
by private/public visibility rules. A public actor may still observe an
unconnected public gap and race to publish synthetic bridging nodes before a
bona fide contributor. That risk requires a later submission-ordering or
epoch-batch-admission policy.

This is not a public-RC blocker for Phase 1387a because this phase only proves
that private or semi-private material cannot construct public economic events.
It does not activate graph reward distribution, public claimability, or a
submission-ordering reward market.

## 3. ADR Coverage Matrix

| ADR | Disposition | Public-RC routing |
| --- | --- | --- |
| ADR-0001 | implemented_or_verified_for_public_rc | canonical encoding remains active; deterministic JSON guardrails apply |
| ADR-0002 | implemented_or_verified_for_public_rc | NDJSON/bundle transport remains covered by prior fetch and bundle tests |
| ADR-0003 | implemented_or_verified_for_public_rc | star-map N-gram routing is routed through CDL-080 and public-RC graph lanes |
| ADR-0004 | implemented_or_verified_for_public_rc | primitive commit epoch is covered by epoch/ledger boundary tests |
| ADR-0005 | governance_or_documentation_only | observational feed design creates no new public-RC activation surface |
| ADR-0006 | implemented_or_verified_for_public_rc | capsule integrity is preserved by existing canonical artifact discipline |
| ADR-0007 | governance_or_documentation_only | constitutional process is active governance, not runtime activation |
| ADR-0008 | explicitly_deferred_outside_public_rc | usefulness/governance weighting remains non-public-RC economic scoring unless later activated |
| ADR-0009 | implemented_or_verified_for_public_rc | bundle distribution path is covered by CDL-076/CDL-077/CDL-087 |
| ADR-0010 | implemented_or_verified_for_public_rc | communication-plane separation remains enforced by package/public-surface gates |
| ADR-0011 | explicitly_deferred_outside_public_rc | native P2P public activation remains separately gated |
| ADR-0012 | covered_by_phase_1387a_firewall | ECU/ILC coupling cannot be driven by private or semi-private nodes |
| ADR-0013 | governance_or_documentation_only | third-party payment boundary creates no public-RC runtime obligation |
| ADR-0014 | implemented_or_verified_for_public_rc | identity envelope routed through CDL-069/CDL-090 and ADR-0038 |
| ADR-0015 | covered_by_phase_1387a_firewall | node transfer economics must pass public admission before public economics |
| ADR-0016 | covered_by_phase_1387a_firewall | productive ECU expansion requires public-node admission evidence |
| ADR-0017 | explicitly_deferred_outside_public_rc | post-issuance transition remains outside current public-RC claim |
| ADR-0019 | governance_or_documentation_only | governance compilation boundary is policy/canon only for this gate |
| ADR-0020 | implemented_or_verified_for_public_rc | knowledge-node-first principle is preserved by public node admission evidence |
| ADR-0022 | covered_by_phase_1387a_firewall | local/private use remains operator-local advisory only; no protocol ECU |
| ADR-0023 | explicitly_deferred_outside_public_rc | quality signals are not public economic events unless admitted by firewall |
| ADR-0024 | governance_or_documentation_only | skills infrastructure creates no protocol economic event |
| ADR-0025 | implemented_or_verified_for_public_rc | D2D HTTP gossip remains bounded by fetch/gossip guardrails |
| ADR-0026 | governance_or_documentation_only | harness/product boundary prevents harness claims becoming protocol claims |
| ADR-0027 | implemented_or_verified_for_public_rc | self-describing bootstrap/receipt boundary is routed through release gates |
| ADR-0028 | implemented_or_verified_for_public_rc | settlement substrate graduation covered by Phase 1386a/1386c/1387 |
| ADR-0029 | covered_by_phase_1387a_firewall | hypergraph economic events require public admission evidence |
| ADR-0030 | implemented_or_verified_for_public_rc | embedding substrate is non-economic unless public event construction is invoked |
| ADR-0031 | implemented_or_verified_for_public_rc | sidecar query runtime completeness closed at Phase 1379 |
| ADR-0032 | implemented_or_verified_for_public_rc | temporal hypergraph epoch stamping is routed through epoch-based guards |
| ADR-0033 | implemented_or_verified_for_public_rc | star-map entity rules are routed through CDL-080 and graph discipline |
| ADR-0034 | explicitly_deferred_outside_public_rc | sealed sender mechanism is not a public-RC sender-privacy claim |
| ADR-0036 | implemented_or_verified_for_public_rc | release-key binding is routed through release/signing gates |
| ADR-0037 | implemented_or_verified_for_public_rc | Genesis lineage contract routed through identity/release proofs |
| ADR-0038 | implemented_or_verified_for_public_rc | agent birth attestation routed through CDL-090 |
| ADR-0039 | implemented_or_verified_for_public_rc | endpoint registry ratified and used by Phase 1386c projection |

## 4. Ratified CDL Coverage Matrix

| CDL | Disposition | Public-RC routing |
| --- | --- | --- |
| CDL-001 | governance_or_documentation_only | foundational constitutional row; no direct runtime activation |
| CDL-002 | governance_or_documentation_only | foundational constitutional row; no direct runtime activation |
| CDL-003 | governance_or_documentation_only | foundational constitutional row; no direct runtime activation |
| CDL-004 | governance_or_documentation_only | foundational constitutional row; no direct runtime activation |
| CDL-005 | governance_or_documentation_only | foundational constitutional row; no direct runtime activation |
| CDL-006 | implemented_or_verified_for_public_rc | challenge-node runtime completed in Phases 1381-1382 |
| CDL-007 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-008 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-009 | implemented_or_verified_for_public_rc | fork-legitimacy UX completed in Phase 1383 |
| CDL-010 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-011 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-012 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-013 | implemented_or_verified_for_public_rc | governance-weight integration exists; public economics still gated |
| CDL-014 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-015 | covered_by_phase_1387a_firewall | node transfer economics require public-node admission |
| CDL-017 | explicitly_deferred_outside_public_rc | validator admission/ejection remains not activated for dynamic admission |
| CDL-019 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-020 | explicitly_deferred_outside_public_rc | distribution architecture work remains outside this public-RC gate |
| CDL-022 | implemented_or_verified_for_public_rc | Genesis state/signing routed through release/signing artifacts |
| CDL-023 | implemented_or_verified_for_public_rc | epoch snapshot mechanism has runtime/hash coverage |
| CDL-024 | implemented_or_verified_for_public_rc | wire protocol is routed through transport/fetch/TLS/QUIC gates |
| CDL-025 | explicitly_deferred_outside_public_rc | emission runtime exists but production minting remains inactive |
| CDL-026 | explicitly_deferred_outside_public_rc | C_max cap runtime exists; production minting remains inactive |
| CDL-027 | explicitly_deferred_outside_public_rc | epoch schedule runtime exists; production minting remains inactive |
| CDL-028 | explicitly_deferred_outside_public_rc | fee-burn quote runtime exists; production fee collection inactive |
| CDL-029 | explicitly_deferred_outside_public_rc | allocation quote runtime exists; production distribution inactive |
| CDL-030 | explicitly_deferred_outside_public_rc | ECU price clamp runtime exists; live adjustment inactive |
| CDL-031 | explicitly_deferred_outside_public_rc | dynamic ranking policy remains deferred to governance/reputation lane |
| CDL-032 | governance_or_documentation_only | CLI-first SDK surface is not public economics |
| CDL-033 | governance_or_documentation_only | OpenClaw skill publication contract is not public economics |
| CDL-034 | implemented_or_verified_for_public_rc | truth primitive lineage routed through CDL-074/CDL-075 |
| CDL-035 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-036 | implemented_or_verified_for_public_rc | dissemination routed through CDL-076/CDL-077 |
| CDL-037 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-038 | covered_by_phase_1387a_firewall | promotion continuity zero-carry-forward verified; Gap A sealed by firewall |
| CDL-039 | implemented_or_verified_for_public_rc | topology/shuffle dependencies routed through CDL-068 and QUIC projection |
| CDL-040 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-041 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-042 | implemented_or_verified_for_public_rc | identity namespace routed through CDL-069/CDL-090 |
| CDL-043 | implemented_or_verified_for_public_rc | adaptive pruning runtime exists and remains non-economic |
| CDL-044 | implemented_or_verified_for_public_rc | retention epoch policy covered by pruning runtime |
| CDL-045 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-046 | covered_by_phase_1387a_firewall | hyperedge attribution must pass public admission before public economics |
| CDL-047 | explicitly_deferred_outside_public_rc | treasury runtime quote exists; production treasury inactive |
| CDL-048 | explicitly_deferred_outside_public_rc | dry-run wiring exists; activation is Phase 1388 |
| CDL-049 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-050 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-051 | implemented_or_verified_for_public_rc | consensus/epoch finality covered by Spec D and Phase 1387 |
| CDL-052 | implemented_or_verified_for_public_rc | truth primitive graph-output contract routed through CDL-074/CDL-075 |
| CDL-054 | explicitly_deferred_outside_public_rc | validator reward routing quote exists; production rewards inactive |
| CDL-055 | governance_or_documentation_only | conversion interaction clauses routed through CDL-089/Phase 1388 |
| CDL-056 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-057 | explicitly_deferred_outside_public_rc | epoch-boundary witness active for conversion vehicle; live value path still Phase 1388 |
| CDL-058 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-059 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-060 | implemented_or_verified_for_public_rc | routing reputation runtime is relay-only; no protocol ECU event without firewall |
| CDL-061 | implemented_or_verified_for_public_rc | gossip envelope dependency remains routed through D2D tests |
| CDL-063 | governance_or_documentation_only | no direct public-RC runtime obligation |
| CDL-064 | implemented_or_verified_for_public_rc | exact numeric contract enforced by guardrails |
| CDL-065 | implemented_or_verified_for_public_rc | coupling invariants routed through consensus/economic gates |
| CDL-066 | implemented_or_verified_for_public_rc | sender authorization covered by fast-path signature checks |
| CDL-067 | implemented_or_verified_for_public_rc | settlement-state scope routed through epoch/settlement gates |
| CDL-068 | implemented_or_verified_for_public_rc | topology epoch scoping used by ADR-0039/Phase 1386c |
| CDL-069 | implemented_or_verified_for_public_rc | PQ identity root and endorsement routed through identity-bootstrap lane |
| CDL-071 | governance_or_documentation_only | temporal tier reconciliation creates no new public-RC runtime surface |
| CDL-072 | implemented_or_verified_for_public_rc | Row-5 jitter formula is activated only through gated mixing framework |
| CDL-073 | implemented_or_verified_for_public_rc | homoiconic bootstrap schema routed through release/package gates |
| CDL-074 | implemented_or_verified_for_public_rc | truth primitive runtime implemented and commit.epoch rejected |
| CDL-075 | implemented_or_verified_for_public_rc | truth primitive graph persistence implemented |
| CDL-076 | implemented_or_verified_for_public_rc | truth primitive announcement gossip implemented |
| CDL-077 | implemented_or_verified_for_public_rc | WANT-HAVE/WANT-BLOCK fetch implemented with rate limits |
| CDL-078 | implemented_or_verified_for_public_rc | relay fallback used by Phase 1386c; no micro-payment path |
| CDL-079 | implemented_or_verified_for_public_rc | bootstrap distribution routed through CDL-077 fetch |
| CDL-080 | implemented_or_verified_for_public_rc | star-map route index routed through graph/public-RC lanes |
| CDL-081 | covered_by_phase_1387a_firewall | hyperedge ECU attribution requires public-node admission |
| CDL-082 | implemented_or_verified_for_public_rc | beacon threshold amendment routed through gossip/star-map lanes |
| CDL-083 | explicitly_deferred_outside_public_rc | ejected-stake/refutation payout helpers exist; production distribution inactive |
| CDL-084 | explicitly_deferred_outside_public_rc | provenance attribution helpers exist; production attribution inactive |
| CDL-085 | implemented_or_verified_for_public_rc | Werner phi-bound routed through runtime/economic-flow evidence |
| CDL-086 | explicitly_deferred_outside_public_rc | public launch packaging remains behind publication/signing gates |
| CDL-087 | explicitly_deferred_outside_public_rc | public fetch/sidecar serving remains separately gated |
| CDL-088 | covered_by_phase_1387a_firewall | public-only economics admission required and now implemented |
| CDL-089 | explicitly_deferred_outside_public_rc | CDL-048 activation vehicle remains Phase 1388-gated |
| CDL-090 | implemented_or_verified_for_public_rc | identity bootstrap ratified; identity artifact creation remains separately gated |

## 5. Non-Authorization

This matrix does not activate public claimability, public economics, public ECU,
public reputation, public settlement, public corroboration, public P2P, public
verifier APIs, wallet actions, ECU minting, ILC settlement, source publication,
release signing, counsel approval, or legal conclusions.
