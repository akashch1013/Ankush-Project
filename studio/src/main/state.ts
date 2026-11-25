// Builds the board's view of every chapter from the files the pipeline already writes.
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { watch, type FSWatcher } from 'chokidar';
import { getSettings, tasksDir } from './settings';
import { runPipeline } from './tools';
import { readReview } from './review';
import type { ChapterState, PageStage, PageState, SurveyRow, WorkspaceState } from '@shared/types';

const STAGES: PageStage[] = ['source', 'planned', 'built', 'rendered', 'math_pass', 'pending', 'approved', 'changes'];

function readJson<T>(path: string): T | null {
  try {
    return JSON.parse(readFileSync(path, 'utf8')) as T;
  } catch {
    return null;
  }
}

function mtime(path: string): number {
  try {
    return statSync(path).mtimeMs;
  } catch {
    return 0;
  }
}

// ---------- survey (cached per src dir mtime) ----------
const surveyCache = new Map<string, { mtime: number; rows: SurveyRow[] }>();

export function parseSurvey(out: string): SurveyRow[] {
  const rows: SurveyRow[] = [];
  for (const line of out.split('\n')) {
    const m = line.trim().match(/^(P\d{3})\s+(\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)/);
    if (m) rows.push({ page: m[1], kind: m[2], panels: +m[3], story: +m[4], examples: +m[5], equations: +m[6], words: +m[7] });
  }
  return rows;
}

async function survey(srcDir: string): Promise<SurveyRow[]> {
  const t = mtime(srcDir);
  const hit = surveyCache.get(srcDir);
  if (hit && hit.mtime === t) return hit.rows;
  const tasks = tasksDir()!;
  const r = await runPipeline('textcheck.py', ['survey', relative(tasks, srcDir)], undefined, 60_000);
  const rows = r.code === 0 ? parseSurvey(r.out) : [];
  surveyCache.set(srcDir, { mtime: t, rows });
  return rows;
}

// ---------- reference folders → chapter ids ----------
export function referenceChapters(tasks: string): Map<string, { dir: string; manuscript?: string; register?: string }> {
  const map = new Map<string, { dir: string; manuscript?: string; register?: string }>();
  const ref = join(tasks, 'Reference');
  if (!existsSync(ref)) return map;
  for (const d of readdirSync(ref, { withFileTypes: true })) {
    if (!d.isDirectory() || /\bold\b/i.test(d.name)) continue;
    for (const f of readdirSync(join(ref, d.name))) {
      const m = f.match(/^(CH\d{2})-.*\.docx$/i);
      if (!m) continue;
      const id = m[1].toUpperCase();
      const e = map.get(id) ?? { dir: `Reference/${d.name}` };
      if (/MANUSCRIPT/i.test(f)) e.manuscript = `Reference/${d.name}/${f}`;
      if (/REGISTER/i.test(f)) e.register = `Reference/${d.name}/${f}`;
      map.set(id, e);
    }
  }
  return map;
}

// ---------- image cost ----------
export function imageCosts(tasks: string): { total: number; byChapter: Map<string, number> } {
  const byChapter = new Map<string, number>();
  let total = 0;
  try {
    const lines = readFileSync(join(tasks, 'pipeline', 'usage-all.tsv'), 'utf8').split('\n').slice(1);
    for (const l of lines) {
      const cols = l.split('\t');
      const usd = parseFloat(cols[8]);
      if (!isFinite(usd)) continue;
      total += usd;
      const m = `${cols[1]} ${cols[3] ?? ''} ${cols[5] ?? ''}`.match(/ch-?0?(\d{1,2})/i);
      if (m) {
        const id = `CH${m[1].padStart(2, '0')}`;
        byChapter.set(id, (byChapter.get(id) ?? 0) + usd);
      }
    }
  } catch {
    /* no usage yet */
  }
  return { total, byChapter };
}

interface PlanPage {
  page: string;
  title?: string;
  purpose?: string;
  panels?: { art?: { kind?: string } }[];
}

export function stageOf(p: Omit<PageState, 'stage'>): PageStage {
  if (p.review.status === 'approved') return 'approved';
  if (p.review.status === 'changes') return 'changes';
  if (p.review.status === 'pending') return 'pending';
  if (p.math?.startsWith('PASS') && !p.review.edited) return 'math_pass';
  if (p.preview && p.pdf) return 'rendered';
  if (p.built) return 'built';
  if (p.planned) return 'planned';
  return 'source';
}

async function chapterState(tasks: string, id: string, ref?: { dir: string; manuscript?: string; register?: string }, cost = 0): Promise<ChapterState> {
  const chDir = join(tasks, 'PdfSheetsGenTask', id);
  const srcDir = join(chDir, 'src');
  const hasSrc = existsSync(srcDir);
  const plan = readJson<{ chapter_label?: string; pages?: PlanPage[] }>(join(chDir, 'pages.json'));
  const artifacts = readJson<Record<string, { math?: string }>>(join(chDir, 'artifacts.json')) ?? {};
  const review = readReview(id);
  const rows = hasSrc ? await survey(srcDir) : [];

  const ids = new Set<string>();
  rows.forEach((r) => ids.add(r.page));
  plan?.pages?.forEach((p) => ids.add(p.page));
  if (existsSync(chDir)) for (const d of readdirSync(chDir)) if (/^P\d{3}$/.test(d)) ids.add(d);

  const pages: PageState[] = [...ids].sort().map((page) => {
    const pp = plan?.pages?.find((x) => x.page === page);
    const pageDir = join(chDir, page);
    const previewAbs = join(pageDir, 'preview.png');
    const pdfAbs = join(tasks, 'Output', id, `${id}-${page}.pdf`);
    const base: Omit<PageState, 'stage'> = {
      page,
      title: pp?.title,
      purpose: pp?.purpose,
      survey: rows.find((r) => r.page === page),
      planned: !!pp,
      built: existsSync(join(pageDir, 'index.html')),
      preview: existsSync(previewAbs) ? relative(tasks, previewAbs) : undefined,
      previewMtime: mtime(previewAbs) || undefined,
      pdf: existsSync(pdfAbs) ? relative(tasks, pdfAbs) : undefined,
      math: review[page]?.math ?? artifacts[page]?.math,
      review: review[page] ?? { status: 'none' },
      newArt: pp?.panels?.filter((x) => x.art?.kind === 'new').length ?? 0,
    };
    return { ...base, stage: stageOf(base) };
  });

  const counts = Object.fromEntries(STAGES.map((s) => [s, 0])) as Record<PageStage, number>;
  pages.forEach((p) => counts[p.stage]++);
  return {
    id,
    label: plan?.chapter_label,
    referenceDir: ref?.dir,
    manuscript: ref?.manuscript,
    register: ref?.register,
    hasSrc,
    hasPlan: !!plan,
    pages,
    imageCostUsd: cost,
    counts,
  };
}

export async function workspaceState(): Promise<WorkspaceState> {
  const tasks = tasksDir();
  const repo = getSettings().repo;
  if (!tasks || !existsSync(join(tasks, 'CLAUDE.md'))) {
    return { repo, tasks: null, chapters: [], imageCostUsd: 0, error: 'Choose the repo folder (the one containing Tasks/) in Settings.' };
  }
  const refs = referenceChapters(tasks);
  const ids = new Set<string>(refs.keys());
  const sheets = join(tasks, 'PdfSheetsGenTask');
  if (existsSync(sheets)) for (const d of readdirSync(sheets)) if (/^CH\d{2}$/.test(d) && d !== 'CH00') ids.add(d);
  const costs = imageCosts(tasks);
  const chapters = await Promise.all([...ids].sort().map((id) => chapterState(tasks, id, refs.get(id), costs.byChapter.get(id) ?? 0)));
  return { repo, tasks, chapters, imageCostUsd: costs.total };
}

// ---------- watching ----------
let watcher: FSWatcher | null = null;
let timer: NodeJS.Timeout | null = null;

export function watchWorkspace(onChange: () => void) {
  watcher?.close();
  const tasks = tasksDir();
  if (!tasks || !existsSync(tasks)) return;
  const targets = ['PdfSheetsGenTask', 'Output', 'Reference', 'pipeline/usage-all.tsv', 'LESSONS.md', 'FEEDBACK.md']
    .map((p) => join(tasks, p))
    .filter(existsSync);
  watcher = watch(targets, {
    ignoreInitial: true,
    depth: 3,
    ignored: (p: string) => /[\\/](assets|fonts|design|node_modules)([\\/]|$)/.test(p),
  });
  watcher.on('all', () => {
    if (timer) clearTimeout(timer);
    timer = setTimeout(onChange, 500);
  });
}
