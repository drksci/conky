// The shape of graph.json as bench/dynamics.py writes it, and what a frame of it shows.
// Nothing here classifies or infers: a frame is the steps up to one, applied in order.

export type Mode = "dynamics" | "topology";

export interface Row {
  id: string;
  name: string;
  value: string;
  key: boolean;
  expr: { reads: string[]; body: string } | null;
}

export interface Panel {
  kind: "fields" | "rules" | "hears" | "plugs";
  title: string;
  symbol: string;
  more: number;
  rows: Row[];
}

export interface GraphNode {
  id: string;
  name: string;
  archetype: string;
  kind: string;
  symbol: string;
  form: "cell" | "space" | "note";
  label: string;
  parent: string | null;
  avatar: string | null;
  refused: boolean;
  modes: Mode[];
  panels: Panel[];
}

export interface GraphEdge {
  id: string;
  kind: string;
  label: string;
  source: string;
  sourceRow: string | null;
  target: string;
  targetRow: string | null;
  modes: Mode[];
}

export interface Step {
  i: number;
  kind: string;
  symbol: string;
  caption: string;
  appear: string[];
  change: { row: string; value: string }[];
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
  steps: Step[];
}

/** What one frame shows: the elements that have appeared, each row's value, the pen meaning of
 * each subject, and what is dimmed. In topology every element is shown at its final value. */
export interface Frame {
  shown: Set<string>;
  values: Map<string, string>;
  pens: Map<string, string>;
  dim: Set<string>;
}

export function frame(graph: Graph, mode: Mode, step: number): Frame {
  const last = mode === "topology" ? graph.steps.length - 1 : step;
  const shown = new Set<string>();
  const values = new Map<string, string>();
  for (const node of graph.nodes) for (const p of node.panels) for (const r of p.rows) values.set(r.id, r.value);
  for (const s of graph.steps.slice(0, last + 1)) {
    s.appear.forEach((id) => shown.add(id));
    s.change.forEach((c) => values.set(c.row, c.value));
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
  return { shown, values, pens, dim };
}

/** The frame a cell is measured in before layout: everything shown, and every row at the longest
 * value it takes in any step, so the layout leaves room for each value the steps will show. */
export function widest(graph: Graph): Frame {
  const values = new Map<string, string>();
  const keep = (row: string, value: string) => {
    if ((values.get(row) ?? "").length < value.length) values.set(row, value);
  };
  for (const node of graph.nodes) for (const p of node.panels) for (const r of p.rows) keep(r.id, r.value);
  for (const s of graph.steps) s.change.forEach((c) => keep(c.row, c.value));
  const shown = new Set<string>([...graph.nodes.map((n) => n.id), ...values.keys()]);
  return { shown, values, pens: new Map(), dim: new Set() };
}

/** The panels a cell shows in a mode: every panel in topology; in dynamics only the rows that
 * matter to the trial, as the record marks them. */
export function panelsIn(node: GraphNode, mode: Mode): Panel[] {
  if (mode === "topology") return node.panels;
  return node.panels
    .map((p) => ({ ...p, more: 0, rows: p.rows.filter((r) => r.key) }))
    .filter((p) => p.rows.length > 0);
}

export function inMode(graph: Graph, mode: Mode): Graph {
  return {
    ...graph,
    nodes: graph.nodes.filter((n) => n.modes.includes(mode)),
    edges: graph.edges.filter((e) => e.modes.includes(mode)),
  };
}
