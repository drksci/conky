// A connector between two sockets, along ELK's route. Its kind (edge-heard, edge-wrote,
// edge-caused, edge-turned-away, edge-asks) sets the line and its signal (signal-<kind>, from
// the socket table) the pen, both classes that view.css styles.
import type { GraphEdge } from "./graph";
import { standing, type Seen } from "./frame-context";
import type { Point, RoutedEdge } from "./components/Edge";

export function edgeOf(e: GraphEdge, seen: Seen, route: { points: Point[] } | undefined): RoutedEdge {
  const stand = standing(seen, e.id);
  return {
    id: e.id,
    type: "routed",
    source: e.source,
    target: e.target,
    sourceHandle: e.sourceSocket,
    targetHandle: e.targetSocket,
    data: { points: route?.points ?? [], kind: e.kind, standing: stand },
    className: `edge edge-${e.kind} signal-${e.signal} ${stand}`,
    selectable: false,
    focusable: false,
  };
}
