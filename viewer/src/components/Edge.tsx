import { BaseEdge, EdgeLabelRenderer, type Edge as FlowEdge, type EdgeProps } from "@xyflow/react";
import { SPACE } from "../metrics";

const JOG = SPACE.wide; // how far before a border a route turns onto its handle

export interface Point {
  x: number;
  y: number;
}

export type RoutedEdge = FlowEdge<{ points: Point[]; label: string; labelAt: Point | null; standing: string }, "routed">;

/** ELK's route with its ends on the handles React Flow drew. ELK moves a port on the border of
 * a space it lays out with its members (a hierarchical port) away from the fixed position it was
 * given, so an edge into a space's row would end beside the row. Where an end is off its
 * handle, the route keeps ELK's way and turns to the handle just before the border it enters,
 * in the gap ELK left there, so it stays square and clear of the other routes. */
export function onto(points: Point[], s: Point, t: Point): Point[] {
  if (points.length < 2) {
    if (Math.abs(s.y - t.y) < 1) return [s, t];
    const mx = (s.x + t.x) / 2;
    return [s, { x: mx, y: s.y }, { x: mx, y: t.y }, t];
  }
  const p = points.map((c) => ({ ...c }));
  const off = (a: Point, b: Point) => Math.abs(a.y - b.y) >= 1 || Math.abs(a.x - b.x) >= 1;
  const head: Point[] = off(p[0], s) ? [s, { x: s.x + JOG, y: s.y }, { x: s.x + JOG, y: p[0].y }] : [s];
  const tail: Point[] = off(p[p.length - 1], t) ? [{ x: t.x - JOG, y: p[p.length - 1].y }, { x: t.x - JOG, y: t.y }, t] : [t];
  return [...head, ...p.slice(1, -1), ...tail];
}

/** An edge along the route ELK found for it, drawn by React Flow's own BaseEdge with its own
 * arrowhead. React Flow's step and bezier edges draw a path of their own between the handles,
 * which crosses other edges and puts labels on top of each other; ELK's route and label place
 * avoid both, so this edge only hands them to BaseEdge. Kind and pen are classes on the edge. */
export function RoutedEdgeView({ data, markerEnd, sourceX, sourceY, targetX, targetY }: EdgeProps<RoutedEdge>) {
  const points = onto(data?.points ?? [], { x: sourceX, y: sourceY }, { x: targetX, y: targetY });
  const path = points.map((p, k) => `${k ? "L" : "M"}${p.x},${p.y}`).join(" ");
  return (
    <>
      <BaseEdge path={path} markerEnd={markerEnd} />
      {data?.labelAt && (
        <EdgeLabelRenderer>
          <div className={`edge-label ${data.standing}`} style={{ transform: `translate(${data.labelAt.x}px, ${data.labelAt.y}px)` }}>
            {data.label}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
}

export const EDGE_TYPES = { routed: RoutedEdgeView };
