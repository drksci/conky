// Layout by ELK layered with hierarchy: members laid out inside their space, the notes of a
// crowded space packed in labelled regions, edges running between fixed-side sockets with their
// labels placed outside the cell. Sizes and socket positions are what React Flow measured of
// the cells as drawn. Every position comes from ELK; this file only translates the graph into
// ELK's terms and back, and tunes ELK's options.
import ELK, { type ElkExtendedEdge, type ElkNode, type ElkPort } from "elkjs/lib/elk.bundled.js";
import type { Density, Graph, GraphNode, Region } from "./graph";
import { socketsIn } from "./graph";
import { GRID_COLUMNS, REGION_HEAD, SPACE } from "./metrics";
import type { Point } from "./components/Edge";

export interface Port {
  id: string; // a socket id, which is also the React Flow handle id
  side: "WEST" | "EAST" | "SOUTH";
  x: number;
  y: number;
  label: { width: number; height: number };
}

export interface Measured {
  width: number;
  height: number;
  ports: Port[];
  band: number; // for a space: the height of its header and panels above its members
  foot: number; // for a space: the height of its footer below them
}

export interface Placed {
  nodes: Record<string, { x: number; y: number; width: number; height: number; parent: string | null }>; // x, y within parent
  labels: Record<string, Record<string, Point>>; // by node, each socket label's place within it
  edges: Record<string, { points: Point[] }>; // absolute
  width: number;
  height: number;
}

const elk = new ELK();

const ROOT = {
  "elk.algorithm": "layered",
  "elk.direction": "RIGHT",
  "elk.hierarchyHandling": "INCLUDE_CHILDREN",
  "elk.edgeRouting": "ORTHOGONAL",
  "elk.layered.nodePlacement.strategy": "BRANDES_KOEPF",
  "elk.layered.considerModelOrder.strategy": "NODES_AND_EDGES",
  "elk.layered.spacing.nodeNodeBetweenLayers": String(SPACE.far + SPACE.wide),
  "elk.layered.spacing.edgeNodeBetweenLayers": String(SPACE.wide),
  "elk.spacing.nodeNode": String(SPACE.wide + SPACE.base),
  "elk.spacing.edgeNode": String(SPACE.wide),
  "elk.spacing.edgeEdge": String(SPACE.base),
  "elk.spacing.labelPortHorizontal": String(SPACE.hair),
  "elk.spacing.labelPortVertical": String(SPACE.hair),
  "elk.portLabels.placement": "OUTSIDE",
  "elk.padding": `[top=${SPACE.base},left=${SPACE.far},bottom=${SPACE.wide},right=${SPACE.far}]`,
};

/** The regions of a crowded space, or members nothing connects, side by side in order. */
const BESIDE = {
  "elk.algorithm": "box",
  "elk.box.packingMode": "SIMPLE",
  "elk.hierarchyHandling": "SEPARATE_CHILDREN",
  "elk.spacing.nodeNode": String(SPACE.wide),
  "elk.aspectRatio": "4",
};

/** The order regions are packed in: what the space was shown, then the rest. */
const PRIORITY: Record<string, number> = { shown: 3, desk: 2, hidden: 1, terms: 0 };

/** The members of a region, packed by ELK's box layout into rows of about ten. */
const GRID = (count: number, w: number, h: number, columns: number) => ({
  "elk.algorithm": "box",
  "elk.box.packingMode": "SIMPLE",
  "elk.spacing.nodeNode": String(SPACE.fine),
  "elk.padding": `[top=${REGION_HEAD},left=${SPACE.base},bottom=${SPACE.base},right=${SPACE.base}]`,
  "elk.aspectRatio": String((Math.min(count, columns) * (w + SPACE.fine)) / (Math.ceil(count / columns) * (h + SPACE.fine))),
});

export async function place(graph: Graph, size: Record<string, Measured>, regions: Region[], density: Density): Promise<Placed> {
  const inRegion = new Map(regions.flatMap((r) => r.members.map((m) => [m, r] as const)));
  const members = (parent: string | null) => graph.nodes.filter((n) => n.parent === parent && !inRegion.has(n.id));
  const widen: Record<string, number> = {}; // room on the right of a space, from a first pass
  const byId = new Map(graph.nodes.map((n) => [n.id, n]));

  const ports = (n: GraphNode): ElkPort[] => {
    const drawn = new Set(socketsIn(n, density).map((s) => s.id));
    return size[n.id].ports
      .filter((p) => drawn.has(p.id))
      .map((p) => ({
        id: p.id,
        x: p.x,
        y: p.y,
        width: 0,
        height: 0,
        labels: p.side === "SOUTH" ? [] : [{ id: `${p.id}::label`, text: p.id, ...p.label }], // a slot's label is in the cell
        layoutOptions: { "elk.port.side": p.side },
      }));
  };
  const region = (r: Region): ElkNode => {
    const kids = r.members.map((m) => byId.get(m)).filter((m): m is GraphNode => Boolean(m));
    const first = size[kids[0]?.id] ?? { width: 0, height: 0 };
    return {
      id: r.id,
      layoutOptions: { ...GRID(kids.length, first.width, first.height, GRID_COLUMNS[r.kind]), "elk.priority": String(PRIORITY[r.kind]) },
      children: kids.map((k) => ({ id: k.id, width: size[k.id].width, height: size[k.id].height, ports: ports(k), layoutOptions: { "elk.portConstraints": "FIXED_POS" } })),
    };
  };
  // Members no connector touches are packed side by side in a grid rather than in layers.
  const touched = new Set(graph.edges.flatMap((e) => [e.source, e.target]));
  const apart = (kids: GraphNode[]) => kids.every((k) => !touched.has(k.id) && !members(k.id).length);
  const build = (n: GraphNode): ElkNode => {
    const m = size[n.id];
    const base: ElkNode = { id: n.id, ports: ports(n), layoutOptions: { "elk.portConstraints": "FIXED_POS" } };
    const kids = members(n.id);
    const own = regions.filter((r) => r.space === n.id);
    if (!kids.length && !own.length) return { ...base, width: m.width, height: m.height };
    return {
      ...base,
      children: [...kids.map(build), ...own.map(region)],
      layoutOptions: {
        ...base.layoutOptions,
        ...(apart(kids) ? BESIDE : {}),
        "elk.padding": `[top=${m.band + SPACE.base},left=${SPACE.wide},bottom=${m.foot + SPACE.base},right=${SPACE.wide + (widen[n.id] ?? 0)}]`,
      },
    };
  };

  const edges = (): ElkExtendedEdge[] => graph.edges.map((e) => ({ id: e.id, sources: [e.sourceSocket], targets: [e.targetSocket] }));
  const run = () =>
    elk.layout({
      id: "::root",
      layoutOptions: ROOT,
      children: [...members(null).map(build), ...regions.filter((r) => r.space === null).map(region)],
      edges: edges(),
    });

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

  const placed: Placed = { nodes: {}, labels: {}, edges: {}, width: done.width ?? 0, height: done.height ?? 0 };
  const origin: Record<string, Point> = { "::root": { x: 0, y: 0 } };
  const walk = (n: ElkNode, parent: string | null, at: Point) => {
    for (const c of n.children ?? []) {
      placed.nodes[c.id] = { x: c.x ?? 0, y: c.y ?? 0, width: c.width ?? 0, height: c.height ?? 0, parent };
      origin[c.id] = { x: at.x + (c.x ?? 0), y: at.y + (c.y ?? 0) };
      placed.labels[c.id] = {};
      for (const p of c.ports ?? []) {
        const l = p.labels?.[0];
        if (l) placed.labels[c.id][p.id] = { x: (p.x ?? 0) + (l.x ?? 0), y: (p.y ?? 0) + (l.y ?? 0) };
      }
      walk(c, c.id, origin[c.id]);
    }
  };
  walk(done, null, { x: 0, y: 0 });
  // An edge's route is relative to the node ELK names as its container.
  for (const e of (done.edges ?? []) as (ElkExtendedEdge & { container?: string })[]) {
    const o = origin[e.container ?? "::root"] ?? { x: 0, y: 0 };
    const s = e.sections?.[0];
    const at = (p: Point) => ({ x: p.x + o.x, y: p.y + o.y });
    placed.edges[e.id] = { points: s ? [s.startPoint, ...(s.bendPoints ?? []), s.endPoint].map(at) : [] };
  }
  return placed;
}
