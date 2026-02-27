# Popper and ILC: A Three-Part Analysis v0.1

Status: Canonical reference
Date: 2026-02-26
Classification: Internal working document — not for public distribution
Owner: G8 Constitution Cluster A
Related: `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`

Primary source for this analysis: Stanford Encyclopedia of Philosophy, "Karl Popper," §4 "Basic Statements, Falsifiability and Convention." https://plato.stanford.edu/entries/popper/#BasiStatFalsConv

---

## Purpose

This document provides a structured analysis of Karl Popper's epistemology in relation to ILC's design. It identifies:

1. Where Popper and ILC align — structural isomorphisms that validate design choices.
2. Where they diverge — genuine tensions, including theories that have been superseded or formally disproven since Popper's time.
3. Direct application of Popper's Section 4 concepts (basic statements, falsifiability, testing regress, jury analogy, pile/swamp metaphor) to ILC's operational architecture.

This document is a companion to `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`. The epistemological foundations document explains ILC's overall epistemic structure; this document provides the Popper-specific analysis that grounds and qualifies those claims.

---

## Part 1: Where Popper and ILC Align

### 1.1 Falsifiability as the demarcation criterion — and its structural echo in CDL evidence prelocks

Popper's core move was to replace verifiability with falsifiability as the criterion for meaningful empirical claims. The asymmetry is fundamental: universal propositions cannot be conclusively verified through experience (no finite number of confirmations is sufficient), but a single genuine counter-instance falsifies them logically. (Popper, *The Logic of Scientific Discovery*, 1959, §6.)

ILC's CDL evidence prelock system is structurally Popperian. Before any constitutional decision can be ratified, the protocol must specify what would constitute a counter-instance — what evidence would refute the proposed decision, or what outcome would demonstrate it was wrong. The "evidence prelock" is precisely the step of declaring the falsification conditions in advance, before the ratification ceremony executes. A CDL row that moves directly to ratification without a prelock is the equivalent of an unfalsifiable claim: it has made itself immune to refutation by never specifying what would refute it.

This is not merely analogous. It is the same constraint operating in different substrate.

### 1.2 Fallibilism and the self-amending constitution

Popper's fallibilism holds that all scientific beliefs are held tentatively and provisionally — the correct epistemic posture is "I believe this for now, subject to refutation." No belief is immune from revision. The appropriate response to this is not skepticism but systematic self-correction: build revision mechanisms into the knowledge system itself. (Popper, *Conjectures and Refutations*, 1963, ch. 1.)

ILC's CDL is directly Popperian: decisions are ratified but can be reopened; the option inventory in each CDL entry preserves all alternatives considered, so that ratification is a provisional selection rather than permanent elimination of other paths; the no-ratification-before-lock guard prevents premature closure that would foreclose revision.

The missing element (not yet required by ILC's CDL schema): an explicit **falsification criterion** in each ratified CDL row — a specific, observable outcome that, if observed, would trigger reopening. Currently CDLs close without stating what would reopen them. Adding this field as a required schema element would make the Popperian structure explicit and testable. (See Open Question 1 in `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md`.)

### 1.3 Intersubjective testability — the material condition for basic statements

Popper requires that basic statements — the singular existential claims that can potentially falsify a theory — be not just formally appropriate (singular and existential in structure) but materially intersubjectively testable: multiple observers operating independently should be able to evaluate them against observable fact. (SEP §4; *Logic of Scientific Discovery* §29.)

This is the deep reason why ILC's commit-anchored tests are not merely quality control. They are the intersubjective testability mechanism. Any agent — human or AI — can independently run the test suite and evaluate whether the claims about the system's behavior hold. The test suite is the mechanism by which constitutional claims become intersubjectively evaluable rather than author-asserted.

A test that can only be run by the author, or that produces results only the author can interpret, fails Popper's material condition for basic statements. This is a constraint on ILC's testing architecture, not merely a recommendation.

### 1.4 Science starts with problems, not observations — theory-ladenness of all observation

Popper insisted that science does not begin with raw, theory-neutral observation. It begins with problems, and all observations are theory-laden: the choice of what to observe, what counts as an observation, and how to describe what is observed are all shaped by prior theoretical commitments. (*Conjectures and Refutations*, ch. 1; SEP §5.)

ILC's design mirrors this. The reuse graph does not measure raw "value" — it measures reuse weighted by the reuser's centrality, which presupposes the theoretical claim that centrality-weighted-reuse is a good proxy for value. The measurement is always already theory-laden. This is honest, not a defect. Popper's response is not to pretend the measurement is theory-neutral but to make the theoretical commitments explicit and subject them to falsification. ILC's commitment (reuse-centrality tracks value) must itself be subject to the question: what observable outcome would show that this commitment is wrong?

### 1.5 The pile/swamp metaphor and ILC's evidence-prelock architecture

Popper's pile metaphor: "Like a building erected on piles driven into a swamp, we stop when we are satisfied that the piles are firm enough to carry the structure, at least for the time being." Scientific knowledge has no bedrock; it rests on piles driven into indeterminate ground. The stopping criterion is pragmatic: firm enough for the current load, for now. (Popper, *Logic of Scientific Discovery*, §30; SEP §4.)

This is precisely the epistemological status of ILC's foundation. Evidence prelocks do not establish eternal bedrock — they establish "firm enough for the next tranche." Each window's closure gate confirms the piles are holding before the next floor is built. The architecture is explicitly provisional and load-bearing rather than claiming to rest on incorrigible foundations.

A critical implication for ILC that follows from the pile metaphor: the closure gate standard must scale with the load. A structure carrying more load requires firmer piles. As ILC moves toward external deployment, the closure gate criteria must become progressively stricter, because the consequences of pile failure become progressively larger. The current closure gate structure (commit-boundary tests, walkthrough hygiene, window-level coherence) is appropriate for the current load. It will need revision before external participants are present.

---

## Part 2: Where Popper and ILC Diverge — Including What Has Been Superseded

### 2.1 The sharpest divergence: Popper's rejection of experience as the basis of truth

Popper argues explicitly that basic statements cannot be justified by experience. "Experiences can motivate a decision, and hence an acceptance or a rejection of a statement, but a basic statement cannot be justified by them. Rather, statements can be justified only by other statements." (*Logic of Scientific Discovery*, §29; SEP §4.) This is Popper's anti-psychologism: knowledge is not derived from subjective experience; it belongs to World 3 (objective cultural artifacts), not World 2 (subjective psychological states). (See Popper's Three Worlds ontology, SEP §7.)

This is a direct collision with ILC's praxic epistemology. ILC's claim is precisely that value is grounded in participant experience — what gets reused, by whom, weighted by their centrality. The centrality measurement is a measurement of experienced usefulness, aggregated across many participants over time. Popper would identify this as psychologistic: deriving epistemic warrant from subjective states rather than from the logical structure of statement-to-statement justification.

**The resolution — and why it matters to get it right**: ILC does not claim that individual participant experiences justify claims. It claims that the aggregate behavioral pattern — the reuse graph — is an objective, intersubjectively measurable artifact. A single participant's experience report is World 2 (subjective psychological state). The reuse graph is World 3 — an objective cultural artifact produced by the interaction of many World 2 states and measurable independently by any observer with graph access.

The Popperian discipline this imposes on ILC: individual experience reports must not be allowed to directly modify centrality scores. They must pass through a verification and aggregation layer before they affect the graph. A participant's stated preference is not a valid reuse event. The actual behavioral act of reuse — the observable, third-party-verifiable event — is. This distinction is not merely technical; it is the epistemological boundary between ILC's praxic approach (legitimate) and naive psychologism (not legitimate).

If ILC's identity and D2e subsystems allow experience reports to directly modify centrality without behavioral verification, the design has crossed into psychologism in Popper's sense. This is a non-trivial constraint on the D2e identity subsystem architecture.

### 2.2 Verisimilitude — Popper's later theory is formally broken

Popper introduced verisimilitude (truthlikeness) in the 1960s as a metalogical measure of how close a theory is to the truth, even when false. The intent was to explain why we should prefer one false theory over another: Theory A is better than Theory B if A has more truth-content and less falsity-content. (*Conjectures and Refutations*, ch. 10.)

David Miller (1974) and Pavel Tichý (1974) independently proved that Popper's formal definition fails: his conditions for comparing truthlikeness can only be satisfied when both theories are true. For false theories — the interesting case — Popper's verisimilitude measure is formally unworkable. This was a genuine formal defeat of a significant part of Popper's later theory. (Miller, "Popper's Qualitative Theory of Verisimilitude," *British Journal for the Philosophy of Science* 25(2), 1974; Tichý, "On Popper's Definitions of Verisimilitude," *British Journal for the Philosophy of Science* 25(2), 1974.)

ILC does not use verisimilitude. It uses revealed preference (what gets reused) rather than proximity-to-truth. This makes ILC immune to the Miller-Tichý problem: ILC never claims to measure how close a knowledge claim is to the objective truth; it measures how much participants act on that claim. The behavioral measurement avoids the formal collapse.

This is one case where ILC's praxic approach is technically superior to Popper's later theoretical additions.

### 2.3 Anti-inductivism — where ILC must consciously diverge

Popper was a radical anti-inductivist: no number of confirmatory instances justifies raising the probability that a theory is true. Corroboration — surviving testing — is not confirmation; it only means the theory has not yet been refuted. Popper explicitly rejected Bayesian confirmation as a model of scientific inference. (*Logic of Scientific Discovery*, ch. 10; SEP §3.)

ILC uses what is functionally an inductive signal: high reuse over many interactions raises the centrality weight of a knowledge claim. Past reuse informs future weighting. This is inductively structured — the history of successful reuse is treated as evidence for the claim's future reliability. Goldman's reliabilism licenses this (a belief-forming process that reliably tracks value is epistemically warranted by its track record), but Popper would not. Popper would say the reuse history gives you no logical grounds for preferring the claim going forward — it only tells you the claim has not yet been massively abandoned.

ILC's pragmatist response (via Peirce): the inductive-appearing signal is not a claim about logical probability. It is a claim about convergent behavioral evidence. "What investigators converge on" is not inductive in Popper's sense — it is an empirical social fact about the community's current behavior. But this is a genuine philosophical tension, not a trivially resolved one. ILC should be explicit that it is departing from Popperian anti-inductivism and explain why (pragmatist track record, Goldman's reliabilism) rather than pretending the tension does not exist.

### 2.4 Historical developments that update Popper

Several developments in philosophy of science since Popper's major works (1934–1963) are directly relevant to ILC's design:

**Kuhn's paradigm shifts (1962)**: Thomas Kuhn demonstrated in *The Structure of Scientific Revolutions* (1962) that scientists rarely abandon theories on the basis of single counter-instances. Instead, they adjust auxiliary hypotheses and accumulate anomalies until the burden becomes unsustainable, at which point a paradigm shift occurs — a wholesale replacement of the conceptual framework rather than piecemeal revision. Kuhn's challenge to Popper is that methodological falsificationism is not how science actually works, even if logical falsifiability is the right demarcation criterion.

ILC's CDL captures the Kuhnian insight: a ratified CDL row functions like a paradigm commitment, protected by auxiliary hypotheses (the evidence prelock artifacts, the deployment assumptions) until the evidence of failure is sufficient to trigger reopening. The evidence prelock structure specifies the falsification threshold — how much anomalous evidence triggers reopening — rather than relying on any single counter-instance.

**Lakatos's research programmes (1970)**: Imre Lakatos synthesized Popper and Kuhn with the methodology of scientific research programmes: a hard core of protected theoretical commitments surrounded by a positive heuristic (guidance for extending the theory) and a negative heuristic (decisions about which anomalies to deflect). The positive heuristic is the research program's forward direction. (Lakatos, "Falsification and the Methodology of Scientific Research Programmes," in Lakatos & Musgrave, *Criticism and the Growth of Knowledge*, 1970.)

ILC's CDL is a Lakatosian structure: the ratified CDLs are the hard core; the evidence prelock lanes and option inventories are the positive and negative heuristics; the window sequence structure (one window does not undermine the previous window's commitments) is the protected hard core discipline.

**Bayesian confirmation theory**: The dominant contemporary framework in philosophy of science is Bayesian, not Popperian. Scientists update beliefs on evidence using probabilistic reasoning; experiments raise or lower posterior probabilities; theories are evaluated not just by falsifiability but by their prior plausibility and how much the evidence shifts their probability. ILC's governance layer operates partly in Bayesian mode (evidence packages shift the ratification quorum's probability assessments) while the object-level measurement system is praxic. The two levels use different epistemological frameworks, which is the correct structure.

**Social epistemology (Goldman, Longino, Kitcher)**: Popper largely ignored the social dimension of science. Post-Popperian social epistemologists showed that the intersubjective testability Popper required is itself a social achievement, dependent on institutional structures, norms of communication, and diversity of perspectives. Helen Longino (*Science as Social Knowledge*, 1990) argued that objectivity requires not just public testability but active uptake of critical responses — the community must actually engage with challenges. Philip Kitcher (*The Advancement of Science*, 1993) showed that diversity of research approaches in a scientific community often produces better epistemic outcomes than convergence on a single approach.

ILC's ratification quorum, CDL process, and proposed diversity requirements are the institutional structures that make intersubjective testability operational in Popper's sense. The diversity requirements for ratification quorums (CDL-V3) are directly motivated by Kitcher's result: epistemic monoculture is worse for the community's knowledge production than managed diversity, even if individual community members have selfish reasons to prefer their own approach.

---

## Part 3: Section 4 Passages Applied Directly to ILC

*All section 4 references are to the Stanford Encyclopedia of Philosophy entry on Popper, §4 "Basic Statements, Falsifiability and Convention": https://plato.stanford.edu/entries/popper/#BasiStatFalsConv*

### 3.1 Basic statements as the agent decomposition criteria ILC does not yet have

Popper defines basic statements with two requirements:

**(a) Formal**: singular and existential in structure — of the form "There is an X at Y" — not universal, not vague, not compound. A basic statement makes a specific claim about a specific observable state of affairs.

**(b) Material**: intersubjectively testable — multiple independent observers can evaluate it against observable fact without coordinating on how to interpret the claim.

You identified this correctly as a gap: this is a potential formal criterion for agents decomposing "subjective broader submissions to ILC into smaller, 'objective' building blocks that can be reused and recombined into new knowledge." ILC currently has no formal definition of what constitutes a valid submittable knowledge unit. The Popperian basic statement requirements supply this.

A valid ILC knowledge unit (the ILC analog of a Popperian basic statement) must satisfy:

1. **Formally singular and existential**: it makes a specific claim about a specific thing under specific conditions. "This algorithm solved problem-class X under conditions Y" is valid. "This algorithm is generally better" is not — it is universal, not singular; vague, not existential.

2. **Materially intersubjectively testable**: another agent, given the same inputs and conditions, can independently evaluate whether the claim holds without relying on the submitter's interpretation.

3. **Falsifiable by counter-instance**: there must exist specifiable conditions under which the claim would be refuted, and those conditions must be observationally detectable by independent agents.

The agent decomposition process — taking a subjective holistic submission and extracting from it the singular, testable, falsifiable components — is not a preprocessing convenience. It is the epistemological gatekeeping mechanism that determines what enters the ILC knowledge graph at all. A claim that fails any of the three conditions above should not receive a centrality weight; it cannot be meaningfully reused, because it cannot be independently evaluated.

This is CDL-V7 (see §4 below for disposition).

### 3.2 Methodological vs. logical falsification — the distinction between evidence prelock and CDL ratification

Popper distinguishes sharply between the logical structure and the methodological practice of falsification. Logically, a single genuine counter-instance falsifies a universal statement — there is no escape. Methodologically, a single anomaly is never sufficient in practice: measurement error, observer error, and auxiliary hypothesis adjustment all intervene. The scientist's response to a single counter-instance is rarely to abandon the theory; it is to investigate whether the anomaly is genuine. (SEP §4.)

ILC's two-stage structure maps onto this distinction precisely:

- **Evidence prelock** = the logical falsification structure. The prelock specifies what would constitute a genuine counter-instance for the CDL claim. It sets the logical conditions under which the claim must be considered falsified. This is where the demarcation criterion operates.

- **CDL ratification ceremony** = the methodological judgment. The ratification quorum evaluates the assembled evidence and makes the conventional decision that the evidence is sufficient. This is Popper's methodological falsification — a conventional decision, subject to revision, that the piles are firm enough.

The prelock exists precisely to prevent ratification from becoming purely conventional with no logical anchor. The ratification exists because logical conditions alone are never sufficient to settle the real-world question — someone must evaluate whether the counter-instance is genuine and whether the threshold has been met.

A CDL process that skips the prelock and goes directly to ratification has discarded the logical structure and retained only the conventional decision. It has achieved the appearance of epistemic discipline without the content.

### 3.3 The testing regress and the jury analogy — as models for ratification termination

Popper: "Every test of a theory, whether resulting in its corroboration or falsification, must stop at some basic statement or other which we decide to accept. This decision is a decision to accept a basic statement — which is not itself derived from observation or from a further test, but is a conventional decision to call the testing off." (SEP §4, paraphrasing *Logic of Scientific Discovery* §29.)

The jury analogy: acceptance of basic statements is comparable to a jury verdict — a conventional agreement arising from established procedures and deliberation, not from an incorrigible fact of nature. Jury verdicts are:
- Conventional (based on procedural norms, not direct access to truth),
- Intersubjective (a group reaches the verdict, not an individual),
- Revisable (appeal mechanisms exist, verdicts can be overturned),
- Bounded (the jury cannot deliberate until the evidence presentation is complete).

For ILC: ratification ceremonies are jury verdicts. They terminate the testing regress by convention (the quorum agrees the evidence package is sufficient). They are revisable (CDL rows can be reopened if falsification criteria are triggered). The no-ratification-before-lock guard is the equivalent of procedural due process — the jury cannot deliberate before the evidence is assembled.

What ILC currently lacks that the jury analogy demands: a formal **appeal mechanism**. The CDL can be reopened, but who initiates reopening, under what conditions, and via what formal process? The Genesis agent's intervention criteria (documented in `docs/specs/ilc_epistemological_foundations_canonical_v0.1.md` §5) cover intervention against capture or constitutional violation. But the routine appeal case — "we believe this ratified decision was reached on insufficient evidence and should be re-evaluated" — is not yet formally specified. This is the CDL-V4 / formalized reopening protocol gap (see §4 below).

### 3.4 The pile/swamp metaphor — and what it means for ILC's epistemic humility

Popper: "Like a building erected on piles driven into a swamp, our theories are not anchored to any bedrock, nor derived from any certain foundation. We simply stop when we are satisfied that the piles are firm enough to carry the structure, at least for the time being." (SEP §4; *Logic of Scientific Discovery* §30.)

This is the exact epistemic posture of ILC's window-closure gates. The Phase 307 closure gate did not prove that the D2e system is correct. It established that the piles are firm enough to carry the next floor (Phase 308-317). The Phase 295 closure gate did not prove that the CDL-031/033 ratifications were optimal. It established that the foundation is firm enough to begin the D2 schema baseline work.

Every closure gate is a conventional "firm enough for now" decision, not a claim to have reached bedrock. This is epistemologically correct. But it also carries a specific responsibility: the convention of calling the piles firm enough must be genuinely informed by the evidence assembled, not merely performed to advance the schedule.

The closure gate validation categories (prompt contract, lane-specific tests, cross-phase regression, mutation canary, CLI contract, walkthrough hygiene) are the operational specification of "firm enough." Each category is one axis of structural integrity. If any category fails, the piles are not firm enough, and the structure must not advance.

### 3.5 Popper's rejection of experience-as-foundation — and what ILC must assert instead

From SEP §4: "Experiences can motivate a decision, and hence an acceptance or a rejection of a statement, but a basic statement cannot be justified by them — a basic statement cannot be derived from, nor verified by, experience alone. Rather, statements can be justified only by other statements."

This is Popper's sharpest anti-psychologistic claim. You noted correctly: "This is a deep statement here that might conflict with ILC, depending on how we do things."

The conflict is real and ILC must be explicit about how it navigates it:

**What Popper forbids**: deriving epistemic warrant from individual subjective experience. A single participant saying "I found this claim valuable" does not constitute evidence. The participant's experience may have motivated their reuse, but the experience itself is not the epistemological content.

**What ILC claims**: the aggregate behavioral pattern — the reuse graph, the centrality distribution — is an objective World 3 artifact. It is produced by many subjective experiences, but it is not reducible to any of them. Any independent observer with graph access can verify the centrality measurements. The graph is intersubjectively testable in exactly Popper's sense.

**The operational consequence**: ILC must build and maintain a strict boundary between:
- **World 2 experience reports** (participant testimonials, stated preferences, qualitative assessments) — these can motivate reuse decisions but cannot directly modify the graph.
- **World 3 behavioral records** (verified reuse events, confirmed identity linkages, commit-anchored test outcomes) — these are the valid epistemic inputs to the graph.

If the D2e identity subsystem or the reuse event submission protocol allows experience reports to directly modify centrality without behavioral verification, ILC has crossed into psychologism. This constraint should be explicit in the CDL-033 (OpenClaw skill publication) and D2e subsystem contracts: the distinction between stated preference and verified behavioral reuse is a constitutional requirement, not an implementation detail.

---

## Summary Table

| Dimension | Popper | ILC | Status |
|---|---|---|---|
| Falsifiability as demarcation | Core criterion | Evidence prelock declares falsification conditions | **Aligned** |
| Fallibilism / revisability | All beliefs tentative | CDL rows can be reopened | **Aligned** |
| Intersubjective testability | Material condition for basic statements | Commit-anchored tests | **Aligned** |
| Theory-ladenness of observation | All observation theory-laden | Centrality measurement is theory-laden | **Aligned — must be explicit** |
| Provisional foundations (pile/swamp) | No bedrock; stop when firm enough | Window closure gates | **Aligned** |
| Experience as truth-basis | Rejected (psychologism) | Aggregate reuse graph is World 3, not World 2 | **Navigable — requires explicit boundary** |
| Anti-inductivism | Strict — corroboration is not confirmation | Reuse history informs centrality weights | **Genuine tension — departure must be explicit** |
| Verisimilitude | Proposed but formally broken (Miller-Tichý 1974) | Not used | **ILC avoids the broken theory** |
| Kuhnian paradigm structure | Not in Popper | Ratified CDL as hard core + evidence prelock protective belt | **ILC extends Popper via Lakatos/Kuhn** |
| Social epistemology | Largely ignored by Popper | Quorum diversity, ratification norms | **ILC extends Popper via Goldman/Kitcher** |
| Bayesian confirmation | Rejected by Popper | Governance layer operates partly Bayesian | **ILC uses two-level framework** |
| Appeal/reopening mechanism | Jury verdicts are revisable | Informal Genesis authority only | **Gap — CDL-V4 candidate** |
| Agent decomposition criteria | Basic statement requirements | Not yet formalized | **Gap — CDL-V7 candidate** |

---

## Section 4: Disposition of the Two Gaps Identified

### 4.1 CDL-V7: Formal criteria for a valid ILC knowledge unit

**What it is**: A constitutional decision establishing the formal demarcation criterion for what counts as a valid submittable knowledge unit in the ILC epistemic graph. Grounded in Popper's basic statement requirements: singular, existential, intersubjectively testable, falsifiable by counter-instance.

**Why it matters now**: Without this criterion, the agent decomposition layer (the process by which subjective holistic submissions are decomposed into objective reusable building blocks) has no constitutional basis. It will be implemented ad hoc rather than consistently. This is an increasingly urgent gap as D2e subsystems begin accepting external knowledge submissions.

**Recommended disposition**:
- **Phase 315** (schema/evidence track, window 308-317): Write the evidence prelock document establishing the CDL-V7 design question, the option inventory, and the candidate specification.
- **Window 318+**: Open CDL-V7 as a formal CDL entry and execute ratification lane.

**Why not now**: We are in window 308-317 with a no-ratification-before-lock guard and CDL mutation prohibitions. The correct action in this window is to document the design question and prepare the evidence prelock package.

### 4.2 Formalized reopening protocol (CDL-V4 scope expansion)

**What it is**: A formal specification of the conditions under which a ratified CDL row may be reopened, who may initiate reopening, what evidence threshold triggers mandatory review, and what process governs the re-evaluation. This is the operational implementation of the jury appeal mechanism the Popperian model requires.

**Current state**: CDL-V4 was proposed as "minority dissent and appeal mechanism." The reopening protocol is the appropriate CDL-V4 scope expansion — the appeal mechanism IS the reopening protocol.

**Recommended disposition**:
- **Phase 315** (schema/evidence track, window 308-317): Expand the CDL-V4 evidence prelock scope to include the formalized reopening protocol. Document the proposed structure: initiating conditions, evidence threshold, re-evaluation process, Genesis agent intervention criteria for reopening disputes.
- **Window 318+**: Execute CDL-V4 ratification lane.

**Why not now**: Same constraint as CDL-V7. Window 308-317 prohibits CDL mutation.

---

## References

Primary philosophical sources:

- Popper, K.R. (1934/1959). *The Logic of Scientific Discovery*. Hutchinson. (Original German: *Logik der Forschung*, 1934.)
- Popper, K.R. (1963). *Conjectures and Refutations: The Growth of Scientific Knowledge*. Routledge.
- Popper, K.R. (1972). *Objective Knowledge: An Evolutionary Approach*. Oxford University Press.

Formal disproof of Popper's verisimilitude:

- Miller, D. (1974). "Popper's Qualitative Theory of Verisimilitude." *British Journal for the Philosophy of Science*, 25(2), 166–177.
- Tichý, P. (1974). "On Popper's Definitions of Verisimilitude." *British Journal for the Philosophy of Science*, 25(2), 155–160.

Post-Popperian developments:

- Kuhn, T.S. (1962). *The Structure of Scientific Revolutions*. University of Chicago Press.
- Lakatos, I. (1970). "Falsification and the Methodology of Scientific Research Programmes." In I. Lakatos & A. Musgrave (Eds.), *Criticism and the Growth of Knowledge*. Cambridge University Press.
- Goldman, A. (1986). *Epistemology and Cognition*. Harvard University Press.
- Goldman, A. (1999). *Knowledge in a Social World*. Oxford University Press.
- Longino, H. (1990). *Science as Social Knowledge: Values and Objectivity in Scientific Inquiry*. Princeton University Press.
- Kitcher, P. (1993). *The Advancement of Science: Science without Legend, Objectivity without Illusions*. Oxford University Press.

Encyclopedia reference for this analysis:

- Thornton, S. (2024). "Karl Popper." In E.N. Zalta & U. Nodelman (Eds.), *Stanford Encyclopedia of Philosophy*. https://plato.stanford.edu/entries/popper/
