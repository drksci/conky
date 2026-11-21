import { regionOf } from "../graph";
import { standing, useSeen } from "../frame-context";
import type { CellData } from "./Cell";

/** A note among many in one space, by the region it is in: shown to the space, a compact cell
 * with its number and the first line of its text; otherwise a small numbered square. */
export function Note({ data }: { data: CellData }) {
  const seen = useSeen();
  const { node } = data;
  const shown = regionOf(seen.frame.regions, node.id)?.kind === "shown";
  return (
    <div
      className={`cell cell-note ${shown ? "is-shown-note" : ""} ${standing(seen, node.id)}`}
      data-cell={node.id}
      title={node.name}
    >
      <span className="note-number" data-head={node.id}>
        {node.header.label}
      </span>
      {shown && <span className="note-line">{node.header.line}</span>}
    </div>
  );
}
