# ILC CDL-087 Canonical Fetch Distribution Policy Opening 1227 v0.1

**CDL number:** CDL-087
**Title:** Canonical Fetch Distribution Policy
**Status:** OPEN
**Opened phase:** 1227
**Opened date:** 2026-05-06
**Opening token:** `cdl_087_canonical_fetch_distribution_policy_opened_phase_1227`
**Non-ratification token:** `cdl_087_not_ratified_phase_1227`
**Ratification gate:** deferred pending SIM-FETCH-01 evidence (Window 1233+)
**Basis:** `fetch_distribution_architecture_reframed_phase_1222`

---

## 1. Opening Statement

CDL-087 opens the constitutional lane for canonical fetch distribution policy.
It gives governance footing to the Phase 1222 reframing: ordinary reads of
canonical content are public verifiable infrastructure, not per-requester
admission decisions.

This CDL is opened, not ratified. Q1-Q5 remain open until Phase 1228 prelock.
Ratification requires SIM-FETCH-01 evidence demonstrating actual fetch pressure
distribution, cache hit rates, high-centrality serve profiles, and
non-cacheable request pressure.

---

## 2. Motivation

Phase 1222 initially documented a reciprocal fetch admission candidate. That
candidate assumed symmetric peer pressure: healthy nodes pull roughly as much
as they serve. Phase 1222 §8 corrected that assumption and recorded:

```text
fetch_distribution_architecture_reframed_phase_1222
```

ILC fetch traffic is rooted and topological. New agents, bootstrapping agents,
archival readers, and agent-native graph projection tools legitimately pull
Genesis, ADR-0004 truth primitives, accepted CDLs/ADRs, manifests, lineage
receipts, and epoch/checkpoint material before they have served anything back.
That is correct bootstrapping behavior, not abuse.

The constitutional distinction is therefore:

| Surface | CDL-087 posture |
|---------|-----------------|
| Canonical reads | Publicly verifiable by content hash and Genesis-lineage proof; validity does not depend on requester identity |
| Writes, mutations, publication | Separately gated by existing stake, reputation, authority, and CDL/ADR rules |
| Economic recognition | Separately gated by Genesis-lineage-valid participation and economics CDLs |
| Non-cacheable abuse or malformed requests | Controlled by protocol-boundary validation, static circuit breakers, operator-local backpressure, and future SIM-calibrated policy |

High-centrality read pressure should be handled by caching, mirroring, verified
snapshots, and observability before any reciprocal scoring or ECU-escrow
admission formula is considered.

---

## 3. Q1-Q5 Deliberation Agenda

The following questions are opened by this phase and must be resolved at Phase
1228 prelock. CDL-087 opening records the agenda; it does not lock the answers.

| Q | Open question |
|---|---------------|
| Q1 | What artifacts constitute the high-centrality canonical infrastructure tier? Candidate classes include Genesis artifacts, ADR-0004 truth primitives, accepted CDLs and ADRs, manifests, lineage receipts, and epoch checkpoints. Exact enumeration locks at prelock. |
| Q2 | What caching and staleness guarantees must operators maintain for high-centrality tier artifacts? TTL, staleness bounds, and content-hash verification schema lock at prelock; numeric constants remain provisional until SIM-FETCH-01. |
| Q3 | What is the minimum snapshot format that allows a new node to bootstrap from a Genesis-rooted verified snapshot? Format, required fields, and lineage proof chain lock at prelock. |
| Q4 | What observability signals must a node expose before any future fetch admission CDL ratification is permitted? Metric names, collection interval, and output format lock at prelock. |
| Q5 | Does CDL-077 require amendment, or does CDL-087 supplement it without amending? Preliminary opening posture: supplement without amendment; confirmation locks at prelock. |

---

## 4. Scope Boundary

CDL-087 governs:

1. High-centrality tier definition: what artifacts are canonical public
   infrastructure.
2. Caching and mirroring requirements for high-centrality tier artifacts.
3. Snapshot distribution requirements for new-node bootstrap from a
   Genesis-rooted verified snapshot.
4. Observability requirements that must precede any future fetch admission CDL.
5. Read/write asymmetry: canonical reads are publicly verifiable and must not be
   gated by per-requester identity; writes, mutations, publication, and economic
   recognition remain separately gated.
6. Static rate-limiter preservation: CDL-077 WANT-BLOCK limiting remains active
   as an abuse circuit breaker. CDL-087 supplements CDL-077 by defining the
   caching/replication layer that reduces legitimate fetch pressure; CDL-087
   does not supersede CDL-077.

CDL-087 does not govern:

1. Peer-to-peer block serving for non-cached or tail content.
2. Reciprocal scoring, ECU-escrow fetch admission, puzzle admission, or
   reputation-weighted read capacity.
3. Gossip pull capacity, which remains governed by CDL-060 and related gossip
   lanes.
4. Write/mutation admission, which remains governed by existing
   stake/reputation/CDL authority paths.

Publicly verifiable reads do not create an unlimited service obligation for any
single operator. CDL-077 circuit breakers, protocol-boundary validation,
bounded request handling, and operator-local abuse controls remain active.
CDL-087's near-term purpose is to make legitimate high-centrality reads cheap
through caching/replication, not to waive defensive controls.

---

## 5. Dependency Chain

| Dependency | Relationship |
|------------|--------------|
| CDL-077 | Governs WANT-HAVE/WANT-BLOCK fetch and the static WANT-BLOCK limiter. CDL-087 supplements without amending at opening. |
| CDL-086 | Public-launch packaging blocker. CDL-087 is public-access infrastructure required before public RC/public launch acts may be claimed. |
| ADR-0037 | Genesis Canonical Lineage Contract. CDL-087 read validity relies on content hash plus Genesis-lineage proof rather than requester identity. |
| `fetch_distribution_architecture_reframed_phase_1222` | Phase 1222 §8 reframing that rejects reciprocal scoring as the preferred near-term architecture. |

---

## 6. Ratification Boundary

```text
cdl_087_not_ratified_phase_1227
```

No ratification act is authorized in Phase 1227 or Phase 1228. CDL-087 remains
OPEN after this phase. Phase 1228 may prelock Q1-Q5 and ratification
conditions, but ratification requires SIM-FETCH-01 evidence demonstrating:

- actual request pressure per artifact tier;
- cache hit rates;
- high-centrality node serve profiles;
- non-cacheable request volume;
- failure/error rates;
- abuse/circuit-breaker activation patterns.

Any future ratification attempt without SIM-FETCH-01 evidence must fail closed.

---

## 7. Non-Claims

This opening does not:

- ratify CDL-087;
- amend CDL-077;
- implement runtime code;
- deprecate or weaken static rate limiting;
- open a reciprocal scoring CDL;
- authorize public launch;
- authorize public repository publication;
- authorize public release artifact distribution;
- authorize external contributor onboarding;
- authorize v0.2 signing or release-key generation.
