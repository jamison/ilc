# ILC External Constitutional Center and Exclusion Matrix 673 v0.1

Status: criteria artifact
Date: 2026-04-15
Phase: 673
Owner lane: G8 censorship-resistance and independence strike force

## 1. Purpose and row-8 target

Phase 673 defines what counts as an external constitutional center and fixes
the substrate-family exclusion matrix for row 8.

`external_constitutional_center_means_outside_system_with_de_facto_or_formal_legitimacy_veto`

This artifact is criteria work. It does not select a substrate.

## 2. Core definitions

External constitutional center:
- an outside actor, system, or governance surface whose formal or de facto
  approval becomes necessary to create, preserve, contest, migrate, or
  recognize ILC public legitimacy

Outside veto authority:
- unilateral or practically unavoidable power to freeze, reorder, suppress,
  refuse exit from, or nullify continuity of legitimacy-relevant public state

De facto source of truth:
- an outside system that becomes the practical authority for admission,
  namespace, quorum authority, settlement legitimacy, auditability, or
  continuity, even if the protocol does not officially name it as such

`outside_veto_authority_is_presumptively_disqualifying`

## 3. Exclusion rules

The following dependency patterns are disqualifying for row 8:
- protocol legitimacy can be overridden or nullified by an outside governance
  body
- admission or namespace authority can be created outside protocol lineage
- public settlement legitimacy can be declared without protocol receipt basis
- public reputation continuity depends on outside operator or vendor approval
- the only practical audit or exit path runs through one hosted control plane
- migration requires privileged consent from the original operator or provider

The following dependency patterns are risky but not automatically disqualifying:
- external durability or ordering services that remain downstream of protocol
  legitimacy
- convenience dashboards, managed RPC, or hosted control planes that are
  bypassable and non-authoritative
- third-party infrastructure concentration that does not become the legitimacy
  source by design

## 4. Substrate-family classification matrix

`substrate_families_classified_as_admissible_risky_or_presumptively_inadmissible`

| Substrate family or posture | Classification | Reason |
|---|---|---|
| sovereign minimal L1 / BFT network where protocol legitimacy stays upstream and exit is credible | presumptively admissible | outside infrastructure may carry legitimacy, but does not author it |
| external chain or rollup used only as downstream settlement/durability layer with credible export and replay | risky but potentially admissible | must prove outside governance cannot become the practical legitimacy root |
| shared sequencer or managed settlement service with unilateral freeze/reorder power | presumptively inadmissible | outside veto authority becomes real, not hypothetical |
| hosted dashboard or provider shell as the ordinary public legitimacy surface | presumptively inadmissible | fails row-7 and row-8 anti-bottleneck rules directly |
| custodial exchange, wallet, or portal standing in for settlement legitimacy | presumptively inadmissible | continuity and exit depend on external operator approval |
| multi-provider or self-hostable convenience stack that remains non-authoritative | risky but potentially admissible | must remain bypassable and non-constitutive |

## 5. Genesis bootstrap exception versus ordinary third-party dependence

`genesis_bootstrap_exception_not_equal_to_third_party_sovereign_dependency`

Genesis is not treated here as an ordinary third party because canon already
grounds the network in Genesis-rooted artifact lineage and bounded bootstrap
necessity.

That exception is narrow:
- Genesis may be special enough to bootstrap the canonical network
- Genesis may not become indefinite hidden sovereign authority
- Genesis may not be used as a rhetorical shield for ordinary third-party
  dependence

Therefore:
- a later vendor, shell, sequencer, foundation service, or provider may not
  claim Genesis-like exception status
- later backends may carry legitimacy, but may not become the constitutional
  center that authors it

## 6. Carry-forward implications

The matrix fixed here is a hard gate for later substrate work:
- later substrate lanes may evaluate candidates within the admissible/risky
  space
- later substrate lanes may not rehabilitate presumptively inadmissible
  families without reopening the row-8 lock itself
- later substrate lanes must show how risky-but-admissible candidates avoid
  drifting into de facto external constitutional centers

## 7. What this artifact does not decide

This artifact does not:
- pick the final Option-B substrate
- prove row-7 runtime compliance for any concrete implementation
- open `CDL-062`
- decide the row-5 privacy mechanism
