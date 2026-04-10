#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
VENV_PATH="${ROOT_DIR}/out/mempalace_runtime"
MEMPALACE_VERSION="3.1.0"
PYTHON_OVERRIDE="${ILC_MEMPALACE_PYTHON:-}"

usage() {
  cat <<USAGE
Usage: $0 [--venv PATH] [--python PATH] [--version X.Y.Z]

Create or refresh a dedicated local MemPalace virtualenv.
Supported Python versions: 3.9-3.12.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --venv)
      VENV_PATH="$2"
      shift 2
      ;;
    --python)
      PYTHON_OVERRIDE="$2"
      shift 2
      ;;
    --version)
      MEMPALACE_VERSION="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown_arg:$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

choose_python() {
  local candidate version major minor
  if [[ -n "$PYTHON_OVERRIDE" ]]; then
    if [[ ! -x "$PYTHON_OVERRIDE" ]]; then
      echo "python_override_not_executable:$PYTHON_OVERRIDE" >&2
      exit 1
    fi
    candidate="$PYTHON_OVERRIDE"
    version="$($candidate -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
    major="${version%%.*}"
    minor="${version##*.}"
    if [[ "$major" != "3" ]] || (( minor < 9 || minor > 12 )); then
      echo "unsupported_python_version:$version" >&2
      exit 1
    fi
    echo "$candidate"
    return 0
  fi

  for candidate in python3.12 python3.11 python3.10 python3.9; do
    if command -v "$candidate" >/dev/null 2>&1; then
      echo "$(command -v "$candidate")"
      return 0
    fi
  done

  echo "no_supported_python_found" >&2
  exit 1
}

PYTHON_BIN="$(choose_python)"
mkdir -p "$(dirname "$VENV_PATH")"
rm -rf "$VENV_PATH"
"$PYTHON_BIN" -m venv "$VENV_PATH"
PATH="$VENV_PATH/bin:$PATH" python -m pip install --upgrade pip >/dev/null
PATH="$VENV_PATH/bin:$PATH" python -m pip install "mempalace==${MEMPALACE_VERSION}" >/dev/null
# Reinstall top-level wheels explicitly so entry points are present even when
# the first dependency-heavy install path completes without exposing them.
PATH="$VENV_PATH/bin:$PATH" python -m pip install --no-deps "chromadb==0.6.3" "mempalace==${MEMPALACE_VERSION}" >/dev/null
"$VENV_PATH/bin/mempalace" --help >/dev/null
printf 'mempalace_env_ready\npython=%s\nvenv=%s\nversion=%s\n' "$PYTHON_BIN" "$VENV_PATH" "$MEMPALACE_VERSION"
