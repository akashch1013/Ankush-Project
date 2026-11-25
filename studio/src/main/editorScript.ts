// Injected into a page's index.html when it is opened in Studio's editor (studio://file/...index.html?edit=1).
// Talks to the parent window with postMessage only; the page file itself is never touched by this script.
export const EDITOR_SCRIPT = String.raw`
(function () {
  var INLINE = { B:1, I:1, EM:1, STRONG:1, SPAN:1, BR:1, SUP:1, SUB:1, SMALL:1, U:1, MARK:1 };
  var mode = 'view';
  var originals = new WeakMap();
  var style = document.createElement('style');
  style.textContent =
    '.studio-cand{outline:2px dashed rgba(0,170,255,.85)!important;outline-offset:2px;cursor:text}' +
    '.studio-edit{outline:2px solid #00aaff!important;outline-offset:2px;background:rgba(0,170,255,.08)!important}' +
    '.studio-changed{outline:2px solid #f5a623!important;outline-offset:2px}' +
    '.studio-math{outline-color:#e5484d!important}' +
    '.studio-img{outline:3px dashed #b48cff!important;outline-offset:-3px;cursor:pointer}';
  document.head.appendChild(style);

  function editable(el) {
    if (!el || el.nodeType !== 1 || el === document.body) return false;
    if (el.closest('svg,script,style')) return false;
    var hasText = false;
    for (var i = 0; i < el.childNodes.length; i++) {
      var n = el.childNodes[i];
      if (n.nodeType === 3 && n.nodeValue.trim()) hasText = true;
    }
    if (!hasText) return false;
    var all = el.querySelectorAll('*');
    for (var j = 0; j < all.length; j++) if (!INLINE[all[j].tagName]) return false;
    return true;
  }
  function target(el) {
    while (el && el !== document.body) {
      if (editable(el)) {
        // Prefer the outermost inline-only block (a whole bubble, not one <b> inside it).
        var p = el.parentElement;
        while (p && p !== document.body && editable(p)) { el = p; p = p.parentElement; }
        return el;
      }
      el = el.parentElement;
    }
    return null;
  }
  function path(el) {
    var out = [];
    while (el && el !== document.body) {
      var p = el.parentElement, i = 0;
      for (var c = p.firstElementChild; c && c !== el; c = c.nextElementSibling) i++;
      out.unshift(i);
      el = p;
    }
    return out;
  }
  function isMath(el) { return el.hasAttribute('data-math') || !!el.closest('[data-math]') || !!el.querySelector('[data-math]'); }
  function post(m) { parent.postMessage(Object.assign({ studio: true }, m), '*'); }

  var hover = null;
  document.addEventListener('mouseover', function (e) {
    if (hover) hover.classList.remove('studio-cand');
    hover = null;
    if (mode !== 'text') return;
    var t = target(e.target);
    if (t && !t.isContentEditable) { t.classList.add('studio-cand'); if (isMath(t)) t.classList.add('studio-math'); hover = t; }
  }, true);

  document.addEventListener('click', function (e) {
    if (mode === 'image') {
      var img = e.target.closest && e.target.closest('img');
      if (img) { e.preventDefault(); e.stopPropagation(); post({ type: 'image', src: img.getAttribute('src') || '', alt: img.getAttribute('alt') || '' }); }
      return;
    }
    if (mode !== 'text') return;
    var t = target(e.target);
    if (!t) return;
    e.preventDefault();
    if (!originals.has(t)) originals.set(t, { text: t.textContent, path: path(t) });
    t.contentEditable = 'true';
    t.classList.remove('studio-cand');
    t.classList.add('studio-edit');
    t.focus();
  }, true);

  document.addEventListener('focusout', function (e) {
    var t = e.target;
    if (!t || !t.classList || !t.classList.contains('studio-edit')) return;
    t.contentEditable = 'false';
    t.classList.remove('studio-edit');
    var o = originals.get(t);
    if (!o) return;
    var changed = t.textContent !== o.text;
    t.classList.toggle('studio-changed', changed);
    post({ type: 'edit', key: o.path.join('.'), edit: { path: o.path, oldText: o.text, newHtml: t.innerHTML, newText: t.textContent }, changed: changed, math: isMath(t) });
  }, true);

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && document.activeElement && document.activeElement.isContentEditable) document.activeElement.blur();
  }, true);

  window.addEventListener('message', function (e) {
    var d = e.data || {};
    if (d.type === 'mode') {
      mode = d.mode;
      document.querySelectorAll('img').forEach(function (i) { i.classList.toggle('studio-img', mode === 'image'); });
    }
  });
  post({ type: 'ready' });
})();
`;
