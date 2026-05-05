import threading

from ilc_core.network.d2d.http_fetch_transport_runtime import (
    PERSISTENT_RATE_LIMITER_STATE_SAVE_FAILED_TOKEN,
)
from ilc_core.network.d2d.persistent_fetch_rate_limiter_runtime import (
    PERSISTENT_RATE_LIMITER_AUDIT_HARDENING_TOKEN,
    PersistentFetchRateLimiter,
)


def test_persistent_rate_limiter_has_audit_hardening_token():
    assert (
        PERSISTENT_RATE_LIMITER_AUDIT_HARDENING_TOKEN
        == "persistent_rate_limiter_audit_hardened_phase_1217"
    )


def test_persistent_rate_limiter_uses_reentrant_lock():
    limiter = PersistentFetchRateLimiter(limit_per_window=2)
    assert isinstance(limiter._lock, type(threading.RLock()))


def test_persistent_rate_limiter_concurrent_consumption_is_bounded():
    limiter = PersistentFetchRateLimiter(limit_per_window=3)
    results: list[bool] = []
    results_lock = threading.Lock()

    def _consume() -> None:
        allowed = limiter.check_and_consume("agent-concurrent", 7)
        with results_lock:
            results.append(allowed)

    threads = [threading.Thread(target=_consume) for _ in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert results.count(True) == 3
    assert results.count(False) == 17


def test_persistent_rate_limiter_save_failure_token_constant():
    assert PERSISTENT_RATE_LIMITER_STATE_SAVE_FAILED_TOKEN == (
        "persistent_rate_limiter_state_save_failed"
    )
