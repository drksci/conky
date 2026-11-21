// Serve the repository to the built view, so a card can be opened in a browser:
//   npm run view            then open the address it prints
// The view reads docs/results/cards/<card>/graph.json; browsers refuse to fetch it from disk.
import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";

export const REPO = fileURLToPath(new URL("../..", import.meta.url));
const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".webp": "image/webp",
  ".svg": "image/svg+xml",
};

/** Start a static server on the repository, on the given port (0 for any free one). */
export function serve(port = 0) {
  const server = createServer((ask, answer) => {
    const path = normalize(decodeURIComponent(new URL(ask.url, "http://x").pathname)).replace(/^([/\\])+/, "");
    const file = join(REPO, path);
    if (!file.startsWith(REPO) || !existsSync(file) || !statSync(file).isFile()) {
      answer.writeHead(404).end("not found");
      return;
    }
    answer.writeHead(200, { "content-type": TYPES[extname(file)] ?? "application/octet-stream" });
    createReadStream(file).pipe(answer);
  });
  return new Promise((done) => server.listen(port, "127.0.0.1", () => done(server)));
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const server = await serve(Number(process.env.PORT ?? 5174));
  const { port } = server.address();
  console.log(`serving the repository at http://127.0.0.1:${port}/`);
  console.log(
    `open http://127.0.0.1:${port}/viewer/dist/index.html?graph=/docs/results/cards/a-keeper-hears-the-no/graph.json`,
  );
  console.log("(run `npm run build` first if viewer/dist is missing; ctrl-c stops)");
}
