import { createContext, useContext } from "react";
import type { Frame, Mode } from "./graph";

export interface Seen {
  frame: Frame;
  mode: Mode;
}

export const FrameContext = createContext<Seen>({
  frame: { shown: new Set(), values: new Map(), pens: new Map(), dim: new Set() },
  mode: "dynamics",
});

export const useSeen = () => useContext(FrameContext);

/** The classes that say how an element stands in this frame: not yet there, the subject of the
 * step with the meaning of its pen, or dimmed. The stylesheet decides what each looks like. */
export function standing(seen: Seen, id: string): string {
  const pen = seen.frame.pens.get(id);
  return [
    seen.frame.shown.has(id) ? "" : "is-hidden",
    pen ? `is-subject is-${pen}` : "",
    seen.frame.dim.has(id) ? "is-dim" : "",
  ]
    .filter(Boolean)
    .join(" ");
}
