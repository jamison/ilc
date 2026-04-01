#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEFAULT_CONFIG_DIR="$REPO_ROOT/tests/fixtures/phase_572_three_machine_smoke"
MODE=""
CONFIG_DIR="$DEFAULT_CONFIG_DIR"
FORCE_TRANSPORT_FAILURE=0

usage() {
  cat <<'EOF'
Usage: tools/run_three_machine_smoke_phase_572.sh [--local-smoke | --operator-guide] [--config-dir DIR] [--force-transport-failure]
EOF
}

print_marker() {
  printf '%s\n' "$1"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --local-smoke)
      MODE="local"
      shift
      ;;
    --operator-guide)
      MODE="operator"
      shift
      ;;
    --config-dir)
      CONFIG_DIR="$2"
      shift 2
      ;;
    --force-transport-failure)
      FORCE_TRANSPORT_FAILURE=1
      shift
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$MODE" ]]; then
  usage
  exit 1
fi

required_files=(
  "$CONFIG_DIR/node1_config.json"
  "$CONFIG_DIR/node2_config.json"
  "$CONFIG_DIR/node3_config.json"
  "$CONFIG_DIR/genesis_ref.json"
  "$CONFIG_DIR/genesis_bundle.json"
  "$CONFIG_DIR/cert.pem"
  "$CONFIG_DIR/key.pem"
)

for required in "${required_files[@]}"; do
  if [[ ! -f "$required" ]]; then
    print_marker "smoke_config_failure"
    exit 1
  fi
done

if [[ "$MODE" == "operator" ]]; then
  cat <<EOF
Operator-guided three-machine mode
Machine 1:
  python3 tools/run_ilc_node_service_v1.py start --config $CONFIG_DIR/node1_config.json --genesis-ref $CONFIG_DIR/genesis_ref.json --stay-alive-seconds 30
Machine 2:
  python3 tools/run_ilc_node_service_v1.py start --config $CONFIG_DIR/node2_config.json --genesis-ref $CONFIG_DIR/genesis_ref.json --stay-alive-seconds 30
Machine 3:
  python3 tools/run_ilc_node_service_v1.py start --config $CONFIG_DIR/node3_config.json --genesis-ref $CONFIG_DIR/genesis_ref.json --stay-alive-seconds 30
Sender check:
  python3 - <<'PY'
from ilc_core.node.node_startup_runtime import build_node_startup_context
from ilc_core.network.d2d.http_gossip_transport_runtime import HttpGossipTransportRuntime
context = build_node_startup_context('$CONFIG_DIR/node1_config.json', '$CONFIG_DIR/genesis_ref.json')
runtime = HttpGossipTransportRuntime(context.transport_config)
print(runtime.send_gossip('https://127.0.0.1:19572', 'centrality_delta', 'cid:1234567890abcdef', 572, 'sig-572'))
PY
Expected markers:
  smoke_node_1_ready
  smoke_node_2_ready
  smoke_node_3_ready
  smoke_gossip_send_ok
  smoke_gossip_receive_ok
  smoke_explicit_http_fallback_ok
  smoke_genesis_import_ok
  smoke_restart_ok
EOF
  exit 0
fi

TMP_DIR="$(mktemp -d)"
pids=()
logs=()
cleanup() {
  for pid in "${pids[@]:-}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
    fi
  done
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

start_node() {
  local node_name="$1"
  local stay_seconds="$2"
  local log_file="$TMP_DIR/${node_name}.log"
  python3 "$REPO_ROOT/tools/run_ilc_node_service_v1.py" start \
    --config "$CONFIG_DIR/${node_name}_config.json" \
    --genesis-ref "$CONFIG_DIR/genesis_ref.json" \
    --stay-alive-seconds "$stay_seconds" \
    >"$log_file" 2>&1 &
  pids+=("$!")
  logs+=("$log_file")
}

start_node node1 6
start_node node2 6
start_node node3 1
sleep 1.5

for idx in 1 2 3; do
  log_file="$TMP_DIR/node${idx}.log"
  if ! grep -q 'node_service_ready' "$log_file"; then
    cat "$log_file"
    print_marker "smoke_lifecycle_failure"
    exit 1
  fi
  print_marker "smoke_node_${idx}_ready"
done
print_marker "smoke_genesis_import_ok"

if [[ "$FORCE_TRANSPORT_FAILURE" -eq 1 ]]; then
  if python3 - <<PY
from ilc_core.network.d2d.http_gossip_transport_runtime import HttpGossipTransportRuntime, TransportRuntimeConfig
config = TransportRuntimeConfig(
    transport_kind='quic',
    bind_host='127.0.0.1',
    bind_port=0,
    tls_cert_path='$CONFIG_DIR/cert.pem',
    tls_key_path='$CONFIG_DIR/key.pem',
)
runtime = HttpGossipTransportRuntime(config)
runtime.send_gossip('https://127.0.0.1:19572', 'centrality_delta', 'cid:1234567890abcdef', 572, 'sig-572')
PY
  then
    print_marker "smoke_lifecycle_failure"
    exit 1
  fi
  print_marker "smoke_transport_failure"
  exit 1
fi

if ! status="$(python3 - <<PY
from ilc_core.node.node_startup_runtime import build_node_startup_context
from ilc_core.network.d2d.http_gossip_transport_runtime import HttpGossipTransportRuntime
context = build_node_startup_context('$CONFIG_DIR/node1_config.json', '$CONFIG_DIR/genesis_ref.json')
runtime = HttpGossipTransportRuntime(context.transport_config)
print(runtime.send_gossip('https://127.0.0.1:19572', 'centrality_delta', 'cid:1234567890abcdef', 572, 'sig-572'))
PY
)"
then
  print_marker "smoke_transport_failure"
  exit 1
fi
if [[ "$status" != "202" ]]; then
  print_marker "smoke_transport_failure"
  exit 1
fi
print_marker "smoke_gossip_send_ok"
print_marker "smoke_gossip_receive_ok"
print_marker "smoke_explicit_http_fallback_ok"

wait "${pids[2]}" 2>/dev/null || true
if ! python3 "$REPO_ROOT/tools/run_ilc_node_service_v1.py" start \
  --config "$CONFIG_DIR/node3_config.json" \
  --genesis-ref "$CONFIG_DIR/genesis_ref.json" \
  --stay-alive-seconds 0.5 \
  >"$TMP_DIR/node3-restart.log" 2>&1
then
  cat "$TMP_DIR/node3-restart.log"
  print_marker "smoke_lifecycle_failure"
  exit 1
fi
if ! grep -q 'node_service_ready' "$TMP_DIR/node3-restart.log"; then
  cat "$TMP_DIR/node3-restart.log"
  print_marker "smoke_lifecycle_failure"
  exit 1
fi
print_marker "smoke_restart_ok"
