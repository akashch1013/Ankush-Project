import { useEffect, useMemo, useState } from 'react';
import type { RunAction, WorkspaceState } from '@shared/types';
import { api } from '../api';
import { StageChip } from './Board';

const KINDS = ['story', 'story+math', 'math-heavy', 'text-heavy', 'teaching'];

function parseRange(s: string): number[] {
  const out: number[] = [];
  for (const part of s.split(',').map((x) => x.trim()).filter(Boolean)) {
    const m = part.match(/^P?(\d+)\s*(?:-\s*P?(\d+))?$/i);
    if (!m) continue;
    const a = +m[1];
    const b = m[2] ? +m[2] : a;
    for (let i = Math.min(a, b); i <= Math.max(a, b); i++) out.push(i);
  }
  return out;
}

export function RunWizard({ ws, initialChapter, close, started }: { ws: WorkspaceState; initialChapter: string | null; close: () => void; started: (sessionId?: string) => void }) {
  const [mode, setMode] = useState<'existing' | 'upload'>(ws.chapters.length ? 'existing' : 'upload');
  const [chapterId, setChapterId] = useState(initialChapter ?? ws.chapters[0]?.id ?? '');
  const [action, setAction] = useState<RunAction>('run');
  const [kind, setKind] = useState('text-heavy');
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [range, setRange] = useState('');
  const [chunk, setChunk] = useState(20);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  // upload
  const [folder, setFolder] = useState('');
  const [files, setFiles] = useState<string[]>([]);
  const [uploadLog, setUploadLog] = useState<string[]>([]);

  useEffect(() => {
    api['settings:get']().then((s) => setChunk(s.chunkSize));
  }, []);

  const chapter = ws.chapters.find((c) => c.id === chapterId);
  const rows = chapter?.pages ?? [];

  useEffect(() => setSelected(new Set()), [chapterId]);

  const applyRange = () => {
    const nums = new Set(parseRange(range));
    setSelected(new Set(rows.filter((r) => nums.has(parseInt(r.page.slice(1), 10))).map((r) => r.page)));
  };

  const pages = useMemo(() => [...selected].sort(), [selected]);
  const chunks = Math.ceil(pages.length / Math.max(1, chunk));

  const doUpload = async () => {
    setBusy(true);
    setErr(null);
    const r = await api['upload:chapter'](folder, files);
    setBusy(false);
    setUploadLog(r.log);
    if (!r.ok) return setErr(r.error ?? 'Upload or source prep failed: see the log.');
    setChapterId(r.chapter!);
    setMode('existing');
  };

  const start = async () => {
    if (!chapter) return;
    if (action !== 'sample' && !pages.length) return setErr('Select at least one page.');
    setBusy(true);
    const run = await api['run:start'](chapter.id, action, action === 'sample' ? [] : pages, chunk, action === 'sample' ? kind : undefined);
    setBusy(false);
    started(run.sessionIds[0]);
  };

  const preview =
    action === 'sample'
      ? `/comic-master sample ${kind} ${chapterId}`
      : pages.length
        ? `${chunks} session(s) of ≤ ${chunk} pages · first: /comic-master ${action === 'plan' ? 'plan' : pages.length <= 5 ? 'page' : 'run'} ${chapterId} ${pages.slice(0, chunk)[0]}…${pages.slice(0, chunk).slice(-1)[0]}`
        : '';

  return (
    <div className="modal" onClick={close}>
      <div className="dialog" onClick={(e) => e.stopPropagation()}>
        <div className="row gap">
          <h2 className="grow">New run</h2>
          <button onClick={close}>✕</button>
        </div>
        <div className="tabs">
          <button className={mode === 'existing' ? 'on' : ''} onClick={() => setMode('existing')} disabled={!ws.chapters.length}>
            Existing chapter
          </button>
          <button className={mode === 'upload' ? 'on' : ''} onClick={() => setMode('upload')}>
            Upload a new chapter
          </button>
        </div>

        {mode === 'upload' && (
          <div className="col gap">
            <p className="small muted">
              Pick the panelized manuscript (<code>CHxx-PANELIZED-MANUSCRIPT-Vxx.docx</code>), the location register and any reference images. They are copied into a new{' '}
              <code>Tasks/Reference/&lt;folder&gt;/</code> (existing files are never overwritten), then the free setup prep runs and the setup agent prepares the chapter for the other agents.
            </p>
            <label>
              Folder name <input value={folder} placeholder="e.g. Chap4" onChange={(e) => setFolder(e.target.value)} />
            </label>
            <div
              className="drop"
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                setFiles((f) => [...new Set([...f, ...[...e.dataTransfer.files].map((x) => api.pathForFile(x))])]);
              }}
            >
              Drop files here or{' '}
              <button onClick={async () => {
                const picked = await api['upload:pick']();
                setFiles((f) => [...new Set([...f, ...picked])]);
              }}>
                choose files
              </button>
              {files.map((f) => (
                <div key={f} className="small">
                  {f.split(/[\\/]/).pop()}{' '}
                  <button className="tiny" onClick={() => setFiles(files.filter((x) => x !== f))}>
                    ✕
                  </button>
                </div>
              ))}
            </div>
            <button className="primary" disabled={busy || !folder.trim() || !files.length} onClick={doUpload}>
              {busy ? 'Copying and preparing…' : 'Upload and prepare'}
            </button>
            {uploadLog.length > 0 && <pre className="code small">{uploadLog.join('\n')}</pre>}
          </div>
        )}

        {mode === 'existing' && (
          <div className="col gap">
            <div className="row gap wrap">
              <label>
                Chapter{' '}
                <select value={chapterId} onChange={(e) => setChapterId(e.target.value)}>
                  {ws.chapters.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.id} {c.label ?? ''}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Action{' '}
                <select value={action} onChange={(e) => setAction(e.target.value as RunAction)}>
                  <option value="run">Full run (plan → art → pages → maths → review)</option>
                  <option value="plan">Plan only (pages.json, no images)</option>
                  <option value="sample">Sample page (picked by survey)</option>
                </select>
              </label>
              {action === 'sample' && (
                <label>
                  Kind{' '}
                  <select value={kind} onChange={(e) => setKind(e.target.value)}>
                    {KINDS.map((k) => (
                      <option key={k}>{k}</option>
                    ))}
                  </select>
                </label>
              )}
              {action !== 'sample' && (
                <label title="Pages per agent session. Each chunk starts a fresh master session (the skill recommends 20–25).">
                  Pages per session <input type="number" min={1} max={35} value={chunk} onChange={(e) => setChunk(+e.target.value || 20)} style={{ width: 60 }} />
                </label>
              )}
            </div>

            {chapter && !chapter.hasSrc && <div className="warn small">This chapter's sources aren't split yet. Close this and use “Prepare sources” on the board first, or the master will do it in the run.</div>}

            {action !== 'sample' && (
              <>
                <div className="row gap">
                  <input placeholder="Pages, e.g. 1-20, 25, 30-32" value={range} onChange={(e) => setRange(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && applyRange()} />
                  <button onClick={applyRange}>Select range</button>
                  <button onClick={() => setSelected(new Set(rows.filter((r) => !r.built).map((r) => r.page)))}>All not built</button>
                  <button onClick={() => setSelected(new Set())}>None</button>
                  <span className="muted small">{pages.length} selected</span>
                </div>
                <div className="pagetable">
                  <table>
                    <thead>
                      <tr>
                        <th />
                        <th>Page</th>
                        <th>Kind</th>
                        <th>Panels</th>
                        <th>Eq</th>
                        <th>Words</th>
                        <th>Stage</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((r) => (
                        <tr key={r.page} onClick={() => setSelected((s) => { const n = new Set(s); n.has(r.page) ? n.delete(r.page) : n.add(r.page); return n; })} className={selected.has(r.page) ? 'sel' : ''}>
                          <td>
                            <input type="checkbox" readOnly checked={selected.has(r.page)} />
                          </td>
                          <td>{r.page}</td>
                          <td>{r.survey?.kind ?? ''}</td>
                          <td>{r.survey?.panels ?? ''}</td>
                          <td>{r.survey?.equations ?? ''}</td>
                          <td>{r.survey?.words ?? ''}</td>
                          <td>
                            <StageChip stage={r.stage} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
            {preview && <div className="small muted">{preview}</div>}
            <div className="small muted">
              Gates still apply. A new chapter's first 2 panels and first finished page wait for your approval in the agent panel. Every paid image batch asks before it is submitted.
            </div>
            <div className="row gap">
              <button className="primary" disabled={busy || !chapter || (action !== 'sample' && !pages.length)} onClick={start}>
                Start
              </button>
            </div>
          </div>
        )}
        {err && <pre className="errorbox">{err}</pre>}
      </div>
    </div>
  );
}
