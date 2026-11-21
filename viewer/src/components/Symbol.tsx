import { icons } from "lucide-react";
import tokens from "../../../src/conky/tokens.json";

export type SymbolName = keyof typeof tokens.symbol;

const pascal = (name: string) => name.replace(/(^|-)([a-z0-9])/g, (_, __, c: string) => c.toUpperCase());

/** The one mark of a kind, from the symbol table in src/conky/tokens.json, drawn with a Lucide
 * line icon in the current ink. The table's plain-text mark stands in when the icon is missing. */
export function Symbol({ name }: { name: string }) {
  const entry = tokens.symbol[name as SymbolName];
  if (!entry) return null;
  const Icon = icons[pascal(entry.icon) as keyof typeof icons];
  if (!Icon) return <span className="symbol symbol-text">{entry.text}</span>;
  return <Icon className="symbol" aria-hidden absoluteStrokeWidth />;
}

export const wordOf = (name: string) => tokens.symbol[name as SymbolName]?.word ?? name;
