from pathlib import Path


SEQUENCE_LOCK = Path("docs/specs/ilc_phase_1233_1240_sequence_lock_v0.1.md")


def _lock_text() -> str:
    return SEQUENCE_LOCK.read_text(encoding="utf-8")


def test_sequence_lock_file_exists() -> None:
    assert SEQUENCE_LOCK.exists()
    assert SEQUENCE_LOCK.read_text(encoding="utf-8").strip()


def test_previous_window_closure_verdict_recorded() -> None:
    assert "window_1225_1232_closure_gate_verdict=pass" in _lock_text()


def test_phase_1233_sequence_lock_token_present() -> None:
    assert "window_1233_1240_sequence_lock_committed" in _lock_text()


def test_immutable_diagnostic_sha_recorded() -> None:
    assert (
        "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56"
        in _lock_text()
    )


def test_genesis_v0_1_root_hash_recorded() -> None:
    assert (
        "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
        in _lock_text()
    )


def test_cdl_087_not_ratified_token_recorded() -> None:
    text = _lock_text()
    assert "cdl_087_not_ratified_phase_1228" in text
    assert "OPEN / PRELOCKED / NOT RATIFIED" in text


def test_v0_2_signing_deferral_recorded() -> None:
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in _lock_text()


def test_sensitive_phase_boundaries_recorded() -> None:
    text = _lock_text()
    assert "| 1233 | Window sequence lock | **SENSITIVE** |" in text
    assert "| 1240 | Window closure gate | **SENSITIVE** |" in text
    assert "GO Phase 1235" in text
    assert "GO Phase 1236" in text
