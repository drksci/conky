import { Handle, Position } from "@xyflow/react";
import tokens from "../../../src/conky/tokens.json";
import type { Density, Socket as SocketData } from "../graph";
import { standing, useSeen } from "../frame-context";

export type SocketKind = keyof typeof tokens.socket;

const POSITION = { WEST: Position.Left, EAST: Position.Right, SOUTH: Position.Bottom } as const;

/** The plain label of a kind of socket: the whole word in detailed, the fixed mark in compact,
 * both from the one table in src/conky/tokens.json. */
export function socketLabel(kind: string, density: Density): string {
  const entry = tokens.socket[kind as SocketKind];
  if (!entry) return kind;
  return density === "detailed" ? entry.word : entry.mark;
}

/** A socket: a small square inset in a cell's edge, with an inner mark in the pen of the signal
 * it carries, hollow when nothing is plugged or filled. It is a React Flow handle, so a
 * connector ends on it; inputs sit on the left, outputs on the right, slots on the bottom. */
export function Socket({ socket, filled = false }: { socket: SocketData | undefined; filled?: boolean }) {
  const seen = useSeen();
  if (!socket) return null;
  const hollow = !(socket.plugged || filled);
  return (
    <Handle
      type={socket.side === "WEST" ? "target" : "source"}
      position={POSITION[socket.side]}
      id={socket.id}
      isConnectable={false}
      data-socket={socket.id}
      data-side={socket.side}
      className={`socket socket-${socket.side.toLowerCase()} signal-${socket.kind} ${hollow ? "is-hollow" : ""} ${standing(seen, socket.id)}`}
    />
  );
}
