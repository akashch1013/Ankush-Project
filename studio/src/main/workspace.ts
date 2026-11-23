// Creates a ChandRush workspace from the starter kit bundled with the app (resources/workspace,
// built by scripts/kit.mjs), so Studio needs no clone of the GitHub repo.
import { app } from 'electron';
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, renameSync } from 'node:fs';
import { join } from 'node:path';
import { runCmd } from './tools';
import { saveSettings } from './settings';
import type { Settings } from '@shared/types';

export function kitDir(): string | null {
  const d = app.isPackaged ? join(process.resourcesPath, 'workspace') : join(app.getAppPath(), 'build', 'workspace');
  return existsSync(join(d, 'Tasks', 'CLAUDE.md')) ? d : null;
}

export function kitInfo(): { available: boolean; version?: string } {
  const d = kitDir();
  if (!d) return { available: false };
  try {
    return { available: true, version: JSON.parse(readFileSync(join(d, 'studio-kit.json'), 'utf8')).version };
  } catch {
    return { available: true };
  }
}

export const defaultWorkspacePath = () => join(app.getPath('documents'), 'ChandRush Studio');

/** Copy the kit into `target` (existing files are never overwritten) and make it the workspace. */
export async function createWorkspace(target: string): Promise<{ ok: boolean; error?: string; settings?: Settings }> {
  const kit = kitDir();
  if (!kit) return { ok: false, error: 'This build has no bundled workspace. Choose an existing folder instead.' };
  if (existsSync(target) && readdirSync(target).length && !existsSync(join(target, 'Tasks', 'CLAUDE.md'))) {
    return { ok: false, error: `${target} is not empty. Pick an empty folder, or a folder that already holds a ChandRush workspace.` };
  }
  try {
    mkdirSync(target, { recursive: true });
    cpSync(kit, target, { recursive: true, force: false, errorOnExist: false });
    const claude = join(target, '_claude');
    if (existsSync(claude)) {
      if (existsSync(join(target, '.claude'))) cpSync(claude, join(target, '.claude'), { recursive: true, force: false, errorOnExist: false });
      else renameSync(claude, join(target, '.claude'));
    }
    for (const d of ['Output', 'PdfSheetsGenTask', 'FInalChangesTask', 'BagroundGenTask']) mkdirSync(join(target, 'Tasks', d), { recursive: true });
  } catch (e) {
    return { ok: false, error: `Could not create the workspace: ${(e as Error).message}` };
  }
  // Best effort: a git repo lets the Rules view show what changed in LESSONS.md / FEEDBACK.md.
  if (!existsSync(join(target, '.git'))) {
    const git = (args: string[]) => runCmd('git', args, target, 60_000);
    if ((await git(['init', '-q'])).code === 0) {
      await git(['add', '-A']);
      await git(['-c', 'user.name=ChandRush Studio', '-c', 'user.email=studio@localhost', 'commit', '-qm', 'ChandRush Studio workspace']);
    }
  }
  return { ok: true, settings: saveSettings({ repo: target }) };
}
