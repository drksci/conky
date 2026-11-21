import { createContext, useContext } from "react";
import type { Density, Frame, Mode } from "./graph";

export interface Seen {
  frame: Frame;
  mode: Mode;
  density: Density;
  open?: (id: string) => void; // the side panel, in the interactive view only
}

export const FrameContext = createContext<Seen>({
  frame: { shown: new Set(), values: new Map(), pens: new Map(), dim: new Set(), plugged: new Set(), regions: [], step: 0 },
  mode: "dynamics",
  density: "compact",
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

/** A value as it stands in this frame. */
export const valueOf = (seen: Seen, id: string | null | undefined): string => (id ? seen.frame.values.get(id) ?? "" : "");
