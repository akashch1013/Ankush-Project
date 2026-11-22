// Agent sessions over the Claude Agent SDK, using the user's installed `claude` (same CLAUDE.md, skills, agents, login).
import { app } from 'electron';
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';
import { query, createSdkMcpServer, tool, type Query, type SDKMessage, type SDKUserMessage, type PermissionResult } from '@anthropic-ai/claude-agent-sdk';
import { z } from 'zod';
import { getSettings, requireTasks, claudeBin, childEnv } from './settings';
import { hardRule, presetDecision } from './policy';
import { setStatus, updatePage, logFeedback, today } from './review';
import { runCmd } from './tools';
import type { AgentEvent, GateRequest, PermissionRequest, RunAction, RunInfo, SessionDetail, SessionInfo, SessionKind, TaskInfo, TimelineItem } from '@shared/types';

export const STUDIO_APPEND = `
# Running inside ChandRush Studio
You are driven by ChandRush Studio, a desktop app over this harness. The author watches your work there. Differences from chat:
- **No Claude Artifacts.** The Artifact tool is not available in this session. Skip every Artifact step (quickstart, publish, read, comments) and do not try to load it. A page is finished when its PDF and preview.png are rendered, textcheck passes and math-checker returns PASS. The author reviews pages in Studio. Do not write artifacts.json entries.
- **Gates.** At every user gate, and whenever finished pages are ready for the author to look at, call \`mcp__studio__request_review\` with the chapter, pages, gate type and a short summary. Then end your turn and wait. The author's answer comes back as a message such as "approved P039" or "changes P041: <note>". Treat "changes" as a fix request and as feedback.
- **Progress.** Call \`mcp__studio__report_stage\` when a page reaches a stage (planned, art, built, rendered, math_pass, math_fail), so the Studio board stays live.
- **Run chunks.** If the prompt says it is a Studio run chunk, call \`mcp__studio__chunk_done\` with a one-paragraph report once every page of the chunk is rendered, PASSed and sent for review. Then end your turn. Studio starts the next chunk in a fresh session, so you never need to ask the user to /clear.
- Studio already logs the author's review decisions in FEEDBACK.md. Do not log approvals again, but do record feedback rules as usual.
- Immediate image calls and quality "max" are blocked. Paid batch submits are shown to the author for approval first, so submit them as normal and wait.
`;

type Emit = (e: AgentEvent) => void;
let emit: Emit = () => undefined;
export function setEmitter(fn: Emit) {
  emit = fn;
}

const dir = () => {
  const d = join(app.getPath('userData'), 'sessions');
  mkdirSync(d, { recursive: true });
  return d;
};

// ---------- input queue for streaming-input mode ----------
class Inbox implements AsyncIterable<SDKUserMessage> {
  private q: SDKUserMessage[] = [];
  private waiters: ((r: IteratorResult<SDKUserMessage>) => void)[] = [];
  private closed = false;
  push(text: string) {
    const msg: SDKUserMessage = { type: 'user', message: { role: 'user', content: text }, parent_tool_use_id: null } as SDKUserMessage;
    const w = this.waiters.shift();
    if (w) w({ value: msg, done: false });
    else this.q.push(msg);
  }
  close() {
    this.closed = true;
    this.waiters.splice(0).forEach((w) => w({ value: undefined as never, done: true }));
  }
  [Symbol.asyncIterator](): AsyncIterator<SDKUserMessage> {
    return {
      next: () => {
        const m = this.q.shift();
        if (m) return Promise.resolve({ value: m, done: false });
        if (this.closed) return Promise.resolve({ value: undefined as never, done: true });
        return new Promise((r) => this.waiters.push(r));
      },
    };
  }
}

const trunc = (s: string, n = 6000) => (s.length > n ? s.slice(0, n) + `\n… (${s.length - n} more chars)` : s);

function resultText(content: unknown): string {
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) return content.map((c) => (c?.type === 'text' ? c.text : c?.type === 'image' ? '[image]' : JSON.stringify(c))).join('\n');
  return JSON.stringify(content);
}

// ---------- session ----------
class Session {
  info: SessionInfo;
  timeline: TimelineItem[] = [];
  tasks = new Map<string, TaskInfo>();
  private q: Query | null = null;
  private inbox: Inbox | null = null;
  private toolItems = new Map<string, TimelineItem>();
  private perms = new Map<string, (r: PermissionResult) => void>();
  private baseCost = 0;
  private saveTimer: NodeJS.Timeout | null = null;
  onTurnEnd?: () => void;
  chunkDone = false;

  constructor(info: SessionInfo, timeline: TimelineItem[] = [], tasks: TaskInfo[] = []) {
    this.info = info;
    this.timeline = timeline;
    tasks.forEach((t) => this.tasks.set(t.taskId, t));
    for (const it of timeline) if (it.tool) this.toolItems.set(it.tool.useId, it);
  }

  get live() {
    return !!this.q;
  }

  detail(): SessionDetail {
    return { ...this.info, timeline: this.timeline, tasks: [...this.tasks.values()] };
  }

  private publish() {
    emit({ type: 'session', session: { ...this.info } });
    this.save();
  }

  private save() {
    if (this.saveTimer) return;
    this.saveTimer = setTimeout(() => {
      this.saveTimer = null;
      const d = this.detail();
      d.timeline = d.timeline.slice(-1500);
      writeFileSync(join(dir(), `${this.info.id}.json`), JSON.stringify(d));
    }, 800);
  }

  add(item: Omit<TimelineItem, 'id' | 'at'> & { id?: string }) {
    const full: TimelineItem = { id: item.id ?? randomUUID(), at: Date.now(), ...item } as TimelineItem;
    this.timeline.push(full);
    emit({ type: 'timeline', sessionId: this.info.id, item: full });
    this.save();
    return full;
  }

  update(item: TimelineItem) {
    emit({ type: 'timeline-update', sessionId: this.info.id, item });
    this.save();
  }

  setStatus(s: SessionInfo['status']) {
    this.info.status = s;
    this.publish();
  }

  private refreshWaiting() {
    const open = this.timeline.some((t) => (t.permission && t.permission.state === 'open') || (t.gate && t.gate.state === 'open'));
    if (open && this.info.status !== 'waiting') this.setStatus('waiting');
    else if (!open && this.info.status === 'waiting') this.setStatus(this.busy ? 'running' : 'idle');
  }

  private busy = false;

  send(text: string) {
    this.add({ type: 'user', text });
    if (!this.q) this.start();
    this.busy = true;
    this.inbox!.push(text);
    if (this.info.status !== 'waiting') this.setStatus('running');
  }

  private start() {
    const s = getSettings();
    const tasks = requireTasks();
    this.inbox = new Inbox();
    const self = this;
    const studio = createSdkMcpServer({
      name: 'studio',
      version: '0.1.0',
      tools: [
        tool(
          'request_review',
          'Ask the author to review finished pages (or a gate sample) in ChandRush Studio. After calling it, end your turn and wait for the answer message.',
          {
            chapter: z.string().describe('e.g. CH01'),
            pages: z.array(z.string()).describe('page ids, e.g. ["P039"]'),
            gate: z.enum(['sample-panels', 'first-page', 'pages', 'bg-samples', 'question']).describe('which gate'),
            summary: z.string().describe('what the author should look at, one short paragraph'),
          },
          async (a) => {
            const gate: GateRequest = { id: randomUUID(), chapter: a.chapter, pages: a.pages, gate: a.gate, summary: a.summary, state: 'open' };
            if (a.pages.length) setStatus(a.chapter, a.pages, 'pending', undefined, a.gate);
            self.add({ type: 'gate', gate });
            self.refreshWaiting();
            return { content: [{ type: 'text', text: 'Queued for the author in Studio. End your turn now; the decision will arrive as the next message.' }] };
          },
        ),
        tool(
          'report_stage',
          'Report that a page reached a pipeline stage, so the Studio board updates live.',
          {
            chapter: z.string(),
            page: z.string(),
            stage: z.enum(['planned', 'art', 'built', 'rendered', 'math_pass', 'math_fail', 'failed']),
            note: z.string().optional(),
          },
          async (a) => {
            const patch: Record<string, unknown> = { stage: a.stage };
            if (a.stage === 'math_pass') Object.assign(patch, { math: `PASS ${today()}${a.note ? ` (${a.note})` : ''}`, edited: undefined });
            if (a.stage === 'math_fail') patch.math = `FAIL ${today()}${a.note ? `: ${a.note}` : ''}`;
            updatePage(a.chapter, a.page, patch);
            return { content: [{ type: 'text', text: 'ok' }] };
          },
        ),
        tool(
          'chunk_done',
          'Signal that every page of this Studio run chunk is finished. Studio then starts the next chunk in a fresh session.',
          { summary: z.string() },
          async (a) => {
            self.chunkDone = true;
            self.add({ type: 'system', text: `Chunk done: ${a.summary}` });
            return { content: [{ type: 'text', text: 'Recorded. End your turn now.' }] };
          },
        ),
      ],
    });

    this.q = query({
      prompt: this.inbox,
      options: {
        cwd: tasks,
        pathToClaudeCodeExecutable: claudeBin(),
        env: childEnv(),
        settingSources: ['project', 'user', 'local'],
        systemPrompt: { type: 'preset', preset: 'claude_code', append: STUDIO_APPEND },
        permissionMode: 'default',
        model: this.info.kind === 'quick' ? 'sonnet' : undefined,
        resume: this.info.sdkSessionId,
        mcpServers: { studio },
        includePartialMessages: false,
        hooks: {
          PreToolUse: [
            {
              hooks: [
                async (input) => {
                  if (input.hook_event_name !== 'PreToolUse') return {};
                  const h = hardRule(input.tool_name, (input.tool_input ?? {}) as Record<string, unknown>, tasks);
                  if (!h) return {};
                  return {
                    hookSpecificOutput: {
                      hookEventName: 'PreToolUse',
                      permissionDecision: h.kind === 'deny' ? 'deny' : 'ask',
                      permissionDecisionReason: h.reason,
                    },
                  };
                },
              ],
            },
          ],
        },
        canUseTool: (toolName, input, opts) => this.permission(toolName, input, opts.signal),
      },
    });
    this.baseCost = this.info.costUsd;
    this.pump(this.q);
  }

  private permission(toolName: string, input: Record<string, unknown>, signal: AbortSignal): Promise<PermissionResult> {
    const tasks = requireTasks();
    const h = hardRule(toolName, input, tasks);
    if (h?.kind === 'deny') return Promise.resolve({ behavior: 'deny', message: h.reason });
    if (!h && presetDecision(getSettings().permissionMode, toolName, input, tasks) === 'allow') {
      return Promise.resolve({ behavior: 'allow', updatedInput: input });
    }
    const req: PermissionRequest = { id: randomUUID(), tool: toolName, input, kind: h?.kind === 'spend' ? 'spend' : 'permission', reason: h?.reason, state: 'open' };
    const item = this.add({ type: 'permission', permission: req });
    this.refreshWaiting();
    if (req.kind === 'spend') this.attachCost(item, input);
    return new Promise((resolve) => {
      this.perms.set(req.id, resolve);
      signal.addEventListener('abort', () => this.answerPermission(req.id, false, 'aborted'));
    });
  }

  /** For a batch submit, show the workspace's spend so far next to the request (free). */
  private async attachCost(item: TimelineItem, input: Record<string, unknown>) {
    const m = String(input.command ?? '').match(/--ws\s+(\S+)/);
    if (!m) return;
    const r = await runCmd(getSettings().python, ['pipeline/imggen.py', '--ws', m[1].replace(/^['"]|['"]$/g, ''), 'cost'], requireTasks(), 30_000);
    if (item.permission) item.permission.reason = `${item.permission.reason ?? ''}\n${r.out.trim().split('\n').slice(-4).join('\n')}`;
    this.update(item);
  }

  answerPermission(id: string, allow: boolean, message?: string) {
    const resolve = this.perms.get(id);
    const item = this.timeline.find((t) => t.permission?.id === id);
    if (item?.permission) {
      item.permission.state = allow ? 'allowed' : 'denied';
      this.update(item);
    }
    if (resolve) {
      this.perms.delete(id);
      resolve(allow ? { behavior: 'allow', updatedInput: (item?.permission?.input as Record<string, unknown>) ?? {} } : { behavior: 'deny', message: message || 'The author denied this in Studio.' });
    }
    this.refreshWaiting();
  }

  answerGate(id: string, answer: string) {
    const item = this.timeline.find((t) => t.gate?.id === id);
    if (item?.gate) {
      item.gate.state = 'answered';
      item.gate.answer = answer;
      this.update(item);
    }
    this.refreshWaiting();
    this.send(answer);
  }

  openGates(): GateRequest[] {
    return this.timeline.filter((t) => t.gate?.state === 'open').map((t) => t.gate!);
  }

  private async pump(q: Query) {
    try {
      for await (const m of q) this.handle(m);
    } catch (e) {
      this.add({ type: 'error', text: String((e as Error)?.message ?? e) });
      this.info.status = 'error';
    } finally {
      if (this.q === q) {
        this.q = null;
        this.inbox = null;
        this.busy = false;
        for (const id of [...this.perms.keys()]) this.answerPermission(id, false, 'session ended');
        if (this.info.status !== 'error') this.info.status = 'stopped';
        this.publish();
      }
    }
  }

  private taskFor(parent: string | null | undefined) {
    if (!parent) return undefined;
    for (const t of this.tasks.values()) if (t.toolUseId === parent) return t;
    return undefined;
  }

  private handle(m: SDKMessage) {
    switch (m.type) {
      case 'system': {
        const sm = m as SDKMessage & { subtype: string } & Record<string, unknown>;
        if (sm.subtype === 'init') {
          this.info.sdkSessionId = sm.session_id as string;
          this.info.model = sm.model as string;
          this.publish();
        } else if (sm.subtype === 'task_started') {
          const t: TaskInfo = {
            taskId: sm.task_id as string,
            toolUseId: sm.tool_use_id as string | undefined,
            description: sm.description as string,
            agent: sm.subagent_type as string | undefined,
            status: 'running',
            startedAt: Date.now(),
          };
          this.tasks.set(t.taskId, t);
          emit({ type: 'task', sessionId: this.info.id, task: t });
        } else if (sm.subtype === 'task_progress' || sm.subtype === 'task_notification') {
          const t = this.tasks.get(sm.task_id as string);
          if (!t) break;
          const u = sm.usage as { total_tokens: number; tool_uses: number } | undefined;
          if (u) Object.assign(t, { tokens: u.total_tokens, toolUses: u.tool_uses });
          if (sm.last_tool_name) t.lastTool = sm.last_tool_name as string;
          if (sm.summary) t.summary = sm.summary as string;
          if (sm.subtype === 'task_notification') t.status = sm.status as TaskInfo['status'];
          emit({ type: 'task', sessionId: this.info.id, task: t });
          this.save();
        } else if (sm.subtype === 'compact_boundary') {
          this.add({ type: 'system', text: 'Context compacted.' });
        }
        break;
      }
      case 'assistant': {
        const parent = m.parent_tool_use_id;
        if (m.error) this.add({ type: 'error', text: `API error: ${m.error}`, parent });
        for (const b of m.message.content as { type: string; text?: string; thinking?: string; name?: string; input?: unknown; id?: string }[]) {
          if (b.type === 'text' && b.text?.trim()) this.add({ type: 'text', text: b.text, parent });
          else if (b.type === 'thinking' && b.thinking?.trim()) this.add({ type: 'thinking', text: b.thinking, parent });
          else if (b.type === 'tool_use' || b.type === 'server_tool_use' || b.type === 'mcp_tool_use') {
            const it = this.add({ type: 'tool', parent, tool: { name: b.name ?? '?', input: b.input, useId: b.id ?? randomUUID() } });
            this.toolItems.set(it.tool!.useId, it);
            const t = this.taskFor(parent);
            if (t) {
              t.lastTool = b.name;
              emit({ type: 'task', sessionId: this.info.id, task: t });
            }
          }
        }
        break;
      }
      case 'user': {
        const content = (m.message as { content: unknown }).content;
        if (!Array.isArray(content)) break;
        for (const b of content as { type: string; tool_use_id?: string; content?: unknown; is_error?: boolean }[]) {
          if (b.type !== 'tool_result' || !b.tool_use_id) continue;
          const it = this.toolItems.get(b.tool_use_id);
          if (!it?.tool) continue;
          it.tool.output = trunc(resultText(b.content));
          it.tool.isError = !!b.is_error;
          this.update(it);
        }
        break;
      }
      case 'result': {
        const r = m as SDKMessage & { subtype: string; total_cost_usd?: number; result?: string; errors?: string[]; num_turns?: number };
        this.info.costUsd = r.total_cost_usd ?? this.info.costUsd;
        if (r.subtype !== 'success') this.add({ type: 'error', text: `Turn ended: ${r.subtype}${r.errors?.length ? ` · ${r.errors.join('; ')}` : ''}` });
        this.add({ type: 'result', cost: this.info.costUsd, text: `Turn done · ${r.num_turns ?? '?'} steps · session $${this.info.costUsd.toFixed(3)}` });
        this.busy = false;
        this.info.status = this.openGates().length ? 'waiting' : 'idle';
        this.publish();
        this.onTurnEnd?.();
        break;
      }
      default:
        break;
    }
  }

  async interrupt() {
    if (!this.q) return;
    this.add({ type: 'system', text: 'Stop requested by the author.' });
    try {
      await this.q.interrupt();
    } catch (e) {
      this.add({ type: 'error', text: `interrupt failed: ${e}` });
    }
  }

  async stopTask(taskId: string) {
    await this.q?.stopTask(taskId).catch((e) => this.add({ type: 'error', text: `stop task failed: ${e}` }));
  }

  close() {
    this.inbox?.close();
    this.q?.close();
  }
}

// ---------- registry ----------
const sessions = new Map<string, Session>();
const runs = new Map<string, RunInfo>();

export function loadSessions() {
  for (const f of readdirSync(dir())) {
    if (!f.endsWith('.json') || f === 'runs.json') continue;
    try {
      const d = JSON.parse(readFileSync(join(dir(), f), 'utf8')) as SessionDetail;
      const { timeline, tasks, ...info } = d;
      if (['running', 'starting', 'waiting'].includes(info.status)) info.status = 'stopped';
      tasks.forEach((t) => t.status === 'running' && (t.status = 'stopped'));
      sessions.set(info.id, new Session({ ...info, queued: info.queued ?? [] }, timeline, tasks));
    } catch {
      /* skip corrupt */
    }
  }
  try {
    for (const r of JSON.parse(readFileSync(join(dir(), 'runs.json'), 'utf8')) as RunInfo[]) {
      if (r.status === 'running') r.status = 'paused';
      runs.set(r.id, r);
    }
  } catch {
    /* none */
  }
}

const saveRuns = () => writeFileSync(join(dir(), 'runs.json'), JSON.stringify([...runs.values()]));

export function listSessions(): SessionInfo[] {
  return [...sessions.values()].map((s) => s.info).sort((a, b) => b.createdAt - a.createdAt);
}
export function listRuns(): RunInfo[] {
  return [...runs.values()].sort((a, b) => b.createdAt - a.createdAt);
}
export function getSession(id: string): SessionDetail | null {
  return sessions.get(id)?.detail() ?? null;
}

export function createSession(kind: SessionKind, title: string, prompt: string, chapter?: string, extra: Partial<SessionInfo> = {}): SessionInfo {
  const info: SessionInfo = { id: randomUUID(), title, kind, chapter, status: 'starting', createdAt: Date.now(), costUsd: 0, queued: [], ...extra };
  const s = new Session(info);
  sessions.set(info.id, s);
  emit({ type: 'session', session: { ...info } });
  s.send(prompt);
  return s.info;
}

export function sendMessage(id: string, text: string) {
  const s = sessions.get(id);
  if (!s) throw new Error('No such session');
  s.send(text);
}
export const interrupt = (id: string) => sessions.get(id)?.interrupt();
export const stopTask = (id: string, taskId: string) => sessions.get(id)?.stopTask(taskId);
export const answerPermission = (id: string, permId: string, allow: boolean, msg?: string) => sessions.get(id)?.answerPermission(permId, allow, msg);
export function closeSession(id: string) {
  sessions.get(id)?.close();
}
export function closeAll() {
  sessions.forEach((s) => s.close());
}

/** The chapter's desk session: one long-lived master session for page fixes, edits and feedback. */
export function desk(chapter: string | undefined, text: string, title?: string): SessionInfo {
  const key = chapter ?? 'ALL';
  const existing = [...sessions.values()].filter((s) => s.info.kind === 'desk' && (s.info.chapter ?? 'ALL') === key && s.info.status !== 'error').sort((a, b) => b.info.createdAt - a.info.createdAt)[0];
  if (existing) {
    existing.send(text);
    return existing.info;
  }
  return createSession('desk', title ?? `${key} desk`, text, chapter);
}

export function quick(text: string, title: string, chapter?: string): SessionInfo {
  return createSession('quick', title, text, chapter);
}

// ---------- review decisions ----------
export interface Decision {
  page: string;
  status: 'approved' | 'changes';
  note?: string;
}

function decisionText(ds: Decision[]) {
  const ok = ds.filter((d) => d.status === 'approved').map((d) => d.page);
  const ch = ds.filter((d) => d.status === 'changes');
  const parts: string[] = [];
  if (ok.length) parts.push(`approved ${ok.join(', ')}`);
  for (const c of ch) parts.push(`changes ${c.page}: ${c.note ?? ''}`);
  return `Review from the author (ChandRush Studio): ${parts.join('; ')}.${ch.length ? ' Apply the changes (fix + feedback rules), re-render, re-check the maths if it changed, then request review again.' : ' Continue.'}`;
}

/** Record the author's verdicts. If a session is waiting on a gate for these pages, it gets the answer; changes outside a gate go to the chapter desk. */
export function review(chapter: string, decisions: Decision[], gate?: { sessionId: string; gateId: string }) {
  for (const d of decisions) {
    setStatus(chapter, [d.page], d.status, d.note);
    logFeedback(`${chapter} ${d.page}`, 'review', d.note ?? '', d.status === 'approved' ? 'approved in Studio' : 'changes requested in Studio');
  }
  let target = gate;
  if (!target) {
    for (const s of sessions.values()) {
      const g = s.openGates().find((g) => g.chapter === chapter && decisions.some((d) => g.pages.includes(d.page)));
      if (g) {
        target = { sessionId: s.info.id, gateId: g.id };
        break;
      }
    }
  }
  if (target) {
    sessions.get(target.sessionId)?.answerGate(target.gateId, decisionText(decisions));
    return { routed: 'gate', sessionId: target.sessionId };
  }
  const changes = decisions.filter((d) => d.status === 'changes');
  if (changes.length) {
    const info = desk(chapter, changes.map((c) => `/comic-master fix ${chapter} ${c.page} "${(c.note ?? '').replace(/"/g, "'")}"`).join('\n'));
    return { routed: 'desk', sessionId: info.id };
  }
  return { routed: 'none' };
}

export function answerGateText(sessionId: string, gateId: string, text: string) {
  sessions.get(sessionId)?.answerGate(gateId, text);
}

// ---------- runs (chunked batches) ----------
export function ranges(pages: string[]): string {
  const nums = pages.map((p) => parseInt(p.slice(1), 10)).sort((a, b) => a - b);
  const out: string[] = [];
  for (let i = 0; i < nums.length; ) {
    let j = i;
    while (j + 1 < nums.length && nums[j + 1] === nums[j] + 1) j++;
    const a = `P${String(nums[i]).padStart(3, '0')}`;
    const b = `P${String(nums[j]).padStart(3, '0')}`;
    out.push(i === j ? a : `${a}-${b}`);
    i = j + 1;
  }
  return out.join(',');
}

export function chunkPrompt(run: RunInfo, i: number): string {
  const pages = run.chunks[i] ?? [];
  const r = ranges(pages);
  let cmd: string;
  if (run.action === 'sample') cmd = `/comic-master sample ${run.sampleKind ?? 'teaching'} ${run.chapter}`;
  else if (run.action === 'plan') cmd = `/comic-master plan ${run.chapter} ${r}`;
  else cmd = pages.length <= 5 ? `/comic-master page ${run.chapter} ${r}` : `/comic-master run ${run.chapter} ${r}`;
  const note =
    run.chunks.length > 1 || run.action !== 'sample'
      ? `\n\nThis is Studio run chunk ${i + 1} of ${run.chunks.length} (pages ${r || 'chosen by survey'}). Stay inside these pages. When the chunk is finished, call mcp__studio__chunk_done with your report and end your turn.`
      : '';
  return cmd + note;
}

export function startRun(chapter: string, action: RunAction, pages: string[], chunkSize: number, sampleKind?: string): RunInfo {
  const size = Math.max(1, Math.min(35, chunkSize));
  const sorted = [...pages].sort();
  const chunks: string[][] = [];
  if (action === 'sample') chunks.push([]);
  else for (let i = 0; i < sorted.length; i += size) chunks.push(sorted.slice(i, i + size));
  const run: RunInfo = { id: randomUUID(), chapter, action, sampleKind, chunks, current: -1, sessionIds: [], status: 'running', createdAt: Date.now() };
  runs.set(run.id, run);
  advance(run);
  return run;
}

function advance(run: RunInfo) {
  if (run.status !== 'running') return;
  const next = run.current + 1;
  if (next >= run.chunks.length) {
    run.status = 'done';
    saveRuns();
    emit({ type: 'run', run: { ...run } });
    return;
  }
  // Close the previous chunk's session: the next chunk starts cold, with a clean context.
  const prev = run.sessionIds[run.current];
  if (prev) closeSession(prev);
  run.current = next;
  const label = run.action === 'sample' ? `sample ${run.sampleKind}` : `${run.action} ${ranges(run.chunks[next])}`;
  const info = createSession('run', `${run.chapter} ${label}`, chunkPrompt(run, next), run.chapter, { runId: run.id, chunkIndex: next });
  run.sessionIds.push(info.id);
  const s = sessions.get(info.id)!;
  s.onTurnEnd = () => {
    if (s.chunkDone && !s.openGates().length) advance(run);
  };
  saveRuns();
  emit({ type: 'run', run: { ...run } });
}

export function controlRun(id: string, action: 'pause' | 'resume' | 'stop' | 'next') {
  const run = runs.get(id);
  if (!run) return;
  if (action === 'pause') run.status = 'paused';
  if (action === 'stop') {
    run.status = 'stopped';
    const cur = run.sessionIds[run.current];
    if (cur) interrupt(cur);
  }
  if (action === 'resume' || action === 'next') {
    run.status = 'running';
    const cur = sessions.get(run.sessionIds[run.current]);
    if (action === 'next' || !cur || cur.chunkDone) advance(run);
    else if (cur && !cur.live) cur.send(`Continue the Studio run chunk: ${chunkPrompt(run, run.current)}`);
    else if (cur) cur.onTurnEnd = () => cur.chunkDone && !cur.openGates().length && advance(run);
  }
  saveRuns();
  emit({ type: 'run', run: { ...run } });
}

export function sessionsExist() {
  return existsSync(dir());
}
