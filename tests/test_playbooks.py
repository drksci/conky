"""Every file in tests/playbooks/ is a test: a short scenario run by tests/playbook.py."""

import sys
from pathlib import Path

import pytest

from conky import Vault

from . import playbook
from .test_pages import Stand

FILES = sorted((Path(__file__).parent / "playbooks").glob("*.yaml"))


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.stem)
def test_playbook(
    path: Path, vault: Vault, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stand = Stand(tmp_path / "stand")
    monkeypatch.setenv("CONKY_COMMAND_STAND", f"{sys.executable} {stand.folder / 'model.py'}")
    playbook.run(path, vault, stand)
