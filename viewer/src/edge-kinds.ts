// An edge between row handles, along ELK's route, with React Flow's own arrowhead. A kind is
// only a class (edge-heard, edge-wrote, edge-caused, edge-turned-away, edge-plugs) that
// view.css styles; the arrowhead takes the colour of the line as a token variable.
import { MarkerType } from "@xyflow/react";
import tokens from "../../src/conky/tokens.json";
import type { GraphEdge } from "./graph";
import { standing, type Seen } from "./frame-context";
import type { Point, RoutedEdge } from "./components/Edge";

const QUIET = new Set(["caused", "plugs"]); // drawn in mute, as view.css says

function ink(kind: string, pen: string | undefined): string {
  if (pen) return `var(--ds-pen-${tokens.meaning[pen as keyof typeof tokens.meaning]})`;
  return QUIET.has(kind) ? "var(--ds-color-mute)" : "var(--ds-color-ink)";
}

export function edgeOf(e: GraphEdge, seen: Seen, route: { points: Point[]; labelAt: Point | null }): RoutedEdge {
  const pen = seen.frame.pens.get(e.id);
  const stand = standing(seen, e.id);
  return {
    id: e.id,
    type: "routed",
    source: e.source,
    target: e.target,
    sourceHandle: e.sourceRow ? `${e.sourceRow}:out` : "out",
    targetHandle: e.targetRow ? `${e.targetRow}:in` : "in",
    data: { ...route, label: e.label, standing: `edge-label-${e.kind} ${stand}` },
    markerEnd: { type: MarkerType.ArrowClosed, color: ink(e.kind, pen), width: tokens.space.base + tokens.space.fine, height: tokens.space.base + tokens.space.fine },
    className: `edge edge-${e.kind} ${stand}`,
    selectable: false,
    focusable: false,
  };
}
