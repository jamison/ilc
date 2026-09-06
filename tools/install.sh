#!/usr/bin/env bash
set -euo pipefail

INSTALLER_VERSION="GAP-CONSENSUS-BINARY-DEPLOY-FIX2-00-0417"
RC_WHEEL_URL="https://files.pythonhosted.org/packages/9b/84/59b4793e2e6ca20508978837c9a34830fa09cc05faf30349670ea523685c/ilc_core-0.4.17-py3-none-any.whl"
RC_WHEEL_SHA256="414702127dcbf4e97a8f29e0875f1f1494811b1873cff9fa748606b1b5f657f1"
RC_WHEEL_SIZE="1466767"
RC_MIN_PYTHON_MINOR="10"
RC_RELEASE_ID="ilc-core-0.4.17"
RC_WHEEL_ARTIFACT_ID="ilc-artifact:ilc-core-python-wheel-0417@phase-1628"
RC_SDIST_ARTIFACT_ID="ilc-artifact:ilc-core-python-sdist-0417@phase-1628"
RC_SDIST_SHA256="5957ea7be367d579b97bdf155f00ce36e4ae5e585db5b5640d3d7040c97cf2e7"
RC_SDIST_SIZE="1197171"
DEFAULT_RC_RELEASE_ENVELOPE_REF="https://raw.githubusercontent.com/jamison/ilc/main/docs/specs/ilc_core_0415_release_envelopes_GAP_RELEASE_SIGN_00c_v0.1.json"
RC_RELEASE_ENVELOPE_REF="${ILC_INSTALL_RELEASE_ENVELOPE_REF:-${DEFAULT_RC_RELEASE_ENVELOPE_REF}}"
RC_RELEASE_SIGNER_PUBLIC_KEY_HEX="5bf71c1e0ac93f2d7414b0dc315161fc4a57462c198ba1618e2890ec89a5b15a"
CONSENSUS_BIN_URL="https://github.com/jamison/ilc/releases/download/v0.4.16/ilc-consensus-linux-x86_64-v0.4.16.tar.gz"
CONSENSUS_BIN_SHA256="adde50e924c1ac0e0259998b29ef2778f4a4a7a8b4dfbfed72c206ca9f20bc42"
CONSENSUS_BIN_SIZE="4304398"
CONSENSUS_BIN_INSTALL_DIR="${ILC_CONSENSUS_BIN_INSTALL_DIR:-${HOME:-}/.ilc/bin}"

CHANNEL="rc"
INVITE_BUNDLE=""
INVITE_CODE=""
TARGET_DIR=""
RELAY_URL=""
RELAY_TLS_CERT_DER_SHA256=""
RELAY_NETWORK_ID=""
RELAY_INTERNAL_PORT=""
ENABLE_UPNP="0"
VERIFY_SIGNATURE="0"
DRY_RUN="0"
TMP_DIR=""
TMP_WHEEL=""
PROBE_OBSERVERS=()
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
INSTALLER_ROOT="$(CDPATH= cd -- "${SCRIPT_DIR}/.." && pwd -P)"

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
usage: install.sh [--channel rc] (--invite-bundle PATH | --invite-code CODE) [--target-dir PATH] [--relay-url URL] [--relay-tls-cert-der-sha256 HEX] [--relay-network-id ID] [--relay-internal-port PORT] [--probe-observer URL] [--enable-upnp] [--verify-signature] [--dry-run]

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
    --verify-signature)
      VERIFY_SIGNATURE="1"
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
  printf 'RC_RELEASE_ENVELOPE_REF=%s\n' "${RC_RELEASE_ENVELOPE_REF}"
  printf 'CONSENSUS_BIN_URL=%s\n' "${CONSENSUS_BIN_URL}"
  printf 'CONSENSUS_BIN_SHA256=%s\n' "${CONSENSUS_BIN_SHA256}"
  printf 'CONSENSUS_BIN_SIZE=%s\n' "${CONSENSUS_BIN_SIZE}"
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
  if [[ "${VERIFY_SIGNATURE}" == "1" ]]; then
    printf 'verify_signature=true\n'
  fi
  for observer in ${PROBE_OBSERVERS[@]+"${PROBE_OBSERVERS[@]}"}; do
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

if [[ "${VERIFY_SIGNATURE}" == "1" ]]; then
  if ! python3 -c "import cryptography" >/dev/null 2>&1; then
    die 1 "install_sh_signature_verification_failed:cryptography_not_available"
  fi
  python3 - "${TMP_WHEEL}" "${RC_RELEASE_ID}" "${RC_WHEEL_ARTIFACT_ID}" "${RC_WHEEL_SHA256}" "${RC_WHEEL_SIZE}" "${RC_RELEASE_ENVELOPE_REF}" "${RC_RELEASE_SIGNER_PUBLIC_KEY_HEX}" "${RC_SDIST_ARTIFACT_ID}" "${RC_SDIST_SHA256}" "${RC_SDIST_SIZE}" "${INSTALLER_ROOT}" <<'PY'
import hashlib
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

(
    _wheel_path,
    release_id,
    artifact_id,
    artifact_sha256,
    artifact_size,
    envelope_ref,
    signer_public_key_hex,
    sdist_artifact_id,
    sdist_sha256,
    sdist_size,
    installer_root,
) = sys.argv[1:12]
MAX_ENVELOPE_SET_BYTES = 65536
SCHEMA_VERSION = "GAP_RELEASE_SIGN_00b_v0.2"
SIGNED_PREIMAGE_ALGORITHM = "sha256_of_canonical_json"
SIGNED_PREIMAGE_DOMAIN = "ILC_RELEASE_ARTIFACT_SIGNATURE_V1"
SIGNING_ALGORITHM = "Ed25519"
SIGNED_AT = "1970-01-01T00:00:00Z"

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


class NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(req.full_url, code, "redirect_forbidden", headers, fp)


def fail(token):
    raise SystemExit(token)


def read_envelope_set(ref):
    parsed = urlparse(ref)
    if parsed.scheme:
        if parsed.scheme != "https":
            fail("release_envelope_fetch_insecure_url")
        request = Request(ref, headers={"User-Agent": "ilc-install/release-signature"})
        try:
            response = build_opener(NoRedirectHandler).open(request, timeout=30)
        except HTTPError as exc:
            if exc.code in {301, 302, 303, 307, 308}:
                fail("release_envelope_fetch_redirect_forbidden")
            fail(f"release_envelope_fetch_failed:{exc.code}")
        except (URLError, TimeoutError):
            fail("release_envelope_fetch_failed:network")
        with response:
            declared = response.headers.get("Content-Length")
            if declared is not None:
                try:
                    declared_size = int(declared)
                except ValueError:
                    fail("release_envelope_content_length_invalid")
                if declared_size > MAX_ENVELOPE_SET_BYTES:
                    fail("release_envelope_set_too_large")
            body = response.read(MAX_ENVELOPE_SET_BYTES + 1)
    else:
        path = Path(ref).expanduser()
        if not path.is_absolute() and not path.is_file():
            path = Path(installer_root) / path
        if not path.is_file():
            fail("release_envelope_set_path_not_found")
        with path.open("rb") as handle:
            body = handle.read(MAX_ENVELOPE_SET_BYTES + 1)
    if len(body) > MAX_ENVELOPE_SET_BYTES:
        fail("release_envelope_set_too_large")
    try:
        data = json.loads(body.decode("utf-8"), parse_constant=lambda value: fail("release_envelope_set_invalid_json"))
    except Exception:
        fail("release_envelope_set_invalid_json")
    if not isinstance(data, dict):
        fail("release_envelope_set_not_object")
    return data


def canonical_json(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def preimage_sha256(envelope):
    payload = {
        "artifact_id": envelope["artifact_id"],
        "artifact_sha256": envelope["artifact_sha256"],
        "genesis_lineage_ref": envelope["genesis_lineage_ref"],
        "prior_release_envelope_ref": envelope["prior_release_envelope_ref"],
        "release_id": envelope["release_id"],
        "release_key_registration_ref": envelope["release_key_registration_ref"],
        "schema_version": SCHEMA_VERSION,
        "signed_at": SIGNED_AT,
        "signed_preimage_domain": SIGNED_PREIMAGE_DOMAIN,
        "signing_algorithm": SIGNING_ALGORITHM,
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def require_envelope(envelope_set, envelope_artifact_id, expected_sha256):
    envelopes = envelope_set.get("envelopes")
    if not isinstance(envelopes, dict):
        fail("release_envelope_set_envelopes_invalid")
    envelope = envelopes.get(envelope_artifact_id)
    if not isinstance(envelope, dict):
        fail("release_envelope_missing_artifact")
    required = {
        "artifact_id",
        "artifact_sha256",
        "genesis_lineage_ref",
        "prior_release_envelope_ref",
        "release_id",
        "release_key_registration_ref",
        "schema_version",
        "signature_hex",
        "signed_at",
        "signed_preimage_algorithm",
        "signed_preimage_domain",
        "signed_preimage_sha256",
        "signer_public_key_hex",
        "signing_algorithm",
    }
    if set(envelope) != required:
        fail("release_envelope_field_set_invalid")
    if envelope["artifact_id"] != envelope_artifact_id:
        fail("release_envelope_artifact_id_mismatch")
    if envelope["artifact_sha256"] != expected_sha256:
        fail("release_envelope_artifact_sha256_mismatch")
    if envelope["release_id"] != release_id:
        fail("release_envelope_release_id_mismatch")
    if envelope["schema_version"] != SCHEMA_VERSION:
        fail("release_envelope_schema_version_invalid")
    if envelope["signed_at"] != SIGNED_AT:
        fail("release_envelope_signed_at_invalid")
    if envelope["signed_preimage_domain"] != SIGNED_PREIMAGE_DOMAIN:
        fail("release_envelope_preimage_domain_invalid")
    if envelope["signed_preimage_algorithm"] != SIGNED_PREIMAGE_ALGORITHM:
        fail("release_envelope_preimage_algorithm_invalid")
    if envelope["signing_algorithm"] != SIGNING_ALGORITHM:
        fail("release_envelope_signing_algorithm_invalid")
    if envelope["signer_public_key_hex"] != signer_public_key_hex:
        fail("release_envelope_signer_public_key_mismatch")
    expected_preimage = preimage_sha256(envelope)
    if envelope["signed_preimage_sha256"] != expected_preimage:
        fail("release_envelope_preimage_mismatch")
    return envelope

manifest = {
    "artifacts": [
        {
            "arch": "any",
            "artifact_id": artifact_id,
            "artifact_type": "python_wheel",
            "canonical_hash": f"sha256:{artifact_sha256}",
            "channel": "rc",
            "download_url": "https://files.pythonhosted.org/",
            "lineage_reference": "artifact:ilc-artifact:source-release-tarball@phase-1334@sha256:60a2f404576e5abbc45bc29ab4ae106368a764aa3d37f2ca458d35363cc45a47",
            "min_python_version": "3.10",
            "platform": "any",
            "produced_phase": 1628,
            "ratification_token": "cdl_086_ratified_phase_1220",
            "signing_status": "signed",
            "size_bytes": int(artifact_size),
        },
        {
            "arch": "any",
            "artifact_id": sdist_artifact_id,
            "artifact_type": "python_sdist",
            "canonical_hash": f"sha256:{sdist_sha256}",
            "channel": "rc",
            "download_url": "https://files.pythonhosted.org/",
            "lineage_reference": "artifact:ilc-artifact:source-release-tarball@phase-1334@sha256:60a2f404576e5abbc45bc29ab4ae106368a764aa3d37f2ca458d35363cc45a47",
            "min_python_version": "3.10",
            "platform": "any",
            "produced_phase": 1628,
            "ratification_token": "cdl_086_ratified_phase_1220",
            "signing_status": "signed",
            "size_bytes": int(sdist_size),
        }
    ],
    "channel": "rc",
    "manifest_produced_phase": 1628,
    "manifest_schema_version": "ilc_installable_release_manifest_GAP_PUBLIC_INSTALL_01.v0.1",
    "non_claims": ["no_public_mirror_push"],
    "release_envelope_ref": envelope_ref,
    "release_id": release_id,
}
envelope_set = read_envelope_set(envelope_ref)
if envelope_set.get("schema_version") != SCHEMA_VERSION or envelope_set.get("version") != "0.4.17":
    fail("release_envelope_set_schema_version_invalid")
expected_artifact_ids = {item["artifact_id"] for item in manifest["artifacts"]}
if set(envelope_set.get("envelopes", {})) != expected_artifact_ids:
    fail("release_envelope_set_artifact_coverage_mismatch")
sdist_envelope = require_envelope(envelope_set, sdist_artifact_id, sdist_sha256)
wheel_envelope = require_envelope(envelope_set, artifact_id, artifact_sha256)
try:
    public_key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(signer_public_key_hex))
    for envelope in (wheel_envelope, sdist_envelope):
        public_key.verify(
            bytes.fromhex(envelope["signature_hex"]),
            bytes.fromhex(envelope["signed_preimage_sha256"]),
        )
except (InvalidSignature, ValueError):
    fail("release_envelope_signature_invalid")
print(f"install_sh_signature_verified:{artifact_id}")
PY
fi

python3 -m venv "${TARGET_DIR}"
"${TARGET_DIR}/bin/python" -m pip install --quiet "${TMP_WHEEL}"
"${TARGET_DIR}/bin/python" -m ilc_core.cli.main --help >/dev/null 2>&1 || die 1 "install_sh_post_install_check_failed"

OS_NAME="$(uname -s)"
ARCH_NAME="$(uname -m)"
if [[ "${OS_NAME}" == "Linux" && ( "${ARCH_NAME}" == "x86_64" || "${ARCH_NAME}" == "amd64" ) ]]; then
  if [[ "${CONSENSUS_BIN_INSTALL_DIR}" == "/.ilc/bin" ]]; then
    die 1 "install_sh_consensus_binary_home_missing"
  fi
  CONSENSUS_TARBALL="${TMP_DIR}/ilc-consensus-linux-x86_64-v0.4.16.tar.gz"
  CONSENSUS_BIN_SIZE_CAP="$(( (CONSENSUS_BIN_SIZE * 11 + 9) / 10 ))"
  python3 - "${CONSENSUS_BIN_URL}" "${CONSENSUS_TARBALL}" "${CONSENSUS_BIN_SIZE_CAP}" <<'PY'
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

url, output_path, cap_text = sys.argv[1], sys.argv[2], sys.argv[3]
cap = int(cap_text)
request = Request(url, headers={"User-Agent": "ilc-install/consensus-binary"})
try:
    with urlopen(request, timeout=120) as response:
        raw_status = getattr(response, "status", None)
        status = 200 if raw_status is None else int(raw_status)
        if status != 200:
            raise SystemExit(f"install_sh_consensus_binary_download_failed:{status}")
        declared = response.headers.get("Content-Length")
        if declared is not None and int(declared) > cap:
            raise SystemExit("install_sh_consensus_binary_size_exceeded")
        total = 0
        with open(output_path, "wb") as handle:
            while True:
                chunk = response.read(65536)
                if not chunk:
                    break
                total += len(chunk)
                if total > cap:
                    raise SystemExit("install_sh_consensus_binary_size_exceeded")
                handle.write(chunk)
except HTTPError as exc:
    raise SystemExit(f"install_sh_consensus_binary_download_failed:{exc.code}") from exc
except URLError as exc:
    raise SystemExit("install_sh_consensus_binary_download_failed:network") from exc
except TimeoutError as exc:
    raise SystemExit("install_sh_consensus_binary_download_failed:timeout") from exc
except ValueError as exc:
    raise SystemExit("install_sh_consensus_binary_content_length_invalid") from exc
PY
  actual_consensus_size="$(wc -c < "${CONSENSUS_TARBALL}" | tr -d '[:space:]')"
  if [[ "${actual_consensus_size}" != "${CONSENSUS_BIN_SIZE}" ]]; then
    die 1 "install_sh_consensus_binary_size_verification_failed:expected_${CONSENSUS_BIN_SIZE}:actual_${actual_consensus_size}"
  fi
  if [[ "${HASH_COMMAND}" == "shasum" ]]; then
    actual_consensus_hash="$(shasum -a 256 "${CONSENSUS_TARBALL}" | awk '{print $1}')"
  else
    actual_consensus_hash="$(sha256sum "${CONSENSUS_TARBALL}" | awk '{print $1}')"
  fi
  if [[ "${actual_consensus_hash}" != "${CONSENSUS_BIN_SHA256}" ]]; then
    die 1 "install_sh_consensus_binary_hash_verification_failed:expected_${CONSENSUS_BIN_SHA256}:actual_${actual_consensus_hash}"
  fi
  mkdir -p "${CONSENSUS_BIN_INSTALL_DIR}"
  python3 - "${CONSENSUS_TARBALL}" "${CONSENSUS_BIN_INSTALL_DIR}" <<'PY'
import os
import stat
import sys
import tarfile
from pathlib import Path

tarball, output_dir = sys.argv[1], Path(sys.argv[2])
expected = {
    "bls_verify_digest",
    "invite_pop_bls",
    "keygen",
    "validator_endpoint_assertion_bls",
    "validator_harness",
}
with tarfile.open(tarball, "r:gz") as archive:
    members = archive.getmembers()
    if len(members) != len(expected):
        raise SystemExit("install_sh_consensus_binary_tar_member_count_invalid")
    names = {member.name for member in members}
    if names != expected:
        raise SystemExit("install_sh_consensus_binary_tar_members_invalid")
    for member in members:
        path = Path(member.name)
        if path.is_absolute() or len(path.parts) != 1 or not member.isfile():
            raise SystemExit("install_sh_consensus_binary_tar_member_unsafe")
        if member.size <= 0 or member.size > 50_000_000:
            raise SystemExit("install_sh_consensus_binary_member_size_invalid")
        source = archive.extractfile(member)
        if source is None:
            raise SystemExit("install_sh_consensus_binary_member_unreadable")
        destination = output_dir / member.name
        temporary = output_dir / f".{member.name}.tmp"
        with source, temporary.open("wb") as handle:
            while True:
                chunk = source.read(65536)
                if not chunk:
                    break
                handle.write(chunk)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH | stat.S_IRGRP | stat.S_IROTH)
        os.replace(temporary, destination)
print("install_sh_consensus_binaries_installed")
PY
else
  printf 'install_sh_consensus_binaries_skipped platform=%s_%s\n' "${OS_NAME}" "${ARCH_NAME}"
fi

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
for observer in ${PROBE_OBSERVERS[@]+"${PROBE_OBSERVERS[@]}"}; do
  INSTALL_ARGS+=(--probe-observer "${observer}")
done
printf 'install_sh_running_invite_onboard\n'
"${TARGET_DIR}/bin/python" -m ilc_core.cli.main install "${INSTALL_ARGS[@]}"
printf 'install_sh_invite_onboard_complete\n'
