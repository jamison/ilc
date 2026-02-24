from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = ROOT / "tests"


def _iter_test_files() -> list[Path]:
    return sorted(
        p for p in TESTS_DIR.glob("test_*.py") if p.name != Path(__file__).name
    )


def _find_pattern_matches(pattern: str) -> list[str]:
    regex = re.compile(pattern, flags=re.MULTILINE | re.DOTALL)
    matches: list[str] = []
    for path in _iter_test_files():
        text = path.read_text(encoding="utf-8")
        if regex.search(text):
            matches.append(str(path.relative_to(ROOT)))
    return matches


def test_no_silent_head_fallback_in_tests() -> None:
    offenders = sorted(
        set(
            _find_pattern_matches(r'return\s+["\']HEAD["\']')
            + _find_pattern_matches(r'or\s+["\']HEAD["\']')
        )
    )
    assert offenders == []


def test_no_swallowed_broad_exceptions_in_tests() -> None:
    offenders = _find_pattern_matches(r"except\s+Exception\s*:\s*\n\s*pass")
    assert offenders == []


def test_no_assert_true_placeholders_in_tests() -> None:
    offenders = _find_pattern_matches(r"^\s*assert\s+True\b")
    assert offenders == []
