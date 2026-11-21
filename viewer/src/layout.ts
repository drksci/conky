// Layout by ELK layered with hierarchy: members laid out inside their space, the notes of a
// crowded space packed in labelled regions, and every hop of a connection routed between two
// ports on port boards. A cell with ports has a pair of boards on one axis: left and right, or
// top and bottom. A first pass with free ports shows which way a cell's connections run, and a
// cell takes the axis most of them run along (a space always left and right, so a jumper never
// crosses its own rows). Inputs sit on the first board of the pair, outputs and slots on the
// second, each board's ports in a row in the standard order. ELK then lays the graph out again
// with those boards as part of the cell. Sizes are what React Flow measured of the cells as
// drawn. Every position comes from ELK or from a board's own fixed measures; this file only
// translates the graph into ELK's terms and back.
import ELK, { type ElkExtendedEdge, type ElkNode, type ElkPort } from "elkjs/lib/elk.bundled.js";
import type { Graph, GraphNode, Region, Side, Socket } from "./graph";
import { hopsOf, wiredIn } from "./graph";
import { GRID_COLUMNS, PORT, REGION_HEAD, SPACE } from "./metrics";
import type { Point } from "./components/Edge";

/** A cell as React Flow measured it before layout: its body, and the band above a space's
 * members and the footer below them, from the top of the body. */
export interface Measured {
  width: number;
  height: number;
  band: number;
  foot: number;
}

/** A port's place on a board, in the cell's coordinates: its block, with the line for its rules
 * above it when a wall shows them. */
export interface Entry {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Board {
  side: Side;
  x: number;
  y: number;
  width: number;
  height: number;
  entries: Entry[];
}

export interface Box {
  x: number; // within its parent
  y: number;
  width: number;
  height: number;
  parent: string | null;
  body: { x: number; y: number; width: number; height: number };
  boards: Board[];
}

export interface Placed {
  nodes: Record<string, Box>;
  edges: Record<string, { points: Point[] }>; // by hop, absolute
  width: number;
  height: number;
}

const elk = new ELK();
const SIDES: Side[] = ["NORTH", "EAST", "SOUTH", "WEST"]; // clockwise, as ELK counts ports
const vertical = (s: Side) => s === "WEST" || s === "EAST";
const PAIRS = { across: ["WEST", "EAST"], down: ["NORTH", "SOUTH"] } as const;
type Axis = keyof typeof PAIRS;

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

/** How long a port's entry is along its board, and how far along it the block's centre is: a
 * block, after the line for its rules where a wall shows them. */
const long = (s: Socket) => PORT.block + (s.rules.length ? PORT.line : 0);
const along = (s: Socket) => long(s) - PORT.block / 2;
/** How long a row of ports is, with a pad at each end. */
const rowLength = (on: Socket[]) => (on.length ? on.reduce((t, s) => t + long(s), 0) + (on.length - 1) * PORT.gap + 2 * PORT.pad : 0);

export async function place(graph: Graph, size: Record<string, Measured>, regions: Region[]): Promise<Placed> {
  const inRegion = new Map(regions.flatMap((r) => r.members.map((m) => [m, r] as const)));
  const members = (parent: string | null) => graph.nodes.filter((n) => n.parent === parent && !inRegion.has(n.id));
  const byId = new Map(graph.nodes.map((n) => [n.id, n]));
  const wired = wiredIn(graph);
  const hops = hopsOf(graph);
  const touched = new Set(hops.flatMap((h) => [h.source, h.target]));
  const apart = (kids: GraphNode[]) => kids.every((k) => !touched.has(k.id) && !members(k.id).length);
  const isSpace = (n: GraphNode) => members(n.id).length > 0 || regions.some((r) => r.space === n.id);

  const side: Record<string, Side> = {}; // each port's edge
  const inset: Record<string, Record<Side, number>> = {};
  const leaf: Record<string, { body: { width: number; height: number }; at: Map<string, Point> }> = {};
  const widen: Record<string, number> = {}; // room on the right of a space, from a first pass

  const portsOf = (n: GraphNode, second: boolean): ElkPort[] => {
    if (!second) return n.board.filter((s) => wired.has(s.id)).map((s) => ({ id: s.id, width: 0, height: 0 }));
    if (!isSpace(n)) {
      const at = leaf[n.id].at;
      return n.board.map((s) => ({ id: s.id, x: at.get(s.id)!.x, y: at.get(s.id)!.y, width: 0, height: 0, layoutOptions: { "elk.port.side": side[s.id] } }));
    }
    // ELK keeps the order of a space's ports only among those with a connection, and puts the
    // rest after them: it is given those, and the boards set every port in its row afterwards
    const round = SIDES.flatMap((d) => {
      const on = n.board.filter((s) => side[s.id] === d && wired.has(s.id));
      return d === "SOUTH" || d === "WEST" ? on.reverse() : on; // clockwise
    });
    return round.map((s, k) => ({ id: s.id, width: 0, height: 0, layoutOptions: { "elk.port.side": side[s.id], "elk.port.index": String(k) } }));
  };
  /** Where each of a space's ports sits along its board: in a row in the standard order, an even
   * gap apart, between the band above its members and its footer, the row placed where its
   * connected ports come closest to where ELK routed their connections. */
  const rowsOf = (n: GraphNode, c: ElkNode): Map<string, number> => {
    const elkAt = new Map((c.ports ?? []).map((p) => [p.id, p.y ?? 0]));
    const out = new Map<string, number>();
    for (const d of PAIRS.across) {
      const on = n.board.filter((s) => side[s.id] === d);
      const offset = new Map<string, number>();
      on.reduce((t, s) => (offset.set(s.id, t + along(s)), t + long(s) + PORT.gap), 0);
      const lo = inset[n.id].NORTH + size[n.id].band + PORT.pad;
      const hi = Math.max(lo, (c.height ?? 0) - inset[n.id].SOUTH - size[n.id].foot - rowLength(on) + PORT.pad);
      const wiredOn = on.filter((s) => elkAt.has(s.id));
      const cost = (start: number) => wiredOn.reduce((t, s) => t + Math.abs(start + offset.get(s.id)! - elkAt.get(s.id)!), 0);
      const starts = [lo, ...wiredOn.map((s) => Math.min(hi, Math.max(lo, elkAt.get(s.id)! - offset.get(s.id)!)))];
      const start = starts.reduce((best, x) => (cost(x) < cost(best) ? x : best), starts[starts.length > 1 ? 1 : 0]);
      on.forEach((s) => out.set(s.id, start + offset.get(s.id)!));
    }
    return out;
  };

  const region = (r: Region, second: boolean): ElkNode => {
    const kids = r.members.map((m) => byId.get(m)).filter((m): m is GraphNode => Boolean(m));
    const first = size[kids[0]?.id] ?? { width: 0, height: 0 };
    return {
      id: r.id,
      layoutOptions: { ...GRID(kids.length, first.width, first.height, GRID_COLUMNS[r.kind]), "elk.priority": String(PRIORITY[r.kind]) },
      children: kids.map((k) => leafNode(k, second)),
    };
  };
  const leafNode = (n: GraphNode, second: boolean): ElkNode => {
    const m = size[n.id];
    if (!second) return { id: n.id, width: m.width, height: m.height, ports: portsOf(n, false), layoutOptions: { "elk.portConstraints": "FREE" } };
    const i = inset[n.id];
    const b = leaf[n.id].body;
    return { id: n.id, width: b.width + i.WEST + i.EAST, height: b.height + i.NORTH + i.SOUTH, ports: portsOf(n, true), layoutOptions: { "elk.portConstraints": "FIXED_POS" } };
  };
  const build = (n: GraphNode, second: boolean): ElkNode => {
    if (!isSpace(n)) return leafNode(n, second);
    const m = size[n.id];
    const i = second ? inset[n.id] : { WEST: 0, EAST: 0, NORTH: 0, SOUTH: 0 };
    const kids = members(n.id);
    const own = regions.filter((r) => r.space === n.id);
    const rows = Math.max(...PAIRS.across.map((d) => rowLength(n.board.filter((s) => side[s.id] === d))));
    return {
      id: n.id,
      ports: portsOf(n, second),
      children: [...kids.map((k) => build(k, second)), ...own.map((r) => region(r, second))],
      layoutOptions: {
        "elk.portConstraints": second ? "FIXED_ORDER" : "FREE",
        ...(second
          ? {
              "elk.spacing.portPort": String(Math.max(...n.board.map(long)) + PORT.gap),
              // ELK keeps ports clear of the padding by itself, and the padding already holds the
              // band above the members and the footer: naming them here too would count them
              // twice, and the member a port connects to would be pulled that far down
              "elk.spacing.portsSurrounding": `[top=${PORT.pad},left=0,bottom=${PORT.pad},right=0]`,
              "elk.nodeSize.constraints": "[MINIMUM_SIZE]",
              "elk.nodeSize.minimum": `(0,${i.NORTH + m.band + rows + m.foot + i.SOUTH})`,
            }
          : {}),
        ...(apart(kids) ? BESIDE : {}),
        "elk.padding": `[top=${i.NORTH + m.band + SPACE.base},left=${i.WEST + SPACE.wide},bottom=${i.SOUTH + m.foot + SPACE.base},right=${i.EAST + SPACE.wide + (widen[n.id] ?? 0)}]`,
      },
    };
  };
  const run = (second: boolean) =>
    elk.layout({
      id: "::root",
      layoutOptions: ROOT,
      children: [...members(null).map((n) => build(n, second)), ...regions.filter((r) => r.space === null).map((r) => region(r, second))],
      edges: hops.map((h) => ({ id: h.id, sources: [h.sourceSocket], targets: [h.targetSocket] }) as ElkExtendedEdge),
    });

  // Pass one: free ports, so that ELK turns each port toward what it connects to.
  const faced: Record<string, Side> = {};
  const facing = (n: ElkNode): void =>
    (n.children ?? []).forEach((c) => {
      for (const p of c.ports ?? []) {
        const w = c.width ?? 0;
        const h = c.height ?? 0;
        const d: [Side, number][] = [["WEST", p.x ?? 0], ["EAST", w - (p.x ?? 0)], ["NORTH", p.y ?? 0], ["SOUTH", h - (p.y ?? 0)]];
        faced[p.id] = d.sort((a, b) => a[1] - b[1])[0][0];
      }
      facing(c);
    });
  facing(await run(false));

  // The pair of boards: on the axis most of a cell's connections run along, inputs first.
  for (const n of graph.nodes) {
    const m = size[n.id];
    if (!m) continue;
    const i = { WEST: 0, EAST: 0, NORTH: 0, SOUTH: 0 } as Record<Side, number>;
    inset[n.id] = i;
    const across = n.board.filter((s) => faced[s.id] && vertical(faced[s.id])).length;
    const down = n.board.filter((s) => faced[s.id] && !vertical(faced[s.id])).length;
    const axis: Axis = isSpace(n) || across >= down ? "across" : "down";
    const [first, second] = PAIRS[axis];
    n.board.forEach((s) => (side[s.id] = s.pair === "first" ? first : second));
    if (!n.board.length) {
      leaf[n.id] = { body: { width: m.width, height: m.height }, at: new Map() };
      continue;
    }
    i[first] = i[second] = PORT.block;
    if (isSpace(n)) continue;
    // A leaf's ports in a row from the start of each board, an even gap apart.
    const at = new Map<string, Point>();
    let { width, height } = m;
    for (const d of [first, second]) {
      const on = n.board.filter((s) => side[s.id] === d);
      let cursor = PORT.pad;
      for (const s of on) {
        at.set(s.id, vertical(d) ? { x: 0, y: cursor + along(s) } : { x: cursor + along(s), y: 0 });
        cursor += long(s) + PORT.gap;
      }
      if (vertical(d)) height = Math.max(height, rowLength(on));
      else width = Math.max(width, rowLength(on));
    }
    const W = width + i.WEST + i.EAST;
    const H = height + i.NORTH + i.SOUTH;
    for (const [id, p] of at) {
      if (side[id] === "EAST") p.x = W;
      if (side[id] === "SOUTH") p.y = H;
      if (side[id] === "NORTH" || side[id] === "SOUTH") p.x += i.WEST;
    }
    leaf[n.id] = { body: { width, height }, at };
  }

  // Pass two. ELK sizes a space around its members and may leave it narrower than its own rows:
  // such a space is given the difference as padding on its right, and laid out once more.
  let done: ElkNode = await run(true);
  const short = (n: ElkNode): void =>
    (n.children ?? []).forEach((c) => {
      const i = inset[c.id];
      const want = size[c.id]?.width ?? 0;
      const has = (c.width ?? 0) - (i ? i.WEST + i.EAST : 0);
      if (c.children?.length && has < want) widen[c.id] = want - has;
      short(c);
    });
  short(done);
  if (Object.keys(widen).length) done = await run(true);

  const placed: Placed = { nodes: {}, edges: {}, width: done.width ?? 0, height: done.height ?? 0 };
  const origin: Record<string, Point> = { "::root": { x: 0, y: 0 } };
  const walk = (n: ElkNode, parent: string | null, at: Point) => {
    for (const c of n.children ?? []) {
      origin[c.id] = { x: at.x + (c.x ?? 0), y: at.y + (c.y ?? 0) };
      const W = c.width ?? 0;
      const H = c.height ?? 0;
      const i = inset[c.id] ?? { WEST: 0, EAST: 0, NORTH: 0, SOUTH: 0 };
      const node = byId.get(c.id);
      const box: Box = { x: c.x ?? 0, y: c.y ?? 0, width: W, height: H, parent, body: { x: i.WEST, y: i.NORTH, width: W - i.WEST - i.EAST, height: H - i.NORTH - i.SOUTH }, boards: [] };
      if (node && size[c.id]) box.boards = boards(node, c, box, i);
      placed.nodes[c.id] = box;
      walk(c, c.id, origin[c.id]);
    }
  };
  /** The pair of boards of a placed cell, each the whole length of its edge, with its ports
   * where ELK or the leaf's own row put them. */
  const boards = (n: GraphNode, c: ElkNode, box: Box, i: Record<Side, number>): Board[] => {
    const port = new Map((c.ports ?? []).map((p) => [p.id, { x: p.x ?? 0, y: p.y ?? 0 }]));
    if (isSpace(n)) rowsOf(n, c).forEach((y, id) => port.set(id, { x: 0, y }));
    const out: Board[] = [];
    for (const d of SIDES) {
      if (!i[d]) continue;
      const t = i[d];
      const entries: Entry[] = n.board
        .filter((s) => side[s.id] === d)
        .map((s) => {
          const p = port.get(s.id)!;
          return vertical(d)
            ? { id: s.id, x: d === "WEST" ? 0 : box.width - t, y: p.y - along(s), width: t, height: long(s) }
            : { id: s.id, x: p.x - t / 2, y: d === "NORTH" ? 0 : box.height - t, width: t, height: t };
        });
      out.push(
        vertical(d)
          ? { side: d, x: d === "WEST" ? 0 : box.width - t, y: 0, width: t, height: box.height, entries }
          : { side: d, x: 0, y: d === "NORTH" ? 0 : box.height - t, width: box.width, height: t, entries },
      );
    }
    return out;
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
