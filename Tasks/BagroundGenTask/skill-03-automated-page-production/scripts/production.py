#!/usr/bin/env python3
"""Objective production guards; never a substitute for visual review or InDesign."""
import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_checks(path):
    text = Path(path).read_text(encoding='utf-8-sig')
    # Only the actual ID-led headings, not mentions in prose/change records.
    matches = list(re.finditer(r'^([A-Z]\d{2})[ \t]+(.+)$', text, re.M))
    checks = []
    for m in matches:
        lines = [m.group(2)]
        tail = text[m.end():].splitlines()[1:]
        for line in tail:
            if not line.strip():
                break
            if not line[0].isspace():
                break
            lines.append(line.strip())
        checks.append({'id': m.group(1), 'requirement': ' '.join(lines)})
    ids = [x['id'] for x in checks]
    require(len(ids) == 40 and len(set(ids)) == 40,
            f'Expected 40 distinct current checklist IDs, found {len(ids)}. Inspect the checklist/parser; do not invent checks.')
    return checks


def image_report(a):
    from PIL import Image
    with Image.open(a.file) as im:
        original = im.size
    x, y, w, h = a.crop or (0, 0, *original)
    require(min(a.width_pt, a.height_pt, w, h) > 0, 'Positive dimensions required')
    require(x >= 0 and y >= 0 and x + w <= original[0] and y + h <= original[1], 'Crop outside native image')
    scale = (min if a.fit == 'contain' else max)(a.width_pt / w, a.height_pt / h)
    return {'file': a.file, 'sha256': digest(a.file), 'native_pixels': original,
            'crop_pixels': [x, y, w, h], 'frame_pt': [a.width_pt, a.height_pt],
            'placed_size_pt': [w * scale, h * scale], 'fit': a.fit,
            'effective_ppi': 72 / scale, 'meets_300_ppi': 72 / scale >= 299.5,
            'limitation': 'Native pixel calculation only; inspect crop, sharpness and any prior upscaling.'}


def pdf_report(file, pages=1, reported_bytes=None, render_dir=None):
    import fitz
    path = Path(file)
    size = path.stat().st_size
    if reported_bytes is not None:
        require(size == reported_bytes, f'Download size {size} differs from reported {reported_bytes}')
    with path.open('rb') as f:
        f.seek(max(0, size - 2048))
        require(b'%%EOF' in f.read(), 'PDF lacks final EOF marker')
    report = {'file': str(path), 'sha256': digest(path), 'bytes': size, 'pages': []}
    with fitz.open(path) as doc:
        require(not doc.is_repaired, 'PDF required repair; retry download or investigate export')
        require(not doc.needs_pass, 'PDF is encrypted')
        require(len(doc) == pages, f'Expected {pages} pages, got {len(doc)}')
        report['metadata'] = doc.metadata
        for i, pg in enumerate(doc):
            require(abs(pg.rect.width - 864) < .1 and abs(pg.rect.height - 648) < .1,
                    f'Wrong page dimensions on PDF page {i + 1}: {pg.rect}')
            require(pg.rotation == 0, 'Unexpected page rotation')
            boxes = {k: list(getattr(pg, k)) for k in ('mediabox', 'cropbox', 'trimbox', 'bleedbox')}
            for key, box in boxes.items():
                require(all(abs(x - y) < .1 for x, y in zip(box, boxes['mediabox'])), f'{key} differs from media box')
            rasters = []
            for image in pg.get_image_info(hashes=True):
                a, b, c, d, _, _ = image['transform']
                wp, hp = math.hypot(a, b), math.hypot(c, d)
                rasters.append({'pixels': [image['width'], image['height']],
                                'placed_size_pt': [wp, hp],
                                'effective_ppi': [72 * image['width'] / wp if wp else None,
                                                  72 * image['height'] / hp if hp else None],
                                'colorspace': image.get('cs-name'),
                                'pixel_digest': image['digest'].hex()})
            pix = pg.get_pixmap(matrix=fitz.Matrix(1, 1), alpha=False)
            if render_dir:
                rd = Path(render_dir)
                rd.mkdir(parents=True, exist_ok=True)
                pix.save(rd / f'{path.stem}-{i+1:03}.png')
            report['pages'].append({'index': i + 1, 'boxes': boxes, 'rasters': rasters,
                                    'render_sha256': hashlib.sha256(pix.samples).hexdigest()})
    report['limitation'] = 'Objective file checks only. Does not certify all colours, visual quality, source completeness, font availability or overset.'
    return report


def review_check(a):
    rp = Path(a.file)
    data = json.loads(rp.read_text())
    expected = source_checks(a.checklist)
    ids = {c['id'] for c in expected}
    require(data.get('checklist_sha256') == digest(a.checklist), 'Stale checklist digest')
    require(data.get('pages'), 'No page reviews')
    seen = set()
    counts = {s: 0 for s in ('PASS', 'NEEDS FIX', 'NOT CHECKED', 'NOT APPLICABLE')}
    unresolved = []
    for page in data['pages']:
        pn = page['page']
        require(pn not in seen, 'Duplicate page review')
        seen.add(pn)
        entries = page['checks']
        require(len(entries) == 40 and {c['id'] for c in entries} == ids, f'Wrong check coverage page {pn}')
        pdf = rp.parent / page.get('pdf', '')
        require(pdf.is_file() and page.get('pdf_sha256') == digest(pdf), f'Page {pn}: missing/current PDF hash mismatch')
        for c in entries:
            st = c['status']
            require(st in counts, f'Unknown status {st}')
            counts[st] += 1
            field = 'observation' if st in ('PASS', 'NOT APPLICABLE') else 'limitation'
            require(isinstance(c.get(field), str) and c[field].strip(), f'Page {pn} {c["id"]}: missing {field}')
            if st in ('NEEDS FIX', 'NOT CHECKED'):
                unresolved.append({'page': pn, 'id': c['id'], 'status': st, 'limitation': c['limitation']})
    return {'schema_valid': True, 'counts': counts, 'unresolved': unresolved,
            'all_checks_resolved': not unresolved,
            'limitation': 'Checks record structure and hashes, not the truth of visual observations or author approval.'}


def merge_pages(a):
    import fitz
    manifest = Path(a.manifest)
    data = json.loads(manifest.read_text())
    entries = data['pages']
    require(entries, 'Empty merge manifest')
    page_ids = [p['page'] for p in entries]
    require(all(isinstance(n, int) for n in page_ids), 'Page identifiers must be integers')
    require(page_ids == sorted(set(page_ids)), 'Page IDs must be unique and in manuscript order')
    require(all(y == x + 1 for x, y in zip(page_ids, page_ids[1:])), 'Missing page in batch sequence')
    output = Path(a.out)
    inputs = []
    for item in entries:
        for key in ('pdf', 'source', 'receipt'):
            path = manifest.parent / item[key]
            require(path.is_file() and digest(path) == item[key + '_sha256'], f'Stale or missing {key} on page {item["page"]}')
            require(output.resolve() != path.resolve(), 'Output would overwrite an input')
        inputs.append(pdf_report(manifest.parent / item['pdf']))
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.staging.pdf')
    with fitz.open() as combined:
        for item in entries:
            with fitz.open(manifest.parent / item['pdf']) as source:
                combined.insert_pdf(source)
        combined.save(temporary, garbage=0, deflate=False)
    try:
        checked = pdf_report(temporary, len(entries))
        for i, original in enumerate(inputs):
            before, after = original['pages'][0], checked['pages'][i]
            for key in ('boxes', 'rasters', 'render_sha256'):
                require(before[key] == after[key], f'Packaging altered {key} on page {page_ids[i]}')
        temporary.replace(output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return {'file': str(output), 'sha256': digest(output), 'bytes': output.stat().st_size,
            'page_order': page_ids, 'structural_merge_verified': True,
            'limitation': 'Receipts must be inspected for actual InDesign execution; merge does not establish content/visual approval.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    h = sub.add_parser('hash', help='Hash supplied source files')
    h.add_argument('files', nargs='+')
    im = sub.add_parser('image', help='Calculate effective PPI after crop and fitting')
    im.add_argument('file'); im.add_argument('--width-pt', type=float, required=True)
    im.add_argument('--height-pt', type=float, required=True)
    im.add_argument('--fit', choices=['contain', 'cover'], default='contain')
    im.add_argument('--crop', type=int, nargs=4, metavar=('X', 'Y', 'W', 'H'))
    pdf = sub.add_parser('pdf', help='Validate and optionally render an exported PDF')
    pdf.add_argument('file'); pdf.add_argument('--pages', type=int, default=1)
    pdf.add_argument('--reported-bytes', type=int); pdf.add_argument('--render-dir')
    rt = sub.add_parser('review-template', help='Create unreviewed entries from current checklist')
    rt.add_argument('checklist'); rt.add_argument('--pages', type=int, nargs='+', required=True); rt.add_argument('--out', required=True)
    rc = sub.add_parser('review-check', help='Validate review coverage, evidence fields and current hashes')
    rc.add_argument('file'); rc.add_argument('--checklist', required=True)
    mg = sub.add_parser('merge', help='Combine already exported native PDF pages without resampling')
    mg.add_argument('manifest'); mg.add_argument('--out', required=True)
    a = p.parse_args()
    if a.command == 'hash':
        result = [{'file': f, 'bytes': Path(f).stat().st_size, 'sha256': digest(f)} for f in a.files]
    elif a.command == 'image': result = image_report(a)
    elif a.command == 'pdf': result = pdf_report(a.file, a.pages, a.reported_bytes, a.render_dir)
    elif a.command == 'review-template':
        checks = source_checks(a.checklist)
        require(len(set(a.pages)) == len(a.pages), 'Duplicate page numbers')
        data = {'checklist_sha256': digest(a.checklist), 'pages': [
            {'page': n, 'pdf': '', 'pdf_sha256': '', 'checks': [dict(c, status='NOT CHECKED', observation='', limitation='') for c in checks],
             'corrections': [], 'unresolved_limitations': []} for n in a.pages]}
        write_json(a.out, data)
        result = {'file': a.out, 'pages': a.pages, 'checks_per_page': 40, 'review_completed': False}
    elif a.command == 'review-check': result = review_check(a)
    else: result = merge_pages(a)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        sys.exit(2)
