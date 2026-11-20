"""The trail environment: the real 1992 game in a browser, handed to a harness as a browser tool.

The runner starts one headless Chromium with a debugging port. The evaluator (`evaluator.js`)
connects to it first, plays the fixed opening to the first travelling screen and records
evidence for the whole run. Then a Playwright MCP server is attached to the same browser and its
address is what an adapter receives. Nothing here captions a screen for a harness: a harness
sees screenshots and sends keys and clicks.

Manual smoke check, never run by `scripts/check` (it loads the real site):

    python -m bench.envs.oregon_trail_site.site --smoke --evidence /tmp/trail-smoke \
        --mcp-bin /path/to/node_modules/.bin/playwright-mcp

It boots the site, plays the opening, attaches the MCP server and plays two inputs through it:
a click on Continue and, a few seconds later, a click on Time Out.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from bench.mcpclient import McpClient

HERE = Path(__file__).resolve().parent
FLAGS = [
    "--headless=new",
    "--no-sandbox",
    "--use-gl=swiftshader",
    "--enable-unsafe-swiftshader",
    "--no-first-run",
    "--no-default-browser-check",
    "--window-size=1100,800",
]
# Where the travelling screen's two big buttons sit, in canvas pixels (canvas 1030 by 774).
CONTINUE = (727, 601)
PAUSE = (727, 601)


def free_port() -> int:
    with socket.socket() as found:
        found.bind(("127.0.0.1", 0))
        return found.getsockname()[1]


def chromium() -> str:
    """Return the Chromium that Playwright for Node has installed."""
    out = subprocess.run(
        ["node", "-e", "console.log(require('playwright').chromium.executablePath())"],
        capture_output=True,
        text=True,
        env=node_env(),
        check=True,
    )
    return out.stdout.strip()


def node_env() -> dict[str, str]:
    """Let node find a globally installed playwright."""
    root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    paths = [p for p in (os.environ.get("NODE_PATH", ""), root) if p]
    return {**os.environ, "NODE_PATH": os.pathsep.join(paths)}


def wait_for(check, seconds: float, what: str):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        found = check()
        if found:
            return found
        time.sleep(0.5)
    raise TimeoutError(f"{what} did not happen within {seconds:.0f} seconds")


@dataclass
class Site:
    """One running environment: the browser, the evaluator and the MCP server."""

    evidence: Path
    cdp: str
    mcp: str
    processes: list[subprocess.Popen]

    def stop(self) -> None:
        (self.evidence / "stop").write_text("stop\n")
        for proc in reversed(self.processes):
            if proc.poll() is None:
                if proc.stdin:
                    proc.stdin.close()
                try:
                    proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()


def _cdp_up(port: int) -> bool:
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(f"http://127.0.0.1:{port}/json/version", timeout=2) as reply:
            return reply.status == 200
    except OSError:
        return False


def start(evidence: Path, mcp_bin: str, opening: bool = True) -> Site:
    """Start the browser, run the opening with the evaluator, then attach the MCP server."""
    evidence.mkdir(parents=True, exist_ok=True)
    port, mcp_port = free_port(), free_port()
    logs = (evidence / "browser.log").open("w")
    browser = subprocess.Popen(
        [
            chromium(),
            *FLAGS,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={evidence}/profile",
        ],
        stdout=logs,
        stderr=subprocess.STDOUT,
    )
    processes = [browser]
    wait_for(lambda: _cdp_up(port), 30, "the browser's debugging port")
    cdp = f"http://127.0.0.1:{port}"
    command = ["node", str(HERE / "evaluator.js"), "--cdp", cdp, "--evidence", str(evidence)]
    if not opening:
        command.append("--no-opening")
    evaluator = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=(evidence / "evaluator.out").open("w"),
        stderr=subprocess.STDOUT,
        env=node_env(),
    )
    processes.append(evaluator)

    def ready():
        if evaluator.poll() is not None:
            raise RuntimeError(f"the evaluator stopped: see {evidence / 'evaluator.log'}")
        path = evidence / "ready.json"
        return json.loads(path.read_text()) if path.exists() else None

    found = wait_for(ready, 600, "the opening")
    if not found.get("ok"):
        raise RuntimeError(f"the opening failed: {found}")
    server = subprocess.Popen(
        [mcp_bin, "--cdp-endpoint", cdp, "--caps", "vision", "--port", str(mcp_port)]
        + ["--output-dir", str(evidence / "mcp-files"), "--image-responses", "allow"],
        stdout=(evidence / "mcp.log").open("w"),
        stderr=subprocess.STDOUT,
        env=node_env(),
    )
    processes.append(server)
    mcp = f"http://127.0.0.1:{mcp_port}/mcp"

    def listening() -> bool:
        with socket.socket() as probe:
            return probe.connect_ex(("127.0.0.1", mcp_port)) == 0

    wait_for(listening, 60, "the MCP server")
    (evidence / "endpoint.json").write_text(json.dumps({"mcp": mcp, "cdp_private": cdp}))
    return Site(evidence, cdp, mcp, processes)


def save_image(content: list[dict], path: Path) -> bool:
    for item in content:
        if item.get("type") == "image":
            path.write_bytes(base64.b64decode(item["data"]))
            return True
    return False


def smoke(evidence: Path, mcp_bin: str) -> int:
    started = time.monotonic()
    site = start(evidence, mcp_bin)
    report = {"opening_seconds": round(time.monotonic() - started, 1)}
    try:
        ready = json.loads((evidence / "ready.json").read_text())
        box = ready["canvas"]
        client = McpClient(site.mcp)
        client.start()
        names = [tool["name"] for tool in client.tools()]
        report["tools"] = names
        shot = client.call("browser_take_screenshot", {"type": "png"})
        report["screenshot_inline"] = save_image(shot, evidence / "smoke-0.png")
        x, y = box["x"] + CONTINUE[0], box["y"] + CONTINUE[1]
        report["input_1"] = client.call(
            "browser_mouse_click_xy", {"element": "Continue", "x": x, "y": y}
        )[:1]
        time.sleep(6)
        save_image(
            client.call("browser_take_screenshot", {"type": "png"}), evidence / "smoke-1.png"
        )
        x, y = box["x"] + PAUSE[0], box["y"] + PAUSE[1]
        report["input_2"] = client.call(
            "browser_mouse_click_xy", {"element": "Time Out", "x": x, "y": y}
        )[:1]
        time.sleep(3)
        save_image(
            client.call("browser_take_screenshot", {"type": "png"}), evidence / "smoke-2.png"
        )
    finally:
        site.stop()
    inputs = evidence / "inputs.jsonl"
    report["evidence_inputs"] = inputs.read_text().splitlines() if inputs.exists() else []
    report["evidence_shots"] = sorted(p.name for p in (evidence / "shots").glob("*.png"))[:20]
    print(json.dumps(report, indent=1, default=str)[:6000])
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--mcp-bin", default=shutil.which("playwright-mcp") or "playwright-mcp")
    args = parser.parse_args()
    if args.smoke:
        return smoke(args.evidence, args.mcp_bin)
    parser.error("only --smoke is offered on its own; the runner starts the site for runs")
    return 2


if __name__ == "__main__":
    sys.exit(main())
