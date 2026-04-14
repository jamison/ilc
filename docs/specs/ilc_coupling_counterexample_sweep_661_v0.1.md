# ILC Coupling Counterexample Sweep 661 v0.1

Status: constitutional review artifact
Date: 2026-04-14
Phase: 661
Owner lane: G8 coupling-invariants governance lock

## 1. Purpose and threat model

This sweep pressure-tests the row-6 lock against the bad cases the project
actually cares about.

The threat model is not limited to a malicious chain. It also includes:
- backend substitution pressure
- legitimacy laundering through anchoring language
- lineage breakage hidden behind later settlement convenience
- foreign constitutional centers trying to become practical veto points

The question for each case is simple:
- does the later backend try to author legitimacy that belongs upstream to the
  protocol
- if so, does the proposed row-6 lock block it clearly enough

## 2. Counterexample cases

### Case 1: Backend mints legitimacy by carrying data first

`backend_cannot_author_legitimacy_counterexample`

Counterexample:
- a later backend accepts an actor, settles that actor's activity, and then
  claims that the protocol should treat the actor as public-legitimate because
  the backend already recorded the state

### Case 2: Backend ordering becomes protocol truth

`backend_cannot_override_protocol_truth_counterexample`

Counterexample:
- a later backend orders or finalizes a disputed state and then claims the
  ordered result should override protocol-side legitimacy because the backend
  now has the more durable record

### Case 3: Namespace inheritance without protocol lineage

`backend_cannot_inherit_namespace_without_lineage_counterexample`

Counterexample:
- a forked or alternate backend carries forward a public handle map and claims
  the namespace is still canonical even though the protocol-side lineage root
  is missing or diverged

### Case 4: Reputation inheritance without protocol lineage

`backend_cannot_inherit_reputation_without_lineage_counterexample`

Counterexample:
- a later backend clones prior public history and claims the clone inherits the
  same reputation, even though the protocol-side receipt lineage was broken

### Case 5: External constitutional center veto pressure

`external_constitutional_center_veto_risk_counterexample`

Counterexample:
- a later backend or related operator/governance body becomes the place where
  public legitimacy is practically approved or denied, turning the protocol
  into a dependent shell around an external constitutional center

## 3. Why each case fails the row-6 lock

Case-by-case failure basis:
- Case 1 fails because public admission legitimacy is upstream. A backend may
  carry already-admitted activity, but it may not backfill admission by having
  carried the activity first.
- Case 2 fails because backend durability does not outrank protocol truth. The
  backend may anchor already-legitimate state, but it may not convert later
  ordering into legitimacy authority.
- Case 3 fails because canonical namespace authority requires protocol lineage.
  Carrying a copied name map is not the same as inheriting canonical authority.
- Case 4 fails because public reputation continuity requires admission and
  receipt continuity. A copied history without protocol lineage is only a copy.
- Case 5 fails because the row-6 lock requires the protocol layer to remain the
  legitimacy root. A later backend may serve settlement or anchoring functions,
  but it may not become the practical veto center over public legitimacy.

The practical discipline is the same across all five cases:
- carry, order, anchor, finalize, and settle are downstream services
- author, inherit, override, or veto legitimacy are upstream powers

## 4. Residual ambiguity and future-lane routing

Residual ambiguity still exists in later rows, not in the basic row-6 rule.

Carried forward:
- row 5 must later decide what privacy-preserving public legitimacy looks like
  without breaking auditability
- row 7 must later define what level of censorship resistance counts as enough
- row 8 must later define how external constitutional-center dependence is
  measured and excluded
- row 9 must later prove operational maturity, especially for bounded metadata
  push versus heavy payload pull

Routing:
- row 6 continues to Phase 662 for `CDL-065` opening and admissibility
- row 9 threshold work belongs to Window 665-670
- rows 7 and 8 criteria lock work belongs to Window 671-676
- row 5 narrowing and mechanism-family work belongs to Window 677-682
