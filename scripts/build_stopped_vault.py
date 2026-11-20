"""Build the stopped vault that `conky assimilate` takes over when it is given no source.

    python scripts/build_stopped_vault.py src/conky/stopped/lemonade.bundle

The vault is the first four steps of the `lemonade` example, at fixed instants, signed by a key
derived from a fixed seed. Ed25519 signatures are deterministic, so every run gives the same
commit ids. The seed stands in for a key that is never kept: nothing it signs needs trust, and the
packaged vault holds only the public half.
"""

from __future__ import annotations

import base64
import hashlib
import struct
import subprocess
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

from conky import demo
from conky.vault import Vault

SEED = hashlib.sha256(b"conky stopped vault: lemonade").digest()
START = datetime(2026, 1, 1, 9, 0, 0, tzinfo=UTC)
STOPPED_AFTER = 4

_P = 2**255 - 19
_D = -121665 * pow(121666, _P - 2, _P) % _P


def _add(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    """Add two points of edwards25519 in extended coordinates."""
    p, d = _P, _D
    e = (a[1] - a[0]) * (b[1] - b[0]) % p
    f = (a[1] + a[0]) * (b[1] + b[0]) % p
    g = 2 * a[3] * b[3] * d % p
    h = 2 * a[2] * b[2] % p
    e, f, g, h = f - e, h - g, h + g, f + e
    return e * f % p, g * h % p, f * g % p, e * h % p


def _public(seed: bytes) -> bytes:
    """Return the Ed25519 public key for a 32-byte seed (RFC 8032, section 5.1.5)."""
    digest = hashlib.sha512(seed).digest()
    scalar = (int.from_bytes(digest[:32], "little") & ((1 << 254) - 8)) | (1 << 254)
    y = 4 * pow(5, _P - 2, _P) % _P
    x2 = (y * y - 1) * pow(_D * y * y + 1, _P - 2, _P) % _P
    x = pow(x2, (_P + 3) // 8, _P)
    if (x * x - x2) % _P:
        x = x * pow(2, (_P - 1) // 4, _P) % _P
    if x & 1:
        x = _P - x
    point, total = (x, y, 1, x * y % _P), (0, 1, 1, 0)
    while scalar:
        if scalar & 1:
            total = _add(total, point)
        point = _add(point, point)
        scalar >>= 1
    zinv = pow(total[2], _P - 2, _P)
    gx, gy = total[0] * zinv % _P, total[1] * zinv % _P
    return (gy | ((gx & 1) << 255)).to_bytes(32, "little")


def _string(data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + data


def write_key(keys_dir: Path, actor: str) -> None:
    """Write the OpenSSH private and public key files for actor from the fixed seed."""
    public = _public(SEED)
    blob = _string(b"ssh-ed25519") + _string(public)
    private = (
        struct.pack(">II", 1, 1)
        + _string(b"ssh-ed25519")
        + _string(public)
        + _string(SEED + public)
        + _string(actor.encode())
    )
    private += bytes(range(1, 8 - len(private) % 8 + 1)) if len(private) % 8 else b""
    body = (
        b"openssh-key-v1\0"
        + _string(b"none")
        + _string(b"none")
        + _string(b"")
        + struct.pack(">I", 1)
        + _string(blob)
        + _string(private)
    )
    text = base64.b64encode(body).decode()
    lines = [text[i : i + 70] for i in range(0, len(text), 70)]
    keys_dir.mkdir(parents=True, exist_ok=True)
    key = keys_dir / actor
    key.write_text(
        "-----BEGIN OPENSSH PRIVATE KEY-----\n"
        + "\n".join(lines)
        + "\n-----END OPENSSH PRIVATE KEY-----\n"
    )
    key.chmod(0o600)
    line = f"ssh-ed25519 {base64.b64encode(blob).decode()} {actor}\n"
    (keys_dir / f"{actor}.pub").write_text(line)


def build(bundle: Path) -> None:
    """Build the stopped vault in a scratch folder and bundle it at the path bundle."""
    steps = demo.load("lemonade").steps[:STOPPED_AFTER]
    instants = iter(START + timedelta(minutes=n) for n in range(len(steps)))
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        for actor in sorted({step.actor for step in steps}):
            write_key(root / "keys", actor)
        vault = Vault.init(root / "vault", root / "keys")
        for step in steps:
            at = next(instants).strftime("%Y-%m-%dT%H:%M:%SZ")
            vault.write(step.page, step.fields, step.body, actor=step.actor, at=at)
        bundle.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "bundle", "create", str(bundle.resolve()), "--all"],
            cwd=root / "vault",
            check=True,
            capture_output=True,
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/build_stopped_vault.py OUTPUT.bundle")
    build(Path(sys.argv[1]))
