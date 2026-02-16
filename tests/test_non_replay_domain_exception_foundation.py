from __future__ import annotations

from ilc_core.exceptions import (
    ClauseBindingValidationError,
    CliPayloadError,
    CliToolInvocationError,
    EventLogValidationError,
    GovernanceIngestValidationError,
    IlcError,
    LedgerError,
    LedgerExportContractError,
    ProtocolError,
)


def test_protocol_non_replay_exception_hierarchy() -> None:
    for exc in (
        EventLogValidationError("x"),
        ClauseBindingValidationError("x"),
        GovernanceIngestValidationError("x"),
    ):
        assert isinstance(exc, ProtocolError)
        assert isinstance(exc, ValueError)


def test_ledger_non_replay_exception_hierarchy() -> None:
    exc = LedgerExportContractError("x")
    assert isinstance(exc, LedgerError)
    assert isinstance(exc, ValueError)


def test_cli_non_replay_exception_hierarchy() -> None:
    for exc in (CliPayloadError("x"), CliToolInvocationError("x")):
        assert isinstance(exc, IlcError)
        assert isinstance(exc, ValueError)
