// app.js 순수 로직 자체점검 — 브라우저 없이: node webapp/tests/selfcheck.js
const fs = require('fs'), vm = require('vm'), a = require('assert'), path = require('path');
// 브라우저와 같은 순서로 잇는다 — mine.js·hist.js·event.js는 app.js의 전역을 그대로 쓴다
const src = ['app.js', 'mine.js', 'hist.js', 'event.js']
  .map(f => fs.readFileSync(path.join(__dirname, '..', f), 'utf8')).join('\n');
const els = {};
const el = id => els[id] ??= { value: '', textContent: '', className: '', dataset: {},
                               classList: { _s: new Set(), add(c) { this._s.add(c); },
                                            remove(c) { this._s.delete(c); },
                                            contains(c) { return this._s.has(c); } },
                               addEventListener() {},
                               style: {}, click() {}, innerHTML: '', remove() {},
                               insertAdjacentHTML(_, html) { this.innerHTML += html; } };
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
  fetch: async (...args) => { ctx.__fetchCalls.push(args); ctx.__lastFetch = args; return {}; },
  __fetchCalls: [],
  crypto: { randomUUID: () => `uuid-${++ctx.__uuidN}` }, __uuidN: 0,
  // 선시동 목업 — 없으면(브라우저 밖) bootPy가 조용히 실패해야 하고, 있으면 몇 번 불려도 한 번만 떠야 한다
  loadPyodide: async () => { ctx.__pyodideCalls++;
    return { FS: { mkdirTree(){}, writeFile(){} }, pyimport: () => ({}), runPython(){} }; },
  __pyodideCalls: 0,
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
  doRestore, reloadAfterRestore, batchReport, canReport, card,
  memoIndex, renderHome, updateDirty, FIELD_CAP, memoDel, persistMemos,
  showMine, mineSave, mineCancel, mineMemoDel, reporterId,
  editOps, undoOp, opBegin, opEnd, opCard, HIST_OPS, ops: () => OPS,
  clearMemos: () => { MEMOS = null; },
  markAllSent, sentIndex, clearSent: () => { SENT = null; },
  loadSpeakers, fillBrowse, doBrowse, openGroup, browseGroups, spkOf, mapName,
  evOf, evName, evLabel, eventRows, evJump, openSpot, openEvent,
  setFocus: v => { FOCUS = v; },
  parseQuery, rowMatch, search, goHome, tagValues,
  GENERAL_FORM, feedbackMenu, sendFeedback,
  setSpk: v => { SPK = v; MAPNAME = null; }, BROWSE_CAP,
  applyEdit, replaceMenu, replacePreview, replaceApply, replAll, REPL_CAP,
  replHits: () => REPL,
  setHits: h => { HITS = h; }, hits: () => HITS, bootPy,
  resetBoot: () => { bootPromise = null; bootAnnounce = false; }};
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

// 이력 기록: append-only — 같은 행을 두 번 고쳐도 이벤트가 각각 쌓인다
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
ctx.S.sha = 'expsha'; ctx.S.base = 'expbase'; ctx.S.meta = null;
ctx.S.edits = new Map([['0:1:2', { sec: 0, map: 1, idx: 2, k: 'x', v: 'exported' }]]);
ctx.S.applied = new Map();
let capturedBlobText = null;
const exported = () => { capturedBlobText = null; ctx.exportFix();
  return capturedBlobText === null ? null : capturedBlobText.trim().split('\n').map(l => JSON.parse(l)); };
ctx.URL.createObjectURL = b => { capturedBlobText = b.parts.join(''); return 'blob:mock'; };
const expLines = exported();
a.deepEqual(expLines[0], { app: 'studio-1', patch: 'expbase' });  // meta 없으면 순정 기준 해시(빌드마다 바뀌는 sha 아님)
a.deepEqual(expLines[1], { sec: 0, map: 1, idx: 2, k: 'x', v: 'exported' });

// 내보내기 합집합: 이미 빌드된 applied도 함께 나가고, 같은 행은 아직 안 빌드된 pending이 이긴다
ctx.S.applied = new Map([
  ['0:1:2', { sec: 0, map: 1, idx: 2, k: 'x', v: '빌드된값' }],       // pending과 겹침 → 밀린다
  ['0:1:9', { sec: 0, map: 1, idx: 9, k: 'q', v: '빌드만된값' }]]);   // pending에 없음 → 그대로 나간다
const unionLines = exported().slice(1);
a.equal(unionLines.length, 2);
a.equal(unionLines.find(e => e.idx === 2).v, 'exported');            // pending 우선
a.equal(unionLines.find(e => e.idx === 9).v, '빌드만된값');

// 양쪽 다 비었을 때만 "내보낼 수정 없음" — applied만 있어도 내보낼 수 있어야 한다
ctx.S.edits = new Map();
a.equal(exported().slice(1).length, 2);                             // applied 2건만으로도 파일이 나온다
ctx.S.applied = new Map();
a.equal(exported(), null);                                          // 둘 다 비면 파일 없음
a.equal(el('toast').textContent, '내보낼 수정이 없어요');

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
    // Uint8Array 분기 — pyBuild가 그대로 반환. 빌드가 도는 동안의 복원 버튼 상태를 여기서 엿본다
    build_dat: () => { lockDuringBuild = el('restorebtn').disabled; return new VMU8([9, 9]); },
    load_dat: () => JSON.stringify({ meta: null, sha: 'newsha', rows: [] }),
  };
  ctx.S.sha = 'oldsha'; ctx.S.base = 'buildbase';
  ctx.S.edits = new Map([['0:1:2', { sec: 0, map: 1, idx: 2, k: 'x', v: 'y' }]]);
  ctx.S.applied = new Map();
  ctx.persist();
  let lockDuringBuild = null;
  el('restorebtn').disabled = false;
  await ctx.build();
  a.equal(lockDuringBuild, true);                           // 빌드 도는 동안 복원은 잠긴다(맞잠금)
  a.equal(el('restorebtn').disabled, false);                // 끝나면 함께 풀린다
  a.equal(ctx.S.edits.size, 0);                             // 빌드 성공 시 edits 비움
  a.equal(ctx.S.applied.get('0:1:2').v, 'y');               // 비운 게 아니라 applied로 옮겨진다
  a.deepEqual(JSON.parse(ctx.localStorage.getItem('edits:buildbase')), []);  // 기준 키는 그대로, 내용만 비움
  a.deepEqual(JSON.parse(ctx.localStorage.getItem('applied:buildbase')),     // applied도 같은 기준 키로 저장
    [{ sec: 0, map: 1, idx: 2, k: 'x', v: 'y' }]);
  a.equal(ctx.S.sha, 'newsha');                              // 새 dat로 상태 재동기화
  a.deepEqual(ctx.histAll().at(-1).type, 'build');           // 빌드도 이력에 남는다

  // applied 복원: 로드 시 edits와 같은 원문 대조로 걸러 되살아난다
  ctx.S.rows = [{ sec: 0, map: 1, idx: 2, k: 'x', v: 'y' }];
  ctx.restoreEdits();
  a.equal(ctx.S.applied.get('0:1:2').v, 'y');
  ctx.S.rows = [{ sec: 0, map: 1, idx: 2, k: '새판원문', v: 'y' }];
  ctx.restoreEdits();
  a.equal(ctx.S.applied.size, 0);                            // 판이 바뀌면 applied도 제외

  // 가져오기 충돌: 이미 빌드된 내 수정(applied)과 겹쳐도 충돌로 잡혀야 한다(조용히 덮이면 안 됨)
  ctx.S.rows = [{ sec: 0, map: 1, idx: 2, k: 'x', v: '원문' }];
  ctx.S.edits = new Map();
  ctx.S.applied = new Map([['0:1:2', { sec: 0, map: 1, idx: 2, k: 'x', v: '빌드된내수정' }]]);
  ctx.importFix();
  await el('importfile').onchange({ target: { files: [{ text: async () =>
    JSON.stringify({ sec: 0, map: 1, idx: 2, k: 'x', v: '가져온수정' }) + '\n' }], value: 'x' } });
  a.equal(ctx.S.edits.has('0:1:2'), false);                   // 병합 대신 충돌 카드로 분기
  a.ok(el('out').innerHTML.includes('겹치는 1행'));
  a.ok(el('out').innerHTML.includes('빌드된내수정'));          // "내 것"으로 applied 값이 제시된다

  // 복원: applied(반영됨)는 pending으로 합류하고, 새 dat 재로드까지 끝나야 빌드·내보내기가 열린다
  ctx.S.edits = new Map([['0:1:2', { sec: 0, map: 1, idx: 2, k: 'x', v: '미빌드수정' }]]);
  ctx.S.applied = new Map([
    ['0:1:2', { sec: 0, map: 1, idx: 2, k: 'x', v: '빌드된값' }],      // pending과 겹침 → pending 유지
    ['0:1:9', { sec: 0, map: 1, idx: 9, k: 'q', v: '빌드만된값' }]]);  // 겹치지 않음 → pending으로 이동
  ctx.S.base = 'restorebase';
  el('buildbtn').disabled = false; el('exportbtn').disabled = false;
  await ctx.doRestore('Data/korean.dat.bak');
  a.equal(ctx.S.applied.size, 0);                            // "반영됨" 표시는 사라지고
  a.equal(ctx.S.edits.get('0:1:2').v, '미빌드수정');          // 겹친 행은 미빌드분이 이긴다
  a.equal(ctx.S.edits.get('0:1:9').v, '빌드만된값');          // 반영됐던 수정은 잃지 않고 pending으로
  a.deepEqual(JSON.parse(ctx.localStorage.getItem('applied:restorebase')), []);  // 저장분도 함께 비움
  a.equal(ctx.histAll().at(-1).type, 'restore');
  a.equal(el('buildbtn').disabled, false);                   // 재로드까지 끝났으니 다시 열린다
  a.equal(el('exportbtn').disabled, false);

  // 재로드 실패: 파일은 복원됐지만 화면은 옛 기준 — 빌드·내보내기는 잠긴 채로 [다시 불러오기]만 준다
  const goodLoad = ctx.S.core.load_dat;
  ctx.S.core.load_dat = () => { throw new Error('재로드 실패 목업'); };
  await ctx.doRestore('Data/korean.dat.bak');
  a.equal(el('buildbtn').disabled, true);
  a.equal(el('exportbtn').disabled, true);
  a.equal(el('restorebtn').disabled, false);                 // 복원 버튼만 풀어 다시 시도할 수 있게
  a.ok(el('out').innerHTML.includes('다시 불러오기'));
  ctx.S.core.load_dat = goodLoad;
  await ctx.reloadAfterRestore('Data/korean.dat.bak');        // 완료 카드의 버튼이 하는 일
  a.equal(el('buildbtn').disabled, false);
  a.equal(el('exportbtn').disabled, false);

  // 빌드 경합: 빌드 도는 사이 저장된 수정이 반영됨으로 잘못 넘어가면 안 된다(스냅샷 이후분은 pending 유지)
  ctx.S.sha = 'oldrace'; ctx.S.base = 'racebase';
  ctx.S.edits = new Map([['0:1:2', { sec: 0, map: 1, idx: 2, k: 'x', v: 'y' }]]);
  ctx.S.applied = new Map();
  ctx.S.core = {
    build_dat: () => {
      // build_dat이 도는 동안 다른 저장이 끼어든 상황을 흉내낸다: 같은 rid 재수정 + 새 rid 추가
      ctx.S.edits.set('0:1:2', { sec: 0, map: 1, idx: 2, k: 'x', v: '다시고침' });
      ctx.S.edits.set('0:1:9', { sec: 0, map: 1, idx: 9, k: 'z', v: '새로추가' });
      return new VMU8([9, 9]);
    },
    load_dat: () => JSON.stringify({ meta: null, sha: 'newrace', rows: [] }),
  };
  await ctx.build();
  a.equal(ctx.S.applied.has('0:1:2'), false);                 // 스냅샷 이후 재수정된 rid는 반영 처리되지 않는다
  a.equal(ctx.S.edits.get('0:1:2').v, '다시고침');             // pending에 최신 값 그대로 남는다
  a.equal(ctx.S.edits.get('0:1:9').v, '새로추가');             // 스냅샷 이후 추가분도 pending 유지

  // 제보: 7필드가 FormData에 담기고 no-cors POST로 fetch가 불려야 한다
  ctx.REPORT_FORM.id = 'formid123';
  Object.assign(ctx.REPORT_FORM.entries, {sec:'e.sec', idx:'e.idx', k:'e.k', v:'e.v',
    suggest:'e.suggest', comment:'e.comment', patch:'e.patch'});
  ctx.S.meta = null; ctx.S.sha = 'reportsha';
  const reportRow = { sec: 3, map: 7, idx: 9, k: '원문키', v: '원문값' };
  ctx.setHits([reportRow]);
  el('v0').value = '원문값';                                          // 무편집 → suggest는 prompt(빈 문자열) 결과
  const reporterId = ctx.reporterId();                                // 최초 호출 시 발급되어 이후 재사용된다
  a.equal(ctx.reporterId(), reporterId);                              // 두 번 불러도 같은 해시(localStorage 재사용)
  await ctx.report(0);
  const [reportUrl, reportInit] = ctx.__lastFetch;
  a.equal(reportUrl, 'https://docs.google.com/forms/d/e/formid123/formResponse');
  a.equal(reportInit.method, 'POST'); a.equal(reportInit.mode, 'no-cors');
  const fd = reportInit.body._m;
  a.equal(fd.get('e.sec'), '3:도감 설명');
  a.equal(fd.get('e.idx'), '7:9');
  a.equal(fd.get('e.k'), '원문키');
  a.equal(fd.get('e.v'), '원문값');
  a.equal(fd.get('e.suggest'), '');                                   // 저장한 수정이 없으면 빈 제안
  a.equal(fd.get('e.comment'), '');                                   // 메모가 없으면 prompt 결과(빈 문자열)
  a.equal(fd.get('e.patch'), `hash:reportsha / studio-1 / u:${reporterId.slice(0,8)}`); // meta 없으면 hash:sha로 대체 + 제보자 해시

  // 제안=내가 저장한 번역, 코멘트=그 행 메모 — 둘 다 있으면 물어보지 않는다
  ctx.S.rows = [reportRow];
  ctx.S.edits = new Map([['3:7:9', { sec: 3, map: 7, idx: 9, k: '원문키', v: '내가고친값' }]]);
  ctx.S.applied = new Map();
  ctx.memoIndex().set('3:7:9', { k: '원문키', text: '어투 확인 필요' });
  ctx.prompt = () => { throw new Error('메모가 있으면 물어보면 안 된다'); };
  await ctx.report(0);
  const fd2 = ctx.__lastFetch[1].body._m;
  a.equal(fd2.get('e.suggest'), '내가고친값');
  a.equal(fd2.get('e.comment'), '어투 확인 필요');

  // 제보 prompt 취소(null)는 전송하지 않는다
  ctx.S.edits = new Map();
  ctx.S.rows = [{ sec: 3, map: 7, idx: 9, k: '원문키', v: '원문값' }];
  const noMemoRow = { sec: 5, map: null, idx: 1, k: '메모없는키', v: '메모없는값' };
  ctx.setHits([noMemoRow]);
  ctx.prompt = () => null;
  ctx.__lastFetch = null;
  await ctx.report(0);
  a.equal(ctx.__lastFetch, null);                                     // fetch 자체가 안 불린다
  ctx.prompt = () => '';

  // 제보 버튼 비활성: 수정도 메모도 없는 행만 잠긴다
  a.equal(ctx.canReport('5:-1:1'), false);
  a.ok(ctx.card(noMemoRow, 0).includes('disabled'));
  a.ok(ctx.card(noMemoRow, 0).includes('수정하거나 메모를 남긴 행만'));
  a.equal(ctx.canReport('3:7:9'), true);                              // 메모가 있으면 열린다
  ctx.setHits([reportRow]);
  a.ok(!ctx.card(reportRow, 0).includes('disabled'));
  ctx.S.applied = new Map([['5:-1:1', { sec: 5, map: null, idx: 1, k: '메모없는키', v: '반영된값' }]]);
  a.equal(ctx.canReport('5:-1:1'), true);                             // 반영됨(applied)도 제보 재료
  ctx.S.applied = new Map();

  // 일괄 제보: 항목마다 개별 제보와 같은 필드로 행 단위 전송, 「모아서」 표기는 patch 칸에만
  ctx.S.rows = [reportRow, { sec: 0, map: 1, idx: 2, k: '', v: '키없는원문' }];
  ctx.S.edits = new Map([['3:7:9', { sec: 3, map: 7, idx: 9, k: '원문키', v: '수정A' }]]);
  ctx.S.applied = new Map([['0:1:2', { sec: 0, map: 1, idx: 2, k: '', v: '수정B' }]]);
  // memoIndex()에는 위에서 넣어둔 '3:7:9' 메모가 그대로 남아 있다 → 3:7:9는 수정+메모 겹침, 0:1:2는 수정만
  ctx.__fetchCalls.length = 0;
  await ctx.batchReport();
  a.equal(ctx.__fetchCalls.length, 2);                                 // 수정이 있는 행 2건 — 개별 POST 2회
  const byIdx = ctx.__fetchCalls.map(([, init]) => init.body._m)
    .sort((x, y) => x.get('e.idx').localeCompare(y.get('e.idx')));
  const [rowA, rowB] = byIdx;                                          // idx '1:2' < idx '7:9' 사전순
  a.equal(rowA.get('e.sec'), '0:맵 대사'); a.equal(rowA.get('e.idx'), '1:2');
  a.equal(rowA.get('e.k'), ''); a.equal(rowA.get('e.v'), '키없는원문');
  a.equal(rowA.get('e.suggest'), '수정B'); a.equal(rowA.get('e.comment'), '');
  a.equal(rowB.get('e.sec'), '3:도감 설명'); a.equal(rowB.get('e.idx'), '7:9');
  a.equal(rowB.get('e.k'), '원문키'); a.equal(rowB.get('e.v'), '원문값');
  a.equal(rowB.get('e.suggest'), '수정A'); a.equal(rowB.get('e.comment'), '어투 확인 필요'); // 수정+메모 겹치는 행
  a.equal(rowA.get('e.patch'), `hash:reportsha / studio-1 / u:${reporterId.slice(0,8)} / 모아서`);
  a.equal(rowB.get('e.patch'), `hash:reportsha / studio-1 / u:${reporterId.slice(0,8)} / 모아서`);

  // 메모만 있고 수정이 없는 행은 comment만 채운 1행으로 간다
  ctx.S.edits = new Map(); ctx.S.applied = new Map();
  ctx.__fetchCalls.length = 0;
  await ctx.batchReport();
  a.equal(ctx.__fetchCalls.length, 1);
  const memoOnly = ctx.__fetchCalls[0][1].body._m;
  a.equal(memoOnly.get('e.sec'), '3:도감 설명'); a.equal(memoOnly.get('e.idx'), '7:9');
  a.equal(memoOnly.get('e.suggest'), ''); a.equal(memoOnly.get('e.comment'), '어투 확인 필요');

  // 30,000자 절단(단건 제보와 동일한 방어 로직, 일괄에서도 유지)
  ctx.S.edits = new Map([['3:7:9', { sec: 3, map: 7, idx: 9, k: '원문키', v: 'x'.repeat(40000) }]]);
  ctx.__fetchCalls.length = 0;
  await ctx.batchReport();
  const longSuggest = ctx.__fetchCalls[0][1].body._m.get('e.suggest');
  a.equal(longSuggest.length, ctx.FIELD_CAP + '…(이하 생략)'.length);
  a.ok(longSuggest.endsWith('…(이하 생략)'));

  // 재진입 가드: 전송 중 재호출은 fetch를 추가하지 않고 안내만 한다(no-cors라 중복 적재를 나중에 알 길이 없다)
  ctx.S.edits = new Map([['3:7:9', { sec: 3, map: 7, idx: 9, k: '원문키', v: '재진입값' }]]);
  ctx.__fetchCalls.length = 0;
  const inFlight = ctx.batchReport();              // 첫 호출 — await 전이라 아직 진행 중
  await ctx.batchReport();                          // 진행 중 재호출
  a.equal(el('toast').textContent, '일괄 제보가 진행 중이에요 — 끝날 때까지 기다려 주세요');
  await inFlight;
  a.equal(ctx.__fetchCalls.length, 1);              // 재호출로 fetch가 늘지 않았다 — 같은 행 중복 적재 없음

  // 같은 내용은 두 번 안 간다 — 일괄 제보가 저장분 전체를 매번 다시 던져 시트에 중복이 쌓였던 자리
  ctx.S.edits = new Map([['3:7:9', { sec: 3, map: 7, idx: 9, k: '원문키', v: '중복검사값' }]]);
  ctx.__fetchCalls.length = 0;
  await ctx.batchReport();
  a.equal(ctx.__fetchCalls.length, 1);
  await ctx.batchReport();                          // 그대로 다시 눌러도
  a.equal(ctx.__fetchCalls.length, 1);              // 한 건도 더 안 나간다
  a.equal(el('toast').textContent, '이미 보낸 1건뿐이에요 — 새로 보낼 게 없어요');
  ctx.S.edits = new Map([['3:7:9', { sec: 3, map: 7, idx: 9, k: '원문키', v: '중복검사값-고침' }]]);
  await ctx.batchReport();                          // 값을 고치면 서명이 달라져 다시 나간다
  a.equal(ctx.__fetchCalls.length, 2);

  // 「이미 보낸 것으로 표시」 — 이 기능 이전에 제보한 사람이 한 번 눌러 통째로 빼는 이주 수단
  ctx.S.edits = new Map([['3:7:9', { sec: 3, map: 7, idx: 9, k: '원문키', v: '이주값' }]]);
  ctx.markAllSent();
  ctx.__fetchCalls.length = 0;
  await ctx.batchReport();
  a.equal(ctx.__fetchCalls.length, 0);

  // 보낼 게 없으면 전송하지 않고 버튼도 잠긴다
  ctx.S.edits = new Map(); ctx.S.applied = new Map();
  ctx.localStorage.removeItem('hist:' + ctx.S.base);
  ctx.memoIndex().clear();
  ctx.updateDirty();
  a.equal(el('batchbtn').disabled, true);
  ctx.__lastFetch = null;
  await ctx.batchReport();
  a.equal(ctx.__lastFetch, null);
  a.equal(el('toast').textContent, '보낼 수정이나 메모가 없어요');

  // 홈 화면: 상태 요약 수치가 지금 상태와 맞아야 한다
  ctx.S.rows = [reportRow];
  ctx.S.edits = new Map([['3:7:9', { sec: 3, map: 7, idx: 9, k: '원문키', v: '수정A' }]]);
  ctx.S.applied = new Map([['0:1:2', { sec: 0, map: 1, idx: 2, k: '', v: '수정B' }]]);
  ctx.memoIndex().set('3:7:9', { k: '원문키', text: '메모1' });
  ctx.renderHome();
  const home = el('out').innerHTML;
  a.ok(home.includes('대기 1건') && home.includes('반영됨 1건') && home.includes('메모 1건'));
  a.ok(home.includes('모아서 제보') && home.includes('내보내기') && home.includes('이력'));
  ctx.updateDirty();
  a.equal(el('batchbtn').disabled, false);

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

  // ─ 일괄 바꾸기 ─
  // 미리보기는 지금 값(미빌드 수정 반영) 기준으로 찾고, 강조는 이스케이프한 뒤에 끼운다
  ctx.S.rows = [
    { sec: 0, map: 1, idx: 1, k: 'a', v: '메달을 받았다' },
    { sec: 0, map: 1, idx: 2, k: 'b', v: '<b>메달</b> 진열장' },      // 태그가 그대로 살아나면 안 된다
    { sec: 0, map: 1, idx: 3, k: 'c', v: '\\c[2]메달\\PN' },          // 치환이 코드를 삼키는 행
    { sec: 0, map: 1, idx: 4, k: 'd', v: '관계없는 행' },
  ];
  ctx.S.edits = new Map(); ctx.S.applied = new Map();
  ctx.S.base = 'replbase';
  ctx.replaceMenu();
  el('rfind').value = '메달'; el('rto').value = '배지';
  ctx.replacePreview();
  a.equal(ctx.replHits().length, 3);
  a.equal(el('meta').textContent, '3행 매칭');
  const prev = el('replout').innerHTML;
  a.ok(prev.includes('<mark>메달</mark>') && prev.includes('<mark>배지</mark>'));
  a.ok(prev.includes('&lt;b&gt;') && !prev.includes('<b>메달'));      // 원문 태그는 문자로만 나온다
  a.ok(prev.includes('id=rc0 checked'));                              // 멀쩡한 행은 기본 선택

  // 마크업을 삼키는 행은 자동 해제 + 경고, 나머지는 기본 선택
  el('rto').value = '';                                              // \c[2]메달\PN → \c[2]\PN? 아니, '메달'만 지운다
  ctx.replacePreview();
  const del = ctx.replHits();
  a.deepEqual(del.map(h => h.lost.length ? 1 : 0), [0, 0, 0]);       // '메달'만 지우면 코드는 남는다
  el('rfind').value = '\\c[2]메달'; el('rto').value = '메달';         // 이번엔 색 코드를 삼킨다
  ctx.replacePreview();
  const lostHit = ctx.replHits();
  a.equal(lostHit.length, 1);
  a.deepEqual(lostHit[0].lost, ['\\c[2]']);
  a.ok(el('replout').innerHTML.includes('색·이름 코드가 사라져요'));
  a.ok(!el('replout').innerHTML.includes('checked'));                 // 경고 행은 기본 해제
  el('rc0').checked = false;
  ctx.replAll(true);
  a.equal(el('rc0').checked, false);                                  // [모두 선택]도 경고 행은 건너뛴다
  a.ok(el('replout').innerHTML.includes('class=nv'));                 // 결과 줄에도 줄바꿈이 보이는 클래스

  // 선택 적용: 체크한 행만 edits에 들어가고 이력에도 행마다 남는다
  el('rfind').value = '메달'; el('rto').value = '배지';
  ctx.replacePreview();
  ctx.replAll(false);
  el('rc0').checked = true; el('rc2').checked = true;                 // 1·3번째 행만
  const histBefore = ctx.histAll().length;
  ctx.replaceApply();
  a.equal(ctx.S.edits.size, 2);
  a.equal(ctx.S.edits.get('0:1:1').v, '배지을 받았다');                // 조사는 안 고쳐진다 — 행별 확인이 필요한 이유
  a.equal(ctx.S.edits.get('0:1:3').v, '\\c[2]배지\\PN');
  a.equal(ctx.S.edits.has('0:1:2'), false);                           // 체크 안 한 행은 그대로
  a.equal(ctx.histAll().length - histBefore, 2);                      // 행마다 한 건씩
  a.equal(ctx.histAll().at(-1).type, 'edit');
  a.ok(el('meta').textContent.startsWith('2행 적용'));
  a.equal(ctx.replHits().length, 1);                                  // 적용된 행은 새 값이라 목록에서 빠진다

  // 원문으로 되돌리는 치환은 edits에서 빠져야 한다(저장 버튼과 같은 의미)
  el('rfind').value = '배지'; el('rto').value = '메달';
  ctx.replacePreview();
  a.equal(ctx.replHits().length, 2);                                  // 방금 고친 두 행
  ctx.replAll(true);
  ctx.replaceApply();
  a.equal(ctx.S.edits.size, 0);                                       // 원문과 같아지면 수정 해제

  // 원문 조건: 번역에 걸려도 스페인어 원문에 그 말이 없으면 뺀다(「무사히」/「갑주무사」 사고 자리)
  ctx.S.rows = [
    { sec: 0, map: 1, idx: 1, k: 'la medalla', v: '메달을 받았다' },
    { sec: 0, map: 1, idx: 2, k: 'el escudo', v: '메달 모양 방패' },   // 번역에만 '메달'
    { sec: 23, idx: 9, v: '메달 보관함' },                             // 원문이 없는 절
  ];
  ctx.S.edits = new Map();
  ctx.replaceMenu();
  el('rfind').value = '메달'; el('rto').value = '배지'; el('rsrc').value = 'medalla';
  ctx.replacePreview();
  a.equal(ctx.replHits().length, 1);
  a.equal(ctx.replHits()[0].r.idx, 1);
  a.ok(el('meta').textContent.includes('원문 조건으로 2행 제외'));
  a.ok(el('replout').innerHTML.includes('건너뛴 2행'));                // 빠진 행은 목록으로 보여준다
  a.ok(el('replout').innerHTML.includes('el escudo'));
  a.ok(el('replout').innerHTML.includes('<mark>medalla</mark>'));      // 매칭 카드엔 원문도 함께
  ctx.replAll(true); ctx.replaceApply();
  a.equal(ctx.S.edits.size, 1);
  a.equal(ctx.S.edits.get('0:1:1').v, '배지을 받았다');
  el('rsrc').value = '';                                              // 조건을 비우면 전체 대상
  ctx.replacePreview();
  a.equal(ctx.replHits().length, 2);                                  // 방금 고친 행은 '메달'이 없어 빠진다
  a.ok(!el('meta').textContent.includes('제외'));
  ctx.S.rows = [                                                      // 아래 묶음 시험이 쓰는 행으로 되돌린다
    { sec: 0, map: 1, idx: 1, k: 'a', v: '메달을 받았다' },
    { sec: 0, map: 1, idx: 2, k: 'b', v: '<b>메달</b> 진열장' },
    { sec: 0, map: 1, idx: 3, k: 'c', v: '\\c[2]메달\\PN' },
    { sec: 0, map: 1, idx: 4, k: 'd', v: '관계없는 행' },
  ];
  ctx.S.edits = new Map();
  ctx.replaceMenu();

  // ─ 동작 묶음과 되돌리기 ─
  // 일괄 바꾸기 한 번 = 한 묶음. 낱개 저장은 낱개대로 선다.
  ctx.localStorage.removeItem('hist:replbase');
  ctx.S.edits = new Map();
  el('rfind').value = '메달'; el('rto').value = '배지';
  ctx.replacePreview(); ctx.replAll(true); ctx.replaceApply();        // 3행짜리 일괄 바꾸기
  ctx.setHits([ctx.S.rows[3]]);
  el('v0').value = '낱개로 고친 행'; ctx.save(0);
  let ops = ctx.editOps();
  a.equal(ops.length, 2);
  a.equal(ops[0].kind, 'one');                                        // 최근 동작이 앞
  a.deepEqual([ops[1].kind, ops[1].evs.length], ['bulk', 3]);
  a.ok(ops[1].key.startsWith('bulk-'));                               // op 표로 묶인다(시각 창 폴백 아님)

  // 되돌리기: 그 동작 전 값으로 돌아가고, 되돌린 것도 한 묶음으로 이력에 남는다
  ctx.showHist();
  a.ok(el('out').innerHTML.includes('일괄 바꾸기') && el('out').innerHTML.includes('3행'));
  a.ok(el('meta').textContent.includes('동작 2개'));
  ctx.undoOp(1);
  a.equal(ctx.S.edits.has('0:1:1'), false);                           // 원문으로 돌아가 대기에서 빠지고
  a.equal(ctx.S.edits.get('0:1:4').v, '낱개로 고친 행');               // 딴 동작은 그대로
  ops = ctx.editOps();
  a.equal(ops[0].kind, 'undo');
  a.equal(ops[0].evs.length, 3);
  a.equal(el('toast').textContent, '3행을 되돌렸어요');

  // 그 뒤에 다시 고친 행은 되돌리기가 건드리지 않는다
  ctx.localStorage.removeItem('hist:replbase');
  ctx.S.edits = new Map();
  el('rfind').value = '메달'; el('rto').value = '배지';
  ctx.replacePreview(); ctx.replAll(true); ctx.replaceApply();
  ctx.setHits([ctx.S.rows[0]]);
  el('v0').value = '나중에 손으로 고친 값'; ctx.save(0);
  ctx.showHist();                                                     // 버튼은 이 화면이 그린 목록의 자리로 부른다
  ctx.undoOp(ctx.ops().findIndex(o => o.kind === 'bulk'));
  a.equal(ctx.S.edits.get('0:1:1').v, '나중에 손으로 고친 값');        // 남의 고침은 보존
  a.ok(el('toast').textContent.includes('1행은 그 뒤에 다시 고쳐져'));

  // op 표가 없는 옛 이력도 시각 창으로 묶인다(판 올리기 전에 쌓인 기록)
  ctx.localStorage.setItem('hist:replbase', JSON.stringify([
    {t:'2026-08-07T10:00:00.000Z', type:'edit', rid:'0:1:1', k:'a', old:'x', new:'y', via:'bulk'},
    {t:'2026-08-07T10:00:01.000Z', type:'edit', rid:'0:1:2', k:'b', old:'x', new:'y', via:'bulk'},
    {t:'2026-08-07T10:30:00.000Z', type:'edit', rid:'0:1:3', k:'c', old:'x', new:'y', via:'bulk'},
  ]));
  ops = ctx.editOps();
  a.deepEqual(ops.map(o => o.evs.length), [1, 2]);                     // 30분 뒤 것은 딴 묶음

  // 수정이 아닌 이벤트는 묶이지 않고 제 차례에 그대로 선다 — 묶음도 그 자리에서 끊긴다
  ctx.hist({type:'build', n:3});
  ctx.hist({type:'edit', rid:'0:1:4', k:'d', old:'x', new:'y', via:'bulk'});
  ops = ctx.editOps();
  a.deepEqual(ops.map(o => o.kind), ['bulk', 'ev', 'bulk', 'bulk']);
  ctx.showHist();
  a.ok(el('out').innerHTML.includes('빌드') && el('out').innerHTML.includes('3건 반영'));

  // ─ 찾아보기 ─
  // speakers.json이 없을 때: 화자 옵션은 아예 안 뜨고 맵별·분류별만 남는다
  ctx.setSpk(null);
  await ctx.loadSpeakers();                                           // 목업 fetch는 ok가 없다 → 조용히 무시
  ctx.fillBrowse();
  a.ok(el('browse').innerHTML.includes('value=map') && el('browse').innerHTML.includes('value=sec'));
  a.ok(!el('browse').innerHTML.includes('value=sprite') && !el('browse').innerHTML.includes('value=group'));

  // 실제 생성물을 그대로 먹인다 — 생성기 형식이 바뀌면 여기서 걸린다
  const spkPath = path.join(__dirname, '..', 'speakers.json');
  const realSpk = JSON.parse(fs.readFileSync(spkPath, 'utf8'));
  const savedFetch = ctx.fetch;
  ctx.fetch = async () => ({ ok: true, json: async () => realSpk });
  ctx.setSpk(null);
  await ctx.loadSpeakers();
  ctx.fillBrowse();
  a.ok(el('browse').innerHTML.includes('value=sprite') && el('browse').innerHTML.includes('value=group'));
  ctx.fetch = savedFetch;

  // 조인: 조인표에 있는 (맵, 원문 k) 행에만 화자가 붙는다
  const someMap = Object.keys(realSpk.maps).find(m => Object.keys(realSpk.maps[m].rows).length);
  const someK = Object.keys(realSpk.maps[someMap].rows)[0];
  const [spI, gpI] = realSpk.maps[someMap].rows[someK];
  const joined = { sec: 0, map: +someMap, idx: 0, k: someK, v: '번역문' };
  const unjoined = { sec: 0, map: +someMap, idx: 1, k: '조인표에 없는 원문', v: '번역문2' };
  a.deepEqual(ctx.spkOf(joined), [realSpk.sp[spI], realSpk.gp[gpI]]);
  a.equal(ctx.spkOf(unjoined), null);
  a.equal(ctx.spkOf({ sec: 23, idx: 0, v: 'x' }), null);              // 맵 대사가 아닌 절은 화자 없음

  // 카드 칩: 화자가 붙은 행에만 스프라이트·분류 칩이 뜬다
  ctx.S.edits = new Map(); ctx.S.applied = new Map();
  a.ok(ctx.card(joined, 0).includes(ctx.esc(realSpk.sp[spI])));
  a.ok(!ctx.card(unjoined, 0).includes(ctx.esc(realSpk.sp[spI])));

  // 묶기: 절별은 절 단위로, 맵별은 21절 이름을 병기, 화자별은 조인된 행만
  ctx.S.rows = [joined, unjoined, { sec: 21, idx: +someMap, v: '어느마을' },
                { sec: 23, idx: 0, v: '시스템 문구' }];
  ctx.setSpk(realSpk);
  a.equal(ctx.mapName(+someMap), '어느마을');                          // 21절이 조인표 이름을 이긴다
  const bySec = ctx.browseGroups('sec');
  a.deepEqual(bySec.map(g => [g.label, g.rows.length]),
    [['0 · 맵 대사', 2], ['21 · 맵 이름', 1], ['23 · 시스템 문구', 1]]);
  const byMap = ctx.browseGroups('map');
  a.equal(byMap.length, 1);
  a.ok(byMap[0].label.includes('어느마을'));
  a.equal(byMap[0].rows.length, 2);
  const bySprite = ctx.browseGroups('sprite');
  a.deepEqual(bySprite.map(g => [g.label, g.rows.length]), [[realSpk.sp[spI], 1]]);  // 조인 안 된 행은 빠진다

  // 묶음 열기: 카드 목록으로 넘어가고 500행 상한이 걸린다
  ctx.doBrowse('map');
  a.ok(el('out').innerHTML.includes('어느마을') && el('out').innerHTML.includes('2행'));
  ctx.openGroup(0);
  a.ok(el('meta').textContent.includes('2행'));
  a.ok(el('out').innerHTML.includes('번역문'));
  const many = Array.from({ length: ctx.BROWSE_CAP + 10 },
    (_, i) => ({ sec: 0, map: 1, idx: i, k: 'k'+i, v: 'v'+i }));
  ctx.S.rows = many;
  ctx.setSpk(null);
  ctx.doBrowse('map');
  ctx.openGroup(0);
  a.ok(el('meta').textContent.includes(`앞 ${ctx.BROWSE_CAP}행만`));

  // ─ 이벤트 모아 보기 ─
  // 생성물에서 자리가 여럿인 원문과 하나뿐인 원문을 실제로 찾아 쓴다(형식이 바뀌면 여기서 걸린다)
  ctx.setSpk(realSpk);
  let evMap, multiK, soloK;
  for (const [m, mv] of Object.entries(realSpk.maps)){
    for (const [k, e] of Object.entries(mv.rows)){
      if (!e[2]) continue;
      if (e[2].length > 1 && !multiK){ evMap = m; multiK = k; }
      if (evMap === m && e[2].length === 1 && !soloK) soloK = k;
    }
    if (multiK && soloK) break;
    multiK = soloK = undefined;
  }
  a.ok(multiK && soloK, '자리가 여럿인 원문과 하나인 원문이 같은 맵에 있어야 한다');
  const mapN = +evMap, multi = realSpk.maps[evMap].rows[multiK][2], solo = realSpk.maps[evMap].rows[soloK][2];
  const rowOf = k => ({ sec: 0, map: mapN, idx: 0, k, v: '번역:' + k.slice(0, 8) });
  a.equal(ctx.evOf(rowOf(multiK)).length, multi.length);
  a.equal(ctx.evOf({ sec: 0, map: mapN, idx: 0, k: '조인표에 없는 원문' }), null);
  a.equal(ctx.evOf({ sec: 23, idx: 0 }), null);                       // 맵 대사가 아닌 절은 자리 없음
  a.equal(ctx.evName(solo[0]), realSpk.en[solo[0][3]]);

  // 한 이벤트 페이지의 행은 명령 순번대로 선다
  const [ev, page] = solo[0];
  const inPage = [];
  for (const [k, e] of Object.entries(realSpk.maps[evMap].rows))
    for (const p of e[2] ?? []) if (p[0] === ev && p[1] === page) inPage.push([p[2], k]);
  inPage.sort((x, y) => x[0] - y[0]);
  const want = [...new Set(inPage.map(([, k]) => k))];                // dat는 (맵,원문)마다 한 행
  ctx.S.rows = want.map(rowOf).reverse();                             // 일부러 거꾸로 넣어도
  a.deepEqual(ctx.eventRows(mapN, ev, page).map(r => r.k), want);     // 명령 순서로 돌아온다
  a.deepEqual(ctx.eventRows(mapN, 999999, 0), []);                    // 없는 이벤트는 빈 목록

  // 카드 칩: 이벤트 이름이 뜨고, 자리가 여럿이면 몇 곳인지 붙는다
  ctx.S.edits = new Map(); ctx.S.applied = new Map();
  ctx.setHits([rowOf(multiK), rowOf(soloK)]);
  a.ok(ctx.card(rowOf(multiK), 0).includes(`외 ${multi.length - 1}곳`));
  a.ok(ctx.card(rowOf(soloK), 1).includes(ctx.esc(ctx.evName(solo[0]))));
  a.ok(!ctx.card({ sec: 23, idx: 0, v: 'x' }, 2).includes('evJump'));  // 자리 없는 행엔 칩이 없다

  // 자리가 여럿이면 목록부터, 하나면 곧장 이벤트 화면
  ctx.S.rows = Object.keys(realSpk.maps[evMap].rows).map(rowOf);
  ctx.evJump(0);
  a.ok(el('meta').textContent.includes(`${multi.length}곳`));
  a.ok(el('out').innerHTML.includes('openSpot(0)'));
  ctx.openSpot(0);
  a.ok(el('meta').textContent.includes(ctx.evName(multi[0])));
  a.ok(el('card' + ctx.hits().findIndex(r => r.k === multiK)).classList.contains('focus'));
  ctx.setHits([rowOf(multiK), rowOf(soloK)]);                         // 이벤트 화면이 HITS를 갈아 끼웠으니 되돌린다
  ctx.evJump(1);                                                      // soloK — 목록을 거치지 않는다
  a.ok(!el('out').innerHTML.includes('openSpot('));
  a.ok(el('meta').textContent.includes(ctx.evName(solo[0])));

  // ─ 문제 제보(행 무관) ─
  ctx.GENERAL_FORM.id = 'genform1';
  Object.assign(ctx.GENERAL_FORM.entries, {kind:'g.kind', text:'g.text', patch:'g.patch'});
  ctx.feedbackMenu();
  a.ok(el('out').innerHTML.includes('전반적 번역 문제'));       // 종류 선택지가 뜬다
  el('fbtext').value = '   ';
  ctx.__lastFetch = null;
  await ctx.sendFeedback();
  a.equal(ctx.__lastFetch, null);                               // 빈 내용은 전송하지 않는다
  el('fbtext').value = '너즐록 화면 글자가 겹쳐 보여요';
  ctx.S.meta = 'v5'; ctx.S.sha = 'gsha';
  await ctx.sendFeedback();
  const [gUrl, gInit] = ctx.__lastFetch;
  a.equal(gUrl, 'https://docs.google.com/forms/d/e/genform1/formResponse');
  const gfd = gInit.body._m;
  a.equal(gfd.get('g.kind'), '전반적 번역 문제');               // querySelector 없는 환경은 기본 종류
  a.equal(gfd.get('g.text'), '너즐록 화면 글자가 겹쳐 보여요');
  a.ok(gfd.get('g.patch').startsWith('v5 / studio-1 / u:'));
  a.equal(el('fbtext').value, '');                              // 보낸 뒤 입력칸 비움
  ctx.S.meta = null;

  // ─ 태그 검색 ─
  // 파서: 태그·따옴표 값·태그 없는 낱말이 제자리에 앉는다
  {
    const f = ctx.parseQuery('분류:"도구 이름" 맵:12 화자:간호사 상태:수정 원문:hola 번역:안녕 그냥말');
    a.deepEqual([f.sec, f.map, f.spk, f.state, f.k, f.v, f.text],
      [['도구 이름'], ['12'], ['간호사'], ['수정'], ['hola'], ['안녕'], ['그냥말']]);
    a.deepEqual(ctx.parseQuery('상태:').state, []);               // 빈 값 태그는 무시
    a.deepEqual(ctx.parseQuery('"띄어 쓴 본문"').text, ['띄어 쓴 본문']);
  }
  // 행 매칭: 분류 라벨 부분일치·맵 번호/이름·상태·본문 AND
  ctx.setSpk(realSpk);
  ctx.S.rows = [joined, unjoined, { sec: 21, idx: +someMap, v: '어느마을' },
                { sec: 7, idx: 1, k: 'poción', v: '상처약' }];
  ctx.S.edits = new Map([[ctx.rid(joined), { ...joined, v: '고침' }]]);
  ctx.S.applied = new Map();
  a.ok(ctx.rowMatch(ctx.S.rows[3], ctx.parseQuery('분류:도구')));         // "도구 이름" 라벨 부분일치
  a.ok(!ctx.rowMatch(ctx.S.rows[3], ctx.parseQuery('분류:대사')));
  a.ok(ctx.rowMatch(joined, ctx.parseQuery('맵:' + someMap)));            // 맵 번호
  // 숫자 맵 태그는 정확 일치만 — 「맵:1」이 137이나 이름 속 숫자에 걸리면 안 된다
  ctx.S.rows.push({ sec: 0, map: 137, idx: 0, k: 'k137', v: 'v137' },
                  { sec: 21, idx: 137, v: '1번째마을' });
  a.ok(!ctx.rowMatch(ctx.S.rows.at(-2), ctx.parseQuery('맵:1')));
  a.ok(!ctx.tagValues('맵', '1').some(x => x.v === '137'));               // 자동완성도 접두 확장 금지
  a.ok(ctx.tagValues('맵', '137').some(x => x.v === '137'));
  ctx.S.rows.length -= 2;
  a.ok(ctx.rowMatch(joined, ctx.parseQuery('맵:어느마을')));              // 21절 이름으로도
  a.ok(!ctx.rowMatch(ctx.S.rows[3], ctx.parseQuery('맵:' + someMap)));    // 맵 없는 절은 맵 태그에 안 걸린다
  a.ok(ctx.rowMatch(joined, ctx.parseQuery('화자:' + realSpk.sp[spI])));
  a.ok(!ctx.rowMatch(unjoined, ctx.parseQuery('화자:' + realSpk.sp[spI])));
  a.ok(ctx.rowMatch(joined, ctx.parseQuery('상태:수정')));
  a.ok(!ctx.rowMatch(unjoined, ctx.parseQuery('상태:수정')));
  a.ok(ctx.rowMatch(ctx.S.rows[3], ctx.parseQuery('원문:poción 번역:상처')));
  a.ok(!ctx.rowMatch(ctx.S.rows[3], ctx.parseQuery('상처 없는말')));      // 본문 낱말은 AND
  // search(): 태그 조합이 실제 목록으로 떨어진다
  el('q').value = '분류:도구 상처';
  ctx.search();
  a.equal(el('meta').textContent, '1행 매칭');
  a.ok(el('out').innerHTML.includes('상처약'));
  // 자동완성 값 후보: 분류·상태·맵 이름
  a.ok(ctx.tagValues('분류', '도구').includes('도구 이름'));
  a.deepEqual(ctx.tagValues('상태', ''), ['수정', '반영', '메모']);
  a.ok(ctx.tagValues('맵', '어느').some(x => x.label.includes('어느마을')));
  // 홈: 로고 클릭 — 검색어가 비워지고 홈 카드가 선다
  ctx.S.dir = {};
  ctx.goHome();
  a.equal(el('q').value, '');
  a.ok(el('out').innerHTML.includes('할 수 있는 일'));
  ctx.S.edits = new Map();

  // ─ 내 수정 화면 ─
  // 메모 이전: 옛 판은 메모가 이력에만 있었다 — 첫 조회에서 활성 목록으로 옮기고, 같은 행은 최신이 남는다
  ctx.S.base = 'minebase';
  ctx.clearMemos();
  ctx.localStorage.setItem('hist:minebase', JSON.stringify([
    { t: '2026-08-01T00:00:00Z', type: 'memo', rid: '0:1:1', k: 'a', text: '옛 메모' },
    { t: '2026-08-02T00:00:00Z', type: 'memo', rid: '0:1:1', k: 'a', text: '고친 메모' },
    { t: '2026-08-02T01:00:00Z', type: 'memo', rid: '0:1:2', k: 'b', text: '둘째 메모' },
  ]));
  a.equal(ctx.localStorage.getItem('memos:minebase'), null);   // 이전 전에는 활성 목록이 없다
  a.equal(ctx.memoIndex().size, 2);
  a.equal(ctx.memoIndex().get('0:1:1').text, '고친 메모');      // 같은 행은 최신 것만
  a.ok(ctx.localStorage.getItem('memos:minebase'));            // 이전 결과가 저장된다
  // 이미 활성 목록이 있으면 이력에서 다시 만들지 않는다(지운 메모가 되살아나면 안 된다)
  ctx.localStorage.setItem('memos:minebase', JSON.stringify([['0:1:2', { k: 'b', text: '둘째 메모' }]]));
  ctx.clearMemos();
  a.equal(ctx.memoIndex().size, 1);
  a.equal(ctx.memoIndex().has('0:1:1'), false);

  // 메모 삭제: 활성 목록에서 빠지고 이력에는 삭제 기록이 남는다
  ctx.S.rows = [
    { sec: 0, map: 1, idx: 1, k: '스페인어원문1', v: '번역1' },
    { sec: 0, map: 1, idx: 2, k: '스페인어원문2', v: '번역2' },
  ];
  ctx.S.edits = new Map(); ctx.S.applied = new Map();
  ctx.memoDel('0:1:2');
  a.equal(ctx.memoIndex().size, 0);
  a.equal(ctx.histAll().at(-1).type, 'memo-del');
  a.deepEqual(JSON.parse(ctx.localStorage.getItem('memos:minebase')), []);   // 저장분에서도 사라진다
  ctx.clearMemos();
  a.equal(ctx.memoIndex().size, 0);                            // 다시 읽어도 안 살아난다

  // 삭제한 메모는 일괄 제보에도 개별 제보 코멘트에도 실리지 않는다 — 보낼 게 없어 전송조차 안 된다
  ctx.__fetchCalls.length = 0;
  await ctx.batchReport();
  a.equal(ctx.__fetchCalls.length, 0);
  a.equal(ctx.canReport('0:1:2'), false);

  // 인라인 재수정: 목록에서 고친 값이 그대로 대기 수정에 앉는다
  ctx.S.edits = new Map([['0:1:1', { sec: 0, map: 1, idx: 1, k: '스페인어원문1', v: '고친값' }]]);
  ctx.persist();
  ctx.showMine();
  a.ok(el('out').innerHTML.includes('대기 중인 수정 1건'));
  a.ok(el('out').innerHTML.includes('고친값') && el('out').innerHTML.includes('스페인어원문1'));
  el('mv0:1:1').value = '다시 고친값';
  ctx.mineSave('0:1:1');
  a.equal(ctx.S.edits.get('0:1:1').v, '다시 고친값');
  a.equal(JSON.parse(ctx.localStorage.getItem('edits:minebase'))[0].v, '다시 고친값');
  a.equal(ctx.histAll().at(-1).new, '다시 고친값');            // 재수정도 이력에 남는다
  a.ok(el('out').innerHTML.includes('고친값'));                // 저장이 목록을 다시 그리면 안 된다 —
  a.ok(!el('out').innerHTML.includes('다시 고친값'));          // 다른 행에 입력 중이던 글이 날아간다

  // 저장도 색·이름 코드 경고를 지나야 한다 — 물어봐서 아니라고 하면 값이 안 바뀐다
  const savedConfirm = ctx.confirm;
  ctx.confirm = () => false;
  el('mv0:1:1').value = '코드 없는 값';
  ctx.S.rows[0].v = '\\c[2]번역1';
  ctx.mineSave('0:1:1');
  a.equal(ctx.S.edits.get('0:1:1').v, '다시 고친값');          // 거절했으니 그대로
  ctx.confirm = savedConfirm;
  ctx.S.rows[0].v = '번역1';

  // 수정 취소: 대기에서 빠지고 저장분도 함께 비워진다
  ctx.mineCancel('0:1:1');
  a.equal(ctx.S.edits.size, 0);
  a.deepEqual(JSON.parse(ctx.localStorage.getItem('edits:minebase')), []);
  a.equal(ctx.histAll().at(-1).new, '번역1');                  // 원문으로 되돌린 기록
  a.equal(el('dirty').style.display, 'none');                  // "빌드 필요" 표시도 내려간다
  ctx.mineCancel('0:1:1');                                     // 없는 행을 또 취소해도 조용히 넘어간다
  a.equal(ctx.S.edits.size, 0);

  // CR이 든 원문도 취소가 먹어야 한다 — 저장값은 textarea가 접은 LF 모양이라 그대로 비교하면 안 빠진다
  ctx.S.rows = [{ sec: 0, map: 1, idx: 1, k: '스페인어원문1', v: '첫 줄\r\n둘째 줄' }];
  ctx.S.edits = new Map([['0:1:1', { sec: 0, map: 1, idx: 1, k: '스페인어원문1', v: '고친 줄' }]]);
  ctx.mineCancel('0:1:1');
  a.equal(ctx.S.edits.size, 0);
  ctx.S.rows = [{ sec: 0, map: 1, idx: 1, k: '스페인어원문1', v: '번역1' }];

  // 반영됨은 표시만 — 취소 버튼 없이 되돌리는 방법만 알려준다
  ctx.S.applied = new Map([['0:1:2', { sec: 0, map: 1, idx: 2, k: '스페인어원문2', v: '반영된값' }]]);
  ctx.showMine();
  a.ok(el('out').innerHTML.includes('반영된값'));
  a.ok(el('out').innerHTML.includes('검색해 다시 고치세요'));
  a.ok(!el('out').innerHTML.includes("mineCancel('0:1:2')"));
  a.ok(el('out').innerHTML.includes('남긴 메모가 없어요'));    // 빈 상태 문구

  // 선시동(announce 없음) 도중 실제 호출(announce:true)이 합류하면 남은 단계부터 화면 문구가 떠야 한다
  // (버그였던 지점: bootPromise 캐시가 announce 게이트보다 먼저라 화면이 안 갱신됐었다)
  {
    ctx.S.py = null;
    let resolveLoad;
    const savedLoadPyodide = ctx.loadPyodide, savedFetch3 = ctx.fetch;
    ctx.loadPyodide = async () => { ctx.__pyodideCalls++;
      await new Promise(res => { resolveLoad = res; });
      return { FS: { mkdirTree(){}, writeFile(){} }, pyimport: () => ({}), runPython(){} }; };
    ctx.fetch = async () => ({ ok: true, text: async () => '' });
    el('meta').textContent = '시작 화면';
    const prefetch = ctx.bootPy(); prefetch.catch(()=>{});   // announce 없음 — 화면 안 건드림
    a.equal(el('meta').textContent, '시작 화면');
    const real = ctx.bootPy({announce: true});               // 진행 중인 선시동에 합류
    resolveLoad();
    await real;
    a.equal(el('meta').textContent, '엔진 시동...');          // 합류 후 남은 단계는 화면에 뜬다
    ctx.loadPyodide = savedLoadPyodide; ctx.fetch = savedFetch3;
    ctx.resetBoot();   // 다음 테스트가 이번에 뜬 엔진을 재사용하지 않게
  }

  // 선시동 중복 방지: 파일 fetch가 정상 응답하는 환경에서 bootPy를 겹쳐 불러도 loadPyodide는 한 번만 떠야 한다
  ctx.S.py = null;
  const savedFetchForBoot = ctx.fetch;
  ctx.fetch = async () => ({ ok: true, text: async () => '' });
  const callsBefore = ctx.__pyodideCalls;
  const [bootA, bootB] = await Promise.all([ctx.bootPy(), ctx.bootPy()]);   // 동시 호출
  a.equal(ctx.__pyodideCalls, callsBefore + 1);                            // loadPyodide는 1회만
  a.equal(bootA, bootB);                                                   // 같은 py 인스턴스를 공유
  await ctx.bootPy();                                                      // 이미 뜬 뒤 재호출도 늘지 않는다
  a.equal(ctx.__pyodideCalls, callsBefore + 1);
  ctx.fetch = savedFetchForBoot;
  ctx.S.py = null;   // 이후 테스트에 영향 없게 되돌린다(다른 테스트는 S.py를 직접 목업해 쓴다)

  console.log('SELFCHECK_OK');
})().catch(e => { console.error(e); process.exit(1); });
