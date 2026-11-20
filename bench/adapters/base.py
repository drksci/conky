"""Helpers for adapters written in Python. Nothing here is required by the contract.

The contract is in `bench/adapters/README.md`: an adapter is any command that accepts the
arguments `parse_args` reads, runs the environment command given after `--`, and exits when the
environment ends. These helpers give a Python adapter the arguments, a pseudo-terminal, the
prompt pack with its markers, and a call to the meter in the OpenAI shape.
"""

from __future__ import annotations

import argparse
import json
import os
import pty
import select
import signal
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

SETTLE = 0.25


def parser(description: str) -> argparse.ArgumentParser:
    found = argparse.ArgumentParser(description=description)
    found.add_argument("--scenario", type=Path, required=True)
    found.add_argument("--prompts", type=Path, required=True)
    found.add_argument("--workdir", type=Path, required=True)
    found.add_argument("--meter", required=True, help="the meter's base URL")
    found.add_argument("--token", required=True)
    found.add_argument("--model", required=True)
    found.add_argument("--calls", type=int, required=True)
    found.add_argument("--tokens", type=int, required=True)
    found.add_argument("--resume", action="store_true", help="a fresh process: carry on")
    found.add_argument("--seed", type=int, default=0, help="for arms that draw at random")
    found.add_argument("--shelf", action="store_true", help="the shelf is offered on this run")
    found.add_argument("command", nargs=argparse.REMAINDER)
    return found


def parse_args(description: str, argv: list[str] | None = None) -> argparse.Namespace:
    args = parser(description).parse_args(argv)
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        raise SystemExit("give the environment command after --")
    args.workdir.mkdir(parents=True, exist_ok=True)
    return args


@dataclass
class Pack:
    """The shared prompt pack: task text and house-rule wording, verbatim."""

    task: str
    rules: str

    @classmethod
    def load(cls, folder: Path) -> Pack:
        read = lambda name: (folder / name).read_text(encoding="utf-8").strip()  # noqa: E731
        return cls(read("task.md"), read("rules.md"))

    @staticmethod
    def mark(text: str) -> str:
        return f"<<<pack>>>{text}<<</pack>>>"


def mark_screen(text: str) -> str:
    return f"<<<screen>>>{text}<<</screen>>>"


class Terminal:
    """A program in a pseudo-terminal: read what it shows until it goes quiet, type lines."""

    def __init__(self, command: list[str], settle: float = SETTLE) -> None:
        self.settle = settle
        self.master, slave = pty.openpty()
        self.proc = subprocess.Popen(
            command, stdin=slave, stdout=slave, stderr=slave, start_new_session=True
        )
        os.close(slave)
        self.ended = False

    def read(self, limit: float = 600.0) -> str:
        """Return what the program printed until it was quiet for the settle time."""
        chunks: list[bytes] = []
        deadline = time.monotonic() + limit
        quiet_since = None
        while time.monotonic() < deadline:
            ready = select.select([self.master], [], [], 0.05)[0]
            if ready:
                try:
                    data = os.read(self.master, 4096)
                except OSError:
                    data = b""
                if not data:
                    self.ended = True
                    break
                chunks.append(data)
                quiet_since = time.monotonic()
            elif chunks and quiet_since and time.monotonic() - quiet_since >= self.settle:
                break
            elif self.proc.poll() is not None and not ready:
                self.ended = True
                break
        return b"".join(chunks).decode("utf-8", "replace").replace("\r\n", "\n")

    def type(self, line: str) -> None:
        os.write(self.master, (line + "\n").encode("utf-8"))

    def close(self) -> None:
        if self.proc.poll() is None:
            os.killpg(self.proc.pid, signal.SIGTERM)
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(self.proc.pid, signal.SIGKILL)
        os.close(self.master)


def ask_meter(
    meter: str, token: str, model: str, messages: list[dict], timeout: float = 300
) -> tuple[int, str]:
    """Send one chat call to the meter; return the status and the answer text or error."""
    body = json.dumps({"model": model, "messages": messages}).encode("utf-8")
    request = urllib.request.Request(
        meter.rstrip("/") + "/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=timeout) as reply:
            data = json.loads(reply.read())
        return 200, data["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")


class Notes:
    """An adapter's own append-only record in its working directory, one JSON object a line."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def read(self) -> list[dict]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        return [json.loads(line) for line in lines if line]

    def add(self, entry: dict) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
