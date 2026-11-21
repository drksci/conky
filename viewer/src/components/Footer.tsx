import type { GraphNode } from "../graph";
import { slotsIn } from "../graph";
import { standing, useSeen, valueOf } from "../frame-context";
import { Expression } from "./Expression";

/** The footer row of a cell: the function block of a slot that has one (what a space shows
 * first), then at the right in mute how many members a space has and the step the page last
 * changed at. The slots themselves, with what fills them, are sockets on the bottom board. */
export function Footer({ node }: { node: GraphNode }) {
  const seen = useSeen();
  const detailed = seen.density === "detailed";
  const members = valueOf(seen, node.footer.members);
  const changed = detailed ? valueOf(seen, node.footer.changed) : "";
  const tail = [members, changed].filter(Boolean).join(" · ");
  const exprs = detailed ? slotsIn(node, seen.density).filter((s) => s.expr && s.filled) : [];
  if (!exprs.length && !tail) return null;
  return (
    <div className="cell-foot">
      {exprs.map((s) => (
        <div key={s.id} className={`foot-expr ${standing(seen, s.id)}`}>
          <span className="foot-expr-label">{s.label} first</span>
          <Expression expr={s.expr!} />
        </div>
      ))}
      {tail && <div className="foot-tail">{tail}</div>}
    </div>
  );
}
