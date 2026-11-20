"""Pages that ask a model: a provider is a page, an answer is an ordinary recorded write.

Every test talks to a real HTTP server on 127.0.0.1 that speaks the two wire formats.
No test reaches a live provider.
"""

import contextlib
import json
import socket
import threading
import time
from collections.abc import Callable, Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import pytest

from conky import Vault, arch, model
from conky.cli import main
from conky.git import trailers

from .conftest import AT, git, signed_by

SECRET = "sk-test-0123456789abcdef"
PROMPT = "Summarise this request in one sentence: ![[ticket#text]]"
ASKED = "Summarise this request in one sentence: printer jams"


class Stand:
    """A stand-in provider: records every request and answers in either wire format."""

    def __init__(self) -> None:
        self.requests: list[dict[str, Any]] = []
        self.answer: str | Callable[[int], str] = "The printer keeps jamming."
        self.status = 200
        self.delay = 0.0
        self.raw: bytes | None = None
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self.server.daemon_threads = True
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def _handler(self) -> type[BaseHTTPRequestHandler]:
        stand = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                size = int(self.headers["Content-Length"])
                body = json.loads(self.rfile.read(size))
                headers = {k.lower(): v for k, v in self.headers.items()}
                stand.requests.append({"path": self.path, "headers": headers, "body": body})
                with contextlib.suppress(OSError):
                    self._reply()

            def _reply(self) -> None:
                time.sleep(stand.delay)
                text = stand.answer
                if callable(text):
                    text = text(len(stand.requests))
                if self.path.endswith("/messages"):
                    data = {
                        "content": [
                            {"type": "thinking", "thinking": "hm"},
                            {"type": "text", "text": text},
                        ],
                        "usage": {"input_tokens": 11, "output_tokens": 7},
                    }
                else:
                    data = {
                        "choices": [{"message": {"content": text}}],
                        "usage": {"prompt_tokens": 11, "completion_tokens": 7},
                    }
                payload = stand.raw if stand.raw is not None else json.dumps(data).encode()
                self.send_response(stand.status)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args: Any) -> None:
                pass

        return Handler

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture(autouse=True)
def local_network(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("no_proxy", "NO_PROXY"):
        monkeypatch.setenv(name, "127.0.0.1")
    monkeypatch.delenv("CONKY_SECRET_HELPER", raising=False)


@pytest.fixture
def stand() -> Iterator[Stand]:
    found = Stand()
    yield found
    found.stop()


def w(vault: Vault, page: str, changes: dict, actor: str = "alice"):
    return vault.write(page, changes, None, actor=actor, at=AT)


def provider(vault: Vault, stand: Stand, api: str = "openai", name: str = "helper", **extra: Any):
    path = "/v1/messages" if api == "anthropic" else "/v1/chat/completions"
    fields = {"api": api, "url": stand.url + path, "model": "test-model", **extra}
    assert w(vault, name, fields).ok


def watch(provider_name: str = "helper", prompt: str = PROMPT, into: str = "summary") -> list[dict]:
    ask = {"provider": provider_name, "prompt": prompt, "into": into}
    return [{"on": "ticket", "when": "other.status == 'new'", "ask": ask}]


def desk(vault: Vault, **extra: Any) -> None:
    """A ticket that is not new yet, and a desk page that asks about new tickets."""
    assert w(vault, "ticket", {"status": "old", "text": "printer jams"}).ok
    assert w(vault, "desk", {"summary": "", "watch": watch(), **extra}).ok


def new_ticket(vault: Vault, **changes: Any):
    return w(vault, "ticket", {"status": "new", **changes})


def commits(vault: Vault) -> list[str]:
    return git(vault.path, "log", "--reverse", "--format=%H", "main").split()


def message(vault: Vault, revision: str = "HEAD") -> tuple[str, dict[str, str]]:
    text = git(vault.path, "log", "-1", "--format=%B", revision)
    return text, trailers(text)


def last_refusal(vault: Vault, page: str = "desk") -> dict[str, str]:
    for commit in reversed(commits(vault)):
        _, found = message(vault, commit)
        if found["Kind"] == "refused" and found["Page"] == page:
            return found
    raise AssertionError(f"no refusal on {page}")


@arch.holds("flow.ask.model")
def test_an_ask_entry_answers_as_a_signed_write_by_the_asking_page(
    vault: Vault, stand: Stand
) -> None:
    provider(vault, stand, max_tokens=50)
    desk(vault)
    assert new_ticket(vault).ok
    assert len(stand.requests) == 1
    assert stand.requests[0]["body"]["messages"] == [{"role": "user", "content": ASKED}]
    found = vault.read("desk").fields
    assert found["summary"] == "The printer keeps jamming."
    text, tags = message(vault)
    assert signed_by(vault.path) == "desk@conky"
    assert git(vault.path, "log", "-1", "--format=%an", "HEAD").strip() == "desk"
    assert tags == {
        "Kind": "write",
        "Page": "desk",
        "Model": "helper",
        "Model-Name": "test-model",
        "Tokens-In": "11",
        "Tokens-Out": "7",
        "Read": "ticket",
        "Cause": commits(vault)[-2],
    }
    assert text.splitlines()[0] == "write desk"
    assert text.split("\n\n")[1] == ASKED
    vault.verify()


@pytest.mark.parametrize(
    ("api", "path", "header", "expected"),
    [
        ("openai", "/v1/chat/completions", "authorization", "Bearer " + SECRET),
        ("anthropic", "/v1/messages", "x-api-key", SECRET),
    ],
)
@arch.holds("flow.ask.model")
def test_each_wire_format_sends_the_right_request_and_reads_the_answer(
    vault: Vault,
    stand: Stand,
    monkeypatch: pytest.MonkeyPatch,
    api: str,
    path: str,
    header: str,
    expected: str,
) -> None:
    monkeypatch.setenv("CONKY_SECRET_HELPER", SECRET)
    provider(vault, stand, api, secret="helper")
    desk(vault)
    new_ticket(vault)
    sent = stand.requests[0]
    assert sent["path"] == path
    assert sent["headers"][header] == expected
    assert sent["headers"]["content-type"] == "application/json"
    messages = [{"role": "user", "content": ASKED}]
    if api == "openai":
        assert sent["body"] == {"model": "test-model", "messages": messages}
        assert "x-api-key" not in sent["headers"]
    else:
        assert sent["body"] == {"model": "test-model", "max_tokens": 1024, "messages": messages}
        assert sent["headers"]["anthropic-version"] == "2023-06-01"
        assert "authorization" not in sent["headers"]
    assert vault.read("desk").fields["summary"] == "The printer keeps jamming."
    assert message(vault)[1]["Tokens-In"] == "11" and message(vault)[1]["Tokens-Out"] == "7"


@arch.holds("flow.ask.model")
def test_the_answer_names_each_page_that_was_embedded_once_in_order(
    vault: Vault, stand: Stand
) -> None:
    provider(vault, stand)
    assert w(vault, "other", {"x": 1}).ok
    assert w(vault, "ticket", {"status": "old", "text": "printer jams"}).ok
    prompt = (
        "![[other#x]] ![[ticket#text]] ![[other#x]] ![[ticket#status]] ![[ghost#y]] ![[ticket#no]]"
    )
    assert w(vault, "desk", {"summary": "", "watch": watch(prompt=prompt)}).ok
    new_ticket(vault)
    text, tags = message(vault)
    assert tags["Read"] == "other, ticket"
    assert text.count("\nRead: ") == 2
    assert vault.log()[-1].endswith("model helper read other, ticket")
    vault.verify()


def test_an_embed_with_no_field_reads_the_body_and_the_answer_names_the_page(
    vault: Vault, stand: Stand
) -> None:
    provider(vault, stand)
    assert vault.write("log", {"n": 1}, "first line\nsecond line\n", actor="alice", at=AT).ok
    assert w(vault, "ticket", {"status": "old"}).ok
    prompt = "Log: ![[log]] and ![[log#n]]"
    assert w(vault, "desk", {"summary": "", "watch": watch(prompt=prompt)}).ok
    new_ticket(vault)
    sent = stand.requests[0]["body"]["messages"][0]["content"]
    assert sent == "Log: first line\nsecond line\n and 1"
    assert message(vault)[1]["Read"] == "log"
    assert vault.log()[-1].endswith("model helper read log")
    vault.verify()


def test_a_changed_body_is_a_changed_question_and_an_unchanged_one_is_not(
    vault: Vault, stand: Stand
) -> None:
    provider(vault, stand)
    assert vault.write("log", {}, "one\n", actor="alice", at=AT).ok
    assert w(vault, "ticket", {"status": "old"}).ok
    assert w(vault, "desk", {"summary": "", "watch": watch(prompt="![[log]]")}).ok
    new_ticket(vault)
    assert len(stand.requests) == 1
    assert w(vault, "log", {"n": 2}).ok
    assert w(vault, "ticket", {"note": "again"}).ok
    assert len(stand.requests) == 1
    assert vault.write("log", {}, "two\n", actor="alice", at=AT).ok
    assert w(vault, "ticket", {"note": "once more"}).ok
    assert len(stand.requests) == 2
    assert stand.requests[1]["body"]["messages"][0]["content"] == "two\n"


def test_a_missing_page_or_an_empty_body_embeds_nothing_and_is_not_read(
    vault: Vault, stand: Stand
) -> None:
    provider(vault, stand)
    assert w(vault, "empty", {"n": 1}).ok
    assert w(vault, "ticket", {"status": "old"}).ok
    prompt = "[![[ghost]]|![[empty]]]"
    assert w(vault, "desk", {"summary": "", "watch": watch(prompt=prompt)}).ok
    new_ticket(vault)
    assert stand.requests[0]["body"]["messages"][0]["content"] == "[|]"
    assert "Read" not in message(vault)[1]


def test_an_answer_to_a_prompt_with_no_embeds_has_no_read_trailer(
    vault: Vault, stand: Stand
) -> None:
    provider(vault, stand)
    assert w(vault, "ticket", {"status": "old"}).ok
    assert w(vault, "desk", {"summary": "", "watch": watch(prompt="Say hello.")}).ok
    new_ticket(vault)
    assert "Read" not in message(vault)[1]
    assert vault.log()[-1].endswith("model helper")


def test_an_answer_refused_by_a_rule_still_says_what_was_read(vault: Vault, stand: Stand) -> None:
    provider(vault, stand)
    desk(vault, rules=["page.summary.size() <= 5"])
    new_ticket(vault)
    assert last_refusal(vault)["Read"] == "ticket"


@arch.holds("law.provider.page")
def test_changing_provider_is_editing_one_page(vault: Vault, stand: Stand) -> None:
    provider(vault, stand)
    desk(vault)
    new_ticket(vault)
    assert stand.requests[0]["path"] == "/v1/chat/completions"
    provider(vault, stand, "anthropic")
    assert w(vault, "ticket", {"text": "scanner jams"}).ok
    assert [r["path"] for r in stand.requests] == ["/v1/chat/completions", "/v1/messages"]
    assert message(vault)[1]["Model"] == "helper"
    assert vault.read("desk").fields["summary"] == "The printer keeps jamming."


def test_max_tokens_is_sent_in_both_formats(vault: Vault, stand: Stand) -> None:
    provider(vault, stand, "anthropic", name="claude", max_tokens=50)
    provider(vault, stand, "openai", max_tokens=60)
    desk(vault)
    assert w(vault, "desk", {"watch": watch() + watch("claude", into="other")}).ok
    new_ticket(vault)
    assert sorted(r["body"]["max_tokens"] for r in stand.requests) == [50, 60]


def test_a_secret_comes_from_the_environment(
    vault: Vault, stand: Stand, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CONKY_SECRET_OPENROUTER", SECRET)
    provider(vault, stand, secret="openrouter")
    desk(vault)
    assert new_ticket(vault).ok
    assert stand.requests[0]["headers"]["authorization"] == f"Bearer {SECRET}"


def test_a_secret_comes_from_a_file_in_the_key_directory(
    vault: Vault, stand: Stand, keys_dir: Path
) -> None:
    keys_dir.mkdir(parents=True, exist_ok=True)
    (keys_dir / "openrouter.secret").write_text(SECRET + "\n")
    provider(vault, stand, secret="openrouter")
    desk(vault)
    assert new_ticket(vault).ok
    assert stand.requests[0]["headers"]["authorization"] == f"Bearer {SECRET}"


def test_the_environment_wins_over_the_file(
    vault: Vault, stand: Stand, keys_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    keys_dir.mkdir(parents=True, exist_ok=True)
    (keys_dir / "openrouter.secret").write_text("from-the-file")
    monkeypatch.setenv("CONKY_SECRET_OPENROUTER", "from-the-environment")
    provider(vault, stand, secret="openrouter")
    desk(vault)
    new_ticket(vault)
    assert stand.requests[0]["headers"]["authorization"] == "Bearer from-the-environment"


@arch.holds("law.provider.page")
def test_a_secret_appears_nowhere_in_the_vault(
    vault: Vault, stand: Stand, keys_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    keys_dir.mkdir(parents=True, exist_ok=True)
    (keys_dir / "filed.secret").write_text("filed-" + SECRET)
    monkeypatch.setenv("CONKY_SECRET_ENVIRONED", "environ-" + SECRET)
    provider(vault, stand, secret="filed")
    provider(vault, stand, name="other", secret="environed", model="other-model")
    desk(vault)
    assert w(vault, "desk", {"watch": watch() + watch("other", into="other")}).ok
    assert new_ticket(vault).ok
    assert len(stand.requests) == 2
    assert w(vault, "desk", {"watch": watch("ghost")}).ok
    new_ticket(vault, text="again")
    for found in vault.path.rglob("*"):
        if found.is_file():
            assert SECRET.encode() not in found.read_bytes(), found
    assert SECRET not in git(vault.path, "log", "--all", "-p", "--format=fuller")


def test_a_provider_without_a_secret_sends_no_credential(vault: Vault, stand: Stand) -> None:
    provider(vault, stand)
    provider(vault, stand, "anthropic", name="claude")
    desk(vault)
    assert w(vault, "desk", {"watch": watch() + watch("claude", into="other")}).ok
    assert new_ticket(vault).ok
    assert len(stand.requests) == 2
    for sent in stand.requests:
        assert "authorization" not in sent["headers"] and "x-api-key" not in sent["headers"]


@arch.holds("flow.ask.model")
def test_a_settled_question_is_not_asked_twice_and_a_changed_one_is(
    vault: Vault, stand: Stand
) -> None:
    provider(vault, stand)
    desk(vault)
    new_ticket(vault)
    assert len(stand.requests) == 1
    before = len(commits(vault))
    assert w(vault, "ticket", {"note": "unrelated"}).ok
    assert len(stand.requests) == 1
    assert len(commits(vault)) == before + 1
    assert message(vault)[1]["Page"] == "ticket"
    stand.answer = "Now it is the scanner."
    assert w(vault, "ticket", {"text": "scanner jams"}).ok
    assert len(stand.requests) == 2
    assert stand.requests[1]["body"]["messages"][0]["content"].endswith("scanner jams")
    assert vault.read("desk").fields["summary"] == "Now it is the scanner."


def test_the_depth_cap_still_ends_a_question_that_never_settles(vault: Vault, stand: Stand) -> None:
    provider(vault, stand)
    stand.answer = lambda n: f"answer {n}"
    again = {"provider": "helper", "prompt": "again ![[desk#summary]]", "into": "summary"}
    entry = {"on": "desk", "when": "true", "ask": again}
    assert w(vault, "desk", {"summary": "", "watch": [entry]}).ok
    assert len(stand.requests) == 12
    assert "cycle" in last_refusal(vault)["Reason"]
    vault.verify()


def test_an_answer_that_breaks_a_rule_is_a_refusal_and_the_field_is_unchanged(
    vault: Vault, stand: Stand
) -> None:
    provider(vault, stand)
    desk(vault, rules=["page.summary.size() <= 5"])
    new_ticket(vault)
    assert len(stand.requests) == 2
    refusal = last_refusal(vault)
    assert refusal["Reason"].startswith("rule: page.summary.size() <= 5")
    assert refusal["Model"] == "helper"
    assert vault.read("desk").fields == {"summary": ""}
    vault.verify()


def broken(stand: Stand, how: str, monkeypatch: pytest.MonkeyPatch) -> tuple[str, list[str]]:
    """Break the provider setup one way; return the provider asked and what the reason says."""
    if how == "server-error":
        stand.status = 500
        return "helper", ["HTTP 500", "then ask again"]
    if how == "timeout":
        stand.delay = 1.0
        monkeypatch.setattr(model, "TIMEOUT", 0.2)
        return "helper", ["cannot reach", "then ask again"]
    if how == "not-an-answer":
        stand.raw = b'{"unexpected": true}'
        return "helper", ["no answer text", "check that api matches"]
    if how == "not-json":
        stand.raw = b"<html>"
        return "helper", ["did not send JSON", "check that its url"]
    if how == "missing-page":
        return "ghost", ["does not exist", "write it with api, url, model and secret"]
    if how == "missing-secret":
        return "helper", ["set CONKY_SECRET_NOKEY", "nokey.secret in the key directory"]
    raise AssertionError(how)


@pytest.mark.parametrize(
    "how",
    [
        "server-error",
        "timeout",
        "not-an-answer",
        "not-json",
        "missing-page",
        "missing-secret",
        "unreachable",
    ],
)
@arch.holds("law.reflex.free", "flow.ask.model")
def test_every_failure_is_a_model_refusal_and_nothing_else_is_affected(
    vault: Vault, stand: Stand, monkeypatch: pytest.MonkeyPatch, how: str
) -> None:
    extra = {"secret": "nokey"} if how == "missing-secret" else {}
    provider(vault, stand, **extra)
    if how == "unreachable":
        with socket.socket() as taken:
            taken.bind(("127.0.0.1", 0))
            closed = taken.getsockname()[1]
        assert w(vault, "helper", {"url": f"http://127.0.0.1:{closed}/v1/chat/completions"}).ok
        name, words = "helper", ["cannot reach", "then ask again"]
    else:
        name, words = broken(stand, how, monkeypatch)
    assert w(vault, "ticket", {"status": "old", "text": "printer jams"}).ok
    for other in ("aaa", "zzz"):
        seen = {"on": "ticket", "when": "true", "set": {"seen": "other.status"}}
        assert w(vault, other, {"watch": [seen]}).ok
    assert w(vault, "desk", {"summary": "", "watch": watch(name)}).ok
    assert new_ticket(vault).ok
    refusal = last_refusal(vault)
    assert refusal["Reason"].startswith("model: ")
    assert all(word in refusal["Reason"] for word in words)
    assert vault.read("ticket").fields["status"] == "new"
    assert vault.read("aaa").fields == {"seen": "new"}
    assert vault.read("zzz").fields == {"seen": "new"}
    assert vault.read("desk").fields["summary"].startswith("No model was around")
    assert refusal["Page"] == "desk"
    vault.verify()


@arch.holds("flow.vault.clone")
def test_history_verifies_and_reads_with_no_network_and_no_secrets(
    vault: Vault, stand: Stand, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CONKY_SECRET_HELPER", SECRET)
    provider(vault, stand, secret="helper")
    desk(vault)
    new_ticket(vault)
    asked = len(stand.requests)
    stand.stop()
    monkeypatch.delenv("CONKY_SECRET_HELPER")
    git(tmp_path, "clone", "-q", str(vault.path), "copy")
    copy = Vault(tmp_path / "copy", tmp_path / "no-such-keys")
    copy.verify()
    assert copy.read("desk").fields["summary"] == "The printer keeps jamming."
    assert copy.log() == vault.log()
    assert vault.log()[-1].endswith("model helper read ticket")
    assert " cause " in vault.log()[-1]
    assert len(stand.requests) == asked
    assert not (tmp_path / "no-such-keys").exists()


def run(tmp_path: Path, *args: str) -> int:
    return main(["--vault", str(tmp_path / "v"), "--keys", str(tmp_path / "k"), *args])


def test_conky_ask_writes_the_answer_as_the_actor(
    tmp_path: Path, stand: Stand, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--keys", str(tmp_path / "k"), "init", str(tmp_path / "v")]) == 0
    fields = ["api=openai", f"url={stand.url}/v1/chat/completions", "model=test-model"]
    assert run(tmp_path, "write", "helper", *fields, "--as", "alice") == 0
    assert run(tmp_path, "write", "ticket", "text=printer jams", "--as", "alice") == 0
    capsys.readouterr()
    ask = ["ask", "desk", "summary", "--provider", "helper", "--as", "bob"]
    assert run(tmp_path, *ask, "--prompt", PROMPT) == 0
    assert capsys.readouterr().out.startswith("written (commit ")
    assert stand.requests[0]["body"]["messages"][0]["content"] == ASKED
    vault = Vault(tmp_path / "v", tmp_path / "k")
    assert vault.read("desk").fields["summary"] == "The printer keeps jamming."
    assert signed_by(vault.path) == "bob@conky"
    text, tags = message(vault)
    assert tags["Model"] == "helper" and tags["Model-Name"] == "test-model" and ASKED in text
    assert run(tmp_path, "verify") == 0
    stand.stop()
    capsys.readouterr()
    assert run(tmp_path, *ask, "--prompt", "again") == 0
    seen = capsys.readouterr()
    assert "No model answered. To give Conky one" in seen.err
    assert "No model was around to answer" in seen.out
    assert "model: cannot reach" in message(vault, "HEAD~1")[1]["Reason"]
    with pytest.raises(SystemExit) as stopped:
        run(tmp_path, "ask", "desk", "summary", "--provider", "ghost", "--as", "bob")
    assert stopped.value.code == 2
    assert run(tmp_path, "verify") == 0


def test_ask_that_breaks_a_rule_exits_non_zero_and_leaves_the_page(
    tmp_path: Path, stand: Stand, capsys: pytest.CaptureFixture[str]
) -> None:
    main(["--keys", str(tmp_path / "k"), "init", str(tmp_path / "v")])
    fields = ["api=openai", f"url={stand.url}/v1/chat/completions", "model=test-model"]
    run(tmp_path, "write", "helper", *fields, "--as", "alice")
    run(
        tmp_path,
        "write",
        "desk",
        'rules=["page.summary.size() <= 3"]',
        "summary=''",
        "--as",
        "alice",
    )
    capsys.readouterr()
    ask = ["ask", "desk", "summary", "--provider", "helper", "--prompt", "q", "--as", "alice"]
    assert run(tmp_path, *ask) == 1
    assert "rule: page.summary.size() <= 3" in capsys.readouterr().err
    assert Vault(tmp_path / "v", tmp_path / "k").read("desk").fields == {"summary": ""}


@pytest.mark.parametrize(
    "entry",
    [
        {
            "on": "ticket",
            "when": "true",
            "set": {"a": "1"},
            "ask": {"provider": "helper", "prompt": "q", "into": "a"},
        },
        {"on": "ticket", "when": "true", "ask": {"provider": "helper", "prompt": "q"}},
        {"on": "ticket", "when": "true", "ask": {"provider": "helper", "into": "a"}},
        {"on": "ticket", "when": "true", "ask": {"prompt": "q", "into": "a", "otherwise": 3}},
        {
            "on": "ticket",
            "when": "true",
            "ask": {"provider": "helper", "prompt": "q", "into": "a", "x": "y"},
        },
        {
            "on": "ticket",
            "when": "true",
            "ask": {"provider": "Bad Name", "prompt": "q", "into": "a"},
        },
        {"on": "ticket", "when": "true", "ask": {"provider": "helper", "prompt": "q", "into": ""}},
        {"on": "ticket", "when": "true", "ask": {"prompt": "q", "writes": "Bad Name"}},
        {"on": "ticket", "when": "true", "ask": {"prompt": "q", "writes": 3}},
        {"on": "ticket", "when": "true", "ask": "q"},
        {"on": "ticket", "when": "true"},
    ],
)
def test_a_malformed_ask_entry_is_a_shape_refusal(vault: Vault, entry: dict) -> None:
    result = w(vault, "desk", {"watch": [entry]})
    assert not result.ok and result.reason is not None
    assert (
        result.reason.startswith("shape: ") and "ask (prompt, with into or writes" in result.reason
    )
    assert not (vault.pages_dir / "desk.md").exists()


@pytest.mark.parametrize(
    ("fields", "why"),
    [
        ({"api": "gemini"}, "api must be one of"),
        ({"url": "ftp://x"}, "url must be an http or https address"),
        ({"model": ""}, "model must be"),
        ({"secret": "sk-Live Key"}, "secret must be the name of a secret"),
        ({"max_tokens": 0}, "max_tokens must be a positive whole number"),
        ({"max_tokens": True}, "max_tokens must be a positive whole number"),
    ],
)
def test_a_malformed_provider_page_is_named_and_asks_for_the_field_to_be_corrected(
    vault: Vault, stand: Stand, fields: dict, why: str
) -> None:
    provider(vault, stand)
    assert w(vault, "helper", fields).ok
    desk(vault)
    new_ticket(vault)
    reason = last_refusal(vault)["Reason"]
    assert reason.startswith("model: provider page 'helper' is malformed") and why in reason
    assert not stand.requests


def test_a_rule_can_constrain_provider_pages(vault: Vault, stand: Stand) -> None:
    assert w(
        vault, "providers", {"rules": [{"each": "page.model == 'approved'"}], "model": "approved"}
    ).ok
    result = w(vault, "helper", {"within": "providers", "api": "openai", "model": "other"})
    assert not result.ok and result.reason is not None and "page.model" in result.reason
