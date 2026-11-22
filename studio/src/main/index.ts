import { app, BrowserWindow, dialog, ipcMain, net, protocol, shell } from 'electron';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { basename, extname, join, normalize, relative, isAbsolute } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { getSettings, saveSettings, requireTasks, tasksDir } from './settings';
import { workspaceState, watchWorkspace } from './state';
import { runDoctor } from './doctor';
import { runCmd, runPipeline } from './tools';
import { updatePage, logFeedback } from './review';
import { uploadChapter, prepChapter } from './upload';
import { applyEditsToFile } from './inline';
import { EDITOR_SCRIPT } from './editorScript';
import * as agent from './agent';
import { referenceChapters } from './state';
import type { InlineEdit, InlineSaveResult, Settings } from '@shared/types';

const here = fileURLToPath(new URL('.', import.meta.url));

protocol.registerSchemesAsPrivileged([{ scheme: 'studio', privileges: { standard: true, secure: true, supportFetchAPI: true, stream: true } }]);

let win: BrowserWindow | null = null;

function send(channel: string, payload: unknown) {
  win?.webContents.send(channel, payload);
}

async function pushState() {
  send('state', await workspaceState());
}

function safeTasksPath(rel: string): string {
  const tasks = requireTasks();
  const abs = normalize(isAbsolute(rel) ? rel : join(tasks, rel));
  const r = relative(join(tasks, '..'), abs);
  if (r.startsWith('..') || isAbsolute(r)) throw new Error('Path outside the workspace');
  return abs;
}

function registerProtocol() {
  // studio://file/<Tasks-relative path>  — page previews, PDFs and page HTML (with ?edit=1 the editor is injected)
  protocol.handle('studio', async (req) => {
    const url = new URL(req.url);
    try {
      const rel = decodeURIComponent(url.pathname.replace(/^\/+/, ''));
      const abs = safeTasksPath(rel);
      if (!existsSync(abs)) return new Response('not found', { status: 404 });
      if (url.searchParams.has('edit') && extname(abs) === '.html') {
        let html = readFileSync(abs, 'utf8');
        const tag = `<script>${EDITOR_SCRIPT}</script>`;
        html = /<\/head>/i.test(html) ? html.replace(/<\/head>/i, `${tag}</head>`) : tag + html;
        return new Response(html, { headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' } });
      }
      const res = await net.fetch(pathToFileURL(abs).toString());
      const headers = new Headers(res.headers);
      headers.set('cache-control', 'no-store');
      return new Response(res.body, { status: res.status, headers });
    } catch (e) {
      return new Response(String(e), { status: 400 });
    }
  });
}

function pagePaths(chapter: string, page: string) {
  return {
    dir: `PdfSheetsGenTask/${chapter}/${page}`,
    plan: `PdfSheetsGenTask/${chapter}/pages.json`,
  };
}

function planEntry(chapter: string, page: string): Record<string, unknown> | null {
  try {
    const plan = JSON.parse(readFileSync(join(requireTasks(), pagePaths(chapter, page).plan), 'utf8'));
    return plan.pages?.find((p: { page: string }) => p.page === page) ?? null;
  } catch {
    return null;
  }
}

/** Map an <img src> on a page back to the image item that made it (pages.json art.item / spot art ids). */
function imageItem(chapter: string, page: string, src: string) {
  const name = basename(src).replace(/\.[^.]+$/, '');
  const entry = planEntry(chapter, page);
  const ids = new Set<string>();
  const walk = (v: unknown) => {
    if (Array.isArray(v)) v.forEach(walk);
    else if (v && typeof v === 'object') {
      const o = v as Record<string, unknown>;
      for (const k of ['item', 'id']) if (typeof o[k] === 'string') {
        const id = o[k] as string;
        const srcBase = typeof o.src === 'string' ? basename(o.src as string).replace(/\.[^.]+$/, '') : '';
        if (id === name || srcBase === name) ids.add(id);
      }
      Object.values(o).forEach(walk);
    }
  };
  walk(entry);
  return { name, item: [...ids][0] ?? null, file: `${pagePaths(chapter, page).dir}/${src}` };
}

function ipc() {
  const h = (ch: string, fn: (...a: any[]) => unknown) => ipcMain.handle(ch, (_e, ...a) => fn(...a));

  h('state:get', () => workspaceState());
  h('settings:get', () => getSettings());
  h('settings:save', (patch: Partial<Settings>) => {
    const s = saveSettings(patch);
    watchWorkspace(pushState);
    pushState();
    return s;
  });
  h('settings:pickRepo', async () => {
    const r = await dialog.showOpenDialog(win!, { title: 'Choose the ChandRush repo folder (contains Tasks/)', properties: ['openDirectory'] });
    if (r.canceled || !r.filePaths[0]) return null;
    let repo = r.filePaths[0];
    if (basename(repo) === 'Tasks' && existsSync(join(repo, 'CLAUDE.md'))) repo = join(repo, '..');
    const s = saveSettings({ repo });
    watchWorkspace(pushState);
    pushState();
    return s;
  });
  h('doctor:run', () => runDoctor());

  // files
  h('file:read', (rel: string) => {
    try {
      return readFileSync(safeTasksPath(rel), 'utf8');
    } catch {
      return null;
    }
  });
  h('file:open', (rel: string) => shell.openPath(safeTasksPath(rel)));
  h('file:reveal', (rel: string) => shell.showItemInFolder(safeTasksPath(rel)));
  h('git:diff', async (rels: string[]) => (await runCmd('git', ['diff', '--', ...rels], requireTasks())).out);

  // pages
  h('page:plan', (chapter: string, page: string) => planEntry(chapter, page));
  h('page:imageItem', (chapter: string, page: string, src: string) => imageItem(chapter, page, src));
  h('page:render', async (chapter: string, page: string) => {
    const r = await runPipeline('pagekit.py', ['render', pagePaths(chapter, page).dir], `${chapter}/${page}`);
    pushState();
    return r;
  });
  h('page:saveInline', async (chapter: string, page: string, edits: InlineEdit[]): Promise<InlineSaveResult> => {
    const p = pagePaths(chapter, page);
    const file = join(requireTasks(), p.dir, 'index.html');
    const ap = applyEditsToFile(file, edits);
    const render = ap.applied ? await runPipeline('pagekit.py', ['render', p.dir], `${chapter}/${page}`) : { code: 0, out: 'nothing changed' };
    const textcheck = ap.applied ? await runPipeline('textcheck.py', ['page', p.dir, p.plan], `${chapter}/${page}`) : { code: 0, out: '' };
    if (ap.applied) {
      updatePage(chapter, page, { edited: new Date().toISOString(), ...(ap.mathChanged ? { math: undefined } : {}) });
      const words = edits.map((e) => `${e.oldText.trim().slice(0, 80)} ⇒ ${e.newText.trim().slice(0, 80)}`).join(' | ');
      logFeedback(`${chapter} ${page}`, 'inline edit', words, textcheck.code === 0 ? 'edited in Studio' : 'edited in Studio · author override (text differs from manuscript)');
    }
    pushState();
    return { applied: ap.applied, skipped: ap.skipped, render, textcheck, mathChanged: ap.mathChanged };
  });

  // chapters
  h('upload:pick', async () => {
    const r = await dialog.showOpenDialog(win!, {
      title: 'Choose the chapter manuscript, location register and reference images',
      properties: ['openFile', 'multiSelections'],
      filters: [{ name: 'Manuscript / register / images', extensions: ['docx', 'jpg', 'jpeg', 'png', 'webp'] }],
    });
    return r.canceled ? [] : r.filePaths;
  });
  h('upload:chapter', async (folder: string, files: string[]) => {
    const r = await uploadChapter(folder, files);
    pushState();
    return r;
  });
  h('chapter:prep', async (chapter: string) => {
    const ref = referenceChapters(requireTasks()).get(chapter);
    if (!ref?.manuscript) return [{ code: 1, out: `No manuscript found for ${chapter} in Reference/` }];
    const r = await prepChapter(chapter, ref.manuscript, ref.register);
    pushState();
    return r;
  });

  // review
  h('review:decide', (chapter: string, decisions: agent.Decision[], gate?: { sessionId: string; gateId: string }) => {
    const r = agent.review(chapter, decisions, gate);
    pushState();
    return r;
  });

  // agent sessions
  h('agent:list', () => ({ sessions: agent.listSessions(), runs: agent.listRuns() }));
  h('agent:get', (id: string) => agent.getSession(id));
  h('agent:create', (kind: 'desk' | 'quick', title: string, prompt: string, chapter?: string) => agent.createSession(kind, title, prompt, chapter));
  h('agent:send', (id: string, text: string) => agent.sendMessage(id, text));
  h('agent:desk', (chapter: string | undefined, text: string) => agent.desk(chapter, text));
  h('agent:interrupt', (id: string) => agent.interrupt(id));
  h('agent:stopTask', (id: string, taskId: string) => agent.stopTask(id, taskId));
  h('agent:close', (id: string) => agent.closeSession(id));
  h('agent:permission', (id: string, permId: string, allow: boolean, msg?: string) => agent.answerPermission(id, permId, allow, msg));
  h('agent:gateText', (id: string, gateId: string, text: string) => agent.answerGateText(id, gateId, text));
  h('run:start', (chapter: string, action: 'plan' | 'run' | 'sample', pages: string[], chunkSize: number, sampleKind?: string) => agent.startRun(chapter, action, pages, chunkSize, sampleKind));
  h('run:control', (id: string, action: 'pause' | 'resume' | 'stop' | 'next') => agent.controlRun(id, action));
  h('shell:external', (url: string) => /^https:\/\//.test(url) && shell.openExternal(url));
}

function createWindow() {
  win = new BrowserWindow({
    width: 1500,
    height: 920,
    minWidth: 1100,
    minHeight: 700,
    title: 'ChandRush Studio',
    backgroundColor: '#14110f',
    webPreferences: { preload: join(here, '../preload/index.mjs'), sandbox: false, contextIsolation: true },
  });
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (/^https:\/\//.test(url)) shell.openExternal(url);
    return { action: 'deny' };
  });
  // Debug/verification: STUDIO_SHOT=/path/shot.png captures the window after load (STUDIO_SHOT_JS runs first), then quits.
  const shot = process.env.STUDIO_SHOT;
  if (shot) {
    win.webContents.once('did-finish-load', async () => {
      await new Promise((r) => setTimeout(r, 2500));
      if (process.env.STUDIO_SHOT_JS) {
        await win!.webContents.executeJavaScript(process.env.STUDIO_SHOT_JS).catch((e) => console.error('shot js', e));
        await new Promise((r) => setTimeout(r, Number(process.env.STUDIO_SHOT_WAIT ?? 2500)));
      }
      const img = await win!.webContents.capturePage();
      writeFileSync(shot, img.toPNG());
      app.quit();
    });
  }
  if (process.env.ELECTRON_RENDERER_URL) win.loadURL(process.env.ELECTRON_RENDERER_URL);
  else win.loadFile(join(here, '../renderer/index.html'));
}

app.whenReady().then(() => {
  registerProtocol();
  agent.setEmitter((e) => send('agent', e));
  agent.loadSessions();
  ipc();
  createWindow();
  if (tasksDir()) watchWorkspace(pushState);
});

app.on('window-all-closed', () => {
  agent.closeAll();
  app.quit();
});
