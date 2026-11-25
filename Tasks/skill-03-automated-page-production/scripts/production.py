#!/usr/bin/env python3
"""Objective production guards; never a substitute for visual review or InDesign."""
import argparse
import hashlib
import json
import math
import re
import sys
import tempfile
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
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_checks(path, expected_count=None):
    """Read reviewed JSON or a simple, ID-led text checklist."""
    text = Path(path).read_text(encoding='utf-8-sig')
    if Path(path).suffix.lower() == '.json' or text.lstrip().startswith('{'):
        data = json.loads(text)
        checks = data['checks'] if isinstance(data, dict) else data
        require(isinstance(checks, list), 'Expected a list of checklist entries')
    else:
        checks = []
        active = None
        heading = re.compile(
            r'^\s*(?:\[([^]\n]+)\]|([A-Za-z][A-Za-z_.-]*\d+[A-Za-z0-9_.-]*)'
            r'|([0-9]+(?:\.[0-9]+)*)[.)])(?:[ \t]+|[ \t]*[:–—][ \t]*)(\S.*)$')
        for raw in text.splitlines():
            match = heading.match(raw)
            if match:
                ident = next(group for group in match.groups()[:3] if group is not None)
                active = {'id': ident, 'requirement': match.group(4).strip()}
                checks.append(active)
            elif not raw.strip():
                active = None
            elif active is not None:
                # PDF text can wrap flush left. A new unindented prose paragraph
                # after a finished item is an editorial note or section heading.
                complete = re.search(r'[.!?][\u2019\u201d"\')]*$', active['requirement'])
                if complete and not raw[0].isspace() and raw.strip()[0].isupper():
                    active = None
                else:
                    active['requirement'] += ' ' + raw.strip()
    require(checks, 'No checks found. Supply the checked list as JSON for an unstructured source.')
    for item in checks:
        require(isinstance(item, dict) and all(isinstance(item.get(k), str) and item[k].strip()
                for k in ('id', 'requirement')), 'Each check needs a text ID and the complete requirement')
    require(len({item['id'] for item in checks}) == len(checks), 'Duplicate checklist IDs')
    if expected_count is not None:
        require(len(checks) == expected_count, f'Expected {expected_count} checks, found {len(checks)}')
    return [{'id': item['id'], 'requirement': item['requirement']} for item in checks]


def page_id(value):
    return int(value) if re.fullmatch(r'0|[1-9][0-9]*', value) else value


def image_report(a):
    from PIL import Image
    with Image.open(a.file) as im:
        original = im.size
    x, y, w, h = a.crop or (0, 0, *original)
    require(min(a.width_pt, a.height_pt, w, h) > 0, 'Positive dimensions required')
    require(x >= 0 and y >= 0 and x + w <= original[0] and y + h <= original[1], 'Crop outside native image')
    scale = (min if a.fit == 'contain' else max)(a.width_pt / w, a.height_pt / h)
    ppi = 72 / scale
    result = {'file': a.file, 'sha256': digest(a.file), 'native_pixels': original,
            'crop_pixels': [x, y, w, h], 'frame_pt': [a.width_pt, a.height_pt],
            'placed_size_pt': [w * scale, h * scale], 'fit': a.fit,
            'effective_ppi': ppi,
            'limitation': 'Native pixel calculation only; inspect crop, sharpness and any prior upscaling.'}
    minimum = getattr(a, 'min_ppi', None)
    if minimum is not None:
        require(minimum > 0, 'Minimum PPI must be positive')
        result.update(minimum_ppi=minimum, meets_minimum=ppi + 0.01 >= minimum)
    return result


def pdf_report(file, pages=1, reported_bytes=None, render_dir=None, trim_pt=None, zero_bleed=False):
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
            boxes = {k: list(getattr(pg, k)) for k in ('mediabox', 'cropbox', 'trimbox', 'bleedbox')}
            require(pg.trimbox.width > 0 and pg.trimbox.height > 0, 'Empty trim box')
            if trim_pt is not None:
                require(all(abs(a - b) < .1 for a, b in zip(
                    (pg.trimbox.width, pg.trimbox.height), trim_pt)),
                    f'Wrong trim size on PDF page {i + 1}: {pg.trimbox}')
            if zero_bleed:
                for key, box in boxes.items():
                    require(all(abs(a-b) < .1 for a, b in zip(box, boxes['mediabox'])),
                            f'{key} differs from media box on a zero-bleed page')
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
            report['pages'].append({'index': i + 1, 'rotation': pg.rotation, 'boxes': boxes, 'rasters': rasters,
                                    'render_sha256': hashlib.sha256(pix.samples).hexdigest()})
    report['limitation'] = 'Objective file checks only. Does not certify all colours, visual quality, source completeness, font availability or overset.'
    return report


def review_check(a):
    rp = Path(a.file)
    data = json.loads(rp.read_text())
    expected = source_checks(a.checklist)
    requirements = {c['id']: c['requirement'] for c in expected}
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
        require(len(entries) == len(expected) and {c['id'] for c in entries} == requirements.keys(),
                f'Wrong check coverage on page {pn}')
        pdf = rp.parent / page.get('pdf', '')
        require(pdf.is_file() and page.get('pdf_sha256') == digest(pdf), f'Page {pn}: missing/current PDF hash mismatch')
        for c in entries:
            require(c.get('requirement') == requirements[c['id']],
                    f'Page {pn} {c["id"]}: requirement differs from the current checklist')
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
    require(all(isinstance(n, (int, str)) for n in page_ids), 'Expected folio strings or integers')
    require(len(set(page_ids)) == len(page_ids), 'Duplicate page IDs')
    if 'expected_pages' in data:
        require(page_ids == data['expected_pages'], 'Page order differs from the assignment')
    elif all(isinstance(n, int) for n in page_ids):
        require(all(y == x + 1 for x, y in zip(page_ids, page_ids[1:])),
                'Missing or reordered page. For selected ranges supply expected_pages in manuscript order.')
    output = Path(a.out)
    inputs = []
    for item in entries:
        for key in ('pdf', 'source', 'receipt'):
            path = manifest.parent / item[key]
            require(path.is_file() and digest(path) == item[key + '_sha256'], f'Stale or missing {key} on page {item["page"]}')
            require(output.resolve() != path.resolve(), 'Output would overwrite an input')
        inputs.append(pdf_report(manifest.parent / item['pdf']))
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix='.pdf', delete=False) as staging:
        temporary = Path(staging.name)
    try:
        with fitz.open() as combined:
            for item in entries:
                with fitz.open(manifest.parent / item['pdf']) as source:
                    combined.insert_pdf(source)
            combined.save(temporary, garbage=0, deflate=False)
        checked = pdf_report(temporary, len(entries))
        for i, original in enumerate(inputs):
            before, after = original['pages'][0], checked['pages'][i]
            for key in ('rotation', 'boxes', 'rasters', 'render_sha256'):
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
    im.add_argument('--min-ppi', type=float, help='Optional minimum specified by the edition')
    pdf = sub.add_parser('pdf', help='Validate and optionally render an exported PDF')
    pdf.add_argument('file'); pdf.add_argument('--pages', type=int, default=1)
    pdf.add_argument('--reported-bytes', type=int); pdf.add_argument('--render-dir')
    pdf.add_argument('--trim-pt', type=float, nargs=2, metavar=('WIDTH', 'HEIGHT'))
    pdf.add_argument('--zero-bleed', action='store_true', help='Require coincident page boxes')
    rt = sub.add_parser('review-template', help='Create unreviewed entries from current checklist')
    rt.add_argument('checklist'); rt.add_argument('--pages', type=page_id, nargs='+', required=True); rt.add_argument('--out', required=True)
    rt.add_argument('--expected-count', type=int, help='Optional count from this edition')
    rc = sub.add_parser('review-check', help='Validate review coverage, evidence fields and current hashes')
    rc.add_argument('file'); rc.add_argument('--checklist', required=True)
    mg = sub.add_parser('merge', help='Combine already exported native PDF pages without resampling')
    mg.add_argument('manifest'); mg.add_argument('--out', required=True)
    a = p.parse_args()
    if a.command == 'hash':
        result = [{'file': f, 'bytes': Path(f).stat().st_size, 'sha256': digest(f)} for f in a.files]
    elif a.command == 'image': result = image_report(a)
    elif a.command == 'pdf': result = pdf_report(a.file, a.pages, a.reported_bytes, a.render_dir, a.trim_pt, a.zero_bleed)
    elif a.command == 'review-template':
        checks = source_checks(a.checklist, a.expected_count)
        require(len(set(a.pages)) == len(a.pages), 'Duplicate page numbers')
        data = {'checklist_sha256': digest(a.checklist), 'pages': [
            {'page': n, 'pdf': '', 'pdf_sha256': '', 'checks': [dict(c, status='NOT CHECKED', observation='', limitation='') for c in checks],
             'corrections': [], 'unresolved_limitations': []} for n in a.pages]}
        write_json(a.out, data)
        result = {'file': a.out, 'pages': a.pages, 'checks_per_page': len(checks), 'review_completed': False}
    elif a.command == 'review-check': result = review_check(a)
    else: result = merge_pages(a)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        sys.exit(2)
