from __future__ import annotations

from ilc_core.exceptions import (
    IlcError,
    ProtocolError,
    ProtocolSchemaLoadError,
    ProtocolMappingError,
    ReplayProofError,
    ReplayProofManifestError,
    ReplayProofPackageError,
    ReplayProofBaselineError,
)


def test_protocol_exception_hierarchy_foundation() -> None:
    assert issubclass(ProtocolError, IlcError)
    assert issubclass(ProtocolError, ValueError)
    assert issubclass(ProtocolSchemaLoadError, ProtocolError)
    assert issubclass(ProtocolMappingError, ProtocolError)


def test_replay_proof_exception_hierarchy_foundation() -> None:
    assert issubclass(ReplayProofError, IlcError)
    assert issubclass(ReplayProofError, ValueError)
    assert issubclass(ReplayProofManifestError, ReplayProofError)
    assert issubclass(ReplayProofPackageError, ReplayProofError)
    assert issubclass(ReplayProofBaselineError, ReplayProofError)


def test_exception_messages_are_stable() -> None:
    assert str(ProtocolSchemaLoadError("protocol_schema_load_failed")) == "protocol_schema_load_failed"
    assert str(ProtocolMappingError("protocol_mapping_failed")) == "protocol_mapping_failed"
    assert str(ReplayProofManifestError("schema_violation:invalid_manifest_path")) == "schema_violation:invalid_manifest_path"
    assert str(ReplayProofPackageError("schema_violation:invalid_replay_proof_package_shape")) == "schema_violation:invalid_replay_proof_package_shape"
    assert str(ReplayProofBaselineError("schema_validation_failed")) == "schema_validation_failed"
