// review.json per chapter (the author's verdicts) + FEEDBACK.md logging.
import { appendFileSync, existsSync, readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { tasksDir, requireTasks } from './settings';
import type { ReviewEntry, ReviewStatus } from '@shared/types';

type ReviewFile = Record<string, ReviewEntry>;

const fileFor = (chapter: string) => join(requireTasks(), 'PdfSheetsGenTask', chapter, 'review.json');

export function readReview(chapter: string): ReviewFile {
  const t = tasksDir();
  if (!t) return {};
  try {
    return JSON.parse(readFileSync(join(t, 'PdfSheetsGenTask', chapter, 'review.json'), 'utf8'));
  } catch {
    return {};
  }
}

function write(chapter: string, data: ReviewFile) {
  const f = fileFor(chapter);
  mkdirSync(dirname(f), { recursive: true });
  const sorted = Object.fromEntries(Object.entries(data).sort(([a], [b]) => a.localeCompare(b)));
  writeFileSync(f, JSON.stringify(sorted, null, 1) + '\n');
}

export function updatePage(chapter: string, page: string, patch: Partial<ReviewEntry>) {
  const data = readReview(chapter);
  const cur: ReviewEntry = data[page] ?? { status: 'none' };
  data[page] = { ...cur, ...patch };
  write(chapter, data);
  return data[page];
}

export function setStatus(chapter: string, pages: string[], status: ReviewStatus, note?: string, gate?: string) {
  const data = readReview(chapter);
  const at = new Date().toISOString();
  for (const page of pages) {
    const cur: ReviewEntry = data[page] ?? { status: 'none' };
    const history = [...(cur.history ?? []), { status, note, at }].slice(-20);
    data[page] = { ...cur, status, note, at, gate: gate ?? cur.gate, history };
  }
  write(chapter, data);
}

export const today = () => new Date().toLocaleDateString('en-CA'); // local YYYY-MM-DD

/** One FEEDBACK.md line in the existing "- date · chapter/page · stage · words → action" format. */
export function logFeedback(where: string, stage: string, words: string, action: string) {
  const f = join(requireTasks(), 'FEEDBACK.md');
  if (!existsSync(f)) return;
  const quoted = words ? `"${words.replace(/\s+/g, ' ').trim()}"` : '';
  const line = `- ${today()} · ${where} · ${stage} · ${[quoted, action].filter(Boolean).join(' → ')}\n`;
  const cur = readFileSync(f, 'utf8');
  appendFileSync(f, cur.endsWith('\n') ? line : '\n' + line);
}
