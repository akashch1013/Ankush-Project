import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { getSettings, tasksDir, claudeBin } from './settings';
import { runCmd } from './tools';
import { keyStatus } from './secrets';
import type { DoctorCheck } from '@shared/types';

export async function runDoctor(): Promise<DoctorCheck[]> {
  const s = getSettings();
  const tasks = tasksDir();
  const checks: DoctorCheck[] = [];

  const ws = !!tasks && existsSync(join(tasks, 'CLAUDE.md'));
  checks.push({ name: 'Workspace', ok: ws, detail: ws ? tasks! : 'Tasks/CLAUDE.md not found', fix: 'Settings → create a workspace, or choose the folder that contains Tasks/.' });

  const py = await runCmd(s.python, ['-c', 'import sys, PIL; print(sys.version.split()[0], "PIL", PIL.__version__)']);
  checks.push({ name: 'Python 3 + Pillow', ok: py.code === 0, detail: py.out.trim() || 'not found', fix: `Install Python 3 and Pillow (pip install pillow), or set the Python path in Settings (now "${s.python}").` });

  const ff = await runCmd(s.firefox, ['--version']);
  checks.push({ name: 'Firefox (PDF render)', ok: ff.code === 0, detail: ff.out.trim().split('\n').pop() || 'not found', fix: 'pipeline/render_pdf.py runs `firefox --headless`. Install Firefox and make sure it is on PATH.' });

  const bin = claudeBin() ?? s.claude;
  const cl = await runCmd(bin, ['--version']);
  checks.push({ name: 'Claude Code CLI', ok: cl.code === 0, detail: cl.out.trim() || 'not found', fix: `Install Claude Code, or set its path in Settings (now "${s.claude}").` });

  if (cl.code === 0) {
    const auth = await runCmd(bin, ['auth', 'status'], undefined, 20_000);
    const ok = auth.code === 0 && !/not (logged|signed) in/i.test(auth.out);
    checks.push({ name: 'Claude login', ok, detail: auth.out.trim().split('\n').slice(0, 3).join(' · ') || `exit ${auth.code}`, fix: 'Run `claude auth login` in a terminal.' });
  }

  {
    // Same lookup order as pipeline/imggen.py; only presence is checked, the value is never shown.
    const k = keyStatus();
    const file = tasks ? ['.env', 'BagroundGenTask/.env'].find((f) => existsSync(join(tasks, f))) : undefined;
    checks.push({
      name: 'OpenAI key',
      ok: k.source !== null || !!file,
      detail: k.saved ? `saved in Studio (${k.hint})` : k.source === 'env' ? 'OPENAI_API_KEY / CHATGPT_API set in the environment' : file ? `Tasks/${file} present (not read)` : 'no key saved',
      fix: 'Needed for image batches. Settings → OpenAI API key → paste your key.',
    });
  }
  checks.push({ name: 'Node (Electron)', ok: true, detail: `node ${process.versions.node} · electron ${process.versions.electron}` });
  return checks;
}
