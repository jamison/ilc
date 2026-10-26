# SPDX-License-Identifier: AGPL-3.0-only
"""Release manifest validation helpers."""

from ilc_core.release.installable_release_manifest import (
    InstallableReleaseManifestError,
    canonical_installable_release_manifest_bytes,
    load_installable_release_manifest,
    validate_installable_release_manifest,
)
from ilc_core.release.installable_release_signature import (
    InstallableReleaseSignatureError,
    build_envelope_skeleton,
    canonical_envelope_json,
    compute_signed_preimage_sha256,
    validate_envelope,
    validate_envelope_for_artifact,
    validate_envelope_set,
)
from ilc_core.release.install_sh_manifest_sync import verify_install_sh_manifest_sync
from ilc_core.release.consensus_binary_deploy import (
    CONSENSUS_BINARY_MEMBERS,
    ConsensusBinaryDeployError,
    VerifiedConsensusBinaryBundle,
    deploy_verified_consensus_binary_bundle,
    fetch_verified_consensus_binary_bundle,
    fetch_verify_and_deploy_consensus_binary_bundle,
)
from ilc_core.release.update_runtime import (
    enforce_download_size,
    is_already_current,
    select_update_artifact,
    verify_download_hash,
)
from ilc_core.release.update_signature_verifier import (
    PUBLIC_RC_RELEASE_SIGNER_PUBLIC_KEY_HEX,
    fetch_and_validate_envelope_set,
    verify_artifact_signature,
)
from ilc_core.release.upgrade_check import (
    UpgradeCheckError,
    check_for_upgrade,
    fetch_upgrade_assertion_json,
    validate_release_assertion,
)
from ilc_core.release.upgrade_state import (
    default_upgrade_state_path,
    read_upgrade_state,
    write_upgrade_state,
)

__all__ = [
    "InstallableReleaseManifestError",
    "InstallableReleaseSignatureError",
    "CONSENSUS_BINARY_MEMBERS",
    "ConsensusBinaryDeployError",
    "UpgradeCheckError",
    "VerifiedConsensusBinaryBundle",
    "build_envelope_skeleton",
    "canonical_installable_release_manifest_bytes",
    "canonical_envelope_json",
    "check_for_upgrade",
    "default_upgrade_state_path",
    "deploy_verified_consensus_binary_bundle",
    "fetch_upgrade_assertion_json",
    "fetch_verified_consensus_binary_bundle",
    "fetch_verify_and_deploy_consensus_binary_bundle",
    "compute_signed_preimage_sha256",
    "load_installable_release_manifest",
    "enforce_download_size",
    "is_already_current",
    "PUBLIC_RC_RELEASE_SIGNER_PUBLIC_KEY_HEX",
    "read_upgrade_state",
    "select_update_artifact",
    "validate_envelope",
    "validate_envelope_for_artifact",
    "validate_envelope_set",
    "validate_installable_release_manifest",
    "validate_release_assertion",
    "fetch_and_validate_envelope_set",
    "verify_install_sh_manifest_sync",
    "verify_artifact_signature",
    "verify_download_hash",
    "write_upgrade_state",
]
