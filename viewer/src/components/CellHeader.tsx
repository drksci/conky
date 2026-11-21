import tokens from "../../../src/conky/tokens.json";
import type { GraphNode } from "../graph";
import { useSeen, valueOf } from "../frame-context";
import { Symbol } from "./Symbol";

const picture = (a: string) => /^(https?:|data:|\.{0,2}\/)|\.(png|jpe?g|gif|svg|webp)$/i.test(a);

/** The header row of a cell: the avatar or the kind's symbol, the name as the title with the
 * kind words under it in the small label style, and at the right end the count of model calls
 * and of writes turned away, each only when there is one. A second, smaller line says which
 * spaces the page is within and the phrases it is known as. */
export function CellHeader({ node }: { node: GraphNode }) {
  const seen = useSeen();
  const { header } = node;
  const thought = Number(valueOf(seen, header.thought) || 0);
  const refused = Number(valueOf(seen, header.refused) || 0);
  const detailed = seen.density === "detailed";
  const within = header.within.filter((s) => s !== node.parent || header.within.length > 1);
  return (
    <div className="cell-head" data-head={node.id}>
      <div className="cell-head-row">
        <span className="cell-mark">
          {header.avatar ? (
            picture(header.avatar) ? <img className="cell-avatar" src={header.avatar} alt="" /> : <span className="cell-avatar">{header.avatar}</span>
          ) : (
            <Symbol name={header.symbol} />
          )}
        </span>
        <span className="cell-title">
          <span className="cell-name" title={node.name}>
            {node.name}
          </span>
          <span className="cell-kind">{header.kinds.join(" · ")}</span>
        </span>
        {(thought > 0 || refused > 0) && (
          <span className="cell-counts">
            {thought > 0 && (
              <span className="cell-count is-thought" title={`${thought} model ${thought === 1 ? "call" : "calls"}`}>
                <Symbol name="thought" />
                {thought}
              </span>
            )}
            {refused > 0 && (
              <span className="cell-count is-refused" title={`${refused} turned away`}>
                <Symbol name="refusal" />
                {refused}
              </span>
            )}
          </span>
        )}
      </div>
      {(within.length > 0 || header.known_as.length > 0) && (detailed || header.known_as.length > 0) && (
        <div className="cell-sub">
          {within.length > 0 && (
            <span>
              {tokens.words.within} {within.join(", ")}
            </span>
          )}
          {header.known_as.length > 0 && (
            <span>
              {tokens.words.known_as} {header.known_as.map((k) => `“${k}”`).join(", ")}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
