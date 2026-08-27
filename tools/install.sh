#!/usr/bin/env bash
set -euo pipefail

INSTALLER_VERSION="GAP-ONBOARDING-PACKAGE-044-00b"
RC_WHEEL_URL="https://files.pythonhosted.org/packages/01/1e/78a69d572d4fa7e563a5d20ae5e2dbcca94f1b511c4373d09137639095c9/ilc_core-0.4.4-py3-none-any.whl"
RC_WHEEL_SHA256="4e6891c836d2b9c6757fa798b41b0fd1758b17503248783e89a94c60c6bfbd13"
RC_WHEEL_SIZE="1364353"
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
WHEEL_BASENAME="${RC_WHEEL_URL##*/}"
if [[ ! "${WHEEL_BASENAME}" =~ ^ilc_core-[0-9]+(\.[0-9]+){1,2}-py3-none-any\.whl$ ]]; then
  die 1 "install_sh_wheel_filename_invalid:${WHEEL_BASENAME}"
fi
TMP_WHEEL="${TMP_DIR}/${WHEEL_BASENAME}"
RC_WHEEL_SIZE_CAP="$(( (RC_WHEEL_SIZE * 11 + 9) / 10 ))"

python3 - "${RC_WHEEL_URL}" "${TMP_WHEEL}" "${RC_WHEEL_SIZE_CAP}" <<'PY'
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

url, output_path, cap_text = sys.argv[1], sys.argv[2], sys.argv[3]
cap = int(cap_text)
request = Request(url, headers={"User-Agent": "ilc-install/GAP-PUBLIC-INSTALL"})
try:
    with urlopen(request, timeout=120) as response:
        raw_status = getattr(response, "status", None)
        status = 200 if raw_status is None else int(raw_status)
        if status != 200:
            raise SystemExit(f"install_sh_download_failed:{status}")
        declared = response.headers.get("Content-Length")
        if declared is not None and int(declared) > cap:
            raise SystemExit("install_sh_download_size_exceeded")
        total = 0
        with open(output_path, "wb") as handle:
            while True:
                chunk = response.read(65536)
                if not chunk:
                    break
                total += len(chunk)
                if total > cap:
                    raise SystemExit("install_sh_download_size_exceeded")
                handle.write(chunk)
except HTTPError as exc:
    raise SystemExit(f"install_sh_download_failed:{exc.code}") from exc
except URLError as exc:
    raise SystemExit("install_sh_download_failed:network") from exc
except TimeoutError as exc:
    raise SystemExit("install_sh_download_failed:timeout") from exc
except ValueError as exc:
    raise SystemExit("install_sh_download_content_length_invalid") from exc
PY

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
