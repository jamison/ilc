#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MANIFEST_PATH="${ILC_MEMPALACE_FULL_MANIFEST:-$ROOT_DIR/docs/tools/mempalace/ilc_mempalace_full_corpus_manifest_v0.1.json}"
RUNTIME_PATH="${ILC_MEMPALACE_FULL_RUNTIME:-$ROOT_DIR/out/mempalace_runtime_active}"
STAGED_ROOT="${ILC_MEMPALACE_FULL_STAGE:-$ROOT_DIR/out/mempalace_full_corpus_stage}"
PALACE_PATH="${ILC_MEMPALACE_FULL_PALACE:-$ROOT_DIR/out/mempalace_full_corpus_palace}"
TMPDIR_PATH="${ILC_MEMPALACE_TMPDIR:-$ROOT_DIR/out/mempalace_tmp}"
LOG_PATH="${ILC_MEMPALACE_FULL_LOG:-$ROOT_DIR/out/mempalace_full_corpus_build.log}"

mkdir -p "$TMPDIR_PATH"
export TMPDIR="$TMPDIR_PATH"

START_TIME="$(date '+%Y-%m-%d %H:%M:%S')"
echo "Full corpus MemPalace build started: $START_TIME" | tee "$LOG_PATH"
echo "  manifest: $MANIFEST_PATH" | tee -a "$LOG_PATH"
echo "  staged_root: $STAGED_ROOT" | tee -a "$LOG_PATH"
echo "  palace: $PALACE_PATH" | tee -a "$LOG_PATH"
echo "" | tee -a "$LOG_PATH"

# Ensure venv (reuse active runtime if already installed)
bash "$ROOT_DIR/tools/mempalace/install_local_mempalace_env.sh" --venv "$RUNTIME_PATH" 2>&1 | tee -a "$LOG_PATH"

echo "" | tee -a "$LOG_PATH"
echo "Staging and mining corpus..." | tee -a "$LOG_PATH"

PATH="$RUNTIME_PATH/bin:$PATH" python3 "$ROOT_DIR/tools/mempalace/build_tiered_corpus.py" \
  --manifest "$MANIFEST_PATH" \
  --staged-root "$STAGED_ROOT" \
  --palace "$PALACE_PATH" \
  --mode copy \
  --clean \
  "$@" 2>&1 | tee -a "$LOG_PATH"

END_TIME="$(date '+%Y-%m-%d %H:%M:%S')"
echo "" | tee -a "$LOG_PATH"
echo "Full corpus MemPalace build complete." | tee -a "$LOG_PATH"
echo "  started:  $START_TIME" | tee -a "$LOG_PATH"
echo "  finished: $END_TIME" | tee -a "$LOG_PATH"
echo "  manifest: $MANIFEST_PATH" | tee -a "$LOG_PATH"
echo "  palace:   $PALACE_PATH" | tee -a "$LOG_PATH"
echo "  log:      $LOG_PATH" | tee -a "$LOG_PATH"
echo "" | tee -a "$LOG_PATH"

# Report palace size
if [ -d "$PALACE_PATH" ]; then
  du -sh "$PALACE_PATH" | tee -a "$LOG_PATH"
fi
