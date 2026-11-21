// The few numbers the layout needs, from the token file, and the view's framing.
import tokens from "../../src/conky/tokens.json";

export const SPACE = tokens.space;
// about this many members in a row of a region: notes shown to a space are wide, others small
export const GRID_COLUMNS: Record<string, number> = { shown: 2, hidden: 8, desk: 8, terms: 1 };
export const REGION_HEAD = tokens.space.wide + tokens.space.base; // room for a region's label
export const SHEET = 720; // CSS pixels a rendered picture is at most wide: the README's width
export const MAX_ZOOM = 1.25; // a small graph is not blown up past this
export const MIN_ZOOM = 0.6; // below this the labels stop being legible
