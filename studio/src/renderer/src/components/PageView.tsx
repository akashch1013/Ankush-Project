import { useEffect, useRef, useState } from 'react';
import type { ChapterState, InlineEdit, InlineSaveResult } from '@shared/types';
import { api, fileUrl } from '../api';
import { StageChip } from './Board';

type Tab = 'preview' | 'text' | 'image' | 'plan' | 'source';
const PAGE_W = 1152; // 12 in at 96 px/in
const PAGE_H = 864;

function useFit(ref: React.RefObject<HTMLDivElement | null>) {
  const [scale, setScale] = useState(0.5);
  useEffect(() => {
    if (!ref.current) return;
    const ro = new ResizeObserver(([e]) => setScale(Math.min(e.contentRect.width / PAGE_W, e.contentRect.height / PAGE_H)));
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, [ref]);
  return scale;
}

export function PageView({ chapter, page, back, openSession }: { chapter: ChapterState; page: string; back: () => void; openSession: (id: string) => void }) {
  const p = chapter.pages.find((x) => x.page === page);
  const [tab, setTab] = useState<Tab>(p?.preview ? 'preview' : 'source');
  const [plan, setPlan] = useState<Record<string, unknown> | null>(null);
  const [src, setSrc] = useState<string | null>(null);
  const [note, setNote] = useState('');
  const [fix, setFix] = useState('');
  const [msg, setMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  // inline editor state
  const [edits, setEdits] = useState<Record<string, InlineEdit & { math: boolean }>>({});
  const [saveResult, setSaveResult] = useState<InlineSaveResult | null>(null);
  const [img, setImg] = useState<{ name: string; item: string | null; file: string } | null>(null);
  const [imgPrompt, setImgPrompt] = useState('');
  const [frameKey, setFrameKey] = useState(0);
  const frame = useRef<HTMLIFrameElement>(null);
  const box = useRef<HTMLDivElement>(null);
  const scale = useFit(box);

  useEffect(() => {
    api['page:plan'](chapter.id, page).then(setPlan);
    api['file:read'](`PdfSheetsGenTask/${chapter.id}/src/${page}.txt`).then(setSrc);
    setEdits({});
    setSaveResult(null);
    setImg(null);
    setMsg(null);
  }, [chapter.id, page]);

  useEffect(() => {
    const onMsg = async (e: MessageEvent) => {
      const d = e.data;
      if (!d?.studio) return;
      if (d.type === 'ready') frame.current?.contentWindow?.postMessage({ type: 'mode', mode: tab === 'text' ? 'text' : tab === 'image' ? 'image' : 'view' }, '*');
      if (d.type === 'edit') {
        setEdits((cur) => {
          const n = { ...cur };
          if (d.changed) n[d.key] = { ...d.edit, math: d.math };
          else delete n[d.key];
          return n;
        });
      }
      if (d.type === 'image') setImg(await api['page:imageItem'](chapter.id, page, d.src));
    };
    window.addEventListener('message', onMsg);
    return () => window.removeEventListener('message', onMsg);
  }, [tab, chapter.id, page]);

  useEffect(() => {
    frame.current?.contentWindow?.postMessage({ type: 'mode', mode: tab === 'text' ? 'text' : tab === 'image' ? 'image' : 'view' }, '*');
  }, [tab]);

  if (!p) return <div className="empty">Page {page} not found.</div>;

  const toDesk = async (text: string, label: string) => {
    setBusy(true);
    const s = await api['agent:desk'](chapter.id, text);
    setBusy(false);
    setMsg(`${label} → sent to ${s.title}.`);
    openSession(s.id);
  };

  const decide = async (status: 'approved' | 'changes') => {
    if (status === 'changes' && !note.trim()) return setMsg('Write what should change first.');
    setBusy(true);
    const r = await api['review:decide'](chapter.id, [{ page, status, note: note.trim() || undefined }]);
    setBusy(false);
    setNote('');
    setMsg(status === 'approved' ? `Approved${r.routed === 'gate' ? ' (the waiting agent was told)' : ''}.` : `Changes recorded and sent to the ${r.routed === 'gate' ? 'waiting run' : 'chapter desk'}.`);
    if (r.sessionId && status === 'changes') openSession(r.sessionId);
  };

  const saveInline = async () => {
    setBusy(true);
    setMsg('Saving, rendering and checking the text…');
    const list = Object.values(edits).map(({ math: _m, ...e }) => e);
    const r = await api['page:saveInline'](chapter.id, page, list);
    setSaveResult(r);
    setEdits({});
    setBusy(false);
    setMsg(`${r.applied} edit(s) saved${r.skipped.length ? `, ${r.skipped.length} skipped` : ''}. Render ${r.render.code === 0 ? 'OK' : 'FAILED'} · textcheck ${r.textcheck.code === 0 ? 'OK' : 'differs from manuscript'}.`);
    setFrameKey((k) => k + 1);
  };

  const rerender = async () => {
    setBusy(true);
    setMsg('Rendering…');
    const r = await api['page:render'](chapter.id, page);
    setBusy(false);
    setMsg(r.code === 0 ? 'Rendered.' : `Render failed:\n${r.out.slice(-800)}`);
    setFrameKey((k) => k + 1);
  };

  const editing = tab === 'text' || tab === 'image';
  const editCount = Object.keys(edits).length;
  const mathEdits = Object.values(edits).some((e) => e.math);

  return (
    <div className="pageview">
      <div className="pv-main">
        <div className="tabs">
          <button className="link" onClick={back}>
            ← Board
          </button>
          {p.preview && (
            <button className={tab === 'preview' ? 'on' : ''} onClick={() => setTab('preview')}>
              Preview
            </button>
          )}
          {p.built && (
            <>
              <button className={tab === 'text' ? 'on' : ''} onClick={() => setTab('text')}>
                Edit text
              </button>
              <button className={tab === 'image' ? 'on' : ''} onClick={() => setTab('image')}>
                Edit image
              </button>
            </>
          )}
          <button className={tab === 'plan' ? 'on' : ''} onClick={() => setTab('plan')}>
            Plan
          </button>
          <button className={tab === 'source' ? 'on' : ''} onClick={() => setTab('source')}>
            Manuscript
          </button>
          <span className="grow" />
          {p.pdf && <button onClick={() => api['file:open'](p.pdf!)}>Open PDF</button>}
          {p.built && <button onClick={() => api['file:reveal'](`PdfSheetsGenTask/${chapter.id}/${page}/index.html`)}>Show folder</button>}
        </div>

        <div className="stagebox" ref={box}>
          {tab === 'preview' && p.preview && <img className="fitimg" src={fileUrl(p.preview, p.previewMtime)} alt={page} />}
          {editing && (
            <div className="framewrap" style={{ width: PAGE_W * scale, height: PAGE_H * scale }}>
              <iframe
                key={frameKey}
                ref={frame}
                title="page editor"
                src={`${fileUrl(`PdfSheetsGenTask/${chapter.id}/${page}/index.html`)}?edit=1&t=${frameKey}`}
                style={{ width: PAGE_W, height: PAGE_H, transform: `scale(${scale})` }}
              />
            </div>
          )}
          {tab === 'plan' && <pre className="code">{plan ? JSON.stringify(plan, null, 2) : 'Not planned yet.'}</pre>}
          {tab === 'source' && <pre className="code wrap">{src ?? 'No source split for this page yet (prepare the chapter sources).'}</pre>}
        </div>
        {tab === 'text' && (
          <div className="hint">
            Click any bubble, caption or teaching text to edit it. Press Esc or click away to finish. Orange = changed, red outline = contains maths. SVG
            diagrams are edited through the agent.
          </div>
        )}
        {tab === 'image' && <div className="hint">Click an image on the page to pick it, then describe the change in the panel on the right.</div>}
      </div>

      <div className="pv-side">
        <div className="row gap">
          <h2>
            {chapter.id} {page}
          </h2>
          <StageChip stage={p.stage} />
        </div>
        {p.title && <div className="muted">{p.title}</div>}
        <div className="facts small">
          {p.math && <div>Maths: {p.math}</div>}
          {p.review.edited && <div className="warn">Text edited in Studio {new Date(p.review.edited).toLocaleString()}{!p.math ? ' · maths needs a re-check' : ''}</div>}
          {p.newArt > 0 && <div>{p.newArt} panel(s) with new art</div>}
          {p.review.note && <div>Last note: “{p.review.note}”</div>}
        </div>
        {msg && <pre className="msg">{msg}</pre>}

        {tab === 'text' && (
          <section className="box">
            <h3>Inline text edit</h3>
            <div className="small muted">{editCount ? `${editCount} unsaved change(s)` : 'No changes yet.'}</div>
            {Object.values(edits).map((e, i) => (
              <div key={i} className="editrow small">
                <s>{e.oldText.trim().slice(0, 90)}</s>
                <div>{e.newText.trim().slice(0, 90)}</div>
                {e.math && <div className="warn">contains maths: math-checker should re-run</div>}
              </div>
            ))}
            <div className="row gap">
              <button className="primary" disabled={!editCount || busy} onClick={saveInline}>
                Save &amp; render
              </button>
              <button disabled={!editCount || busy} onClick={() => (setEdits({}), setFrameKey((k) => k + 1))}>
                Discard
              </button>
            </div>
            {mathEdits && <div className="small warn">Maths edits run mathcheck on render. The independent math-checker can be run below.</div>}
            {saveResult && saveResult.textcheck.code !== 0 && <pre className="errorbox small">{saveResult.textcheck.out.slice(-600)}</pre>}
            {saveResult && saveResult.render.code !== 0 && <pre className="errorbox small">{saveResult.render.out.slice(-600)}</pre>}
          </section>
        )}

        {tab === 'image' && (
          <section className="box">
            <h3>Edit an image by prompt</h3>
            {img ? (
              <div className="small">
                Selected: <b>{img.item ?? img.name}</b> {img.item ? '' : '(no image item found in the plan: the agent will work out its source)'}
              </div>
            ) : (
              <div className="small muted">Click an image on the page.</div>
            )}
            <textarea rows={3} placeholder="e.g. Tez should hold the brass lantern in his left hand; make the sky deeper indigo" value={imgPrompt} onChange={(e) => setImgPrompt(e.target.value)} />
            <button
              className="primary"
              disabled={!img || !imgPrompt.trim() || busy}
              onClick={() => {
                const what = img!.item ? `image ${img!.item}` : `image ${img!.file}`;
                toDesk(`/comic-master fix ${chapter.id} ${page} "${what}: ${imgPrompt.trim().replace(/"/g, "'")}"`, 'Image fix');
                setImgPrompt('');
              }}
            >
              Send image fix (batch; you approve the spend)
            </button>
          </section>
        )}

        <section className="box">
          <h3>Review</h3>
          <textarea rows={3} placeholder="Note for the agent (required for changes)…" value={note} onChange={(e) => setNote(e.target.value)} />
          <div className="row gap">
            <button className="ok" disabled={busy || !p.preview} onClick={() => decide('approved')}>
              Approve
            </button>
            <button className="bad" disabled={busy} onClick={() => decide('changes')}>
              Request changes
            </button>
          </div>
        </section>

        <section className="box">
          <h3>Ask the agent</h3>
          <textarea rows={3} placeholder="e.g. move Ahana's bubble left so it doesn't cover the dial; colour the answer card teal" value={fix} onChange={(e) => setFix(e.target.value)} />
          <div className="row gap wrap">
            <button
              className="primary"
              disabled={!fix.trim() || busy}
              onClick={() => {
                toDesk(`/comic-master fix ${chapter.id} ${page} "${fix.trim().replace(/"/g, "'")}"`, 'Fix');
                setFix('');
              }}
            >
              Send fix
            </button>
            {!p.built && (
              <button disabled={busy} onClick={() => toDesk(`/comic-master page ${chapter.id} ${page}`, 'Build')}>
                Build this page
              </button>
            )}
            {p.built && (
              <button disabled={busy} onClick={() => toDesk(`Spawn math-checker on ${chapter.id} ${page} (the author may have edited it in Studio). Report the result with mcp__studio__report_stage and fix any FAIL with page-builder.`, 'Math check')}>
                Run math check
              </button>
            )}
            {p.built && (
              <button disabled={busy} onClick={rerender}>
                Re-render (free)
              </button>
            )}
          </div>
        </section>

        {!!p.review.history?.length && (
          <section className="box">
            <h3>History</h3>
            {[...p.review.history].reverse().map((h, i) => (
              <div key={i} className="small">
                <span className={`chip st-${h.status === 'none' ? 'source' : h.status}`}>{h.status}</span> {new Date(h.at).toLocaleString()} {h.note ? `· ${h.note}` : ''}
              </div>
            ))}
          </section>
        )}
      </div>
    </div>
  );
}
