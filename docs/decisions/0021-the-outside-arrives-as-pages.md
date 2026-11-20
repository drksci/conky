---
kind: decision
title: The outside arrives as pages
status: accepted
date: 2026-11-20
source: maintainers
---

# 0021 The outside arrives as pages

## Context

- The terminal connector turns a program's screen into writes to one page and a character's answer into writes to another.
- The next consumers are a browser and the many tool servers that speak the Model Context Protocol. One connector per case would give each its own way to be found, called and limited.
- The survey in [browser drivers](../research/browser-drivers.md) found that most leading browser drivers can be reached over that protocol, so a general connector reaches the browser without driver code of its own.

## Decision

A connector brings a space into the vault. The pages it writes are what it perceives, and the pages others write to are what it can do. Nothing else is added: the parts are space, page, write, watch and rule.

- A tool is a page. A call is a write to it, and the result is a signed write back, caused by the request.
- A character finds what it can sense and do by reading the spaces it is within. There is no registry and no tool list placed in a prompt for it.
- What must never be called is a rule on the page or its space, evaluated by the runtime.
- A large or binary result is a file kept beside the page and linked from it.
- Characters do not call tools. A go-between page turns what a connector perceives into what a person would take from it, and turns a character's plain words into the request a tool expects. Its providers are tried in order and end in a reflex that needs no model.

The mechanism is set out in [the outside arrives as pages](../ideas/tools.md), which stays at the rung idea until it is built.

## Consequences

- The terminal connector is the first instance of this shape and is restated to it, not replaced.
- A general connector for the Model Context Protocol is built before any connector for a single product.
- Reach by membership depends on spaces handing down more than rules, which is the roadmap step marked next.
- A party cannot see a canvas game until files beside pages and image-reading providers exist. Until then a figure of that game is a schematic and says so.
- Removed: a separate tool registry, and tool lists written into prompts.
