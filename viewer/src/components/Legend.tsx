import tokens from "../../../src/conky/tokens.json";
import { densityOf, panelsIn, socketsIn, wiredIn, type Graph, type Mode } from "../graph";
import { socketLabel } from "./Socket";
import { Symbol, wordOf } from "./Symbol";

/** The key to the picture, small and quiet under the caption: the symbols it uses, each with
 * its word, then the sockets it draws, each with its mark and what its colour carries. */
export function Legend({ graph, mode }: { graph: Graph; mode: Mode }) {
  const density = densityOf(mode);
  const used = [
    ...graph.nodes.map((n) => n.header.symbol),
    ...graph.nodes.flatMap((n) => panelsIn(n, density).map((p) => ({ holds: "fields", bound: "rule", when: "hears", text: "page" })[p.kind])),
    ...graph.steps.map((s) => s.symbol),
  ];
  const names = [...new Set(used)];
  const wired = wiredIn(graph);
  const kinds = new Set(graph.nodes.flatMap((n) => socketsIn(n, density, wired).map((s) => s.kind)));
  const sockets = Object.keys(tokens.socket).filter((k) => kinds.has(k));
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
      {sockets.length > 0 && (
        <div className="legend-line">
          {sockets.map((k) => (
            <span key={k} className={`legend-item signal-${k}`}>
              <span className="legend-socket" />
              {density === "compact" && <span className="legend-mark">{socketLabel(k, "compact")}</span>}
              {socketLabel(k, "detailed")}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
