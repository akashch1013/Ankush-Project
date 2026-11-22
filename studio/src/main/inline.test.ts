import { test } from 'node:test';
import assert from 'node:assert/strict';
import { applyEdits } from './inline.ts';

const html = `<!doctype html><html><head><title>t</title></head><body>
<div class="page"><div class="bubble">Hello   <b>Tez</b>!</div>
<p class="cap">Second line</p><span data-math="2 + 2 = 4">2 + 2 = 4</span></div>
<!-- keep me --></body></html>`;

test('edits only the targeted element', () => {
  const r = applyEdits(html, [{ path: [0, 1], oldText: 'Second line', newText: 'Second line!', newHtml: 'Second line!' }]);
  assert.equal(r.applied, 1);
  assert.equal(r.html, html.replace('Second line</p>', 'Second line!</p>'));
});

test('falls back to unique text when the path is stale, keeps inline markup', () => {
  const r = applyEdits(html, [{ path: [5, 5], oldText: 'Hello Tez!', newText: 'Hi Tez!', newHtml: 'Hi <b>Tez</b>!' }]);
  assert.equal(r.applied, 1);
  assert.match(r.html, /<div class="bubble">Hi <b>Tez<\/b>!<\/div>/);
  assert.match(r.html, /<!-- keep me -->/);
});

test('data-math follows the text and flags maths', () => {
  const r = applyEdits(html, [{ path: [0, 2], oldText: '2 + 2 = 4', newText: '2 + 3 = 5', newHtml: '2 + 3 = 5' }]);
  assert.equal(r.mathChanged, true);
  assert.match(r.html, /<span data-math="2 \+ 3 = 5">2 \+ 3 = 5<\/span>/);
});

test('unknown text is skipped', () => {
  const r = applyEdits(html, [{ path: [9], oldText: 'nope', newText: 'x', newHtml: 'x' }]);
  assert.equal(r.applied, 0);
  assert.equal(r.html, html);
});
