#!/usr/bin/env bash
set -euo pipefail

IMAGE="python:3.10-slim"
LIVE="0"

usage() {
  cat >&2 <<'USAGE'
usage: test_install_e2e.sh [--image IMAGE] [--live]

Runs tools/install.sh inside a fresh Linux Docker container.
Default mode is installer dry-run only. --live performs the real wheel download,
SHA-256 verification, pip install, and module-entrypoint smoke check.
USAGE
}

die() {
  local code="$1"
  shift
  printf '%s\n' "$*" >&2
  exit "${code}"
}

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --image)
      [[ "$#" -ge 2 ]] || die 2 "install_e2e_missing_image_value"
      IMAGE="$2"
      shift 2
      ;;
    --live)
      LIVE="1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      die 2 "install_e2e_unknown_argument:$1"
      ;;
  esac
done

command -v docker >/dev/null 2>&1 || die 1 "install_e2e_docker_missing"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_SH="${ROOT_DIR}/tools/install.sh"
[[ -f "${INSTALL_SH}" ]] || die 1 "install_e2e_install_sh_missing"

container_script='
set -euo pipefail
bash /tmp/install.sh --channel rc --dry-run --no-onboard | tee /tmp/install-dry-run.log
grep "install_sh_dry_run" /tmp/install-dry-run.log >/dev/null
grep -E "RC_WHEEL_SHA256=[0-9a-f]{64}" /tmp/install-dry-run.log >/dev/null
grep -E "RC_WHEEL_SIZE=[1-9][0-9]*" /tmp/install-dry-run.log >/dev/null
if [[ "${ILC_INSTALL_E2E_LIVE}" == "1" ]]; then
  bash /tmp/install.sh --channel rc --no-onboard
  python3 -m ilc_core.cli.main --help >/dev/null
fi
'

docker run --rm \
  -e "ILC_INSTALL_E2E_LIVE=${LIVE}" \
  -v "${INSTALL_SH}:/tmp/install.sh:ro" \
  "${IMAGE}" \
  bash -lc "${container_script}"

printf 'install_e2e_pass mode=%s image=%s\n' "$([[ "${LIVE}" == "1" ]] && printf live || printf dry-run)" "${IMAGE}"
