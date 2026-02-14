from __future__ import annotations

from ilc_core import exceptions as exc


def test_ilc_error_is_base() -> None:
    assert issubclass(exc.IlcError, Exception)


def test_insufficient_stake_subclasses_value_error() -> None:
    assert issubclass(exc.InsufficientStakeError, ValueError)
    assert issubclass(exc.InsufficientStakeError, exc.IlcError)
    err = exc.InsufficientStakeError("agent_1", stake=5.0, required=10.0)
    assert err.agent_id == "agent_1"
    assert "agent_1" in str(err)


def test_stake_not_found_subclasses_key_error() -> None:
    assert issubclass(exc.StakeNotFoundError, KeyError)
    assert issubclass(exc.StakeNotFoundError, exc.IlcError)


def test_graph_hierarchy_shapes() -> None:
    assert issubclass(exc.GraphIntegrityError, ValueError)
    assert issubclass(exc.DuplicateNodeError, exc.GraphIntegrityError)
    assert issubclass(exc.NodeNotFoundError, KeyError)


def test_manifest_hierarchy() -> None:
    assert issubclass(exc.ManifestParseError, exc.ManifestError)
    assert issubclass(exc.ManifestParseError, ValueError)
    assert issubclass(exc.ManifestEntryNotFoundError, FileNotFoundError)


def test_canon_verification_subclasses_value_error() -> None:
    assert issubclass(exc.CanonVerificationError, ValueError)
    assert issubclass(exc.CanonVerificationError, exc.IlcError)


def test_config_not_found_subclasses_file_not_found() -> None:
    assert issubclass(exc.ConfigNotFoundError, FileNotFoundError)
    assert issubclass(exc.ConfigNotFoundError, exc.ConfigError)


def test_backward_compat_imports() -> None:
    from ilc_core.protocol.ilc_cluster_a_replay_proof_batch_ops import (
        ManifestParseError as ManifestParseErrorFromOps,
    )
    from ilc_core.ledger.canon_loader import (
        CanonVerificationError as CanonVerificationErrorFromLoader,
    )
    from ilc_core.star_map.route_index import (
        NgramExtractionError as NgramExtractionErrorFromRouteIndex,
        TokenizationError as TokenizationErrorFromRouteIndex,
    )

    assert issubclass(ManifestParseErrorFromOps, exc.ManifestError)
    assert issubclass(CanonVerificationErrorFromLoader, exc.IlcError)
    assert issubclass(TokenizationErrorFromRouteIndex, exc.IlcError)
    assert issubclass(NgramExtractionErrorFromRouteIndex, exc.IlcError)
