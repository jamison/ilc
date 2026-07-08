from pathlib import Path


SCRIPT = Path("tools/scripts/generate_public_mirror.sh")


def test_public_mirror_exclusion_builder_reads_full_history() -> None:
    content = SCRIPT.read_text(encoding="utf-8")

    assert "PUBLIC_RC_EXCLUDE detection — history-wide and header-anchored only" in content
    assert '"log", "--all", "--name-only", "--format=", "-z"' in content
    assert '"rev-list", "--objects", "--all"' in content
    assert '"cat-file", "--batch"' in content
    assert "_historical_header_marked_paths" in content


def test_public_mirror_exclusion_verifier_checks_historical_blobs() -> None:
    content = SCRIPT.read_text(encoding="utf-8")

    assert "REMAINING_EXCLUDE_BLOBS" in content
    assert "header-marked blobs remain in filtered history" in content
    assert "PUBLIC_RC_EXCLUDE header-marked files remain in filtered working tree" in content


def test_public_mirror_exclusion_scan_is_not_raw_marker_grep() -> None:
    content = SCRIPT.read_text(encoding="utf-8")

    forbidden = (
        'grep -aFi -m 1 -- "PUBLIC_RC_EXCLUDE"',
        "grep -RIl \"PUBLIC_RC_EXCLUDE\"",
        'if "PUBLIC_RC_EXCLUDE" in text',
    )
    for needle in forbidden:
        assert needle not in content


def test_public_mirror_commit_count_guard_is_ratio_based() -> None:
    content = SCRIPT.read_text(encoding="utf-8")

    assert 'MIN_COMMIT_COUNT_AFTER="$((COMMIT_COUNT_BEFORE * 60 / 100))"' in content
    assert '"commit_count_min_required": int(commit_count_min_required)' in content
    assert "commit_count_after_too_low:$COMMIT_COUNT_AFTER:min_required:" in content
