import os
import subprocess
from pathlib import Path

import pytest

from conky import Vault

AT = "2026-01-01T00:00:00Z"
ISOLATION = {
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_TERMINAL_PROMPT": "0",
}
PERSON = {
    f"GIT_{role}_{key}": value
    for role in ("AUTHOR", "COMMITTER")
    for key, value in (("NAME", "plain"), ("EMAIL", "plain@example.com"))
}


def git(cwd: Path, *args: str) -> str:
    """Run plain git in cwd, shut off from the machine's configuration."""
    done = subprocess.run(
        ["git", *args],
        cwd=cwd,
        env={**os.environ, **ISOLATION, **PERSON},
        capture_output=True,
        text=True,
        check=True,
    )
    return done.stdout


def signed_by(cwd: Path, revision: str = "HEAD") -> str:
    """Return the allowed_signers principal whose key signed the revision."""
    signers = (cwd / "keys" / "allowed_signers").resolve()
    return git(
        cwd,
        "-c",
        "gpg.format=ssh",
        "-c",
        f"gpg.ssh.allowedSignersFile={signers}",
        "log",
        "-1",
        "--format=%GS",
        revision,
    ).strip()


@pytest.fixture
def keys_dir(tmp_path: Path) -> Path:
    return tmp_path / "keys"


@pytest.fixture
def vault(tmp_path: Path, keys_dir: Path) -> Vault:
    return Vault.init(tmp_path / "vault", keys_dir)


@pytest.fixture(autouse=True)
def no_detected_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep every test from reaching a model that happens to be set up on this machine."""
    monkeypatch.setenv("CONKY_PROVIDER", "none")
