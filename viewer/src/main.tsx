import { createRoot } from "react-dom/client";
import "@xyflow/react/dist/base.css";
import "virtual:tokens.css";
import "./view.css";
import { App } from "./App";
import type { Graph } from "./graph";
import { readParams } from "./params";

const params = readParams();
if (params.theme) document.documentElement.dataset.theme = params.theme;
const root = createRoot(document.getElementById("root")!);

function Missing({ why }: { why: string }) {
  const open = (file: File | undefined) =>
    file?.text().then((text) => root.render(<App graph={JSON.parse(text) as Graph} mode={params.mode} step={params.step} bare={params.bare} />));
  return (
    <div className="missing">
      <p>{why}</p>
      <p>
        Choose a <code>graph.json</code> from <code>docs/results/cards/&lt;card&gt;/</code>, or run <code>npm run view</code> in{" "}
        <code>viewer/</code> and follow the address it prints.
      </p>
      <input type="file" accept="application/json,.json" onChange={(e) => open(e.target.files?.[0])} />
    </div>
  );
}

if (!params.graph) {
  root.render(<Missing why="No graph named: add ?graph=<url of a graph.json> to the address." />);
} else {
  fetch(params.graph)
    .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`${r.status} ${r.statusText}`))))
    .then((graph: Graph) => root.render(<App graph={graph} mode={params.mode} step={params.step} bare={params.bare} />))
    .catch((e: Error) => root.render(<Missing why={`Could not load ${params.graph}: ${e.message}.`} />));
}
