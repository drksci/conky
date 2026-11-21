// npm test: the built view, headless, on every published card's graph.json, in both densities
// (dynamics is compact, topology detailed) and both looks. Each is a property, measured:
// - one cell a node, and every cell in the detailed density has a header;
// - nothing overflows: every cell, row and code block holds its content (scrollWidth and
//   scrollHeight within clientWidth and clientHeight; sockets sit in a cell's padding on purpose
//   and are left out of this);
// - nothing overlaps except by containment, and a member sits inside its space or region with
//   at least the token padding;
// - no two sockets overlap, every edge ends on two sockets of its own kind of signal, every
//   watch entry has an input and an output socket, and an empty slot is drawn hollow;
// - text has a WCAG contrast of at least 4.5, cell edges and connectors at least 3, against the
//   ground a picture is shown on (#ffffff light, #0d1117 dark);
// - colours only from the token file, symbols only from its table, and no colour, weight or
//   size literal in the components.
import assert from "node:assert/strict";
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "../scripts/browser.mjs";
import { REPO, serve } from "../scripts/serve.mjs";
import { tokens } from "../tokens.mjs";

const here = fileURLToPath(new URL(".", import.meta.url));
const t = tokens();
const cardsDir = join(REPO, "docs", "results", "cards");
const cards = readdirSync(cardsDir).filter((c) => existsSync(join(cardsDir, c, "graph.json")));
assert.ok(cards.length > 0, "no published card to test: publish one with python -m bench.dynamics");
const GROUND = { light: "#ffffff", dark: "#0d1117" };

// Components carry no colour, weight or size of their own: those live in view.css and the tokens.
const components = join(here, "..", "src", "components");
for (const file of readdirSync(components)) {
  const text = readFileSync(join(components, file), "utf-8");
  assert.doesNotMatch(text, /#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(/, `${file} names a colour`);
  assert.doesNotMatch(text, /(fontSize|strokeWidth|fontWeight|color|stroke|fill)\s*[:=]/, `${file} sets a look inline`);
}
const source = readdirSync(join(here, "..", "src"), { recursive: true }).filter((f) => /\.tsx?$/.test(f));
for (const f of source) {
  const text = readFileSync(join(here, "..", "src", f), "utf-8");
  assert.doesNotMatch(text, /import \{(?![^}]*\bicons\b)[^}]*\} from "lucide-react"/, `${f} imports an icon by name, not from the table`);
}

const rgb = (hex) => {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
};
const allowed = new Set(
  [...Object.values(t.color), ...Object.values(t.pen)].flatMap((pair) => Object.values(pair)).map((hex) => `rgb(${rgb(hex).join(", ")})`),
);
allowed.add("rgba(0, 0, 0, 0)");
const parse = (css) => (css.match(/[\d.]+/g) ?? []).slice(0, 3).map(Number);
const luminance = ([r, g, b]) =>
  [r, g, b].map((c) => ((c /= 255) <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)).reduce((s, c, k) => s + c * [0.2126, 0.7152, 0.0722][k], 0);
const contrast = (a, b) => {
  const [x, y] = [luminance(a), luminance(b)].sort((p, q) => q - p);
  return (x + 0.05) / (y + 0.05);
};

const server = await serve(0);
const browser = await chromium();
const base = `http://127.0.0.1:${server.address().port}`;
let checked = 0;
try {
  for (const card of cards) {
    const graph = JSON.parse(readFileSync(join(cardsDir, card, "graph.json"), "utf-8"));
    const named = new Set([...graph.nodes.map((n) => n.header.symbol), ...graph.steps.map((s) => s.symbol)]);
    for (const name of named) assert.ok(t.symbol[name], `${card}: symbol ${name} is not in tokens.json`);
    const sockets = new Map(graph.nodes.flatMap((n) => n.sockets.map((s) => [s.id, s])));
    for (const e of graph.edges) {
      const [a, b] = [sockets.get(e.sourceSocket), sockets.get(e.targetSocket)];
      assert.ok(a && b, `${card}: edge ${e.id} does not end on two sockets`);
      assert.equal(a.kind, e.signal, `${card}: ${e.id} leaves a ${a.kind} socket`);
      assert.equal(b.kind, e.signal, `${card}: ${e.id} plugs into a ${b.kind} socket`);
      assert.ok(t.socket[a.kind], `${card}: socket kind ${a.kind} is not in tokens.json`);
    }
    for (const n of graph.nodes)
      for (const p of n.panels)
        if (p.kind === "when") for (const r of p.rows) assert.ok(sockets.get(r.in)?.side === "WEST" && sockets.get(r.out)?.side === "EAST", `${card}: ${r.id} lacks its sockets`);
    // the last step of each arrangement in the animation, and the final state
    const views = [...new Set(graph.steps.map((s) => s.arrangement))].map((a) => ["dynamics", Math.max(...graph.steps.filter((s) => s.arrangement === a).map((s) => s.i))]);
    views.push(["topology", graph.steps.length - 1]);
    for (const [mode, step] of views)
      for (const look of ["light", "dark"]) {
        const page = await browser.newPage({ viewport: { width: 1600, height: 1200 } });
        const where = `${card} ${mode} step ${step} ${look}`;
        await page.goto(`${base}/viewer/dist/index.html?graph=/docs/results/cards/${card}/graph.json&mode=${mode}&theme=${look}&bare=1&step=${step}`);
        await page.waitForFunction(() => window.conky?.ready, null, { timeout: 60000 });
        await page.evaluate((n) => window.conky.step(n), step);
        const seen = await page.evaluate(() => {
          const box = (el) => {
            const r = el.getBoundingClientRect();
            return { x: r.x, y: r.y, w: r.width, h: r.height };
          };
          const hidden = (el) => Boolean(el.closest(".is-hidden"));
          const sockets = [...document.querySelectorAll(".view-graph [data-socket]")].filter((el) => !hidden(el));
          const socketBoxes = sockets.map((el) => ({ id: el.dataset.socket, hollow: el.classList.contains("is-hollow"), ...box(el) }));
          sockets.forEach((el) => (el.style.display = "none"));
          const overflow = [...document.querySelectorAll(".view-graph [data-cell], .view-graph .cell-head-row, .view-graph .holds-row > *, .view-graph .rule, .view-graph .when-cell, .view-graph .then-cell, .view-graph .record-row, .view-graph .slot, .view-graph .expr, .view-graph .region")]
            .filter((el) => el.scrollWidth > el.clientWidth + 0.5 || el.scrollHeight > el.clientHeight + 0.5)
            .map((el) => `${el.dataset.cell ?? el.className} ${el.scrollWidth}/${el.clientWidth} ${el.scrollHeight}/${el.clientHeight}`);
          sockets.forEach((el) => (el.style.display = ""));
          const cells = [...document.querySelectorAll(".react-flow__node [data-cell]")].map((el) => ({
            id: el.dataset.cell,
            ...box(el),
            head: Boolean(el.querySelector("[data-head]")),
            border: getComputedStyle(el).borderTopColor,
            colours: [getComputedStyle(el).color, getComputedStyle(el).borderTopColor, getComputedStyle(el).backgroundColor],
            hidden: hidden(el),
          }));
          const regions = [...document.querySelectorAll("[data-region]")].map((el) => ({ id: el.dataset.region, ...box(el), hidden: hidden(el) }));
          const texts = [];
          const walker = document.createTreeWalker(document.querySelector(".view"), NodeFilter.SHOW_TEXT);
          for (let n = walker.nextNode(); n; n = walker.nextNode()) {
            const el = n.parentElement;
            if (!n.textContent.trim() || hidden(el) || el.closest(".measure")) continue;
            texts.push({ text: n.textContent.trim().slice(0, 30), colour: getComputedStyle(el).color });
          }
          const strokes = [...document.querySelectorAll(".view-graph .react-flow__edge:not(.is-hidden) .react-flow__edge-path")].map((el) => getComputedStyle(el).stroke);
          const zoom = new DOMMatrix(getComputedStyle(document.querySelector(".view-graph .react-flow__viewport")).transform).a;
          return { overflow, cells, regions, socketBoxes, texts, strokes, zoom };
        });
        const ground = rgb(GROUND[look]);
        assert.deepEqual(seen.overflow, [], `${where}: content overflows`);
        const want = graph.nodes.filter((n) => n.modes.includes(mode)).map((n) => n.id).sort();
        assert.deepEqual(seen.cells.map((c) => c.id).sort(), want, `${where}: one cell a node`);
        if (mode === "topology") for (const c of seen.cells) assert.ok(c.head, `${where}: ${c.id} has no header`);
        const parent = Object.fromEntries(graph.nodes.map((n) => [n.id, n.parent]));
        const regionOf = Object.fromEntries((graph.arrangements[graph.steps[step].arrangement] ?? []).flatMap((r) => r.members.map((m) => [m, r.id])));
        const up = (id) => regionOf[id] ?? parent[id] ?? (String(id).includes("::") && !id.startsWith("::") ? id.split("::")[0] : null);
        const holds = (a, b) => {
          for (let p = up(b); p; p = up(p)) if (p === a) return true;
          return false;
        };
        const things = [...seen.cells, ...seen.regions].filter((c) => !c.hidden);
        const byId = Object.fromEntries(things.map((c) => [c.id, c]));
        for (const a of things)
          for (const b of things) {
            if (a.id >= b.id || holds(a.id, b.id) || holds(b.id, a.id)) continue;
            const apart = a.x + a.w <= b.x + 0.5 || b.x + b.w <= a.x + 0.5 || a.y + a.h <= b.y + 0.5 || b.y + b.h <= a.y + 0.5;
            assert.ok(apart, `${where}: ${a.id} and ${b.id} overlap`);
          }
        for (const c of things) {
          const outer = byId[up(c.id)];
          if (!outer) continue;
          const pad = t.space.fine * seen.zoom - 0.5; // the token padding, at the zoom the picture is drawn at
          const inside = c.x >= outer.x + pad && c.y >= outer.y + pad && c.x + c.w <= outer.x + outer.w - pad && c.y + c.h <= outer.y + outer.h - pad;
          assert.ok(inside, `${where}: ${c.id} is not inside ${outer.id} with room around it`);
        }
        for (const [k, a] of seen.socketBoxes.entries())
          for (const b of seen.socketBoxes.slice(k + 1)) {
            const apart = a.x + a.w <= b.x + 0.5 || b.x + b.w <= a.x + 0.5 || a.y + a.h <= b.y + 0.5 || b.y + b.h <= a.y + 0.5;
            assert.ok(apart, `${where}: sockets ${a.id} and ${b.id} overlap`);
          }
        const hollow = new Map(seen.socketBoxes.map((s) => [s.id, s.hollow]));
        for (const n of graph.nodes)
          for (const s of n.footer.slots) if (!s.filled && hollow.has(s.socket)) assert.ok(hollow.get(s.socket), `${where}: empty slot ${s.id} is not hollow`);
        for (const e of graph.edges.filter((e) => e.modes.includes(mode))) {
          const drawn = await page.locator(`[data-socket="${e.sourceSocket}"]`).count();
          assert.ok(drawn > 0 || !seen.strokes.length, `${where}: ${e.id} has no socket to leave from`);
        }
        for (const x of seen.texts) assert.ok(contrast(parse(x.colour), ground) >= 4.5, `${where}: "${x.text}" in ${x.colour} is too faint`);
        for (const c of seen.cells.filter((c) => !c.hidden)) assert.ok(contrast(parse(c.border), ground) >= 3, `${where}: ${c.id}'s edge in ${c.border} is too faint`);
        for (const s of seen.strokes) assert.ok(contrast(parse(s), ground) >= 3, `${where}: a connector in ${s} is too faint`);
        for (const c of [...seen.cells.flatMap((c) => c.colours), ...seen.strokes]) assert.ok(allowed.has(c), `${where}: ${c} is not a token colour`);
        checked += 1;
        await page.close();
      }
  }
  console.log(`view test passed: ${cards.length} cards, ${checked} pictures checked`);
} finally {
  await browser.close();
  server.close();
}
