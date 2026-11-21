// Render the pictures of published cards with the built view, headless.
//   npm run render -- docs/results/cards/<card> ...     (no folder: every published card)
// For each card and each look (light, dark) this opens the view at every step, takes a frame
// with a transparent ground at twice the pixel density, and writes dynamics-<look>.webp, an
// animated WebP (it plays in a GitHub README and keeps the transparency), holding the last step
// longer; and topology-<look>.png, the final state.
import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, relative, resolve } from "node:path";
import { build } from "vite";
import { chromium } from "./browser.mjs";
import { REPO, serve } from "./serve.mjs";

const STEP = 1.8; // seconds a step stays
const LAST = 4.5; // seconds the last step stays
const LOOKS = ["light", "dark"];
const FFMPEG = process.env.FFMPEG ?? "ffmpeg";

const asked = process.argv.slice(2).filter((a) => a !== "--");
const cardsDir = join(REPO, "docs", "results", "cards");
const folders = (asked.length ? asked.map((a) => resolve(a)) : readdirSync(cardsDir).map((c) => join(cardsDir, c))).filter((f) =>
  existsSync(join(f, "graph.json")),
);

await build({ root: resolve(REPO, "viewer"), logLevel: "warn" });
const server = await serve(0);
const base = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium();

async function open(folder, mode, look) {
  const page = await browser.newPage({ viewport: { width: 2400, height: 1600 }, deviceScaleFactor: 2 });
  const graph = "/" + relative(REPO, join(folder, "graph.json")).split("\\").join("/");
  await page.goto(`${base}/viewer/dist/index.html?graph=${encodeURIComponent(graph)}&mode=${mode}&theme=${look}&bare=1&step=0`);
  await page.waitForFunction(() => window.conky?.ready, null, { timeout: 60000 });
  return page;
}

function ffmpeg(args) {
  const done = spawnSync(FFMPEG, ["-hide_banner", "-loglevel", "error", "-y", ...args], { encoding: "utf-8" });
  if (done.status !== 0) throw new Error(`ffmpeg failed: ${done.stderr || done.error}`);
}

for (const folder of folders) {
  for (const look of LOOKS) {
    const work = mkdtempSync(join(tmpdir(), "conky-view-"));
    const page = await open(folder, "dynamics", look);
    const steps = await page.evaluate(() => window.conky.steps);
    const list = [];
    let tall = 0; // a caption can wrap: every frame is as tall as the tallest, so none jumps
    for (let i = 0; i < steps; i++) {
      await page.evaluate((n) => window.conky.step(n), i);
      tall = Math.max(tall, (await page.locator(".view").boundingBox()).height);
    }
    await page.evaluate((h) => document.documentElement.style.setProperty("--view-tall", `${h}px`), tall);
    for (let i = 0; i < steps; i++) {
      await page.evaluate((n) => window.conky.step(n), i);
      const frame = join(work, `step-${String(i).padStart(3, "0")}.png`);
      await page.locator(".view").screenshot({ path: frame, omitBackground: true });
      list.push(`file '${frame}'`, `duration ${i === steps - 1 ? LAST : STEP}`);
    }
    list.push(list[list.length - 2]); // the concat list repeats the last file so its time holds
    writeFileSync(join(work, "list.txt"), list.join("\n") + "\n");
    await page.close();
    const out = join(folder, `dynamics-${look}.webp`);
    ffmpeg(["-f", "concat", "-safe", "0", "-i", join(work, "list.txt"), "-fps_mode", "vfr", "-c:v", "libwebp_anim",
      "-lossless", "0", "-quality", "90", "-compression_level", "6", "-pix_fmt", "yuva420p", "-loop", "0", out]);
    const still = await open(folder, "topology", look);
    const topo = join(folder, `topology-${look}.png`);
    await still.locator(".view").screenshot({ path: topo, omitBackground: true });
    await still.close();
    rmSync(work, { recursive: true, force: true });
    const kb = (p) => `${Math.round(statSync(p).size / 1024)} kB`;
    console.log(`${relative(REPO, out)} (${steps} steps, ${kb(out)}), ${relative(REPO, topo)} (${kb(topo)})`);
  }
}
await browser.close();
server.close();
