// Pure token/cost accounting over SDK result messages, and rate-limit normalising.
// Shared by main and renderer; unit-tested in src/main/usage.test.ts.
import type { RateLimitState, TokenUsage } from './types.ts';

export interface Totals {
  tokens: TokenUsage;
  costUsd: number;
}

export const zeroTokens = (): TokenUsage => ({ input: 0, output: 0, cacheRead: 0, cacheWrite: 0 });
export const tokenSum = (t: TokenUsage) => t.input + t.output + t.cacheRead + t.cacheWrite;
export const addTokens = (a: TokenUsage, b: TokenUsage): TokenUsage => ({
  input: a.input + b.input,
  output: a.output + b.output,
  cacheRead: a.cacheRead + b.cacheRead,
  cacheWrite: a.cacheWrite + b.cacheWrite,
});
const subTokens = (a: TokenUsage, b: TokenUsage): TokenUsage => ({
  input: a.input - b.input,
  output: a.output - b.output,
  cacheRead: a.cacheRead - b.cacheRead,
  cacheWrite: a.cacheWrite - b.cacheWrite,
});
const keys = ['input', 'output', 'cacheRead', 'cacheWrite'] as const;
const geq = (a: TokenUsage, b: TokenUsage) => keys.every((k) => a[k] >= b[k]);

type ModelUsageLike = { inputTokens?: number; outputTokens?: number; cacheReadInputTokens?: number; cacheCreationInputTokens?: number };
type UsageLike = { input_tokens?: number; output_tokens?: number; cache_read_input_tokens?: number; cache_creation_input_tokens?: number };
export type ResultLike = { total_cost_usd?: number; modelUsage?: Record<string, ModelUsageLike>; usage?: UsageLike };

/** Running totals for the query() call, from modelUsage (all models, subagents included). Undefined when absent. */
export function modelUsageTotals(r: ResultLike): TokenUsage | undefined {
  const mu = r.modelUsage && Object.values(r.modelUsage);
  if (!mu?.length) return undefined;
  const t = zeroTokens();
  for (const m of mu) {
    t.input += m.inputTokens ?? 0;
    t.output += m.outputTokens ?? 0;
    t.cacheRead += m.cacheReadInputTokens ?? 0;
    t.cacheWrite += m.cacheCreationInputTokens ?? 0;
  }
  return t;
}

/** This turn's main-loop tokens (`usage`: per turn, no subagents). A lower bound on what the turn spent. */
export function turnUsage(r: ResultLike): TokenUsage {
  const u = r.usage;
  return { input: u?.input_tokens ?? 0, output: u?.output_tokens ?? 0, cacheRead: u?.cache_read_input_tokens ?? 0, cacheWrite: u?.cache_creation_input_tokens ?? 0 };
}

/**
 * Keeps a Studio session's token and cost totals across results and across query() processes.
 * modelUsage and total_cost_usd are running totals for the query() call, so we add the difference from the
 * previous result. A difference is only trusted when it is at least the turn's own main-loop `usage`; otherwise
 * the totals restarted (a /clear, or a resumed process that did not carry the transcript's total) and the
 * whole value is this turn's. The first result of a resumed process is compared with the stored session total,
 * because the SDK may carry the earlier total into it. A zeroed crash result is ignored. Without modelUsage,
 * `usage` is added per turn.
 */
export class UsageTracker {
  private last: Totals | null = null;
  session: Totals;
  constructor(session: Totals = { tokens: zeroTokens(), costUsd: 0 }) {
    this.session = session;
  }

  /** Call when a new query() process starts for this session. */
  newProcess() {
    this.last = null;
  }

  onResult(r: ResultLike): Totals {
    const mu = modelUsageTotals(r);
    const turn = turnUsage(r);
    const cost = r.total_cost_usd ?? 0;
    if (cost === 0 && tokenSum(mu ?? turn) === 0) return this.session;
    const prior = this.session;
    const base = this.last ?? (prior.costUsd > 0 || tokenSum(prior.tokens) > 0 ? prior : null);
    let tokens: TokenUsage;
    let continues: boolean;
    if (mu) {
      continues = !!base && geq(mu, base.tokens) && geq(subTokens(mu, base.tokens), turn) && cost >= base.costUsd - 1e-9;
      tokens = continues ? subTokens(mu, base!.tokens) : mu;
    } else {
      continues = !!base && cost >= base.costUsd - 1e-9;
      tokens = turn;
    }
    const costDelta = continues ? Math.max(0, cost - base!.costUsd) : cost;
    this.session = { tokens: addTokens(prior.tokens, tokens), costUsd: prior.costUsd + costDelta };
    this.last = { tokens: mu ?? zeroTokens(), costUsd: cost };
    return this.session;
  }
}

type RateLimitInfoLike = { status?: string; resetsAt?: number; rateLimitType?: string; utilization?: number; isUsingOverage?: boolean; overageInUse?: boolean };

/** Normalise an SDK rate_limit_event's info (resetsAt may be epoch seconds) into what Studio stores. */
export function rateLimitFrom(info: RateLimitInfoLike | undefined, now = Date.now()): RateLimitState | undefined {
  if (!info?.status) return undefined;
  const ms = (t?: number) => (t == null ? undefined : t < 1e12 ? t * 1000 : t);
  return {
    status: info.status as RateLimitState['status'],
    resetsAt: ms(info.resetsAt),
    type: info.rateLimitType,
    utilization: info.utilization,
    overage: !!(info.isUsingOverage || info.overageInUse) || undefined,
    at: now,
  };
}

/** A state with no reset time is shown for an hour after it was reported. */
const NO_RESET_TTL = 3_600_000;
export const rateLimitUntil = (r: RateLimitState) => r.resetsAt ?? r.at + NO_RESET_TTL;

/** True when the author should see a subscription-limit warning for this state. */
export const rateLimitActive = (r: RateLimitState | undefined, now = Date.now()) => !!r && r.status !== 'allowed' && rateLimitUntil(r) > now;

/** Reset time, with the day when it is more than 24 h away. */
export function fmtReset(t: number, now = Date.now()): string {
  const d = new Date(t);
  const time = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  return t - now > 86_400_000 ? `${d.toLocaleDateString([], { weekday: 'short', day: 'numeric', month: 'short' })} ${time}` : time;
}

/** Short label for the top bar pill. */
export function rateLimitLabel(r: RateLimitState, now = Date.now()): string {
  const what = r.overage ? 'using overage' : r.status === 'rejected' ? 'subscription limit reached' : 'near subscription limit';
  return r.resetsAt ? `${what} · resets ${fmtReset(r.resetsAt, now)}` : what;
}

/** One-line message, e.g. "Subscription five hour limit reached (100% used). Resets 24/11/2026, 18:00:00." */
export function rateLimitText(r: RateLimitState): string {
  const kind = r.type ? ` ${r.type.replace(/_/g, ' ')}` : '';
  // utilization is a 0-1 fraction.
  const pct = r.utilization != null ? ` (${Math.round(r.utilization * 100)}% used)` : '';
  const state = r.status === 'rejected' ? (r.overage ? 'reached, now using overage' : 'reached') : 'warning';
  const when = r.resetsAt ? ` Resets ${new Date(r.resetsAt).toLocaleString()}.` : '';
  return `Subscription${kind} limit ${state}${pct}.${when}`;
}

/** 15060000 -> "15.06M", 13800 -> "13.8k". */
export const fmtTokens = (n: number) => (n >= 1e6 ? `${(n / 1e6).toFixed(2)}M` : n >= 1e3 ? `${(n / 1e3).toFixed(1)}k` : String(Math.round(n)));
