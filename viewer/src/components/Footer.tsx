import type { GraphNode } from "../graph";
import { slotsIn } from "../graph";
import { standing, useSeen, valueOf } from "../frame-context";
import { Expression } from "./Expression";
import { PortTag } from "./Port";

/** The footer of a cell: its slots, each with the name of its port, its word and what fills it
 * (who it asks, where it writes, what a space hands down and shows); the function block of a
 * slot that has one (what a space shows first); then at the right in mute how many members a
 * space has and the step the page last changed at. */
export function Footer({ node }: { node: GraphNode }) {
  const seen = useSeen();
  const detailed = seen.density === "detailed";
  const members = valueOf(seen, node.footer.members);
  const changed = detailed ? valueOf(seen, node.footer.changed) : "";
  const tail = [members, changed].filter(Boolean).join(" · ");
  const slots = slotsIn(node, seen.density);
  const ports = new Map(node.board.map((s) => [s.id, s]));
  const exprs = detailed ? slots.filter((s) => s.expr && s.filled) : [];
  if (!slots.length && !tail) return null;
  return (
    <div className="cell-foot">
      {slots.length > 0 && (
        <div className="foot-slots">
          {slots.map((s) => (
            <span key={s.id} className={`foot-slot ${standing(seen, s.id)}`} data-row={s.id}>
              {ports.has(s.socket) && <PortTag socket={ports.get(s.socket)!} slot={s} />}
              <span className="foot-slot-word">{s.label}</span>
              <span className="foot-slot-value">{valueOf(seen, s.id)}</span>
            </span>
          ))}
        </div>
      )}
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
