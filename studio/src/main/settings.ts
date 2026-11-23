import { app } from 'electron';
import { existsSync, readFileSync, writeFileSync, mkdirSync, realpathSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, dirname, isAbsolute } from 'node:path';
import type { Settings } from '@shared/types';
import { getOpenAIKey } from './secrets';

const file = () => join(app.getPath('userData'), 'settings.json');

const defaults: Settings = {
  repo: null,
  python: process.platform === 'win32' ? 'python' : 'python3',
  claude: 'claude',
  firefox: 'firefox',
  permissionMode: 'safe',
  chunkSize: 20,
  setupDone: false,
};

let cache: Settings | null = null;

export function getSettings(): Settings {
  if (cache) return cache;
  try {
    cache = { ...defaults, ...JSON.parse(readFileSync(file(), 'utf8')) };
  } catch {
    cache = { ...defaults };
  }
  // First run from inside the repo (dev): studio/ sits next to Tasks/.
  if (!cache!.repo) {
    const guess = join(app.getAppPath(), '..');
    if (existsSync(join(guess, 'Tasks', 'CLAUDE.md'))) cache!.repo = guess;
  }
  return cache!;
}

export function saveSettings(patch: Partial<Settings>): Settings {
  cache = { ...getSettings(), ...patch };
  mkdirSync(dirname(file()), { recursive: true });
  writeFileSync(file(), JSON.stringify(cache, null, 2));
  return cache;
}

export function tasksDir(): string | null {
  const repo = getSettings().repo;
  return repo ? join(repo, 'Tasks') : null;
}

export function requireTasks(): string {
  const t = tasksDir();
  if (!t || !existsSync(join(t, 'CLAUDE.md'))) throw new Error('Workspace not set: create one or choose the folder that contains Tasks/ in Settings.');
  return t;
}

/** Absolute path of the claude CLI: the configured path, else PATH or ~/.local/bin; undefined = the SDK's bundled CLI. */
export function claudeBin(): string | undefined {
  const c = getSettings().claude;
  if (c && c !== 'claude') return c;
  const exe = process.platform === 'win32' ? 'claude.exe' : 'claude';
  const dirs = [...(process.env.PATH ?? '').split(process.platform === 'win32' ? ';' : ':'), join(homedir(), '.local', 'bin'), join(homedir(), '.claude', 'local')];
  for (const d of dirs) {
    const p = join(d, exe);
    if (d && existsSync(p)) return realpathSync(p);
  }
  return undefined;
}

/**
 * Environment for child processes: the OpenAI key saved in Studio becomes OPENAI_API_KEY (imggen.py reads it
 * first), and a custom Firefox path goes first on PATH (render_pdf.py runs `firefox`).
 */
export function childEnv(): NodeJS.ProcessEnv {
  const env: NodeJS.ProcessEnv = { ...process.env };
  const key = getOpenAIKey();
  if (key) env.OPENAI_API_KEY = key;
  const ff = getSettings().firefox;
  const sepc = process.platform === 'win32' ? ';' : ':';
  if (ff && isAbsolute(ff)) env.PATH = `${dirname(ff)}${sepc}${process.env.PATH ?? ''}`;
  return env;
}
