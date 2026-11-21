// The design tokens as CSS custom properties, generated from src/conky/tokens.json at build time.
//
// Every colour pair becomes --ds-color-<name> and every pen --ds-pen-<name>, with the light value
// by default, the dark value under prefers-color-scheme: dark, and either one forced by
// data-theme="light" or data-theme="dark" on the root. Weights, dashes, sizes and spaces become
// --ds-weight-*, --ds-dash-*, --ds-size-* and --ds-space-* in px. Each meaning gets a class,
// .is-<meaning>, that sets --pen to the pen carrying it: a stylesheet colours a subject with
// var(--pen) and never names a pen itself.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const TOKENS_PATH = fileURLToPath(new URL("../src/conky/tokens.json", import.meta.url));

export function tokens() {
  return JSON.parse(readFileSync(TOKENS_PATH, "utf-8"));
}

export function tokensCss(t = tokens()) {
  const look = (which) =>
    [
      ...Object.entries(t.color).map(([k, v]) => `  --ds-color-${k}: ${v[which]};`),
      ...Object.entries(t.pen).map(([k, v]) => `  --ds-pen-${k}: ${v[which]};`),
      `  color-scheme: ${which};`,
    ].join("\n");
  const scale = [
    ...Object.entries(t.weight).map(([k, v]) => `  --ds-weight-${k}: ${v}px;`),
    ...Object.entries(t.dash).map(([k, v]) => `  --ds-dash-${k}: ${v};`),
    ...Object.entries(t.size).map(([k, v]) => `  --ds-size-${k}: ${v}px;`),
    ...Object.entries(t.space).map(([k, v]) => `  --ds-space-${k}: ${v}px;`),
    `  --ds-radius: ${t.radius}px;`,
    `  --ds-shadow: ${t.shadow};`,
    `  --ds-font-text: ${t.type.embedded_text.map((f) => (f.includes(" ") ? `"${f}"` : f)).join(", ")};`,
    `  --ds-font-code: ${t.type.embedded_code.map((f) => (f.includes(" ") ? `"${f}"` : f)).join(", ")};`,
  ].join("\n");
  const meanings = Object.entries(t.meaning)
    .map(([meaning, pen]) => `.is-${meaning} { --pen: var(--ds-pen-${pen}); }`)
    .join("\n");
  return [
    "/* generated from src/conky/tokens.json by viewer/tokens.mjs; edit the token file */",
    `:root {\n${scale}\n${look("light")}\n}`,
    `@media (prefers-color-scheme: dark) {\n:root:not([data-theme="light"]) {\n${look("dark")}\n}\n}`,
    `:root[data-theme="dark"] {\n${look("dark")}\n}`,
    `:root[data-theme="light"] {\n${look("light")}\n}`,
    meanings,
    "",
  ].join("\n");
}
