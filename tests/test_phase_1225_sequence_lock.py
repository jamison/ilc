from pathlib import Path


LOCK = Path("docs/specs/ilc_phase_1225_1232_sequence_lock_v0.1.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")
STATUS = Path("docs/phases/STATUS.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1225_sequence_lock_file_exists_and_token_present():
    text = _read(LOCK)

    assert "GO Phase 1225" in text
    assert "window_1225_1232_sequence_lock_committed" in text
    assert "window_1225_1232_sequence_lock_verdict=pass" in text


def test_phase_1225_records_immutable_anchors_and_fix1_baseline():
    text = _read(LOCK)

    assert "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56" in text
    assert "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c" in text
    assert "052d62b5" in text
    assert "21a5ad86" in text
    assert "e4486d9a" in text


def test_phase_1225_locks_sensitive_boundaries():
    text = _read(LOCK)

    assert "Phase 1227" in text
    assert "GO Phase 1227" in text
    assert "ILC_CDL_MUTATION_AUTHORIZED=1" in text
    assert "ILC_CDL_MUTATION_PHASE=1227" in text
    assert "Phase 1228" in text
    assert "GO Phase 1228" in text
    assert "SENSITIVE even without a CDL register mutation" in text


def test_phase_1225_records_v0_2_skip_default():
    text = _read(LOCK)

    assert "Phase 1230 is skip-default" in text
    assert "v0_2_signing_ceremony_authorized_phase_1230" in text
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in text


def test_phase_1225_records_graph_runtime_location_and_sidecar_defer():
    text = _read(LOCK)

    assert "ilc_core/graph/__init__.py" in text
    assert "ilc_core/graph/agent_graph_projection_runtime.py" in text
    assert "L3 visualization sidecar" in text
    assert "Deferred to Window 1233+" in text


def test_phase_1225_planning_index_and_status_advanced():
    index = _read(PLANNING_INDEX)
    status = _read(STATUS)

    assert "Window 1225-1232" in index
    assert "in progress through Phase" in index or "CLOSED through Phase 1232" in index
    assert "docs/specs/ilc_phase_1225_1232_sequence_lock_v0.1.md" in index
    assert "## Phase 1225" in status
    assert "window_1225_1232_sequence_lock_committed" in status


def test_phase_1225_non_authorization_boundary_present():
    text = _read(LOCK)

    assert "public launch" in text
    assert "public repository publication" in text
    assert "v0.2 signing" in text
    assert "CDL-087 ratification" in text
