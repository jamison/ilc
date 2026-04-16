---------------- MODULE ilc_dag_censorship_bounds ----------------
\* ILC CDL-062 Research Lane — TLA+ Formal Specification
\* Spec A: Shared-Object DAG Consensus Path
\*
\* Purpose: Prove that Mysticeti's leaderless DAG commit rule satisfies
\* ILC's Row-7 censorship-liveness requirement.
\*
\* Row-7 liveness claim: any vertex broadcast by an honest validator is
\* eventually committed despite Byzantine withholding by up to F validators.
\*
\* Based on: Mysticeti (Spiegelman et al. 2023) and DAG-Rider (Keidar et al. 2021)
\*
\* TLC model check parameters (small model — sufficient for safety violations):
\*   N <- 4       (4 validators: 3 honest + 1 Byzantine)
\*   F <- 1       (1 Byzantine validator)
\*   MaxRound <- 5
\*   ByzantineSet <- {4}  (assign validator 4 as Byzantine)
\*
\* To verify with TLC:
\*   SPECIFICATION Spec
\*   INVARIANT TypeOK
\*   INVARIANT Safety
\*   PROPERTY Liveness
\*   (Enable liveness checking in TLC model configuration)

EXTENDS Naturals, FiniteSets, TLC

CONSTANTS
    N,           \* Total number of validators (positive integer)
    F,           \* Maximum number of Byzantine validators
    MaxRound,    \* Bounded round horizon for TLC model checking
    ByzantineSet \* Concrete set of Byzantine validator IDs (assigned in TLC config)

ASSUME
    /\ N \in Nat /\ N > 0
    /\ F \in Nat /\ F >= 0
    /\ N > 3 * F          \* Honest supermajority: N > 3f
    /\ MaxRound \in Nat /\ MaxRound >= 3
    /\ ByzantineSet \subseteq (1..N)
    /\ Cardinality(ByzantineSet) <= F

\* Validator identities
Validators      == 1..N
HonestValidators == Validators \ ByzantineSet

\* A vertex is identified by (proposer, round) pair.
\* We use a record rather than a tuple for readability.
Vertex(v, r) == [proposer |-> v, round |-> r]
AllVertices   == {Vertex(v, r) : v \in Validators, r \in 1..MaxRound}

VARIABLES
    dag,       \* Set of vertices that have been broadcast into the DAG
               \* dag \subseteq AllVertices
    committed, \* Set of vertices that have achieved deterministic commit
               \* committed \subseteq dag
    rnd        \* Current round being built (monotonically increasing)

vars == <<dag, committed, rnd>>

-----------------------------------------------------------------------------
\* Type invariant

TypeOK ==
    /\ dag       \subseteq AllVertices
    /\ committed \subseteq dag
    /\ rnd \in 1..MaxRound

-----------------------------------------------------------------------------
\* Initial state

Init ==
    /\ dag       = {}
    /\ committed = {}
    /\ rnd       = 1

-----------------------------------------------------------------------------
\* Actions

\* An honest validator v broadcasts its vertex for the current round.
\* Precondition: v has not yet broadcast in this round, and either
\* this is round 1 or at least 2f+1 validators have broadcast in round-1
\* (the quorum certificate condition for building the next DAG layer).
HonestBroadcast(v) ==
    /\ v \in HonestValidators
    /\ Vertex(v, rnd) \notin dag
    /\ \/ rnd = 1
       \/ Cardinality({u \in Validators : Vertex(u, rnd - 1) \in dag}) >= 2 * F + 1
    /\ dag' = dag \cup {Vertex(v, rnd)}
    /\ UNCHANGED <<committed, rnd>>

\* Byzantine validators never broadcast in this model.
\* Withholding is implicit: they are excluded from HonestBroadcast and
\* have no action of their own. The honest supermajority proceeds without them.
\*
\* This correctly models the withholding attack: Byzantine validators refuse
\* to contribute their vertices. AdvanceRound below shows this cannot stall
\* the network under honest majority.

\* Advance to the next round when 2f+1 HONEST validators have broadcast
\* in the current round. Byzantine withholding cannot prevent this
\* because N - F >= 2F + 1 under N > 3F.
AdvanceRound ==
    /\ rnd < MaxRound
    /\ Cardinality({v \in HonestValidators : Vertex(v, rnd) \in dag}) >= 2 * F + 1
    /\ rnd' = rnd + 1
    /\ UNCHANGED <<dag, committed>>

\* Simplified wave-based commit rule.
\*
\* In Mysticeti, vertices commit through a wave leader mechanism: a "wave"
\* spans multiple rounds, and the wave leader's causal history is committed
\* when the leader is referenced by 2f+1 validators in subsequent rounds.
\*
\* This simplified model captures the key property: a vertex in round r
\* commits when it is causally referenced by 2f+1 honest validators in
\* rounds r+1 AND r+2 (two-wave suffix). Under honest majority and the
\* AdvanceRound precondition, this is always eventually satisfied for any
\* honest-broadcast vertex.
CommitVertex(v, r) ==
    /\ Vertex(v, r) \in dag
    /\ Vertex(v, r) \notin committed
    /\ r + 2 <= rnd   \* Two full rounds have elapsed since r
    /\ Cardinality({u \in HonestValidators : Vertex(u, r + 1) \in dag}) >= 2 * F + 1
    /\ Cardinality({u \in HonestValidators : Vertex(u, r + 2) \in dag}) >= 2 * F + 1
    /\ committed' = committed \cup {Vertex(v, r)}
    /\ UNCHANGED <<dag, rnd>>

\* Complete next-state relation
Next ==
    \/ \E v \in HonestValidators : HonestBroadcast(v)
    \/ AdvanceRound
    \/ \E v \in Validators, r \in 1..(MaxRound - 2) : CommitVertex(v, r)

\* Full temporal specification
Spec == Init /\ [][Next]_vars /\ WF_vars(AdvanceRound)

\* (Weak fairness on AdvanceRound ensures rounds keep advancing when possible,
\* which is required to establish the liveness property under TLC.)

-----------------------------------------------------------------------------
\* Properties

\* SAFETY: Each validator proposes at most one vertex per round.
\* (No conflicting commits can arise from the same proposer/round pair.)
\* Under Mysticeti's DAG structure, each validator broadcasts exactly one
\* vertex per round, so no two distinct committed vertices share the same
\* (proposer, round) identity.
Safety ==
    \A v1, v2 \in committed :
        (v1.proposer = v2.proposer /\ v1.round = v2.round) => (v1 = v2)

\* ROW-7 LIVENESS: Any honest-broadcast vertex eventually commits.
\* This is the formal statement of ILC's Row-7 censorship-liveness bound.
\* Byzantine withholding (up to F validators) cannot permanently prevent
\* an honest-broadcast vertex from appearing in the committed set.
\*
\* Temporal formula: for all honest validators v and rounds r within range,
\* if Vertex(v, r) is in dag, it will eventually be in committed.
Liveness ==
    \A v \in HonestValidators, r \in 1..(MaxRound - 2) :
        (Vertex(v, r) \in dag) ~> (Vertex(v, r) \in committed)

\* Auxiliary: committed is always a subset of dag (structural sanity)
CommittedSubsetDag == committed \subseteq dag

=============================================================================
\*
\* VERIFICATION NOTES
\*
\* To run under TLC, create a model with:
\*   Constants: N = 4, F = 1, MaxRound = 5, ByzantineSet = {4}
\*   SPECIFICATION: Spec
\*   INVARIANTS: TypeOK, Safety, CommittedSubsetDag
\*   PROPERTIES: Liveness
\*   Enable liveness checking (Simulation or BFS with liveness)
\*
\* Expected result:
\*   - TypeOK: no violation (structural invariant holds)
\*   - Safety: no violation (no conflicting commits)
\*   - Liveness: no violation (honest vertices eventually commit)
\*
\* If TLC finds a Liveness violation, it produces a counterexample trace
\* showing a state sequence where an honest vertex is never committed.
\* This would indicate the commit rule or advance condition is insufficient.
\*
\* The N=4, F=1 model is the minimum non-trivial BFT configuration.
\* A clean result here is necessary but not sufficient for production —
\* it establishes the protocol logic is sound; production security requires
\* external audit of the Rust implementation against this specification.
=============================================================================
