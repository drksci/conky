#!/usr/bin/env python3
"""The helper the agent plays with: `./game "<line>"` types one line, `./game` shows the screen.

It talks to the adapter that holds the game open, through a socket beside it, prints what comes
back and nothing else. It keeps no state of its own. Standard library only.
"""

import os
import socket
import sys

SOCKET = ".game.sock"


def main(argv: list[str]) -> int:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    if len(argv) > 2:
        print('give one line in quotes: ./game "<line>"', file=sys.stderr)
        return 2
    request = argv[1] if len(argv) == 2 else None
    body = ("T" + request if request is not None else "S").encode("utf-8")
    link = socket.socket(socket.AF_UNIX)
    try:
        link.connect(SOCKET)
    except OSError:
        print("the game is not running here: nothing to type into", file=sys.stderr)
        return 1
    link.sendall(body)
    link.shutdown(socket.SHUT_WR)
    chunks = []
    while data := link.recv(65536):
        chunks.append(data)
    sys.stdout.write(b"".join(chunks).decode("utf-8", "replace"))
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
