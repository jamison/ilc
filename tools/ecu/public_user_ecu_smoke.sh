#!/usr/bin/env bash
set -euo pipefail

PHASE="1603"
PACKAGE_VERSION="0.4.31"
GO_PHRASE="GO Phase 1603 ECU-PUBLIC-USER-SMOKE-AUTHORIZED"
HELLO_WORLD_CID="bafyreihqyyhtogvgz6ndvkkkurdhz45n5jv3ovtgo56oqcrpariwx46dji"
HELPER_URL="https://github.com/jamison/ilc/releases/download/v0.4.31/ilc-consensus-linux-x86_64-v0.4.31.tar.gz"
HELPER_SHA256="f493ae06732b5a0e55576aaf86dbeb20ce4a742d3488579e73933a6ac1721036"
STALE_BRIDGE_TOKEN="python_in_memory_ecu_python_rust_balance_bridge_missing_phase_1597"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${ILC_PHASE_1603_REPO_ROOT:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
OUT_DIR="${ILC_PHASE_1603_OUT_DIR:-${REPO_ROOT}/out/phase_1603_public_user_smoke}"
mkdir -p "${OUT_DIR}"

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/ilc_phase_1603_public_user_smoke.XXXXXX")"
cleanup() {
    if [[ "${ILC_PHASE_1603_KEEP_TMP:-0}" != "1" ]]; then
        rm -rf "${TMP_ROOT}"
    fi
}
trap cleanup EXIT

export HOME="${TMP_ROOT}/home"
mkdir -p "${HOME}/.ilc/bin" "${HOME}/.ilc/identity"
unset PYTHONPATH

PYTHON_BIN="${PYTHON_BIN:-/usr/local/bin/python3.12}"
if [[ ! -x "${PYTHON_BIN}" ]]; then
    if command -v python3.12 >/dev/null 2>&1; then
        PYTHON_BIN="$(command -v python3.12)"
    else
        PYTHON_BIN="$(command -v python3)"
    fi
fi

VENV="${TMP_ROOT}/venv"
"${PYTHON_BIN}" -m venv "${VENV}"
PY="${VENV}/bin/python"
ILC="${VENV}/bin/ilc"

# The smoke must not import from the checked-out repository via cwd.
cd "${TMP_ROOT}"

"${PY}" -m pip install --upgrade pip --quiet
"${PY}" -m pip install "ilc-core==${PACKAGE_VERSION}" >"${OUT_DIR}/pip_install.txt" 2>&1

HELPER_TARBALL="${TMP_ROOT}/ilc-consensus-linux-x86_64-v0.4.31.tar.gz"
curl -fsSL "${HELPER_URL}" -o "${HELPER_TARBALL}"
ACTUAL_HELPER_SHA256="$(shasum -a 256 "${HELPER_TARBALL}" | awk '{print $1}')"
if [[ "${ACTUAL_HELPER_SHA256}" != "${HELPER_SHA256}" ]]; then
    echo "helper_tarball_sha256_mismatch" >&2
    echo "expected=${HELPER_SHA256}" >&2
    echo "actual=${ACTUAL_HELPER_SHA256}" >&2
    exit 1
fi
tar -xzf "${HELPER_TARBALL}" -C "${TMP_ROOT}"
if [[ ! -f "${TMP_ROOT}/attribution_batch_ingest" ]]; then
    echo "attribution_batch_ingest_missing_from_helper_tarball" >&2
    exit 1
fi
install -m 0755 "${TMP_ROOT}/attribution_batch_ingest" "${HOME}/.ilc/bin/attribution_batch_ingest"

HELP_DIR="${OUT_DIR}/help"
mkdir -p "${HELP_DIR}"
"${ILC}" --help >"${HELP_DIR}/ilc_help.txt"
"${ILC}" agent --help >"${HELP_DIR}/ilc_agent_help.txt"
"${ILC}" submit --help >"${HELP_DIR}/ilc_submit_help.txt"
"${ILC}" ecu status --help >"${HELP_DIR}/ilc_ecu_status_help.txt"

grep -q "generate" "${HELP_DIR}/ilc_agent_help.txt"
grep -q "source-refs" "${HELP_DIR}/ilc_submit_help.txt"
grep -q "primitive" "${HELP_DIR}/ilc_submit_help.txt"
grep -q "wallet-store" "${HELP_DIR}/ilc_ecu_status_help.txt"
grep -q "endpoint" "${HELP_DIR}/ilc_ecu_status_help.txt"

MODULE_PROOF="$("${PY}" - <<'PY'
import ilc_core
print(ilc_core.__version__)
print(ilc_core.__file__)
PY
)"
INSTALLED_VERSION="$(printf '%s\n' "${MODULE_PROOF}" | sed -n '1p')"
MODULE_PATH="$(printf '%s\n' "${MODULE_PROOF}" | sed -n '2p')"
VENV_REAL="$(cd "${VENV}" && pwd -P)"
MODULE_PATH_REAL="$("${PY}" -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "${MODULE_PATH}")"
case "${MODULE_PATH_REAL}" in
    "${VENV_REAL}"/*) ;;
    *)
        echo "clean_venv_import_path_invalid:${MODULE_PATH}" >&2
        exit 1
        ;;
esac
REPO_ROOT_REAL="$(cd "${REPO_ROOT}" && pwd -P)"
if [[ -d "${REPO_ROOT_REAL}/.git" && "${MODULE_PATH_REAL}" == "${REPO_ROOT_REAL}"* ]]; then
    echo "repo_import_leak_detected:${MODULE_PATH}" >&2
    exit 1
fi
if [[ "${INSTALLED_VERSION}" != "${PACKAGE_VERSION}" ]]; then
    echo "package_version_mismatch:${INSTALLED_VERSION}" >&2
    exit 1
fi

AGENT_RAW="$("${ILC}" agent generate)"
AGENT_ID="$(AGENT_RAW="${AGENT_RAW}" "${PY}" - <<'PY'
import json
import os
import re
import sys

raw = os.environ["AGENT_RAW"].strip()
if re.fullmatch(r"[0-9a-f]{96}", raw):
    print(raw)
    sys.exit(0)
try:
    payload = json.loads(raw)
except json.JSONDecodeError:
    raise SystemExit("agent_generate_output_not_json_or_hex")
for candidate in (
    payload.get("agent_id"),
    payload.get("data", {}).get("agent_id") if isinstance(payload.get("data"), dict) else None,
    payload.get("data", {}).get("_raw") if isinstance(payload.get("data"), dict) else None,
    payload.get("_raw"),
):
    if isinstance(candidate, str) and re.fullmatch(r"[0-9a-f]{96}", candidate):
        print(candidate)
        sys.exit(0)
raise SystemExit("agent_generate_output_missing_agent_id")
PY
)"

PAYLOAD_FILE="${TMP_ROOT}/phase_1603_payload.json"
cat >"${PAYLOAD_FILE}" <<'JSON'
{
  "canonical_external_id": "phase_1603_public_user_smoke_0431",
  "epistemic_type": "objective",
  "parent_node_ids": [],
  "primitive_type": "observation",
  "content": {
    "claim": "Phase 1603 public-user smoke node created from a clean PyPI install."
  }
}
JSON

export ILC_TRUTH_GRAPH_STORE_PATH="${TMP_ROOT}/truth_graph_store"
export ILC_WALLET_STORE_PATH="${TMP_ROOT}/wallet_store"
export ILC_CONSENSUS_LMDB_PATH="${TMP_ROOT}/consensus_balance_store.lmdb"

"${PY}" - <<'PY'
import os
from pathlib import Path

from ilc_core.storage.lmdb_public_runtime import LmdbWalletStore

store = LmdbWalletStore(Path(os.environ["ILC_WALLET_STORE_PATH"]))
store.close()
PY

SUBMIT_STDOUT="${OUT_DIR}/submit_stdout.json"
"${ILC}" submit \
    --primitive assert.truth \
    --payload-file "${PAYLOAD_FILE}" \
    --source-refs "${HELLO_WORLD_CID}" \
    --agent-id "${AGENT_ID}" \
    --epoch 1 \
    >"${SUBMIT_STDOUT}"

STATUS_STDOUT="${OUT_DIR}/ecu_status_stdout.json"
"${ILC}" ecu status \
    --agent-id "${AGENT_ID}" \
    --wallet-store "${ILC_WALLET_STORE_PATH}" \
    >"${STATUS_STDOUT}"

EVIDENCE_FILE="${OUT_DIR}/evidence.json"
AGENT_ID="${AGENT_ID}" \
HELLO_WORLD_CID="${HELLO_WORLD_CID}" \
TMP_ROOT="${TMP_ROOT}" \
HOME_DIR="${HOME}" \
VENV="${VENV}" \
PYTHON_BIN="${PY}" \
MODULE_PATH="${MODULE_PATH}" \
HELPER_URL="${HELPER_URL}" \
HELPER_SHA256="${HELPER_SHA256}" \
ACTUAL_HELPER_SHA256="${ACTUAL_HELPER_SHA256}" \
SUBMIT_STDOUT="${SUBMIT_STDOUT}" \
STATUS_STDOUT="${STATUS_STDOUT}" \
EVIDENCE_FILE="${EVIDENCE_FILE}" \
ILC_TRUTH_GRAPH_STORE_PATH="${ILC_TRUTH_GRAPH_STORE_PATH}" \
ILC_WALLET_STORE_PATH="${ILC_WALLET_STORE_PATH}" \
ILC_CONSENSUS_LMDB_PATH="${ILC_CONSENSUS_LMDB_PATH}" \
"${PY}" - <<'PY'
import json
import os
from pathlib import Path

from ilc_core.encoding.cidv1 import parse_nodeid_strict

STALE = "python_in_memory_ecu_python_rust_balance_bridge_missing_phase_1597"
SUBMIT = Path(os.environ["SUBMIT_STDOUT"])
STATUS = Path(os.environ["STATUS_STDOUT"])
EVIDENCE = Path(os.environ["EVIDENCE_FILE"])

submit_payload = json.loads(SUBMIT.read_text(encoding="utf-8"))
submit_data = submit_payload.get("data", submit_payload)
if submit_payload.get("ok") is not True:
    raise SystemExit("submit_response_not_ok")
node_id = submit_data.get("node_id")
if not isinstance(node_id, str) or not node_id:
    raise SystemExit("phase_1603_local_graph_persistence_missing_node_id")
node_id_parse = parse_nodeid_strict(node_id)
node_id_parse.pop("digest_bytes", None)
if submit_data.get("graph_persistence") != "persisted":
    raise SystemExit("phase_1603_local_graph_persistence_not_persisted")
gossip_delivery = submit_data.get("gossip_delivery")
if not isinstance(gossip_delivery, str) or not gossip_delivery.startswith("deferred"):
    raise SystemExit("phase_1603_unexpected_gossip_delivery")
if submit_data.get("node_primitive_type") != "observation":
    raise SystemExit("phase_1603_node_primitive_type_unexpected")

status_payload = json.loads(STATUS.read_text(encoding="utf-8"))
status_data = status_payload.get("data", status_payload)
if status_payload.get("ok") is not True:
    raise SystemExit("ecu_status_response_not_ok")
if status_data.get("agent_id") != os.environ["AGENT_ID"]:
    raise SystemExit("ecu_status_agent_id_mismatch")
if status_data.get("balance_ecu_source") == STALE:
    raise SystemExit("phase_1603_rust_bridge_not_wired_in_package")
if status_data.get("balance_ecu_source") != "rust_balance_store_committed_aggregate":
    raise SystemExit("phase_1603_rust_balance_source_unexpected")
if status_data.get("status") != "local_rust_balance_store_committed_aggregate":
    raise SystemExit("phase_1603_rust_status_unexpected")
if status_data.get("pending_attribution_quote") != "0":
    raise SystemExit("phase_1603_pending_quote_unexpected")
if status_data.get("committed_ecu_balance") != "0":
    raise SystemExit("phase_1603_committed_balance_unexpected")

evidence = {
    "schema_version": "phase_1603_public_user_smoke.v0.2",
    "phase": "1603",
    "go_phrase": "GO Phase 1603 ECU-PUBLIC-USER-SMOKE-AUTHORIZED",
    "result": "pass",
    "package": {
        "name": "ilc-core",
        "version": "0.4.31",
        "module_path": os.environ["MODULE_PATH"],
        "python_executable": os.environ["PYTHON_BIN"],
        "clean_venv": os.environ["VENV"],
        "repo_import_leak_checked": True,
    },
    "helper_binary": {
        "source_url": os.environ["HELPER_URL"],
        "expected_tarball_sha256": os.environ["HELPER_SHA256"],
        "actual_tarball_sha256": os.environ["ACTUAL_HELPER_SHA256"],
        "installed_path": str(Path(os.environ["HOME_DIR"]) / ".ilc/bin/attribution_batch_ingest"),
    },
    "local_paths": {
        "home": os.environ["HOME_DIR"],
        "truth_graph_store": os.environ["ILC_TRUTH_GRAPH_STORE_PATH"],
        "wallet_store": os.environ["ILC_WALLET_STORE_PATH"],
        "consensus_lmdb": os.environ["ILC_CONSENSUS_LMDB_PATH"],
    },
    "agent_id": os.environ["AGENT_ID"],
    "hello_world_cid": os.environ["HELLO_WORLD_CID"],
    "submit": {
        "ok": True,
        "node_id": node_id,
        "node_id_parse": node_id_parse,
        "graph_persistence": submit_data.get("graph_persistence"),
        "gossip_delivery": gossip_delivery,
        "primitive": submit_data.get("primitive"),
        "node_primitive_type": submit_data.get("node_primitive_type"),
        "source_refs": [os.environ["HELLO_WORLD_CID"]],
        "raw_stdout_path": str(SUBMIT),
    },
    "ecu_status": {
        "ok": True,
        "pending_attribution_quote": status_data.get("pending_attribution_quote"),
        "committed_ecu_balance": status_data.get("committed_ecu_balance"),
        "balance_ecu_source": status_data.get("balance_ecu_source"),
        "status": status_data.get("status"),
        "non_claim": status_data.get("non_claim"),
        "raw_stdout_path": str(STATUS),
    },
    "output_tokens": [
        "ecu_public_user_smoke_complete_phase_1603",
        "ecu_quote_visibility_confirmed_phase_1603",
    ],
    "non_claims": [
        "ecu_committed_balance_zero_until_observe_00",
        "no_live_validator_acceptance_claim",
        "no_native_network_ingress_claim",
        "gossip_delivery_deferred_is_expected_for_phase_1603",
        "no_ecu_minting",
        "no_ilc_minting",
        "no_monthly_close_claim",
        "no_mainnet_claim",
    ],
}
EVIDENCE.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({
    "result": "pass",
    "node_id": node_id,
    "balance_ecu_source": status_data.get("balance_ecu_source"),
    "pending_attribution_quote": status_data.get("pending_attribution_quote"),
    "committed_ecu_balance": status_data.get("committed_ecu_balance"),
    "evidence": str(EVIDENCE),
}, sort_keys=True))
PY
