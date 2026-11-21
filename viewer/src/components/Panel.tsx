import type { Panel as PanelData } from "../graph";
import { Row } from "./Row";

/** A panel of a cell: its name, then its rows, and how many more there are when capped. */
export function Panel({ panel }: { panel: PanelData }) {
  return (
    <div className={`panel panel-${panel.kind}`}>
      <div className="panel-name">{panel.title}</div>
      {panel.rows.map((row) => (
        <Row key={row.id} row={row} symbol={panel.kind === "fields" ? null : panel.symbol} />
      ))}
      {panel.more > 0 && <div className="panel-more">{panel.more} more</div>}
    </div>
  );
}
