// New chapter: copy the author's files into a NEW Reference folder (never overwrite), then the free setup prep
// (pipeline/setup_chapter.py). The caller then starts the chapter-setup agent for the judgement steps.
import { copyFileSync, existsSync, mkdirSync, readdirSync } from 'node:fs';
import { basename, join } from 'node:path';
import { requireTasks } from './settings';
import { runPipeline } from './tools';
import type { ToolRunResult } from '@shared/types';

export interface UploadResult {
  ok: boolean;
  chapter?: string;
  folder?: string;
  copied: string[];
  log: string[];
  error?: string;
}

export async function uploadChapter(folderName: string, files: string[]): Promise<UploadResult> {
  const tasks = requireTasks();
  const log: string[] = [];
  const clean = folderName.trim().replace(/[\\/:*?"<>|]/g, '');
  if (!clean) return { ok: false, copied: [], log, error: 'Give the chapter folder a name, e.g. "Chap4".' };
  const docx = files.filter((f) => /\.docx$/i.test(f));
  const ms = docx.find((f) => /MANUSCRIPT/i.test(basename(f)));
  if (!ms) return { ok: false, copied: [], log, error: 'No *PANELIZED-MANUSCRIPT*.docx among the files.' };
  const m = basename(ms).match(/^(CH\d{2})-/i);
  if (!m) return { ok: false, copied: [], log, error: 'The manuscript file name must start with the chapter id, e.g. CH04-PANELIZED-MANUSCRIPT-V01.docx.' };
  const chapter = m[1].toUpperCase();

  const dest = join(tasks, 'Reference', clean);
  if (existsSync(dest) && readdirSync(dest).length) {
    const clash = files.filter((f) => existsSync(join(dest, basename(f))));
    if (clash.length) return { ok: false, copied: [], log, error: `Reference/${clean} already has ${clash.map((f) => basename(f)).join(', ')}. Reference files are never overwritten: use a new folder name or a new version number.` };
  }
  mkdirSync(dest, { recursive: true });
  const copied: string[] = [];
  for (const f of files) {
    copyFileSync(f, join(dest, basename(f)));
    copied.push(`Reference/${clean}/${basename(f)}`);
  }
  log.push(`Copied ${copied.length} file(s) to Reference/${clean}/`);
  const prep = await prepChapter(chapter, clean);
  log.push(...prep.map((r) => r.out.trim().split('\n').slice(-3).join('\n')));
  return { ok: prep.every((r) => r.code === 0), chapter, folder: `Reference/${clean}`, copied, log };
}

/** Setup prep (free): dumps, src/ pages, page index, register + plates, cast, maths pre-scan, chapter.json. */
export async function prepChapter(chapter: string, folder?: string): Promise<ToolRunResult[]> {
  return [await runPipeline('setup_chapter.py', ['prep', folder ?? chapter], chapter, 180_000)];
}

/** Prompt for the master session that runs the chapter-setup agent (masters, locations, cast, maths triage). */
export const setupPrompt = (chapter: string) =>
  `/comic-master setup ${chapter}\n\nThe author just handed over ${chapter} in Studio. The free prep already ran. Spawn the chapter-setup agent, then call mcp__studio__request_review with its "Needs the author" items (or "setup complete") so the author sees them.`;
