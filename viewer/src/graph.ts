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

/** A port on a cell's pair of boards. `face` says what plugs in: a connector arriving (in) or
 * leaving (out), a slot's standing connection, or, on a space, a connection crossing its wall,
 * with the space's rules judged there. `pair` is the board of the pair it sits on: inputs the
 * first (left or top), outputs and slots the second. `name` is its short name, its kind's
 * prefix and its index among the cell's ports of that kind. A board lists them in the standard
 * order. */
export interface Socket {
  id: string;
  kind: string; // a key of the socket table in src/conky/tokens.json
  face: "in" | "out" | "slot" | "wall";
  pair: "first" | "second";
  row: string | null;
  order: number;
  name: string;
  label: string;
  rules: { row: string; says: "yes" | "no" }[];
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
  rows: { id: string; label: string; from: string | null; expr: Expr; key: boolean }[];
}
export interface WhenRow {
  id: string;
  when: string;
  expr: Expr | null;
  then: { words: string; expr: Expr | null }[];
  key: boolean;
}
export interface WhenPanel {
  kind: "when";
  title: string;
  then: string;
  rows: WhenRow[];
  record: { id: string; key: boolean }[];
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
  ports: Record<string, { prefix: string; word: string }>; // each kind of port, in the standard order
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
  plugged: Set<string>; // the ports a connector shown in this frame plugs into
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

/** The ports a connector shown plugs into: a port is solid from the step its connector arrives,
 * not before. */
export const pluggedIn = (graph: Graph, shown: Set<string>): Set<string> =>
  new Set(hopsOf(graph).filter((h) => shown.has(h.id)).flatMap((h) => [h.sourceSocket, h.targetSocket]));

/** The ports something plugs into: the ends of the hops. */
export const wiredIn = (graph: Graph): Set<string> => new Set(hopsOf(graph).flatMap((h) => [h.sourceSocket, h.targetSocket]));

/** Whether something is plugged into a port in a frame: a connector shown ending on it, or, for
 * a slot, what stands in it. */
export const isPlugged = (frame: Frame, socket: Socket, slot: Slot | undefined): boolean => (slot ? slot.filled : frame.plugged.has(socket.id));

/** The ports that belong to each row of a cell: a watch entry's input and output, a record
 * row's output, a slot's own port, and the wall ports where a rule was judged. */
export function portsByRow(node: GraphNode): Map<string, Socket[]> {
  const out = new Map<string, Socket[]>();
  const add = (row: string, s: Socket) => out.set(row, [...(out.get(row) ?? []), s]);
  for (const s of node.board) {
    if (s.row) add(s.row, s);
    s.rules.forEach((r) => add(r.row, s));
  }
  return out;
}

/** A graph as one mode draws it: the nodes and edges it shows, and on each wall only the ports a
 * connection it shows crosses by (a wall port exists for its crossing alone). */
export function inMode(graph: Graph, mode: Mode): Graph {
  const edges = graph.edges.filter((e) => e.modes.includes(mode));
  const crossed = new Set(edges.flatMap((e) => e.hops.flatMap((h) => [h.sourceSocket, h.targetSocket])));
  return {
    ...graph,
    nodes: graph.nodes.filter((n) => n.modes.includes(mode)).map((n) => ({ ...n, board: n.board.filter((s) => s.face !== "wall" || crossed.has(s.id)) })),
    edges,
  };
}

export const densityOf = (mode: Mode): Density => (mode === "dynamics" ? "compact" : "detailed");

/** The region a node is drawn in, if any, in an arrangement. */
export function regionOf(regions: Region[], id: string): Region | undefined {
  return regions.find((r) => r.members.includes(id));
}
