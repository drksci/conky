"""Check the documentation: frontmatter, folders, statuses and links."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
KEYS = ("kind", "title", "status", "date", "source")
FOLDER_KIND = {
    "decisions": "decision",
    "ideas": "idea",
    "essays": "essay",
    "project": "project",
    "research": "research",
}
STATUSES = {
    "design": {"current", "draft"},
    "decision": {"accepted", "open", "superseded"},
    "idea": {"idea", "folded", "enforced", "proven"},
    "essay": {"current", "draft"},
    "project": {"current", "draft"},
    "research": {"current", "draft"},
}
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
STEP = re.compile(r"^- (R\d+) \((done|next|later)\): ", re.MULTILINE)
DECISION_NAME = re.compile(r"^(\d{4})-[a-z0-9]+(-[a-z0-9]+)*\.md$")


def checked_documents() -> list[Path]:
    """Every Markdown file under docs/ except the index."""
    found = []
    for path in sorted(DOCS.rglob("*.md")):
        if path == DOCS / "README.md":
            continue
        found.append(path)
    return found


def frontmatter(text: str) -> dict | None:
    """Return the parsed frontmatter mapping, or None if absent or invalid."""
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def expected_kind(path: Path) -> str:
    rel = path.relative_to(DOCS)
    if len(rel.parts) == 1:
        return "design" if rel.name == "design.md" else ""
    return FOLDER_KIND.get(rel.parts[0], "")


def check_links(path: Path, text: str) -> list[str]:
    problems = []
    for target in LINK.findall(text):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
            continue
        file_part = target.split("#", 1)[0]
        if file_part and not (path.parent / file_part).resolve().exists():
            problems.append(f"{path.relative_to(ROOT)}: broken link {target}")
    return problems


def check_roadmap(text: str) -> list[str]:
    """The roadmap has steps with unique ids and exactly one step marked next."""
    steps = STEP.findall(text)
    problems = []
    if not steps:
        problems.append("docs/project/roadmap.md: no steps found")
    ids = [step_id for step_id, _ in steps]
    for step_id in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(f"docs/project/roadmap.md: duplicate id {step_id}")
    marked = [step_id for step_id, state in steps if state == "next"]
    if steps and len(marked) != 1:
        problems.append(
            f"docs/project/roadmap.md: exactly one step must be next, found {len(marked)}"
        )
    return problems


def check() -> list[str]:
    problems: list[str] = []
    documents = checked_documents()
    for path in documents:
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        meta = frontmatter(text)
        if meta is None:
            problems.append(f"{rel}: missing or invalid frontmatter")
        else:
            missing = [k for k in KEYS if k not in meta]
            if missing:
                problems.append(f"{rel}: frontmatter missing {', '.join(missing)}")
            kind = meta.get("kind")
            want = expected_kind(path)
            if not want:
                problems.append(f"{rel}: not in a known docs folder")
            elif kind != want:
                problems.append(f"{rel}: kind is {kind!r}, expected {want!r}")
            if kind in STATUSES and meta.get("status") not in STATUSES[kind]:
                problems.append(f"{rel}: status {meta.get('status')!r} not allowed for {kind}")
            if kind not in STATUSES:
                problems.append(f"{rel}: unknown kind {kind!r}")
        problems += check_links(path, text)

    numbers = []
    for path in documents:
        if path.parent == DOCS / "decisions":
            match = DECISION_NAME.match(path.name)
            if match:
                numbers.append(int(match.group(1)))
            else:
                problems.append(f"{path.relative_to(ROOT)}: name must be NNNN-short-name.md")
    if sorted(numbers) != list(range(1, len(numbers) + 1)):
        problems.append("decisions: numbers must be unique and consecutive from 0001")

    index = DOCS / "README.md"
    index_text = index.read_text(encoding="utf-8") if index.exists() else ""
    if not index.exists():
        problems.append("docs/README.md: missing")
    linked = {
        (index.parent / t.split("#", 1)[0]).resolve()
        for t in LINK.findall(index_text)
        if not re.match(r"^[a-z][a-z0-9+.-]*:", t)
    }
    for path in documents:
        if path.resolve() not in linked:
            problems.append(f"docs/README.md: does not link {path.relative_to(ROOT)}")

    roadmap = DOCS / "project" / "roadmap.md"
    if roadmap.exists():
        problems += check_roadmap(roadmap.read_text(encoding="utf-8"))
    else:
        problems.append("docs/project/roadmap.md: missing")

    for extra in (index, ROOT / "README.md", ROOT / "CLAUDE.md"):
        if extra.exists():
            problems += check_links(extra, extra.read_text(encoding="utf-8"))
    return problems


def main() -> int:
    problems = check()
    for problem in problems:
        print(problem)
    if problems:
        print(f"{len(problems)} problem(s)")
        return 1
    print(f"docs ok: {len(checked_documents())} documents")
    return 0


if __name__ == "__main__":
    sys.exit(main())
