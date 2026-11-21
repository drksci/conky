import { BaseEdge, type Edge as FlowEdge, type EdgeProps } from "@xyflow/react";
import { SPACE } from "../metrics";

const JOG = SPACE.wide; // how far before a border a route turns onto its socket
const NEAR = SPACE.fine; // an end this close to its socket is moved onto it, keeping square corners
const PLUG = SPACE.fine + SPACE.hair; // the length of the plug a connector ends in

export interface Point {
  x: number;
  y: number;
}

/** `plugs`: the ends a plug is seated at. A jumper has none at a wall: it goes on from the
 * socket there, through the wall. */
export type RoutedEdge = FlowEdge<{ points: Point[]; plugs: { source: boolean; target: boolean } }, "routed">;

const horizontal = (a: Point, b: Point) => Math.abs(a.y - b.y) < 0.5;

/** ELK's route with its ends on the sockets React Flow drew. An end a little off its socket is
 * moved onto it with the next corner, so the route stays square. ELK moves a port on the border
 * of a space it lays out with its members away from the place it was given; where an end is
 * far off, the route keeps ELK's way and turns to the socket just before the border it enters,
 * in the gap ELK left there. */
export function onto(points: Point[], s: Point, t: Point, down: boolean): Point[] {
  if (points.length < 2) {
    if (Math.abs(s.y - t.y) < 1) return [s, t];
    if (down) return [s, { x: s.x, y: t.y }, t];
    const mx = (s.x + t.x) / 2;
    return [s, { x: mx, y: s.y }, { x: mx, y: t.y }, t];
  }
  const p = points.map((c) => ({ ...c }));
  const fix = (end: number, next: number, to: Point): Point[] | null => {
    const a = p[end];
    if (Math.abs(a.x - to.x) > NEAR || Math.abs(a.y - to.y) > NEAR) return null;
    if (p.length > 2) {
      if (horizontal(a, p[next])) p[next].y = to.y;
      else p[next].x = to.x;
    }
    p[end] = { ...to };
    return [];
  };
  const head = fix(0, 1, s) ?? (down ? [s, { x: s.x, y: s.y + JOG }, { x: p[0].x, y: s.y + JOG }] : [s, { x: s.x + JOG, y: s.y }, { x: s.x + JOG, y: p[0].y }]);
  const last = p.length - 1;
  const tail = fix(last, last - 1, t) ?? [{ x: t.x - JOG, y: p[last].y }, { x: t.x - JOG, y: t.y }, t];
  const mid = head.length ? p.slice(1) : p;
  const body = tail.length ? mid.slice(0, -1) : mid;
  return [...head, ...body, ...tail].filter((q, k, all) => k === 0 || q.x !== all[k - 1].x || q.y !== all[k - 1].y);
}

/** The plug a connector ends in: a short squared tip along the last segment, seated in the
 * socket. */
function plug(points: Point[]): string {
  const t = points[points.length - 1];
  const b = points[points.length - 2] ?? t;
  const len = Math.hypot(t.x - b.x, t.y - b.y) || 1;
  const k = Math.min(PLUG, len) / len;
  return `M${t.x - (t.x - b.x) * k},${t.y - (t.y - b.y) * k} L${t.x},${t.y}`;
}

/** One hop of a connector along the route ELK found for it, drawn by React Flow's own
 * BaseEdge from socket to socket and ending in a plug. Its line is by kind and its pen by the
 * signal it carries, both classes on the edge. */
export function RoutedEdgeView({ data, sourceX, sourceY, targetX, targetY, sourcePosition }: EdgeProps<RoutedEdge>) {
  const points = onto(data?.points ?? [], { x: sourceX, y: sourceY }, { x: targetX, y: targetY }, sourcePosition === "bottom");
  const path = points.map((p, k) => `${k ? "L" : "M"}${p.x},${p.y}`).join(" ");
  return (
    <>
      <BaseEdge path={path} />
      {data?.plugs.target && <path className="edge-plug" d={plug(points)} />}
      {data?.plugs.source && <path className="edge-plug edge-plug-source" d={plug([...points].reverse())} />}
    </>
  );
}

export const EDGE_TYPES = { routed: RoutedEdgeView };
