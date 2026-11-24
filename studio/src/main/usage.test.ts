import { test } from 'node:test';
import assert from 'node:assert/strict';
import { UsageTracker, rateLimitActive, rateLimitFrom, rateLimitLabel, rateLimitText, modelUsageTotals, fmtTokens } from '../shared/usage.ts';

const mu = (input: number, output: number, cacheRead: number, cacheWrite: number) => ({ inputTokens: input, outputTokens: output, cacheReadInputTokens: cacheRead, cacheCreationInputTokens: cacheWrite });
const result = (cost: number, models: Record<string, ReturnType<typeof mu>>) => ({ type: 'result', subtype: 'success', total_cost_usd: cost, modelUsage: models, usage: { input_tokens: 1, output_tokens: 1, cache_read_input_tokens: 1, cache_creation_input_tokens: 1 } });

test('modelUsageTotals sums across models (subagents included)', () => {
  const t = modelUsageTotals(result(0.5, { sonnet: mu(10, 20, 300, 40), haiku: mu(1, 2, 3, 4) }));
  assert.deepEqual(t, { input: 11, output: 22, cacheRead: 303, cacheWrite: 44 });
  assert.equal(modelUsageTotals({ total_cost_usd: 0.1 }), undefined);
});

test('running totals within one process are not double counted', () => {
  const u = new UsageTracker();
  u.newProcess();
  u.onResult(result(0.1, { s: mu(10, 10, 100, 10) }));
  const s = u.onResult(result(0.3, { s: mu(25, 30, 400, 15) }));
  assert.deepEqual(s.tokens, { input: 25, output: 30, cacheRead: 400, cacheWrite: 15 });
  assert.ok(Math.abs(s.costUsd - 0.3) < 1e-9);
});

test('a fresh process after resume adds to the stored total; a carried total is not re-added', () => {
  const stored = { costUsd: 1, tokens: { input: 100, output: 100, cacheRead: 1000, cacheWrite: 100 } };
  const fresh = new UsageTracker(structuredClone(stored));
  fresh.newProcess();
  const a = fresh.onResult(result(0.2, { s: mu(5, 5, 50, 5) }));
  assert.deepEqual(a.tokens, { input: 105, output: 105, cacheRead: 1050, cacheWrite: 105 });
  assert.ok(Math.abs(a.costUsd - 1.2) < 1e-9);

  const carried = new UsageTracker(structuredClone(stored));
  carried.newProcess();
  const b = carried.onResult(result(1.2, { s: mu(105, 105, 1050, 105) }));
  assert.deepEqual(b.tokens, { input: 105, output: 105, cacheRead: 1050, cacheWrite: 105 });
  const c = carried.onResult(result(1.5, { s: mu(110, 110, 1100, 110) }));
  assert.deepEqual(c.tokens, { input: 110, output: 110, cacheRead: 1100, cacheWrite: 110 });
});

test('a /clear reset starts a new running total; zeroed crash results are ignored', () => {
  const u = new UsageTracker();
  u.newProcess();
  u.onResult(result(0.5, { s: mu(50, 50, 500, 50) }));
  u.onResult({ total_cost_usd: 0, modelUsage: {}, usage: { input_tokens: 0, output_tokens: 0, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 } });
  const s = u.onResult(result(0.1, { s: mu(5, 5, 50, 5) }));
  assert.deepEqual(s.tokens, { input: 55, output: 55, cacheRead: 550, cacheWrite: 55 });
  assert.ok(Math.abs(s.costUsd - 0.6) < 1e-9);
});

test('a large first turn after resume without a carried total is not read as carried', () => {
  const u = new UsageTracker({ costUsd: 0.05, tokens: { input: 2500, output: 2500, cacheRead: 2500, cacheWrite: 2500 } });
  u.newProcess();
  const r = { total_cost_usd: 0.8, modelUsage: { s: mu(50_000, 50_000, 50_000, 50_000) }, usage: { input_tokens: 49_000, output_tokens: 49_000, cache_read_input_tokens: 49_000, cache_creation_input_tokens: 49_000 } };
  const s = u.onResult(r);
  assert.deepEqual(s.tokens, { input: 52_500, output: 52_500, cacheRead: 52_500, cacheWrite: 52_500 });
  assert.ok(Math.abs(s.costUsd - 0.85) < 1e-9);
});

test('without modelUsage, per-turn usage is added each turn', () => {
  const u = new UsageTracker();
  u.newProcess();
  const turn = (cost: number, n: number) => ({ total_cost_usd: cost, usage: { input_tokens: n, output_tokens: n, cache_read_input_tokens: n, cache_creation_input_tokens: n } });
  u.onResult(turn(0.1, 100));
  const s = u.onResult(turn(0.25, 150));
  assert.deepEqual(s.tokens, { input: 250, output: 250, cacheRead: 250, cacheWrite: 250 });
  assert.ok(Math.abs(s.costUsd - 0.25) < 1e-9);
});

test('rate limit without a reset time expires; overage is softened', () => {
  const now = 1_800_000_000_000;
  const w = rateLimitFrom({ status: 'allowed_warning' }, now)!;
  assert.ok(rateLimitActive(w, now + 1000));
  assert.ok(!rateLimitActive(w, now + 3_600_001));
  const o = rateLimitFrom({ status: 'rejected', isUsingOverage: true, rateLimitType: 'five_hour' }, now)!;
  assert.equal(o.overage, true);
  assert.match(rateLimitText(o), /reached, now using overage/);
  assert.equal(rateLimitLabel(o, now), 'using overage');
  const far = rateLimitFrom({ status: 'rejected', resetsAt: now / 1000 + 3 * 86400 }, now)!;
  assert.match(rateLimitLabel(far, now), /^subscription limit reached · resets \S+ /);
});

test('rate_limit_event is normalised and warns until reset', () => {
  const now = 1_800_000_000_000;
  const rl = rateLimitFrom({ status: 'rejected', resetsAt: now / 1000 + 3600, rateLimitType: 'five_hour', utilization: 1 }, now)!;
  assert.equal(rl.resetsAt, now + 3_600_000);
  assert.equal(rl.at, now);
  assert.ok(rateLimitActive(rl, now));
  assert.ok(!rateLimitActive(rl, now + 3_600_001));
  assert.match(rateLimitText(rl), /^Subscription five hour limit reached \(100% used\)\. Resets /);
  assert.ok(!rateLimitActive(rateLimitFrom({ status: 'allowed' }, now), now));
  assert.ok(rateLimitActive(rateLimitFrom({ status: 'allowed_warning' }, now), now));
  assert.equal(rateLimitFrom(undefined), undefined);
});

test('fmtTokens', () => {
  assert.equal(fmtTokens(15_060_000), '15.06M');
  assert.equal(fmtTokens(13_800), '13.8k');
  assert.equal(fmtTokens(42), '42');
});
