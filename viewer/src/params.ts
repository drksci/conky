// The address of a view: ?graph=<url>&mode=dynamics|topology&step=N&theme=light|dark&bare=1
import type { Mode } from "./graph";

export interface Params {
  graph: string | null;
  mode: Mode;
  step: number | null;
  theme: "light" | "dark" | null;
  bare: boolean;
}

export function readParams(search: string = window.location.search): Params {
  const q = new URLSearchParams(search);
  const step = q.get("step");
  const theme = q.get("theme");
  return {
    graph: q.get("graph"),
    mode: q.get("mode") === "topology" ? "topology" : "dynamics",
    step: step !== null && /^\d+$/.test(step) ? Number(step) : null,
    theme: theme === "light" || theme === "dark" ? theme : null,
    bare: q.get("bare") === "1",
  };
}
