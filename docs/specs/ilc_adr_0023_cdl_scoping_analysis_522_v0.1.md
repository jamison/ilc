# ILC ADR-0023 CDL Scoping Analysis 522 v0.1

Status: scoping analysis
Date: 2026-03-30
Owner lane: G8 Constitution Cluster A

## 1. ADR-0023 summary

adr_0023_quality_signal_architecture

ADR-0023 describes a proposed multi-layer quality signal architecture for ILC nodes:
- objective verdicts for falsifiable content,
- aesthetic consensus for expressive content,
- use centrality as a long-run structural signal,
- bounded passive ECU attribution derived from those signals.

ADR-0023 is not a ratified CDL.

## 2. Protocol-layer constitutional necessity test

ADR-0023 is not yet ready for constitutional ratification because the design still depends on:
- simulation calibration for quality-score and quality-factor mapping,
- simulation calibration for passive ECU budget routing,
- unresolved governance triggers for aesthetic evaluation and re-evaluation,
- unresolved constitutional boundaries for any future signal failure semantics.

These are protocol-relevant questions, but they are not yet narrowed enough to open a clean CDL
without prematurely freezing experimental economics and discovery logic.

## 3. Research-guidance sufficiency assessment

ADR/research guidance is currently sufficient because:
- the architecture is explicitly marked pre-constitutional,
- no runtime in the current validator window depends on ADR-0023 becoming law,
- the key open items are simulation and calibration tasks rather than implementation guardrails,
- the current window is still dominated by validator and re_admission runtime work.

## 4. Recommendation

adr_0023_remains_research_guidance

ADR-0023 should remain ADR/research guidance in the current window. Opening `CDL-059` now would
force constitutional choices before the signal layer count, economic weighting, and passive ECU
budget boundaries have evidence-backed calibration.

## 5. Window 525+ prerequisites (if CDL-059 opening recommended)

No CDL opening is recommended in Phase 522. If a future `CDL-059` lane is proposed, Window 525+
should first require:
- simulation evidence for centrality convergence and ECU budget stability,
- simulation evidence for novelty-bonus calibration,
- simulation evidence for expressive-panel diversity and failure modes,
- a narrowed statement of which protocol fields require constitutional protection.

## 6. Governance boundary

No decision-log mutation occurs in Phase 522.

CDL-022 (ADM governance) interaction is deferred unless ADR-0023 graduates from research into a
future constitutional lane. CDL-V3 diversity-floor interactions are noted for any future panel
design work. ADR-0022 private/gated boundary remains separate.
