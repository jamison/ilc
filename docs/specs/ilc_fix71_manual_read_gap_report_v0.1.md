# ILC Fix71 Manual Read Gap Report

## Status

Support-only planning report.

## Source

This report summarizes all non-empty `fix71_public_rc_gap_note` rows found in
the unified Genesis Atlas LMDB after the Fix71 direct-read classification pass.
The full machine-readable ledger is:

- `docs/specs/ilc_fix71_manual_read_gap_ledger_v0.1.json`

The ledger contains every raw row, including duplicate `repo:file` and
`repo:file_ref` records where both were manually classified. This report groups
the findings for planning.

## Scope Counts

| Metric | Count |
| --- | ---: |
| Gap-note rows | 899 |
| Unique source paths | 587 |
| Categories | 11 |
| Rows requiring pre-public-RC fix or decision | 13 |
| Rows requiring pre-public-RC cleanup or policy confirmation | 5 |
| Rows that are boundary reminders to preserve | 452 |
| Rows that are watch items | 250 |

## Category Counts

| Category | Count | Planning meaning |
| --- | ---: | --- |
| `economic_runtime_activation_boundary` | 258 | Mostly correct default-off/non-activation boundaries. Preserve unless an explicit activation phase opens. |
| `public_rc_boundary_or_exclude` | 158 | Public path, public P2P, public source export, or public RC gates remain blocked or scoped. |
| `determinism_numeric_or_serialization_hardening` | 149 | Numeric, timestamp, randomness, canonical JSON, or reproducibility watch items. |
| `other_manual_review_note` | 135 | Mixed manual findings that need human triage before deciding whether they are work items. |
| `package_content_identity_or_build_gap` | 66 | Package, dependency, content-addressing, or source identity issues. |
| `cryptography_signature_or_keying_gap` | 48 | Signing, key custody, schema-vs-signature, or crypto-boundary notes. |
| `network_transport_or_sidecar_boundary` | 36 | Transport, sidecar, admission, replay, relay, or public networking boundaries. |
| `lmdb_graph_write_or_store_boundary` | 20 | Atlas LMDB, truth-store LMDB, safe-writer, or raw-adapter boundary notes. |
| `authority_lifecycle_or_alias_cleanup` | 14 | Proposed/open/lifecycle/alias records that should stay non-authority or resolve through canonical nodes. |
| `support_simulation_or_diagnostic_only` | 13 | SIM, rehearsal, observability, or analytics support material. |
| `task_queue_durability_future_work` | 2 | Durable/distributed task routing remains future work. |

## Priority Model

### P0: Immediate Graph Integrity

No P0 graph integrity defect was found in this pass.

- Dangling edges: `0`.
- Missing edge IDs: `0`.
- Remaining unread `ilc_core/` repo-file nodes: `0`.
- Orphaned `phase:*` nodes: `0`.
- Public-path `CLASSIFIED_BY` fan-in remains `1`.

### P1: Pre-Public-RC Fix Or Decision

These are the highest-value concrete fixes before public RC documentation or
public protocol surfaces rely on these paths.

| Area | Files | Required action |
| --- | --- | --- |
| Demo numeric payloads | `ilc_core/cli/ep_task_cli.py` | Replace float literals in demo payloads with string or Decimal-compatible examples before using this path in public docs. |
| Hardware-potential input contract | `ilc_core/consensus/governance.py` | Decide whether public/network inputs are exact strings or another canonical numeric form; avoid public reliance on `List[float]`. |
| Canonical JSON non-finite rejection | `ilc_core/network/wire_transport_runtime.py`, `ilc_core/protocol/ilc_cluster_a_acceptance_evidence.py` | Add or confirm `allow_nan=False` before treating outputs as canonical public preimages. |
| Wire timestamp semantics | `ilc_core/protocol/schemas/ilc_protocol_wire_format_v0.1.json` | Reconcile timestamp field with newer no-wall-clock commitments for public protocol use. |
| Privacy metric floats | `ilc_core/privacy/metrics.py` | Keep as monitoring output only, or document why float telemetry cannot enter economic/settlement state. |
| Package dependency closure | `ilc_core/crypto/__init__.py` | Ensure public package metadata includes the required `cbor2` and `cryptography` versions/profile. |
| Schema packaging | `ilc_core/genesis/schema.py` | Move root-path schema loading into package data or graph-addressed content before relying on packaged public builds. |

### P1b: Pre-Public-RC Cleanup Or Policy Confirmation

These are small but important cleanup items because stale text and CLI naming
can mislead operators or future agents.

| Area | Files | Required action |
| --- | --- | --- |
| Stale ADR status prose | ADR-0036, ADR-0037 | Direct-read cleanup: remove stale internal "Proposed" wording where accepted header/LMDB authority is already established. |
| CLI contract wording | `ilc_core/cli/atlas_lmdb_cli.py` | Docstring says read-only while guarded write commands exist. Rename or clarify as read-first guarded-write. |
| Historical raw adapter use | `tools/evaluators/sim_genesis_base_graph_lmdb_rematerialization_1545p_fix41.py` | Leave historical evaluator intact, but document that future routine writes must continue through `AtlasLmdbSafeWriter`. |
| ADR index staleness | `docs/adr/README.md` | Regenerate or correct stale ADR status index before public documentation freeze. |
| Config docstring mismatch | `ilc_core/config.py` | Update `governance_mvp.yaml` wording to match the actual `governance_mvp.json` default. |

### P2: Numeric, Determinism, And Serialization Sweep

This is the largest technically meaningful watch bucket. It includes exact
numeric hardening, randomness separation, timestamp reproducibility, and
canonical JSON behavior. Representative findings:

- `ilc_core/types.py`: `WeightParams` contains provisional float-like fields.
- `ilc_core/genesis/work_task.py`: `difficulty_factor` is `Optional[float]`.
- `ilc_core/analysis/node_value_input_canon.py`: reward/stake/age fields accept
  int/float before normalization.
- `ilc_core/consensus/engine.py`: contains float formulas for age/tax/bounty
  and accepts `agent_potentials` as floats.
- `ilc_core/sim/*`: several SIM/devnet paths correctly use floats/randomness
  but must remain simulation-only.
- Export and report paths that write current timestamps need explicit timestamp
  overrides for reproducible/signing contexts.

Recommended treatment: one targeted hardening phase that does not try to remove
all floats everywhere. It should classify each float/timestamp/randomness use as
one of: protocol-forbidden, simulation-only, telemetry-only, or exact-numeric
runtime.

### P3: Package, Content Identity, And Build Reconstruction

These findings tie directly to homoiconic build from graph/network state.

- Schema/resource loading must not depend on fragile repository-root paths.
- Public package metadata must carry dependency versions required by public
  protocol profiles.
- File identity and `file_ref` resolution remain load-bearing for package
  reconstruction.
- Unsigned pre-RC manifests must not be mistaken for signed Genesis package
  roots.

Recommended treatment: continue the Fix64/Fix65 package lineage by adding a
build-critical file audit that verifies content hash, source path, package
membership, dependency membership, and verifier/test relation for all public
protocol files.

### P4: Cryptography And Keying Boundaries

The code shape is mostly conservative: many modules correctly require caller
provided keyring, operator key, or external signing authority. The main gap is
documentation and enforcement at public surfaces.

Representative findings:

- `ilc_core/crypto/cose_sign1.py`: key custody and signing authority are caller
  supplied.
- `ilc_core/genesis/assertion_schema.py`: validates shape but delegates ML-DSA
  signature verification.
- `ilc_core/protocol/ilc_governance_record_validate.py`: schema validation is
  not cryptographic verification.
- Several schemas contain examples/HMAC compatibility records and must not be
  treated as final authority.

Recommended treatment: a crypto-boundary audit that names which modules perform
schema validation, which verify signatures, and which require external signing
ceremony inputs.

### P5: Economic And Public Activation Boundaries

Most rows in this bucket are not bugs. They are reminders that default-off
guards are working and must remain explicit until a future GO/activation phase.

Examples:

- Production emission remains off.
- Treasury/validator rewards remain off.
- Ejected-stake distribution remains off.
- Productive ECU expansion and bounty payout remain off.
- Public P2P, public serving, public source export, and public RC remain gated.

Recommended treatment: preserve these notes as release-gate assertions. Do not
convert them into implementation work unless the relevant activation phase is
explicitly opened.

### P6: Network, Sidecar, And Admission Boundaries

These rows mostly confirm that local/private sidecar and transport surfaces are
not public relay or public P2P activation.

Recommended treatment: keep the public docs precise. A local sidecar helper,
private message delivery loop, or known-peer receipt is not a public transport
network unless the relevant public networking gate opens.

### P7: Authority Lifecycle And Alias Cleanup

These rows confirm that proposed/open/lifecycle/alias nodes should not become
independent authority nodes. They should resolve through canonical ADR/CDL nodes
using `SAME_AUTHORITY`, `OPENED_FOR`, `PRELOCK_FOR`,
`RATIFICATION_EVIDENCE_FOR`, `PROPOSES_CHANGE_TO`, or `RESOLVED_BY`.

Recommended treatment: keep these records as support/lifecycle evidence unless
a direct read shows that a canonical accepted authority node is missing.

### P8: Durable Task Routing

`ilc_core/work/task_queue.py` is intentionally in-memory. This is not a public
RC blocker for the current local/sandbox scope, but it is real future product
work if network-level jobs become public protocol behavior.

## Recommended Execution Order

1. P1 quick cleanup phase: fix demo floats, stale ADR prose, CLI/docstring
   mismatches, dependency packaging notes, and canonical JSON `allow_nan=False`
   where outputs may become public preimages.
2. P2 numeric/determinism phase: classify all float/timestamp/randomness rows
   into protocol-forbidden, exact-runtime, simulation-only, or telemetry-only.
3. P3 package/build phase: ensure build-critical files have content hash,
   source path, package membership, dependency membership, and verifier/test
   relation.
4. P4 crypto-boundary phase: document and test schema-vs-signature-vs-key
   custody boundaries.
5. P5/P6 boundary audit: preserve default-off and private/local boundaries as
   release-gate assertions rather than treating them as implementation defects.
6. P7 lifecycle cleanup: only promote or rewire lifecycle/alias nodes where a
   direct read shows a missing canonical authority record.

## Non-Claims

- This report does not sign Genesis material.
- This report does not activate public RC, mainnet, public P2P, production
  minting, or economic settlement.
- This report does not mutate runtime code.
- The JSON ledger is a planning artifact, not canonical public authority.
