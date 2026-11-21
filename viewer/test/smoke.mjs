// npm test: the built view, headless, on every published card's graph.json, in both densities
// (dynamics is compact, topology detailed) and both looks. Each is a property, measured:
// - one cell a node, and every cell in the detailed density has a header;
// - nothing overflows: every cell, row and code block holds its content (scrollWidth and
//   scrollHeight within clientWidth and clientHeight), and every port's name sits inside its
//   block;
// - nothing overlaps except by containment, and a member sits inside its space or region with
//   at least the token padding;
// - no two ports overlap, and every edge ends on two ports of its own kind of signal;
// - a cell with ports has a pair of boards, left and right or top and bottom, and nothing else,
//   each the whole length of its edge; every port is a square as wide as its board is thick;
//   every port of the graph is drawn, solid when something is plugged in and a bar when not,
//   and its name is unique in its cell and the one graph.json gives;
// - text has a WCAG contrast of at least 4.5, cell edges and connectors at least 3, against the
//   ground a picture is shown on (#ffffff light, #0d1117 dark), and a port's white name at least
//   4.5 against its block;
// - the port colours: white on each at least 4.5 in both looks, and every two kinds told apart
//   by a distance in OKLab of at least 0.09, and at least 0.03 (about one and a half times the
//   smallest step most people see) with protanopia, deuteranopia and tritanopia simulated by the
//   full-severity matrices of Machado, Oliveira and Fernandes (2009) in linear RGB;
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
  [...Object.values(t.color), ...Object.values(t.pen), ...Object.values(t.port).filter((v) => typeof v === "object")].flatMap((pair) => Object.values(pair)).map((hex) => `rgb(${rgb(hex).join(", ")})`),
);
allowed.add("rgba(0, 0, 0, 0)");
const parse = (css) => (css.match(/[\d.]+/g) ?? []).slice(0, 3).map(Number);
const luminance = ([r, g, b]) =>
  [r, g, b].map((c) => ((c /= 255) <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)).reduce((s, c, k) => s + c * [0.2126, 0.7152, 0.0722][k], 0);
const contrast = (a, b) => {
  const [x, y] = [luminance(a), luminance(b)].sort((p, q) => q - p);
  return (x + 0.05) / (y + 0.05);
};

// The port colours, told apart at a glance by everyone.
const linear = (c) => ((c /= 255) <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);
const MACHADO = {
  protanopia: [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
  deuteranopia: [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.01182, 0.04294, 0.968881]],
  tritanopia: [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.3039]],
};
const oklab = ([r, g, b]) => {
  const [l, m, q] = [
    0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b,
    0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b,
    0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b,
  ].map(Math.cbrt);
  return [0.2104542553 * l + 0.793617785 * m - 0.0040720468 * q, 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * q, 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * q];
};
const seenAs = (hex, m) => {
  const c = rgb(hex).map(linear);
  return m ? m.map((row) => Math.min(1, Math.max(0, row.reduce((t, k, j) => t + k * c[j], 0)))) : c;
};
const kindsOfPort = Object.keys(t.socket);
assert.deepEqual(Object.keys(t.port).filter((k) => typeof t.port[k] === "object" && k !== "label"), kindsOfPort, "tokens.json: one port colour a kind of port, in the socket table's order");
for (const look of ["light", "dark"]) {
  for (const k of kindsOfPort)
    assert.ok(contrast(rgb(t.port.label[look]), rgb(t.port[k][look])) >= 4.5, `port ${k} (${look}): its white name is too faint on it`);
  for (const [name, m] of [["normal vision", null], ...Object.entries(MACHADO)])
    for (const [i, a] of kindsOfPort.entries())
      for (const b of kindsOfPort.slice(i + 1)) {
        const [p, q] = [oklab(seenAs(t.port[a][look], m)), oklab(seenAs(t.port[b][look], m))];
        const d = Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2]);
        assert.ok(d >= (m ? 0.03 : 0.09), `ports ${a} and ${b} (${look}) are too alike with ${name}: ${d.toFixed(3)}`);
      }
}
const prefixes = Object.values(t.socket).map((s) => s.prefix);
assert.equal(new Set(prefixes).size, prefixes.length, "tokens.json: two kinds of port share a prefix");

const server = await serve(0);
const browser = await chromium();
const base = `http://127.0.0.1:${server.address().port}`;
let checked = 0;
try {
  for (const card of cards) {
    const graph = JSON.parse(readFileSync(join(cardsDir, card, "graph.json"), "utf-8"));
    const named = new Set([...graph.nodes.map((n) => n.header.symbol), ...graph.steps.map((s) => s.symbol)]);
    for (const name of named) assert.ok(t.symbol[name], `${card}: symbol ${name} is not in tokens.json`);
    const sockets = new Map(graph.nodes.flatMap((n) => n.board.map((s) => [s.id, s])));
    const kinds = Object.keys(t.socket); // the standard order
    for (const e of graph.edges)
      for (const h of e.hops) {
        const [a, b] = [sockets.get(h.sourceSocket), sockets.get(h.targetSocket)];
        assert.ok(a && b, `${card}: hop ${h.id} does not end on two sockets`);
        assert.equal(a.kind, e.signal, `${card}: ${h.id} leaves a ${a.kind} socket`);
        assert.equal(b.kind, e.signal, `${card}: ${h.id} plugs into a ${b.kind} socket`);
        assert.ok(t.socket[a.kind], `${card}: socket kind ${a.kind} is not in tokens.json`);
      }
    for (const n of graph.nodes) {
      const order = n.board.map((s) => kinds.indexOf(s.kind));
      assert.deepEqual(order, [...order].sort((x, y) => x - y), `${card}: ${n.id}'s board is not in the standard order`);
    }
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
          const socketBoxes = sockets.map((el) => {
            const name = el.querySelector(".port-name");
            return {
              id: el.dataset.socket,
              idle: el.classList.contains("is-idle"),
              name: name.textContent,
              label: box(name),
              fill: getComputedStyle(el).backgroundColor,
              side: el.dataset.side,
              deep: el.offsetWidth,
              bars: Object.fromEntries(["Top", "Right", "Bottom", "Left"].map((d) => [d, [parseFloat(getComputedStyle(el)[`border${d}Width`]), getComputedStyle(el)[`border${d}Color`]]])),
              ink: getComputedStyle(name).color,
              ...box(el),
            };
          });
          const overflow = [...document.querySelectorAll(".view-graph [data-cell], .view-graph .cell-head-row, .view-graph .holds-row > *, .view-graph .rule, .view-graph .when-cell, .view-graph .then-cell, .view-graph .record-row, .view-graph .foot-slot, .view-graph .expr, .view-graph .region")]
            .filter((el) => el.scrollWidth > el.clientWidth + 0.5 || el.scrollHeight > el.clientHeight + 0.5)
            .map((el) => `${el.dataset.cell ?? el.className} ${el.scrollWidth}/${el.clientWidth} ${el.scrollHeight}/${el.clientHeight}`);
          const cells = [...document.querySelectorAll(".react-flow__node [data-cell]")].map((el) => ({
            id: el.dataset.cell,
            ...box(el),
            head: Boolean(el.querySelector("[data-head]")),
            border: getComputedStyle(el).borderTopColor,
            colours: [getComputedStyle(el).color, getComputedStyle(el).borderTopColor, getComputedStyle(el).backgroundColor],
            hidden: hidden(el),
          }));
          const regions = [...document.querySelectorAll("[data-region]")].map((el) => ({ id: el.dataset.region, ...box(el), hidden: hidden(el) }));
          const boards = [...document.querySelectorAll(".view-graph [data-board]")]
            .filter((el) => !hidden(el))
            .map((el) => ({ id: el.dataset.board, ...box(el), sockets: [...el.querySelectorAll("[data-socket]")].map((s) => ({ id: s.dataset.socket, ...box(s) })) }));
          const hops = [...document.querySelectorAll(".view-graph .react-flow__edge")]
            .filter((el) => !el.classList.contains("is-hidden"))
            .map((el) => {
              const path = el.querySelector(".react-flow__edge-path");
              const m = path.getScreenCTM();
              const len = path.getTotalLength();
              const at = (k) => {
                const p = path.getPointAtLength(k).matrixTransform(m);
                return { x: p.x, y: p.y };
              };
              const points = [];
              for (let k = 0; k < len; k += 2) points.push(at(k));
              return { id: el.dataset.id, points, start: at(0), end: at(len) };
            });
          const texts = [];
          const walker = document.createTreeWalker(document.querySelector(".view"), NodeFilter.SHOW_TEXT);
          for (let n = walker.nextNode(); n; n = walker.nextNode()) {
            const el = n.parentElement;
            if (!n.textContent.trim() || hidden(el) || el.closest(".measure")) continue;
            if (el.closest(".port:not(.is-idle), .port-tag:not(.is-idle)")) continue; // white on its block, checked against it
            texts.push({ text: n.textContent.trim().slice(0, 30), colour: getComputedStyle(el).color });
          }
          const strokes = [...document.querySelectorAll(".view-graph .react-flow__edge:not(.is-hidden) .react-flow__edge-path")].map((el) => getComputedStyle(el).stroke);
          const zoom = new DOMMatrix(getComputedStyle(document.querySelector(".view-graph .react-flow__viewport")).transform).a;
          return { overflow, cells, regions, socketBoxes, boards, hops, texts, strokes, zoom };
        });
        const ground = rgb(GROUND[look]);
        assert.deepEqual(seen.overflow, [], `${where}: content overflows`);
        const nodesIn = graph.nodes.filter((n) => n.modes.includes(mode));
        const want = nodesIn.map((n) => n.id).sort();
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
        // boards: every wire ends in a plug on a board, boards keep clear of every body but the
        // spaces that hold them and of each other, sockets on a board in the standard order, and
        // no wire enters a space except through a socket on that space's board
        const meet = (a, b) => !(a.x + a.w <= b.x + 0.5 || b.x + b.w <= a.x + 0.5 || a.y + a.h <= b.y + 0.5 || b.y + b.h <= a.y + 0.5);
        const onBoard = new Map(seen.boards.flatMap((b) => b.sockets.map((s) => [s.id, s])));
        const near = (p, s) => p.x >= s.x - 1.5 && p.x <= s.x + s.w + 1.5 && p.y >= s.y - 1.5 && p.y <= s.y + s.h + 1.5;
        const hopOf = new Map(graph.edges.flatMap((e) => e.hops.map((h) => [h.id, h])));
        for (const d of seen.hops) {
          const h = hopOf.get(d.id);
          const [a, b] = [onBoard.get(h.sourceSocket), onBoard.get(h.targetSocket)];
          assert.ok(a && b, `${where}: ${d.id} does not run between two sockets on boards`);
          assert.ok(near(d.start, a) && near(d.end, b), `${where}: ${d.id} is not plugged into its sockets`);
        }
        for (const [k, a] of seen.boards.entries()) {
          for (const b of seen.boards.slice(k + 1)) assert.ok(!meet(a, b), `${where}: boards ${a.id} and ${b.id} overlap`);
          const owner = a.id.split(":")[0];
          for (const c of seen.cells.filter((c) => !c.hidden)) if (!holds(c.id, owner)) assert.ok(!meet(a, c), `${where}: board ${a.id} lies on ${c.id}`);
          // a board runs the whole edge it is on, and every port on it is a square as wide as the
          // board is thick
          const body = seen.cells.find((c) => c.id === owner);
          const upright = a.id.endsWith(":west") || a.id.endsWith(":east");
          const long = upright ? [a.h, body.h] : [a.w, body.w];
          assert.ok(Math.abs(long[0] - long[1]) <= 1, `${where}: board ${a.id} is ${long[0]} long on an edge ${long[1]} long`);
          const thick = upright ? a.w : a.h;
          for (const p of a.sockets)
            assert.ok(Math.abs(p.w - thick) <= 1 && Math.abs(p.h - thick) <= 1, `${where}: port ${p.id} is ${p.w} by ${p.h} on a board ${thick} thick`);
          const along = upright ? "y" : "x";
          const order = [...a.sockets].sort((p, q) => p[along] - q[along]).map((s) => kinds.indexOf(sockets.get(s.id).kind));
          assert.deepEqual(order, [...order].sort((x, y) => x - y), `${where}: board ${a.id} is not in the standard order`);
        }
        const spaceCells = seen.cells.filter((c) => !c.hidden && graph.nodes.find((n) => n.id === c.id)?.form === "space");
        for (const d of seen.hops) {
          const h = hopOf.get(d.id);
          for (const s of spaceCells) {
            if (s.id === h.within || (h.within && holds(s.id, h.within))) continue;
            const inside = d.points.find((p) => p.x > s.x + 1 && p.x < s.x + s.w - 1 && p.y > s.y + 1 && p.y < s.y + s.h - 1);
            assert.ok(!inside, `${where}: ${d.id} enters ${s.id} away from its board`);
          }
        }
        // the pair of boards, and every port: drawn, named as graph.json names it, solid when
        // something is plugged in and a bar on the cell's side when nothing is, its white name legible on it
        const edgesIn = graph.edges.filter((e) => e.modes.includes(mode));
        const crossed = new Set(edgesIn.flatMap((e) => e.hops.flatMap((h) => [h.sourceSocket, h.targetSocket])));
        const appeared = new Set(graph.steps.slice(0, step + 1).flatMap((s) => s.appear));
        const shownHops = edgesIn.flatMap((e) => e.hops).filter((h) => mode === "topology" || appeared.has(h.id));
        const plugged = new Set(shownHops.flatMap((h) => [h.sourceSocket, h.targetSocket]));
        const drawn = new Map(seen.socketBoxes.map((s) => [s.id, s]));
        for (const n of nodesIn) {
          if (mode === "dynamics" && !appeared.has(n.id)) continue;
          const ports = n.board.filter((s) => s.face !== "wall" || crossed.has(s.id)).filter((s) => mode === "topology" || appeared.has(s.id));
          const pair = seen.boards.filter((b) => b.id.split(":")[0] === n.id).map((b) => b.id.split(":")[1]).sort();
          if (ports.length) assert.ok(["east,west", "north,south"].includes(pair.join(",")), `${where}: ${n.id} has boards ${pair.join(", ")}, not a pair`);
          const slots = new Map(n.footer.slots.map((s) => [s.socket, s]));
          const names = ports.map((s) => s.name);
          assert.equal(new Set(names).size, names.length, `${where}: ${n.id} names two ports alike`);
          for (const s of ports) {
            const d = drawn.get(s.id);
            assert.ok(d, `${where}: port ${s.id} is not drawn`);
            assert.equal(d.name, s.name, `${where}: port ${s.id} is named ${d.name}, not ${s.name}`);
            const solid = slots.has(s.id) ? slots.get(s.id).filled : plugged.has(s.id);
            assert.equal(!d.idle, solid, `${where}: port ${s.id} is ${d.idle ? "a bar" : "solid"} with ${solid ? "something" : "nothing"} plugged in`);
            const l = d.label;
            assert.ok(l.x >= d.x - 0.5 && l.y >= d.y - 0.5 && l.x + l.w <= d.x + d.w + 0.5 && l.y + l.h <= d.y + d.h + 0.5, `${where}: the name of ${s.id} overflows its block`);
            if (!d.idle) assert.ok(contrast(parse(d.ink), parse(d.fill)) >= 4.5, `${where}: the name on ${s.id} is too faint on its block`);
            else {
              // nothing plugged in: no fill, and one bar in the kind's colour on the edge that
              // touches the cell, the token's share of the port's depth
              const facing = { WEST: "Right", EAST: "Left", NORTH: "Bottom", SOUTH: "Top" }[d.side];
              assert.equal(d.fill, "rgba(0, 0, 0, 0)", `${where}: idle port ${s.id} is filled`);
              for (const [edge, [wide, colour]] of Object.entries(d.bars)) {
                if (edge !== facing) assert.equal(wide, 0, `${where}: idle port ${s.id} has an edge on its ${edge.toLowerCase()}`);
                else {
                  assert.ok(Math.abs(wide - t.port.idle_bar * d.deep) <= 0.5, `${where}: the bar of ${s.id} is ${wide} px of ${d.deep}`);
                  assert.equal(colour, `rgb(${rgb(t.port[s.kind][look]).join(", ")})`, `${where}: the bar of ${s.id} is not its kind's colour`);
                }
              }
            }
          }
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
