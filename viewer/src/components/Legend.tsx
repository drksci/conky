import { panelsIn, type Graph, type Mode } from "../graph";
import { Symbol, wordOf } from "./Symbol";

/** The symbols this picture uses, each with its word: small and quiet, under the caption. */
export function Legend({ graph, mode }: { graph: Graph; mode: Mode }) {
  const used = [
    ...graph.nodes.map((n) => n.symbol),
    ...graph.nodes.flatMap((n) => panelsIn(n, mode).map((p) => p.symbol)),
    ...graph.steps.map((s) => s.symbol),
  ];
  const names = [...new Set(used)];
  return (
    <div className="legend">
      {names.map((name) => (
        <span key={name} className="legend-item">
          <Symbol name={name} />
          {wordOf(name)}
        </span>
      ))}
    </div>
  );
}
