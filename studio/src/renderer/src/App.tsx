import { useEffect, useMemo, useState } from 'react';
import { useStudio, fmtUsd } from './store';
import { Sidebar, type View } from './components/Sidebar';
import { Board } from './components/Board';
import { PageView } from './components/PageView';
import { AgentPanel } from './components/AgentPanel';
import { RunWizard } from './components/RunWizard';
import { RulesView } from './components/RulesView';
import { DoctorView } from './components/DoctorView';
import { SettingsView } from './components/SettingsView';
import { Setup } from './components/Setup';
import { api } from './api';

export function App() {
  const studio = useStudio();
  const { ws, sessions, runs } = studio;
  const [view, setView] = useState<View>('board');
  const [chapterId, setChapterId] = useState<string | null>(null);
  const [page, setPage] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [wizard, setWizard] = useState(false);
  const [agentOpen, setAgentOpen] = useState(true);
  const [setup, setSetup] = useState<boolean | null>(null);

  useEffect(() => {
    api['settings:get']().then((s) => setSetup(!s.setupDone));
  }, []);

  const chapter = useMemo(() => ws?.chapters.find((c) => c.id === chapterId) ?? null, [ws, chapterId]);

  useEffect(() => {
    if (!chapterId && ws?.chapters.length) setChapterId(ws.chapters.find((c) => c.hasPlan)?.id ?? ws.chapters[0].id);
  }, [ws, chapterId]);

  useEffect(() => {
    if (!ws) return;
    if (!ws.tasks) setView('settings');
  }, [ws?.tasks]);

  // Follow the newest session the app starts, so the author sees the agent pick up the work.
  const [lastCount, setLastCount] = useState(0);
  useEffect(() => {
    if (sessions.length > lastCount && lastCount > 0) setSessionId(sessions[0].id);
    setLastCount(sessions.length);
  }, [sessions.length]);

  const waiting = sessions.filter((s) => s.status === 'waiting').length;
  const running = sessions.filter((s) => s.status === 'running' || s.status === 'starting').length;
  const tokenCost = sessions.reduce((a, s) => a + s.costUsd, 0);

  const openSession = (id: string) => {
    setSessionId(id);
    setAgentOpen(true);
  };

  if (setup === null) return null;
  if (setup) return <Setup done={() => { setSetup(false); studio.refresh(); }} />;

  return (
    <div className={`app ${agentOpen ? 'with-agent' : ''}`}>
      <Sidebar
        ws={ws}
        view={view}
        setView={(v) => {
          setView(v);
          if (v === 'board') setPage(null);
        }}
        chapterId={chapterId}
        setChapter={(id) => {
          setChapterId(id);
          setPage(null);
          setView('board');
        }}
        sessions={sessions}
        runs={runs}
        sessionId={sessionId}
        openSession={openSession}
        newRun={() => setWizard(true)}
      />
      <main className="center">
        <header className="topbar">
          <div className="crumbs">
            {view === 'board' && chapter && (
              <>
                <button className="link" onClick={() => setPage(null)}>
                  {chapter.id}
                  {chapter.label ? ` · ${chapter.label}` : ''}
                </button>
                {page && <span> / {page}</span>}
              </>
            )}
            {view !== 'board' && <span className="cap">{view}</span>}
          </div>
          <div className="topstats">
            {running > 0 && <span className="pill run">{running} running</span>}
            {waiting > 0 && <span className="pill wait">{waiting} waiting for you</span>}
            <span className="muted" title="Agent tokens (estimate) + image batches (usage-all.tsv)">
              agents {fmtUsd(tokenCost)} · images {fmtUsd(ws?.imageCostUsd ?? 0)}
            </span>
            <button onClick={() => setWizard(true)} className="primary">
              New run
            </button>
            <button onClick={() => setAgentOpen((o) => !o)} title="Toggle the agent panel">
              {agentOpen ? 'Hide agents' : 'Agents'}
            </button>
          </div>
        </header>
        <div className="content">
          {view === 'board' && chapter && !page && <Board chapter={chapter} openPage={setPage} onPrep={studio.refresh} />}
          {view === 'board' && chapter && page && <PageView chapter={chapter} page={page} back={() => setPage(null)} openSession={openSession} />}
          {view === 'board' && !chapter && <div className="empty">No chapters yet. Use “New run” → upload a chapter.</div>}
          {view === 'rules' && <RulesView openSession={openSession} />}
          {view === 'doctor' && <DoctorView />}
          {view === 'settings' && <SettingsView />}
        </div>
      </main>
      {agentOpen && <AgentPanel studio={studio} sessionId={sessionId} setSessionId={setSessionId} chapter={chapter?.id} />}
      {wizard && ws && (
        <RunWizard
          ws={ws}
          initialChapter={chapterId}
          close={() => setWizard(false)}
          started={(sid) => {
            setWizard(false);
            if (sid) openSession(sid);
          }}
        />
      )}
    </div>
  );
}
