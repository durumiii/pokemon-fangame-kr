// ─── 내 수정 ──────────────────────────────────────────
// 이력은 지나간 기록이라 손댈 수 없다. 이 화면은 지금 살아 있는 것 — 대기 중인 수정과 메모를
// 여기서 다시 고치고 지운다. app.js 다음에 실린다(전역 S·applyEdit·memoIndex를 그대로 쓴다).

const mineRow = id => S.rows.find(r => rid(r) === id);
// 원문 자리 — 스페인어 원문 k가 정본이고, k가 없는 절은 현재 번역문이 그 자리에 선다
const mineSrc = (r, e) => (r?.k || r?.v || e?.k || '');
const mineChips = (r, e) => {
  const s = r ?? e;
  return s ? `<span class=chip>${SEC_LABEL[s.sec] ?? '절'+s.sec}</span>` +
    (s.map != null ? `<span class=chip>맵 ${s.map}</span>` : '') : '';
};

function showMine(){
  const byId = new Map(S.rows.map(r => [rid(r), r]));
  const memos = memoIndex();
  $('meta').textContent =
    `내 수정 — 대기 ${S.edits.size}건 · 메모 ${memos.size}건 · 반영됨 ${S.applied.size}건`;

  // 대기 목록도 최근 고친 것부터 — Map은 처음 넣은 차례라 다시 고쳐도 자리가 안 바뀐다
  const lastT = new Map();
  for (const e of histAll()) if (e.type === 'edit') lastT.set(e.rid, e.t);
  const pending = [...S.edits]
    .sort((a, b) => (lastT.get(b[0]) ?? '').localeCompare(lastT.get(a[0]) ?? ''))
    .map(([id, e]) => `<div class="card saved">
    ${mineChips(byId.get(id), e)}
    <div class=es>${esc(mineSrc(byId.get(id), e))}</div>
    <textarea id=mv${id}>${esc(e.v)}</textarea>
    <div class=rowbar><button class=primary onclick="mineSave('${id}')">저장</button>
      <button class=ghost onclick="mineCancel('${id}')">수정 취소</button></div></div>`).join('');

  const memoCards = [...memos].map(([id, m]) => `<div class=card>
    ${mineChips(byId.get(id), m)}
    <div class=es>${esc(mineSrc(byId.get(id), m))}</div>
    <div>${esc(m.text)}</div>
    <div class=rowbar><button class=ghost onclick="mineMemoDel('${id}')">메모 삭제</button></div></div>`).join('');

  const appliedCards = [...S.applied].map(([id, e]) => `<div class=card>
    ${mineChips(byId.get(id), e)}<span class=chip>반영됨</span>
    <div class=es>${esc(mineSrc(byId.get(id), e))}</div>
    <div>${esc(e.v)}</div></div>`).join('');

  const head = (title, desc) => `<div class=card><div>${title}</div><div class=es>${desc}</div></div>`;
  $('out').innerHTML =
    head(`대기 중인 수정 ${S.edits.size}건`, '아직 게임 파일에 안 들어갔어요. 여기서 다시 고치거나 취소할 수 있어요.') +
    (pending || '<div class=empty>대기 중인 수정이 없어요.</div>') +
    head(`메모 ${memos.size}건`, '빌드에는 들어가지 않고 제보할 때 코멘트로 함께 실려요.') +
    (memoCards || '<div class=empty>남긴 메모가 없어요.</div>') +
    head(`반영됨 ${S.applied.size}건`, '이미 게임 파일에 들어간 수정이에요. 되돌리려면 그 문구를 검색해 다시 고치세요.') +
    (appliedCards || '<div class=empty>반영된 수정이 없어요.</div>');
}

function mineSave(id){
  const r = mineRow(id);
  if (!r) return;
  const v = $('mv'+id).value;
  if (!confirmMarkup(r, v)) return;
  applyEdit(r, v);
  // 목록을 다시 그리지 않는다 — 다른 행에 입력 중이던 글이 날아간다(검색 화면의 save와 같은 이유)
  persist(); updateDirty();
  toast('저장됨 — [빌드]를 누르면 게임에 반영돼요');
}
// 원문 그대로를 다시 앉히면 applyEdit가 대기 목록에서 뺀다 — 취소와 저장이 같은 경로다
function mineCancel(id){
  const r = mineRow(id);
  if (!r || !S.edits.has(id)) return;
  applyEdit(r, (r.v ?? '').replace(/\r\n?/g, '\n'));
  persist(); updateDirty(); showMine();
  toast('수정을 취소했어요 — 원래 문구로 돌아갔어요');
}
function mineMemoDel(id){
  memoDel(id);
  showMine();
  toast('메모를 지웠어요 — 이력에는 지운 기록이 남아요');
}
