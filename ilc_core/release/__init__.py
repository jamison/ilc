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

__all__ = [
    "InstallableReleaseManifestError",
    "InstallableReleaseSignatureError",
    "build_envelope_skeleton",
    "canonical_installable_release_manifest_bytes",
    "canonical_envelope_json",
    "compute_signed_preimage_sha256",
    "load_installable_release_manifest",
    "enforce_download_size",
    "is_already_current",
    "PUBLIC_RC_RELEASE_SIGNER_PUBLIC_KEY_HEX",
    "select_update_artifact",
    "validate_envelope",
    "validate_envelope_for_artifact",
    "validate_envelope_set",
    "validate_installable_release_manifest",
    "fetch_and_validate_envelope_set",
    "verify_install_sh_manifest_sync",
    "verify_artifact_signature",
    "verify_download_hash",
]
