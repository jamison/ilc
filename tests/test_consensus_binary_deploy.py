from __future__ import annotations

from pathlib import Path

import pytest

from ilc_core.consensus import binary_paths
from ilc_core.identity import bls_backend, first_run_provisioning
from ilc_core.node import operator_init_runtime
from ilc_core.validator import endpoint_rotation_runtime


def _executable(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    path.chmod(0o700)
    return path


def test_installed_consensus_binary_uses_home_ilc_bin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "home"
    helper = _executable(home / ".ilc" / "bin" / "bls_verify_digest")
    monkeypatch.delenv("ILC_CONSENSUS_BIN_DIR", raising=False)
    monkeypatch.setattr(Path, "home", lambda: home)

    assert binary_paths.installed_consensus_binary_command("bls_verify_digest") == (
        str(helper),
    )


def test_installed_consensus_binary_env_dir_takes_precedence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "home"
    env_dir = tmp_path / "managed-bin"
    home_helper = _executable(home / ".ilc" / "bin" / "keygen")
    env_helper = _executable(env_dir / "keygen")
    monkeypatch.setenv("ILC_CONSENSUS_BIN_DIR", str(env_dir))
    monkeypatch.setattr(Path, "home", lambda: home)

    assert binary_paths.installed_consensus_binary_command("keygen") == (
        str(env_helper),
    )


def test_installed_consensus_binary_rejects_path_like_name() -> None:
    with pytest.raises(ValueError, match="consensus_binary_name_invalid"):
        binary_paths.installed_consensus_binary_command("../keygen")


def test_installed_consensus_binary_rejects_unknown_or_dot_names() -> None:
    for name in (".", "..", "not_an_ilc_helper"):
        with pytest.raises(ValueError, match="consensus_binary_name_invalid"):
            binary_paths.installed_consensus_binary_command(name)


def test_bls_verify_auto_discovers_installed_binary_before_repo_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    helper = _executable(tmp_path / "bls_verify_digest")
    monkeypatch.delenv("ILC_BLS_VERIFY_COMMAND", raising=False)
    monkeypatch.setenv("ILC_CONSENSUS_BIN_DIR", str(tmp_path))
    monkeypatch.setattr(bls_backend.shutil, "which", lambda _name: None)

    assert bls_backend._resolve_bls_verify_command() == [str(helper)]


def test_bls_verify_auto_prefers_installed_binary_before_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    installed = _executable(tmp_path / "installed" / "bls_verify_digest")
    path_binary = _executable(tmp_path / "path" / "bls_verify_digest")
    monkeypatch.delenv("ILC_BLS_VERIFY_COMMAND", raising=False)
    monkeypatch.setenv("ILC_CONSENSUS_BIN_DIR", str(installed.parent))
    monkeypatch.setattr(bls_backend.shutil, "which", lambda _name: str(path_binary))

    assert bls_backend._resolve_bls_verify_command() == [str(installed)]


def test_bls_verify_env_override_rejects_wrappers_and_wrong_names(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    wrapper = _executable(tmp_path / "wrapper")
    helper = _executable(tmp_path / "bls_verify_digest")
    monkeypatch.setenv("ILC_BLS_VERIFY_COMMAND", f"{helper} --unexpected")
    assert bls_backend._resolve_bls_verify_command() is None

    monkeypatch.setenv("ILC_BLS_VERIFY_COMMAND", str(wrapper))
    assert bls_backend._resolve_bls_verify_command() is None


def test_onboarding_discovers_installed_keygen_and_invite_pop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    keygen = _executable(tmp_path / "keygen")
    invite_pop = _executable(tmp_path / "invite_pop_bls")
    monkeypatch.delenv("ILC_ONBOARDING_BLS_KEYGEN_COMMAND", raising=False)
    monkeypatch.delenv("ILC_ONBOARDING_BLS_POP_COMMAND", raising=False)
    monkeypatch.setenv("ILC_CONSENSUS_BIN_DIR", str(tmp_path))

    assert first_run_provisioning._configured_keygen_command() == [str(keygen)]
    assert first_run_provisioning._configured_invite_pop_command() == [str(invite_pop)]


def test_operator_init_discovers_installed_keygen_and_assertion_signer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    keygen = _executable(tmp_path / "keygen")
    signer = _executable(tmp_path / "validator_endpoint_assertion_bls")
    monkeypatch.setenv("ILC_CONSENSUS_BIN_DIR", str(tmp_path))

    assert operator_init_runtime._default_bls_keygen_command() == (str(keygen),)
    assert operator_init_runtime._default_bls_sign_command() == (str(signer),)


def test_operator_init_keygen_empty_stdout_raises_stable_error(tmp_path: Path) -> None:
    helper = tmp_path / "keygen"
    secret_path = tmp_path / "signing_key.hex"
    helper.write_text(
        "#!/bin/sh\n"
        "printf '%064d\\n' 1 > \"$2\"\n"
        "exit 0\n",
        encoding="utf-8",
    )
    helper.chmod(0o700)

    with pytest.raises(ValueError, match="operator_init_bls_keygen_no_stdout"):
        operator_init_runtime._generate_bls_keypair_external(
            command=(str(helper),),
            secret_path=secret_path,
        )


def test_endpoint_rotation_discovers_installed_assertion_signer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    signer = _executable(tmp_path / "validator_endpoint_assertion_bls")
    monkeypatch.setenv("ILC_CONSENSUS_BIN_DIR", str(tmp_path))

    assert endpoint_rotation_runtime._default_bls_sign_command() == (str(signer),)
