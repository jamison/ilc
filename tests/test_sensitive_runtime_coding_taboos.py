from __future__ import annotations

from tools.check_sensitive_runtime_coding_taboos import find_violations


def test_sensitive_runtime_coding_taboos_guardrail() -> None:
    violations = find_violations()
    assert violations == []
