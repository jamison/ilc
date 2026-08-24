#!/usr/bin/env bash
set -euo pipefail

INSTALLER_VERSION="GAP-AGENT-ONBOARDING-PACKAGE-00b"
RC_WHEEL_URL="https://files.pythonhosted.org/packages/2a/42/5f67c2a63e253caa64092a44dc82d5339188f3d9408cfcc24a713223459d/ilc_core-0.4.0-py3-none-any.whl"
RC_WHEEL_SHA256="523fca5a3262eb7921cb0388a185a140d2a9417064483e5689acd64a71f50924"
RC_WHEEL_SIZE="1362456"
RC_MIN_PYTHON_MINOR="10"

CHANNEL="rc"
NO_ONBOARD="0"
TARGET_DIR=""
DRY_RUN="0"
TMP_DIR=""
TMP_WHEEL=""

cleanup() {
  if [[ -n "${TMP_DIR}" && -d "${TMP_DIR}" ]]; then
    rm -rf "${TMP_DIR}"
  elif [[ -n "${TMP_WHEEL}" && -f "${TMP_WHEEL}" ]]; then
    rm -f "${TMP_WHEEL}"
  fi
}
trap cleanup EXIT

usage() {
  cat >&2 <<'USAGE'
usage: install.sh [--channel rc] [--no-onboard] [--target-dir PATH] [--dry-run]

Installs the ilc-core Python wheel after SHA-256 verification.
Defaults to an ILC-managed venv at ~/.ilc/venv unless --target-dir is supplied.
Channels stable and dev are reserved but not embedded in this installer yet.
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
    --channel)
      [[ "$#" -ge 2 ]] || die 2 "install_sh_missing_channel_value"
      CHANNEL="$2"
      shift 2
      ;;
    --no-onboard)
      NO_ONBOARD="1"
      shift
      ;;
    --target-dir)
      [[ "$#" -ge 2 ]] || die 2 "install_sh_missing_target_dir_value"
      TARGET_DIR="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      die 2 "install_sh_unknown_argument:$1"
      ;;
  esac
done

if [[ "${CHANNEL}" != "rc" ]]; then
  die 1 "install_sh_channel_not_embedded:${CHANNEL}"
fi

next_step_hint() {
  if [[ "${NO_ONBOARD}" == "0" ]]; then
    local subcommand="install"
    local source_kind="invite"
    printf 'next_step_hint: ilc %s --from-%s <path>\n' "${subcommand}" "${source_kind}"
  fi
}

if [[ "${DRY_RUN}" == "1" ]]; then
  printf 'install_sh_dry_run\n'
  printf 'INSTALLER_VERSION=%s\n' "${INSTALLER_VERSION}"
  printf 'channel=%s\n' "${CHANNEL}"
  printf 'RC_WHEEL_URL=%s\n' "${RC_WHEEL_URL}"
  printf 'RC_WHEEL_SHA256=%s\n' "${RC_WHEEL_SHA256}"
  printf 'RC_WHEEL_SIZE=%s\n' "${RC_WHEEL_SIZE}"
  printf 'RC_MIN_PYTHON_MINOR=%s\n' "${RC_MIN_PYTHON_MINOR}"
  if [[ -n "${TARGET_DIR}" ]]; then
    printf 'target_dir=%s\n' "${TARGET_DIR}"
  fi
  next_step_hint
  exit 0
fi

command -v python3 >/dev/null 2>&1 || die 2 "install_sh_python3_missing"

PY_MINOR="$(
  python3 - <<'PY'
import sys
if sys.version_info.major != 3:
    raise SystemExit(1)
print(sys.version_info.minor)
PY
)" || die 2 "install_sh_python_version_parse_failed"

if (( PY_MINOR < RC_MIN_PYTHON_MINOR )); then
  die 2 "install_sh_python_version_too_old:3.${PY_MINOR}:requires_3.${RC_MIN_PYTHON_MINOR}"
fi

python3 -m pip --version >/dev/null 2>&1 || die 1 "install_sh_pip_missing"
python3 -m venv --help >/dev/null 2>&1 || die 1 "install_sh_venv_unavailable"

if command -v shasum >/dev/null 2>&1; then
  HASH_COMMAND="shasum"
elif command -v sha256sum >/dev/null 2>&1; then
  HASH_COMMAND="sha256sum"
else
  die 1 "install_sh_sha256_tool_missing"
fi

if command -v curl >/dev/null 2>&1; then
  DOWNLOADER="curl"
elif command -v wget >/dev/null 2>&1; then
  DOWNLOADER="wget"
else
  die 1 "install_sh_downloader_missing"
fi

if [[ -z "${TARGET_DIR}" ]]; then
  TARGET_DIR="${HOME}/.ilc/venv"
fi

if [[ -e "${TARGET_DIR}" ]]; then
  if [[ ! -d "${TARGET_DIR}" || ! -f "${TARGET_DIR}/pyvenv.cfg" ]]; then
    die 1 "install_sh_target_dir_exists_not_venv:${TARGET_DIR}"
  fi
  if [[ ! -x "${TARGET_DIR}/bin/python" ]]; then
    die 1 "install_sh_target_venv_python_missing:${TARGET_DIR}"
  fi
fi

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ilc-install-XXXXXX")"
TMP_WHEEL="${TMP_DIR}/ilc-core-0.4.0.whl"

if [[ "${DOWNLOADER}" == "curl" ]]; then
  curl -fsSL --progress-bar --max-time 120 -o "${TMP_WHEEL}" "${RC_WHEEL_URL}"
else
  wget -q --show-progress --timeout=120 -O "${TMP_WHEEL}" "${RC_WHEEL_URL}"
fi

actual_size="$(wc -c < "${TMP_WHEEL}" | tr -d '[:space:]')"
if [[ "${actual_size}" != "${RC_WHEEL_SIZE}" ]]; then
  die 1 "install_sh_size_verification_failed:expected_${RC_WHEEL_SIZE}:actual_${actual_size}"
fi

if [[ "${HASH_COMMAND}" == "shasum" ]]; then
  actual_hash="$(shasum -a 256 "${TMP_WHEEL}" | awk '{print $1}')"
else
  actual_hash="$(sha256sum "${TMP_WHEEL}" | awk '{print $1}')"
fi

if [[ "${actual_hash}" != "${RC_WHEEL_SHA256}" ]]; then
  die 1 "install_sh_hash_verification_failed:expected_${RC_WHEEL_SHA256}:actual_${actual_hash}"
fi

python3 -m venv "${TARGET_DIR}"
"${TARGET_DIR}/bin/python" -m pip install --quiet "${TMP_WHEEL}"
"${TARGET_DIR}/bin/python" -m ilc_core.cli.main --help >/dev/null 2>&1 || die 1 "install_sh_post_install_check_failed"

printf 'install_sh_success version=%s channel=%s\n' "${INSTALLER_VERSION}" "${CHANNEL}"
printf 'install_target_dir=%s\n' "${TARGET_DIR}"
next_step_hint
