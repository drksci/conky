import tokens from "../../../src/conky/tokens.json";
import { densityOf, panelsIn, type Graph, type Mode } from "../graph";
import { Symbol, wordOf } from "./Symbol";

/** The key to the picture, small and quiet under the caption: the symbols it uses, each with
 * its word, then the kinds of port it draws, each a chip in its colour with the prefix its
 * ports' names start with and the word it stands for, and last how a port looks with nothing
 * plugged in. The table comes from graph.json. */
export function Legend({ graph, mode }: { graph: Graph; mode: Mode }) {
  const density = densityOf(mode);
  const used = [
    ...graph.nodes.map((n) => n.header.symbol),
    ...graph.nodes.flatMap((n) => panelsIn(n, density).map((p) => ({ holds: "fields", bound: "rule", when: "hears", text: "page" })[p.kind])),
    ...graph.steps.map((s) => s.symbol),
  ];
  const names = [...new Set(used)];
  const kinds = new Set(graph.nodes.flatMap((n) => n.board.map((s) => s.kind)));
  const ports = Object.entries(graph.ports).filter(([k]) => kinds.has(k));
  return (
    <div className="legend">
      <div className="legend-line">
        {names.map((name) => (
          <span key={name} className="legend-item">
            <Symbol name={name} />
            {wordOf(name)}
          </span>
        ))}
      </div>
      {ports.length > 0 && (
        <div className="legend-line">
          {ports.map(([k, p]) => (
            <span key={k} className="legend-item">
              <span className={`port-tag signal-${k}`}>{p.prefix}</span>
              {p.word}
            </span>
          ))}
          <span className="legend-item">
            <span className={`port-tag signal-${ports[0][0]} is-idle`}>{ports[0][1].prefix}</span>
            {tokens.words.idle}
          </span>
        </div>
      )}
    </div>
  );
}
