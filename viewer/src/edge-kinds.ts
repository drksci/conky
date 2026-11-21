// One hop of a connector, between two sockets on port boards. Its connector's kind (edge-heard,
// edge-wrote, edge-caused, edge-turned-away, edge-asks) sets the line and its signal
// (signal-<kind>, from the socket table) the pen, both classes that view.css styles; a jumper,
// the hop inside a space's wall, is also .is-jumper.
import type { GraphEdge, Hop } from "./graph";
import { standing, type Seen } from "./frame-context";
import type { Point, RoutedEdge } from "./components/Edge";

export function edgeOf(e: GraphEdge, h: Hop, seen: Seen, route: { points: Point[] } | undefined, walls: Set<string>): RoutedEdge {
  return {
    id: h.id,
    type: "routed",
    source: h.source,
    target: h.target,
    sourceHandle: h.sourceSocket,
    targetHandle: h.targetSocket,
    data: { points: route?.points ?? [], plugs: { source: !(h.jumper && walls.has(h.sourceSocket)), target: !(h.jumper && walls.has(h.targetSocket)) } },
    className: `edge edge-${e.kind} signal-${e.signal} ${h.jumper ? "is-jumper" : ""} ${standing(seen, h.id)}`,
    selectable: false,
    focusable: false,
  };
}
