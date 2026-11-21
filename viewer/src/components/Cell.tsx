import type { GraphNode } from "../graph";
import { panelsIn } from "../graph";
import { standing, useSeen } from "../frame-context";
import { CellHeader } from "./CellHeader";
import { Panel } from "./Panel";

export interface CellData extends Record<string, unknown> {
  node: GraphNode;
}

/** The one form of a page: a flat cell with a kind line, a name and its panels of rows. Every
 * archetype is drawn by this; `variant` only adds the class a stylesheet can use. */
export function Cell({ data, variant }: { data: CellData; variant: string }) {
  const seen = useSeen();
  const { node } = data;
  return (
    <div className={`cell cell-${variant} archetype-${node.archetype} ${standing(seen, node.id)}`} data-cell={node.id}>
      <CellHeader node={node} />
      {panelsIn(node, seen.mode).map((panel) => (
        <Panel key={panel.kind} panel={panel} />
      ))}
    </div>
  );
}
