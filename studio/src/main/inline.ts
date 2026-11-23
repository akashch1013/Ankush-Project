// Inline text edits from the page editor: targeted replacements in index.html, nothing else touched.
import { readFileSync, writeFileSync } from 'node:fs';
import { parse, type HTMLElement } from 'node-html-parser';
import type { InlineEdit } from '../shared/types.ts';

const INLINE = new Set(['b', 'i', 'em', 'strong', 'span', 'br', 'sup', 'sub', 'small', 'u', 'mark']);
const norm = (s: string) => s.replace(/\s+/g, ' ').trim();

function byPath(body: HTMLElement, path: number[]): HTMLElement | null {
  let el: HTMLElement | null = body;
  for (const i of path) {
    const kids: HTMLElement[] = el.childNodes.filter((n): n is HTMLElement => n.nodeType === 1);
    el = kids[i] ?? null;
    if (!el) return null;
  }
  return el;
}

function all(root: HTMLElement): HTMLElement[] {
  return root.querySelectorAll('*');
}

export interface ApplyResult {
  html: string;
  applied: number;
  skipped: string[];
  mathChanged: boolean;
}

/** Apply edits to an HTML string. Each edit is located by element path, verified by its old text, else found by unique old text. */
export function applyEdits(html: string, edits: InlineEdit[]): ApplyResult {
  const root = parse(html, { comment: true, blockTextElements: { script: true, style: true, noscript: true, pre: true } });
  const body = root.querySelector('body') ?? root;
  let applied = 0;
  let mathChanged = false;
  const skipped: string[] = [];
  // Splice each element's source range so the rest of the file stays byte-identical.
  const splices: { start: number; end: number; text: string }[] = [];
  for (const e of edits) {
    let el = byPath(body, e.path);
    if (!el || norm(el.textContent) !== norm(e.oldText)) {
      const matches = all(body).filter((x) => norm(x.textContent) === norm(e.oldText) && all(x).every((k) => INLINE.has(k.rawTagName.toLowerCase())));
      el = matches.length === 1 ? matches[0] : null;
    }
    if (!el) {
      skipped.push(e.oldText.slice(0, 60));
      continue;
    }
    const [start, end] = el.range;
    const open = html.slice(start, end).match(/^<[^>]*>/)?.[0] ?? '';
    const tag = el.rawTagName;
    let openTag = open;
    const dm = el.getAttribute('data-math');
    if (dm !== undefined && dm !== null) {
      mathChanged = true;
      // Keep data-math in step when it mirrored the visible text.
      if (norm(dm) === norm(e.oldText)) openTag = open.replace(/data-math=("[^"]*"|'[^']*')/, `data-math="${e.newText.replace(/"/g, '&quot;')}"`);
    }
    if (el.querySelector('[data-math]') || el.closest('[data-math]')) mathChanged = true;
    splices.push({ start, end, text: `${openTag}${e.newHtml}</${tag}>` });
    applied++;
  }
  // Apply from the end so earlier ranges stay valid; drop overlapping edits (keep the outer one first seen).
  splices.sort((a, b) => b.start - a.start);
  let out = html;
  let lastStart = Infinity;
  for (const s of splices) {
    if (s.end > lastStart) {
      skipped.push('(overlapping edit)');
      applied--;
      continue;
    }
    out = out.slice(0, s.start) + s.text + out.slice(s.end);
    lastStart = s.start;
  }
  return { html: out, applied, skipped, mathChanged };
}

export function applyEditsToFile(file: string, edits: InlineEdit[]): ApplyResult {
  const html = readFileSync(file, 'utf8');
  const r = applyEdits(html, edits);
  if (r.applied) writeFileSync(file, r.html);
  return r;
}
