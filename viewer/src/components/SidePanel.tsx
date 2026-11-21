import { useMemo, useState } from "react";
import { marked } from "marked";
import hljs from "highlight.js/lib/core";
import yaml from "highlight.js/lib/languages/yaml";
import markdown from "highlight.js/lib/languages/markdown";
import tokens from "../../../src/conky/tokens.json";
import type { GraphNode } from "../graph";
import { PortTag } from "./Port";

hljs.registerLanguage("yaml", yaml);
hljs.registerLanguage("markdown", markdown);

/** The page as it stood at a step: the last version written at or before it. */
export function sourceAt(node: GraphNode, step: number): string {
  let source = "";
  for (const v of node.versions) if (v.step <= step) source = v.source;
  return source;
}

/** A source split into its frontmatter and its Markdown body. */
function split(source: string): { head: string; body: string } {
  const m = /^---\n([\s\S]*?)\n?---\n?([\s\S]*)$/.exec(source);
  return m ? { head: m[1], body: m[2] } : { head: "", body: source };
}

/** The side panel of the interactive view, loaded only when a cell is first opened: the page in
 * full as of the current step, rendered as a small printed article (Markdown by marked) or as
 * its source, frontmatter and Markdown highlighted by highlight.js in a theme built from the
 * tokens in view.css. Above the page, every port it has by its short name, solid or hatched as
 * it stands at the step. Nothing is capped here. */
export default function SidePanel({ node, step, onClose }: { node: GraphNode; step: number; onClose: () => void }) {
  const [tab, setTab] = useState<"page" | "source">("page");
  const slots = new Map(node.footer.slots.map((s) => [s.socket, s]));
  const source = sourceAt(node, step);
  const { head, body } = split(source);
  const article = useMemo(() => marked.parse(body, { async: false }) as string, [body]);
  const lit = useMemo(
    () => ({
      head: hljs.highlight(head, { language: "yaml" }).value,
      body: hljs.highlight(body, { language: "markdown" }).value,
    }),
    [head, body],
  );
  return (
    <aside className="side" data-side-panel={node.id}>
      <header className="side-head">
        <span className="side-name">{node.name}</span>
        <span className="side-kind">{node.header.kinds.join(" · ")}</span>
        <button type="button" className="side-close" onClick={onClose}>
          close
        </button>
      </header>
      {node.board.length > 0 && (
        <ul className="side-ports" aria-label={tokens.words.ports}>
          {node.board.map((s) => (
            <li key={s.id} className="side-port">
              <PortTag socket={s} slot={slots.get(s.id)} />
              {s.label}
            </li>
          ))}
        </ul>
      )}
      <nav className="side-tabs">
        {(["page", "source"] as const).map((t) => (
          <button key={t} type="button" className={`side-tab ${tab === t ? "is-on" : ""}`} onClick={() => setTab(t)}>
            {t}
          </button>
        ))}
      </nav>
      {!source && <p className="side-empty">Not written yet at this step.</p>}
      {source && tab === "page" && (
        <article className="side-page">
          <h1>{node.name}</h1>
          {body.trim() ? <div dangerouslySetInnerHTML={{ __html: article }} /> : <p className="side-empty">No text.</p>}
        </article>
      )}
      {source && tab === "source" && (
        <pre className="side-source hljs">
          <span className="hljs-meta">---</span>
          {"\n"}
          <span dangerouslySetInnerHTML={{ __html: lit.head }} />
          {"\n"}
          <span className="hljs-meta">---</span>
          {"\n"}
          <span dangerouslySetInnerHTML={{ __html: lit.body }} />
        </pre>
      )}
    </aside>
  );
}
