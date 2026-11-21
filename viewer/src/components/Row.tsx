import { Handle, Position } from "@xyflow/react";
import type { Row as RowData } from "../graph";
import { standing, useSeen } from "../frame-context";
import { Symbol } from "./Symbol";
import { Expression } from "./Expression";

/** One row of a panel, and a port: an edge that belongs to the row attaches to it. */
export function Row({ row, symbol }: { row: RowData; symbol: string | null }) {
  const seen = useSeen();
  const value = seen.frame.values.get(row.id) ?? row.value;
  return (
    <div className={`row ${standing(seen, row.id)}`}>
      <div className="row-line" data-row={row.id}>
        <Handle type="target" position={Position.Left} id={`${row.id}:in`} className="port" isConnectable={false} />
        <span className="row-name">
          {symbol && <Symbol name={symbol} />}
          {row.name}
        </span>
        {value && <span className="row-value">{value}</span>}
        <Handle type="source" position={Position.Right} id={`${row.id}:out`} className="port" isConnectable={false} />
      </div>
      {row.expr && <Expression reads={row.expr.reads} body={row.expr.body} />}
    </div>
  );
}
