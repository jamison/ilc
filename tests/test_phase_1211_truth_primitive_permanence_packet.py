from pathlib import Path


PACKET = Path("docs/specs/ilc_truth_primitive_permanence_ratification_packet_1211_v0.1.md")


def _packet_text() -> str:
    return PACKET.read_text(encoding="utf-8")


def test_packet_file_exists():
    assert PACKET.exists()


def test_packet_contains_token():
    assert "truth_primitive_permanence_ratification_packet_committed_phase_1211" in _packet_text()


def test_packet_contains_all_required_sections():
    text = _packet_text()
    for section in (
        "## 2. Primitive Set",
        "## 3. Evidence Bundle",
        "## 4. Ratifier Class",
        "## 5. Event Mechanics",
        "## 6. Threshold",
        "## 7. Sunset Boundary",
        "## 8. Non-Bypass Rule",
    ):
        assert section in text


def test_packet_names_exact_new_seven_and_excludes_star_map():
    text = _packet_text()
    for primitive in (
        "`assert.truth`",
        "`validate.claim`",
        "`contradict.assert`",
        "`refute.claim`",
        "`revise.assert`",
        "`link.claim`",
        "`commit.epoch`",
    ):
        assert primitive in text
    assert "`star.map` is explicitly excluded" in text


def test_packet_records_commit_epoch_consensus_only_exception():
    text = _packet_text()
    assert "commit_epoch_agent_submission_rejected" in text
    assert "`commit.epoch` is a truth primitive but not agent-issuable" in text


def test_packet_records_sunset_and_non_bypass_boundary():
    text = _packet_text()
    assert "Window 1218-1224" in text
    assert "Window 1225-1232 closure" in text
    assert "No public RC claim, public launch claim" in text


def test_packet_ratifier_class_is_not_single_agent():
    text = _packet_text()
    assert "cannot be ratified by a single agent" in text
    assert "At least three distinct Genesis founding/member signers" in text
    assert "At least one external witness signer" in text
