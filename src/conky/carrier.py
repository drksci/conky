"""A carrier: how a sender's outbox is made available to another theatre, and brought there.

A carrier moves one thing, a Git bundle file of an outbox vault's `main`. It reads nothing else
of the other theatre. The `local` driver hands the file over a path. A real carrier (the first
planned is Radicle, with one private repository per outbox and the receiver's key allowed) plugs
in here by adding a driver with the same two methods: nothing else in the runtime changes.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Protocol

from conky import arch, git
from conky.errors import BadInput

DEFAULT = "local"
BUNDLE = "bundle"


@arch.slot(
    "slot.carrier",
    "carrier",
    "How an outbox is made available to a peer, and how a peer's bundle is brought here.",
    doc="connectors.md#the-post-connector",
)
class Carrier(Protocol):
    """The seam for real carriers: two methods, and no state."""

    def publish(self, outbox: Path, to: str | None) -> str:
        """Make the outbox vault's `main` available as a Git bundle and say where."""
        ...

    def fetch(self, peer: Mapping[str, Any], where: str | None) -> Path:
        """Bring the peer's bundle here and return the path of the bundle file.

        `peer` holds the fields of the peer page. `where` overrides the place they name.
        """
        ...


class Local:
    """The `local` driver: the bundle is a file at a path, which a shared folder can carry."""

    def publish(self, outbox: Path, to: str | None) -> str:
        """Write `git bundle create FILE main`, by default beside the outbox, and return FILE."""
        target = Path(to) if to else outbox.resolve().parent / f"{outbox.resolve().name}.bundle"
        target = target.expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        git.run(["bundle", "create", str(target), "main"], outbox)
        return str(target)

    def fetch(self, peer: Mapping[str, Any], where: str | None) -> Path:
        """Return the file the peer page's `bundle` field names, or `where` when given."""
        named = where or peer.get(BUNDLE)
        if not isinstance(named, str) or not named.strip():
            raise BadInput(
                f"no bundle to take: write {BUNDLE}=PATH on the peer page, or pass --from FILE"
            )
        found = Path(named.strip()).expanduser()
        if not found.is_file():
            raise BadInput(
                f"no bundle file at {found}: ask the sender to run `conky connect post publish`, "
                "or correct the path"
            )
        return found


DRIVERS: dict[str, Carrier] = {DEFAULT: Local()}


def driver(name: str) -> Carrier:
    """Return the carrier called name, or raise BadInput listing those that exist."""
    if name not in DRIVERS:
        raise BadInput(f"no carrier named {name!r}: use one of {', '.join(sorted(DRIVERS))}")
    return DRIVERS[name]
