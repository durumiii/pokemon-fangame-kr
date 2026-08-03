// app.js 순수 로직 자체점검 — 브라우저 없이: node webapp/tests/selfcheck.js
const fs = require('fs'), vm = require('vm'), a = require('assert'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', 'app.js'), 'utf8');
const els = {};
const el = id => els[id] ??= { value: '', textContent: '', className: '', dataset: {},
                               classList: { add() {}, remove() {} }, addEventListener() {},
                               style: {} };
const ctx = {
  document: {
    getElementById: el,
    createElement: () => ({
      set textContent(v) { this._t = v; },
      get innerHTML() { return String(this._t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); },
    }),
  },
  localStorage: { _m: {}, getItem(k) { return this._m[k] ?? null; }, setItem(k, v) { this._m[k] = v; } },
  addEventListener() {}, confirm: () => true,
  setTimeout, clearTimeout, console,
};
vm.createContext(ctx);
// const/let은 vm 전역에 붙지 않으므로 명시적으로 꺼낸다
vm.runInContext(src + '\n;globalThis.X = {rid, esc, MARKUP, S, persist, restoreEdits, save,' +
  ' setHits: h => { HITS = h; }};', ctx);
Object.assign(ctx, ctx.X);

a.equal(ctx.rid({ sec: 0, map: 3, idx: 7 }), '0:3:7');
a.equal(ctx.rid({ sec: 23, idx: 7 }), '23:-1:7');           // map 없는 절도 안정된 키
a.equal(ctx.esc('a"<b>&'), 'a&quot;&lt;b&gt;&amp;');        // 속성값 따옴표 탈출

const orig = '\\c[2]안녕 {1}\\PN';
const found = orig.match(ctx.MARKUP);
a.deepEqual(found, ['\\c[2]', '{1}', '\\PN']);
a.deepEqual(found.filter(t => !'안녕 {1}'.includes(t)), ['\\c[2]', '\\PN']);  // 사라진 코드만 경고

ctx.S.sha = 'abc';
ctx.S.edits = new Map([['0:1:2', { sec: 0, map: 1, idx: 2, k: 'x', v: 'y' }]]);
ctx.persist();
ctx.S.edits = new Map();
ctx.restoreEdits();
a.equal(ctx.S.edits.get('0:1:2').v, 'y');                   // localStorage 왕복

// CR이 든 값: textarea가 돌려주는 LF 형태로 저장을 눌러도 수정으로 잡히면 안 된다
const cr = { sec: 23, idx: 5, v: '첫 줄\r\n둘째 줄' };
ctx.S.edits = new Map();
ctx.setHits([cr]);
el('v0').value = cr.v.replace(/\r\n?/g, '\n');
ctx.save(0);
a.equal(ctx.S.edits.size, 0);
el('v0').value = '고친 줄';                                // 진짜 수정은 잡혀야 한다
ctx.save(0);
a.equal(ctx.S.edits.get('23:-1:5').v, '고친 줄');

console.log('SELFCHECK_OK');
