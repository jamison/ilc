# Idea-Descent Objective: ILC Claim Decomposition Quality

**Objective ID:** ilc_decomposition_descent_v0.1
**Evaluator:** tools/evaluators/ilc_decomposition_evaluator.py
**Candidate type:** Any structured text document containing claims (specs, research notes, phase prompts, economics papers, protocol descriptions)

## Goal

Produce a claim document that, when processed by the ILC decomposition evaluator:

1. Extracts a non-trivial set of candidate assertion units (at least 3 claims)
2. Achieves at least 50% ILC-refutable claims (each has an operational falsification condition)
3. Has zero CRITICAL invariant failures (no structurally unfalsifiable asserted claims)
4. Has zero SIGNIFICANT scope-risk violations (no cross-domain scope transfer without bridge argument)
5. Has zero SIGNIFICANT evidence-bridge-risk violations (no theoretical result stated as empirical prediction without a bridge)

## Profile selection

The evaluator loads one or more domain profiles. Specify which profiles apply to
the candidate document in the `--profiles` argument or objective metadata. If
omitted, the default profile is `en_scientific_claims`.

| Profile | When to use |
|---------|-------------|
| `en_scientific_claims` | English-language scientific or technical documents |
| `romer_macro_ai_transition` | Economics claims from growth models; AI-as-capital transition risks |
| `ilc_protocol_claims` | ILC protocol specs, ADR/CDL/OBL documents, runtime claims |

## Acceptance criterion

`ilc_decomposition_evaluator.py` exits 0 with a summary containing `0 invariant failures`.

## Non-goals

This descent loop evaluates structural claim quality (scope, evidence type, falsifiability).
It does not evaluate:
- Semantic truth of claims
- Completeness of an argument
- Writing style or clarity
- Whether the specific claim content is correct for ILC protocol purposes

Content correctness review is a separate human/Codex phase review step.

## Non-claims

This objective document does not open a CDL, ADR, or OBL. It does not authorize
graph writes, ECU allocation, public RC activation, or CDL/ADR mutation.
