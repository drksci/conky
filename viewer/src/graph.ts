// The shape of graph.json as bench/dynamics.py writes it, and what a frame of it shows.
// Nothing here classifies or infers: a frame is the steps up to one, applied in order.

export type Mode = "dynamics" | "topology";
/** How much a cell shows: compact in the animations, detailed in the final state and the
 * interactive view. The side panel shows a page in full. */
export type Density = "compact" | "detailed";
/** The edge of a cell a port board sits on: chosen by the layout, never by the record. */
export type Side = "WEST" | "EAST" | "NORTH" | "SOUTH";

export interface Expr {
  reads: string[];
  body: string;
  lines: string[];
}

/** A socket on a cell's port board. `face` says what plugs in: a connector arriving (in) or
 * leaving (out), a slot's standing connection, or, on a space, a connection crossing its wall,
 * with the space's rules judged there. A board lists them in the standard order. */
export interface Socket {
  id: string;
  kind: string; // a key of the socket table in src/conky/tokens.json
  face: "in" | "out" | "slot" | "wall";
  row: string | null;
  order: number;
  label: string;
  mark: number | null; // the small number it shares with its row
  rules: { row: string; says: "yes" | "no"; mark: number }[];
}

/** One stretch of a connection, from a socket to the next: a jumper when it runs inside a
 * space from or to the inner face of the socket on that space's wall. */
export interface Hop {
  id: string;
  source: string;
  sourceSocket: string;
  target: string;
  targetSocket: string;
  within: string | null;
  jumper: boolean;
}

export interface TextPanel {
  kind: "text";
  id: string;
  body: string;
  key: boolean;
}
export interface HoldsPanel {
  kind: "holds";
  title: string;
  more: number;
  rows: { id: string; name: string; key: boolean }[];
}
export interface BoundPanel {
  kind: "bound";
  title: string;
  rows: { id: string; label: string; from: string | null; expr: Expr; mark: number | null; key: boolean }[];
}
export interface WhenRow {
  id: string;
  when: string;
  expr: Expr | null;
  then: { words: string; expr: Expr | null }[];
  mark: number | null;
  key: boolean;
}
export interface WhenPanel {
  kind: "when";
  title: string;
  then: string;
  rows: WhenRow[];
  record: { id: string; mark: number | null; key: boolean }[];
}
export type Panel = TextPanel | HoldsPanel | BoundPanel | WhenPanel;

export interface Slot {
  id: string;
  slot: string;
  label: string;
  filled: boolean;
  socket: string;
  expr: Expr | null;
  key: boolean;
}

export interface GraphNode {
  id: string;
  name: string;
  archetype: string;
  form: "cell" | "space" | "note";
  parent: string | null;
  modes: Mode[];
  header: {
    kinds: string[];
    symbol: string;
    avatar: string | null;
    label: string;
    line: string;
    within: string[];
    known_as: string[];
    thought: string; // ids of values
    refused: string;
  };
  panels: Panel[];
  footer: { slots: Slot[]; members: string | null; changed: string };
  board: Socket[];
  versions: { step: number; source: string }[];
}

export interface GraphEdge {
  id: string;
  kind: string;
  signal: string;
  source: string;
  sourceSocket: string;
  target: string;
  targetSocket: string;
  modes: Mode[];
  hops: Hop[];
}

export interface Region {
  id: string;
  space: string | null;
  kind: "desk" | "shown" | "hidden" | "terms";
  label: string;
  members: string[];
}

export interface Step {
  i: number;
  kind: string;
  symbol: string;
  caption: string;
  arrangement: number;
  appear: string[];
  change: { id: string; value: string }[];
  subject: { id: string; pen: string }[];
  dim: string[];
}

export interface Graph {
  card: string;
  title: string;
  draw: number;
  pens: string[];
  nodes: GraphNode[];
  edges: GraphEdge[];
  values: Record<string, string>;
  arrangements: Region[][];
  steps: Step[];
}

/** What one frame shows: the elements that have appeared, each value as it stands, the pen
 * meaning of each subject, and what is dimmed. In topology every element is shown at its final
 * value. `regions` is the arrangement the frame is drawn in. */
export interface Frame {
  shown: Set<string>;
  values: Map<string, string>;
  pens: Map<string, string>;
  dim: Set<string>;
  plugged: Set<string>; // the sockets a connector shown in this frame plugs into
  regions: Region[];
  step: number;
}

export function lastStep(graph: Graph, mode: Mode, step: number): number {
  return mode === "topology" ? graph.steps.length - 1 : step;
}

export function frame(graph: Graph, mode: Mode, step: number): Frame {
  const last = lastStep(graph, mode, step);
  const shown = new Set<string>();
  const values = new Map<string, string>(Object.entries(graph.values));
  for (const s of graph.steps.slice(0, last + 1)) {
    s.appear.forEach((id) => shown.add(id));
    s.change.forEach((c) => values.set(c.id, c.value));
  }
  const now = graph.steps[last];
  const pens = new Map<string, string>();
  const dim = new Set<string>();
  if (mode === "dynamics" && now) {
    now.subject.forEach((s) => pens.set(s.id, s.pen));
    now.dim.forEach((id) => dim.add(id));
  }
  if (mode === "topology") {
    graph.nodes.forEach((n) => shown.add(n.id));
    hopsOf(graph).forEach((h) => shown.add(h.id));
  }
  return { shown, values, pens, dim, plugged: pluggedIn(graph, shown), regions: graph.arrangements[now?.arrangement ?? 0] ?? [], step: last };
}

/** The frame a cell is measured in before layout: everything shown, and every value at the
 * longest it takes in any step, so the layout leaves room for each value the steps will show. */
export function widest(graph: Graph, regions: Region[]): Frame {
  const values = new Map<string, string>(Object.entries(graph.values));
  for (const s of graph.steps)
    s.change.forEach((c) => {
      if ((values.get(c.id) ?? "").length <= c.value.length) values.set(c.id, c.value); // a tie goes to the later value: a count of 0 draws nothing, 1 does
    });
  const shown = new Set<string>([...graph.nodes.map((n) => n.id), ...values.keys()]);
  hopsOf(graph).forEach((h) => shown.add(h.id));
  return { shown, values, pens: new Map(), dim: new Set(), plugged: pluggedIn(graph, shown), regions, step: graph.steps.length - 1 };
}

/** A cell's panels in a density: every panel in detailed; in compact only the rows that matter
 * to the trial, as the record marks them. */
export function panelsIn(node: GraphNode, density: Density): Panel[] {
  if (density === "detailed") return node.panels;
  const out: Panel[] = [];
  for (const p of node.panels) {
    if (p.kind === "text") {
      if (p.key) out.push(p);
    } else if (p.kind === "when") {
      const rows = p.rows.filter((r) => r.key);
      const record = p.record.filter((r) => r.key);
      if (rows.length || record.length) out.push({ ...p, rows, record });
    } else if (p.kind === "holds") {
      const rows = p.rows.filter((r) => r.key);
      if (rows.length) out.push({ ...p, rows, more: 0 });
    } else {
      const rows = p.rows.filter((r) => r.key);
      if (rows.length) out.push({ ...p, rows });
    }
  }
  return out;
}

export function slotsIn(node: GraphNode, density: Density): Slot[] {
  return density === "detailed" ? node.footer.slots : node.footer.slots.filter((s) => s.key);
}

/** Every hop of a graph's connections. */
export const hopsOf = (graph: Graph): Hop[] => graph.edges.flatMap((e) => e.hops);

/** The sockets a connector shown plugs into: a socket is filled from the step its connector
 * arrives, not before. */
export const pluggedIn = (graph: Graph, shown: Set<string>): Set<string> =>
  new Set(hopsOf(graph).filter((h) => shown.has(h.id)).flatMap((h) => [h.sourceSocket, h.targetSocket]));

/** The sockets something plugs into: the ends of the hops. */
export const wiredIn = (graph: Graph): Set<string> => new Set(hopsOf(graph).flatMap((h) => [h.sourceSocket, h.targetSocket]));

/** The sockets a cell draws on its boards in a density: the slots it shows, and the sockets a
 * connector plugs into, of the rows it shows or of the cell itself. */
export function socketsIn(node: GraphNode, density: Density, wired: Set<string>): Socket[] {
  const slots = new Set(slotsIn(node, density).map((s) => s.socket));
  if (density === "detailed") return node.board.filter((s) => slots.has(s.id) || wired.has(s.id));
  const rows = new Set<string>();
  for (const p of panelsIn(node, density)) {
    if (p.kind === "text") continue;
    p.rows.forEach((r) => rows.add(r.id));
    if (p.kind === "when") p.record.forEach((r) => rows.add(r.id));
  }
  return node.board.filter((s) => slots.has(s.id) || (wired.has(s.id) && (s.row === null || rows.has(s.row))));
}

export function inMode(graph: Graph, mode: Mode): Graph {
  return {
    ...graph,
    nodes: graph.nodes.filter((n) => n.modes.includes(mode)),
    edges: graph.edges.filter((e) => e.modes.includes(mode)),
  };
}

export const densityOf = (mode: Mode): Density => (mode === "dynamics" ? "compact" : "detailed");

/** The region a node is drawn in, if any, in an arrangement. */
export function regionOf(regions: Region[], id: string): Region | undefined {
  return regions.find((r) => r.members.includes(id));
}
