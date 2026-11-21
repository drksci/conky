import tokens from "../../../src/conky/tokens.json";
import type { BoundPanel, HoldsPanel, Panel as PanelData, Socket, TextPanel, WhenPanel } from "../graph";
import { standing, useSeen, valueOf } from "../frame-context";
import { Expression } from "./Expression";
import { PortTags } from "./Port";
import { Symbol } from "./Symbol";

/** The ports of a cell's rows, by row. */
type Ports = Map<string, Socket[]>;

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
 * comes from, and each with its function block. A space's own rule for its members carries the
 * names of the ports on its wall where it judged a write. */
function Bound({ panel, ports }: { panel: BoundPanel; ports: Ports }) {
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
            <PortTags ports={ports.get(r.id)} />
          </div>
          <Expression expr={r.expr} />
        </div>
      ))}
    </div>
  );
}

/** The heart of a cell: one row a watch entry in two aligned columns, "when" (what it listens
 * for, with its condition) and "then" (what it does); then the rows from the record that no
 * watch entry explains. A watch entry's input is named at the end of its "when", its output at
 * the end of its "then", and a record row's port at its end. */
function When({ panel, ports }: { panel: WhenPanel; ports: Ports }) {
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
                <PortTags ports={ports.get(r.id)?.filter((s) => s.face === "in")} />
              </div>
              <div className="then-cell">
                {r.then.map((t, k) => (
                  <div key={k} className="then-item">
                    <span className="then-words">{t.words}</span>
                    {t.expr && <Expression expr={t.expr} />}
                  </div>
                ))}
                <PortTags ports={ports.get(r.id)?.filter((s) => s.face !== "in")} />
              </div>
            </div>
          ))}
        </div>
      )}
      {panel.record.map((r) => (
        <div key={r.id} className={`record-row ${standing(seen, r.id)}`} data-row={r.id}>
          <span className="record-words">{unbroken(valueOf(seen, r.id))}</span>
          <PortTags ports={ports.get(r.id)} />
        </div>
      ))}
    </div>
  );
}

export function Panel({ panel, ports }: { panel: PanelData; ports: Ports }) {
  if (panel.kind === "text") return <Text panel={panel} />;
  if (panel.kind === "holds") return <Holds panel={panel} />;
  if (panel.kind === "bound") return <Bound panel={panel} ports={ports} />;
  return <When panel={panel} ports={ports} />;
}
