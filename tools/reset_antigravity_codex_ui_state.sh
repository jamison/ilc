#!/bin/zsh
set -euo pipefail

app_support="${HOME}/Library/Application Support/Antigravity"
backup_root="${HOME}/.antigravity/rollback_backups"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_dir="${backup_root}/${timestamp}-antigravity-codex-ui-reset"
status_file="${HOME}/Documents/ILC_Main/01_Current/out/antigravity_codex_ui_reset_status.txt"

mkdir -p "$(dirname "${status_file}")"

write_status() {
  printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" > "${status_file}"
}

write_status "waiting_for_antigravity_to_close"

for _ in {1..180}; do
  if ! pgrep -f "/Applications/Antigravity.app/Contents/MacOS/Antigravity" >/dev/null 2>&1 \
    && ! pgrep -f "Antigravity Helper" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

if pgrep -f "/Applications/Antigravity.app/Contents/MacOS/Antigravity" >/dev/null 2>&1 \
  || pgrep -f "Antigravity Helper" >/dev/null 2>&1; then
  write_status "aborted_antigravity_still_running"
  echo "Antigravity is still running after waiting 180 seconds." >&2
  exit 1
fi

mkdir -p "${backup_dir}/app_support" "${backup_dir}/user_state"
write_status "backing_up_state_to_${backup_dir}"

copy_if_exists() {
  local src="$1"
  if [ -e "${src}" ]; then
    rsync -a "${src}" "${backup_dir}/app_support/"
  fi
}

copy_if_exists "${app_support}/Local Storage"
copy_if_exists "${app_support}/Session Storage"
copy_if_exists "${app_support}/Service Worker"
copy_if_exists "${app_support}/WebStorage"
copy_if_exists "${app_support}/Cache"
copy_if_exists "${app_support}/Code Cache"
copy_if_exists "${app_support}/GPUCache"
copy_if_exists "${app_support}/blob_storage"
copy_if_exists "${app_support}/User/globalStorage/state.vscdb"
copy_if_exists "${app_support}/User/globalStorage/state.vscdb.backup"
copy_if_exists "${app_support}/User/workspaceStorage"

global_db="${app_support}/User/globalStorage/state.vscdb"
if [ -f "${global_db}" ]; then
  write_status "clearing_global_codex_ui_state"
  sqlite3 "${global_db}" <<'SQL'
DELETE FROM ItemTable
WHERE key IN (
  'openai.chatgpt',
  'chat.ChatSessionStore.index',
  'memento/mainThreadWebviewPanel.origins',
  'memento/webviewViews.origins'
);
VACUUM;
SQL
fi

write_status "clearing_workspace_codex_ui_state"
for db in "${app_support}"/User/workspaceStorage/*/state.vscdb; do
  [ -f "${db}" ] || continue
  sqlite3 "${db}" <<'SQL'
DELETE FROM ItemTable
WHERE key = 'chat.ChatSessionStore.index'
   OR key LIKE 'memento/webviewView.chatgpt.%'
   OR key LIKE 'memento/webviewView.claude%';
VACUUM;
SQL
done

write_status "removing_browser_webview_caches"
for cache_dir in \
  "${app_support}/Local Storage" \
  "${app_support}/Session Storage" \
  "${app_support}/Service Worker" \
  "${app_support}/WebStorage" \
  "${app_support}/Cache" \
  "${app_support}/Code Cache" \
  "${app_support}/GPUCache" \
  "${app_support}/blob_storage"; do
  if [ -e "${cache_dir}" ]; then
    rm -rf "${cache_dir}"
  fi
done

write_status "completed_backup_${backup_dir}"
echo "Backed up reset inputs to: ${backup_dir}"
echo "Cleared Antigravity browser/webview state and removed Codex persisted UI state."
