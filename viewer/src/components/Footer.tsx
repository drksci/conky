import type { GraphNode, Slot } from "../graph";
import { slotsIn } from "../graph";
import { standing, useSeen, valueOf } from "../frame-context";
import { Expression } from "./Expression";
import { Socket } from "./Socket";

/** The footer row of a cell: its slots, each a socket on the bottom edge with its plain label
 * and what is plugged in (hollow when the slot is empty), then at the far right in mute how
 * many members a space has and the step the page last changed at. */
export function Footer({ node }: { node: GraphNode }) {
  const seen = useSeen();
  const slots = slotsIn(node, seen.density);
  const sockets = new Map(node.sockets.map((s) => [s.id, s]));
  const detailed = seen.density === "detailed";
  const members = valueOf(seen, node.footer.members);
  const changed = detailed ? valueOf(seen, node.footer.changed) : "";
  const tail = [members, changed].filter(Boolean).join(" · ");
  if (!slots.length && !tail) return null;
  const exprs = detailed ? slots.filter((s) => s.expr && s.filled) : [];
  return (
    <div className="cell-foot">
      {exprs.map((s) => (
        <div key={s.id} className={`foot-expr ${standing(seen, s.id)}`}>
          <span className="foot-expr-label">{s.label} first</span>
          <Expression expr={s.expr!} />
        </div>
      ))}
      <div className="foot-row">
        {slots.map((s: Slot) => (
          <span key={s.id} className={`slot ${s.filled ? "" : "is-hollow"} ${standing(seen, s.id)}`} data-row={s.id}>
            <Socket socket={sockets.get(s.socket)} filled={s.filled} />
            <span className="slot-label">{s.label}</span>
            <span className="slot-value">{valueOf(seen, s.id)}</span>
          </span>
        ))}
        {tail && <span className="foot-tail">{tail}</span>}
      </div>
    </div>
  );
}
