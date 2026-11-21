// npm test: the built view, headless, on a fixture graph (a copy of a published card's graph.json).
// It checks one cell a node, no two cells overlapping except a space holding its members, colours
// of cells and edges only from the token file, every symbol from the token table, and no colour,
// weight or size literal in the components.
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "../scripts/browser.mjs";
import { REPO, serve } from "../scripts/serve.mjs";
import { tokens } from "../tokens.mjs";

const here = fileURLToPath(new URL(".", import.meta.url));
const t = tokens();
const graph = JSON.parse(readFileSync(join(here, "fixture.json"), "utf-8"));

// Components carry no colour, weight or size of their own: those live in view.css and the tokens.
const components = join(here, "..", "src", "components");
for (const file of readdirSync(components)) {
  const text = readFileSync(join(components, file), "utf-8");
  assert.doesNotMatch(text, /#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(/, `${file} names a colour`);
  assert.doesNotMatch(text, /(fontSize|strokeWidth|fontWeight|color|stroke|fill)\s*[:=]/, `${file} sets a look inline`);
}

// Every symbol the record names is in the one table, and the view draws no other icon.
const named = new Set([
  ...graph.nodes.map((n) => n.symbol),
  ...graph.nodes.flatMap((n) => n.panels.map((p) => p.symbol)),
  ...graph.steps.map((s) => s.symbol),
]);
for (const name of named) assert.ok(t.symbol[name], `symbol ${name} is not in tokens.json`);
const source = readdirSync(join(here, "..", "src"), { recursive: true }).filter((f) => /\.tsx?$/.test(f));
for (const f of source) {
  const text = readFileSync(join(here, "..", "src", f), "utf-8");
  assert.doesNotMatch(text, /import \{(?![^}]*\bicons\b)[^}]*\} from "lucide-react"/, `${f} imports an icon by name, not from the table`);
}

const allowed = new Set(
  [...Object.values(t.color), ...Object.values(t.pen)].flatMap((pair) => Object.values(pair)).map((hex) => {
    const n = parseInt(hex.slice(1), 16);
    return `rgb(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255})`;
  }),
);
allowed.add("rgba(0, 0, 0, 0)");

const server = await serve(0);
const browser = await chromium();
const base = `http://127.0.0.1:${server.address().port}`;
const fixture = "/" + join("viewer", "test", "fixture.json");
try {
  for (const [mode, look] of [["topology", "light"], ["dynamics", "dark"]]) {
    const page = await browser.newPage({ viewport: { width: 1600, height: 1200 } });
    await page.goto(`${base}/viewer/dist/index.html?graph=${fixture}&mode=${mode}&theme=${look}&bare=1&step=${graph.steps.length - 1}`);
    await page.waitForFunction(() => window.conky?.ready, null, { timeout: 60000 });
    const cells = await page.evaluate(() =>
      [...document.querySelectorAll(".react-flow__node [data-cell]")].map((el) => {
        const r = el.getBoundingClientRect();
        const style = getComputedStyle(el);
        return { id: el.dataset.cell, x: r.x, y: r.y, w: r.width, h: r.height, colours: [style.color, style.borderTopColor, style.backgroundColor] };
      }),
    );
    const want = graph.nodes.filter((n) => n.modes.includes(mode)).map((n) => n.id).sort();
    assert.deepEqual(cells.map((c) => c.id).sort(), want, `${mode}: one cell a node`);
    const parent = Object.fromEntries(graph.nodes.map((n) => [n.id, n.parent]));
    const holds = (a, b) => {
      for (let up = parent[b]; up; up = parent[up]) if (up === a) return true;
      return false;
    };
    for (const a of cells)
      for (const b of cells) {
        if (a.id >= b.id || holds(a.id, b.id) || holds(b.id, a.id)) continue;
        const apart = a.x + a.w <= b.x + 0.5 || b.x + b.w <= a.x + 0.5 || a.y + a.h <= b.y + 0.5 || b.y + b.h <= a.y + 0.5;
        assert.ok(apart, `${mode}: ${a.id} and ${b.id} overlap`);
      }
    const edges = await page.evaluate(() =>
      [...document.querySelectorAll(".react-flow__edge-path")].map((el) => getComputedStyle(el).stroke),
    );
    for (const c of [...cells.flatMap((c) => c.colours), ...edges]) assert.ok(allowed.has(c), `${mode}: ${c} is not a token colour`);
    await page.close();
  }
  console.log(`view smoke test passed: ${graph.nodes.length} nodes, ${graph.edges.length} edges, ${graph.steps.length} steps`);
} finally {
  await browser.close();
  server.close();
}
void REPO;
