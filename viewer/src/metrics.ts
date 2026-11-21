// The few numbers the layout needs, from the token file, and the view's framing.
import tokens from "../../src/conky/tokens.json";

export const SPACE = tokens.space;
// A port board's measures, the same as the stylesheet's: a port is a square block as wide as its
// board is thick, set in a row along the board with an even gap and a pad at each end; a port
// on a wall whose rules are shown has a line above its block for them (--line).
const LINE = tokens.size.base * 1.4;
export const PORT = { block: tokens.space.wide + tokens.space.fine, gap: tokens.space.fine, pad: tokens.space.fine, line: LINE };
// about this many members in a row of a region: notes shown to a space are wide, others small
export const GRID_COLUMNS: Record<string, number> = { shown: 2, hidden: 8, desk: 8, terms: 1 };
export const REGION_HEAD = tokens.space.wide + tokens.space.base; // room for a region's label
export const SHEET = 720; // CSS pixels a rendered picture is at most wide: the README's width
export const MAX_ZOOM = 1.25; // a small graph is not blown up past this
export const MIN_ZOOM = 0.6; // below this the labels stop being legible
export const EXPLORE_MIN = 0.03; // exploring, the whole graph fits; what a cell shows follows the zoom
