import type { CellData } from "./Cell";
import { Cell } from "./Cell";

/** A space: the same cell, drawn as the frame its members sit inside. The layout gives it the
 * room its members need below its own rows. */
export function Space({ data }: { data: CellData }) {
  return <Cell data={data} variant="space" />;
}
