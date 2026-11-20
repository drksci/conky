"""Nothing malformed lands: each wrong form under tests/invalid/ is refused when it is written."""

from pathlib import Path

import pytest

from conky import Vault
from conky.page import load_value

from .conftest import AT

FORMS = sorted((Path(__file__).parent / "invalid").glob("*.yaml"))


def w(vault: Vault, page: str, changes: dict):
    return vault.write(page, changes, None, actor="alice", at=AT)


def test_there_are_wrong_forms_to_try() -> None:
    assert len(FORMS) >= 10


@pytest.mark.parametrize("path", FORMS, ids=lambda p: p.stem)
def test_a_wrong_form_is_refused_when_written(path: Path, vault: Vault) -> None:
    plan = load_value(path.read_text(encoding="utf-8"))
    for page, fields in plan["pages"].items():
        assert w(vault, page, fields).ok, f"{path.stem}: starting page {page} was refused"
    attempt = w(vault, plan["write"]["page"], plan["write"]["set"])
    assert not attempt.ok, f"{path.stem} was accepted"
    assert attempt.reason is not None and attempt.reason.split(":")[0] == plan["refused"]


def test_a_refusal_names_the_field_to_read_on_the_other_thing(vault: Vault) -> None:
    plain = w(vault, "den", {"cash": 50, "rules": ["space.cash >= 20"]})
    assert not plain.ok and plain.reason is not None and plain.reason.startswith("rule")
    assert (
        "space.cash does not exist here: this page has cash, read it as page.cash" in plain.reason
    )
    w(vault, "hut", {"owner": "sam"})
    w(vault, "kid", {"within": "hut", "cash": 5})
    refused = w(vault, "hut", {"rules": [{"each": "space.cash >= 20"}]})
    assert not refused.ok and refused.reason is not None and refused.reason.startswith("rule")
    assert "page.cash" in refused.reason and "kid" in refused.reason
    assert "activation" not in refused.reason and "Error" not in refused.reason


def test_a_rule_that_binds_a_variable_is_accepted(vault: Vault) -> None:
    result = w(vault, "den", {"cash": 1, "rules": ["[1, 2].all(i, i <= page.cash + 1)"]})
    assert result.ok, result.reason
