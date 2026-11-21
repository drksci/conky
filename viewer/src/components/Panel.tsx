import tokens from "../../../src/conky/tokens.json";
import type { BoundPanel, GraphNode, HoldsPanel, Panel as PanelData, Socket as SocketData, TextPanel, WhenPanel } from "../graph";
import { standing, useSeen, valueOf } from "../frame-context";
import { Expression } from "./Expression";
import { Socket } from "./Socket";
import { Symbol } from "./Symbol";

type Sockets = Map<string, SocketData>;

/** Prose as printed: a name with a hyphen in it (note-07) is never split across two lines. */
const unbroken = (text: string) => text.replace(/(\w)-(?=\w)/g, "$1\u2011");

/** The page's text as prose, its first lines. */
function Text({ panel }: { panel: TextPanel }) {
  const seen = useSeen();
  const text = valueOf(seen, panel.id);
  return (
    <div className={`panel panel-text ${standing(seen, panel.id)}`}>
      <p className="cell-text">{unbroken(text)}</p>
    </div>
  );
}

/** Plain fields: the name left in mute, the value right in ink, capped with "N more". */
function Holds({ panel }: { panel: HoldsPanel }) {
  const seen = useSeen();
  return (
    <div className="panel panel-holds">
      {seen.density === "detailed" && <div className="panel-head">{panel.title}</div>}
      <dl className="holds">
        {panel.rows.map((r) => (
          <div key={r.id} className={`holds-row ${standing(seen, r.id)}`}>
            <dt>{r.name}</dt>
            <dd>{unbroken(valueOf(seen, r.id))}</dd>
          </div>
        ))}
      </dl>
      {panel.more > 0 && (
        <div className="panel-more">
          {panel.more} {tokens.words.more}
        </div>
      )}
    </div>
  );
}

/** The rules a page is bound by: its own, then those handed down to it, each with the space it
 * comes from, and each with its function block. A space's own rule for its members has the
 * socket a write turned away at its wall plugs into. */
function Bound({ panel, sockets }: { panel: BoundPanel; sockets: Sockets }) {
  const seen = useSeen();
  return (
    <div className="panel panel-bound">
      {seen.density === "detailed" && <div className="panel-head">{panel.title}</div>}
      {panel.rows.map((r) => (
        <div key={r.id} className={`rule ${standing(seen, r.id)}`} data-row={r.id}>
          <div className="rule-label">
            <Symbol name="rule" />
            {r.label}
            {r.from && (
              <span className="rule-from">
                {" "}
                · {tokens.words.from} {r.from}
              </span>
            )}
            {r.in && <Socket socket={sockets.get(r.in)} />}
          </div>
          <Expression expr={r.expr} />
        </div>
      ))}
    </div>
  );
}

/** The heart of a cell: one row a watch entry in two aligned columns, "when" (what it listens
 * for, with its condition) and "then" (what it does), with the input socket on the left edge
 * and the output socket on the right; then the rows from the record that no watch entry
 * explains, each with its output socket. */
function When({ panel, sockets }: { panel: WhenPanel; sockets: Sockets }) {
  const seen = useSeen();
  return (
    <div className="panel panel-when">
      {panel.rows.length > 0 && (
        <div className="when-grid">
          <div className="panel-head">{panel.title}</div>
          <div className="panel-head">{panel.then}</div>
          {panel.rows.map((r) => (
            <div key={r.id} className={`when-row ${standing(seen, r.id)}`} data-row={r.id}>
              <div className="when-cell">
                <span className="when-words">
                  <Symbol name="hears" />
                  {r.when}
                </span>
                {r.expr && <Expression expr={r.expr} />}
                <Socket socket={sockets.get(r.in)} />
              </div>
              <div className="then-cell">
                {r.then.map((t, k) => (
                  <div key={k} className="then-item">
                    <span className="then-words">{t.words}</span>
                    {t.expr && <Expression expr={t.expr} />}
                  </div>
                ))}
                <Socket socket={sockets.get(r.out)} />
              </div>
            </div>
          ))}
        </div>
      )}
      {panel.record.map((r) => (
        <div key={r.id} className={`record-row ${standing(seen, r.id)}`} data-row={r.id}>
          <span className="record-words">{unbroken(valueOf(seen, r.id))}</span>
          <Socket socket={sockets.get(r.out)} />
        </div>
      ))}
    </div>
  );
}

export function Panel({ panel, node }: { panel: PanelData; node: GraphNode }) {
  const sockets = new Map(node.sockets.map((s) => [s.id, s]));
  if (panel.kind === "text") return <Text panel={panel} />;
  if (panel.kind === "holds") return <Holds panel={panel} />;
  if (panel.kind === "bound") return <Bound panel={panel} sockets={sockets} />;
  return <When panel={panel} sockets={sockets} />;
}
