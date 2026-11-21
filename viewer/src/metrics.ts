// The few numbers the layout needs, from the token file, and the view's framing.
import tokens from "../../src/conky/tokens.json";

export const SPACE = tokens.space;
export const GRID_COLUMNS = 10; // about this many notes in a row of a crowded space
export const SHEET = 720; // CSS pixels a rendered picture is at most wide: the README's width
export const MAX_ZOOM = 1.25; // a small graph is not blown up past this
export const MIN_ZOOM = 0.6; // below this the labels stop being legible
