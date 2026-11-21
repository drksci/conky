import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { ReactFlow, ReactFlowProvider, useReactFlow, type Node } from "@xyflow/react";
import { frame, inMode, widest, type Graph, type Mode } from "./graph";
import { FrameContext } from "./frame-context";
import { NODE_TYPES, typeOf } from "./node-types";
import { edgeOf } from "./edge-kinds";
import { EDGE_TYPES } from "./components/Edge";
import { Caption } from "./components/Caption";
import { Scrubber } from "./components/Scrubber";
import { Legend } from "./components/Legend";
import type { CellData } from "./components/Cell";
import { place, type Measured, type Placed } from "./layout";
import { MAX_ZOOM, MIN_ZOOM, SHEET, SPACE } from "./metrics";

declare global {
  interface Window {
    conky?: { ready: boolean; width: number; height: number; steps: number; step: (n: number) => Promise<void> };
  }
}

const nextFrame = () => new Promise<void>((done) => requestAnimationFrame(() => requestAnimationFrame(() => done())));
type Sizes = Record<string, { width: number; height: number }>;

/** Wait until React Flow has measured every node and drawn every edge. */
function useDrawn(nodes: number, edges: number, key: unknown): boolean {
  const flow = useReactFlow();
  const [ready, setReady] = useState(false);
  useEffect(() => {
    let live = true;
    const look = () => {
      const measured = flow.getNodes().filter((n) => flow.getInternalNode(n.id)?.measured.width).length === nodes;
      const drawn = document.querySelectorAll(".react-flow__edge").length >= edges;
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

/** Draw every cell once, unplaced and unseen, with each row at its longest value, and read back
 * what React Flow measured: each cell's size and where its handles sit. Edge labels are
 * measured beside it, for ELK to leave room for them. */
function Measure({ graph, mode, onDone }: { graph: Graph; mode: Mode; onDone: (size: Record<string, Measured>, labels: Sizes) => void }) {
  const flow = useReactFlow();
  const box = useRef<HTMLDivElement>(null);
  const nodes: Node<CellData>[] = useMemo(
    () => graph.nodes.map((n) => ({ id: n.id, type: typeOf(n.form, n.archetype), position: { x: 0, y: 0 }, data: { node: n } })),
    [graph],
  );
  const ready = useDrawn(nodes.length, 0, graph);
  useLayoutEffect(() => {
    if (!ready || !box.current) return;
    const size: Record<string, Measured> = {};
    for (const n of graph.nodes) {
      const inner = flow.getInternalNode(n.id);
      const width = inner?.measured.width ?? 0;
      const cell = box.current.querySelector<HTMLElement>(`[data-cell="${CSS.escape(n.id)}"]`);
      const top = cell?.getBoundingClientRect().top ?? 0;
      const ports: Measured["ports"] = [];
      cell?.querySelectorAll<HTMLElement>("[data-row], [data-head]").forEach((el) => {
        const r = el.getBoundingClientRect();
        const y = r.top - top + r.height / 2;
        const id = el.dataset.row ?? "";
        ports.push({ id: id ? `${id}:in` : "in", side: "WEST", x: 0, y });
        ports.push({ id: id ? `${id}:out` : "out", side: "EAST", x: width, y });
      });
      size[n.id] = { width, height: inner?.measured.height ?? 0, ports };
    }
    const labels: Sizes = {};
    box.current.querySelectorAll<HTMLElement>("[data-label]").forEach((l) => {
      const r = l.getBoundingClientRect();
      labels[l.dataset.label!] = { width: Math.ceil(r.width), height: Math.ceil(r.height) };
    });
    onDone(size, labels);
  }, [ready, onDone, flow, graph]);
  const seen = useMemo(() => ({ frame: widest(graph), mode }), [graph, mode]);
  return (
    <div className="measure" ref={box} aria-hidden>
      <FrameContext.Provider value={seen}>
        <ReactFlow nodes={nodes} edges={[]} nodeTypes={NODE_TYPES} defaultViewport={{ x: 0, y: 0, zoom: 1 }} proOptions={{ hideAttribution: true }} />
      </FrameContext.Provider>
      {graph.edges.map((e) => (
        <div key={e.id} className="edge-label" data-label={e.id}>
          {e.label}
        </div>
      ))}
    </div>
  );
}

function Drawn({ graph, placed, mode, step, bare, onReady }: { graph: Graph; placed: Placed; mode: Mode; step: number; bare: boolean; onReady: () => void }) {
  const flow = useReactFlow();
  const nodes: Node<CellData>[] = useMemo(
    () =>
      graph.nodes.map((n) => {
        const p = placed.nodes[n.id];
        return {
          id: n.id,
          type: typeOf(n.form, n.archetype),
          position: { x: p.x, y: p.y },
          width: p.width,
          height: p.height,
          parentId: n.parent ?? undefined,
          extent: n.parent ? ("parent" as const) : undefined,
          data: { node: n },
          draggable: false,
          selectable: false,
        };
      }),
    [graph, placed],
  );
  const seen = useMemo(() => ({ frame: frame(graph, mode, step), mode }), [graph, mode, step]);
  const edges = useMemo(() => graph.edges.map((e) => edgeOf(e, seen, placed.edges[e.id])), [graph, seen, placed]);
  const ready = useDrawn(nodes.length, edges.length, placed);
  useEffect(() => {
    if (!ready) return;
    flow.fitView({ padding: bare ? 0.02 : 0.05, minZoom: MIN_ZOOM, maxZoom: MAX_ZOOM }).then(nextFrame).then(onReady);
  }, [ready, bare, flow, onReady]);
  return (
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
        minZoom={MIN_ZOOM / 2}
        proOptions={{ hideAttribution: bare }}
      />
    </FrameContext.Provider>
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
  const [placed, setPlaced] = useState<Placed | null>(null);
  const shown = useRef<() => void>(() => {});
  const [asked, setAsked] = useState(0); // each call of window.conky.step, so asking again still answers
  const measured = useCallback(
    (size: Record<string, Measured>, labels: Sizes) => {
      place(graph, size, labels)
        .then(setPlaced)
        .catch((e: Error) => console.error(`the layout failed: ${e.message}`));
    },
    [graph],
  );
  useEffect(() => setPlaced(null), [graph]);
  useEffect(() => {
    if (!placed || !bare) return;
    const s = sheet(placed);
    document.documentElement.style.setProperty("--view-width", `${s.width}px`);
    document.documentElement.style.setProperty("--view-height", `${s.height}px`);
  }, [placed, bare]);
  const onReady = useCallback(() => {
    if (!placed) return;
    window.conky = {
      ready: true,
      width: placed.width,
      height: placed.height,
      steps: whole.steps.length,
      step: (n: number) =>
        new Promise<void>((done) => {
          shown.current = () => nextFrame().then(done);
          setStep(n);
          setAsked((k) => k + 1);
        }),
    };
  }, [placed, whole]);
  useEffect(() => {
    shown.current();
  }, [step, asked]);
  return (
    <div className={`view view-${mode} ${bare ? "is-bare" : ""}`}>
      {!bare && (
        <header className="view-head">
          <span className="view-title">{whole.title}</span>
          <span className="view-draw">draw {whole.draw}</span>
        </header>
      )}
      <div className="view-graph">
        <ReactFlowProvider key={`${mode}:${placed ? "drawn" : "measure"}`}>
          {placed ? (
            <Drawn graph={graph} placed={placed} mode={mode} step={step} bare={bare} onReady={onReady} />
          ) : (
            <Measure graph={graph} mode={mode} onDone={measured} />
          )}
        </ReactFlowProvider>
      </div>
      <Caption graph={whole} mode={mode} step={step} />
      <Legend graph={graph} mode={mode} />
      {!bare && <Scrubber steps={whole.steps.length} step={step} mode={mode} onStep={setStep} onMode={setMode} />}
    </div>
  );
}
