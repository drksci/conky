---
kind: idea
title: "A look: a kind's page says how its pages are drawn"
status: idea
date: 2026-11-21
source: maintainers
arch:
  items:
  - kind: unplaced
    name: a look handed down by a space
    text: A page whose body is drawn against whichever page reads it, with views named from a fixed list. Nothing is built; a trial outside this repository comes first.
---

# A look: a kind's page says how its pages are drawn

## Idea

Rung: idea. Nothing here is built.

Every viewer of a vault ends up deciding how a character, a place or a plain page should be drawn, and each decides alone. The drawing then lives in the viewer's code, where no character can read it, change it or disagree with it.

A look moves that decision into the vault. A look is an ordinary page. Its body is Markdown with embeds and a few fenced blocks. The word after the fence names a view, and the lines inside are its settings in YAML, with a field bound by an expression:

````markdown
---
Mood: 64
asked: 4
budget: {asks: 8}
---
# ![[page#name]]

```meter
value: page.Mood
low: 20
```

```count
value: page.asked
of: page.budget.asks
label: asks
```
````

A space hands a look down to the pages within it, as it hands down rules. Drawing a page means reading its look with `page` standing for that page. The look carries example values in its own fields, so it also draws itself: opened on its own, it is the documentation of the kind.

What a page is drawn from is data. Resolving a look against a page gives a plain list of views with their values, and that list is the thing to get right first. A screen is one consumer of it, a text outline for a model is another, and a test can read it with no screen at all.

## The walk

1. The image. A form printed once and filled in by each person. The printed form is the kind; a filled copy is one page.
2. The general case. A page read through another page. Embeds already do this for one field or one body.
3. Existing words. Page, space, hands down, embed, expression, field, write. One thing is left over: the fenced view.
4. The natural gesture. A person writing a note about themselves puts a heading, a line and a small table. A fenced block is what Markdown already offers for "this part is not prose".
5. Par. A document names a kind of view and binds it to data, and the reader owns the code that draws it. Every system looked at below does this; see Prior art.
6. Who does it. A character can write a look for its own space, since a look is a page. The runtime would only resolve it.
7. The trial. Below.
8. How it is seen. Opening the look shows the kind drawn with its example values. Opening any page of the kind shows the same shape with that page's values, changing as writes arrive.
9. The smallest step. Resolve one look against one recorded page into data, outside this repository, before any screen is changed.

## Three parts

1. Declare. A fenced block on the kind's page: the name of a view, and settings whose values may be expressions over `page`. A node of a drawing is declared the same way, since a node is a name and its data.
2. Resolve. A page read through its look gives a flat list of views with their values. Done for every page, that list is the whole composition of a vault, and it is data that can be checked with no screen.
3. Stream. Each commit changes some fields, so it changes some values in that list. What is sent to a reader is the first list and then the changes.

The reader keeps a list of the views it can draw, by name. A name it does not know is shown as the block's own text.

## Prior art

Looked up on 21 November 2026. Where a point could not be confirmed from the page it says so.

| Approach | Where the drawing code lives | How a document binds data | Code in the document | Changes pushed |
|---|---|---|---|---|
| [Markdoc](https://markdoc.dev/docs/tags) | The renderer: a tag is mapped to a component in configuration | Variables and configured functions | Not confirmed either way | No |
| [MDX](https://mdxjs.com/docs/using-mdx/) | The renderer: "an object mapping component names to components" | JavaScript expressions | Yes | No |
| [MyST directives](https://myst-parser.readthedocs.io/en/latest/syntax/roles-and-directives.html) | The renderer | An option block at the head of a fence | No | Not confirmed |
| [remark-directive](https://github.com/remarkjs/remark-directive) | A plugin of the host | Attributes | No | No |
| [Obsidian code block processors](https://docs.obsidian.md/Plugins/Editor/Markdown+post+processing) | A plugin, registered against a fence's language | The block's own text | No | No |
| [Home Assistant cards](https://www.home-assistant.io/dashboards/cards/) | A module in the browser, named `custom:NAME` | YAML: `type` and `entity` | No | Yes: the card is handed the new state on every change |
| Kubernetes printer columns | The server | A path into the object, declared on the kind's own definition (from a summary of the page, not read in full) | No | Not applicable |
| [React Flow](https://reactflow.dev/learn/customization/custom-nodes) | The application: a map from a node's `type` to a component | The node's `data` | No | No |
| [A2UI](https://a2ui.org/specification/v1.0-a2ui/) | The client's catalogue | A pointer into a data model | No: "A2UI expresses UI using data, not code" | Yes: a stream of component and data updates |
| [AG-UI](https://docs.ag-ui.com/concepts/events) | The front end | State sent whole, then as JSON Patch | No | Yes |

Two things follow. First, a custom node does not need code in the document: in React Flow a node is `id`, `type`, `position` and `data`, and the component is found by `type` in a map the application holds. MDX uses the same kind of map, and what it adds is JavaScript in the document, which is the part to leave out. Second, the closest whole example is Home Assistant: a card is YAML naming a type and the thing it shows, the code is registered apart from it by name, and new state is pushed to the card. The shape proposed here is that one, with a page where it has an entity and an expression where it has an entity's name.

A fence is chosen over a directive because an unknown fence still shows its text in any Markdown tool, where remark's unhandled directives "do not emit anything".

For the second and third parts there are standards to stand on and no reason to invent: A2UI's messages for the list and its updates, which the [screen](a2ui.md) idea already takes; JSON Patch for a change; and the [CloudEvents](https://github.com/cloudevents/spec/blob/main/cloudevents/spec.md) attributes (`type`, `source`, `subject`, `time`) for what wraps an event on its way out.

## Decided against

Components shipped in the vault as code, in the manner of MDX. They would put a program in a place that holds only open formats, make opening a stranger's vault a matter of trust, and let structure be installed where it should be composed. A view is a name the reader knows. A name it does not know is shown as the block's own text, so a vault still reads in any Markdown tool.

A separate stream of events with its own schemas. Every write is already a commit with trailers, and a measure already records its value as an event. A page's fields are its schema. What a live screen needs is one connector that follows the history and says which page changed.

## Composes from

Page, space, embed, expression, and the vault's Git history. The [screen](a2ui.md) and the [codec](codec.md) are consumers of the same resolved list. [What a space hands down](inheritance.md) is the mechanism.

## Removes

Per-kind layouts written into each viewer. A preview mode with sample data. A schema language for events.

## Falsifying test

Three looks (somebody, a place, a plain page) written as pages in a recorded vault replace three layouts now written in a viewer's code, and the pages are drawn the same. The bet is lost if the list of views has to grow past eight to do it, or if a look needs logic that an expression over `page` cannot say. Either result puts components as code back on the table.

## Open questions

- Whether a look is found by `within` alone or a page may name its look.
- Whether a binding inside the vault stays an expression, as rules are, and becomes a pointer only when the list is sent out.
- Whether a view may read pages other than the one being drawn, as an embed can.
- How a look says which of two looks handed down from two spaces wins.
