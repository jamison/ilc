# ILC D2e Lifecycle CLI Handoff 421 v0.1

## 1. Implementation scope summary

Phase 421 adds the D2e timed-out lifecycle CLI surface under a top-level `node` command.
The implementation is limited to `ilc_core/cli/d2e_lifecycle_cli.py` and the required
wiring in `ilc_core/cli/main.py`.

## 2. Dependency/version lock section

- `D2E_LIFECYCLE_CLI_VERSION = "d2e_lifecycle_cli_421.v0.1"`
- `CDL_046_DEPENDENCY = "cdl_046_ratified_409.v0.1"`
- `D2D_GOSSIP_DEPENDENCY = "d2d_gossip_382.v0.1"`
- `ORPHAN_TIMEOUT_EPOCHS = 4`
- `RECOVERY_POLICY = "stake_full_release"`

## 3. node constants subcommand specification

`node constants` returns the ratified timed-out lifecycle constants, the Phase-411 runtime
version, and the Phase-421 CLI version without mutating graph state.

## 4. node timed-out inspect subcommand specification

`node timed-out-inspect` accepts a serialized record JSON plus `current_epoch`, validates
`claim_id` and `orphaned_since_epoch`, evaluates the timed-out boundary, and returns the
applicable lifecycle path together with the locked timeout and recovery constants.

## 5. node timed-out d2d subcommand specification

`node timed-out-d2d` accepts the same record JSON plus D2d channel and sender inputs,
requires `payload_cid`, rejects pre-boundary claims, and builds the D2d dissemination
envelope for a timed-out claim through the existing gossip runtime.

## 6. main.py wiring record

- `"node"` added to OPERATIONAL_COMMANDS in `ilc_core/cli/main.py`
- `_build_parser()` now registers `node constants`, `node timed-out-inspect`, and `node timed-out-d2d`
- `main()` dispatches `node` to `run_node_command`
- `node` joins the `_ensure_local_graph_state` exempt set because Phase-421 node commands are driven by explicit record inputs and do not perform graph observation

## 7. Mutation-scope boundary statement

No decision-log mutation occurred in Phase 421.
Only `ilc_core/cli/` changed under `ilc_core/`.
No node runtime, D2d runtime, or identity runtime file changed.

## 8. Non-goals and carry-forward to Phase 422

Phase 421 does not implement economic governance CLI surfaces or monitoring CLI extensions.
Phase 422 coherence and capsule v1.6 is the authorized next implementation slot.
