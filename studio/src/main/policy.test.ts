import { test } from 'node:test';
import assert from 'node:assert/strict';
import { hardRule, presetDecision } from './policy.ts';

const T = '/repo/Tasks';

test('protected folders are never editable', () => {
  assert.equal(hardRule('Write', { file_path: 'Reference/Chap 2/x.docx' }, T)?.kind, 'deny');
  assert.equal(hardRule('Edit', { file_path: '/repo/Charactors/CHANDRUSH CHARACTERS/a.png' }, T)?.kind, 'deny');
  assert.equal(hardRule('Bash', { command: 'rm -rf "Reference/Chap 2"' }, T)?.kind, 'deny');
  assert.equal(hardRule('Bash', { command: 'python3 pipeline/textcheck.py dump "Reference/Chap 2/CH02-PANELIZED-MANUSCRIPT-V01.docx" PdfSheetsGenTask/CH02/manuscript.txt' }, T), null);
  assert.equal(hardRule('Edit', { file_path: 'PdfSheetsGenTask/CH01/P039/index.html' }, T), null);
});

test('api key and immediate calls are denied, batch submit is spend', () => {
  assert.equal(hardRule('Read', { file_path: '/repo/Tasks/BagroundGenTask/.env' }, T)?.kind, 'deny');
  assert.equal(hardRule('Bash', { command: 'cat BagroundGenTask/.env' }, T)?.kind, 'deny');
  assert.equal(hardRule('Bash', { command: 'python3 pipeline/imggen.py --ws X gen A --immediate-approved' }, T)?.kind, 'deny');
  assert.equal(hardRule('Bash', { command: 'python3 pipeline/imggen.py --ws FInalChangesTask/CH01 batch submit CH01-w1' }, T)?.kind, 'spend');
  assert.equal(hardRule('Bash', { command: 'python3 pipeline/imggen.py --ws FInalChangesTask/CH01 batch build CH01-w1 --ready' }, T), null);
  assert.equal(hardRule('Write', { file_path: 'FInalChangesTask/CH01/jobs.json', content: '{"quality": "max"}' }, T)?.kind, 'deny');
});

test('the key in the environment is never printed', () => {
  for (const command of ['echo $OPENAI_API_KEY', 'printenv', 'env', 'env | grep sk', 'cat /proc/self/environ', 'python3 -c "import os; print(os.environ)"', 'ls && export -p'])
    assert.equal(hardRule('Bash', { command }, T)?.kind, 'deny', command);
  for (const command of ['set -e; python3 pipeline/pagekit.py render X', 'env FOO=1 python3 pipeline/contact.py x'])
    assert.equal(hardRule('Bash', { command }, T), null, command);
  assert.equal(hardRule('Edit', { file_path: '/repo/Tasks/Charactors/a.png' }, T)?.kind, 'deny');
});

test('pipeline-safe preset', () => {
  assert.equal(presetDecision('safe', 'Bash', { command: 'cd /repo/Tasks && python3 pipeline/pagekit.py render PdfSheetsGenTask/CH01/P039 2>&1 | tail -5' }, T), 'allow');
  assert.equal(presetDecision('safe', 'Bash', { command: 'python3 pipeline/textcheck.py survey PdfSheetsGenTask/CH02/src > PdfSheetsGenTask/CH02/survey.txt' }, T), 'allow');
  assert.equal(presetDecision('safe', 'Bash', { command: 'python3 - <<EOF\nprint(1)\nEOF' }, T), 'ask');
  assert.equal(presetDecision('safe', 'Bash', { command: 'curl https://example.com' }, T), 'ask');
  assert.equal(presetDecision('safe', 'Bash', { command: 'git push' }, T), 'ask');
  assert.equal(presetDecision('safe', 'Bash', { command: 'echo hi > ../studio/x' }, T), 'ask');
  assert.equal(presetDecision('safe', 'Write', { file_path: 'PdfSheetsGenTask/CH02/pages.json' }, T), 'allow');
  assert.equal(presetDecision('safe', 'Edit', { file_path: '/repo/.claude/skills/comic-master/SKILL.md' }, T), 'ask');
  assert.equal(presetDecision('safe', 'mcp__studio__request_review', {}, T), 'allow');
  assert.equal(presetDecision('ask', 'Write', { file_path: 'PdfSheetsGenTask/CH02/pages.json' }, T), 'ask');
  assert.equal(presetDecision('auto', 'Bash', { command: 'curl x' }, T), 'allow');
});
