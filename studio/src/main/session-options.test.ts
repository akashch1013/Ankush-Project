import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildSessionOptions, COMIC_SKILLS } from './session-options.ts';

const base = { cwd: '/repo/Tasks', env: { PATH: '/bin' }, append: 'X', mcpServers: {} };

test('run and desk use the configured model at medium effort; quick stays on sonnet', () => {
  assert.equal(buildSessionOptions({ ...base, kind: 'run', model: 'sonnet' }).model, 'sonnet');
  assert.equal(buildSessionOptions({ ...base, kind: 'desk', model: 'opus' }).model, 'opus');
  assert.equal(buildSessionOptions({ ...base, kind: 'desk', model: '' }).model, 'sonnet');
  assert.equal(buildSessionOptions({ ...base, kind: 'quick', model: 'opus' }).model, 'sonnet');
  assert.equal(buildSessionOptions({ ...base, kind: 'run', model: 'sonnet' }).effort, 'medium');
});

test('user settings, plugins, connectors and unrelated skills are kept out', () => {
  const o = buildSessionOptions({ ...base, kind: 'run', model: 'sonnet' });
  assert.deepEqual(o.settingSources, ['project', 'local']);
  assert.equal(o.strictMcpConfig, true);
  assert.equal(o.env?.ENABLE_CLAUDEAI_MCP_SERVERS, 'false');
  assert.equal(o.env?.PATH, '/bin');
  assert.deepEqual(o.skills, COMIC_SKILLS);
  assert.ok(COMIC_SKILLS.includes('comic-master'));
});

test('the skill allowlist matches the repo skills folder', () => {
  const dir = join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..', '.claude', 'skills');
  const onDisk = readdirSync(dir).filter((d) => existsSync(join(dir, d, 'SKILL.md')));
  assert.deepEqual([...COMIC_SKILLS].sort(), onDisk.sort());
});

test('pipeline tools stay allowed, unused ones are dropped', () => {
  const o = buildSessionOptions({ ...base, kind: 'run', model: 'sonnet' });
  for (const t of ['Agent', 'Task', 'Skill', 'Read', 'Write', 'Edit', 'Bash', 'Grep', 'Glob', 'Monitor', 'SendMessage']) assert.ok(!o.disallowedTools?.includes(t), t);
  for (const t of ['WebSearch', 'WebFetch', 'Artifact', 'CronCreate', 'ScheduleWakeup']) assert.ok(o.disallowedTools?.includes(t), t);
  assert.ok(!o.disallowedTools?.some((t) => t.startsWith('mcp__studio')));
});

test('session wiring passes through', () => {
  const canUseTool = async () => ({ behavior: 'deny' as const, message: 'x' });
  const o = buildSessionOptions({ ...base, kind: 'run', model: 'sonnet', resume: 'abc', executable: '/bin/claude', canUseTool });
  assert.equal(o.resume, 'abc');
  assert.equal(o.pathToClaudeCodeExecutable, '/bin/claude');
  assert.equal(o.canUseTool, canUseTool);
  assert.deepEqual(o.systemPrompt, { type: 'preset', preset: 'claude_code', append: 'X' });
});
