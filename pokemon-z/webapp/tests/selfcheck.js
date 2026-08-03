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
  doRestore, reloadAfterRestore, batchReport, batchParts, canReport, card,
  memoIndex, renderHome, updateDirty, FIELD_CAP,
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

  // 제보: 7필드가 FormData에 담기고 no-cors POST로 fetch가 불려야 한다
  ctx.REPORT_FORM.id = 'formid123';
  Object.assign(ctx.REPORT_FORM.entries, {sec:'e.sec', idx:'e.idx', k:'e.k', v:'e.v',
    suggest:'e.suggest', comment:'e.comment', patch:'e.patch'});
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
  a.equal(fd.get('e.suggest'), '');                                   // 저장한 수정이 없으면 빈 제안
  a.equal(fd.get('e.comment'), '');                                   // 메모가 없으면 prompt 결과(빈 문자열)
  a.equal(fd.get('e.patch'), 'hash:reportsha / studio-1');            // meta 없으면 hash:sha로 대체

  // 제안=내가 저장한 번역, 코멘트=그 행 메모 — 둘 다 있으면 물어보지 않는다
  ctx.S.rows = [reportRow];
  ctx.S.edits = new Map([['3:7:9', { sec: 3, map: 7, idx: 9, k: '원문키', v: '내가고친값' }]]);
  ctx.S.applied = new Map();
  ctx.hist({ type: 'memo', rid: '3:7:9', k: '원문키', text: '어투 확인 필요' });
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

  // 일괄 제보: 수정 덤프 + 메모 덤프 + 분류 "일괄 N건"
  ctx.S.rows = [reportRow, { sec: 0, map: 1, idx: 2, k: '', v: '키없는원문' }];
  ctx.S.edits = new Map([['3:7:9', { sec: 3, map: 7, idx: 9, k: '원문키', v: '수정A' }]]);
  ctx.S.applied = new Map([['0:1:2', { sec: 0, map: 1, idx: 2, k: '', v: '수정B' }]]);
  const parts = ctx.batchParts();
  a.equal(parts.n, 3);                                                 // 수정 2 + 메모 1
  a.deepEqual(parts.suggest.split('\n').sort(),
    ['[도감 설명] 원문키 → 수정A', '[맵 대사] 키없는원문 → 수정B'].sort());   // k 없으면 현재 번역문을 원문 자리에
  a.equal(parts.comment, '[메모] 원문키: 어투 확인 필요');
  await ctx.batchReport();
  const fd3 = ctx.__lastFetch[1].body._m;
  a.equal(fd3.get('e.sec'), '일괄 3건');
  a.equal(fd3.get('e.idx'), ''); a.equal(fd3.get('e.k'), ''); a.equal(fd3.get('e.v'), '');
  a.equal(fd3.get('e.patch'), 'hash:reportsha / studio-1');            // 패치 표식은 개별 제보와 같은 형식

  // 30,000자 절단
  ctx.S.edits = new Map([['3:7:9', { sec: 3, map: 7, idx: 9, k: '원문키', v: 'x'.repeat(40000) }]]);
  await ctx.batchReport();
  const longSuggest = ctx.__lastFetch[1].body._m.get('e.suggest');
  a.equal(longSuggest.length, ctx.FIELD_CAP + '…(이하 생략)'.length);
  a.ok(longSuggest.endsWith('…(이하 생략)'));

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
  ctx.hist({ type: 'memo', rid: '3:7:9', k: '원문키', text: '메모1' });
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

  console.log('SELFCHECK_OK');
})().catch(e => { console.error(e); process.exit(1); });
