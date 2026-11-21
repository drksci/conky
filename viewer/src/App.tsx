import { lazy, Suspense, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { ReactFlow, ReactFlowProvider, useReactFlow, type Node } from "@xyflow/react";
import { densityOf, frame, inMode, lastStep, widest, type Graph, type GraphNode, type Mode, type Region } from "./graph";
import { FrameContext, type Seen } from "./frame-context";
import { NODE_TYPES, typeOf } from "./node-types";
import { edgeOf } from "./edge-kinds";
import { EDGE_TYPES } from "./components/Edge";
import { Caption } from "./components/Caption";
import { Scrubber } from "./components/Scrubber";
import { Legend } from "./components/Legend";
import { socketLabel } from "./components/Socket";
import type { CellData } from "./components/Cell";
import { place, type Measured, type Placed, type Port } from "./layout";
import { MAX_ZOOM, MIN_ZOOM, SHEET, SPACE } from "./metrics";

const SidePanel = lazy(() => import("./components/SidePanel"));

declare global {
  interface Window {
    conky?: { ready: boolean; width: number; height: number; steps: number; step: (n: number) => Promise<void> };
  }
}

const nextFrame = () => new Promise<void>((done) => requestAnimationFrame(() => requestAnimationFrame(() => done())));
const BOUNDS = "::bounds"; // an empty node as large as the layout, so the view fits its margins too
const ROUNDS = 2; // a layout is redone at most this many times when a cell's content outgrew it

/** Wait until React Flow has measured every node and drawn every edge, and the fonts are in. */
function useDrawn(nodes: number, edges: number, key: unknown): boolean {
  const flow = useReactFlow();
  const [ready, setReady] = useState(false);
  useEffect(() => {
    let live = true;
    setReady(false);
    const look = () => {
      if (!live) return;
      const measured = flow.getNodes().filter((n) => flow.getInternalNode(n.id)?.measured.width).length === nodes;
      const drawn = document.querySelectorAll(".view-graph .react-flow__edge").length >= edges;
      if (measured && drawn) document.fonts.ready.then(nextFrame).then(() => live && setReady(true));
      else requestAnimationFrame(look);
    };
    look();
    return () => {
      live = false;
    };
  }, [flow, nodes, edges, key]);
  return ready;
}

/** The React Flow nodes of a graph in one arrangement, parents before their members: a crowded
 * space's regions come right after it and its notes sit in them; term pages sit in theirs. */
function flowNodes(graph: Graph, regions: Region[], placed: Placed | null): Node[] {
  const inRegion = new Map(regions.flatMap((r) => r.members.map((m) => [m, r.id] as const)));
  const out: Node[] = [];
  const box = (id: string) => (placed ? placed.nodes[id] : null);
  const at = (id: string, parent: string | null) => {
    const p = box(id);
    return {
      position: { x: p?.x ?? 0, y: p?.y ?? 0 },
      ...(p ? { width: p.width, height: p.height } : {}),
      ...(parent ? { parentId: parent, extent: "parent" as const } : {}),
      draggable: false,
      selectable: false,
    };
  };
  const regionNode = (r: Region): Node => ({ id: r.id, type: "region", data: { region: r }, ...at(r.id, r.space), zIndex: -1 });
  if (placed) out.push({ id: BOUNDS, type: "bounds", data: {}, position: { x: 0, y: 0 }, width: placed.width, height: placed.height, draggable: false, selectable: false });
  regions.filter((r) => r.space === null).forEach((r) => out.push(regionNode(r)));
  for (const n of graph.nodes) {
    const parent = inRegion.get(n.id) ?? n.parent;
    out.push({ id: n.id, type: typeOf(n.form, n.archetype), data: { node: n, labels: placed?.labels[n.id] } satisfies CellData, ...at(n.id, parent) });
    regions.filter((r) => r.space === n.id).forEach((r) => out.push(regionNode(r)));
  }
  // React Flow wants a parent before its children: regions of a space follow the space, and
  // members follow it in the record's order already; notes move behind their region.
  const order = new Map(out.map((n, k) => [n.id, k]));
  return out.sort((a, b) => {
    const depth = (n: Node): number => (n.parentId ? 1 + depth(out[order.get(n.parentId)!]) : 0);
    return depth(a) - depth(b) || order.get(a.id)! - order.get(b.id)!;
  });
}

/** Draw every cell once, placed nowhere and unseen, with each value at its longest, and read
 * back what React Flow measured: each cell's size, where its sockets sit, the band above a
 * space's members and its footer below them, and the size of each socket's label. */
function Measure({ graph, seen, onDone }: { graph: Graph; seen: Seen; onDone: (size: Record<string, Measured>) => void }) {
  const box = useRef<HTMLDivElement>(null);
  const nodes = useMemo(
    () =>
      flowNodes(graph, seen.frame.regions, null)
        .filter((n) => n.type !== "region")
        .map((n) => ({ ...n, parentId: undefined, extent: undefined })),
    [graph, seen],
  );
  const ready = useDrawn(nodes.length, 0, graph);
  useLayoutEffect(() => {
    if (!ready || !box.current) return;
    const size: Record<string, Measured> = {};
    const labels = new Map<string, { width: number; height: number }>();
    box.current.querySelectorAll<HTMLElement>("[data-socket-label]").forEach((l) => {
      const r = l.getBoundingClientRect();
      labels.set(l.dataset.socketLabel!, { width: Math.ceil(r.width), height: Math.ceil(r.height) });
    });
    for (const n of graph.nodes) {
      const cell = box.current.querySelector<HTMLElement>(`[data-cell="${CSS.escape(n.id)}"]`);
      if (!cell) continue;
      const c = cell.getBoundingClientRect();
      const width = Math.ceil(c.width);
      const height = Math.ceil(c.height);
      const ports: Port[] = [];
      cell.querySelectorAll<HTMLElement>("[data-socket]").forEach((el) => {
        const r = el.getBoundingClientRect();
        const side = el.dataset.side as Port["side"];
        const kind = n.sockets.find((s) => s.id === el.dataset.socket)?.kind ?? "";
        const label = labels.get(kind) ?? { width: 0, height: 0 };
        if (side === "SOUTH") ports.push({ id: el.dataset.socket!, side, x: r.left + r.width / 2 - c.left, y: height, label });
        else ports.push({ id: el.dataset.socket!, side, x: side === "WEST" ? 0 : width, y: r.top + r.height / 2 - c.top, label });
      });
      const members = cell.querySelector<HTMLElement>("[data-members]");
      const band = members ? Math.ceil(members.getBoundingClientRect().top - c.top) : 0;
      size[n.id] = { width, height, ports, band, foot: members ? height - band : 0 };
    }
    onDone(size);
  }, [ready, onDone, graph]);
  const kinds = [...new Set(graph.nodes.flatMap((n) => n.sockets.map((s) => s.kind)))];
  return (
    <div className="measure" ref={box} aria-hidden>
      <FrameContext.Provider value={seen}>
        <ReactFlow nodes={nodes} edges={[]} nodeTypes={NODE_TYPES} defaultViewport={{ x: 0, y: 0, zoom: 1 }} proOptions={{ hideAttribution: true }} />
      </FrameContext.Provider>
      {kinds.map((k) => (
        <span key={k} className="socket-label" data-socket-label={k}>
          {socketLabel(k, seen.density)}
        </span>
      ))}
    </div>
  );
}

/** Cells whose content came out larger than the box the layout gave them, with what they need. */
function outgrown(root: HTMLElement, placed: Placed): Record<string, { width: number; height: number }> {
  const out: Record<string, { width: number; height: number }> = {};
  root.querySelectorAll<HTMLElement>(".react-flow__node [data-cell]").forEach((el) => {
    const id = el.dataset.cell!;
    const p = placed.nodes[id];
    if (!p || el.querySelector("[data-members]")) return;
    if (el.scrollWidth > el.clientWidth + 0.5 || el.scrollHeight > el.clientHeight + 0.5)
      out[id] = { width: p.width + el.scrollWidth - el.clientWidth, height: p.height + el.scrollHeight - el.clientHeight };
  });
  return out;
}

function Drawn({ graph, placed, seen, bare, onReady, onOutgrown }: { graph: Graph; placed: Placed; seen: Seen; bare: boolean; onReady: () => void; onOutgrown: (grow: Record<string, { width: number; height: number }>) => boolean }) {
  const flow = useReactFlow();
  const box = useRef<HTMLDivElement>(null);
  const nodes = useMemo(() => flowNodes(graph, seen.frame.regions, placed), [graph, seen.frame.regions, placed]);
  const edges = useMemo(() => graph.edges.map((e) => edgeOf(e, seen, placed.edges[e.id])), [graph, seen, placed]);
  const ready = useDrawn(nodes.length, edges.length, placed);
  useEffect(() => {
    if (!ready || !box.current) return;
    const grow = outgrown(box.current, placed);
    if (Object.keys(grow).length && onOutgrown(grow)) return;
    flow.fitView({ padding: bare ? 0.02 : 0.05, minZoom: MIN_ZOOM, maxZoom: MAX_ZOOM }).then(nextFrame).then(onReady);
  }, [ready, bare, flow, onReady, onOutgrown, placed]);
  return (
    <div className="view-flow" ref={box}>
      <FrameContext.Provider value={seen}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={NODE_TYPES}
          edgeTypes={EDGE_TYPES}
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable={false}
          panOnDrag={!bare}
          zoomOnScroll={!bare}
          zoomOnDoubleClick={false}
          onNodeClick={seen.open ? (_, n) => n.type !== "region" && n.type !== "bounds" && seen.open!(n.id) : undefined}
          minZoom={MIN_ZOOM / 2}
          proOptions={{ hideAttribution: bare }}
        />
      </FrameContext.Provider>
    </div>
  );
}

/** The sheet a bare picture is drawn on: the README's width at most, the graph's shape, and a
 * small graph left at a legible zoom rather than blown up. fitView then scales into it. */
function sheet(placed: Placed) {
  const wide = Math.min(SHEET, placed.width * MAX_ZOOM);
  const zoom = Math.max(MIN_ZOOM, wide / placed.width);
  return { width: Math.ceil(placed.width * zoom) + SPACE.base, height: Math.ceil(placed.height * zoom) + SPACE.base };
}

export function App({ graph: whole, mode: firstMode, step: firstStep, bare }: { graph: Graph; mode: Mode; step: number | null; bare: boolean }) {
  const [mode, setMode] = useState<Mode>(firstMode);
  const graph = useMemo(() => inMode(whole, mode), [whole, mode]);
  const last = whole.steps.length - 1;
  const [step, setStep] = useState(Math.min(firstStep ?? (bare ? 0 : last), last));
  const [opened, setOpened] = useState<string | null>(null);
  const density = densityOf(mode);
  const arrangement = whole.steps[lastStep(whole, mode, step)]?.arrangement ?? 0;
  const regions = whole.arrangements[arrangement] ?? [];
  const layoutKey = `${mode}:${arrangement}`;
  const [placed, setPlaced] = useState<Record<string, Placed>>({});
  const sizes = useRef<Record<string, Record<string, Measured>>>({});
  const rounds = useRef<Record<string, number>>({});
  const [readyFor, setReadyFor] = useState<string | null>(null);
  const shown = useRef<() => void>(() => {});
  const [asked, setAsked] = useState(0); // each call of window.conky.step, so asking again still answers
  const open = useCallback((id: string) => setOpened(id), []);
  const seen: Seen = useMemo(
    () => ({ frame: frame(graph, mode, step), mode, density, open: bare ? undefined : open }),
    [graph, mode, step, density, bare, open],
  );
  const measuring: Seen = useMemo(() => ({ frame: widest(graph, regions), mode, density }), [graph, regions, mode, density]);
  const layOut = useCallback(
    (size: Record<string, Measured>) => {
      sizes.current[layoutKey] = size;
      place(graph, size, regions, density)
        .then((p) => setPlaced((all) => ({ ...all, [layoutKey]: p })))
        .catch((e: Error) => console.error(`the layout failed: ${e.message}`));
    },
    [graph, regions, density, layoutKey],
  );
  const onOutgrown = useCallback(
    (grow: Record<string, { width: number; height: number }>) => {
      const done = rounds.current[layoutKey] ?? 0;
      if (done >= ROUNDS) {
        console.error(`cells outgrew their layout: ${Object.keys(grow).join(", ")}`);
        return false;
      }
      rounds.current[layoutKey] = done + 1;
      const size = { ...sizes.current[layoutKey] };
      for (const [id, g] of Object.entries(grow)) size[id] = { ...size[id], width: Math.ceil(g.width), height: Math.ceil(g.height) };
      layOut(size);
      return true;
    },
    [layoutKey, layOut],
  );
  useEffect(() => {
    setPlaced({});
    sizes.current = {};
    rounds.current = {};
  }, [graph]);
  const now = placed[layoutKey];
  useEffect(() => {
    if (!now || !bare) return;
    const s = sheet(now);
    document.documentElement.style.setProperty("--view-width", `${s.width}px`);
    document.documentElement.style.setProperty("--view-height", `${s.height}px`);
  }, [now, bare]);
  const onReady = useCallback(() => {
    setReadyFor(layoutKey);
    if (!now) return;
    window.conky = {
      ready: true,
      width: now.width,
      height: now.height,
      steps: whole.steps.length,
      step: (n: number) =>
        new Promise<void>((done) => {
          shown.current = () => nextFrame().then(done);
          setStep(n);
          setAsked((k) => k + 1);
        }),
    };
  }, [now, whole, layoutKey]);
  useEffect(() => {
    if (readyFor === layoutKey && now) shown.current();
  }, [step, asked, readyFor, layoutKey, now]);
  const node = opened ? whole.nodes.find((n) => n.id === opened) : undefined;
  return (
    <div className={`view view-${mode} ${bare ? "is-bare" : ""}`}>
      {!bare && (
        <header className="view-head">
          <span className="view-title">{whole.title}</span>
          <span className="view-draw">draw {whole.draw}</span>
        </header>
      )}
      <div className="view-body">
        <div className="view-graph">
          <ReactFlowProvider key={`${layoutKey}:${now ? "drawn" : "measure"}:${opened ? "beside" : "alone"}`}>
            {now ? (
              <Drawn graph={graph} placed={now} seen={seen} bare={bare} onReady={onReady} onOutgrown={onOutgrown} />
            ) : (
              <Measure graph={graph} seen={measuring} onDone={layOut} />
            )}
          </ReactFlowProvider>
        </div>
        {node && (
          <Suspense fallback={<aside className="side" />}>
            <SidePanel node={node as GraphNode} step={seen.frame.step} onClose={() => setOpened(null)} />
          </Suspense>
        )}
      </div>
      <Caption graph={whole} mode={mode} step={step} />
      <Legend graph={graph} mode={mode} />
      {!bare && <Scrubber steps={whole.steps.length} step={step} mode={mode} onStep={setStep} onMode={setMode} />}
    </div>
  );
}
