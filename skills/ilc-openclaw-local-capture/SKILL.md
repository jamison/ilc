# ILC OpenClaw Local Capture

## Purpose

This skill lets an OpenClaw-hosted local agent turn selected prompt, reply,
tool, and API outputs into private ILC-shaped candidate records. It is a local
harness skill, not protocol authority.

## Authority Boundary

- OpenClaw is the harness host. ILC protocol truth remains in `ilc_core/`.
- Captures are local/private by default.
- No captured record is submitted to the public graph automatically.
- No ECU is minted by this skill.
- No ILC is settled by this skill.
- No wallet write is performed by this skill.
- No public-RC activation is performed by this skill.
- Public graph nodes are permanent records. Corrections use revision,
  refutation, pruning, routing refusal, and reputation rather than edit/delete.

## Machine-Readable Actions

| Action | Required input | Output | Authority |
|---|---|---|---|
| `ilc capture` | `raw_payload`, `payload_kind`, `operator_agent_id`, `local_agent_id` | local private capture envelope | none |
| `ilc classify` | capture envelope | candidate node type and proposed edge hints | none |
| `ilc estimate` | capture envelope | `estimate_schema_v0.1_private_heuristic` | non-binding private estimate only |
| `ilc submit` | capture envelope with ConsentGate approval | submission-intent record | no automatic publication |
| `ilc mine-idle` | explicit `maintenance_idle` policy | local maintenance task offer | no credit minted |
| `ilc status` | none | local queue, flagged items, policy state, and next human action | none |

`ilc recommend` is an internal ranking step used by `ilc submit`. It is not a
separate authority-bearing command.

## Capture Rule

Capture is deliberate agent capture only. This skill does not intercept all
OpenClaw traffic, scrape provider logs, or passively collect every API call.

The raw payload is hashed separately from the envelope. Envelope metadata such
as `operator_agent_id`, `local_agent_id`, `provider_id`, `privacy_class`, and
`consent_state` is not part of the raw payload hash.

## Estimate Rule

The ECU estimate is `estimate_schema_v0.1_private_heuristic`.

It contains these Decimal-compatible scores in `[0, 1]`:

- `novelty_score`
- `reuse_potential`
- `evidence_strength`
- `falsifiability`
- `duplicate_risk`
- `privacy_risk`

The estimate is local and non-binding. Local novelty is measured against local
capture context only and is not public graph novelty. The estimate is not a
balance, claimability proof, settlement amount, wallet value, or guarantee.

## ConsentGate Rule

ConsentGate is a synchronous policy API. A local agent may prepare private
candidate records, classify them, estimate them, and show status. A submission
intent requires `consent_state = approved_for_public_submission`.

The regular human touchpoint is:

```text
ilc status
```

The status output should show flagged records, policy state, and the next human
action. Bypass is not permitted.

## Autonomy Defaults

Default setup should support broad public-RC local capture under
`bounded_autonomy`. `maintenance_idle` is a separate explicit opt-in and may be
recommended for confirmed agent-first installs. It must not be silently enabled.
