from __future__ import annotations

import pytest

from ilc_core.exceptions import LedgerExportContractError
from ilc_core.ledger.canon_export_bundle import write_canon_export_bundle
from ilc_core.ledger.canon_export_bundle_sign import load_key_from_file
from ilc_core.ledger.canon_export_format import export_canon_format_v0_1


def test_export_format_missing_required_keys_raises_domain_exception() -> None:
    with pytest.raises(LedgerExportContractError, match="missing required keys"):
        export_canon_format_v0_1({"canon_hash": "h1"})


def test_export_format_invalid_type_raises_domain_exception() -> None:
    with pytest.raises(LedgerExportContractError, match="Field 'epochs' must be a list"):
        export_canon_format_v0_1(
            {
                "canon_hash": "h",
                "canon_export_version": "v",
                "epochs": "not_a_list",
            }
        )


def test_bundle_writer_missing_canon_hash_raises_domain_exception(tmp_path) -> None:
    with pytest.raises(LedgerExportContractError, match="missing required 'canon_hash'"):
        write_canon_export_bundle({}, {}, tmp_path / "bundle")


def test_load_key_from_file_empty_raises_domain_exception(tmp_path) -> None:
    key_path = tmp_path / "empty.txt"
    key_path.write_text("", encoding="utf-8")
    with pytest.raises(LedgerExportContractError, match="Key file is empty"):
        load_key_from_file(key_path)


def test_load_key_from_file_invalid_base64_raises_domain_exception(tmp_path) -> None:
    key_path = tmp_path / "bad.txt"
    key_path.write_text("not-base64", encoding="utf-8")
    with pytest.raises(LedgerExportContractError, match="invalid_key_file"):
        load_key_from_file(key_path)
