"""Generate docs/reference/architecture.md from the code and the documents.

What is built comes from the markers in `src/conky/` (see `conky.arch`). What is planned or an
idea comes from the `arch` key in the frontmatter of the pages in `docs/ideas/` and
`docs/decisions/`. The page is never edited by hand: run this script to rewrite it, and
`scripts/check_docs.py` fails when the committed page differs from what this script makes.

Each frontmatter `arch` is a mapping with two optional keys:

    covers: [kind:name, ...]      built or planned rows this document is carried by
    items:                        facts this document holds
      - kind: law|part|archetype|stage|change|data|flow|unplaced
        name: ...
        roadmap: R12              the step that delivers it, which decides the state
        state: idea               only for an idea with no step, or to say it is still an idea
        text / statement / by / layer / phase / where / title / rank / steps ...
"""

from __future__ import annotations

import ast
import importlib
import pkgutil
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
PAGE = DOCS / "reference" / "architecture.md"
sys.path.insert(0, str(ROOT / "src"))

from conky import arch  # noqa: E402

STEP = re.compile(r"^- (R\d+[a-z]?) \((done|next|later)\): ", re.MULTILINE)
STATES = ("built", "building", "planned", "idea")
PHASE_TITLES = {
    "stimulus": "Stimulus",
    "notice": "Notice",
    "attention": "Attention beyond notice",
    "think": "Think",
    "act": "Act",
    "record": "Record",
}
KINDS = ("law", "part", "archetype", "stage", "change", "data", "flow", "judged", "unplaced")


class ArchitectureError(Exception):
    """The registry and the documents disagree; the message says which and what to edit."""


@dataclass
class Row:
    """One row of the page: a fact from the code or from a document."""

    kind: str
    name: str
    text: str = ""
    doc: str = ""
    code: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    roadmap: str | None = None
    state: str = "built"
    source: str = "code"
    rung: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.kind}:{self.name}"


def slug(heading: str) -> str:
    """Return the anchor GitHub gives a heading."""
    text = re.sub(r"[`*_]", "", heading.strip().lower())
    return re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", text))


def anchors(path: Path) -> set[str]:
    found = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"#{1,6} ", line):
            found.add(slug(line.lstrip("# ")))
    return found


def check_link(target: str, where: str) -> None:
    """Fail unless a link from docs/reference names a real file and heading."""
    file_part, _, anchor = target.partition("#")
    path = (DOCS / "reference" / file_part).resolve()
    if not path.exists():
        raise ArchitectureError(f"{where}: the link {target} names no file: correct its doc=")
    if anchor and anchor not in anchors(path):
        raise ArchitectureError(f"{where}: {target} names a heading that does not exist")


def roadmap() -> dict[str, str]:
    text = (DOCS / "project" / "roadmap.md").read_text(encoding="utf-8")
    return {step: state for step, state in STEP.findall(text)}


def load_code() -> None:
    import conky

    for info in pkgutil.iter_modules(conky.__path__):
        importlib.import_module(f"conky.{info.name}")


def resolve(ref: str) -> object:
    """Import and return the code a reference names, or the path it names."""
    if not ref.startswith("conky."):
        if not (ROOT / ref).exists():
            raise ArchitectureError(f"{ref} is not in the repository: correct the marker")
        return ref
    parts = ref.split(".")
    for cut in range(len(parts), 0, -1):
        try:
            found: object = importlib.import_module(".".join(parts[:cut]))
        except ImportError:
            continue
        for name in parts[cut:]:
            found = getattr(found, name)
        return found
    raise ArchitectureError(f"{ref} does not import")


def test_marks() -> dict[str, list[str]]:
    """Return, for each law or flow name, the measured tests that hold it, found by reading them."""
    found: dict[str, list[str]] = {}
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            for deco in node.decorator_list:
                if (
                    isinstance(deco, ast.Call)
                    and isinstance(deco.func, ast.Attribute)
                    and deco.func.attr == "holds"
                ):
                    kinds = {k.arg: k.value for k in deco.keywords}
                    kind = kinds.get("kind")
                    if isinstance(kind, ast.Constant) and kind.value != "measured":
                        continue
                    for arg in deco.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            ref = f"tests/{path.name}::{node.name}"
                            found.setdefault(arg.value, []).append(ref)
    return found


def state_of(step: str | None, explicit: str | None, where: str, from_code: bool) -> str:
    """Return the state a row has, from the roadmap step it cites."""
    steps = roadmap()
    if step is not None and step not in steps:
        raise ArchitectureError(f"{where}: step {step} is not in docs/project/roadmap.md")
    if from_code:
        if step is None:
            return "built"
        if steps[step] == "later":
            raise ArchitectureError(
                f"{where}: the code is marked with step {step}, which the roadmap says is later: "
                "mark the step done or next in the roadmap, or remove the marker"
            )
        return "built" if steps[step] == "done" else "building"
    if explicit is not None:
        if explicit not in STATES[2:]:
            raise ArchitectureError(f"{where}: state {explicit} must be planned or idea")
        if step is not None and steps[step] == "done":
            raise ArchitectureError(
                f"{where}: step {step} is done, so this is built: annotate the code"
            )
        return explicit
    if step is None:
        raise ArchitectureError(f"{where}: give a roadmap step, or state: idea")
    if steps[step] == "done":
        raise ArchitectureError(
            f"{where}: step {step} is done, so this is built: annotate the code"
        )
    return "building" if steps[step] == "next" else "planned"


def code_rows() -> tuple[dict[str, Row], list[arch.Entry]]:
    rows: dict[str, Row] = {}
    steps = []
    for entry in arch.ENTRIES:
        facts = entry.facts
        if entry.kind in ("step", "holds", "judged"):
            if entry.kind == "step":
                steps.append(entry)
            continue
        name = facts["name"]
        where = f"{entry.ref} ({entry.kind} {name})"
        resolve(entry.ref)
        check_link(facts["doc"], where)
        row = Row(
            entry.kind,
            name,
            facts.get("statement") or facts.get("text") or "",
            facts["doc"],
            roadmap=facts.get("roadmap"),
            extra={
                k: v for k, v in facts.items() if k in ("layer", "by", "phase", "where", "slot")
            },
        )
        row.state = state_of(row.roadmap, None, where, True)
        old = rows.get(row.key)
        if old:
            old.code.append(entry.ref)
            continue
        row.code.append(entry.ref)
        rows[row.key] = row
    return rows, steps


def doc_rows() -> tuple[dict[str, Row], list[tuple[Path, dict]], dict[str, dict]]:
    rows: dict[str, Row] = {}
    docs: list[tuple[Path, dict]] = []
    flows: dict[str, dict] = {}
    for folder in ("ideas", "decisions"):
        for path in sorted((DOCS / folder).glob("*.md")):
            text = path.read_text(encoding="utf-8")
            match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
            meta = yaml.safe_load(match.group(1)) if match else {}
            rel = path.relative_to(ROOT)
            facts = meta.get("arch")
            if not isinstance(facts, dict) or not (facts.get("covers") or facts.get("items")):
                raise ArchitectureError(
                    f"{rel}: has no arch in its frontmatter: add covers (rows that carry it) "
                    "or items (what it holds), or an unplaced item"
                )
            docs.append((path, {"status": meta.get("status"), "arch": facts}))
            link = f"../{folder}/{path.name}"
            for item in facts.get("items") or []:
                kind, name = item.get("kind"), item.get("name")
                where = f"{rel} ({kind} {name})"
                if kind not in KINDS or not name:
                    raise ArchitectureError(f"{where}: kind must be one of {', '.join(KINDS)}")
                if kind == "unplaced":
                    row = Row(kind, name, item.get("text", ""), link, state="idea", source=link)
                else:
                    row = Row(
                        kind,
                        name,
                        item.get("statement") or item.get("text") or item.get("statement_", ""),
                        link,
                        roadmap=item.get("roadmap"),
                        source=link,
                        rung=str(meta.get("status")),
                        extra={
                            k: v
                            for k, v in item.items()
                            if k
                            in (
                                "layer",
                                "by",
                                "phase",
                                "where",
                                "rank",
                                "title",
                                "steps",
                                "question",
                                "evidence",
                                "scale",
                                "checks",
                            )
                        },
                    )
                    row.state = state_of(row.roadmap, item.get("state"), where, False)
                if row.key in rows:
                    raise ArchitectureError(
                        f"{where}: {row.key} is already held by {rows[row.key].source}"
                    )
                rows[row.key] = row
                if kind == "flow":
                    flows[name] = item
    return rows, docs, flows


def build_rows() -> tuple[
    dict[str, Row], list[arch.Entry], list[tuple[Path, dict]], dict[str, dict]
]:
    load_code()
    code, steps = code_rows()
    planned, docs, flows = doc_rows()
    clash = set(code) & set(planned)
    if clash:
        raise ArchitectureError(
            f"{sorted(clash)[0]} is both annotated in the code and written in a document: "
            "keep the code marker and delete the document's item"
        )
    rows = {**code, **planned}
    for layer_row in arch.LAYERS:
        rows[f"layer:{layer_row.id}"] = Row("layer", layer_row.id, layer_row.holds)
    marks = test_marks()
    names = {r.name for r in rows.values() if r.kind == "law"} | {f.name for f in arch.FLOWS}
    names |= set(flows)
    for name, refs in marks.items():
        if name not in names:
            raise ArchitectureError(
                f"{refs[0]} holds {name!r}, which is no law or flow: correct the name in arch.holds"
            )
    for row in rows.values():
        if row.kind == "law":
            row.tests = marks.get(row.name, [])
            if row.state == "built" and not row.tests:
                row.tests = ["review"]
    for row in rows.values():
        layer = row.extra.get("layer")
        if layer and f"layer:{layer}" not in rows:
            raise ArchitectureError(
                f"{row.key}: layer {layer!r} is not one of the layers in conky.arch"
            )
    return rows, steps, docs, flows


def check_coverage(rows: dict[str, Row], docs: list[tuple[Path, dict]], flows: dict) -> None:
    for path, meta in docs:
        for ref in meta["arch"].get("covers") or []:
            if ref not in rows and not any(f"flow:{f.name}" == ref for f in arch.FLOWS):
                raise ArchitectureError(
                    f"{path.relative_to(ROOT)}: covers {ref}, which is no row: correct the name"
                )
    steps = roadmap()
    used = {row.roadmap for row in rows.values() if row.roadmap}
    used |= {f.roadmap for f in arch.FLOWS if f.roadmap}
    used |= {item.get("roadmap") for item in flows.values()}
    for step in steps:
        if step not in used:
            raise ArchitectureError(
                f"roadmap step {step} is in no row: mark the code it delivers with "
                f"roadmap={step!r}, or add an item with roadmap: {step} to the idea or decision "
                "that holds it"
            )


def esc(text: str) -> str:
    return text.replace("|", "\\|")


def cell_code(refs: list[str]) -> str:
    return "<br>".join(f"`{r}`" for r in refs) or "-"


def cell_tests(refs: list[str]) -> str:
    return "<br>".join(r if r == "review" else f"`{r}`" for r in refs) or "-"


def link(row: Row) -> str:
    return f"[{row.doc.rsplit('/', 1)[-1].split('#')[0].removesuffix('.md')}]({row.doc})"


def table(header: list[str], body: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(esc(c) for c in cells) + " |" for cells in body]
    return "\n".join(out)


def ordered(rows: list[Row]) -> list[Row]:
    return sorted(rows, key=lambda r: (STATES.index(r.state), r.name))


def of(rows: dict[str, Row], kind: str) -> list[Row]:
    return [r for r in rows.values() if r.kind == kind]


def doc_label(row: Row) -> str:
    base = row.doc.rsplit("/", 1)[-1]
    return f"[{base}]({row.doc})"


def sections_laws(rows: dict[str, Row]) -> str:
    body = [
        [
            r.name,
            r.text,
            doc_label(r),
            cell_code(r.code),
            cell_tests(r.tests),
            r.roadmap or "-",
            r.state,
        ]
        for r in ordered(of(rows, "law"))
    ]
    return table(["Law", "Statement", "Defined", "Code", "Test", "Step", "State"], body)


def sections_parts(rows: dict[str, Row]) -> str:
    layers = [layer.id for layer in arch.LAYERS]
    parts = sorted(
        of(rows, "part"),
        key=lambda r: (layers.index(r.extra.get("layer", "git")), STATES.index(r.state), r.name),
    )
    body = [
        [
            p.name,
            p.extra.get("layer", "-"),
            p.text,
            doc_label(p),
            cell_code(p.code),
            p.roadmap or "-",
            p.state,
        ]
        for p in parts
    ]
    return table(["Part", "Layer", "What", "Defined", "Code", "Step", "State"], body)


def sections_layers(rows: dict[str, Row]) -> str:
    body = []
    for layer in arch.LAYERS:
        here = [r for r in of(rows, "part") if r.extra.get("layer") == layer.id]
        have = ", ".join(f"`{r.name}`" for r in ordered(here) if r.state in ("built", "building"))
        plan = ", ".join(f"`{r.name}`" for r in ordered(here) if r.state in ("planned", "idea"))
        body.append([f"{layer.name} (`{layer.id}`)", layer.holds, have or "-", plan or "-"])
    return table(["Layer, from the store upwards", "Holds", "Built parts", "Planned parts"], body)


def sections_archetypes(rows: dict[str, Row]) -> str:
    body = [
        [
            a.name,
            a.extra.get("by", "-"),
            a.text,
            doc_label(a),
            cell_code(a.code),
            a.roadmap or "-",
            a.state,
        ]
        for a in ordered(of(rows, "archetype"))
    ]
    return table(["Kind of page", "Made by", "What", "Defined", "Code", "Step", "State"], body)


def members(ref: str) -> str:
    found = resolve(ref)
    if isinstance(found, type) and issubclass(found, __import__("enum").Enum):
        names = [str(m.value) for m in found]
    elif isinstance(found, dict):
        names = [str(k) for k in found]
    elif isinstance(found, tuple | list | set | frozenset):
        names = [str(v) for v in found]
    else:
        names = [getattr(found, "__name__", str(found))]
    return ", ".join(f"`{n}`" for n in names)


def sections_slots(rows: dict[str, Row]) -> str:
    body = [
        [
            s.name,
            s.extra.get("slot", "-"),
            members(s.code[0]),
            doc_label(s),
            cell_code(s.code),
        ]
        for s in sorted(of(rows, "slot"), key=lambda r: (r.extra.get("slot", ""), r.name))
    ]
    return table(["Slot", "Kind", "Members", "Defined", "Code"], body)


def sections_data(rows: dict[str, Row]) -> str:
    order = {k: i for i, k in enumerate(arch.DATA_KINDS)}
    body = [
        [d.name, d.text, doc_label(d), cell_code(d.code), d.roadmap or "-", d.state]
        for d in sorted(of(rows, "data"), key=lambda r: (order.get(r.name.split()[0], 9), r.name))
    ]
    return table(["Data kind", "What", "Defined", "Code", "Step", "State"], body)


def sections_changes(rows: dict[str, Row]) -> str:
    places = {p: i for i, p in enumerate(arch.CHANGE_PLACES)}
    body = [
        [
            c.extra.get("where", "-"),
            c.name,
            doc_label(c),
            cell_code(c.code),
            c.roadmap or "-",
            c.state,
        ]
        for c in sorted(
            of(rows, "change"),
            key=lambda r: (places[r.extra["where"]], STATES.index(r.state), r.name),
        )
    ]
    return table(["Where", "What changes it or does it", "Defined", "Code", "Step", "State"], body)


def sections_stages(rows: dict[str, Row]) -> str:
    order = {p: i for i, p in enumerate(arch.STAGE_PHASES)}
    body = []
    for s in sorted(
        of(rows, "stage"), key=lambda r: (order[r.extra["phase"]], STATES.index(r.state), r.name)
    ):
        body.append(
            [
                PHASE_TITLES[s.extra["phase"]],
                s.name,
                s.text,
                doc_label(s),
                cell_code(s.code),
                s.rung or "-",
                s.roadmap or "-",
                s.state,
            ]
        )
    return table(["Phase", "Stage", "What", "Defined", "Code", "Rung", "Step", "State"], body)


def judged_checks(rows: dict[str, Row]) -> list[dict]:
    """Return every judged declaration, from the code and from the documents."""
    found = [dict(e.facts, ref=e.ref) for e in arch.ENTRIES if e.kind == "judged"]
    for row in of(rows, "judged"):
        found.append({"name": row.name, "ref": row.doc, **row.extra, "state": row.state})
    return found


def sections_checks(rows: dict[str, Row]) -> str:
    """List every law, flow and part with its check, measured or judged, and the ones with none."""
    judged = judged_checks(rows)
    judged_for: dict[str, list[str]] = {}
    for j in judged:
        for name in j.get("checks") or []:
            judged_for.setdefault(name, []).append(j["name"])
    marks = test_marks()
    body = []
    things = [("law", r.name, r) for r in of(rows, "law")]
    things += [("flow", f.name, None) for f in arch.FLOWS]
    things += [("flow", n, r) for n, r in ((r.name, r) for r in of(rows, "flow"))]
    things += [("part", r.name, r) for r in of(rows, "part")]
    for kind, name, row in sorted(things, key=lambda t: (t[0], t[1])):
        state = row.state if row else "built"
        measured = marks.get(name, [])
        if row is not None and row.state not in ("built", "building"):
            cell = ["not built", "-", "-"]
        elif row is not None and row.kind == "law" and row.tests == ["review"]:
            cell = ["-", ", ".join(judged_for.get(name, [])) or "-", "review only"]
        else:
            cell = [
                str(len(measured)) if measured else "-",
                ", ".join(judged_for.get(name, [])) or "-",
                "" if measured or judged_for.get(name) else "none",
            ]
        body.append([f"{kind} `{name}`", state, *cell])
    head = ["Thing", "State", "Measured tests", "Judged checks", "No check"]
    out = table(head, body)
    if judged:
        rows_ = [
            [j["name"], j["question"], j["evidence"], j["scale"], ", ".join(j.get("checks") or [])]
            for j in sorted(judged, key=lambda j: j["name"])
        ]
        out += "\n\n" + table(["Judged check", "Question", "Evidence", "Scale", "Checks"], rows_)
    return out


def mermaid_text(text: str, where: str) -> str:
    if re.search(r"[;#%]", text):
        raise ArchitectureError(f"{where}: the text {text!r} holds a character Mermaid reads")
    return text


def diagram(title: str, state: str, steps: list[dict], where: str) -> str:
    lines = [
        "```mermaid",
        "---",
        f"title: {mermaid_text(title, where)} ({state})",
        "---",
        "sequenceDiagram",
    ]
    lines += [f"    participant {lane}" for lane in arch.LANES]
    inside = False
    for s in steps:
        frm, to, text = s["frm"], s["to"], mermaid_text(s["text"], where)
        for lane in (frm, to):
            if lane is not None and lane not in arch.LANES:
                raise ArchitectureError(
                    f"{where}: lane {lane!r} is not one of {', '.join(arch.LANES)}"
                )
        refusal = bool(s.get("refusal"))
        if refusal and not inside:
            lines.append("    alt refusal")
            inside = True
        if inside and not refusal:
            lines.append("    end")
            inside = False
        pad = "        " if inside else "    "
        if to is None:
            lines.append(f"{pad}Note over {frm}: {text}")
        else:
            arrow = "-->>" if refusal else "->>"
            lines.append(f"{pad}{frm}{arrow}{to}: {text}")
    if inside:
        lines.append("    end")
    lines.append("```")
    return "\n".join(lines)


def flows_section(rows: dict[str, Row], steps: list[arch.Entry], flows: dict[str, dict]) -> str:
    marks = test_marks()
    out = []
    declared = {f.name for f in arch.FLOWS}
    for entry in steps:
        if entry.facts["flow"] not in declared:
            raise ArchitectureError(
                f"{entry.ref}: step of flow {entry.facts['flow']!r}, which conky.arch.FLOWS "
                "does not declare"
            )
    from conky.vault import Vault

    named = {e.ref for e in steps}
    for attr, value in vars(Vault).items():
        if (
            callable(value)
            and not attr.startswith("_")
            and f"conky.vault.Vault.{attr}" not in named
        ):
            raise ArchitectureError(
                f"conky.vault.Vault.{attr} is on the write path but in no flow: add a row to "
                "conky.arch.VAULT_STEPS"
            )
    for flow in arch.FLOWS:
        mine = sorted(
            (e for e in steps if e.facts["flow"] == flow.name), key=lambda e: e.facts["order"]
        )
        if not mine:
            raise ArchitectureError(f"flow {flow.name} has no steps: mark the code that does them")
        orders = [e.facts["order"] for e in mine]
        if len(set(orders)) != len(orders):
            raise ArchitectureError(f"flow {flow.name} has two steps with the same order")
        state = state_of(flow.roadmap, None, f"flow {flow.name}", True)
        check_link(flow.doc, f"flow {flow.name}")
        refs = []
        for e in mine:
            resolve(e.ref)
            if e.ref not in refs:
                refs.append(e.ref)
        out.append(
            render_flow(
                flow.title,
                flow.statement,
                flow.name,
                state,
                flow.doc,
                refs,
                marks.get(flow.name, []),
                flow.roadmap,
                [dict(e.facts) for e in mine],
            )
        )
    for name, item in sorted(flows.items(), key=lambda kv: kv[1].get("rank", 99)):
        row = rows[f"flow:{name}"]
        out.append(
            render_flow(
                item["title"],
                item["statement"],
                name,
                row.state,
                row.doc,
                [],
                [],
                item.get("roadmap"),
                item["steps"],
            )
        )
    return "\n\n".join(out)


def render_flow(title, statement, name, state, doc, code, tests, step, steps) -> str:
    head = diagram(f"{title}", state, steps, f"flow {name}")
    note = table(
        ["Flow", "Doc", "Code", "Test", "Step", "State"],
        [
            [
                name,
                f"[{doc.rsplit('/', 1)[-1]}]({doc})",
                cell_code(code),
                cell_tests(tests),
                step or "-",
                state,
            ]
        ],
    )
    return f"{head}\n\n{statement}\n\n{note}"


FLOWCHART = """```mermaid
flowchart LR
    subgraph stimulus [Stimulus]
        S1["{accepted-write}"]
        S2["{perception-in}"]
        S3["{clock-tick}"]
        S4["{reaction-cascade}"]
        S5["{measure-and-pressure}"]
    end
    N["Notice: watch on and when, pressure, skip when unchanged"]
    T["Think: {asking-a-model}"]
    A["Act: field, {answer-is-pages}, {action-out}, {tool-call}"]
    R["Record: signed event or refusal, {refused-write}"]
    G{{"Rules of the page and its spaces, {join-and-leave}"}}
    S1 --> G
    S2 --> G
    S3 --> G
    G -->|held| R
    G -->|refused| R
    R -->|every write is a stimulus| S4
    S4 --> N
    S5 --> N
    N -->|state is enough| A
    N -->|state cannot answer| T
    T --> A
    A --> G
```"""


def flowchart(rows: dict[str, Row], flows: dict[str, dict]) -> str:
    titles = {f.name: f"{f.title}" for f in arch.FLOWS}
    for name, item in flows.items():
        titles[name] = f"{item['title']} (planned)"
    needed = re.findall(r"\{([a-z-]+)\}", FLOWCHART)
    for name in needed:
        if name not in titles:
            raise ArchitectureError(f"the overview names flow {name}, which does not exist")
    text = FLOWCHART
    for name in needed:
        text = text.replace("{" + name + "}", titles[name])
    return text.replace("{{", "{").replace("}}", "}")


def coverage(docs: list[tuple[Path, dict]], rows: dict[str, Row]) -> str:
    def carried(meta: dict) -> str:
        names = list(meta["arch"].get("covers") or [])
        names += [
            f"{i['kind']}:{i['name']}"
            for i in meta["arch"].get("items") or []
            if i["kind"] != "unplaced"
        ]
        return ", ".join(f"`{n}`" for n in names) or "-"

    parts = []
    for folder, head, column in (
        ("ideas", "Ideas", "Rung"),
        ("decisions", "Decisions", "Status"),
    ):
        body = []
        for path, meta in docs:
            if path.parent.name != folder:
                continue
            body.append(
                [f"[{path.stem}](../{folder}/{path.name})", str(meta["status"]), carried(meta)]
            )
        parts.append(f"### {head}\n\n" + table([head[:-1], column, "Carried by"], body))
    unplaced = [r for r in rows.values() if r.kind == "unplaced"]
    body = [[r.name, doc_label(r), r.text] for r in sorted(unplaced, key=lambda r: r.name)]
    parts.append(
        "### Unplaced\n\nFound in the documents and fitting no row above.\n\n"
        + table(["Item", "Where", "Note"], body)
    )
    return "\n\n".join(parts)


TEMPLATE = """---
kind: reference
title: Architecture index
status: current
date: 2026-11-20
source: maintainers
---

<!-- Generated by scripts/gen_architecture.py. Do not edit by hand. -->

# Architecture index

This page is the complete inventory of Conky's architecture, generated from markers in the code (what is built) and from the frontmatter of the ideas and decisions (what is planned). Every law, part, layer, kind of page, slot, kind of data, change of state, stage of attention and flow is a row. A figure or a document that shows something this page does not list is incomplete, and the fix is to mark the code, or add to the document's `arch`, and run `python scripts/gen_architecture.py`. The words are in [vocabulary](vocabulary.md), and the model in short is [design](../design.md).

`scripts/check_docs.py` fails when this page differs from what the generator makes. Nobody edits it by hand.

## States

| State | Means |
|---|---|
| built | Marked in the code, and the roadmap step, when there is one, is `done`. |
| building | The roadmap step is `next`. |
| planned | A document holds it and a roadmap step is `later`. |
| idea | A document holds it with no step. |

## 1. Laws

The capability and the three laws of [decision 0029](../decisions/0029-autonomy-inside-limits-that-hold.md), and each law of CLAUDE.md's "The model" section. A test of `review` is a gap to close.

{laws}

## 2. Parts

Every concept word and verb of the [vocabulary](vocabulary.md), and each named part of the runtime. The vocabulary page lists the names the code exposes, and `tests/test_house.py` compares it with the code.

{parts}

## 3. Layers

From the store upwards. Each layer sits on the one before.

{layers}

## 4. Archetypes

A kind of page is a way pages are used and never a type the runtime knows. Who makes it is a person, a character, a connector or the runtime, and the runtime makes no page.

{archetypes}

## 5. Slots

A slot is a named place that something plugs into. Where a constant is the list, its members are read from it.

{slots}

## 6. Data kinds

Data lives in three primitives in open formats: a document, a table and a stream ([decision 0010](../decisions/0010-no-debt-no-down-migrations.md)). Files beside pages are the one mechanism under a table and a stream, and a query engine is an optional reader beside the vault, never in the core.

{data}

## 7. Who changes what

A page holds what a vault knows, the fixed runtime does what follows from it, and some things sit beside the vault because they must never enter its history.

{changes}

## 8. Stimuli, attention and action

One chain: a stimulus arrives, it is noticed, thought happens when state cannot answer, and action leaves as a write. The flows in section 9 trace each stage.

{stages}

Attention beyond a watch entry and a threshold is held only by the rows of the attention phase and the rung of the document each cites. No document defines a rule for ranking which of several due things a character looks at first, or a signal of reward, resonance or drive. When one does, its row appears here.

## 9. Flows

Every flow is a sequence diagram with the same eight lanes in the same order, so a message between two lanes always means the same thing. A diagram that leaves a lane out still lists it. A step drawn inside `refusal` is the refusal branch. A planned flow says so in its title.

{lanes}

How the flows join into one loop:

{flowchart}

{flows}

## 10. Checks

Every law, flow and part with its check. A measured check is a deterministic assertion with an exact result, and every pytest test is one. A judged check is open-ended behaviour that no assertion settles: it names the question a reader answers from the end state, the evidence to look at and the scale, and `conky.arch.bundle` writes the evidence with a verdict only when one is given and by whom. A blank in the last column means a check exists, and `none` means nothing checks the thing at all.

{checks}

## 11. Coverage

Every idea and decision, with its rung or status and the rows that carry it. The generator fails when one is missing or names a row that does not exist.

{coverage}
"""  # noqa: E501


def build() -> str:
    rows, steps, docs, flows = build_rows()
    check_coverage(rows, docs, flows)
    lanes = table(["Lane", "Is"], [[lane, arch.LANE_MEANING[lane]] for lane in arch.LANES])
    text = TEMPLATE.format(
        laws=sections_laws(rows),
        parts=sections_parts(rows),
        layers=sections_layers(rows),
        archetypes=sections_archetypes(rows),
        slots=sections_slots(rows),
        data=sections_data(rows),
        changes=sections_changes(rows),
        stages=sections_stages(rows),
        lanes=lanes,
        flowchart=flowchart(rows, flows),
        flows=flows_section(rows, steps, flows),
        checks=sections_checks(rows),
        coverage=coverage(docs, rows),
    )
    return text.rstrip("\n") + "\n"


def check() -> list[str]:
    """Return a problem when the committed page differs from the generated one."""
    try:
        made = build()
    except ArchitectureError as exc:
        return [f"docs/reference/architecture.md: {exc}"]
    have = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
    if have != made:
        return [
            "docs/reference/architecture.md: differs from what the code and the documents say: "
            "run `python scripts/gen_architecture.py` and commit the result"
        ]
    return []


def main() -> int:
    if "--check" in sys.argv:
        problems = check()
        for problem in problems:
            print(problem)
        return 1 if problems else 0
    try:
        text = build()
    except ArchitectureError as exc:
        print(f"error: {exc}")
        return 1
    PAGE.write_text(text, encoding="utf-8")
    print(f"wrote {PAGE.relative_to(ROOT)}: {len(text.splitlines())} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
