# SPDX-License-Identifier: AGPL-3.0-only
"""Strict field sets and bounds for software release assertion v0.1."""

ASSERTION_REQUIRED_FIELDS = frozenset(
    {
        "artifact_nodes",
        "assertion_cid",
        "build_recipe_nodes",
        "release_attestation_edges",
        "schema_version",
        "software_release_node",
    }
)
ASSERTION_OPTIONAL_FIELDS = frozenset({"native_submit_envelope"})
SOFTWARE_RELEASE_NODE_FIELDS = frozenset(
    {
        "artifact_cids",
        "build_recipe_cid",
        "changelog_hash",
        "cid",
        "node_kind",
        "package_name",
        "release_channel",
        "release_date",
        "release_key_pubkey",
        "release_signature_ref",
        "schema_version",
        "source_commit",
        "version",
    }
)
ARTIFACT_NODE_FIELDS = frozenset(
    {
        "artifact_id",
        "artifact_type",
        "cid",
        "filename",
        "node_kind",
        "package_name",
        "package_version",
        "pypi_url",
        "schema_version",
        "sha256",
        "size_bytes",
    }
)
BUILD_RECIPE_NODE_FIELDS = frozenset(
    {
        "build_command",
        "build_date",
        "build_env_hash",
        "build_toolchain",
        "builder_agent_id",
        "cid",
        "node_kind",
        "reproducibility_hash",
        "schema_version",
        "source_commit",
    }
)
ATTESTATION_REQUIRED_FIELDS = frozenset(
    {
        "artifact_id",
        "artifact_sha256",
        "attestation_date",
        "edge_type",
        "genesis_lineage_ref",
        "prior_release_envelope_ref",
        "release_key_registration_ref",
        "schema_version",
        "signature_hex",
        "signed_preimage_domain",
        "signed_preimage_sha256",
        "signer_public_key_hex",
        "signing_algorithm",
        "source",
        "target",
    }
)
ATTESTATION_OPTIONAL_FIELDS = frozenset({"signature_scheme"})
CURRENT_ELIGIBILITY_STATUSES = frozenset(
    {
        "verified_current_policy",
        "rejected_by_current_policy",
        "bounded_compatibility_source",
        "unresolved",
    }
)
MAX_RELEASE_ARTIFACTS = 16
MAX_RELEASE_BUILD_RECIPES = 4
MAX_RELEASE_ATTESTATIONS = 32


__all__ = [
    "ARTIFACT_NODE_FIELDS",
    "ASSERTION_OPTIONAL_FIELDS",
    "ASSERTION_REQUIRED_FIELDS",
    "ATTESTATION_OPTIONAL_FIELDS",
    "ATTESTATION_REQUIRED_FIELDS",
    "BUILD_RECIPE_NODE_FIELDS",
    "CURRENT_ELIGIBILITY_STATUSES",
    "MAX_RELEASE_ARTIFACTS",
    "MAX_RELEASE_ATTESTATIONS",
    "MAX_RELEASE_BUILD_RECIPES",
    "SOFTWARE_RELEASE_NODE_FIELDS",
]
