// Types shared by the main process, the preload bridge and the renderer.

export type ReviewStatus = 'none' | 'pending' | 'approved' | 'changes';

export interface ReviewEntry {
  status: ReviewStatus;
  note?: string;
  at?: string;
  gate?: string;
  math?: string; // "PASS 2026-11-23" etc, reported by the master via report_stage
  stage?: string; // last stage reported by the master
  history?: { status: ReviewStatus; note?: string; at: string }[];
  edited?: string; // set when the author edited text inline (needs math re-check)
}

export type PageStage =
  | 'source' // only in the manuscript split (src/Pxxx.txt)
  | 'planned' // has a pages.json entry
  | 'built' // has index.html
  | 'rendered' // preview.png + PDF
  | 'math_pass'
  | 'pending' // awaiting the author's review
  | 'approved'
  | 'changes';

export interface SurveyRow {
  page: string;
  kind: string;
  panels: number;
  story: number;
  examples: number;
  equations: number;
  words: number;
}

export interface PageState {
  page: string; // P039
  title?: string;
  purpose?: string;
  survey?: SurveyRow;
  planned: boolean;
  built: boolean;
  preview?: string; // repo-relative path
  previewMtime?: number;
  pdf?: string; // repo-relative path
  math?: string;
  review: ReviewEntry;
  stage: PageStage;
  newArt: number; // panels with art.kind == "new"
}

export interface ChapterState {
  id: string; // CH01
  label?: string;
  referenceDir?: string; // Tasks-relative, e.g. "Reference/Chap 2"
  manuscript?: string;
  register?: string;
  hasSrc: boolean;
  hasPlan: boolean;
  pages: PageState[];
  imageCostUsd: number;
  counts: Record<PageStage, number>;
}

export interface WorkspaceState {
  repo: string | null;
  tasks: string | null;
  chapters: ChapterState[];
  imageCostUsd: number;
  error?: string;
}

export interface Settings {
  repo: string | null;
  python: string;
  claude: string;
  firefox: string;
  permissionMode: PermissionPreset;
  permsDefaultV?: number; // settings migration marker for the permission default
  chunkSize: number;
  setupDone: boolean; // first-run setup (OpenAI key + workspace) finished or skipped
}

export interface KeyStatus {
  saved: boolean; // a key is saved in Studio
  source: 'studio' | 'env' | null; // where agents get a key from
  hint?: string; // last 4 characters, e.g. …a1b2
}

export type PermissionPreset = 'ask' | 'safe' | 'auto';

export interface DoctorCheck {
  name: string;
  ok: boolean;
  detail: string;
  fix?: string;
}

// ---------- agent sessions ----------

export type SessionKind = 'run' | 'desk' | 'quick';
export type SessionStatus = 'starting' | 'running' | 'idle' | 'waiting' | 'stopped' | 'error';

export interface TimelineItem {
  id: string;
  at: number;
  type: 'user' | 'text' | 'thinking' | 'tool' | 'result' | 'system' | 'error' | 'gate' | 'permission';
  parent?: string | null; // parent_tool_use_id (subagent) or null for the master
  text?: string;
  tool?: { name: string; input: unknown; output?: string; isError?: boolean; useId: string };
  cost?: number;
  permission?: PermissionRequest;
  gate?: GateRequest;
}

export interface TaskInfo {
  taskId: string;
  toolUseId?: string;
  description: string;
  agent?: string;
  status: 'running' | 'completed' | 'failed' | 'stopped';
  tokens?: number;
  toolUses?: number;
  lastTool?: string;
  summary?: string;
  startedAt: number;
}

export interface PermissionRequest {
  id: string;
  tool: string;
  input: unknown;
  kind: 'permission' | 'spend';
  reason?: string;
  agent?: string;
  state: 'open' | 'allowed' | 'denied';
}

export interface GateRequest {
  id: string;
  chapter: string;
  pages: string[];
  gate: string;
  summary: string;
  state: 'open' | 'answered';
  answer?: string;
}

export interface SessionInfo {
  id: string;
  title: string;
  kind: SessionKind;
  chapter?: string;
  sdkSessionId?: string;
  status: SessionStatus;
  createdAt: number;
  costUsd: number;
  model?: string;
  runId?: string;
  chunkIndex?: number;
  queued: string[];
}

export interface SessionDetail extends SessionInfo {
  timeline: TimelineItem[];
  tasks: TaskInfo[];
}

export type RunAction = 'plan' | 'run' | 'sample';

export interface RunInfo {
  id: string;
  chapter: string;
  action: RunAction;
  sampleKind?: string;
  chunks: string[][];
  current: number; // index of the running chunk, -1 before start
  sessionIds: string[];
  status: 'running' | 'paused' | 'done' | 'stopped';
  createdAt: number;
}

export interface ToolRunResult {
  code: number;
  out: string;
}

export interface InlineEdit {
  path: number[]; // element-child index path from <body>
  oldText: string;
  newHtml: string;
  newText: string;
}

export interface InlineSaveResult {
  applied: number;
  skipped: string[];
  render: ToolRunResult;
  textcheck: ToolRunResult;
  mathChanged: boolean;
}

export type AgentEvent =
  | { type: 'session'; session: SessionInfo }
  | { type: 'timeline'; sessionId: string; item: TimelineItem }
  | { type: 'timeline-update'; sessionId: string; item: TimelineItem }
  | { type: 'task'; sessionId: string; task: TaskInfo }
  | { type: 'run'; run: RunInfo };
