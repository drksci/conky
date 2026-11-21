import type { GraphNode } from "../graph";
import { panelsIn } from "../graph";
import { standing, useSeen } from "../frame-context";
import type { Box } from "../layout";
import { Board, BoardWords } from "./Board";
import { CellHeader } from "./CellHeader";
import { Footer } from "./Footer";
import { Panel } from "./Panel";

export interface CellData extends Record<string, unknown> {
  node: GraphNode;
  box?: Box; // where the layout put the body and the boards; absent while it is measured
}

/** The small numbers a cell's rows share with their sockets: a row whose socket is not beside
 * it, and a rule a crossing on the cell's wall names. */
function tiesOf(node: GraphNode, box: Box | undefined): Map<string, number> {
  const ties = new Map<string, number>();
  const sockets = new Map(node.board.map((s) => [s.id, s]));
  for (const e of box?.boards.flatMap((b) => b.entries) ?? []) {
    const s = sockets.get(e.id);
    if (!s) continue;
    if (e.tied && s.row && s.mark !== null) ties.set(s.row, s.mark);
    s.rules.forEach((r) => ties.set(r.row, r.mark));
  }
  return ties;
}

/** The one form of a page: a body of a header row, its panels in a fixed order and a footer,
 * with port boards attached outside the edges its connectors leave from. Every archetype is
 * drawn by this; `variant` only adds the class a stylesheet can use. A space is the same cell
 * with room for its members between its panels and its footer. */
export function Cell({ data, variant }: { data: CellData; variant: string }) {
  const seen = useSeen();
  const { node, box } = data;
  const ties = tiesOf(node, box);
  return (
    <>
      <div
        className={`cell cell-${variant} archetype-${node.archetype} density-${seen.density} ${standing(seen, node.id)} ${seen.open ? "is-open" : ""}`}
        data-cell={node.id}
        style={box ? { left: box.body.x, top: box.body.y, width: box.body.width, height: box.body.height } : undefined}
      >
        <CellHeader node={node} />
        {panelsIn(node, seen.density).map((panel) => (
          <Panel key={panel.kind} panel={panel} ties={ties} />
        ))}
        {node.form === "space" && <div className="cell-members" data-members={node.id} />}
        <Footer node={node} />
      </div>
      {box ? box.boards.map((b) => <Board key={b.side} board={b} node={node} />) : <BoardWords node={node} />}
    </>
  );
}
