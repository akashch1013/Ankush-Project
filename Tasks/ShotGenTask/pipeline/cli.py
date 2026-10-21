"""Command line for the ChandRush Approach1 pipeline.

Run from the Approach1 folder:  python -m pipeline <command> [options]
Run `python -m pipeline --help` or `python -m pipeline <command> --help` for details.
"""
from __future__ import annotations

import argparse
import json
import sys

from .paths import Batch, default_batch_id, rel


def parse_pages(spec: str | None, batch: Batch) -> list[int]:
    if not spec:
        return list(batch.pages)
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            pages.extend(range(int(a), int(b) + 1))
        elif part:
            pages.append(int(part))
    return pages


def get_batch(args) -> Batch:
    b = Batch(args.batch or default_batch_id())
    b.ensure_dirs()
    return b


# ---------------------------------------------------------------- extract

def cmd_extract(args):
    from .manifest import build_contract, check_contract, verify_manuscript
    batch = get_batch(args)
    v = verify_manuscript()
    print(f"Manuscript {v['file']}: {'MATCHES' if v['match'] else 'DOES NOT MATCH'} manifest checksum")
    if not v["match"]:
        print(f"  expected {v['expected']}\n  actual   {v['actual']}")
    total_panels = total_blocks = 0
    for page in parse_pages(args.pages, batch):
        contract = build_contract(page)
        problems = check_contract(contract)
        path = batch.contract_path(page)
        path.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        n_blocks = sum(len(p["printable"]) for p in contract["panels"])
        missing = [r["literal"] for p in contract["panels"] for r in p["resolved_references"] if r["status"] == "missing"]
        total_panels += len(contract["panels"])
        total_blocks += n_blocks
        print(f"  {contract['page_id']}: {len(contract['panels'])} panels, {n_blocks} printable blocks"
              f"{'; MISSING refs: ' + ', '.join(missing) if missing else ''}"
              f"{'; PROBLEMS: ' + '; '.join(problems) if problems else ''} -> {rel(path)}")
    print(f"Done: {total_panels} panels, {total_blocks} printable blocks.")


# ---------------------------------------------------------------- build

def cmd_build(args):
    from .layout import model_page
    from .render import build_pdf, contact_sheet, pdf_to_pngs, write_build_record
    batch = get_batch(args)
    pages = parse_pages(args.pages, batch)
    mode = args.mode
    proof = mode in ("standin", "placeholder")
    models = [model_page(batch, p, mode) for p in pages]
    failed = False
    for m in models:
        kinds = {}
        for pm in m.panels:
            kinds[pm.art_kind] = kinds.get(pm.art_kind, 0) + 1
        print(f"{m.page_id}: art {kinds}")
        for e in m.errors:
            print(f"  ERROR   {e}")
            failed = True
        for w in m.warnings:
            print(f"  warning {w}")
    if failed and not args.force:
        raise SystemExit("Build stopped: fix the errors above (layout/text problems are never auto-shrunk).")

    suffix = {"placeholder": "-LAYOUT-PROOF", "standin": "-STANDIN-PROOF", "latest": "-LATEST", "final": ""}[mode]
    pdf_dir = batch.output / "proofs" if proof else batch.pdf_dir
    png_dir = batch.output / "proofs" if proof else batch.png_dir
    page_pdfs, pngs, records = [], [], []
    for m in models:
        out = pdf_dir / f"{m.page_id}{suffix}.pdf"
        records += build_pdf([m], batch, out, show_zones=args.zones)
        page_pdfs.append(out)
        pngs += pdf_to_pngs(out, png_dir, dpi=args.dpi)
    name = f"CH01-P{pages[0]:03d}-P{pages[-1]:03d}"
    batch_pdf = (batch.output / "proofs" if proof else batch.output) / f"{name}{suffix or '-REVIEW'}.pdf"
    build_pdf(models, batch, batch_pdf, show_zones=args.zones)
    sheet = contact_sheet(pngs, (batch.output / "proofs" if proof else batch.output) / f"{name}{suffix}-CONTACT-SHEET.png")
    rec = write_build_record(batch, records, f"{name}{suffix}")
    print("Wrote:")
    for p in page_pdfs + [batch_pdf, sheet, rec]:
        print(f"  {rel(p)}")
    print(f"  {len(pngs)} PNG page images at {args.dpi} dpi in {rel(png_dir)}")
    if any(pm.art_kind != "approved" for m in models for pm in m.panels):
        print("NOTE: some panels use stand-in/placeholder/unapproved art, so these files are proofs, not final pages.")


# ---------------------------------------------------------------- prompts & refs

def cmd_prompts(args):
    from .prompts import cmd_draft, lint, load_contracts, load_jobs
    batch = get_batch(args)
    if args.action == "draft":
        cmd_draft(batch, parse_pages(args.pages, batch), args.force)
        return
    jobs = load_jobs(batch)
    contracts = load_contracts(batch)
    if args.action == "show":
        job = next((j for j in jobs if j.panel_id == args.panel), None)
        if not job:
            raise SystemExit(f"No prompt for {args.panel}")
        print(job.prompt)
        return
    bad = 0
    queues = [j.queue for j in jobs]
    if sorted(queues) != list(range(1, len(jobs) + 1)):
        print(f"QUEUE PROBLEM: queue numbers should be 1..{len(jobs)} without gaps; got {sorted(queues)}")
        bad += 1
    for j in jobs:
        problems = lint(batch, j, contracts) if args.action == "lint" else []
        mark = "OK  " if not problems else "FAIL"
        print(f"{mark} #{j.queue:>2} {j.panel_id}  {j.card.get('title', '')}  "
              f"{j.card.get('size')}  {len(j.card.get('attachments', []))} images"
              f"{' + anchor ' + ','.join(j.card.get('anchors')) if j.card.get('anchors') else ''}")
        for p in problems:
            print(f"        - {p}")
        bad += bool(problems)
    expected = sum(len(c["panels"]) for c in contracts.values())
    if len(jobs) != expected:
        print(f"COVERAGE PROBLEM: {len(jobs)} prompt files for {expected} panels")
        bad += 1
    if args.action == "lint":
        print(f"{len(jobs) - bad if bad <= len(jobs) else 0}/{len(jobs)} prompt files pass." if bad else
              f"All {len(jobs)} prompt files pass.")
        if bad:
            raise SystemExit(1)


def cmd_refs(args):
    from .prompts import build_refs, load_jobs, write_queue_md
    batch = get_batch(args)
    n = 0
    for j in load_jobs(batch):
        made = build_refs(batch, j)
        n += len(made)
        print(f"{j.panel_id}: {len(made)} images -> {rel(batch.refs_dir / j.panel_id)}")
    print(f"{n} reference links ready (hard links, no extra disk space).")
    print(f"Queue: {rel(write_queue_md(batch))}")


def cmd_new_batch(args):
    from .paths import BATCHES
    pages = []
    for part in args.pages.split(","):
        a, _, b = part.partition("-")
        pages.extend(range(int(a), int(b or a) + 1))
    batch_id = args.id or f"P{pages[0]:03d}-P{pages[-1]:03d}"
    root = BATCHES / batch_id
    if root.exists():
        raise SystemExit(f"{rel(root)} already exists.")
    root.mkdir(parents=True)
    (root / "batch.json").write_text(json.dumps({
        "batch_id": batch_id, "pages": pages, "manuscript_revision": "V07",
        "look": "Opening V04 PDF design (design/tokens.json)",
        "decisions": {"speaker_prefix": "Balloons omit the exact 'SPEAKER: ' prefix; the tail identifies the speaker."},
    }, indent=2) + "\n", encoding="utf-8")
    Batch(batch_id).ensure_dirs()
    print(f"Created {rel(root)} for pages {pages}. Next: python -m pipeline --batch {batch_id} extract")


# ---------------------------------------------------------------- workflow commands

def _uv(text):
    try:
        u, v = (float(x) for x in text.split(","))
    except ValueError:
        raise SystemExit("Use U,V with values between 0 and 1, e.g. 0.62,0.41")
    if not (0 <= u <= 1 and 0 <= v <= 1):
        raise SystemExit("U and V must be between 0 and 1 (read them off the review grid).")
    return u, v


def cmd_next(args):
    from .workflow import cmd_next as run
    mode = "json" if args.json else "codex" if args.codex else "human"
    run(get_batch(args), args.panel, not args.no_clipboard, not args.no_open, mode)


def cmd_ingest(args):
    from .workflow import cmd_ingest as run
    run(get_batch(args), args.panel, args.file, args.downloads, args.route, args.note, args.from_codex, args.all_new)


def cmd_review(args):
    from .workflow import cmd_review as run
    run(get_batch(args), args.panel, args.version)


def cmd_approve(args):
    from .workflow import cmd_approve as run
    run(get_batch(args), args.panel, args.version, args.status, args.exceptions or [], args.note)


def cmd_reject(args):
    from .workflow import cmd_reject as run
    run(get_batch(args), args.panel, args.version, args.reason)


def cmd_tail(args):
    from .workflow import cmd_tail as run
    run(get_batch(args), args.panel, _uv(args.at), args.block)


def cmd_frame(args):
    from .workflow import cmd_frame as run
    run(get_batch(args), args.panel, _uv(args.focus) if args.focus else None, args.zoom)


def cmd_generate(args):
    from .generate import cmd_generate as run
    from .workflow import next_job
    from . import state as st
    batch = get_batch(args)
    panel = args.panel
    if not panel:
        job = next_job(batch, st.load(batch))
        if not job:
            raise SystemExit("No pending panels.")
        panel = job.panel_id
    run(batch, panel, args.quality, args.run)


def cmd_status(args):
    from .status import cmd_status as run
    run(get_batch(args))


def cmd_audit(args):
    from .audit import run_audit
    batch = get_batch(args)
    results = run_audit(batch, parse_pages(args.pages, batch), args.proof)
    for r in results:
        res = [c["result"] for c in r["checks"]]
        print(f"{r['page_id']}: {r['status']}  (BLOCK {res.count('BLOCK')}, REVIEW {res.count('REVIEW')}, "
              f"PROOF {res.count('PROOF')}, NOTE {res.count('NOTE')})")
        for c in r["checks"]:
            if c["result"] == "BLOCK":
                print(f"    BLOCK {c['check']}: {c['detail']}")
    suffix = {"standin": "-STANDIN-PROOF", "placeholder": "-LAYOUT-PROOF", "latest": "-LATEST"}.get(args.proof, "")
    print(f"Report: {rel(batch.output / f'AUDIT{suffix}.md')}")
    if any(r["status"] in ("FAIL", "MISSING") for r in results):
        raise SystemExit(1)


def cmd_compare(args):
    from .compare import cmd_compare as run
    run(get_batch(args), args.page, args.sample, args.which)


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m pipeline", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--batch", help="Batch folder name under Approach1/batch (default: the only/latest one)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("extract", help="Manifest -> exact page contracts (pages/*.contract.json)")
    p.add_argument("--pages", help="e.g. 9-13 (default: batch pages)")
    p.set_defaults(func=cmd_extract)

    p = sub.add_parser("build", help="Assemble pages -> PDF + 300-dpi PNG + contact sheet")
    p.add_argument("--pages")
    p.add_argument("--mode", default="final", choices=["final", "latest", "standin", "placeholder"],
                   help="final: approved art (stand-ins where missing); latest: newest art even if unapproved; "
                        "standin: location stand-ins only; placeholder: grey layout proof")
    p.add_argument("--zones", action="store_true", help="Outline every text box (layout checking)")
    p.add_argument("--dpi", type=int, default=300)
    p.add_argument("--force", action="store_true", help="Write files even if the layout has errors")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("proof", help="Shortcut: grey layout proof with text zones outlined")
    p.add_argument("--pages")
    p.add_argument("--dpi", type=int, default=150)
    p.set_defaults(func=lambda a: cmd_build(argparse.Namespace(**vars(a), mode="placeholder", zones=True, force=False)))

    p = sub.add_parser("new-batch", help="Create batch/<id>/ for the next pages, e.g. --pages 14-18")
    p.add_argument("--pages", required=True)
    p.add_argument("--id", help="folder name (default P014-P018 style)")
    p.set_defaults(func=cmd_new_batch)

    p = sub.add_parser("prompts", help="lint | list | show | draft the panel prompt files")
    p.add_argument("action", choices=["lint", "list", "show", "draft"])
    p.add_argument("--panel", help="for 'show'")
    p.add_argument("--pages", help="for 'draft' (default: batch pages)")
    p.add_argument("--force", action="store_true", help="for 'draft': overwrite existing prompt files")
    p.set_defaults(func=cmd_prompts)

    p = sub.add_parser("refs", help="Build prompts/refs/<panel>/ packs (numbered images in prompt order)")
    p.set_defaults(func=cmd_refs)

    p = sub.add_parser("next", help="Hand the next panel to an image tool (people: clipboard + folder; Codex: --codex)")
    p.add_argument("--panel", help="a specific panel instead of the next in the queue")
    p.add_argument("--codex", action="store_true",
                   help="print a complete task for Codex: images to view, the exact prompt, the checklist, next commands")
    p.add_argument("--json", action="store_true", help="the same task as JSON (for scripts/agents)")
    p.add_argument("--no-clipboard", action="store_true")
    p.add_argument("--no-open", action="store_true", help="do not open the refs folder in Explorer")
    p.set_defaults(func=cmd_next)

    p = sub.add_parser("ingest", help="File new images (inbox, Downloads or Codex's generated_images) as versioned panel art")
    p.add_argument("--panel", help="which panel the image belongs to (otherwise: ID in the file name, or the current panel)")
    p.add_argument("--file", help="ingest this file instead of the inbox")
    p.add_argument("--downloads", action="store_true", help="take the newest image in ~/Downloads since `next`")
    p.add_argument("--from-codex", action="store_true",
                   help="take the newest image Codex's image_gen saved in ~/.codex/generated_images since `next`")
    p.add_argument("--all-new", action="store_true", help="with --from-codex: file every new image as a version")
    p.add_argument("--route", default="webui", choices=["webui", "codex", "api", "manual", "test"])
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("review", help="Overlay crop, text zones, tail target and a 0..1 grid on a panel's art")
    p.add_argument("--panel", required=True)
    p.add_argument("--version", type=int)
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("approve", help="Accept a panel's art version for assembly")
    p.add_argument("--panel", required=True)
    p.add_argument("--version", type=int)
    p.add_argument("--status", default="PASS", choices=["PASS", "PASS_WITH_LOCATION_EXCEPTION", "REVIEW_LATER"])
    p.add_argument("--exceptions", nargs="*", help="e.g. LOC-EX-11")
    p.add_argument("--note", default="")
    p.set_defaults(func=cmd_approve)

    p = sub.add_parser("reject", help="Reject a version (one automatic retry allowed)")
    p.add_argument("--panel", required=True)
    p.add_argument("--version", type=int)
    p.add_argument("--reason", required=True)
    p.set_defaults(func=cmd_reject)

    p = sub.add_parser("tail", help="Aim a balloon tail at a point on the art (U,V from the review grid)")
    p.add_argument("--panel", required=True)
    p.add_argument("--at", required=True, help="U,V e.g. 0.58,0.40 = just beside the speaker's mouth")
    p.add_argument("--block", help="balloon block id if the panel has several")
    p.set_defaults(func=cmd_tail)

    p = sub.add_parser("frame", help="Adjust how the art is cropped into its frame")
    p.add_argument("--panel", required=True)
    p.add_argument("--focus", help="U,V point of the image to keep centred")
    p.add_argument("--zoom", type=float, help=">= 1.0")
    p.set_defaults(func=cmd_frame)

    p = sub.add_parser("generate", help="Optional API route via Codex's image CLI (dry run unless --run and OPENAI_API_KEY)")
    p.add_argument("--panel")
    p.add_argument("--quality", default="high", choices=["low", "medium", "high", "auto"])
    p.add_argument("--run", action="store_true", help="really call the API (needs OPENAI_API_KEY)")
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("status", help="Write output/STATUS.md and print it")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("audit", help="Audit the exported PDFs -> output/AUDIT.md")
    p.add_argument("--pages")
    p.add_argument("--proof", choices=["standin", "placeholder", "latest"], help="audit a proof build instead of final")
    p.set_defaults(func=cmd_audit)

    p = sub.add_parser("compare", help="Side-by-side with a page of the Opening V04 sample")
    p.add_argument("--page", type=int, required=True)
    p.add_argument("--sample", type=int, required=True, help="Opening V04 sample page number (1-12)")
    p.add_argument("--which", default="final", choices=["final", "standin", "placeholder", "latest"])
    p.set_defaults(func=cmd_compare)

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main(sys.argv[1:])
