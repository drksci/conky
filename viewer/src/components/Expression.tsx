import type { Expr } from "../graph";

/** An expression shown as what it is: a small function of the names it reads, its body in
 * braces, in the lines bench/expression.py laid it out in. The lines are printed as written
 * (white-space: pre), never reflowed; each is only split into tokens to colour names,
 * operators and literals. */
const TOKEN = /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|\d+(?:\.\d+)?|[A-Za-z_][A-Za-z0-9_]*|\s+|.)/g;

function kind(token: string, next: string): string {
  if (/^\s+$/.test(token)) return "";
  if (/^["'\d]/.test(token)) return "expr-literal";
  if (/^[A-Za-z_]/.test(token)) return next === "(" ? "expr-call" : "expr-name";
  return "expr-op";
}

function Line({ text }: { text: string }) {
  const tokens = text.match(TOKEN) ?? [];
  return (
    <>
      {tokens.map((tok, k) => (
        <span key={k} className={kind(tok, tokens[k + 1] ?? "")}>
          {tok}
        </span>
      ))}
    </>
  );
}

export function Expression({ expr }: { expr: Expr }) {
  const head = (
    <>
      <span className="expr-mark">ƒ</span>
      <span className="expr-op">(</span>
      {expr.reads.map((name, k) => (
        <span key={name}>
          {k > 0 && <span className="expr-op">, </span>}
          <span className="expr-name">{name}</span>
        </span>
      ))}
      <span className="expr-op">) {"{"}</span>
    </>
  );
  if (expr.lines.length <= 1)
    return (
      <code className="expr">
        {head} <Line text={expr.lines[0] ?? ""} /> <span className="expr-op">{"}"}</span>
      </code>
    );
  return (
    <code className="expr">
      {head}
      {expr.lines.map((line, k) => (
        <span key={k}>
          {"\n  "}
          <Line text={line} />
        </span>
      ))}
      {"\n"}
      <span className="expr-op">{"}"}</span>
    </code>
  );
}
