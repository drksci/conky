from pathlib import Path

import pytest

from conky import Vault

AT = "2026-01-01T00:00:00Z"


@pytest.fixture
def keys_dir(tmp_path: Path) -> Path:
    return tmp_path / "keys"


@pytest.fixture
def vault(tmp_path: Path, keys_dir: Path) -> Vault:
    return Vault.init(tmp_path / "vault", keys_dir)
