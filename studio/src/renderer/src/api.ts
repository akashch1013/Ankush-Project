import type {
  AgentEvent, ChapterState, DoctorCheck, InlineEdit, InlineSaveResult, RunAction, RunInfo, SessionDetail, SessionInfo,
  Settings, ToolRunResult, WorkspaceState,
} from '@shared/types';

export interface Decision { page: string; status: 'approved' | 'changes'; note?: string }

interface StudioApi {
  'state:get'(): Promise<WorkspaceState>;
  'settings:get'(): Promise<Settings>;
  'settings:save'(p: Partial<Settings>): Promise<Settings>;
  'settings:pickRepo'(): Promise<Settings | null>;
  'doctor:run'(): Promise<DoctorCheck[]>;
  'file:read'(rel: string): Promise<string | null>;
  'file:open'(rel: string): Promise<string>;
  'file:reveal'(rel: string): Promise<void>;
  'git:diff'(rels: string[]): Promise<string>;
  'page:plan'(ch: string, p: string): Promise<Record<string, unknown> | null>;
  'page:imageItem'(ch: string, p: string, src: string): Promise<{ name: string; item: string | null; file: string }>;
  'page:render'(ch: string, p: string): Promise<ToolRunResult>;
  'page:saveInline'(ch: string, p: string, edits: InlineEdit[]): Promise<InlineSaveResult>;
  'upload:pick'(): Promise<string[]>;
  'upload:chapter'(folder: string, files: string[]): Promise<{ ok: boolean; chapter?: string; folder?: string; copied: string[]; log: string[]; error?: string }>;
  'chapter:prep'(ch: string): Promise<ToolRunResult[]>;
  'review:decide'(ch: string, d: Decision[], gate?: { sessionId: string; gateId: string }): Promise<{ routed: string; sessionId?: string }>;
  'agent:list'(): Promise<{ sessions: SessionInfo[]; runs: RunInfo[] }>;
  'agent:get'(id: string): Promise<SessionDetail | null>;
  'agent:create'(kind: 'desk' | 'quick', title: string, prompt: string, chapter?: string): Promise<SessionInfo>;
  'agent:send'(id: string, text: string): Promise<void>;
  'agent:desk'(chapter: string | undefined, text: string): Promise<SessionInfo>;
  'agent:interrupt'(id: string): Promise<void>;
  'agent:stopTask'(id: string, taskId: string): Promise<void>;
  'agent:close'(id: string): Promise<void>;
  'agent:permission'(id: string, permId: string, allow: boolean, msg?: string): Promise<void>;
  'agent:gateText'(id: string, gateId: string, text: string): Promise<void>;
  'run:start'(ch: string, action: RunAction, pages: string[], chunkSize: number, sampleKind?: string): Promise<RunInfo>;
  'run:control'(id: string, action: 'pause' | 'resume' | 'stop' | 'next'): Promise<void>;
  'shell:external'(url: string): Promise<void>;
  on(channel: 'state', fn: (s: WorkspaceState) => void): () => void;
  on(channel: 'agent', fn: (e: AgentEvent) => void): () => void;
  pathForFile(f: File): string;
}

export const api = (window as unknown as { studio: StudioApi }).studio;
export const fileUrl = (rel: string, bust?: number | string) => `studio://file/${rel.split('/').map(encodeURIComponent).join('/')}${bust ? `?t=${bust}` : ''}`;
export type { ChapterState };
