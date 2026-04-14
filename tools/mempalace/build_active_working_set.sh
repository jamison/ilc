#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MANIFEST_PATH="${ILC_MEMPALACE_ACTIVE_MANIFEST:-$ROOT_DIR/docs/tools/mempalace/ilc_mempalace_current_frontier_manifest_v0.1.json}"
RUNTIME_PATH="${ILC_MEMPALACE_ACTIVE_RUNTIME:-$ROOT_DIR/out/mempalace_runtime_active}"
STAGED_ROOT="${ILC_MEMPALACE_ACTIVE_STAGE:-$ROOT_DIR/out/mempalace_active_stage}"
PALACE_PATH="${ILC_MEMPALACE_ACTIVE_PALACE:-$ROOT_DIR/out/mempalace_active_palace}"
TMPDIR_PATH="${ILC_MEMPALACE_TMPDIR:-$ROOT_DIR/out/mempalace_tmp}"

mkdir -p "$TMPDIR_PATH"
export TMPDIR="$TMPDIR_PATH"

bash "$ROOT_DIR/tools/mempalace/install_local_mempalace_env.sh" --venv "$RUNTIME_PATH"

PATH="$RUNTIME_PATH/bin:$PATH" python3 "$ROOT_DIR/tools/mempalace/build_tiered_corpus.py" \
  --manifest "$MANIFEST_PATH" \
  --staged-root "$STAGED_ROOT" \
  --palace "$PALACE_PATH" \
  --mode copy \
  --clean \
  "$@"

echo "Active MemPalace working set ready."
echo "  manifest: $MANIFEST_PATH"
echo "  runtime: $RUNTIME_PATH"
echo "  staged_root: $STAGED_ROOT"
echo "  palace: $PALACE_PATH"
echo "  tmpdir: $TMPDIR_PATH"
