// The shape of graph.json as bench/dynamics.py writes it, and what a frame of it shows.
// Nothing here classifies or infers: a frame is the steps up to one, applied in order.

export type Mode = "dynamics" | "topology";
/** How much a cell shows: compact in the animations, detailed in the final state and the
 * interactive view. The side panel shows a page in full. */
export type Density = "compact" | "detailed";
export type Side = "WEST" | "EAST" | "SOUTH";

export interface Expr {
  reads: string[];
  body: string;
  lines: string[];
}

export interface Socket {
  id: string;
  kind: string; // a key of the socket table in src/conky/tokens.json
  side: Side;
  row: string | null;
  order: number;
  plugged: boolean;
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
  rows: { id: string; label: string; from: string | null; expr: Expr; in: string | null; key: boolean }[];
}
export interface WhenRow {
  id: string;
  when: string;
  expr: Expr | null;
  then: { words: string; expr: Expr | null }[];
  in: string;
  out: string;
  key: boolean;
}
export interface WhenPanel {
  kind: "when";
  title: string;
  then: string;
  rows: WhenRow[];
  record: { id: string; out: string; key: boolean }[];
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
  sockets: Socket[];
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
    graph.edges.forEach((e) => shown.add(e.id));
  }
  return { shown, values, pens, dim, regions: graph.arrangements[now?.arrangement ?? 0] ?? [], step: last };
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
  graph.edges.forEach((e) => shown.add(e.id));
  return { shown, values, pens: new Map(), dim: new Set(), regions, step: graph.steps.length - 1 };
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

/** The sockets a cell draws in a density: those of the rows and slots it shows, and its own. */
export function socketsIn(node: GraphNode, density: Density): Socket[] {
  if (density === "detailed") return node.sockets;
  const rows = new Set<string>();
  for (const p of panelsIn(node, density)) {
    if (p.kind === "text") continue;
    p.rows.forEach((r) => rows.add(r.id));
    if (p.kind === "when") p.record.forEach((r) => rows.add(r.id));
  }
  slotsIn(node, density).forEach((s) => rows.add(s.id));
  return node.sockets.filter((s) => (s.row === null ? s.plugged : rows.has(s.row)));
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
