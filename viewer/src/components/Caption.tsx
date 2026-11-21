import type { Graph, Mode } from "../graph";
import { Symbol } from "./Symbol";

/** The line under the graph: which step of how many, and what happens in it in plain words. */
export function Caption({ graph, mode, step }: { graph: Graph; mode: Mode; step: number }) {
  const s = graph.steps[step];
  const words = mode === "topology" ? `${graph.title[0].toUpperCase()}${graph.title.slice(1)}, as it stands at the end.` : s?.caption ?? "";
  return (
    <div className="caption">
      {mode === "dynamics" && (
        <span className="caption-count">
          {step + 1}/{graph.steps.length}
        </span>
      )}
      <span className={`caption-words caption-symbol ${mode === "dynamics" && s?.subject[0] ? `is-${s.subject[0].pen}` : ""}`}>
        <Symbol name={mode === "topology" ? "space" : s?.symbol ?? "space"} />
      </span>
      <span className={`caption-words ${mode === "dynamics" && s?.subject[0] ? `is-${s.subject[0].pen}` : ""}`}>
        {words}
      </span>
    </div>
  );
}
