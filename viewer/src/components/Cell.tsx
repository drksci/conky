import type { GraphNode } from "../graph";
import { panelsIn, socketsIn } from "../graph";
import { standing, useSeen } from "../frame-context";
import { CellHeader } from "./CellHeader";
import { Footer } from "./Footer";
import { Panel } from "./Panel";
import { Socket, socketLabel } from "./Socket";

export interface CellData extends Record<string, unknown> {
  node: GraphNode;
  labels?: Record<string, { x: number; y: number }>; // where ELK put each socket's label
}

/** The plain labels of a cell's sockets, outside its frame where the layout left room for
 * them. They sit beside the cell, not in it, so they never crowd its rows. */
export function SocketLabels({ data }: { data: CellData }) {
  const seen = useSeen();
  const drawn = socketsIn(data.node, seen.density);
  return (
    <>
      {drawn.map((s) => {
        const at = data.labels?.[s.id];
        if (!at || s.side === "SOUTH") return null; // a slot's label is printed beside it
        return (
          <span
            key={s.id}
            className={`socket-label signal-${s.kind} ${standing(seen, s.id)}`}
            style={{ transform: `translate(${at.x}px, ${at.y}px)` }}
          >
            {socketLabel(s.kind, seen.density)}
          </span>
        );
      })}
    </>
  );
}

/** The one form of a page: a header row, its panels in a fixed order, and a footer row of
 * slots, with sockets inset in its edges. Every archetype is drawn by this; `variant` only adds
 * the class a stylesheet can use. A space is the same cell with room for its members between
 * its panels and its footer. */
export function Cell({ data, variant }: { data: CellData; variant: string }) {
  const seen = useSeen();
  const { node } = data;
  const own = socketsIn(node, seen.density).filter((s) => s.row === null);
  return (
    <>
      <div
        className={`cell cell-${variant} archetype-${node.archetype} density-${seen.density} ${standing(seen, node.id)} ${seen.open ? "is-open" : ""}`}
        data-cell={node.id}
      >
        <CellHeader
          node={node}
          sockets={own.map((s) => (
            <Socket key={s.id} socket={s} />
          ))}
        />
        {panelsIn(node, seen.density).map((panel) => (
          <Panel key={panel.kind} panel={panel} node={node} />
        ))}
        {node.form === "space" && <div className="cell-members" data-members={node.id} />}
        <Footer node={node} />
      </div>
      <SocketLabels data={data} />
    </>
  );
}
