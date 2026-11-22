import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from './api';
import type { RunInfo, SessionDetail, SessionInfo, WorkspaceState } from '@shared/types';

export function useStudio() {
  const [ws, setWs] = useState<WorkspaceState | null>(null);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [runs, setRuns] = useState<RunInfo[]>([]);
  const [details, setDetails] = useState<Record<string, SessionDetail>>({});
  const detailsRef = useRef(details);
  detailsRef.current = details;

  const refresh = useCallback(async () => setWs(await api['state:get']()), []);

  useEffect(() => {
    refresh();
    api['agent:list']().then((r) => {
      setSessions(r.sessions);
      setRuns(r.runs);
    });
    const offState = api.on('state', setWs);
    const offAgent = api.on('agent', (e) => {
      if (e.type === 'session') {
        setSessions((cur) => {
          const i = cur.findIndex((s) => s.id === e.session.id);
          if (i < 0) return [e.session, ...cur];
          const next = [...cur];
          next[i] = e.session;
          return next;
        });
        setDetails((d) => (d[e.session.id] ? { ...d, [e.session.id]: { ...d[e.session.id], ...e.session } } : d));
      } else if (e.type === 'run') {
        setRuns((cur) => [e.run, ...cur.filter((r) => r.id !== e.run.id)].sort((a, b) => b.createdAt - a.createdAt));
      } else if (e.type === 'timeline' || e.type === 'timeline-update') {
        setDetails((d) => {
          const s = d[e.sessionId];
          if (!s) return d;
          const tl = e.type === 'timeline' ? [...s.timeline, e.item] : s.timeline.map((t) => (t.id === e.item.id ? { ...e.item } : t));
          return { ...d, [e.sessionId]: { ...s, timeline: tl } };
        });
      } else if (e.type === 'task') {
        setDetails((d) => {
          const s = d[e.sessionId];
          if (!s) return d;
          const tasks = s.tasks.some((t) => t.taskId === e.task.taskId) ? s.tasks.map((t) => (t.taskId === e.task.taskId ? e.task : t)) : [...s.tasks, e.task];
          return { ...d, [e.sessionId]: { ...s, tasks } };
        });
      }
    });
    return () => {
      offState();
      offAgent();
    };
  }, [refresh]);

  const loadDetail = useCallback(async (id: string) => {
    if (detailsRef.current[id]) return;
    const d = await api['agent:get'](id);
    if (d) setDetails((cur) => ({ ...cur, [id]: d }));
  }, []);

  return { ws, refresh, sessions, runs, details, loadDetail };
}

export const fmtUsd = (n: number) => `$${n.toFixed(n < 1 ? 3 : 2)}`;
export const ago = (t: number) => {
  const s = Math.round((Date.now() - t) / 1000);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.round(s / 60)}m ago`;
  if (s < 86400) return `${Math.round(s / 3600)}h ago`;
  return new Date(t).toLocaleDateString();
};
