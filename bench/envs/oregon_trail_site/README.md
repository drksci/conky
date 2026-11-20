# The web environment: the 1992 game in a browser

The Oregon Trail Deluxe (MECC, 1992) at https://oregontrail.ws/games/the-oregon-trail-deluxe/play,
in its DOS emulator, for the second scenario. Not runnable as a scenario yet.

## What is built

- `site.py`: starts one headless Chromium (Playwright's) with a debugging port; runs the
  evaluator; attaches a Playwright MCP server (`--cdp-endpoint`, `--caps vision`) to the same
  browser. Its address is what an arm would receive: `browser_take_screenshot`,
  `browser_press_key`, `browser_mouse_click_xy`.
- `evaluator.js`: the evaluator's own connection over CDP. It routes the site's requests
  (third-party requests aborted, at most two at a time, retries with backoff), plays the fixed
  opening (party Ma, Doc, Jed, Tully, Pip; Banker; 6 oxen, 4 clothing, 10 boxes of bullets, one
  spare wheel, axle and tongue, 600 lb of food; start in May), then records every key and
  click the page receives with a canvas screenshot after each, and one every five seconds.
- `bench/mcpclient.py`: a small MCP client over Streamable HTTP.

## Manual smoke check (not run by `scripts/check`)

Playwright MCP is installed outside the repository (`npm install @playwright/mcp` in a scratch
folder); pass its binary:

```
python -m bench.envs.oregon_trail_site.site --smoke --evidence /tmp/trail-smoke \
    --mcp-bin /path/to/node_modules/.bin/playwright-mcp
```

On 2026-11-20 it loaded the site through the proxy in about 165 seconds, reached the first
travelling screen, listed the MCP tools, returned a screenshot inline, and played two clicks
(Continue, then Time Out) that the evaluator recorded with screenshots.

## Not built

Arms for this environment, reading the game's state from screenshots for scoring, local caching
of the site's static assets between runs, and any check of whether the emulator exposes the
game's memory to the page.
