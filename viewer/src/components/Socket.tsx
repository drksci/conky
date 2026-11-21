import { Handle, Position } from "@xyflow/react";
import tokens from "../../../src/conky/tokens.json";
import type { Density, Side, Slot, Socket as SocketData } from "../graph";
import { standing, useSeen, valueOf } from "../frame-context";
import { Symbol, wordOf } from "./Symbol";

export type SocketKind = keyof typeof tokens.socket;

const POSITION: Record<Side, Position> = { WEST: Position.Left, EAST: Position.Right, NORTH: Position.Top, SOUTH: Position.Bottom };

/** The plain word of a kind of socket in a density: the whole word in detailed, the fixed mark
 * in compact, both from the one table in src/conky/tokens.json. */
export function socketLabel(kind: string, density: Density): string {
  const entry = tokens.socket[kind as SocketKind];
  if (!entry) return kind;
  return density === "detailed" ? entry.word : entry.mark;
}

/** A socket: a small square on a port board, with an inner mark in the pen of the signal it
 * carries. It is hollow while nothing shown plugs into it, or when its slot is empty. It is a
 * React Flow handle on the board's outer edge, so a connector ends on it. */
export function Socket({ socket, side, slot }: { socket: SocketData; side: Side; slot?: Slot }) {
  const seen = useSeen();
  const hollow = slot ? !slot.filled : !seen.frame.plugged.has(socket.id);
  return (
    <span className="socket-seat">
      {socket.face === "wall" && (
        // the inner face of a socket on a wall, where a jumper goes on through
        <Handle type="source" position={POSITION[side]} id={socket.id} isConnectable={false} className="socket-through" />
      )}
      <Handle
        type={socket.face === "in" || socket.face === "wall" ? "target" : "source"}
        position={POSITION[side]}
        id={socket.id}
        isConnectable={false}
        data-socket={socket.id}
        data-side={side}
        className={`socket signal-${socket.kind} ${hollow ? "is-hollow" : ""} ${standing(seen, socket.id)}`}
      />
    </span>
  );
}

/** What a socket's board says beside it, once a connector: the kind of signal where it leaves,
 * nothing where it arrives, a slot's word and what fills it, and at a space's wall the rules
 * judged there (a shield, or the refusal symbol where a rule said no), named by the numbers
 * the rules carry in the space. `tie` is the number a socket shares with its row when it is
 * not beside it. */
export function SocketWords({ socket, slot, tie }: { socket: SocketData; slot?: Slot; tie: boolean }) {
  const seen = useSeen();
  const detailed = seen.density === "detailed";
  const mark = tie && socket.mark !== null ? <span className="socket-tie">{socket.mark}</span> : null;
  if (socket.face === "wall") {
    if (!socket.rules.length) return null;
    const no = socket.rules.some((r) => r.says === "no");
    const marks = socket.rules.map((r) => r.mark).join(", ");
    return (
      <span className={`socket-label socket-rules ${no ? "is-stopped" : ""}`} title={socket.rules.map((r) => r.row.split("/bound/")[1] ?? r.row).join("\n")}>
        <Symbol name={no ? "refusal" : "rule"} />
        {detailed && `${wordOf("rule")} ${marks}`}
      </span>
    );
  }
  if (slot)
    return (
      <span className="socket-label">
        <span className="socket-word">{socketLabel(socket.kind, seen.density)}</span> <span className={`socket-value ${standing(seen, slot.id)}`}>{valueOf(seen, slot.id)}</span>
      </span>
    );
  if (socket.face === "in") return mark && <span className="socket-label">{mark}</span>;
  return (
    <span className="socket-label">
      {mark}
      <span className="socket-word">{socketLabel(socket.kind, seen.density)}</span>
    </span>
  );
}
