// app.js 순수 로직 자체점검 — 브라우저 없이: node webapp/tests/selfcheck.js
const fs = require('fs'), vm = require('vm'), a = require('assert'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', 'app.js'), 'utf8');
const els = {};
const el = id => els[id] ??= { value: '', textContent: '', className: '', dataset: {},
                               classList: { add() {}, remove() {} }, addEventListener() {},
                               style: {}, click() {} };
const ctx = {
  document: {
    getElementById: el,
    createElement: () => ({
      set textContent(v) { this._t = v; },
      get innerHTML() { return String(this._t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); },
      click() {}, href: '', download: '',
    }),
  },
  localStorage: { _m: {}, getItem(k) { return this._m[k] ?? null; }, setItem(k, v) { this._m[k] = v; },
                  removeItem(k) { delete this._m[k]; } },
  URL: { createObjectURL: () => 'blob:mock', revokeObjectURL() {} },
  Blob: class { constructor(parts, opts) { this.parts = parts; this.type = opts?.type; } },
  FormData: class { constructor() { this._m = new Map(); } append(k, v) { this._m.set(k, v); } },
  fetch: async (...args) => { ctx.__lastFetch = args; return {}; },
  addEventListener() {}, confirm: () => true, prompt: () => '',
  setTimeout, clearTimeout, console,
  // 메모리 IndexedDB 목업 — app.js의 idbDo가 쓰는 만큼만(open→transaction→get/put→oncomplete)
  indexedDB: {
    _kv: new Map(),
    open() {
      const rq = {};
      setTimeout(() => {
        rq.result = { transaction: () => {
          const tx = { objectStore: () => ({
            get: k => ({ result: ctx.indexedDB._kv.get(k) }),
            put: (v, k) => { ctx.indexedDB._kv.set(k, v); return {}; },
          }) };
          setTimeout(() => tx.oncomplete?.(), 0);
          return tx;
        } };
        rq.onsuccess();
      }, 0);
      return rq;
    },
  },
};
vm.createContext(ctx);
// const/let은 vm 전역에 붙지 않으므로 명시적으로 꺼낸다
// readFile/writeFile은 실제 소스 뒤에서 재정의해 브라우저 FS API 없이 build()를 목업 검증한다
// (같은 스코프의 함수 선언은 나중 정의가 이긴다)
vm.runInContext(src + `
;globalThis.X = {rid, esc, MARKUP, S, persist, restoreEdits, save, build, report,
  exportFix, importFix, showConflicts, pickConflict, CONFLICTS, REPORT_FORM,
  idbGet, idbSet, reopenFolder, migrateEdits, hist, histAll, memo, showHist,
  setHits: h => { HITS = h; }};
function readFile(){ return globalThis.__fsFile; }
function writeFile(){}
`, ctx);
Object.assign(ctx, ctx.X);

a.equal(ctx.rid({ sec: 0, map: 3, idx: 7 }), '0:3:7');
a.equal(ctx.rid({ sec: 23, idx: 7 }), '23:-1:7');           // map 없는 절도 안정된 키
a.equal(ctx.esc('a"<b>&'), 'a&quot;&lt;b&gt;&amp;');        // 속성값 따옴표 탈출

const orig = '\\c[2]안녕 {1}\\PN';
const found = orig.match(ctx.MARKUP);
a.deepEqual(found, ['\\c[2]', '{1}', '\\PN']);
a.deepEqual(found.filter(t => !'안녕 {1}'.includes(t)), ['\\c[2]', '\\PN']);  // 사라진 코드만 경고

ctx.S.sha = 'abc'; ctx.S.base = 'abc';
ctx.S.rows = [{ sec: 0, map: 1, idx: 2, k: 'x', v: '원문' }];   // 복원은 로드된 rows와 대조된다
ctx.S.edits = new Map([['0:1:2', { sec: 0, map: 1, idx: 2, k: 'x', v: 'y' }]]);
ctx.persist();
ctx.S.edits = new Map();
a.equal(ctx.restoreEdits(), 0);
a.equal(ctx.S.edits.get('0:1:2').v, 'y');                   // localStorage 왕복

// 패치 판이 바뀐 경우: 같은 rid에 다른 원문이 서 있으면 옛 수정을 얹지 않는다
ctx.S.rows = [{ sec: 0, map: 1, idx: 2, k: '새판원문', v: '새판' }];
a.equal(ctx.restoreEdits(), 1);                             // 1건 제외
a.equal(ctx.S.edits.size, 0);
a.ok(ctx.localStorage.getItem('edits:abc'));                // 저장분은 지우지 않는다(판을 되돌리면 살아난다)
ctx.S.rows = [{ sec: 0, map: 1, idx: 2, k: 'x', v: '원문' }];

// 기준 키 마이그레이션: 빌드된 dat(sha) 아래 있던 저장분이 순정 기준(base) 키로 1회 옮겨진다
ctx.localStorage.setItem('edits:builtsha', JSON.stringify([{ sec: 0, map: 1, idx: 2, k: 'x', v: '옛저장' }]));
ctx.S.sha = 'builtsha'; ctx.S.base = 'origbase';
ctx.migrateEdits();
a.equal(ctx.localStorage.getItem('edits:builtsha'), null);  // 옛 키는 사라지고
ctx.restoreEdits();
a.equal(ctx.S.edits.get('0:1:2').v, '옛저장');              // 새 기준 키에서 복원된다

// 이력 원장: append-only — 같은 행을 두 번 고쳐도 이벤트가 각각 쌓인다
ctx.hist({ type: 'edit', rid: '0:1:2', k: 'x', old: 'a', new: 'b' });
ctx.hist({ type: 'edit', rid: '0:1:2', k: 'x', old: 'b', new: 'c' });
const h = ctx.histAll();
a.equal(h.length, 2);
a.equal(h[1].new, 'c');
a.ok(h[0].t && !Number.isNaN(Date.parse(h[0].t)));          // ISO 시각이 붙는다

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
a.deepEqual(                                               // 수정은 구→신으로 이력에 남는다
  (({ type, rid, old, new: nv }) => ({ type, rid, old, new: nv }))(ctx.histAll().at(-1)),
  { type: 'edit', rid: '23:-1:5', old: cr.v, new: '고친 줄' });

// 메모: 이력에만 쌓이고 edits(빌드 대상)는 건드리지 않는다
const editsBefore = ctx.S.edits.size;
el('m0').value = '  이 대사 어투 확인 필요  ';
ctx.memo(0);
a.equal(ctx.S.edits.size, editsBefore);                    // 빌드에는 안 들어간다
a.deepEqual(
  (({ type, rid, text }) => ({ type, rid, text }))(ctx.histAll().at(-1)),
  { type: 'memo', rid: '23:-1:5', text: '이 대사 어투 확인 필요' });   // 앞뒤 공백은 다듬어 저장
a.equal(el('m0').value, '');                               // 입력칸은 비워진다

// 내보내기: 헤더 1행 + 수정마다 1행, S.edits 값 그대로
ctx.S.sha = 'expsha'; ctx.S.meta = null;
ctx.S.edits = new Map([['0:1:2', { sec: 0, map: 1, idx: 2, k: 'x', v: 'exported' }]]);
let capturedBlobText = null;
ctx.URL.createObjectURL = b => { capturedBlobText = b.parts.join(''); return 'blob:mock'; };
ctx.exportFix();
const expLines = capturedBlobText.trim().split('\n').map(l => JSON.parse(l));
a.deepEqual(expLines[0], { app: 'studio-1', patch: 'expsha' });   // meta 없으면 sha로 대체
a.deepEqual(expLines[1], { sec: 0, map: 1, idx: 2, k: 'x', v: 'exported' });

// 빌드 성공: edits 비움 + 옛 sha localStorage 키 제거 (readFile/writeFile은 위에서 목업으로 교체됨)
const VMU8 = vm.runInContext('Uint8Array', ctx);   // vm 밖에서 만든 Uint8Array는 vm의 instanceof를 못 통과한다
(async () => {
  // 가져오기: 병합 1건 + 원문 불일치 건너뜀 1건
  ctx.S.rows = [
    { sec: 0, map: 1, idx: 2, k: 'x', v: '원문' },     // rid 0:1:2, k 일치 → 병합 대상
    { sec: 0, map: 1, idx: 3, k: 'z', v: '원문2' },    // rid 0:1:3, k 불일치로 건너뜀 대상
  ];
  ctx.S.edits = new Map();
  ctx.S.sha = 'newsha2';
  const importLines = [
    JSON.stringify({ app: 'studio-1', patch: 'expsha' }),
    JSON.stringify({ sec: 0, map: 1, idx: 2, k: 'x', v: '고침A' }),   // 병합됨
    JSON.stringify({ sec: 0, map: 1, idx: 3, k: 'w', v: '고침B' }),   // k 불일치 → 건너뜀
  ].join('\n') + '\n';
  ctx.importFix();
  await el('importfile').onchange({ target: { files: [{ text: async () => importLines }], value: 'x' } });
  a.equal(ctx.S.edits.get('0:1:2').v, '고침A');                       // 병합 반영
  a.equal(ctx.S.edits.has('0:1:3'), false);                           // 원문 불일치 건너뜀
  a.ok(el('meta').textContent.includes('1건 병합') && el('meta').textContent.includes('1건 건너뜀'));

  // 가져오기 충돌: 같은 행을 내가 이미 다르게 고쳤으면 충돌 카드로 분기하고 값은 아직 안 바뀐다
  ctx.S.edits = new Map([['0:1:2', { sec: 0, map: 1, idx: 2, k: 'x', v: '내수정' }]]);
  const conflictLines = [
    JSON.stringify({ app: 'studio-1', patch: 'expsha' }),
    JSON.stringify({ sec: 0, map: 1, idx: 2, k: 'x', v: '가져온수정' }),
  ].join('\n') + '\n';
  ctx.importFix();
  await el('importfile').onchange({ target: { files: [{ text: async () => conflictLines }], value: 'x' } });
  a.equal(ctx.S.edits.get('0:1:2').v, '내수정');                       // 충돌 중엔 아직 내 값 유지
  a.ok(el('out').innerHTML.includes('겹치는 1행'));                    // 충돌 카드 렌더
  ctx.pickConflict(0, 1);                                             // "가져온 것"을 선택
  a.equal(ctx.S.edits.get('0:1:2').v, '가져온수정');                   // 선택 반영

  // 깨진 줄 하나 섞여도 나머지 정상 줄은 병합돼야 한다 (JSON.parse 실패가 파일 전체를 날리면 안 됨)
  ctx.S.edits = new Map();
  const mixedLines = [
    JSON.stringify({ app: 'studio-1', patch: 'expsha' }),
    '{이건 JSON이 아님',
    JSON.stringify({ sec: 0, map: 1, idx: 2, k: 'x', v: '정상병합' }),
  ].join('\n') + '\n';
  ctx.importFix();
  await el('importfile').onchange({ target: { files: [{ text: async () => mixedLines }], value: 'x' } });
  a.equal(ctx.S.edits.get('0:1:2').v, '정상병합');                     // 깨진 줄 무시하고 나머지 병합
  a.ok(el('meta').textContent.includes('1건 병합') && el('meta').textContent.includes('1건 건너뜀'));

  // v가 문자열이 아닌 줄(예: 객체)은 병합하지 않고 건너뜀 처리해야 한다
  ctx.S.edits = new Map();
  const badTypeLines = [
    JSON.stringify({ app: 'studio-1', patch: 'expsha' }),
    JSON.stringify({ sec: 0, map: 1, idx: 2, k: 'x', v: { oops: true } }),
  ].join('\n') + '\n';
  ctx.importFix();
  await el('importfile').onchange({ target: { files: [{ text: async () => badTypeLines }], value: 'x' } });
  a.equal(ctx.S.edits.has('0:1:2'), false);                           // v 타입 이상 → 병합 안 됨
  a.ok(el('meta').textContent.includes('0건 병합') && el('meta').textContent.includes('1건 건너뜀'));

  // 파일 전체가 JSON이 아니면 병합 시도 없이 한국어 안내로 끝나야 한다
  ctx.S.edits = new Map();
  ctx.importFix();
  await el('importfile').onchange({ target: { files: [{ text: async () => 'not json at all\nstill not json\n' }], value: 'x' } });
  a.equal(ctx.S.edits.size, 0);
  a.equal(el('toast').textContent, '고침 파일 형식이 아니에요');       // 한국어 안내로 종료

  ctx.__fsFile = new VMU8([1, 2, 3]);
  ctx.S.dir = {};
  ctx.S.py = { toPy: x => x };
  ctx.S.core = {
    build_dat: () => new VMU8([9, 9]),                      // Uint8Array 분기 — pyBuild가 그대로 반환
    load_dat: () => JSON.stringify({ meta: null, sha: 'newsha', rows: [] }),
  };
  ctx.S.sha = 'oldsha'; ctx.S.base = 'buildbase';
  ctx.S.edits = new Map([['0:1:2', { sec: 0, map: 1, idx: 2, k: 'x', v: 'y' }]]);
  ctx.persist();
  await ctx.build();
  a.equal(ctx.S.edits.size, 0);                             // 빌드 성공 시 edits 비움
  a.deepEqual(JSON.parse(ctx.localStorage.getItem('edits:buildbase')), []);  // 기준 키는 그대로, 내용만 비움
  a.equal(ctx.S.sha, 'newsha');                              // 새 dat로 상태 재동기화
  a.deepEqual(ctx.histAll().at(-1).type, 'build');           // 빌드도 이력에 남는다

  // 제보: 6필드가 FormData에 담기고 no-cors POST로 fetch가 불려야 한다
  ctx.REPORT_FORM.id = 'formid123';
  Object.assign(ctx.REPORT_FORM.entries, {sec:'e.sec', idx:'e.idx', k:'e.k', v:'e.v', suggest:'e.suggest', patch:'e.patch'});
  ctx.S.meta = null; ctx.S.sha = 'reportsha';
  const reportRow = { sec: 3, map: 7, idx: 9, k: '원문키', v: '원문값' };
  ctx.setHits([reportRow]);
  el('v0').value = '원문값';                                          // 무편집 → suggest는 prompt(빈 문자열) 결과
  await ctx.report(0);
  const [reportUrl, reportInit] = ctx.__lastFetch;
  a.equal(reportUrl, 'https://docs.google.com/forms/d/e/formid123/formResponse');
  a.equal(reportInit.method, 'POST'); a.equal(reportInit.mode, 'no-cors');
  const fd = reportInit.body._m;
  a.equal(fd.get('e.sec'), '3:도감 설명');
  a.equal(fd.get('e.idx'), '7:9');
  a.equal(fd.get('e.k'), '원문키');
  a.equal(fd.get('e.v'), '원문값');
  a.equal(fd.get('e.suggest'), '');                                   // 무편집이면 빈 코멘트
  a.equal(fd.get('e.patch'), 'hash:reportsha / studio-1');            // meta 없으면 hash:sha로 대체

  // 폴더 핸들 보존: IndexedDB 왕복 + 권한 거부 시 폴백
  a.equal(await ctx.idbGet('dirHandle'), undefined);          // 처음엔 비어 있다
  const fakeHandle = { name: 'PokemonZ', _perm: 'denied',
                       requestPermission: async () => fakeHandle._perm };
  await ctx.idbSet('dirHandle', fakeHandle);
  a.equal((await ctx.idbGet('dirHandle')).name, 'PokemonZ');  // 저장한 핸들이 그대로 돌아온다

  ctx.S.dir = 'unchanged';
  await ctx.reopenFolder();                                   // 권한 거부 → 로드하지 않고 안내만
  a.equal(ctx.S.dir, 'unchanged');
  a.ok(el('toast').textContent.includes('폴더 접근 권한이 없어요'));

  console.log('SELFCHECK_OK');
})().catch(e => { console.error(e); process.exit(1); });
