import { defineConfig, type Plugin } from "vite";
import { TOKENS_PATH, tokensCss } from "./tokens.mjs";

// The token stylesheet, made from src/conky/tokens.json when the view is built.
function tokenSheet(): Plugin {
  const id = "\0tokens.css";
  return {
    name: "conky-tokens",
    resolveId: (source) => (source === "virtual:tokens.css" ? id : null),
    load(source) {
      if (source !== id) return null;
      this.addWatchFile(TOKENS_PATH);
      return tokensCss();
    },
  };
}

// One classic script, so the built page also opens straight from disk (file://), where browsers
// refuse module scripts.
function classicScript(): Plugin {
  return {
    name: "conky-classic-script",
    enforce: "post",
    transformIndexHtml: (html) =>
      html.replace(/<script type="module" crossorigin/g, "<script defer").replace(/ crossorigin/g, ""),
  };
}

export default defineConfig({
  base: "./",
  esbuild: { jsx: "automatic" },
  plugins: [tokenSheet(), classicScript()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    modulePreload: false,
    cssCodeSplit: false,
    rollupOptions: { output: { format: "iife", inlineDynamicImports: true } },
  },
});
