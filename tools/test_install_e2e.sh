#!/usr/bin/env bash
set -euo pipefail

IMAGE="python:3.10-slim"
LIVE="0"

usage() {
  cat >&2 <<'USAGE'
usage: test_install_e2e.sh [--image IMAGE] [--live]

Runs tools/install.sh inside a fresh Linux Docker container.
Default mode is installer dry-run only. --live performs the real wheel download,
SHA-256 verification, pip install, invite onboarding, and module-entrypoint
smoke check. Live mode requires ILC_INSTALL_E2E_INVITE_BUNDLE to point to a
complete invite bundle JSON on the host.
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
INVITE_BUNDLE="${ILC_INSTALL_E2E_INVITE_BUNDLE:-}"
if [[ "${LIVE}" == "1" ]]; then
  [[ -n "${INVITE_BUNDLE}" ]] || die 2 "install_e2e_invite_bundle_required_for_live"
  [[ -f "${INVITE_BUNDLE}" ]] || die 1 "install_e2e_invite_bundle_missing:${INVITE_BUNDLE}"
fi

container_script='
set -euo pipefail
bash /tmp/install.sh --channel rc --dry-run --invite-bundle /tmp/invite.json | tee /tmp/install-dry-run.log
grep "install_sh_dry_run" /tmp/install-dry-run.log >/dev/null
grep -E "RC_WHEEL_SHA256=[0-9a-f]{64}" /tmp/install-dry-run.log >/dev/null
grep -E "RC_WHEEL_SIZE=[1-9][0-9]*" /tmp/install-dry-run.log >/dev/null
grep "invite_bundle=/tmp/invite.json" /tmp/install-dry-run.log >/dev/null
if [[ "${ILC_INSTALL_E2E_LIVE}" == "1" ]]; then
  bash /tmp/install.sh --channel rc --invite-bundle /tmp/invite.json
  python3 -m ilc_core.cli.main --help >/dev/null
fi
'

docker_args=(
  --rm
  -e "ILC_INSTALL_E2E_LIVE=${LIVE}" \
  -v "${INSTALL_SH}:/tmp/install.sh:ro"
)
if [[ "${LIVE}" == "1" ]]; then
  docker_args+=(-v "${INVITE_BUNDLE}:/tmp/invite.json:ro")
fi

docker run "${docker_args[@]}" "${IMAGE}" bash -lc "${container_script}"

printf 'install_e2e_pass mode=%s image=%s\n' "$([[ "${LIVE}" == "1" ]] && printf live || printf dry-run)" "${IMAGE}"
