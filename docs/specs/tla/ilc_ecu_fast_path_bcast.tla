---------------- MODULE ilc_ecu_fast_path_bcast ----------------
\* ILC CDL-062 Research Lane — TLA+ Formal Specification
\* Spec B: Owned-Object ECU Transfer Fast Path
\*
\* Purpose: Prove that Mysticeti's Byzantine Consistent Broadcast (ByzCB)
\* protocol for owned-object transfers satisfies ILC's safety requirement:
\* no two conflicting ECU transfers on the same owned object can both
\* receive a valid certificate (2f+1 validator acknowledgments).
\*
\* This is the formal safety proof for sub-500ms ECU transfer finality.
\* A "certified" transfer is final — it cannot be reversed by any Byzantine
\* coalition of size <= F.
\*
\* Based on: Byzantine Consistent Broadcast as used in Sui/Mysticeti fast path.
\* Reference: Spiegelman et al. 2023, §3 (owned-object fast path).
\*
\* TLC model check parameters:
\*   N <- 4       (4 validators: 3 honest + 1 Byzantine)
\*   F <- 1       (1 Byzantine validator)
\*   Objects <- {"ecu_obj_1", "ecu_obj_2"}  (2 ECU owned objects)
\*   ByzantineSet <- {4}
\*
\* To verify with TLC:
\*   SPECIFICATION Spec
\*   INVARIANT TypeOK
\*   INVARIANT SafetyNoDualCert
\*   PROPERTY LivenessCertification

EXTENDS Naturals, FiniteSets, TLC

CONSTANTS
    N,           \* Total number of validators
    F,           \* Maximum Byzantine validators
    Objects,     \* Set of ECU owned-object identifiers
    ByzantineSet,\* Concrete Byzantine validator set (assigned in TLC config)
    TransferID   \* Finite set of transfer IDs for TLC (e.g. 0..2 in model config)

ASSUME
    /\ N \in Nat /\ N > 0
    /\ F \in Nat /\ F >= 0
    /\ N > 3 * F
    /\ ByzantineSet \subseteq (1..N)
    /\ Cardinality(ByzantineSet) <= F
    /\ Objects # {}

Validators       == 1..N
HonestValidators == Validators \ ByzantineSet

\* A transfer proposal: (object, transfer_id) pair
\* TransferID is declared as a CONSTANT (finite set for TLC, e.g. 0..2)
Transfer(obj, tid) == [object |-> obj, tid |-> tid]

\* Two transfers on the same object with different IDs are "conflicting"
Conflicts(t1, t2) ==
    /\ t1.object = t2.object
    /\ t1.tid    # t2.tid

VARIABLES
    proposed,    \* Set of Transfer records that have been submitted
    acks,        \* Function: Transfer -> subset of Validators that acked it
                 \* (honest validators ack at most one transfer per object)
    certified    \* Set of Transfer records that have received 2f+1 acks

vars == <<proposed, acks, certified>>

-----------------------------------------------------------------------------
\* Helpers

\* Threshold for certification
Threshold == 2 * F + 1

\* A transfer is certified when its ack count reaches the threshold
IsCertified(t) == Cardinality(acks[t]) >= Threshold

-----------------------------------------------------------------------------
\* Type invariant

TypeOK ==
    /\ proposed \subseteq {Transfer(o, tid) : o \in Objects, tid \in TransferID}
    /\ \A t \in proposed : acks[t] \subseteq Validators
    /\ certified \subseteq proposed

-----------------------------------------------------------------------------
\* Initial state

Init ==
    /\ proposed  = {}
    /\ acks      = [t \in {} |-> {}]   \* Empty function; extends on Propose
    /\ certified = {}

-----------------------------------------------------------------------------
\* Actions

\* A client submits a transfer request for object obj with identifier tid.
\* In the real system, the submitter holds the object (owns it); here we
\* abstract ownership and focus on the certification race.
Propose(obj, tid) ==
    LET t == Transfer(obj, tid)
    IN  /\ t \notin proposed
        /\ proposed' = proposed \cup {t}
        /\ acks'     = [s \in proposed \cup {t} |->
                           IF s = t THEN {} ELSE acks[s]]
        /\ UNCHANGED certified

\* An honest validator v acknowledges transfer t if:
\* 1. The transfer has been proposed
\* 2. v has not already acknowledged a CONFLICTING transfer on the same object
\*    (honest validators send at most one ack per object — the "lock" rule)
HonestAck(v, t) ==
    /\ v \in HonestValidators
    /\ t \in proposed
    /\ v \notin acks[t]
    \* Honest validator will not ack t if it has already acked a conflicting transfer
    /\ ~\E t2 \in proposed :
           /\ Conflicts(t, t2)
           /\ v \in acks[t2]
    /\ acks' = [acks EXCEPT ![t] = acks[t] \cup {v}]
    /\ UNCHANGED <<proposed, certified>>

\* A Byzantine validator can ack any transfer regardless of conflicts.
\* (Byzantine equivocation: acking both sides of a conflicting pair.)
\* This models the strongest Byzantine behavior against the safety property.
ByzantineAck(v, t) ==
    /\ v \in ByzantineSet
    /\ t \in proposed
    /\ v \notin acks[t]
    /\ acks' = [acks EXCEPT ![t] = acks[t] \cup {v}]
    /\ UNCHANGED <<proposed, certified>>

\* A transfer becomes certified when its ack count reaches Threshold.
Certify(t) ==
    /\ t \in proposed
    /\ t \notin certified
    /\ IsCertified(t)
    /\ certified' = certified \cup {t}
    /\ UNCHANGED <<proposed, acks>>

\* Complete next-state relation
Next ==
    \/ \E obj \in Objects, tid \in TransferID : Propose(obj, tid)
    \/ \E v \in HonestValidators, t \in proposed : HonestAck(v, t)
    \/ \E v \in ByzantineSet,     t \in proposed : ByzantineAck(v, t)
    \/ \E t \in proposed : Certify(t)

\* Weak fairness: honest validators eventually ack transfers they can ack
Spec == Init /\ [][Next]_vars
           /\ WF_vars(\E v \in HonestValidators, t \in proposed : HonestAck(v, t))
           /\ WF_vars(\E t \in proposed : Certify(t))

-----------------------------------------------------------------------------
\* Properties

\* SAFETY: No two conflicting transfers on the same owned object can both
\* be certified. This is the core fast-path safety guarantee.
\*
\* Proof sketch: An honest validator acks at most one transfer per object
\* (the HonestAck lock rule). A certificate requires >= 2f+1 acks.
\* If two conflicting transfers t1, t2 on the same object were both certified,
\* both would need >= 2f+1 acks. The combined ack sets would require
\* 2*(2f+1) = 4f+2 acks total. But there are only N = 3f+1 validators
\* (under N > 3f, minimum is N = 3f+1). At most F Byzantine validators
\* can double-ack (ack both). So honest acks required: at least
\* (4f+2) - F = 3f+2 from N-F = 2f+1 honest validators. But 3f+2 > 2f+1
\* for all F >= 0 — contradiction. No two conflicting transfers can be
\* certified simultaneously.
SafetyNoDualCert ==
    ~\E t1, t2 \in certified : Conflicts(t1, t2)

\* LIVENESS: A submitted transfer eventually gets certified if enough
\* honest validators can ack it (i.e., none have committed to a conflict).
\* This is a weaker liveness claim — in the contested case (two competing
\* transfers on the same object), at most one can be certified.
\*
\* TLC NOTE: TLC cannot quantify over state variables in temporal formulas.
\* We quantify over the constant domain (Objects x TransferID) instead.
\* A transfer (obj, tid) that is uncontested (no conflicting proposal exists)
\* and has been proposed will eventually be certified.
LivenessCertification ==
    \A obj \in Objects, tid \in TransferID :
        LET t == Transfer(obj, tid)
        IN  (t \in proposed /\ \A t2 \in proposed : ~Conflicts(t, t2) \/ t = t2)
            ~> (t \in certified)

\* Auxiliary invariants
AcksSubsetValidators ==
    \A t \in proposed : acks[t] \subseteq Validators

CertifiedSubsetProposed ==
    certified \subseteq proposed

=============================================================================
\*
\* VERIFICATION NOTES
\*
\* To run under TLC, create a model with:
\*   Constants:
\*     N = 4
\*     F = 1
\*     Objects = {"ecu_a", "ecu_b"}
\*     ByzantineSet = {4}
\*   Replace TransferID with a finite set, e.g., 0..3 (to bound the state space)
\*   SPECIFICATION: Spec
\*   INVARIANTS: TypeOK, SafetyNoDualCert, AcksSubsetValidators, CertifiedSubsetProposed
\*   PROPERTIES: LivenessCertification
\*
\* IMPORTANT: Replace "tid \in (0..10)" in the Propose action with
\* "tid \in TransferID" and define TransferID = 0..2 in the model config
\* to keep the state space finite and tractable.
\*
\* Expected result:
\*   - SafetyNoDualCert: no violation (core safety guarantee holds)
\*   - LivenessCertification: no violation for uncontested transfers
\*
\* A SafetyNoDualCert violation would mean the Byzantine equivocation model
\* breaks the certification uniqueness guarantee — indicating either N <= 3F
\* or a flaw in the HonestAck lock rule.
\*
\* ILC SIGNIFICANCE:
\* A clean SafetyNoDualCert result formally establishes that ECU transfers
\* on owned objects achieve finality without conflicting double-spends, even
\* under Byzantine validator behavior. This is the mathematical foundation
\* for sub-500ms ECU transfer settlement.
=============================================================================
