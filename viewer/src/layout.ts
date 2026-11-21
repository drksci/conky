// Layout by ELK layered with hierarchy: members laid out inside their space, the notes of a
// crowded space packed in labelled regions, and every hop of a connection routed between two
// sockets on port boards. ELK chooses the edge of a cell each socket faces in a first pass with
// free ports; each cell then gets a board on each edge that has sockets, and ELK lays the graph
// out again with those boards as part of the cell, the sockets in the standard order. Sizes are
// what React Flow measured of the cells as drawn. Every position comes from ELK or from a
// board's own fixed measures; this file only translates the graph into ELK's terms and back.
import ELK, { type ElkExtendedEdge, type ElkNode, type ElkPort } from "elkjs/lib/elk.bundled.js";
import type { Density, Graph, GraphNode, Region, Side, Socket } from "./graph";
import { hopsOf, socketsIn, wiredIn } from "./graph";
import { BOARD, GRID_COLUMNS, REGION_HEAD, SPACE, THICK } from "./metrics";
import type { Point } from "./components/Edge";

/** A cell as React Flow measured it before layout: its body, the band above a space's members
 * and the footer below them, the bottom of its header, where each row sits (all from the top of
 * the body), and the size of each socket's label as a board prints it. */
export interface Measured {
  width: number;
  height: number;
  band: number;
  foot: number;
  head: number;
  rows: Record<string, { top: number; bottom: number }>;
  labels: Record<string, { width: number; height: number }>;
  sides: Record<string, number>; // the height of each socket's words, wrapped as a side board holds them
}

/** A socket's place on a board, in the cell's coordinates: the box of its socket and label.
 * `tied` when it is not beside its row, so both show the mark they share. */
export interface Entry {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  tied: boolean;
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

/** The box of one socket's entry on a board, and how far along it the socket's centre is. On
 * an edge running up and down, a socket on a space's wall with a label has the label on a line
 * above it, so the jumper that goes on through the wall crosses no words. */
function entrySize(s: Socket, label: { width: number } | undefined, wrapped: number, side: Side, density: Density) {
  const lw = label?.width ?? 0;
  if (!vertical(side)) return { w: BOARD.socket + (lw ? BOARD.gap + lw : 0), h: BOARD.line, along: BOARD.socket / 2 };
  const w = THICK.side[density] - BOARD.pad;
  const lh = lw ? Math.max(BOARD.line, wrapped) : 0;
  if (s.face === "wall" && lw) return { w, h: lh + BOARD.line, along: lh + BOARD.line / 2 };
  return { w, h: Math.max(BOARD.line, lh), along: BOARD.line / 2 };
}

type Sized = Socket & { w: number; h: number; along: number };

export async function place(graph: Graph, size: Record<string, Measured>, regions: Region[], density: Density): Promise<Placed> {
  const inRegion = new Map(regions.flatMap((r) => r.members.map((m) => [m, r] as const)));
  const members = (parent: string | null) => graph.nodes.filter((n) => n.parent === parent && !inRegion.has(n.id));
  const byId = new Map(graph.nodes.map((n) => [n.id, n]));
  const wired = wiredIn(graph);
  const drawn = new Map(graph.nodes.map((n) => [n.id, socketsIn(n, density, wired)]));
  const hops = hopsOf(graph);
  const touched = new Set(hops.flatMap((h) => [h.source, h.target]));
  const apart = (kids: GraphNode[]) => kids.every((k) => !touched.has(k.id) && !members(k.id).length);
  const isSpace = (n: GraphNode) => members(n.id).length > 0 || regions.some((r) => r.space === n.id);

  // Pass one: free ports, so that ELK turns each socket to face what it connects to.
  const side: Record<string, Side> = {};
  const inset: Record<string, Record<Side, number>> = {};
  const leaf: Record<string, { body: { width: number; height: number }; entries: Map<string, { x: number; y: number; side: Side }> }> = {};
  const sized: Record<string, Sized[]> = {};
  const widen: Record<string, number> = {}; // room on the right of a space, from a first pass

  const portsOf = (n: GraphNode, second: boolean): ElkPort[] => {
    const all = (drawn.get(n.id) ?? []).filter((s) => wired.has(s.id));
    if (!second) return all.map((s) => ({ id: s.id, width: 0, height: 0 }));
    if (!isSpace(n)) {
      const at = leaf[n.id].entries;
      return all.map((s) => ({ id: s.id, x: at.get(s.id)!.x, y: at.get(s.id)!.y, width: 0, height: 0, layoutOptions: { "elk.port.side": side[s.id] } }));
    }
    const round = SIDES.flatMap((d) => {
      const on = all.filter((s) => side[s.id] === d);
      return d === "SOUTH" || d === "WEST" ? on.reverse() : on; // clockwise
    });
    return round.map((s, k) => ({ id: s.id, width: 0, height: 0, layoutOptions: { "elk.port.side": side[s.id], "elk.port.index": String(k) } }));
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
    const pitch = Math.max(BOARD.line, ...(sized[n.id] ?? []).filter((s) => vertical(side[s.id])).map((s) => s.h)) + BOARD.gap;
    return {
      id: n.id,
      ports: portsOf(n, second),
      children: [...kids.map((k) => build(k, second)), ...own.map((r) => region(r, second))],
      layoutOptions: {
        "elk.portConstraints": second ? "FIXED_ORDER" : "FREE",
        ...(second ? { "elk.spacing.portPort": String(pitch), "elk.spacing.portsSurrounding": `[top=${i.NORTH + m.band + BOARD.pad},left=0,bottom=${i.SOUTH + m.foot + BOARD.pad},right=0]` } : {}),
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

  const facing = (n: ElkNode): void =>
    (n.children ?? []).forEach((c) => {
      const space = byId.has(c.id) && isSpace(byId.get(c.id)!);
      for (const p of c.ports ?? []) {
        const w = c.width ?? 0;
        const h = c.height ?? 0;
        const d: [Side, number][] = [["WEST", p.x ?? 0], ["EAST", w - (p.x ?? 0)], ["NORTH", p.y ?? 0], ["SOUTH", h - (p.y ?? 0)]];
        let s = d.sort((a, b) => a[1] - b[1])[0][0];
        if (space && !vertical(s)) s = (p.x ?? 0) < w / 2 ? "WEST" : "EAST"; // a crossing never runs through a space's own rows
        side[p.id] = s;
      }
      facing(c);
    });
  facing(await run(false));

  // The boards: a socket nothing plugs into sits on the bottom board, beside the slot it is.
  for (const n of graph.nodes) {
    const m = size[n.id];
    if (!m) continue;
    const all = (drawn.get(n.id) ?? []).map((s) => {
      const d = side[s.id] ?? "SOUTH";
      side[s.id] = d;
      return { ...s, ...entrySize(s, m.labels[s.id], m.sides[s.id] ?? 0, d, density) };
    });
    sized[n.id] = all;
    const i = { WEST: 0, EAST: 0, NORTH: 0, SOUTH: 0 } as Record<Side, number>;
    for (const d of SIDES) {
      const on = all.filter((s) => side[s.id] === d);
      if (on.length) i[d] = vertical(d) ? THICK.side[density] : THICK.across;
    }
    inset[n.id] = i;
    if (isSpace(n)) continue;
    // A leaf's sockets beside their rows where the standard order allows, else just after.
    const entries = new Map<string, { x: number; y: number; side: Side }>();
    let height = m.height;
    let width = m.width;
    for (const d of ["WEST", "EAST"] as Side[]) {
      let cursor = i.NORTH + m.head + BOARD.pad;
      for (const s of all.filter((x) => side[x.id] === d)) {
        const row = s.row ? m.rows[s.row] : undefined;
        const want = row ? i.NORTH + (row.top + row.bottom) / 2 - s.along : cursor;
        const top = Math.max(cursor, want);
        entries.set(s.id, { x: 0, y: top + s.along, side: d }); // x set below, once the width is known
        cursor = top + s.h + BOARD.gap;
      }
      height = Math.max(height, cursor - BOARD.gap + BOARD.pad - i.NORTH);
    }
    for (const d of ["NORTH", "SOUTH"] as Side[]) {
      let cursor = i.WEST + BOARD.pad;
      for (const s of all.filter((x) => side[x.id] === d)) {
        entries.set(s.id, { x: cursor + s.along, y: 0, side: d });
        cursor += s.w + 2 * BOARD.gap;
      }
      width = Math.max(width, cursor - 2 * BOARD.gap + BOARD.pad - i.WEST);
    }
    const W = width + i.WEST + i.EAST;
    const H = height + i.NORTH + i.SOUTH;
    for (const e of entries.values()) {
      if (e.side === "EAST") e.x = W;
      if (e.side === "SOUTH") e.y = H;
    }
    leaf[n.id] = { body: { width, height }, entries };
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
  /** The boards of a placed cell, around the entries of its sockets. */
  const boards = (n: GraphNode, c: ElkNode, box: Box, i: Record<Side, number>): Board[] => {
    const m = size[n.id];
    const port = new Map((c.ports ?? []).map((p) => [p.id, { x: p.x ?? 0, y: p.y ?? 0 }]));
    const at = leaf[n.id]?.entries;
    const out: Board[] = [];
    for (const d of SIDES) {
      const on = sized[n.id].filter((s) => side[s.id] === d);
      if (!on.length) continue;
      const entries: Entry[] = [];
      let cursor = i.WEST + BOARD.pad; // where a socket nothing plugs into goes, after the rest
      for (const s of on) {
        const p = at?.get(s.id) ?? port.get(s.id) ?? { x: cursor + s.along, y: box.height };
        if (vertical(d)) {
          const y = p.y - s.along;
          const x = d === "WEST" ? 0 : box.width - s.w;
          const row = s.row ? m.rows[s.row] : undefined;
          const tied = s.mark !== null && !(row && p.y >= i.NORTH + row.top && p.y <= i.NORTH + row.bottom);
          entries.push({ id: s.id, x, y, width: s.w, height: s.h, tied });
        } else {
          const x = p.x - s.along;
          entries.push({ id: s.id, x, y: d === "NORTH" ? 0 : box.height - s.h, width: s.w, height: s.h, tied: s.mark !== null });
          cursor = Math.max(cursor, x + s.w + 2 * BOARD.gap);
        }
      }
      const t = i[d];
      out.push(
        vertical(d)
          ? { side: d, x: d === "WEST" ? 0 : box.width - t, y: i.NORTH, width: t, height: box.height - i.NORTH - i.SOUTH, entries }
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
