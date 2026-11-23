import { app } from 'electron';
import { existsSync, readFileSync, writeFileSync, mkdirSync, realpathSync } from 'node:fs';
import { homedir } from 'node:os';
import { join, dirname, isAbsolute } from 'node:path';
import type { Settings } from '@shared/types';
import { getOpenAIKey } from './secrets';

const file = () => join(app.getPath('userData'), 'settings.json');

const PERMS_V = 3;

const defaults: Settings = {
  repo: null,
  python: process.platform === 'win32' ? 'python' : 'python3',
  claude: 'claude',
  firefox: 'firefox',
  permissionMode: 'auto',
  permsDefaultV: PERMS_V,
  chunkSize: 20,
  setupDone: false,
};

let cache: Settings | null = null;

/**
 * "Allow everything" is the default permission mode. Saved settings from before that (marker below PERMS_V) move
 * over once; the author can still pick another mode afterwards. The marker is read from the SAVED file, not the
 * merged settings: merging the defaults in first would always supply the current marker and skip the migration
 * (the v2 bug, which left saved "safe" settings in place; v3 moves them over).
 */
export function migrateSettings(saved: Partial<Settings>): { settings: Settings; changed: boolean } {
  const settings: Settings = { ...defaults, ...saved };
  if ((saved.permsDefaultV ?? 1) >= PERMS_V) return { settings, changed: false };
  settings.permissionMode = 'auto';
  settings.permsDefaultV = PERMS_V;
  return { settings, changed: true };
}

export function getSettings(): Settings {
  if (cache) return cache;
  let saved: Partial<Settings> | null = null;
  try {
    saved = JSON.parse(readFileSync(file(), 'utf8'));
  } catch {}
  if (saved) {
    const m = migrateSettings(saved);
    cache = m.settings;
    if (m.changed) {
      try {
        writeFileSync(file(), JSON.stringify(cache, null, 2));
      } catch {}
    }
  } else {
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
