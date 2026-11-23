import type { RunInfo, SessionInfo, WorkspaceState } from '@shared/types';
import { ago, fmtUsd } from '../store';

export type View = 'board' | 'rules' | 'doctor' | 'settings';

const STATUS_DOT: Record<string, string> = { running: 'run', starting: 'run', waiting: 'wait', idle: 'idle', stopped: 'off', error: 'err' };

export function Sidebar(p: {
  ws: WorkspaceState | null;
  view: View;
  setView: (v: View) => void;
  chapterId: string | null;
  setChapter: (id: string) => void;
  sessions: SessionInfo[];
  runs: RunInfo[];
  sessionId: string | null;
  openSession: (id: string) => void;
  newRun: () => void;
}) {
  const activeRuns = p.runs.filter((r) => r.status === 'running' || r.status === 'paused');
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="moon">☾</span> ChandRush <b>Studio</b>
      </div>

      <div className="section">Chapters</div>
      {p.ws?.chapters.map((c) => {
        const done = c.counts.approved;
        const total = c.pages.length;
        const pend = c.counts.pending;
        return (
          <button key={c.id} className={`navitem ${p.view === 'board' && p.chapterId === c.id ? 'active' : ''}`} onClick={() => p.setChapter(c.id)}>
            <span className="grow">
              {c.id}
              <span className="muted small"> {c.hasPlan ? `${c.pages.filter((x) => x.planned).length} planned` : c.hasSrc ? 'source ready' : 'not prepared'}</span>
            </span>
            {pend > 0 && <span className="badge wait">{pend}</span>}
            <span className="muted small">
              {done}/{total}
            </span>
          </button>
        );
      })}

      {activeRuns.length > 0 && <div className="section">Runs</div>}
      {activeRuns.map((r) => (
        <button key={r.id} className="navitem" onClick={() => r.sessionIds[r.current] && p.openSession(r.sessionIds[r.current])}>
          <span className="grow">
            {r.chapter} {r.action}
            <span className="muted small">
              {' '}
              chunk {r.current + 1}/{r.chunks.length}
            </span>
          </span>
          <span className={`badge ${r.status === 'paused' ? 'off' : 'run'}`}>{r.status}</span>
        </button>
      ))}

      <div className="section">Sessions</div>
      <div className="sessions">
        {p.sessions.slice(0, 30).map((s) => (
          <button key={s.id} className={`navitem session ${p.sessionId === s.id ? 'active' : ''}`} onClick={() => p.openSession(s.id)} title={s.title}>
            <span className={`dot ${STATUS_DOT[s.status]}`} />
            <span className="grow ellipsis">{s.title}</span>
            <span className="muted small">{s.status === 'waiting' ? 'needs you' : ago(s.createdAt)}</span>
          </button>
        ))}
        {!p.sessions.length && <div className="muted small pad">No sessions yet.</div>}
      </div>

      <div className="bottomnav">
        <button className={`navitem ${p.view === 'rules' ? 'active' : ''}`} onClick={() => p.setView('rules')}>
          Rules &amp; feedback
        </button>
        <button className={`navitem ${p.view === 'doctor' ? 'active' : ''}`} onClick={() => p.setView('doctor')}>
          Doctor
        </button>
        <button className={`navitem ${p.view === 'settings' ? 'active' : ''}`} onClick={() => p.setView('settings')}>
          Settings
        </button>
        <div className="muted small pad">images so far {fmtUsd(p.ws?.imageCostUsd ?? 0)}</div>
      </div>
    </aside>
  );
}
