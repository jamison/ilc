# ILC OpenClaw Local Capture

Local capture, consent-gated estimation, and invite-gated bootstrap for ILC graph contribution through OpenClaw.

## What It Does

- Captures selected prompt, reply, tool, and API outputs into local private ILC-shaped records.
- Classifies local candidate records and proposes non-authoritative edge hints.
- Produces private, non-binding ECU estimates for local triage.
- Verifies ILC invite bundles before local bootstrap or setup.
- Requires explicit ConsentGate approval before any submission-intent record.

## What It Does Not Do

- It does not mint ECU.
- It does not settle ILC.
- It does not write wallets.
- It does not publish directly to the public graph.
- It does not activate public RC, mainnet, or production settlement.
- It does not passively collect all OpenClaw traffic.

## Requirements

- ILC CLI available as `ilc`.
- A valid invite bundle for local setup actions.
- Explicit human approval before public submission intent.

## Primary Actions

| Action | Scope |
|---|---|
| `ilc capture` | Local private capture envelope |
| `ilc classify` | Local candidate classification |
| `ilc estimate` | Private non-binding usefulness estimate |
| `ilc verify-invite` | Local invite gate decision |
| `ilc submit` | Consent-gated submission intent |
| `ilc mine-idle` | Explicit opt-in maintenance task offer |
| `ilc status` | Local queue and next-action status |

## Source

Public source: https://github.com/jamison/ilc/tree/main/skills/ilc-openclaw-local-capture
