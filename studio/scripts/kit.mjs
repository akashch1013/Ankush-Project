// Builds the starter workspace that ships inside the app (resources/workspace), so Studio
// works on a machine without a clone of the repo. Only git-tracked files are copied: no .env,
// no caches, no generated plates. `.claude/` is stored as `_claude/` (dotfiles are dropped
// by the packager) and renamed back when Studio creates a workspace.
import { execFileSync } from 'node:child_process';
import { cpSync, mkdirSync, rmSync, writeFileSync, readFileSync, existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const studio = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const repo = resolve(studio, '..');
const out = join(studio, 'build', 'workspace');

const INCLUDE = [
  'CLAUDE.md',
  '.claude/',
  'Tasks/CLAUDE.md',
  'Tasks/LESSONS.md',
  'Tasks/FEEDBACK.md',
  'Tasks/KICKOFF.md',
  'Tasks/pipeline/',
  'Tasks/Charactors/',
  'Tasks/Reference/',
  'Tasks/PdfSheetsGenTask/design/',
  'Tasks/FInalChangesTask/PANEL-GUIDE.md',
  'Tasks/FInalChangesTask/library/',
  'Tasks/BagroundGenTask/',
];
// Bulky or per-machine content: old drafts, generated plates, the cost log.
const EXCLUDE = [
  /^Tasks\/BagroundGenTask\/(archive|out|skill-03[^/]*)\//,
  /^Tasks\/BagroundGenTask\/.*\/out\//,
  /^Tasks\/BagroundGenTask\/.*\.(png|jpe?g|webp|zip|jsonl|docx)$/i,
  /^Tasks\/pipeline\/usage-all\.tsv$/,
  /(^|\/)\.env(\.|$)/,
  /(^|\/)\.gitignore$/,
  /__pycache__|\.pyc$/,
];

const files = execFileSync('git', ['ls-files', '-z', '--', ...INCLUDE], { cwd: repo, maxBuffer: 64 << 20 })
  .toString()
  .split('\0')
  .filter((f) => f && !EXCLUDE.some((re) => re.test(f)));

const missing = files.filter((f) => !existsSync(join(repo, f)));
if (missing.length) {
  console.error(`kit: ${missing.length} tracked files are not checked out, e.g. ${missing.slice(0, 3).join(', ')}`);
  process.exit(1);
}

rmSync(out, { recursive: true, force: true });
for (const f of files) {
  const dest = join(out, f.replace(/^\.claude\//, '_claude/'));
  mkdirSync(dirname(dest), { recursive: true });
  cpSync(join(repo, f), dest);
}
const version = JSON.parse(readFileSync(join(studio, 'package.json'), 'utf8')).version;
writeFileSync(join(out, 'studio-kit.json'), JSON.stringify({ version, files: files.length }, null, 2));
console.log(`kit: ${files.length} files → ${out}`);
