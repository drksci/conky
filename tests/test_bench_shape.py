"""The shape of a run: a hand-made vault, a conversation and a policy, with known counts."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from bench import record, shape

ROOT = Path(__file__).resolve().parent.parent
GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]


def commit(vault: Path, message: str) -> None:
    subprocess.run(["git", "-C", str(vault), "add", "-A"], check=True)
    subprocess.run(
        [*GIT, "-C", str(vault), "commit", "--allow-empty", "-q", "-m", message], check=True
    )


def page(vault: Path, name: str, text: str) -> None:
    (vault / "pages" / f"{name}.md").write_text(text, encoding="utf-8")


def run_folder(root: Path, arm: str) -> Path:
    folder = root / "trail" / arm / "full" / "seed-1"
    folder.mkdir(parents=True)
    (folder / "run.json").write_text(json.dumps({"arm": arm, "seed": 1}), encoding="utf-8")
    return folder


def hand_made(root: Path) -> Path:
    folder = run_folder(root, "conky")
    vault = folder / "workdir" / "vault"
    (vault / "pages").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(vault)], check=True)
    page(vault, "den", "---\n---\nThe den.")
    page(vault, "meter", "---\napi: openai\n---\nThe model.")
    commit(vault, "write den\n\nKind: write")
    page(
        vault,
        "hero",
        "---\nwithin: den\nwatch:\n- on: screen\n  when: 'true'\n  ask:\n    into: keys\n"
        "    provider: meter\n    writes: den\n    prompt: go\n---\nHero body.",
    )
    page(vault, "screen", "---\n---\nabc")
    commit(vault, "write hero\n\nKind: write")
    page(vault, "note", "---\nwithin: den\n---\nA note.")
    commit(vault, "write note\n\nKind: write")
    commit(vault, "write den\n\nKind: refused")
    return folder


def register(monkeypatch, harness: str, declared: dict) -> None:
    monkeypatch.setattr(
        record, "manifest", lambda name: {"shape": declared} if name == harness else {}
    )


def test_a_vault_has_its_pages_and_links_at_start_and_end(tmp_path: Path, monkeypatch) -> None:
    register(monkeypatch, "conky", {"kind": "vault", "path": "workdir/vault"})
    got = shape.shape(hand_made(tmp_path))
    assert (got["harness"], got["seed"], got["kind"]) == ("conky", 1, "vault")
    kinds = lambda g: {n["id"]: n["kind"] for n in g["nodes"]}  # noqa: E731
    assert kinds(got["start"]) == {
        "den": "space",
        "hero": "character",
        "meter": "provider",
        "screen": "page",
    }
    assert kinds(got["end"]) == {**kinds(got["start"]), "note": "page"}
    edges = {(e["from"], e["to"], e["kind"]) for e in got["start"]["edges"]}
    assert edges == {
        ("hero", "den", "within"),
        ("hero", "screen", "watch"),
        ("hero", "meter", "ask"),
        ("hero", "den", "writes"),
    }
    assert {(e["from"], e["to"], e["kind"]) for e in got["end"]["edges"]} == edges | {
        ("note", "den", "within")
    }
    sizes = {n["id"]: n["size"] for n in got["end"]["nodes"]}
    assert sizes["hero"] == len("Hero body.")


def test_a_vault_says_what_happened_in_plain_facts(tmp_path: Path, monkeypatch) -> None:
    register(monkeypatch, "conky", {"kind": "vault", "path": "workdir/vault"})
    facts = {f["name"]: f["value"] for f in shape.shape(hand_made(tmp_path))["facts"]}
    assert facts == {
        "pages at start": 4,
        "pages at end": 5,
        "pages it wrote": 1,
        "signed changes": 3,
        "refused": 1,
    }


def test_a_conversation_is_a_model_and_one_growing_conversation(
    tmp_path: Path, monkeypatch
) -> None:
    register(monkeypatch, "loop", {"kind": "conversation"})
    folder = run_folder(tmp_path, "loop")
    rows = [{"status": 200, "chars_in": n} for n in (10, 30)] + [{"status": 429, "chars_in": 99}]
    (folder / "meter.jsonl").write_text("\n".join(map(json.dumps, rows)) + "\n", encoding="utf-8")
    got = shape.shape(folder)
    assert [n["id"] for n in got["end"]["nodes"]] == ["model", "conversation"]
    assert got["end"]["nodes"][1]["size"] == 30
    assert got["start"]["nodes"][1]["size"] == 0
    assert (
        got["end"]["edges"]
        == got["start"]["edges"]
        == [{"from": "model", "to": "conversation", "kind": "reads"}]
    )
    assert {f["name"]: f["value"] for f in got["facts"]} == {
        "messages": 2,
        "characters in the last call": 30,
        "kept after it stops": 0,
    }


def test_a_policy_is_one_node(tmp_path: Path, monkeypatch) -> None:
    register(monkeypatch, "floor", {"kind": "policy"})
    got = shape.shape(run_folder(tmp_path, "floor"))
    assert (
        got["end"]
        == got["start"]
        == {
            "nodes": [{"id": "policy", "kind": "policy", "size": 0}],
            "edges": [],
        }
    )
    assert got["facts"] == []


def test_every_harness_declares_its_shape_and_shared_code_names_none() -> None:
    names = []
    for path in sorted((ROOT / "bench" / "adapters").glob("*/adapter.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["shape"]["kind"] in ("vault", "conversation", "policy"), path
        names += list(data["arms"])
    lines = (ROOT / "bench" / "shape.py").read_text(encoding="utf-8").splitlines()
    text = "\n".join(x for x in lines if not x.startswith("from conky."))
    for name in names:
        assert not re.search(rf"\b{re.escape(name)}\b", text), name
