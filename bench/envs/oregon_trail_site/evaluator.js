// The evaluator's own connection to the browser that every arm plays the trail in.
//
// It connects over the Chrome DevTools Protocol to a Chromium the runner started, routes the
// site's requests politely, plays the fixed opening to the first travelling screen, and then
// records evidence for the whole run: every input the page receives, with a screenshot of the
// game canvas after each one and a screenshot every few seconds while the game runs on its own.
// Scoring reads only this evidence. No harness sees or controls this connection.
//
//   node evaluator.js --cdp http://127.0.0.1:9222 --evidence DIR [--no-opening]
//
// Writes DIR/opening-NN.png, DIR/ready.json, DIR/inputs.jsonl, DIR/shots/NNNNN.png and
// DIR/evaluator.log. It runs until standard input closes or DIR/stop exists.
"use strict";
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const SITE = "https://oregontrail.ws/games/the-oregon-trail-deluxe/play";
const HOST = "oregontrail.ws";
const AGENT =
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36";
const AFTER_INPUT_MS = 1500;
const TICK_MS = 5000;

// The fixed opening, in canvas pixels at the canvas's on-page size (1030 by 774 in a 1100 by
// 800 viewport). Party: Ma (leader, Banker), Doc, Jed, Tully, Pip. The store: 6 oxen, 4 sets of
// clothing, 10 boxes of bullets, 1 spare wheel, axle and tongue, 600 lb of food. Start: May.
const OPENING = [
  { say: "skip the copyright splash (a click on the picture; on the menu it does nothing)", click: [515, 300], wait: 4000, shot: true },
  { say: "title: Travel the Trail", click: [830, 661], wait: 2500, shot: true },
  { say: "welcome: New Game", click: [697, 661], wait: 2500, shot: true },
  { say: "leader name", click: [560, 175], keys: ["Shift+M", "a"] },
  { say: "first companion", click: [750, 402], keys: ["End", ...Array(6).fill("Backspace"), "Shift+D", "o", "c"] },
  { say: "third companion", click: [750, 466], keys: ["End", ...Array(6).fill("Backspace"), "Shift+T", "u", "l", "l", "y"] },
  { say: "fourth companion", click: [750, 498], keys: ["End", ...Array(6).fill("Backspace"), "Shift+P", "i", "p"], shot: true },
  { say: "occupation Banker (default): OK", click: [754, 602], wait: 2500, shot: true },
  { say: "oxen 6", click: [455, 394], keys: ["6"] },
  { say: "clothing 4", click: [455, 423], keys: ["4"] },
  { say: "bullets 10 boxes", click: [455, 452], keys: ["1", "0"] },
  { say: "spare wheel 1", click: [455, 481], keys: ["1"] },
  { say: "spare axle 1", click: [455, 510], keys: ["1"] },
  { say: "spare tongue 1", click: [455, 539], keys: ["1"] },
  { say: "food 600", click: [455, 568], keys: ["6", "0", "0"] },
  { say: "leave the field", click: [1045, 5], wait: 800, shot: true },
  { say: "Buy", click: [563, 661], wait: 2500, shot: true },
  { say: "start in May", click: [578, 605], wait: 3000, shot: true },
];

function args() {
  const found = { opening: true };
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--cdp") found.cdp = argv[++i];
    else if (argv[i] === "--evidence") found.evidence = argv[++i];
    else if (argv[i] === "--no-opening") found.opening = false;
  }
  if (!found.cdp || !found.evidence) {
    console.error("usage: node evaluator.js --cdp URL --evidence DIR [--no-opening]");
    process.exit(2);
  }
  return found;
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const opt = args();
  const dir = opt.evidence;
  fs.mkdirSync(path.join(dir, "shots"), { recursive: true });
  const log = (m) => fs.appendFileSync(path.join(dir, "evaluator.log"), `${new Date().toISOString()} ${m}\n`);
  const browser = await chromium.connectOverCDP(opt.cdp);
  const context = browser.contexts()[0] || (await browser.newContext({ userAgent: AGENT }));
  const page = context.pages()[0] || (await context.newPage());
  await page.setViewportSize({ width: 1100, height: 800 });
  let busy = 0;
  await context.route("**/*", async (route) => {
    const url = route.request().url();
    if (!new URL(url).hostname.endsWith(HOST)) return route.abort();
    while (busy >= 2) await sleep(100);
    busy++;
    try {
      for (let i = 0; i < 6; i++) {
        try {
          const reply = await route.fetch({ timeout: 60000 });
          if (reply.status() < 500) return await route.fulfill({ response: reply });
        } catch (e) {
          log(`retry ${i + 1} ${url.slice(0, 80)}: ${String(e.message).slice(0, 80)}`);
        }
        await sleep(1500 * (i + 1));
      }
      return await route.abort();
    } finally {
      busy--;
    }
  });
  const canvasShot = async (file) => {
    const el = await page.$("canvas");
    if (el) await el.screenshot({ path: file });
  };
  if (opt.opening) {
    log("loading the site");
    await page.goto(SITE, { waitUntil: "domcontentloaded", timeout: 120000 });
    let found = 0;
    for (let i = 0; i < 80 && !found; i++) {
      await sleep(3000);
      found = await page.evaluate(() => document.querySelectorAll("canvas").length);
    }
    if (!found) {
      log("no canvas after four minutes");
      fs.writeFileSync(path.join(dir, "ready.json"), JSON.stringify({ ok: false, why: "no canvas" }));
      process.exit(1);
    }
    await sleep(10000);
    await canvasShot(path.join(dir, "opening-00.png"));
    const box = await (await page.$("canvas")).boundingBox();
    for (const [n, step] of OPENING.entries()) {
      log(`opening ${n + 1}: ${step.say}`);
      if (step.click) {
        const x = box.x + step.click[0];
        const y = box.y + step.click[1];
        await page.mouse.move(x - 30, y - 5);
        await sleep(150);
        await page.mouse.move(x, y, { steps: 6 });
        await sleep(250);
        await page.mouse.down();
        await sleep(200);
        await page.mouse.up();
        await sleep(300);
      }
      for (const key of step.keys || []) {
        await page.keyboard.press(key, { delay: 60 });
        await sleep(100);
      }
      await sleep(step.wait || 400);
      if (step.shot) await canvasShot(path.join(dir, `opening-${String(n + 1).padStart(2, "0")}.png`));
    }
  }
  const box = await (await page.$("canvas")).boundingBox();
  // Evidence hooks: every key and mouse press the page receives, from anyone, is recorded.
  let count = 0;
  const pending = [];
  await page.exposeBinding("__benchInput", async (_source, event) => {
    count += 1;
    const n = count;
    const record = { n, t: new Date().toISOString(), ...event };
    fs.appendFileSync(path.join(dir, "inputs.jsonl"), JSON.stringify(record) + "\n");
    pending.push(
      sleep(AFTER_INPUT_MS).then(() => canvasShot(path.join(dir, "shots", `input-${String(n).padStart(5, "0")}.png`)))
    );
  });
  await page.evaluate(() => {
    const send = (e) => {
      const c = document.querySelector("canvas");
      const r = c ? c.getBoundingClientRect() : { left: 0, top: 0 };
      if (e.type === "keydown") window.__benchInput({ type: "key", key: e.key });
      else window.__benchInput({ type: "click", x: Math.round(e.clientX - r.left), y: Math.round(e.clientY - r.top) });
    };
    window.addEventListener("keydown", send, true);
    window.addEventListener("mousedown", send, true);
  });
  fs.writeFileSync(
    path.join(dir, "ready.json"),
    JSON.stringify({ ok: true, url: page.url(), canvas: box, viewport: { width: 1100, height: 800 } })
  );
  log("ready: the opening is done and the hooks are on");
  let open = true;
  process.stdin.on("end", () => (open = false));
  process.stdin.resume();
  let tick = 0;
  while (open && !fs.existsSync(path.join(dir, "stop"))) {
    await sleep(TICK_MS);
    tick += 1;
    await canvasShot(path.join(dir, "shots", `tick-${String(tick).padStart(5, "0")}.png`)).catch(() => {});
  }
  await Promise.allSettled(pending);
  await canvasShot(path.join(dir, "shots", "final.png")).catch(() => {});
  log(`stopped after ${count} inputs and ${tick} ticks`);
  process.exit(0);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
