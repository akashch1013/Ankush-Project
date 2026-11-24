import { useEffect, useMemo, useRef, useState } from 'react';
import type { SessionDetail, TaskInfo, TimelineItem } from '@shared/types';
import { api } from '../api';
import { fmtUsd, type useStudio } from '../store';
import { fmtTokens, rateLimitActive, rateLimitText, tokenSum } from '@shared/usage';

type Studio = ReturnType<typeof useStudio>;

function toolSummary(name: string, input: unknown): string {
  const i = (input ?? {}) as Record<string, unknown>;
  if (name === 'Bash') return String(i.command ?? '');
  if (name === 'Read' || name === 'Write' || name === 'Edit') return String(i.file_path ?? '');
  if (name === 'Agent' || name === 'Task') return `${i.subagent_type ?? 'agent'}: ${i.description ?? ''}`;
  if (name === 'Skill') return String(i.skill ?? i.name ?? '');
  if (name === 'Grep' || name === 'Glob') return String(i.pattern ?? '');
  if (name.startsWith('mcp__studio__')) return JSON.stringify(i);
  const s = JSON.stringify(i);
  return s.length > 160 ? s.slice(0, 160) + '…' : s;
}

function ToolCard({ it }: { it: TimelineItem }) {
  const [open, setOpen] = useState(false);
  const t = it.tool!;
  const pending = t.output === undefined;
  return (
    <div className={`tool ${t.isError ? 'err' : ''}`}>
      <button className="toolhead" onClick={() => setOpen((o) => !o)}>
        <span className={`dot ${pending ? 'run' : t.isError ? 'err' : 'idle'}`} />
        <b>{t.name.replace(/^mcp__studio__/, 'studio · ')}</b>
        <span className="ellipsis muted">{toolSummary(t.name, t.input)}</span>
      </button>
      {open && (
        <div className="toolbody">
          <pre>{typeof t.input === 'string' ? t.input : JSON.stringify(t.input, null, 2)}</pre>
          {t.output !== undefined && <pre className="out">{t.output}</pre>}
        </div>
      )}
    </div>
  );
}

function PermissionCard({ it, sessionId }: { it: TimelineItem; sessionId: string }) {
  const p = it.permission!;
  const [why, setWhy] = useState('');
  const input = p.input as Record<string, unknown>;
  return (
    <div className={`card-inline ${p.kind === 'spend' ? 'spend' : 'perm'} ${p.state}`}>
      <div className="row gap">
        <b>{p.kind === 'spend' ? '💰 Spend approval' : 'Permission'}</b>
        <span className="muted">{p.tool}</span>
        <span className="grow" />
        {p.state !== 'open' && <span className="chip">{p.state}</span>}
      </div>
      <pre>{p.tool === 'Bash' ? String(input.command) : JSON.stringify(input, null, 2).slice(0, 1500)}</pre>
      {p.reason && <pre className="small muted">{p.reason}</pre>}
      {p.state === 'open' && (
        <div className="row gap">
          <button className="ok" onClick={() => api['agent:permission'](sessionId, p.id, true)}>
            Allow
          </button>
          <input placeholder="why not (optional, the agent sees it)" value={why} onChange={(e) => setWhy(e.target.value)} />
          <button className="bad" onClick={() => api['agent:permission'](sessionId, p.id, false, why || undefined)}>
            Deny
          </button>
        </div>
      )}
    </div>
  );
}

function GateCard({ it, session }: { it: TimelineItem; session: SessionDetail }) {
  const g = it.gate!;
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [text, setText] = useState('');
  const decideAll = (status: 'approved' | 'changes') => {
    const ds = g.pages.map((page) => ({ page, status: notes[page]?.trim() ? ('changes' as const) : status, note: notes[page]?.trim() || undefined }));
    api['review:decide'](g.chapter, ds, { sessionId: session.id, gateId: g.id });
  };
  return (
    <div className={`card-inline gate ${g.state}`}>
      <div className="row gap">
        <b>🔔 Review gate · {g.gate}</b>
        <span className="muted">
          {g.chapter} {g.pages.join(', ')}
        </span>
        <span className="grow" />
        {g.state !== 'open' && <span className="chip">answered</span>}
      </div>
      <div className="small">{g.summary}</div>
      {g.state === 'open' ? (
        g.pages.length ? (
          <>
            {g.pages.map((page) => (
              <div key={page} className="row gap small">
                <b>{page}</b>
                <input placeholder="leave empty to approve, or write the change" value={notes[page] ?? ''} onChange={(e) => setNotes({ ...notes, [page]: e.target.value })} />
              </div>
            ))}
            <div className="row gap">
              <button className="ok" onClick={() => decideAll('approved')}>
                Send review
              </button>
              <span className="muted small">Open the pages on the board to look at them first.</span>
            </div>
          </>
        ) : (
          <div className="row gap">
            <input className="grow" placeholder="Your answer" value={text} onChange={(e) => setText(e.target.value)} />
            <button className="ok" disabled={!text.trim()} onClick={() => api['agent:gateText'](session.id, g.id, text)}>
              Answer
            </button>
          </div>
        )
      ) : (
        g.answer && <div className="small muted">↳ {g.answer}</div>
      )}
    </div>
  );
}

function Item({ it, session, showSub }: { it: TimelineItem; session: SessionDetail; showSub: boolean }) {
  if (it.parent && !showSub && it.type !== 'permission') return null;
  const sub = it.parent ? 'sub' : '';
  switch (it.type) {
    case 'user':
      return <div className="msg-user">{it.text}</div>;
    case 'text':
      return <div className={`msg-text ${sub}`}>{it.text}</div>;
    case 'thinking':
      return <details className={`msg-think ${sub}`}><summary>thinking</summary>{it.text}</details>;
    case 'tool':
      return <div className={sub}><ToolCard it={it} /></div>;
    case 'permission':
      return <PermissionCard it={it} sessionId={session.id} />;
    case 'gate':
      return <GateCard it={it} session={session} />;
    case 'result':
      return <div className="msg-result">{it.text}</div>;
    case 'error':
      return <div className="msg-error">{it.text}</div>;
    default:
      return <div className="msg-system">{it.text}</div>;
  }
}

function TaskTree({ tasks, sessionId }: { tasks: TaskInfo[]; sessionId: string }) {
  if (!tasks.length) return null;
  const running = tasks.filter((t) => t.status === 'running');
  const done = tasks.filter((t) => t.status !== 'running').slice(-6);
  return (
    <div className="tasks">
      <div className="small muted">master → subagents</div>
      {[...running, ...done].map((t) => (
        <div key={t.taskId} className={`task ${t.status}`}>
          <span className={`dot ${t.status === 'running' ? 'run' : t.status === 'completed' ? 'idle' : 'err'}`} />
          <b>{t.agent ?? 'agent'}</b>
          <span className="ellipsis grow muted">{t.summary ?? t.description}</span>
          <span className="small muted">
            {t.tokens != null ? `${fmtTokens(t.tokens)} tok · ` : ''}
            {t.toolUses ?? 0} tools{t.lastTool && t.status === 'running' ? ` · ${t.lastTool}` : ''}
          </span>
          {t.status === 'running' && (
            <button className="tiny" onClick={() => api['agent:stopTask'](sessionId, t.taskId)} title="Stop this subagent">
              ■
            </button>
          )}
        </div>
      ))}
    </div>
  );
}

export function AgentPanel({ studio, sessionId, setSessionId, chapter }: { studio: Studio; sessionId: string | null; setSessionId: (id: string | null) => void; chapter?: string }) {
  const { sessions, details, loadDetail } = studio;
  const [text, setText] = useState('');
  const [showSub, setShowSub] = useState(false);
  const scroller = useRef<HTMLDivElement>(null);
  const info = sessions.find((s) => s.id === sessionId) ?? null;
  const d = sessionId ? details[sessionId] : undefined;

  useEffect(() => {
    if (sessionId) loadDetail(sessionId);
  }, [sessionId, loadDetail]);

  const timeline = d?.timeline ?? [];
  useEffect(() => {
    const el = scroller.current;
    if (el && el.scrollHeight - el.scrollTop - el.clientHeight < 300) el.scrollTop = el.scrollHeight;
  }, [timeline.length]);

  const openAsks = useMemo(() => timeline.filter((t) => (t.permission?.state === 'open') || (t.gate?.state === 'open')).length, [timeline]);

  const send = async () => {
    const t = text.trim();
    if (!t) return;
    setText('');
    if (info) await api['agent:send'](info.id, t);
    else {
      const s = await api['agent:desk'](chapter, t);
      setSessionId(s.id);
    }
  };

  const busy = info && (info.status === 'running' || info.status === 'starting' || info.status === 'waiting');

  return (
    <aside className="agent">
      <div className="agenthead">
        <select value={sessionId ?? ''} onChange={(e) => setSessionId(e.target.value || null)}>
          <option value="">+ new {chapter ?? ''} desk session</option>
          {sessions.map((s) => (
            <option key={s.id} value={s.id}>
              {s.status === 'waiting' ? '● ' : ''}
              {s.title} · {s.status}
            </option>
          ))}
        </select>
        {info && (
          <div className="row gap small">
            <span className={`dot ${info.status === 'running' || info.status === 'starting' ? 'run' : info.status === 'waiting' ? 'wait' : info.status === 'error' ? 'err' : 'idle'}`} />
            <span>{info.status}</span>
            <span className="muted">{info.model ?? ''}</span>
            <span className="muted">{fmtUsd(info.costUsd)}</span>
            {info.tokens && (
              <span
                className="muted"
                title={`input ${info.tokens.input.toLocaleString()} · cache read ${info.tokens.cacheRead.toLocaleString()} · cache write ${info.tokens.cacheWrite.toLocaleString()} · output ${info.tokens.output.toLocaleString()} (includes subagents)`}
              >
                {fmtTokens(tokenSum(info.tokens))} tok
              </span>
            )}
            <span className="grow" />
            <label className="muted">
              <input type="checkbox" checked={showSub} onChange={(e) => setShowSub(e.target.checked)} /> subagent steps
            </label>
            {busy && (
              <button className="bad tiny" onClick={() => api['agent:interrupt'](info.id)}>
                Stop
              </button>
            )}
          </div>
        )}
        {info && rateLimitActive(info.rateLimit) && <div className={`ratelimit ${info.rateLimit!.overage ? 'overage' : info.rateLimit!.status}`}>{rateLimitText(info.rateLimit!)}</div>}
        {d && <TaskTree tasks={d.tasks} sessionId={d.id} />}
      </div>

      <div className="timeline" ref={scroller}>
        {!info && (
          <div className="empty small">
            Type a request for the master agent, e.g. <i>status {chapter ?? 'CH01'}</i>, <i>make a text heavy sample</i>, or use <b>New run</b> for a batch of pages.
          </div>
        )}
        {d && timeline.map((it) => <Item key={it.id} it={it} session={d} showSub={showSub} />)}
        {info && !d && <div className="muted small">Loading…</div>}
      </div>

      {openAsks > 0 && <div className="asks">{openAsks} item(s) waiting for you above</div>}
      <div className="composer">
        <textarea
          rows={3}
          placeholder={info ? (info.status === 'running' ? 'Queue a message for the agent…' : 'Message the agent…') : `New ${chapter ?? ''} desk session: what should the master do?`}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) send();
          }}
        />
        <div className="row gap">
          <span className="muted small grow">Ctrl+Enter to send · /comic-master … commands work</span>
          <button className="primary" onClick={send} disabled={!text.trim()}>
            Send
          </button>
        </div>
      </div>
    </aside>
  );
}
