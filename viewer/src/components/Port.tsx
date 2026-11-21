import { Handle, Position } from "@xyflow/react";
import type { Side, Slot, Socket } from "../graph";
import { isPlugged } from "../graph";
import { useSeen } from "../frame-context";
import { Symbol } from "./Symbol";

const OUTER: Record<Side, Position> = { WEST: Position.Left, EAST: Position.Right, NORTH: Position.Top, SOUTH: Position.Bottom };
const INNER: Record<Side, Position> = { WEST: Position.Right, EAST: Position.Left, NORTH: Position.Bottom, SOUTH: Position.Top };

/** A port: a flat square block in its kind's colour, as wide as its board is thick, with its
 * short name on it. It is solid while something is plugged in, and hatched on the ground while
 * nothing is: before its connector arrives, or while its slot is empty. It is a React Flow
 * handle, so a cable ends on its outer face; a port on a wall has a second handle on its inner
 * face, where the jumper goes on inside. */
export function Port({ socket, side, slot }: { socket: Socket; side: Side; slot?: Slot }) {
  const seen = useSeen();
  const idle = !isPlugged(seen.frame, socket, slot);
  const look = `port signal-${socket.kind} ${idle ? "is-idle" : ""}`;
  return (
    <span className="port-seat">
      <Handle
        type={socket.face === "in" || socket.face === "wall" ? "target" : "source"}
        position={OUTER[side]}
        id={socket.id}
        isConnectable={false}
        data-socket={socket.id}
        data-side={side}
        className={look}
      >
        <span className="port-name" data-port-name={socket.id}>
          {socket.name}
        </span>
      </Handle>
      {socket.face === "wall" && <Handle type="source" position={INNER[side]} id={socket.id} isConnectable={false} className="port-through" />}
    </span>
  );
}

/** The rules a space judged at a port on its wall, on the line above the block: a shield, or
 * the refusal symbol where a rule said no. Their rows in the space carry the port's name. */
export function PortRules({ socket }: { socket: Socket }) {
  if (!socket.rules.length) return null;
  const no = socket.rules.some((r) => r.says === "no");
  return (
    <span className={`port-rules signal-${socket.kind} ${no ? "is-stopped" : ""}`} title={socket.rules.map((r) => r.row.split("/bound/")[1] ?? r.row).join("\n")}>
      <Symbol name={no ? "refusal" : "rule"} />
    </span>
  );
}

/** A port's short name where something else refers to it (a row, the footer, the side panel):
 * a small chip that looks like the port, solid or hatched as the port is now. */
export function PortTag({ socket, slot }: { socket: Socket; slot?: Slot }) {
  const seen = useSeen();
  const idle = !isPlugged(seen.frame, socket, slot);
  return <span className={`port-tag signal-${socket.kind} ${idle ? "is-idle" : ""}`}>{socket.name}</span>;
}

/** The names of the ports a row has, at the row's end. */
export function PortTags({ ports }: { ports: Socket[] | undefined }) {
  if (!ports?.length) return null;
  return (
    <span className="port-tags">
      {ports.map((s) => (
        <PortTag key={s.id} socket={s} />
      ))}
    </span>
  );
}
