import { Handle, Position } from "@xyflow/react";
import type { GraphNode } from "../graph";
import { Symbol } from "./Symbol";

const picture = (a: string) => /^(https?:|data:|\.{0,2}\/)|\.(png|jpe?g|gif|svg|webp)$/i.test(a);

/** The head of a cell: the small kind line, then the name, with the avatar when a page has one.
 * An edge that belongs to the page as a whole attaches here. */
export function CellHeader({ node }: { node: GraphNode }) {
  return (
    <div className="cell-header" data-head={node.id}>
      <Handle type="target" position={Position.Left} id="in" className="port" isConnectable={false} />
      <div className="cell-kind">
        {node.avatar ? (
          picture(node.avatar) ? <img className="cell-avatar" src={node.avatar} alt="" /> : <span className="cell-avatar">{node.avatar}</span>
        ) : (
          <Symbol name={node.symbol} />
        )}
        {node.kind}
      </div>
      <div className="cell-name">{node.name}</div>
      <Handle type="source" position={Position.Right} id="out" className="port" isConnectable={false} />
    </div>
  );
}
