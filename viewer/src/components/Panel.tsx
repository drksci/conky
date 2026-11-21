import tokens from "../../../src/conky/tokens.json";
import type { BoundPanel, HoldsPanel, Panel as PanelData, TextPanel, WhenPanel } from "../graph";
import { standing, useSeen, valueOf } from "../frame-context";
import { Expression } from "./Expression";
import { Symbol } from "./Symbol";

/** The small numbers rows share with their sockets on a board, by row. */
type Ties = Map<string, number>;

/** The number a row shares with its socket, when the socket is not beside it. */
const Tie = ({ id, ties }: { id: string; ties: Ties }) => (ties.has(id) ? <span className="row-tie">{ties.get(id)}</span> : null);

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
function Bound({ panel, ties }: { panel: BoundPanel; ties: Ties }) {
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
            <Tie id={r.id} ties={ties} />
          </div>
          <Expression expr={r.expr} />
        </div>
      ))}
    </div>
  );
}

/** The heart of a cell: one row a watch entry in two aligned columns, "when" (what it listens
 * for, with its condition) and "then" (what it does); then the rows from the record that no
 * watch entry explains. Their sockets are on the cell's boards. */
function When({ panel, ties }: { panel: WhenPanel; ties: Ties }) {
  const seen = useSeen();
  return (
    <div className="panel panel-when">
      {panel.rows.length > 0 && (
        <div className="when-grid">
          <div className="panel-head">{panel.title}</div>
          <div className="panel-head">{panel.then}</div>
          {panel.rows.map((r) => (
            <div key={r.id} className={`when-row ${standing(seen, r.id)}`}>
              <div className="when-cell" data-row={r.id}>
                <span className="when-words">
                  <Symbol name="hears" />
                  {r.when}
                </span>
                {r.expr && <Expression expr={r.expr} />}
                <Tie id={r.id} ties={ties} />
              </div>
              <div className="then-cell">
                {r.then.map((t, k) => (
                  <div key={k} className="then-item">
                    <span className="then-words">{t.words}</span>
                    {t.expr && <Expression expr={t.expr} />}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
      {panel.record.map((r) => (
        <div key={r.id} className={`record-row ${standing(seen, r.id)}`} data-row={r.id}>
          <span className="record-words">{unbroken(valueOf(seen, r.id))}</span>
          <Tie id={r.id} ties={ties} />
        </div>
      ))}
    </div>
  );
}

export function Panel({ panel, ties }: { panel: PanelData; ties: Ties }) {
  if (panel.kind === "text") return <Text panel={panel} />;
  if (panel.kind === "holds") return <Holds panel={panel} />;
  if (panel.kind === "bound") return <Bound panel={panel} ties={ties} />;
  return <When panel={panel} ties={ties} />;
}
