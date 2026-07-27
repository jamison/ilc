---------------- MODULE ilc_substrate_timing_admission_1590 ----------------
\* Phase 1590 — ILC substrate timing/admission safety model.
\*
\* This model extends the Phase 1385a epoch-checkpoint SafetyNoDualCert
\* model with:
\*   - not_before_unix_ms acceptance timing
\*   - minimum epoch duration
\*   - dynamic validator admission/ejection
\*   - Rust quorum_threshold(n) implementation correspondence
\*
\* It intentionally models the live Rust threshold formula:
\*   quorum_threshold(n) = 2 * floor((n - 1) / 3) + 1
\* and therefore checks whether admitting a fifth validator preserves the
\* dual-certificate safety claim under that implementation.

EXTENDS Naturals, FiniteSets, Sequences, TLC

CONSTANTS
    ValidatorIds,
    InitialValidators,
    ByzantineSet,
    Roots,
    Times,
    MaxEpoch,
    MinEpochDuration,
    ClockSkewTolerance

ASSUME
    /\ InitialValidators \subseteq ValidatorIds
    /\ ByzantineSet \subseteq ValidatorIds
    /\ Cardinality(ByzantineSet) = 1
    /\ Cardinality(InitialValidators) = 4
    /\ Roots # {}
    /\ Times # {}
    /\ MaxEpoch \in Nat /\ MaxEpoch > 0
    /\ MinEpochDuration \in Nat /\ MinEpochDuration > 0
    /\ ClockSkewTolerance \in Nat

VARIABLES
    committedEpoch,
    now,
    validators,
    ejectedThisEpoch,
    signed,
    certified

vars == <<committedEpoch, now, validators, ejectedThisEpoch, signed, certified>>

MaxTime == CHOOSE t \in Times : \A x \in Times : x <= t

QuorumThreshold(n) == 2 * ((n - 1) \div 3) + 1

Checkpoint(e, r, t, signers) ==
    [epoch |-> e, root |-> r, not_before |-> t, signers |-> signers]

Conflicts(c1, c2) ==
    /\ c1.epoch = c2.epoch
    /\ c1.root # c2.root

SignedRecord(e, r, v) ==
    [epoch |-> e, root |-> r, signer |-> v]

CanSign(v, e, r) ==
    \/ v \in ByzantineSet
    \/ ~\E s \in signed :
          /\ s.signer = v
          /\ s.epoch = e
          /\ s.root # r

SignersCanSign(e, r, signers) ==
    \A v \in signers : CanSign(v, e, r)

TimingOK(t) ==
    /\ t <= now + ClockSkewTolerance
    /\ IF committedEpoch = 0
       THEN TRUE
       ELSE \A c \in certified :
              c.epoch = committedEpoch => t >= c.not_before + MinEpochDuration

TypeOK ==
    /\ committedEpoch \in 0..MaxEpoch
    /\ now \in Times
    /\ validators \subseteq ValidatorIds
    /\ Cardinality(validators) >= 4
    /\ ejectedThisEpoch \subseteq ValidatorIds
    /\ signed \subseteq { SignedRecord(e, r, v) :
                            e \in 1..MaxEpoch,
                            r \in Roots,
                            v \in ValidatorIds }
    /\ certified \subseteq { Checkpoint(e, r, t, signers) :
                               e \in 1..MaxEpoch,
                               r \in Roots,
                               t \in Times,
                               signers \in SUBSET ValidatorIds }

Init ==
    /\ committedEpoch = 0
    /\ now = 0
    /\ validators = InitialValidators
    /\ ejectedThisEpoch = {}
    /\ signed = {}
    /\ certified = {}

Tick ==
    \E nextNow \in Times :
        /\ nextNow > now
        /\ now' = nextNow
        /\ UNCHANGED <<committedEpoch, validators, ejectedThisEpoch, signed, certified>>

AdmitValidator ==
    \E v \in ValidatorIds :
        /\ v \notin validators
        /\ v \notin ejectedThisEpoch
        /\ validators' = validators \cup {v}
        /\ UNCHANGED <<committedEpoch, now, ejectedThisEpoch, signed, certified>>

EjectValidator ==
    \E v \in validators :
        /\ Cardinality(validators) > 4
        /\ validators' = validators \ {v}
        /\ ejectedThisEpoch' = ejectedThisEpoch \cup {v}
        /\ UNCHANGED <<committedEpoch, now, signed, certified>>

CertifyCheckpoint ==
    \E r \in Roots, t \in Times, signers \in SUBSET validators :
        LET e == committedEpoch + 1
            c == Checkpoint(e, r, t, signers)
        IN
        /\ committedEpoch < MaxEpoch
        /\ Cardinality(signers) >= QuorumThreshold(Cardinality(validators))
        /\ SignersCanSign(e, r, signers)
        /\ TimingOK(t)
        /\ c \notin certified
        /\ certified' = certified \cup {c}
        /\ signed' = signed \cup { SignedRecord(e, r, v) : v \in signers }
        /\ UNCHANGED <<committedEpoch, now, validators, ejectedThisEpoch>>

CommitCheckpoint ==
    \E c \in certified :
        /\ c.epoch = committedEpoch + 1
        /\ committedEpoch' = c.epoch
        /\ ejectedThisEpoch' = {}
        /\ UNCHANGED <<now, validators, signed, certified>>

Stutter ==
    UNCHANGED vars

Next ==
    \/ Tick
    \/ AdmitValidator
    \/ EjectValidator
    \/ CertifyCheckpoint
    \/ CommitCheckpoint
    \/ Stutter

Spec == Init /\ [][Next]_vars

NoSkipEpoch ==
    \A c \in certified : c.epoch \in 1..(committedEpoch + 1)

NoFastMainnetEpoch ==
    \A c1, c2 \in certified :
        (c2.epoch = c1.epoch + 1) => c2.not_before >= c1.not_before + MinEpochDuration

NoFutureCheckpointAccepted ==
    \A c \in certified : c.not_before <= MaxTime + ClockSkewTolerance

NoEjectedValidatorActiveSameEpoch ==
    ejectedThisEpoch \cap validators = {}

SafetyNoDualCert ==
    ~\E c1, c2 \in certified : Conflicts(c1, c2)

=============================================================================
