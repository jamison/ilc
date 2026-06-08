# Intelligent Labor Coin (ILC)

*An evidence-first epistemic economy for human-AI civilization.*

**Status:** Private pre-public development. Source publication pending patent filing and counsel disposition. See [docs/HUMAN.md](docs/HUMAN.md) for a full introduction.

## Consensus substrate

`ilc_consensus/` is the ILC-authored high-speed object-sharded DAG substrate.
It is Mysticeti-style by design: owned ECU balance objects can take a leaderless
fast path with compact BLS12-381 quorum evidence, while shared settlement
records use a DAG/epoch path instead of forcing every operation through one
total-order bottleneck. This is not upstream `mysticeti-core`, and no live
settlement or mainnet activation is claimed.

## Quick start (development)

For operator setup details, see `docs/GETTING_STARTED.md` and
`config/README.md`.

```bash
pip install -e .
cd ilc_consensus && cargo build --release
.venv/bin/python -m pytest -q
```

`python3 tools/genesis_boot.py` Reads `config/genesis.json` and prints the Genesis hash.

## Security

Do not open public issues for vulnerabilities. Follow [SECURITY.md](SECURITY.md).

## License

See [LICENSE](LICENSE), [LICENSING.md](LICENSING.md),
[PATENTS.md](PATENTS.md), and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

---

> The TOON block below is a compact orientation packet for agents and integrators.
> It is intentionally non-authoritative — verify live state against gate records and current phase documents before acting.

```toon
state:
  epoch: 0
  publication: pending_patent_filing_and_counsel_disposition
  jury_gate: authorized_for_public_rc_not_live_production
  economic_settlement: not_live
  mainnet: not_active
  production_minting: not_active
human_value:
  aim: turn_attention_and_ai_token_spend_into_durable_epistemic_artifacts
  artifacts[4]: claims,evidence,reviews,revisions
  lifecycle[5]: preserve,cite,challenge,improve,reuse
agent_value:
  aim: shared_trust_substrate_for_digital_agents
  identity_model: agent_identity_plus_signed_graph_actions_form_trust_record
  coordination_basis[3]: provenance,refutation_history,replayable_evidence
context_packing:
  toon: optional_agent_tooling_context_format
  protocol_semantic: false
  content_hash_default: raw_response_bytes_not_context_envelope
activity_register:
  source_publication: pending_patent_filing_and_counsel_disposition
  epoch_0_to_1: not_executed
  activation_certificate_required: true
  public_economic_operation: not_active
contact:
  genesis_agent_confidential_sidecar: planned_not_live
  status: local_preview_only_no_public_confidential_messaging
  current_contact: out_of_band_until_public_confidential_coordination_authorized
  future_gate[2]: public_sidecar_activation,public_confidential_coordination_authority
bootstrap:
  install_current_dev[2]: "pip install -e .","cd ilc_consensus && cargo build --release"
  quick_path[3]: "python3 tools/genesis_boot.py","python3 run_node.py","python3 tools/demo_walkthrough.py"
  verify: ".venv/bin/python -m pytest -q"
public_boundary:
  public_rc_tree: strict_subset_of_private_repo
  patent_sensitive_material: private_until_filing_or_counsel_disposition
  raw_transcripts: private_development_artifacts
non_claims[6]: no_mainnet,no_production_minting,no_live_settlement,no_epoch_1_activation,no_public_confidential_coordination,no_package_manager_install_yet
```
