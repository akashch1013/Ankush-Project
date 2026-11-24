#!/usr/bin/env python3
"""mathcheck.py: exact check of every equation on a ChandRush page.

  python3 pipeline/mathcheck.py PAGE.html [--json] [-v|--verbose]

Default output: every FAIL and UNTAGGED line plus one summary line; -v also lists every PASS.

The page builder tags every printed mathematical statement with data-math, written in plain notation:
  <span data-math="4 × (−3) = −12">4 × (−3) = −12</span>
  <div data-math="3 + 4 − 6 = 7 − 6 = 1">...</div>                chains: every side must be equal
  <span data-math="(−4) × (−1) > 0">...</span>                    < > ≤ ≥ ≠ = are supported
  <span data-math="2^3 = 8">2³ = 8</span>                         powers: ^ or ² ³ (superscripts)
  <span data-math="3/4 + 1/4 = 1">...</span>                      fractions are exact (no float error)
  <span data-math="25% × 80 = 20">...</span>                      % means /100
  <span data-math="√49 = 7">  <span data-math="∛27 = 3">  √(16 + 9) = 5   roots are exact for perfect powers
  <span data-math="√2 ≈ 1.41">                                    ≈ holds when the right side is the left side
                                                                   rounded to the decimals it shows
  <span data-math="4 − 6 = 2" data-math-expect="false">           a deliberately wrong statement (a "mistake" shown
                                                                   to students); it must evaluate FALSE
Variables: data-math-vars="x=3, y=−2" then data-math="2x + y = 4" (implicit products like 2x and 3(4) work).

Exit 0 only if every tagged statement holds. It also lists UNTAGGED text that looks like an equation
(digits around '=') so the math checker can tag or verify it. Unicode minus, ×, ÷, · and thin spaces are understood.
"""
import ast
import json
import operator
import os
import re
import sys
from fractions import Fraction
from html.parser import HTMLParser

SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
REL = r"(<=|>=|!=|≤|≥|≠|≈|=|<|>)"
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
       ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}
CMP = {"=": operator.eq, "<": operator.lt, ">": operator.gt, "<=": operator.le, ">=": operator.ge, "!=": operator.ne,
       "≤": operator.le, "≥": operator.ge, "≠": operator.ne}


def normalise(s):
    s = s.replace("−", "-").replace("–", "-").replace("×", "*").replace("·", "*").replace("÷", "/")
    s = s.replace(" ", " ").replace(" ", " ").replace(" ", " ").replace("^", "**")
    for sign, fn in (("∛", "cbrt"), ("∜", "qrt"), ("√", "sqrt")):          # √49, √(16+9), 2√9
        s = re.sub(sign + r"\s*(\d+(?:\.\d+)?)", fn + r"(\1)", s).replace(sign, fn)
    s = re.sub(r"([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)", lambda m: "**(" + m.group(1).translate(SUP) + ")", s)
    s = re.sub(r"(\d),(\d{3})(?!\d)", r"\1\2", s)          # 4,158 -> 4158
    s = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"(\1/100)", s)
    s = re.sub(r"(\d|\))\s*(?=[a-zA-Z(])", r"\1*", s)        # 2x, 3(4), (2)(3)
    s = re.sub(r"\b(sqrt|cbrt|qrt)\*\(", r"\1(", s)
    return s


ROOTS = {"sqrt": 2, "cbrt": 3, "qrt": 4}


def _iroot(n, k):
    r = round(n ** (1.0 / k)) if n else 0
    for c in (r - 1, r, r + 1):
        if c >= 0 and c ** k == n:
            return c
    return None


def root(x, k):
    """Exact root of a perfect power; otherwise a 40-digit approximation (so '=' fails, '≈' can pass)."""
    if x < 0:
        if k % 2 == 0:
            raise ValueError("square root of a negative number")
        return -root(-x, k)
    n, d = _iroot(x.numerator, k), _iroot(x.denominator, k)
    if n is not None and d is not None:
        return Fraction(n, d)
    from decimal import Decimal, getcontext
    getcontext().prec = 40
    v = (Decimal(x.numerator) / Decimal(x.denominator)) ** (Decimal(1) / Decimal(k))
    return Fraction(v)


def value(node, env):
    if isinstance(node, ast.Expression):
        return value(node.body, env)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return Fraction(str(node.value))
    if isinstance(node, ast.Name):
        if node.id not in env:
            raise ValueError(f"unknown variable {node.id} (declare it in data-math-vars)")
        return env[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        l, r = value(node.left, env), value(node.right, env)
        if isinstance(node.op, ast.Pow):
            if r.denominator != 1 or abs(r) > 64:
                raise ValueError("only small whole-number powers are supported")
            return l ** int(r)
        return OPS[type(node.op)](l, r)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ROOTS and len(node.args) == 1:
        return root(value(node.args[0], env), ROOTS[node.func.id])
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](value(node.operand, env))
    raise ValueError(f"unsupported syntax: {ast.dump(node)[:60]}")


def evaluate(expr, varstr=""):
    env = {}
    for part in filter(None, (x.strip() for x in normalise(varstr).split(","))):
        k, v = part.split("=")
        env[k.strip()] = value(ast.parse(v.strip(), mode="eval"), {})
    parts = re.split(REL, normalise(expr).replace("==", "="))
    if len(parts) < 3:
        raise ValueError("no relation (=, <, >, ...) found")
    sides = [value(ast.parse(p.strip(), mode="eval"), env) for p in parts[0::2]]
    rels = parts[1::2]
    texts = [p.strip() for p in parts[0::2]]

    def holds(r, a, b, btext):
        if r != "≈":
            return CMP[r](a, b)
        m = re.fullmatch(r"-?\d+(?:\.(\d+))?", btext)         # right side must be a rounded decimal
        dec = len(m.group(1) or "") if m else 6
        return abs(a - b) <= Fraction(1, 2 * 10 ** dec)
    return all(holds(r, a, b, t) for r, a, b, t in zip(rels, sides, sides[1:], texts[1:])), sides


class Page(HTMLParser):
    VOID = {"br", "img", "hr", "meta", "link", "input", "source", "wbr", "area", "col", "embed", "param", "track"}

    def __init__(self):
        super().__init__()
        self.tags, self.stack, self.loose = [], [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("style", "script"):
            self.stack.append(("skip", tag))
            return
        if "data-math" in a:
            self.tags.append({"expr": a["data-math"], "vars": a.get("data-math-vars", ""),
                              "expect": a.get("data-math-expect", "true").lower() != "false",
                              "where": a.get("id") or a.get("class") or tag, "line": self.getpos()[0]})
        if tag not in self.VOID:
            self.stack.append(("math" if "data-math" in a or "data-math-ignore" in a else "", tag))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][1] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if any(k in ("skip", "math") for k, _ in self.stack):
            return
        for m in re.finditer(r"[^.;:!?]*[\d)]\s*[=<>≤≥≠]\s*[−\-(\d][^.;:!?]*", data):
            self.loose.append({"text": m.group(0).strip(), "line": self.getpos()[0]})


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    pg = Page()
    pg.feed(open(sys.argv[1], encoding="utf-8").read())
    results, bad = [], 0
    for t in pg.tags:
        try:
            ok, sides = evaluate(t["expr"], t["vars"])
            passed = ok == t["expect"]
            msg = "" if passed else ("evaluates FALSE" if t["expect"] else "marked as a deliberate mistake but is TRUE")
            vals = " | ".join(str(s) for s in sides)
        except Exception as e:  # noqa: BLE001
            passed, msg, vals = False, f"cannot evaluate: {e}", ""
        bad += not passed
        results.append({**t, "pass": passed, "msg": msg, "values": vals})
    if "--json" in sys.argv:
        print(json.dumps({"tagged": results, "untagged": pg.loose, "failures": bad}, ensure_ascii=False, indent=1))
    else:
        verbose = "-v" in sys.argv or "--verbose" in sys.argv
        for r in results:
            if verbose or not r["pass"]:
                print(f"{'PASS' if r['pass'] else 'FAIL'}  line {r['line']:>4}  {r['expr']}"
                      + (f"   [{r['values']}]" if r["values"] else "") + (f"   <- {r['msg']}" if r["msg"] else ""))
        for l in pg.loose:
            print(f"UNTAGGED line {l['line']:>4}  {l['text'][:110]}")
        if verbose:
            print(f"\n{len(results)} tagged, {bad} failing, {len(pg.loose)} untagged equation-like text(s)")
        else:
            path = os.path.abspath(sys.argv[1])
            name = os.path.basename(os.path.dirname(path)) if os.path.basename(path) == "index.html" else os.path.basename(path)
            print(f"mathcheck {name}: {len(results) - bad} PASS, {bad} FAIL, {len(pg.loose)} UNTAGGED"
                  f" ({len(results)} tagged)")
    sys.exit(1 if bad or not results and pg.loose else 0)


if __name__ == "__main__":
    main()
