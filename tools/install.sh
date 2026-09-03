#!/usr/bin/env bash
set -euo pipefail

INSTALLER_VERSION="GAP-RELAY-BOOTSTRAP-CAPSULE-SIGN-0413-00"
RC_WHEEL_URL="https://files.pythonhosted.org/packages/8e/7f/1f03433a9fbe0621f82af9bad2a820a283f5bf8e42f4a6ff2ebd8d9fcec3/ilc_core-0.4.13-py3-none-any.whl"
RC_WHEEL_SHA256="dba05b1536ddb5330f8483ae976f294e1e4ea2279ef7457b20fe26518e9a7609"
RC_WHEEL_SIZE="1442131"
RC_MIN_PYTHON_MINOR="10"

CHANNEL="rc"
INVITE_BUNDLE=""
INVITE_CODE=""
TARGET_DIR=""
RELAY_URL=""
RELAY_TLS_CERT_DER_SHA256=""
RELAY_NETWORK_ID=""
RELAY_INTERNAL_PORT=""
ENABLE_UPNP="0"
DRY_RUN="0"
TMP_DIR=""
TMP_WHEEL=""
PROBE_OBSERVERS=()

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
usage: install.sh [--channel rc] (--invite-bundle PATH | --invite-code CODE) [--target-dir PATH] [--relay-url URL] [--relay-tls-cert-der-sha256 HEX] [--relay-network-id ID] [--relay-internal-port PORT] [--probe-observer URL] [--enable-upnp] [--dry-run]

Installs the ilc-core Python wheel after SHA-256 verification and completes
invite-based onboarding with the supplied Genesis invite bundle or relay invite code.
Defaults to an ILC-managed venv at ~/.ilc/venv unless --target-dir is supplied.
Relay probing is optional but, when supplied, is handled by the installed CLI
with locally generated relay-admission proof from the fresh AgentID key.
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
    --invite-bundle)
      [[ "$#" -ge 2 ]] || die 2 "install_sh_missing_invite_bundle_value"
      INVITE_BUNDLE="$2"
      shift 2
      ;;
    --invite-code)
      [[ "$#" -ge 2 ]] || die 2 "install_sh_missing_invite_code_value"
      INVITE_CODE="$2"
      shift 2
      ;;
    --target-dir)
      [[ "$#" -ge 2 ]] || die 2 "install_sh_missing_target_dir_value"
      TARGET_DIR="$2"
      shift 2
      ;;
    --relay-url)
      [[ "$#" -ge 2 ]] || die 2 "install_sh_missing_relay_url_value"
      RELAY_URL="$2"
      shift 2
      ;;
    --relay-tls-cert-der-sha256)
      [[ "$#" -ge 2 ]] || die 2 "install_sh_missing_relay_tls_cert_der_sha256_value"
      RELAY_TLS_CERT_DER_SHA256="$2"
      shift 2
      ;;
    --relay-network-id)
      [[ "$#" -ge 2 ]] || die 2 "install_sh_missing_relay_network_id_value"
      RELAY_NETWORK_ID="$2"
      shift 2
      ;;
    --relay-internal-port)
      [[ "$#" -ge 2 ]] || die 2 "install_sh_missing_relay_internal_port_value"
      RELAY_INTERNAL_PORT="$2"
      shift 2
      ;;
    --probe-observer)
      [[ "$#" -ge 2 ]] || die 2 "install_sh_missing_probe_observer_value"
      PROBE_OBSERVERS+=("$2")
      shift 2
      ;;
    --enable-upnp)
      ENABLE_UPNP="1"
      shift
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

if [[ -z "${INVITE_BUNDLE}" && -z "${INVITE_CODE}" ]]; then
  die 2 "install_sh_invite_bundle_or_code_required"
fi
if [[ -n "${INVITE_BUNDLE}" && -n "${INVITE_CODE}" ]]; then
  die 2 "install_sh_invite_bundle_and_code_mutually_exclusive"
fi

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
  printf 'invite_bundle=%s\n' "${INVITE_BUNDLE}"
  if [[ -n "${INVITE_CODE}" ]]; then
    printf 'invite_code=%s\n' "${INVITE_CODE}"
  fi
  if [[ -n "${RELAY_URL}" ]]; then
    printf 'relay_url=%s\n' "${RELAY_URL}"
  fi
  if [[ -n "${RELAY_TLS_CERT_DER_SHA256}" ]]; then
    printf 'relay_tls_cert_der_sha256=%s\n' "${RELAY_TLS_CERT_DER_SHA256}"
  fi
  if [[ -n "${RELAY_NETWORK_ID}" ]]; then
    printf 'relay_network_id=%s\n' "${RELAY_NETWORK_ID}"
  fi
  if [[ -n "${RELAY_INTERNAL_PORT}" ]]; then
    printf 'relay_internal_port=%s\n' "${RELAY_INTERNAL_PORT}"
  fi
  if [[ "${ENABLE_UPNP}" == "1" ]]; then
    printf 'enable_upnp=true\n'
  fi
  for observer in "${PROBE_OBSERVERS[@]}"; do
    printf 'probe_observer=%s\n' "${observer}"
  done
  exit 0
fi

if [[ -n "${INVITE_BUNDLE}" && ! -f "${INVITE_BUNDLE}" ]]; then
  die 1 "install_sh_invite_bundle_not_found:${INVITE_BUNDLE}"
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

if [[ -n "${INVITE_CODE}" ]]; then
  INVITE_BUNDLE="${TMP_DIR}/invite_code_bundle.json"
  "${TARGET_DIR}/bin/python" - "${INVITE_CODE}" "${RELAY_URL}" "${RELAY_TLS_CERT_DER_SHA256}" "${INVITE_BUNDLE}" <<'PY'
import base64
import hashlib
import http.client
import importlib.resources
import json
import ssl
import sys
from urllib.parse import urlparse

from ilc_core.epoch.genesis_settlement_destination import GENESIS_CAPSULE_SIGNING_PK_HEX
from ilc_core.network.relay.invite_code import validate_code
from ilc_core.network.relay.relay_server import parse_relay_bootstrap_capsule, verify_shortcode_invite_bundle

code, relay_url_arg, tls_pin_arg, output_path = sys.argv[1:5]
if not validate_code(code):
    raise SystemExit("install_sh_invite_code_invalid")

def load_capsule_records():
    try:
        raw = importlib.resources.files("ilc_core.data").joinpath("relay_bootstrap_capsule.json").read_text(encoding="utf-8")
        capsule = json.loads(raw)
    except Exception:
        return ()
    return parse_relay_bootstrap_capsule(
        capsule,
        genesis_capsule_pk_hex=GENESIS_CAPSULE_SIGNING_PK_HEX,
        expected_network_id="public-rc",
        current_epoch=0,
    )

records = load_capsule_records()
if relay_url_arg:
    relay_url = relay_url_arg
    matches = [record for record in records if record.get("control_url") == relay_url]
    tls_pin = tls_pin_arg or (matches[0].get("tls_cert_der_sha256") if matches else "")
else:
    if not records:
        raise SystemExit("install_sh_invite_code_no_relay_url_and_no_bundled_capsule")
    selected = sorted(records, key=lambda item: str(item.get("control_url")))[0]
    relay_url = str(selected["control_url"])
    tls_pin = str(selected["tls_cert_der_sha256"])
if not isinstance(tls_pin, str) or len(tls_pin) != 64 or any(char not in "0123456789abcdef" for char in tls_pin):
    raise SystemExit("install_sh_invite_code_tls_pin_invalid")

parsed = urlparse(relay_url)
if parsed.scheme != "https" or parsed.query or parsed.fragment or parsed.username or parsed.password or not parsed.hostname:
    raise SystemExit("install_sh_invite_code_relay_url_invalid")
port = parsed.port or 443
path = f"/relay/invite/{code}"
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
conn = http.client.HTTPSConnection(parsed.hostname, port, context=context, timeout=30)
try:
    conn.connect()
    der = conn.sock.getpeercert(binary_form=True) if conn.sock is not None else b""
    actual_pin = hashlib.sha256(der).hexdigest()
    if actual_pin != tls_pin:
        raise SystemExit("install_sh_invite_code_tls_pin_mismatch")
    conn.request("GET", path, headers={"User-Agent": "ilc-install/invite-code"})
    response = conn.getresponse()
    raw = response.read(65537)
finally:
    conn.close()
if response.status in {301, 302, 303, 307, 308}:
    raise SystemExit("install_sh_invite_code_redirect_forbidden")
if response.status == 410:
    try:
        error = json.loads(raw.decode("utf-8")).get("error")
    except Exception:
        error = ""
    if error == "code_expired":
        raise SystemExit("install_sh_invite_code_expired")
    if error == "code_exhausted":
        raise SystemExit("install_sh_invite_code_exhausted")
    raise SystemExit("install_sh_invite_code_gone")
if response.status != 200:
    raise SystemExit(f"install_sh_invite_code_fetch_failed:{response.status}")
if len(raw) > 65536:
    raise SystemExit("install_sh_invite_code_response_too_large")
try:
    payload = json.loads(raw.decode("utf-8"))
    bundle_raw = base64.b64decode(payload["bundle_b64"].encode("ascii"), validate=True)
except Exception:
    raise SystemExit("install_sh_invite_code_response_invalid")
if len(bundle_raw) > 32768:
    raise SystemExit("install_sh_invite_code_bundle_too_large")
try:
    bundle = json.loads(bundle_raw.decode("utf-8"))
except Exception:
    raise SystemExit("install_sh_invite_code_bundle_json_invalid")
if not isinstance(bundle, dict) or not verify_shortcode_invite_bundle(bundle):
    raise SystemExit("install_sh_invite_code_bundle_signature_invalid")
with open(output_path, "wb") as handle:
    handle.write(bundle_raw)
PY
fi

printf 'install_sh_success version=%s channel=%s\n' "${INSTALLER_VERSION}" "${CHANNEL}"
printf 'install_target_dir=%s\n' "${TARGET_DIR}"

INSTALL_SLICE_DIR="${HOME}/.ilc/installed_slices"
INSTALL_RECEIPT="${INSTALL_SLICE_DIR}/install_receipt.json"
INSTALL_ARGS=(
  --from-invite "${INVITE_BUNDLE}"
  --target-dir "${INSTALL_SLICE_DIR}"
  --output-receipt "${INSTALL_RECEIPT}"
)
if [[ -n "${RELAY_URL}" ]]; then
  INSTALL_ARGS+=(--relay-url "${RELAY_URL}")
fi
if [[ -n "${RELAY_TLS_CERT_DER_SHA256}" ]]; then
  INSTALL_ARGS+=(--relay-tls-cert-der-sha256 "${RELAY_TLS_CERT_DER_SHA256}")
fi
if [[ -n "${RELAY_NETWORK_ID}" ]]; then
  INSTALL_ARGS+=(--relay-network-id "${RELAY_NETWORK_ID}")
fi
if [[ -n "${RELAY_INTERNAL_PORT}" ]]; then
  INSTALL_ARGS+=(--relay-internal-port "${RELAY_INTERNAL_PORT}")
fi
if [[ "${ENABLE_UPNP}" == "1" ]]; then
  INSTALL_ARGS+=(--enable-upnp)
fi
for observer in "${PROBE_OBSERVERS[@]}"; do
  INSTALL_ARGS+=(--probe-observer "${observer}")
done
printf 'install_sh_running_invite_onboard\n'
"${TARGET_DIR}/bin/python" -m ilc_core.cli.main install "${INSTALL_ARGS[@]}"
printf 'install_sh_invite_onboard_complete\n'
