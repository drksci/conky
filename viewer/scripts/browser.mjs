// A headless Chromium through Playwright, found locally or among the global Node packages.
// The view does not install a browser: it uses the one Playwright already has on this machine.
import { execSync } from "node:child_process";
import { createRequire } from "node:module";
import { join } from "node:path";

function playwright() {
  try {
    return createRequire(import.meta.url)("playwright");
  } catch {
    const global = execSync("npm root -g", { encoding: "utf-8" }).trim();
    try {
      return createRequire(join(global, "noop.js"))("playwright");
    } catch {
      throw new Error(
        "Playwright is not installed: install it once with `npm install -g playwright` and " +
          "`npx playwright install chromium`, then run this again",
      );
    }
  }
}

export async function chromium() {
  return playwright().chromium.launch();
}
