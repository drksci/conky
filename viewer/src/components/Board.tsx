import type { GraphNode } from "../graph";
import { standing, useSeen } from "../frame-context";
import type { Board as BoardData } from "../layout";
import { Port, PortRules } from "./Port";

/** A port board: one of a cell's pair, a thin strip of its own attached outside one edge and
 * running its whole length, as thick as a port is wide. Its ports sit in a row along it in the
 * standard order, an even gap apart, like the sockets on the back of a switch. A board with no
 * ports is still drawn, plain, so the pair reads as one frame. */
export function Board({ board, node }: { board: BoardData; node: GraphNode }) {
  const seen = useSeen();
  const sockets = new Map(node.board.map((s) => [s.id, s]));
  const slots = new Map(node.footer.slots.map((s) => [s.socket, s]));
  const side = board.side.toLowerCase();
  return (
    <div className={`board board-${side} ${seen.frame.shown.has(node.id) ? "" : "is-hidden"}`} style={{ left: board.x, top: board.y, width: board.width, height: board.height }} data-board={`${node.id}:${side}`}>
      {board.entries.map((e) => {
        const s = sockets.get(e.id)!;
        return (
          <div
            key={e.id}
            className={`board-entry ${s.rules.length ? "has-rules" : ""} ${standing(seen, e.id)}`}
            style={{ left: e.x - board.x, top: e.y - board.y, width: e.width, height: e.height }}
            data-entry={e.id}
          >
            <PortRules socket={s} />
            <Port socket={s} side={board.side} slot={slots.get(e.id)} />
          </div>
        );
      })}
    </div>
  );
}
