// Builds the starter workspace that ships inside the app (resources/workspace), so Studio
// works on a machine without a clone of the repo. Only git-tracked files are copied: no .env,
// no caches, no generated plates. `.claude/` is stored as `_claude/` (dotfiles are dropped
// by the packager) and renamed back when Studio creates a workspace.
import { execFileSync } from 'node:child_process';
import { cpSync, mkdirSync, rmSync, writeFileSync, readFileSync, existsSync } from 'node:fs';
import { dirname, join, posix, resolve } from 'node:path';
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

// `git ls-files -s`: "<mode> <sha> <stage>\t<path>". Symlinks (mode 120000) are resolved from git and copied
// as real files: Windows checkouts turn them into text files, and a link would point outside the kit anyway.
const entries = execFileSync('git', ['ls-files', '-s', '-z', '--', ...INCLUDE], { cwd: repo, maxBuffer: 64 << 20 })
  .toString()
  .split('\0')
  .filter(Boolean)
  .map((l) => {
    const [meta, path] = l.split('\t');
    const [mode, sha] = meta.split(' ');
    return { mode, sha, path };
  });

const files = [];
for (const e of entries) {
  if (e.mode !== '120000') {
    files.push({ src: e.path, dest: e.path });
    continue;
  }
  const target = posix.normalize(posix.join(posix.dirname(e.path), execFileSync('git', ['cat-file', 'blob', e.sha], { cwd: repo }).toString().trim()));
  const under = execFileSync('git', ['ls-files', '-z', '--', target], { cwd: repo }).toString().split('\0').filter(Boolean);
  if (!under.length) {
    console.error(`kit: symlink ${e.path} → ${target} points at nothing tracked`);
    process.exit(1);
  }
  for (const f of under) files.push({ src: f, dest: under.length === 1 && f === target ? e.path : posix.join(e.path, posix.relative(target, f)) });
}
const kept = files.filter((f) => !EXCLUDE.some((re) => re.test(f.dest)));

const missing = kept.filter((f) => !existsSync(join(repo, f.src)));
if (missing.length) {
  console.error(`kit: ${missing.length} tracked files are not checked out, e.g. ${missing.slice(0, 3).map((f) => f.src).join(', ')}`);
  process.exit(1);
}

rmSync(out, { recursive: true, force: true });
for (const f of kept) {
  const dest = join(out, f.dest.replace(/^\.claude\//, '_claude/'));
  mkdirSync(dirname(dest), { recursive: true });
  cpSync(join(repo, f.src), dest);
}
const version = JSON.parse(readFileSync(join(studio, 'package.json'), 'utf8')).version;
writeFileSync(join(out, 'studio-kit.json'), JSON.stringify({ version, files: kept.length }, null, 2));
console.log(`kit: ${kept.length} files → ${out}`);
