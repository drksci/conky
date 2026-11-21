"""The post connector: letters cross between two theatres in a sealed bag.

A sender's outbox is a small vault of its own. A carrier hands it over as a Git bundle. The
receiver clones the bundle into a temporary folder, checks every commit against the one key its
peer page pins, and takes each letter not yet taken as an ordinary write into the peer's space,
authored by the peer and judged by the receiver's own rules. The connector holds no state: what
is already taken is read from the receiver's history.
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from pathlib import Path

from conky import arch, carrier, git, present
from conky.cache import Cache
from conky.errors import BadInput, VerifyFailed
from conky.page import NAME, Page, ShapeError, check_name, parse
from conky.vault import Trailer, Vault

KEY = "key"
CARRIER = "carrier"
_FORMAT = "%x1e%H%x1f%an%x1f%G?%x1f%GS%x1f%B"
_KEPT = "write"


def _commits(repo: Path, *options: str) -> list[tuple[str, str, str, str, dict[str, str]]]:
    """Return each commit of main, oldest first: id, author, signature, signer and trailers."""
    out = git.run(["log", "--reverse", f"--format={_FORMAT}", *options, "main"], repo)
    found = []
    for record in out.split("\x1e")[1:]:
        commit, author, status, signer, message = record.split("\x1f", 4)
        found.append((commit, author, status, signer, git.trailers(message)))
    return found


def _signers(repo: Path) -> dict[str, str]:
    """Return the key line (`ssh-ed25519 AAAA...`) the bundle's own list gives each name."""
    found = {}
    shown = git.run(["show", f"main:{git.SIGNERS}"], repo)
    for line in shown.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0].endswith("@conky"):
            found[parts[0][: -len("@conky")]] = " ".join(parts[-2:])
    return found


def publish(vault: Vault, to: str | None, name: str, say: Callable[[str], None]) -> int:
    """Verify the outbox, hand it to the carrier and say where it is and whose keys sign it."""
    vault.verify()
    try:
        where = carrier.driver(name).publish(vault.path, to)
    except BadInput as exc:
        raise BadInput(f"the outbox cannot be published: {exc}: write a letter first") from exc
    count = len(vault.log())
    say(f"published {count} commit{'s' if count != 1 else ''} to {where}")
    for actor, key in sorted(_signers(vault.path).items()):
        say(f"key of {actor}: {key}")
    say("tell the receiver this key by another route, so they can pin it on the peer page")
    return 0


def _clone(bundle: Path, into: Path, peer: str, cache: Cache) -> Vault:
    """Clone the bundle into a folder of its own and verify it as a vault."""
    try:
        git.run(["clone", "-q", "-b", "main", "--", str(bundle.resolve()), str(into)], into.parent)
    except BadInput as exc:
        raise BadInput(
            f"cannot read the bundle from {peer}: {exc}: it is damaged or is not a bundle "
            "of a vault, so ask them to publish again"
        ) from exc
    folded = Vault(into, into.parent / "no-keys", cache)
    try:
        folded.verify()
    except VerifyFailed as exc:
        raise BadInput(
            f"the bundle from {peer} does not verify as a vault: {exc}: nothing was taken, "
            "so ask them to publish again"
        ) from exc
    return folded


@arch.law(
    "law.post.pinned",
    "Nothing unverified is attributed to a peer: every commit of a bundle is signed by the one "
    "key pinned on the peer page.",
    doc="connectors.md#the-post-connector",
)
def _pinned(repo: Path, peer: str, key: str | None, folder: Path) -> None:
    """Raise BadInput unless every commit of the bundle is signed by the key the peer pins."""
    found = _signers(repo)
    names = sorted({author for _, author, *_ in _commits(repo)})
    shown = "; ".join(f"{who}: {found.get(who, 'no key listed')}" for who in names)
    if not key or len(key.split()) < 2:
        advice = f"conky write {peer} {KEY}='{found.get(names[0], 'KEY')}' --as YOU"
        raise BadInput(
            f"{peer} pins no key, so nothing was taken. The bundle is signed by {shown}. "
            f"Check that key with the other party by another route, and only then run: {advice}"
        )
    kind, blob = key.split()[:2]
    pinned = folder / "pinned"
    pinned.write_text(
        "".join(f'{who}@conky namespaces="git" {kind} {blob}\n' for who in names),
        encoding="utf-8",
    )
    out = git.run(
        ["-c", f"gpg.ssh.allowedSignersFile={pinned.resolve()}", "log", "--reverse"]
        + ["--format=%h%x1f%G?%x1f%GS%x1f%an", "main"],
        repo,
    )
    for line in out.splitlines():
        short, status, signer, author = line.split("\x1f")
        if status != "G" or signer != f"{author}@conky":
            raise BadInput(
                f"commit {short} of the bundle is not signed by the key pinned on {peer} "
                f"({kind} {blob[:12]}...); the bundle is signed by {shown}. Nothing was taken. "
                f"If {peer} really changed its key, check the new one with them by another "
                f"route and write it to {peer} as {KEY}"
            )


def _taken(vault: Vault, peer: str) -> set[str]:
    """Return the foreign commits already taken: the causes of what the peer authored here."""
    try:
        found = _commits(vault.path, f"--author=^{peer} <")
    except BadInput:
        return set()
    return {t[Trailer.CAUSE] for _, _, _, _, t in found if Trailer.CAUSE in t}


def _letter(repo: Path, commit: str, page: str) -> Page:
    return parse(git.run(["show", f"{commit}:pages/{page}.md"], repo))


@arch.part(
    "part.connect.post",
    "layer.edge",
    "The post connector: a letter crosses between two theatres, taken in as a write.",
    doc="connectors.md#the-post-connector",
    roadmap="R44",
)
@arch.change(
    "place.beside.post",
    "A peer page, which pins the key of another theatre and is the space its letters land in.",
    doc="connectors.md#the-peer-page",
)
def take(
    vault: Vault,
    peer: str,
    name: str,
    where: str | None,
    now: Callable[[], str],
    ui: present.Plain,
    say: Callable[[str], None],
) -> int:
    """Take the letters a peer's bundle holds that are not yet taken, each as a write.

    Raises BadInput when the bundle cannot be read or trusted, and then nothing is written.
    """
    check_name(peer)
    try:
        page = vault.read(peer)
        fields = dict(page.fields)
    except BadInput:
        fields = {}
    bundle = carrier.driver(str(fields.get(CARRIER) or name)).fetch(fields, where)
    key = fields.get(KEY)
    with tempfile.TemporaryDirectory(prefix="conky-post-") as temp:
        folder = Path(temp)
        repo = _clone(bundle, folder / "bag", peer, vault.cache).path
        _pinned(repo, peer, key if isinstance(key, str) else None, folder)
        done = _taken(vault, peer)
        fresh = [c for c in _commits(repo) if c[4].get(Trailer.KIND) == _KEPT and c[0] not in done]
        if not fresh:
            say(f"nothing new from {peer}")
        for commit, _, _, _, found in fresh:
            say(_one(vault, repo, peer, commit, found[Trailer.PAGE], now, ui))
    return 0


def _one(
    vault: Vault,
    repo: Path,
    peer: str,
    commit: str,
    name: str,
    now: Callable[[], str],
    ui: present.Plain,
) -> str:
    """Take one letter as a write by the peer into the peer's space, and say what became of it."""
    label = f"{name} ({commit[:7]})"
    if not NAME.match(name):
        return f"{label}: not taken, {name!r} is not a page name: ask {peer} to correct it"
    try:
        letter = _letter(repo, commit, name)
    except (BadInput, ShapeError) as exc:
        return f"{label}: not taken, the page cannot be read: {exc}"
    dropped = [k for k, v in (("rules", letter.rules), ("watch", letter.watch)) if v]
    changes = {**letter.fields, "within": peer}
    done = vault.write(name, changes, letter.body, actor=peer, at=now(), cause=commit, bound=peer)
    if not done.ok:
        return f"{label}: {ui.refused(done.id[:7], done.reason or '')}"
    kept = f", without its {' and '.join(dropped)}" if dropped else ""
    return f"{label}: {ui.written(done.id[:7])}{kept}"
