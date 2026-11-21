// The few numbers the layout needs, from the token file, and the view's framing.
import tokens from "../../src/conky/tokens.json";

export const SPACE = tokens.space;
// A port board's measures, the same as the stylesheet's: a line of text (--line), the socket
// square (--socket), the room between and around them, and the socket's inset from the board's
// outer edge, which centres it on its line.
const LINE = tokens.size.base * 1.4;
export const BOARD = { line: LINE, socket: tokens.space.base, gap: tokens.space.fine, pad: tokens.space.fine, inset: (LINE - tokens.space.base) / 2 };
// A board's fixed thickness: on a top or bottom edge one line; on a side, room for a socket and
// its mark (compact) or its short words, which wrap there (detailed).
export const THICK = {
  across: LINE + tokens.space.fine,
  side: { compact: tokens.space.far, detailed: tokens.space.far + tokens.space.wide },
};
/** How wide a socket's words may be on a side board: beside the socket, or on a wall, above it. */
export const sideWords = (density: "compact" | "detailed", above: boolean) =>
  THICK.side[density] - BOARD.inset - BOARD.pad - (above ? 0 : BOARD.socket + BOARD.gap);
// about this many members in a row of a region: notes shown to a space are wide, others small
export const GRID_COLUMNS: Record<string, number> = { shown: 2, hidden: 8, desk: 8, terms: 1 };
export const REGION_HEAD = tokens.space.wide + tokens.space.base; // room for a region's label
export const SHEET = 720; // CSS pixels a rendered picture is at most wide: the README's width
export const MAX_ZOOM = 1.25; // a small graph is not blown up past this
export const MIN_ZOOM = 0.6; // below this the labels stop being legible
