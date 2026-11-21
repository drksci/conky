// Layout by ELK layered with hierarchy: members laid out inside their space, edges leaving from
// the port of the row they belong to, heard things to the left of who hears them. Sizes and port
// positions are what React Flow measured of the cells as drawn. Every position comes from ELK;
// this file only translates the graph into ELK's terms and back, and tunes ELK's options.
import ELK, { type ElkExtendedEdge, type ElkNode, type ElkPort } from "elkjs/lib/elk.bundled.js";
import type { Graph, GraphNode } from "./graph";
import { GRID_COLUMNS, SPACE } from "./metrics";
import type { Point } from "./components/Edge";

export interface Port {
  id: string; // a React Flow handle id
  side: "WEST" | "EAST";
  x: number;
  y: number;
}

export interface Measured {
  width: number;
  height: number;
  ports: Port[];
}

export interface Placed {
  nodes: Record<string, { x: number; y: number; width: number; height: number }>; // x, y within parent
  edges: Record<string, { points: Point[]; labelAt: Point | null }>; // absolute
  width: number;
  height: number;
}

const elk = new ELK();

const ROOT = {
  "elk.algorithm": "layered",
  "elk.direction": "RIGHT",
  "elk.hierarchyHandling": "INCLUDE_CHILDREN",
  "elk.edgeRouting": "ORTHOGONAL",
  "elk.layered.nodePlacement.strategy": "NETWORK_SIMPLEX",
  "elk.layered.spacing.nodeNodeBetweenLayers": String(SPACE.far + SPACE.wide),
  "elk.layered.spacing.edgeNodeBetweenLayers": String(SPACE.wide),
  "elk.spacing.nodeNode": String(SPACE.wide),
  "elk.spacing.edgeNode": String(SPACE.wide),
  "elk.spacing.edgeEdge": String(SPACE.base),
  "elk.spacing.edgeLabel": String(SPACE.fine),
  "elk.edgeLabels.placement": "CENTER",
  "elk.padding": `[top=${SPACE.base},left=${SPACE.base},bottom=${SPACE.base},right=${SPACE.base}]`,
};

/** The many notes of a crowded space, packed by ELK's box layout into rows of about ten. */
const GRID = (count: number, w: number, h: number) => ({
  "elk.algorithm": "box",
  "elk.spacing.nodeNode": String(SPACE.fine),
  "elk.padding": "[top=0,left=0,bottom=0,right=0]",
  "elk.aspectRatio": String((Math.min(count, GRID_COLUMNS) * (w + SPACE.fine)) / (Math.ceil(count / GRID_COLUMNS) * (h + SPACE.fine))),
});

const port = (row: string) => (handle: string) => `${row}#${handle}`;

export async function place(
  graph: Graph,
  size: Record<string, Measured>,
  labels: Record<string, { width: number; height: number }>,
): Promise<Placed> {
  const members = (parent: string | null) => graph.nodes.filter((n) => n.parent === parent);
  const widen: Record<string, number> = {}; // room on the right of a space, from a first pass

  const used = new Set(
    graph.edges.flatMap((e) => [port(e.source)(e.sourceRow ? `${e.sourceRow}:out` : "out"), port(e.target)(e.targetRow ? `${e.targetRow}:in` : "in")]),
  );
  const build = (n: GraphNode): ElkNode => {
    const m = size[n.id];
    const ports: ElkPort[] = m.ports.filter((p) => used.has(port(n.id)(p.id))).map((p) => ({
      id: port(n.id)(p.id),
      x: p.x,
      y: p.y,
      width: 0,
      height: 0,
      layoutOptions: { "elk.port.side": p.side },
    }));
    const base: ElkNode = { id: n.id, ports, layoutOptions: { "elk.portConstraints": "FIXED_POS" } };
    const kids = members(n.id).filter((k) => k.form !== "note");
    const notes = members(n.id).filter((k) => k.form === "note");
    if (!kids.length && !notes.length) return { ...base, width: m.width, height: m.height };
    const children = kids.map(build);
    if (notes.length) {
      const note = size[notes[0].id];
      children.push({
        id: `${n.id}::grid`,
        layoutOptions: GRID(notes.length, note.width, note.height),
        children: notes.map((k) => ({ id: k.id, width: size[k.id].width, height: size[k.id].height })),
      });
    }
    return {
      ...base,
      children,
      layoutOptions: {
        ...base.layoutOptions,
        "elk.padding": `[top=${m.height + SPACE.base},left=${SPACE.wide},bottom=${SPACE.wide},right=${SPACE.wide + (widen[n.id] ?? 0)}]`,
      },
    };
  };

  const edges = (): ElkExtendedEdge[] =>
    graph.edges.map((e) => ({
      id: e.id,
      sources: [port(e.source)(e.sourceRow ? `${e.sourceRow}:out` : "out")],
      targets: [port(e.target)(e.targetRow ? `${e.targetRow}:in` : "in")],
      labels: labels[e.id] ? [{ id: `${e.id}::label`, text: e.label, ...labels[e.id] }] : [],
    }));
  const run = () => elk.layout({ id: "::root", layoutOptions: ROOT, children: members(null).map(build), edges: edges() });

  // ELK sizes a space around its members and may leave it narrower than its own rows: such a
  // space is given the difference as padding on its right, and laid out once more.
  let done: ElkNode = await run();
  const short = (n: ElkNode): void =>
    (n.children ?? []).forEach((c) => {
      const want = size[c.id]?.width ?? 0;
      if (c.children?.length && (c.width ?? 0) < want) widen[c.id] = want - (c.width ?? 0);
      short(c);
    });
  short(done);
  if (Object.keys(widen).length) done = await run();

  const placed: Placed = { nodes: {}, edges: {}, width: done.width ?? 0, height: done.height ?? 0 };
  const origin: Record<string, Point> = { "::root": { x: 0, y: 0 } };
  const walk = (n: ElkNode, dx: number, dy: number, at: Point = { x: 0, y: 0 }) => {
    for (const c of n.children ?? []) {
      if (c.id.endsWith("::grid")) {
        walk(c, dx + (c.x ?? 0), dy + (c.y ?? 0), { x: at.x + (c.x ?? 0), y: at.y + (c.y ?? 0) }); // its notes belong to the space around it
        continue;
      }
      placed.nodes[c.id] = { x: dx + (c.x ?? 0), y: dy + (c.y ?? 0), width: c.width ?? 0, height: c.height ?? 0 };
      origin[c.id] = { x: at.x + (c.x ?? 0), y: at.y + (c.y ?? 0) };
      walk(c, 0, 0, origin[c.id]);
    }
  };
  walk(done, 0, 0);
  // An edge's route and label are relative to the node ELK names as its container.
  for (const e of (done.edges ?? []) as (ElkExtendedEdge & { container?: string })[]) {
    const o = origin[e.container ?? "::root"] ?? { x: 0, y: 0 };
    const s = e.sections?.[0];
    const at = (p: Point) => ({ x: p.x + o.x, y: p.y + o.y });
    const l = e.labels?.[0];
    placed.edges[e.id] = {
      points: s ? [s.startPoint, ...(s.bendPoints ?? []), s.endPoint].map(at) : [],
      labelAt: l ? at({ x: l.x ?? 0, y: l.y ?? 0 }) : null,
    };
  }
  return placed;
}
