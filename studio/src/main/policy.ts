// Permission policy for agent tool calls. Pure functions (unit-tested in policy.test.ts).
//
// hardRule() runs on EVERY tool call (PreToolUse hook), whatever the preset or the user's own allow rules:
//   deny  - edits to Tasks/Reference or Charactors, immediate image calls, reading the API key, quality max
//   spend - paid image batch submits: always shown to the author as a Spend card
// presetDecision() answers the prompts the CLI would otherwise show (canUseTool).
import { isAbsolute, join, normalize, relative, sep } from 'node:path';
import type { PermissionPreset } from '../shared/types.ts';

export type Hard = { kind: 'deny'; reason: string } | { kind: 'spend'; reason: string } | null;

const READ_ONLY_TOOLS = new Set([
  'Read', 'Glob', 'Grep', 'ToolSearch', 'Skill', 'Agent', 'Task', 'TodoWrite', 'TaskStop', 'TaskOutput',
  'Monitor', 'ListAgents', 'SendMessage', 'LSP', 'ReadMcpResourceTool', 'ListMcpResourcesTool',
]);
const EDIT_TOOLS = new Set(['Edit', 'Write', 'NotebookEdit', 'MultiEdit']);
const SAFE_EDIT_DIRS = ['PdfSheetsGenTask', 'FInalChangesTask', 'BagroundGenTask', 'Output'];
const SAFE_EDIT_FILES = ['FEEDBACK.md', 'LESSONS.md', 'ACCEPTED-AT-CAP.md'];
const SAFE_CMDS = new Set([
  'ls', 'cat', 'head', 'tail', 'grep', 'rg', 'wc', 'find', 'mkdir', 'cp', 'echo', 'printf', 'sort', 'uniq', 'cut',
  'jq', 'sed', 'awk', 'test', '[', 'cd', 'pwd', 'date', 'file', 'stat', 'diff', 'basename', 'dirname', 'tr', 'true',
  'sleep', 'du', 'xargs', 'touch', 'identify', 'pdfinfo', 'git',
]);
const PY = /^(python3?|py)$/;

function str(v: unknown): string {
  return typeof v === 'string' ? v : '';
}

function inside(abs: string, dir: string) {
  const r = relative(dir, abs);
  return r === '' || (!r.startsWith('..') && !isAbsolute(r));
}

export function resolveIn(tasks: string, p: string): string {
  return normalize(isAbsolute(p) ? p : join(tasks, p));
}

function protectedPath(tasks: string, abs: string) {
  return inside(abs, join(tasks, 'Reference')) || inside(abs, join(tasks, 'Charactors')) || inside(abs, join(tasks, '..', 'Charactors'));
}

const isEnvFile = (p: string) => /(^|[\\/])\.env(\.[\w-]+)?$/.test(p);

export function hardRule(tool: string, input: Record<string, unknown>, tasks: string): Hard {
  const path = str(input.file_path) || str(input.notebook_path) || str(input.path);
  if (EDIT_TOOLS.has(tool) && path && protectedPath(tasks, resolveIn(tasks, path))) {
    return { kind: 'deny', reason: 'Tasks/Reference/ and Charactors/ are read-only (Tasks/CLAUDE.md rule 8).' };
  }
  if ((tool === 'Read' || tool === 'Grep') && path && isEnvFile(path)) {
    return { kind: 'deny', reason: 'The API key file is never read (Tasks/CLAUDE.md rule 8).' };
  }
  const body = str(input.content) + str(input.new_string);
  if (EDIT_TOOLS.has(tool) && /"quality"\s*:\s*"max"/.test(body)) {
    return { kind: 'deny', reason: 'Image quality "max" needs the author\'s approval in chat (rule 3).' };
  }
  if (tool === 'Bash') {
    const cmd = str(input.command);
    if (/--immediate-approved/.test(cmd)) return { kind: 'deny', reason: 'Immediate (non-batch) image calls are not allowed from Studio (rule 3).' };
    if (/(^|[\s'"=/])\.env\b/.test(cmd) && /\b(cat|less|more|head|tail|grep|source|sed|awk|cp|echo|printenv|env)\b|<\s*\S*\.env/.test(cmd)) {
      return { kind: 'deny', reason: 'The API key file is never read or printed (rule 8).' };
    }
    if (/\b(OPENAI_API_KEY|CHATGPT_API)\b|\/proc\/[^\s]*environ|(^|[;&|(]\s*)(env|printenv|export\s+-p|set|declare\s+-p?x?)\s*($|[;&|)>])|\bprintenv\b|os\.environ\b|process\.env\b/.test(cmd)) {
      return { kind: 'deny', reason: 'The API key is in the environment and is never read or printed (rule 8).' };
    }
    if (/--quality\s+max\b/.test(cmd)) return { kind: 'deny', reason: 'Image quality "max" needs the author\'s approval (rule 3).' };
    if (/(Reference\/|Charactors)/.test(cmd) && /(\brm\b|\bmv\b|sed\s+-i|>\s*['"]?\S*(Reference\/|Charactors)|\btee\b[^|]*(Reference\/|Charactors))/.test(cmd)) {
      return { kind: 'deny', reason: 'Tasks/Reference/ and Charactors/ are read-only (rule 8).' };
    }
    if (/imggen\.py\b[^\n]*\bbatch\s+submit\b/.test(cmd) || /imggen\.py\b[^\n]*\s(gen)\s/.test(cmd + ' ')) {
      return { kind: 'spend', reason: 'Submits a paid OpenAI image batch.' };
    }
  }
  return null;
}

/** Split a shell command into simple commands (very conservative). Returns null if it can't be judged. */
export function segments(cmd: string): string[][] | null {
  if (/<<|\$\(|`|\beval\b/.test(cmd)) return null; // heredocs, substitutions: ask
  return cmd
    .replace(/[12]?>&[12]/g, '')
    .split(/&&|\|\||;|\||\n|&/)
    .map((s) => s.trim())
    .filter(Boolean)
    .map((s) => s.replace(/\s*[12]?>\s*\S+/g, '').trim()) // drop redirections (checked separately)
    .map((s) => s.split(/\s+/).filter((t) => !/^[A-Z_][A-Z0-9_]*=/.test(t)));
}

function safeBash(cmd: string, tasks: string): boolean {
  const segs = segments(cmd);
  if (!segs) return false;
  // Redirect targets must stay in the safe edit area.
  for (const m of cmd.matchAll(/(?:^|\s)[12]?>>?\s*(\S+)/g)) {
    const target = m[1].replace(/^['"]|['"]$/g, '');
    if (target === '/dev/null' || target === '&1' || target === '&2') continue;
    if (!safeEditPath(tasks, resolveIn(tasks, target))) return false;
  }
  for (const seg of segs) {
    const [c, ...rest] = seg;
    if (!c) continue;
    if (PY.test(c)) {
      const script = rest.find((a) => !a.startsWith('-'));
      if (!script || !/^(\.\.\/Tasks\/|\.\/)?(pipeline|BagroundGenTask|FInalChangesTask)\/[\w./-]+\.py$/.test(script) || script.includes('..')) return false;
      if (rest.includes('-c')) return false;
      continue;
    }
    if (!SAFE_CMDS.has(c)) return false;
    if (c === 'git' && !['status', 'diff', 'log', 'show'].includes(rest[0] ?? '')) return false;
    if (c === 'sed' && rest.some((a) => a.startsWith('-i'))) {
      const file = rest[rest.length - 1];
      if (!file || !safeEditPath(tasks, resolveIn(tasks, file))) return false;
    }
  }
  return true;
}

export function safeEditPath(tasks: string, abs: string): boolean {
  if (protectedPath(tasks, abs)) return false;
  if (SAFE_EDIT_FILES.some((f) => abs === join(tasks, f))) return true;
  if (SAFE_EDIT_DIRS.some((d) => inside(abs, join(tasks, d)))) return !isEnvFile(abs);
  if (abs.startsWith(normalize('/tmp/claude-')) || abs.startsWith(normalize('/tmp/claude' + sep))) return true; // session scratchpads
  return false;
}

export function presetDecision(preset: PermissionPreset, tool: string, input: Record<string, unknown>, tasks: string): 'allow' | 'ask' {
  if (preset === 'auto') return 'allow';
  if (preset === 'ask') return 'ask';
  if (READ_ONLY_TOOLS.has(tool) || tool.startsWith('mcp__studio__')) return 'allow';
  if (EDIT_TOOLS.has(tool)) {
    const path = str(input.file_path) || str(input.notebook_path);
    return path && safeEditPath(tasks, resolveIn(tasks, path)) ? 'allow' : 'ask';
  }
  if (tool === 'Bash') return safeBash(str(input.command), tasks) ? 'allow' : 'ask';
  return 'ask';
}
