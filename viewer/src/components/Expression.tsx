/** An expression shown as what it is: a small function of the names it reads, its body in
 * braces. The body is only split into tokens for display (names, operators, literals), never
 * parsed; it wraps at spaces, never inside a token. */
const TOKEN = /("[^"]*"|'[^']*'|\d+(?:\.\d+)?|[A-Za-z_][A-Za-z0-9_]*|\s+|.)/g;

function kind(token: string, next: string): string {
  if (/^\s+$/.test(token)) return "";
  if (/^["'\d]/.test(token)) return "expr-literal";
  if (/^[A-Za-z_]/.test(token)) return next === "(" ? "expr-call" : "expr-name";
  return "expr-op";
}

export function Expression({ reads, body }: { reads: string[]; body: string }) {
  const tokens = body.match(TOKEN) ?? [];
  return (
    <code className="expr">
      <span className="expr-mark">ƒ</span>
      <span className="expr-op">(</span>
      {reads.map((name, k) => (
        <span key={name}>
          {k > 0 && <span className="expr-op">, </span>}
          <span className="expr-name">{name}</span>
        </span>
      ))}
      <span className="expr-op">) {"{"} </span>
      {tokens.map((tok, k) => (
        <span key={k} className={kind(tok, tokens[k + 1] ?? "")}>
          {tok}
        </span>
      ))}
      <span className="expr-op"> {"}"}</span>
    </code>
  );
}
