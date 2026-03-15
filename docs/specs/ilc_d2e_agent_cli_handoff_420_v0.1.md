# ILC D2e Agent CLI Handoff 420 v0.1

## 1. Implementation scope summary

Phase 420 adds the D2e agent identity CLI surface for `agent derive` and `agent inspect`.
The implementation is limited to `ilc_core/cli/d2e_agent_cli.py` and the required wiring in
`ilc_core/cli/main.py`.

## 2. Dependency/version lock section

- `D2E_AGENT_CLI_VERSION = "d2e_agent_cli_420.v0.1"`
- `CDL_042_DEPENDENCY = "cdl_042_ratified_407.v0.1"`
- The derive path remains locked to the Phase-410 domain-separated runtime via `b"ilc-agent-id-v1:"`.

## 3. agent derive subcommand specification

`agent derive` accepts `--root-key-hex` and decodes canonical root-key bytes from hex.
It calls `ilc_core.identity.agent_id_runtime.derive_agent_id` directly and returns a JSON-ready
payload containing the derived `agent_id`, the `derive` subcommand token, and the CLI version.
Phase-420-native invalid-hex errors use `agent_derive_invalid_hex`; propagated runtime tokens
from `agent_id_runtime` remain unchanged.

## 4. agent inspect subcommand specification

`agent inspect` accepts `--record-json` and loads a serialized agent record from disk.
It returns the sorted record fields, the raw record object, the original record path, and the
CLI version. Missing-file, invalid-JSON, and non-object-root failures are machine-auditable.

## 5. main.py wiring record

- `"agent"` added to `OPERATIONAL_COMMANDS` in `ilc_core/cli/main.py`
- `_build_parser()` now registers `agent derive` and `agent inspect`
- `main()` dispatches `agent` to `run_agent_command`
- `agent` joins the `_ensure_local_graph_state` exempt set because it is a pure identity CLI surface

## 6. Mutation-scope boundary statement

No decision-log mutation occurred in Phase 420.
Only `ilc_core/cli/` changed under `ilc_core/`.
No identity runtime constants or constitutional artifacts were modified.

## 7. Non-goals and carry-forward to Phase 421

Phase 420 does not implement lifecycle or treasury CLI surfaces.
D2e CLI integration Part 2 (Phase 421) is the authorized next implementation slot.
