"""Git and ssh-keygen, driven as subprocesses with the machine's configuration shut out."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from conky.errors import BadInput

SIGNERS = "keys/allowed_signers"
MIN_GIT = (2, 34)
_ISOLATION = {
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_TERMINAL_PROMPT": "0",
}


def _run(
    command: list[str], cwd: Path, env: dict[str, str] | None = None, stdin: str | None = None
) -> str:
    proc = subprocess.run(
        command,
        cwd=cwd,
        env={**os.environ, **_ISOLATION, **(env or {})},
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr.strip() or proc.stdout.strip() or "no output").splitlines()[-1]
        raise BadInput(f"{' '.join(command[:2])} failed: {detail}")
    return proc.stdout


def run(
    args: list[str], cwd: Path, env: dict[str, str] | None = None, stdin: str | None = None
) -> str:
    """Run git in cwd with SSH signing configured and return its output."""
    signers = (cwd / SIGNERS).resolve()
    config = ["-c", "gpg.format=ssh", "-c", f"gpg.ssh.allowedSignersFile={signers}"]
    return _run(["git", *config, *args], cwd, env, stdin)


def require_tools() -> None:
    """Raise BadInput unless Git 2.34 or newer and ssh-keygen are on PATH."""
    if shutil.which("git") is None:
        raise BadInput("git is not installed: install Git 2.34 or newer")
    if shutil.which("ssh-keygen") is None:
        raise BadInput("ssh-keygen is not installed: install OpenSSH 8.2 or newer (openssh-client)")
    found = re.search(r"(\d+)\.(\d+)", _run(["git", "--version"], Path.cwd()))
    if found is None or (int(found[1]), int(found[2])) < MIN_GIT:
        raise BadInput("git is older than 2.34: upgrade Git to 2.34 or newer")


def init(path: Path) -> None:
    """Create a Git repository on main, set up for SSH signing."""
    path.mkdir(parents=True, exist_ok=True)
    run(["init", "-q", "-b", "main"], path)
    for key, value in (
        ("gpg.format", "ssh"),
        ("gpg.ssh.allowedSignersFile", SIGNERS),
        ("commit.gpgsign", "true"),
    ):
        run(["config", key, value], path)


def register(keys_dir: Path, signers: Path, actor: str) -> tuple[Path, str | None]:
    """Return the actor's private key path, creating the key on first use.

    The second value is the allowed_signers line to add when the file does not list the actor.
    """
    private = keys_dir / actor
    listed = signers.exists() and any(
        line.startswith(f"{actor}@conky ") for line in signers.read_text().splitlines()
    )
    if not private.exists():
        if listed:
            raise BadInput(f"no private key for {actor!r} in {keys_dir}: pass --keys <directory>")
        keys_dir.mkdir(parents=True, exist_ok=True)
        _run(
            ["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", actor, "-f", str(private)],
            keys_dir,
        )
    if listed:
        return private, None
    kind, blob = private.with_name(f"{actor}.pub").read_text().split()[:2]
    return private, f'{actor}@conky namespaces="git" {kind} {blob}\n'


def commit(
    cwd: Path,
    *,
    actor: str,
    at: str,
    key: Path,
    subject: str,
    trailers: list[tuple[str, str]],
    paths: list[str],
    body: str = "",
) -> str:
    """Stage paths and make one signed commit by actor at the instant at; return its id.

    The body, when given, sits between the subject and the trailers exactly as supplied.
    """
    who = {"NAME": actor, "EMAIL": f"{actor}@conky", "DATE": at}
    env = {f"GIT_{role}_{k}": v for role in ("AUTHOR", "COMMITTER") for k, v in who.items()}
    if paths:
        run(["add", "--", *paths], cwd)
    message = subject + "\n\n" + (body + "\n\n" if body else "")
    message += "".join(f"{k}: {v}\n" for k, v in trailers)
    run(
        ["-c", f"user.signingkey={key}", "commit", "-q", "-S", "--allow-empty"]
        + ["--cleanup=verbatim", "-F", "-"],
        cwd,
        env,
        message,
    )
    return run(["rev-parse", "HEAD"], cwd).strip()


def trailers(message: str) -> dict[str, str]:
    """Return the trailer block at the end of a commit message as a mapping."""
    paragraphs = message.strip().split("\n\n")
    found: dict[str, str] = {}
    for line in paragraphs[-1].splitlines() if len(paragraphs) > 1 else []:
        key, sep, value = line.partition(": ")
        if sep:
            found[key] = value
    return found
