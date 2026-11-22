#!/usr/bin/env python3
"""textcheck.py: keep the manuscript's words exact.

  dump DOCX OUT.txt            manuscript/register .docx -> plain text with #-headings and [Style] tags (grep it;
                               never paste a whole manuscript into a prompt)
  pages DOCX OUTDIR            split a paginated manuscript (page ids like CH02-PAGE001) into OUTDIR/P001.txt ...
                               plus _preamble.txt and _common.txt (long lines repeated > 4 times, written once and
                               dropped from the page files). Agents read only their page's file.
  survey SRC_DIR [--kind K]    one row per page from the pages split: panels, story text, teaching load, ~printable
                               words and a kind (story | story+math | math-heavy | text-heavy | teaching). Use it to
                               pick pages for "a text-heavy sample", "a story page", etc. --kind filters and ranks.
  plan PAGES.json              every printable string in the page plan (bubbles, captions, teaching text) must
                               appear verbatim in the plan's manuscript (whitespace, quotes and dashes normalised)
  page PAGE_DIR PAGES.json     every printable string the plan gives this page must appear in its index.html,
                               and no bubble/caption in the HTML may be missing from the plan

Exit 1 on any mismatch. Strings shorter than 3 characters are skipped.
"""
import html as htmllib
import json
import os
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
TASKS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
SUPS = str.maketrans("0123456789-−+()n", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁻⁺⁽⁾ⁿ")


def _simple(s):
    return re.fullmatch(r"[\w.,]+|\(.*\)", s.strip()) is not None


def fracstr(num, den):
    num, den = num.strip(), den.strip()
    return (num if _simple(num) else f"({num})") + "/" + (den if _simple(den) else f"({den})")


def _omml(el):
    """Word equation (OMML) -> plain text: 2², 3/4, √49, ∛27, (…)."""
    tag = el.tag
    kid = lambda name: el.find(M + name)
    txt = lambda node: "".join(_omml(c) for c in node) if node is not None else ""
    if tag == M + "t":
        return el.text or ""
    if tag in (M + "rPr", M + "fPr", M + "radPr", M + "sSupPr", M + "sSubPr", M + "dPr", M + "ctrlPr", W + "rPr"):
        return ""
    if tag == M + "sSup":
        base, sup = txt(kid("e")), txt(kid("sup"))
        return base + (sup.translate(SUPS) if all(ch in "0123456789-−+()n" for ch in sup) else f"^({sup})")
    if tag == M + "sSub":
        return txt(kid("e")) + "_" + txt(kid("sub"))
    if tag == M + "f":
        return fracstr(txt(kid("num")), txt(kid("den")))
    if tag == M + "rad":
        deg, body = txt(kid("deg")).strip(), txt(kid("e")).strip()
        sign = {"": "√", "2": "√", "3": "∛", "4": "∜"}.get(deg, deg.translate(SUPS) + "√")
        return sign + (body if _simple(body) else f"({body})")
    if tag == M + "d":
        pr = el.find(M + "dPr")
        beg = pr.find(M + "begChr") if pr is not None else None
        end = pr.find(M + "endChr") if pr is not None else None
        b = beg.get(M + "val") if beg is not None else "("
        e = end.get(M + "val") if end is not None else ")"
        return b + ", ".join(txt(x) for x in el.findall(M + "e")) + e
    return txt(el)


def _ptext(el):
    out = []

    def walk(n):
        for c in n:
            if c.tag in (M + "oMath", M + "oMathPara"):
                out.append(_omml(c))
            elif c.tag == W + "t":
                out.append(c.text or "")
            elif c.tag == W + "tab":
                out.append("\t")
            elif c.tag in (W + "br", W + "cr"):
                out.append("\n")
            else:
                walk(c)
    walk(el)
    return "".join(out).strip()


def docx_lines(path):
    root = ET.fromstring(zipfile.ZipFile(path).read("word/document.xml"))
    lines = []

    def walk(node):
        for c in node:
            if c.tag == W + "sdt":
                content = c.find(W + "sdtContent")
                if content is not None:
                    walk(content)
            elif c.tag == W + "p":
                st = c.find(f"{W}pPr/{W}pStyle")
                style = st.get(W + "val") if st is not None else ""
                t = _ptext(c)
                if not t:
                    continue
                m = re.match(r"Heading(\d)", style)
                lines.append(("#" * int(m.group(1)) + " " if m else (f"[{style}] " if style and style != "Normal" else "")) + t)
            elif c.tag == W + "tbl":
                for tr in c.findall(W + "tr"):
                    lines.append("| " + " | ".join(" ".join(_ptext(p) for p in tc.iter(W + "p")).replace("\n", " ")
                                                   for tc in tr.findall(W + "tc")) + " |")
    walk(root.find(W + "body"))
    return lines


def norm(s):
    s = htmllib.unescape(s)
    s = s.translate(str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺⁽⁾ⁿ", "0123456789-+()n"))
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("−", "-").replace("–", "-").replace("—", "-").replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


def strings(page):
    """All printable strings of one page entry in pages.json."""
    out = []
    for pn in page.get("panels", []):
        out += [("bubble", b["text"]) for b in pn.get("bubbles", [])]
        out += [("caption", c) for c in pn.get("captions", [])]
    for t in page.get("teaching", []):
        out += [("teaching", x) for x in t.get("text", [])]
        out += [("question", x) for x in t.get("questions", [])]
        if t.get("heading"):
            out.append(("heading", t["heading"]))
    out += [("aside", a["text"]) for a in page.get("asides", [])]
    if page.get("title"):
        out.append(("title", page["title"]))
    return [(k, s) for k, s in out if len(norm(s)) >= 3]


def load_plan(path):
    plan = json.load(open(path, encoding="utf-8"))
    src = plan["sources"]["manuscript"]
    src = src if os.path.isabs(src) else os.path.join(TASKS, src)
    return plan, src


def cmd_plan(path):
    plan, src = load_plan(path)
    text = norm("\n".join(docx_lines(src)))
    bad = 0
    for pg in plan["pages"]:
        for kind, s in strings(pg):
            if norm(s) not in text:
                bad += 1
                print(f"NOT IN MANUSCRIPT  {pg['page']} {kind}: {s[:120]}")
    print(f"{bad} string(s) not found verbatim" if bad else "plan text OK: every string is verbatim from the manuscript")
    sys.exit(1 if bad else 0)


def visible_text(h):
    h = re.sub(r"<(style|script)\b.*?</\1>", " ", h, flags=re.S)
    h = re.sub(r"<br\s*/?>", " ", h)
    # stacked fractions read as a/b, superscripts join their base (2<sup>2</sup> -> 22, like 2² -> 22)
    h = re.sub(r'<span class="frac[^"]*"[^>]*>\s*<span[^>]*>(.*?)</span>\s*<span[^>]*>(.*?)</span>\s*</span>',
               lambda m: fracstr(re.sub(r"<[^>]+>", "", m.group(1)), re.sub(r"<[^>]+>", "", m.group(2))), h, flags=re.S)
    h = re.sub(r"</?(sup|sub)\b[^>]*>", "", h)
    # inline colour/emphasis spans (.mt/.mr, b, i, em, strong) don't break words: <span class="mt">7</span>, -> 7,
    h = re.sub(r'<span class="(?:mt|mr)"[^>]*>([^<]*)</span>', r"\1", h)
    h = re.sub(r"</?(b|i|em|strong)\b[^>]*>", "", h)
    return norm(re.sub(r"<[^>]+>", " ", h))


def cmd_page(page_dir, path):
    plan, _ = load_plan(path)
    pid = os.path.basename(os.path.abspath(page_dir))
    pg = next((p for p in plan["pages"] if p["page"] == pid), None)
    if not pg:
        sys.exit(f"{pid} not in {path}")
    h = open(os.path.join(page_dir, "index.html"), encoding="utf-8").read()
    vis = visible_text(h)
    bad = 0
    for kind, s in strings(pg):
        if norm(s) not in vis:
            bad += 1
            print(f"MISSING/CHANGED  {kind}: {s[:120]}")
    planned = {norm(s) for _, s in strings(pg)}
    for m in re.finditer(r'class="(?:bubble|cap)[^"]*"[^>]*>(.*?)</div>', h, flags=re.S):
        t = norm(re.sub(r"<[^>]+>", " ", m.group(1)))
        if t and not any(t in p or p in t for p in planned):
            bad += 1
            print(f"NOT IN PLAN  {t[:120]}")
    print(f"{bad} problem(s)" if bad else "page text OK")
    sys.exit(1 if bad else 0)


def cmd_pages(docx, outdir):
    from collections import Counter
    lines = docx_lines(docx)
    counts = Counter(lines)
    # only long repeated boilerplate moves to _common.txt; short repeated lines are headings and stay
    common = [l for l, n in counts.items() if n > 4 and len(l) > 120]
    common_set = set(common)
    os.makedirs(outdir, exist_ok=True)
    pages, cur, order = {}, "_preamble", []
    for l in lines:
        # page boundaries only at explicit page-id lines, never at cross-references
        m = re.search(r"PAGE ID:\s*CH\d{2}-PAGE(\d{3})", l) or re.match(r"\[GraphicPageId\].*PAGE\s*(\d{3})", l)
        if m:
            cur = "P" + m.group(1)
        if cur not in pages:
            pages[cur] = []
            order.append(cur)
        if l not in common_set or cur == "_preamble":
            pages[cur].append(l)
    for k in order:
        with open(os.path.join(outdir, k + ".txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(pages[k]) + "\n")
    with open(os.path.join(outdir, "_common.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(f"[x{counts[l]}] {l}" for l in common) + "\n")
    sizes = [len("\n".join(pages[k])) for k in order if k != "_preamble"]
    print(f"{outdir}: {len(sizes)} pages (avg {sum(sizes) // max(1, len(sizes))} chars), "
          f"{len(common)} repeated lines in _common.txt")


NONPRINT = re.compile(r"Meta|Production|Label|Context|Boundary|Section|Identifier|Panelization|Pagination|Note|End\b"
                      r"|Source|Instruction|Heading|PGMeta|PGLabel|MMeta|MScene|MLabel|MBeat|GraphicPageId")
PRINT_TAGS = {"CaptionCopy", "DialogueCopy", "SmallCaption", "MathExample", "AnswerLead", "Equation", "MathSection",
              "MathSubsection", "Caption", "Question", "WorkedStep", "TeacherBridge", "SurfaceCopy", "PrintField"}


def survey_page(text):
    lines = text.splitlines()
    tag = lambda l: (re.match(r"\[(\w+)\]", l) or [None, ""])[1]
    count = lambda *names: sum(1 for l in lines if tag(l) in names)
    panels = len(set(re.findall(r"PANEL CH\d{2}-PAGE\d{3}-PANEL\d{2}", text))) or text.count("END PANEL")
    words, inside, table_eqs = 0, False, 0
    for l in lines:
        t = tag(l)
        if l.startswith("|"):                                   # table-form manuscripts (CH03)
            for seg in re.findall(r"ORIGINAL PANEL CONTENT(.*?)(?:END PANEL|$)", l):
                seg = re.sub(r"DO NOT PRINT.*?reader-facing\.|Production note.*?priority\.", " ", seg)
                words += len(seg.split())
                table_eqs += len(re.findall(r"\d\s*=\s*[−-]?\d", seg))
            continue
        if "ORIGINAL PANEL CONTENT" in l:
            inside = True
            continue
        if re.search(r"END PANEL|END NON-PRINTING|NON-PRINTING", l):
            inside = "END PANEL" not in l and inside and "NON-PRINTING" not in l
            continue
        if t in PRINT_TAGS or (not t and inside) or (inside and t and not NONPRINT.search(t)):
            words += len(re.sub(r"^\[\w+\]\s*", "", l).split())
    story = count("DialogueCopy", "CaptionCopy") + text.count("SPEECH BUBBLE TEXT") + text.count("CAPTION TEXT")
    eqs = count("Equation", "WorkedStep") + table_eqs
    examples = count("MathExample", "Question", "AnswerLead") + len(re.findall(r"Let’s work it through|Now you try", text))
    if not (eqs or examples):
        kind = "story"
    elif eqs >= 6:
        kind = "math-heavy"
    elif words >= 240 and eqs <= 4:
        kind = "text-heavy"
    elif story:
        kind = "story+math"
    else:
        kind = "teaching"
    return dict(panels=panels, story=story, examples=examples, equations=eqs, words=words, kind=kind)


def cmd_survey(src, kind=None):
    rows = []
    for f in sorted(os.listdir(src)):
        if re.fullmatch(r"P\d{3}\.txt", f):
            r = survey_page(open(os.path.join(src, f), encoding="utf-8").read())
            r["page"] = f[:4]
            rows.append(r)
    if kind:
        rows = [r for r in rows if r["kind"] == kind]
        key = {"text-heavy": "words", "math-heavy": "equations", "story": "story"}.get(kind, "words")
        rows.sort(key=lambda r: -r[key])
    print("page  kind        panels story examples equations ~words")
    for r in rows:
        print(f"{r['page']}  {r['kind']:<11} {r['panels']:>6} {r['story']:>5} {r['examples']:>8} {r['equations']:>9} {r['words']:>6}")
    from collections import Counter
    print("totals:", dict(Counter(r["kind"] for r in rows)))


def main():
    a = sys.argv[1:]
    if a[:1] == ["dump"] and len(a) == 3:
        with open(a[2], "w", encoding="utf-8") as fh:
            fh.write("\n".join(docx_lines(a[1])) + "\n")
        print(f"{a[2]}: {sum(1 for _ in open(a[2], encoding='utf-8'))} lines")
    elif a[:1] == ["pages"] and len(a) == 3:
        cmd_pages(a[1], a[2])
    elif a[:1] == ["survey"] and len(a) in (2, 4):
        cmd_survey(a[1], a[3] if len(a) == 4 and a[2] == "--kind" else None)
    elif a[:1] == ["plan"] and len(a) == 2:
        cmd_plan(a[1])
    elif a[:1] == ["page"] and len(a) == 3:
        cmd_page(a[1], a[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
