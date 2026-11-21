import type { GraphNode } from "../graph";
import { panelsIn, portsByRow } from "../graph";
import { standing, useSeen } from "../frame-context";
import type { Box } from "../layout";
import { Board } from "./Board";
import { CellHeader } from "./CellHeader";
import { Footer } from "./Footer";
import { Panel } from "./Panel";

export interface CellData extends Record<string, unknown> {
  node: GraphNode;
  box?: Box; // where the layout put the body and the boards; absent while it is measured
}

/** The one form of a page: a body of a header row, its panels in a fixed order and a footer,
 * with its pair of port boards attached outside. Every archetype is drawn by this; `variant`
 * only adds the class a stylesheet can use. A space is the same cell with room for its members
 * between its panels and its footer. A row that has ports carries their short names at its
 * end. */
export function Cell({ data, variant }: { data: CellData; variant: string }) {
  const seen = useSeen();
  const { node, box } = data;
  const ports = portsByRow(node);
  return (
    <>
      <div
        className={`cell cell-${variant} archetype-${node.archetype} density-${seen.density} ${standing(seen, node.id)} ${seen.open ? "is-open" : ""}`}
        data-cell={node.id}
        style={box ? { left: box.body.x, top: box.body.y, width: box.body.width, height: box.body.height } : undefined}
      >
        <CellHeader node={node} />
        {panelsIn(node, seen.density).map((panel) => (
          <Panel key={panel.kind} panel={panel} ports={ports} />
        ))}
        {node.form === "space" && <div className="cell-members" data-members={node.id} />}
        <Footer node={node} />
      </div>
      {box?.boards.map((b) => <Board key={b.side} board={b} node={node} />)}
    </>
  );
}
