import { standing, useSeen } from "../frame-context";
import type { CellData } from "./Cell";

/** A note among many in one space: a small numbered cell in a grid. */
export function Note({ data }: { data: CellData }) {
  const seen = useSeen();
  const { node } = data;
  return (
    <div className={`cell cell-note ${standing(seen, node.id)}`} data-cell={node.id} title={node.name}>
      {node.label}
    </div>
  );
}
