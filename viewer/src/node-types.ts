import { createElement, type ComponentType } from "react";
import type { NodeProps } from "@xyflow/react";
import { Cell, type CellData } from "./components/Cell";
import { Note } from "./components/Note";
import { Space } from "./components/Space";

type Props = NodeProps & { data: CellData };

/** A node type for an archetype: a thin wrapper over the one cell, adding its class. */
const cellOf = (archetype: string): ComponentType<Props> => {
  const Typed = ({ data }: Props) => createElement(Cell, { data, variant: archetype });
  Typed.displayName = `Cell(${archetype})`;
  return Typed;
};

/** The one table of node types, keyed by the archetype names bench/timeline.py emits, plus the
 * two forms a page can take beside a plain cell: a space and a note. Adding or restyling an
 * archetype is one entry here and one class in view.css. */
export const NODE_TYPES = {
  character: cellOf("character"),
  provider: cellOf("provider"),
  measure: cellOf("measure"),
  reflex: cellOf("reflex"),
  screen: cellOf("screen"),
  hands: cellOf("hands"),
  page: cellOf("page"),
  space: Space,
  note: Note,
} as Record<string, ComponentType<Props>>;

export function typeOf(form: string, archetype: string): string {
  if (form === "space" || form === "note") return form;
  return archetype in NODE_TYPES ? archetype : "page";
}
