import type { GraphNode } from "../graph";
import { standing, useSeen } from "../frame-context";
import type { Board as BoardData } from "../layout";
import { Socket, SocketWords } from "./Socket";
import { sideWords } from "../metrics";

/** A port board: a thin rectangle of its own, attached to the outside of one edge of a cell,
 * holding that edge's sockets in the standard order, each with its words beside it. Wires
 * plug into its outer edge; the cell's body stays clean. */
export function Board({ board, node }: { board: BoardData; node: GraphNode }) {
  const seen = useSeen();
  const sockets = new Map(node.board.map((s) => [s.id, s]));
  const slots = new Map(node.footer.slots.map((s) => [s.socket, s]));
  const side = board.side.toLowerCase();
  return (
    <div className={`board board-${side} ${seen.frame.shown.has(node.id) ? "" : "is-hidden"}`} style={{ left: board.x, top: board.y, width: board.width, height: board.height }} data-board={`${node.id}:${side}`}>
      {board.entries.map((e) => {
        const s = sockets.get(e.id)!;
        const wall = s.face === "wall" && s.rules.length > 0;
        return (
          <div
            key={e.id}
            className={`board-entry signal-${s.kind} ${wall ? "is-above" : ""} ${standing(seen, e.id)}`}
            style={{ left: e.x - board.x, top: e.y - board.y, width: e.width, height: e.height }}
            data-entry={e.id}
          >
            <Socket socket={s} side={board.side} slot={slots.get(e.id)} />
            <SocketWords socket={s} slot={slots.get(e.id)} tie={e.tied} />
          </div>
        );
      })}
    </div>
  );
}

/** Before layout: every socket's words as a board would print them, unseen, so the layout can
 * make each board long enough: on one line, and wrapped as a side board holds them. */
export function BoardWords({ node }: { node: GraphNode }) {
  const seen = useSeen();
  const slots = new Map(node.footer.slots.map((s) => [s.socket, s]));
  return (
    <div className="board-words">
      {node.board.map((s) => (
        <span key={s.id} data-words={s.id}>
          <SocketWords socket={s} slot={slots.get(s.id)} tie />
        </span>
      ))}
      {node.board.map((s) => (
        <span key={s.id} className="board-side-words" data-side-words={s.id} style={{ width: sideWords(seen.density, s.face === "wall" && s.rules.length > 0) }}>
          <SocketWords socket={s} slot={slots.get(s.id)} tie />
        </span>
      ))}
    </div>
  );
}
