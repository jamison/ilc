# Intelligent Labor Coin (ILC)

*A sovereign substrate for human-AI civilization.*

The world generates more intelligence — human and machine — than any institution can coordinate. Centralized systems cannot keep up: they become capture points, bottlenecks, or collapse under the epistemic weight of a billion simultaneous claims about reality. What is needed is a protocol that treats truth as infrastructure.

ILC is that protocol. It is an evidence-first, content-addressed knowledge network designed to serve as shared economic and epistemic ground for autonomous agents, human researchers, and the hybrid intelligence between them. In ILC, no claim is true by declaration — every assertion enters a Popperian epistemic graph where it can be refuted, verified, and economically settled without a trusted intermediary. The network does not ask *who are you?* — it asks *what did you prove?*

The native economic unit, **ECU** (Epistemic Credit Unit), is not minted by fiat. It is constructed by verified work flowing through the jury system and destroyed by decay and mandatory conversion. The external settlement token, **ILC** (Intelligent Labor Coin), is the scarce, auditable proof that some portion of the network's intelligence was deployed productively. Status equals deployment velocity times quality — not accumulated balance.

This is not a blockchain. It is a **morphogenetic hypergraph** — a distributed structure whose organizing principles repeat self-similarly at every scale, from individual claims to the constitutional rules that govern the protocol itself. The governance is *in* the graph: CDLs, ADRs, and activation certificates are first-class nodes, traversable by the same verification machinery as scientific claims. An agent can read the law from the graph.

**One irreversible human moment.** When you initialize an ILC node for the first time, a keypair ceremony takes place. In the full production ceremony (Phase 1431), a seed phrase is generated — 24 words encoding your agent's cryptographic root. **Write it down and store it offline before the command returns.** This seed phrase is the anchor of your identity in the network; lose it and your agent lineage cannot be recovered. From the seed, the protocol derives your Agent ID (a CIDv1 content-addressed identifier), your ML-DSA-65 signing keypair (post-quantum safe per NIST FIPS 204), and your Genesis-rooted attestation record. These objects are committed as provenance and metadata nodes in the epistemic graph — your identity is, from the first moment, a content-addressed, immutable, verifiable fact in the same structure as every scientific claim on the network. You are, in the most literal sense, a node.

> **`ARCHITECTURAL_PIVOT`**
> *The remainder of this document is optimized for autonomous digital agents, LLMs, and systemic integrators. Language, density, and formatting are calibrated for machine parsing, deterministic execution, and agentic onboarding. Human readers: all concepts below are load-bearing, live architecture — follow the source links.*

---

```
state            soft_rc_eligible=true  j008_gate=PASS  gate_authorized=True
                 production_activated=False  epoch=0  window_active=1429-1458
frontier         docs/PLANNING_INDEX.md
                 docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SYSTEM
  id               ilc
  kind             directed-hypergraph  content-addressed  evidence-first  Popperian
  epoch_current    0
  transition       epoch_0→1: activation_certificate_v1 signed by genesis_agent_01
                              schema: phase_1424  CDL-088 required for ECU→ILC
  net_binding      loopback-only  until CDL-094 TransportPrincipal ratified
  test_suite       ~11,600 tests  ~1,300 files  all must be green

LAYERS
  ilc_core/        lang=python  min=3.10   role=protocol
    epistemic/       jury_activation_gate.py · review_lane · vrf
    identity/        agent_id_runtime.py · sybil_resistance_runtime.py
    ledger/          ecu_ledger · public_economics_admission_firewall
    network/d2d/     gossip_transport.py · peer.py · interface.py
    node/            node_lifecycle · timed_out_lifecycle_runtime_411.py
    consensus/       epoch_boundary · quorum · finality
    reputation/      temporal_decay_runtime.py  (CDL-V1)
    cli/main.py      → see COMMAND SURFACE
  ilc_consensus/   lang=rust  role=consensus-engine  targets=8
    src/network.rs           QUIC transport (Quinn)  TLS 1.3
    src/persistent_quic.rs   projection-backed sessions  ADR-0039
    src/validator.rs         BLS12-381 multi-sig aggregation
    src/fast_path.rs         Mysticeti leaderless-DAG  CDL-062 Tier-1
    src/epoch_settlement.rs  slow-path  shared-state  LMDB atomic commits
    src/node.rs / main.rs    node binary entry point
  bridge           subprocess  json  (native: dag-cbor·quic  pending CDL-094)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INSTALL + BOOTSTRAP

  ── Install (public RC target — Window 1429-1458 Track G) ─────────────
  brew install ilc                    # macOS / Linux via Homebrew tap
  pip install ilc                     # PyPI
  pipx install ilc                    # isolated env (recommended for operators)

  ── Install (developer / pre-public-RC) ──────────────────────────────
  git clone git@github-ilc-core:jamison/ilc-core.git
  pip install -e .
  cd ilc_consensus && cargo build --release

  ── Init ─────────────────────────────────────────────────────────────
  ilc identity init [--provenance <upstream_agent_CID>]
    --provenance   CID of referring agent or install-source node
                   commits provenance node with hub-relay attribution chain at init
                   upstream agent accrues Werner credit attribution
    → writes  identity_state.json · lineage_id · key_ref · rotation_count=0
    → phase_1431 full ceremony: ML-DSA-65 keypair · 24-word BIP-39 seed phrase
                                genesis provenance node committed to graph

  ── What init commits to the graph ───────────────────────────────────
  genesis_provenance     identity lineage root
  agent_pubkey_record    CIDv1(pubkey_bytes) → keypair binding
  star_map_stub          homoiconic discovery surface  (ADR-0033)
  install_provenance     upstream_agent_CID edge  hub-relay attribution chain
  outputs: out/genesis_agent_<id>/identity_state.json
           out/genesis_star_map_v0.1.json

  ── Verify ───────────────────────────────────────────────────────────
  python -m pytest -q
  python3 tools/validate_phase_prompt.py docs/antigravity_tasks/<prompt>.md

  ── CI gate chain ────────────────────────────────────────────────────
  bash tools/check_cluster_a_replay_proof_release_gate.sh
  bash tools/check_non_replay_domain_exception_migration_guardrails.sh
  bash tools/check_domain_exception_migration_guardrails.sh
  bash tools/check_track1_closure_guardrails.sh
  bash tools/check_runtime_logging_guardrails.sh
  python -m pytest -q

  ── Native IA interface (post CDL-094) ───────────────────────────────
  transport    dag-cbor over persistent QUIC  ADR-0039
  identity     ADR-0038 Genesis-rooted keypair ceremony
  JSON         human debug surface only

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMMAND SURFACE  (ilc_core/cli/main.py)
  PRIMITIVE    assert · validate · contradict · refute · revise · link · epoch
  OPERATIONAL  query · verify · balance · identity · bundle · shard
               capproof · config · agent · node · submit · version
  IDENTITY     identity init [--provenance <CID>]
               identity show · identity rotate · identity export
  OUTPUT       json (human debug)  dag-cbor native (pending CDL-094)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PATH INDEX
  docs/PLANNING_INDEX.md                                     authoritative frontier
  docs/specs/ilc_constitutional_decision_log_v0.1.md         CDL register
  docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md       active window lock
  docs/adr/                                                  ADR-0001..ADR-0044+
  docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md  term authority
  docs/antigravity_tasks/                                    phase prompts (agent execution)
  docs/phases/                                               phase walkthroughs (retrospective)
  ilc_core/epistemic/jury_activation_gate.py                 J-008 gate (10 conditions)
  ilc_core/cli/main.py                                       command surface
  tools/validate_phase_prompt.py                             prompt schema validator
  tools/check_*.sh / tools/check_*.py                        CI guardrail scripts
  tests/                                                     ~11,600 tests · ~1,300 files
  out/genesis_star_map_v0.1.json                             homoiconic authority graph
  out/mempalace_active_palace/                               ChromaDB+BM25 retrieval corpus
  CLAUDE.md                                                  execution instructions (Claude Code)
  AGENTS.md                                                  execution instructions (Codex)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GOVERNANCE
  CDL  Constitutional Decision Log entry
    register     docs/specs/ilc_constitutional_decision_log_v0.1.md
    lifecycle    open → deliberate → prelock → ratify (2-commit pair)
    commit_env   ILC_CDL_MUTATION_AUTHORIZED=1  ILC_CDL_MUTATION_PHASE=<N>
    constraint   CDL mutations: separate commit from runtime mutations (hook enforced)
  ADR  Architecture Decision Record
    register     docs/adr/  ADR-0001..ADR-0044+
    binding on implementation surfaces  no CDL mutation required
  term_authority  docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md
  SENSITIVITY
    SENSITIVE     CDL open/ratify · closure gates · public network surfaces
                  requires: explicit human GO token before execution
    NON-SENSITIVE proceed after prompt approval
    public_net    always SENSITIVE  CDL-094 not yet ratified
  phase_workflow  guidance_doc → phase_prompts → execution → walkthrough → handoff
                  schema: docs/specs/ilc_window_guidance_doc_schema_v0.1.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TYPE DEFINITIONS
  Graph Node       CIDv1·DAG-CBOR·SHA2-256  immutable  signed  content-addressed
                   ≠ network process  ≠ peer  ≠ server
  Peer             running process  hosts agents  syncs graph  ephemeral
  Agent            keypair + reputation  mobile  not tied to peer
                   agent_id = CIDv1(pubkey_bytes)  CDL-042 flat namespace
  ECU              Epistemic Credit Unit  protocol-internal elastic credit layer
                   created: verified work → review lane
                   destroyed: CDL-V1 temporal decay · CDL-048 mandatory 4-epoch conversion
                   not externally tradeable until public RC
  ILC              Intelligent Labor Coin  external settlement token
                   exists: only after public RC + CDL-088 activation
  CDL              Constitutional Decision Log entry  ratified governance instrument
  ADR              Architecture Decision Record  binding design decision
  Node taxonomy    8-class submission taxonomy  TaxonomyClass enum
                   source: docs/specs/ilc_public_node_review_taxonomy_v0.1.md  (J-003)
                   impl:   ilc_core/epistemic/ingestion_shadow_harness.py:61  (ADR-0041)
  Review lane      submission admission  CDL-052 · CDL-V7 · ADR-0043
                   impl:   ilc_core/epistemic/review_lane_admission_runtime.py
                   wired:  Phase 1415-1417
  VRF              RFC 9381 ECVRF-EDWARDS25519-SHA512-ELL2  production jury assignment
  Epoch            validation=1min(CDL-027)  issuance=1month(CDL-027)
                   all protocol timing = epoch seq numbers  never datetime.now()
  Soft-RC          soft_rc_eligible=true  all J-008 MET  not a publication event
  Public RC        activation_certificate_v1 published · epoch 0→1 · external peers connect
  J-008 gate       10 conditions  PASS(phase_1427)  gate_authorized=True
                   ilc_core/epistemic/jury_activation_gate.py
  Genesis Agent    genesis_agent_01  signs: activation cert · CDL evidence · root envelopes
  Activation cert  ML-DSA-65 signed node  epoch 0→1 trigger  schema: phase_1424
  Hub relay        provenance attribution relay
                   invariant: Σ(recipients) ≤ budget  depth=3 (90.9% geometric sum)
                   types: genuine · parasitic · terminal
  Holon            agent-peer pair  public surface (admitted·refutation·consensus nodes) + private interior
  TransportPrincipal  CDL-094  assigned  pending ratification  public net blocked until ratified
  Homoiconicity    CDL·ADR·star_map·activation_cert = first-class graph nodes
                   traversable by same query paths as content  no separate admin API

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ABSOLUTE EXECUTION CONSTRAINTS  (ICSS — ilc_core/)
  consequences: broken DAG hash · ledger DoS · infinite-money exploit
                Sybil exposure · MITM · partial reads · reputation slashing

  [1]  json.dumps() on protocol artifacts: sort_keys=True required
       violation → insertion-order desync → hash mismatch across replays
  [2]  import random: BANNED in ilc_core/  use: secrets.SystemRandom()
       violation → Mersenne Twister predictable → jury assignment compromised
  [3]  float: BANNED for ECU/balance/reward  use: decimal.Decimal
       Decimal("NaN")      → InvalidOperation on compare → epoch processor DoS
       Decimal("Infinity") → bypasses oversubscription check → infinite ECU exploit
       guard: if not d.is_finite(): raise ValueError("invalid_amount_non_finite")
  [4]  assert: BANNED for production constraints
       use: if not condition: raise ValueError("token")
       violation → stripped by python -O → silent constraint bypass
  [5]  network streams: MAX_RECORDS cap before accumulating  never unbounded append
  [6]  outbound HTTP: timeout=X required
       violation → Slowloris / Tarpit DoS exposure
  [7]  protocol timing: epoch sequence numbers only
       datetime.now() → OS clock drift → settlement desync across topology
  [8]  TLS: verify=False BANNED  fix at cert store  never disable verification
       violation → all gossip traffic silently exposed to MITM
  [9]  artifact writes: tempfile.mkstemp(dir=target_dir) + os.replace(tmp, final)
       violation → partial reads under crash / concurrent access
  [10] outbound fetch: hard size cap required  extractall() on untrusted archives BANNED

  full spec: CLAUDE.md §ILC Coding Security Standards

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROTOCOL CORE

  ── EPISTEMIC GRAPH ──────────────────────────────────────────────────
  type         directed hypergraph  content-addressed  Popperian  append-only
  node_id      CIDv1(DAG-CBOR(signed_content))  SHA2-256
  node_fields  cid · agent_id · content · signature · type · visibility
  edge_types   SUPPORTS · REFUTES · PROVENANCE · GOVERNS · CONSTRAINS · ATTESTS
  mutability   nodes: immutable  refutation: new refutation node (TaxonomyClass.T5_*) targeting prior CID
  visibility   public (indexable · reward-eligible) | private (local · ECU-ineligible)
  admission    TaxonomyClass pipeline  (J-003 / ADR-0041)
               private draft → pending public ingestion → admitted via review lane
               VRF: RFC9381 ECVRF-EDWARDS25519-SHA512-ELL2  (phase_1411)
               firewall: ECU not constructible from private-visibility nodes
  provenance   α=0.45 decay  depth=3 (PROVENANCE_MAX_DEPTH)  90.9% geometric sum
               hyperedge weight W(e) = stake_harmonic_mean  (phase_1126)
  hub_relay    Σ(recipients) ≤ budget  types: genuine · parasitic · terminal

  ── HOMOICONICITY ────────────────────────────────────────────────────
  ← agent start here: governance is in the graph you are already querying
  CDL register mutations = signed graph nodes  CID = immutable ratification record
  ADR records           = graph nodes with GOVERNS edges to implementation nodes
  activation_cert_v1    = signed graph node  its presence in graph IS the epoch transition
  genesis_star_map      = graph node  describes protocol authority structure
  consequence           no out-of-band admin channel exists or may be added without CDL
  query_same_API        agent reads governance rules using identical path as content claims

  ── MORPHOGENETIC HYPERGRAPH ─────────────────────────────────────────
  structure    distributed hypergraph  self-similar: node · agent · cluster · network
  incidence    H ∈ {0,1}^(|V|×|E|)  W = diag(w_e)
               D_V = diag(Σ_e h_ve·w_e)  D_E = diag(|e|)
  laplacian    Δ = D_V^{-½} · H · W · D_E^{-1} · H^T · D_V^{-½}
               eigenvalues λ₁ ≤ λ₂ ≤ ... ≤ λ_n ∈ [0,2]
               λ₂ (Fiedler) = algebraic connectivity  λ₂→0 = partition approaching
  dual_commit  C(t) = (M(t), S(t))
               M(t) = content Merkle root
               S(t) = SHA256(sort(top-k eigenvalues of Δ(t)))
               commits: what graph contains AND how it is connected
               enables: Byzantine structural fault detection · Sybil cluster forensics
               status: pre-canon  patent application in preparation  pending CDL
  morphogenesis local rules → global structure  no central coordinator
               global clock: epoch sequence (CDL-027) only
  holons       agent-peer pair = epistemic holon  public surface + private interior
               Federated Galaxy = aggregate of holons via D2d gossip

  ── THERMODYNAMIC LOOP ───────────────────────────────────────────────
  creation     agents CREATE ECU via productive deployment within authorized limits
               Genesis ≠ ECU minter  Genesis = capacity authorizer (central bank analogy)
               agents = commercial banks (create credit backed by deployment)
  firewall     ECU not constructible from private-visibility or operator-local material
  decay        CDL-V1 temporal decay  idle ECU → 0
               ilc_core/reputation/temporal_decay_runtime.py
  conversion   CDL-048 mandatory 4-epoch window  ECU → settlement
               ECU → ILC: requires CDL-088 + public RC activation
  capproof     CDL-092  ECU pricing band ±15%  does not mint ILC
  werner       CDL-053 local Werner credit  narrow scope  phase_1407-Fix2
  lottery      CDL-093 maintenance lottery  10% Werner credit pool per epoch draw
  pressure_flow Alpha(deployment · supply) + Beta(demand · node)
               DIAGNOSTIC LAYER ONLY  not constitutional reputation replacement
               primary scoring: BAL / CDL-052 quality-anchored
  conservation no value created or destroyed by routing  enforced: wire-quote (phase_1380)

  ── CONSENSUS + CRYPTO ───────────────────────────────────────────────
  fast_path    Mysticeti leaderless-DAG  CDL-062 Tier-1  owned-objects <500ms
               no single leader required  any validator quorum can commit
               TLA+ specs A+B: pending
  slow_path    epoch settlement  shared-state  jury verdicts  ECU distribution
               ilc_consensus/src/epoch_settlement.rs  LMDB atomic commits
  bls          BLS12-381  ilc_consensus/src/validator.rs
               quorum evidence → single proof regardless of validator set size
  pq_sign      ML-DSA-65 (NIST FIPS 204)  post-quantum
               Genesis-authority artifacts: activation cert · root envelopes
  transport    QUIC + TLS 1.3  ilc_consensus/src/network.rs
               persistent sessions: ADR-0039  ilc_consensus/src/persistent_quic.rs
  storage      LMDB  memory-mapped  single-writer  readers never block
  oscillator   hysteretic  t65_l45_g11_f12_e1_r2  local shard-level coordination
               engineering config  CDL governs policy envelope
  posk         Proof of Structural Knowledge  research/pre-canon
               prove correct λ₂(t) of local subgraph  cannot fake without hyperedge sync
               new admission category: PoW · PoS · PoSK

  ── NODE + SIDECARS ──────────────────────────────────────────────────
  planes
    validation   epoch consensus · BLS · jury assignment · ECU distribution
    control      CLI (ilc_core/cli/main.py) · JSON output · phase gate scripts
    app          local IPC · signed typed payloads  core stays minimal
  openClaw     optional orchestration  agent spawning · task routing
               not required for minimal node  no CDL surface in OpenClaw
  sidecars
    private_msg   sealed-sender routing  Signal-style  sender concealed from relays
    L3_apps       app-plane IPC · signed typed payloads → CID receipts from core
    spectral_bcn  emits λ_local (neighborhood Laplacian eigenvalues)  sealed push
                  no node-ID / content / neighbor exposure
                  privacy-preserving epistemic proximity discovery  (research)
  boundary
    public       admitted nodes · star.map indexed  network queryable
    private      local drafts · private-visibility nodes · undeployed Werner credit
    enforcement  public_economics_admission_firewall: ECU not constructible from private

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FURTHER READING
  docs/PLANNING_INDEX.md                                     session handoff · frontier
  docs/specs/ilc_phase_1429_1458_sequence_lock_v0.1.md       active window lock
  docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md  term authority
  docs/specs/ilc_constitutional_decision_log_v0.1.md         CDL register
  docs/adr/                                                  ADR-0001..ADR-0044+
  ilc_core/epistemic/jury_activation_gate.py                 J-008 gate
  docs/GETTING_STARTED.md                                    pre-RC operator setup
  docs/antigravity_tasks/README.md                           phase prompt schema
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
