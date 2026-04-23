# Specs: Sequence Locks, Phase Window Guidance, and Phase Artifacts

This folder carries the recurring planning and governance document families
that drive ILC execution windows.

This README is the local schema contract for:
- sequence locks,
- phase-window guidance / candidate grouping docs,
- phase artifacts such as opening stubs, proof notes, evidence docs,
  coherence reports, and closure gates.

---

## 1. Sequence locks

Sequence locks define the active execution window. They should be narrow,
ordered, and explicit about what the window does and does not authorize.

### Required header fields

- title with phase/window range
- `Status: sequence lock`
- `Date:`
- `Phase:` or active start phase
- `Owner lane:`

### Required sections

1. `Baseline`
2. inherited gates / constraints
3. scope or window meaning
4. phase table and sequencing
5. non-goals
6. source inputs

### Strong recommendations

- include machine-token block near the top
- include inter-lane dependency section when parallel tracks exist
- explicitly distinguish inherited law from new planning posture
- explicitly state what is opening-only versus what would require ratification

---

## 2. Phase-window guidance / candidate grouping docs

These docs shape a window before or alongside its sequence lock.

### Required header fields

- title with window range
- author / owner
- date
- baseline
- reference to higher-level roadmap or transition guide

### Required sections

1. `Window identity and scope`
2. `Inter-lane dependencies`
3. obligated versus deferred work
4. governing constraints inherited from prior windows
5. candidate phase table
6. scope notes for candidate phases

### Strong recommendations

- include explicit hard constraints
- name open questions directly
- keep phase descriptions executable enough that the later sequence lock does
  not have to invent structure

---

## 3. Phase artifacts

Phase artifacts are the concrete outputs of individual phases. Common classes:
- opening stubs
- proof or evidence notes
- coherence reports
- closure gates

### Required header fields

- title with artifact type and phase
- `Status:`
- `Date:`
- `Phase:`
- either `Decision vehicle:` or `Owner lane:`

### Required core sections

1. artifact identity / purpose
2. scope boundary
3. inherited constraints or exclusions
4. artifact-specific findings or selected direction
5. forward obligations

### Subtype rules

#### Opening stubs

Must include:
- lane identity
- problem statement
- bounded opening scope
- non-goals / exclusions
- evidence anchors
- forward obligations

#### Proof or evidence docs

Must include:
- assumptions
- evidence inputs or model inputs
- verdict / disposition
- unresolved gaps

#### Closure gates

Must include:
- checklist of required items
- pass / fail / partial disposition
- explicit blockers and carry-forward items

---

## 4. Content rules for this folder

- Do not silently widen a CDL in an opening stub.
- Do not present planning assumptions as ratified law.
- Do not mutate a row state or decision-log meaning by implication.
- When numbering corrections occur, state them explicitly rather than
  pretending the earlier reference never existed.
- When a phase artifact creates a hard gate for a parallel lane, record the
  gate token in the artifact body.
