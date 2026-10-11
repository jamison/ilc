#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-only
set -euo pipefail

OUT_DIR="${ILC_MODEL_ROUTER_SMOKE_OUT_DIR:-out/phase_1614_model_router_cli_smoke}"
STORE_PATH="${ILC_MODEL_ROUTER_STORE_PATH:-${OUT_DIR}/router_receipts.lmdb}"
GRAPH_STORE_PATH="${ILC_MODEL_ROUTER_GRAPH_STORE_PATH:-${OUT_DIR}/truth_graph.lmdb}"
PROMOTION_DIR="${ILC_MODEL_ROUTER_PROMOTION_DIR:-${OUT_DIR}/promotions}"
mkdir -p "${OUT_DIR}" "${PROMOTION_DIR}"

ILC_CMD=(python -m ilc_core.cli.main)

echo "=== Phase 1614 Model Router CLI Smoke ==="

ROUTE_OUT="$("${ILC_CMD[@]}" sidecar model-router route \
  --model claude-haiku-4-5 \
  --provider anthropic \
  --message '{"role":"user","content":"ping"}' \
  --store-path "${STORE_PATH}" \
  --graph-store-path "${GRAPH_STORE_PATH}" \
  --no-promote \
  --dry-run)"
printf '%s\n' "${ROUTE_OUT}" > "${OUT_DIR}/route_output.json"
echo "route output: ${ROUTE_OUT}"

RECEIPT_TOKEN="$(python3 - <<'PY' "${OUT_DIR}/route_output.json"
import json
import re
import sys

payload = json.loads(open(sys.argv[1], encoding="utf-8").read())
token = payload["receipt_token"]
if not re.fullmatch(r"[0-9a-f]{64}", token):
    raise SystemExit("receipt_token_invalid")
print(token)
PY
)"

LIST_OUT="$("${ILC_CMD[@]}" sidecar model-router list-receipts --store-path "${STORE_PATH}")"
printf '%s\n' "${LIST_OUT}" > "${OUT_DIR}/list_receipts_output.json"
echo "list-receipts output: ${LIST_OUT}"

PROMOTE_OUT="$("${ILC_CMD[@]}" sidecar model-router promote-receipt "${RECEIPT_TOKEN}" \
  --store-path "${STORE_PATH}" \
  --graph-store-path "${GRAPH_STORE_PATH}" \
  --out-dir "${PROMOTION_DIR}")"
printf '%s\n' "${PROMOTE_OUT}" > "${OUT_DIR}/promote_output.json"
echo "promote-receipt output: ${PROMOTE_OUT}"
echo "${PROMOTE_OUT}" | grep '"promotion_status": "promoted"' >/dev/null
echo "${PROMOTE_OUT}" | grep '"node_id": "b' >/dev/null

python3 - <<'PY' "${OUT_DIR}" "${RECEIPT_TOKEN}" "${STORE_PATH}" "${PROMOTION_DIR}"
import json
import os
import sys
import tempfile
from pathlib import Path

out_dir = Path(sys.argv[1])
receipt_token = sys.argv[2]
store_path = sys.argv[3]
promotion_dir = sys.argv[4]
route = json.loads((out_dir / "route_output.json").read_text(encoding="utf-8"))
listed = json.loads((out_dir / "list_receipts_output.json").read_text(encoding="utf-8"))
promoted = json.loads((out_dir / "promote_output.json").read_text(encoding="utf-8"))

evidence = {
    "list_receipts_count": len(listed["receipts"]),
    "model_router_cli_smoke_pass_phase_1614": True,
    "non_claims": [
        "no_live_provider_api_call",
        "no_raw_prompt_or_completion_publication",
        "no_genesis_atlas_lmdb_write",
        "no_ecu_or_ilc_settlement",
    ],
    "output_token": "model_router_cli_smoke_pass_phase_1614",
    "promotion_dir": promotion_dir,
    "promote_status": promoted["promotion_status"],
    "receipt_token": receipt_token,
    "route_status": route["status"],
    "schema_version": "model_router_cli_smoke_phase_1614.v0.1",
    "store_path": store_path,
}

target = out_dir / "smoke_evidence.json"
fd, tmp_name = tempfile.mkstemp(dir=str(out_dir), prefix=".smoke_evidence.", suffix=".tmp")
try:
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(evidence, handle, allow_nan=False, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp_name, target)
finally:
    if os.path.exists(tmp_name):
        os.unlink(tmp_name)
PY

echo "model_router_cli_smoke_pass_phase_1614"
