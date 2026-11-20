"""Keys: ed25519 identities. Private halves stay outside the vault."""

from __future__ import annotations

from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from conky.errors import BadInput

_RAW = {"encoding": serialization.Encoding.Raw}


def _public_hex(private: Ed25519PrivateKey) -> str:
    raw = private.public_key().public_bytes(**_RAW, format=serialization.PublicFormat.Raw)
    return raw.hex()


class Keyring:
    """Signs as an actor, creating its keypair on first use."""

    def __init__(self, private_dir: Path, public_dir: Path) -> None:
        self.private_dir = private_dir
        self.public_dir = public_dir

    def sign(self, actor: str, data: bytes) -> str:
        """Return the hex signature of data by actor."""
        private = self._load(actor)
        return private.sign(data).hex()

    def _load(self, actor: str) -> Ed25519PrivateKey:
        secret = self.private_dir / f"{actor}.key"
        public = self.public_dir / f"{actor}.pub"
        if secret.exists():
            private = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(secret.read_text()))
        elif public.exists():
            raise BadInput(f"no private key for {actor!r} in {self.private_dir}")
        else:
            private = Ed25519PrivateKey.generate()
            raw = private.private_bytes(
                **_RAW,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption(),
            )
            self.private_dir.mkdir(parents=True, exist_ok=True)
            secret.touch(mode=0o600)
            secret.write_text(raw.hex())
        if not public.exists():
            public.write_text(_public_hex(private))
        return private


def check_seal(public_dir: Path, actor: str, data: bytes, seal: str) -> str | None:
    """Return None if seal is valid for actor over data, else the reason it is not."""
    path = public_dir / f"{actor}.pub"
    if not path.exists():
        return f"no public key for actor {actor!r}"
    try:
        key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(path.read_text()))
        key.verify(bytes.fromhex(seal), data)
    except (ValueError, InvalidSignature):
        return f"seal does not verify against the key of {actor!r}"
    return None
