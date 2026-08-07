// ─── 이력 ─────────────────────────────────────────────
// 지나간 기록을 보는 화면. 기록 자체는 손댈 수 없지만(append-only), 한 동작을
// 통째로 되돌릴 수는 있다 — 되돌린 것도 새 기록으로 쌓인다.
// app.js 다음에 실린다(전역 S·histAll·applyEdit을 그대로 쓴다).

const HIST_LABEL = {edit:'수정', memo:'메모', 'memo-del':'메모 삭제',
  build:'빌드', restore:'복원', import:'가져오기'};
const OP_LABEL = {bulk:'일괄 바꾸기', undo:'되돌리기', one:'낱개 수정'};
const HIST_OPS = 60;          // 화면에 세우는 최근 항목 수 — 이력이 길어지면 앞쪽만 그린다
const OP_ROWS = 4;            // 묶음 카드에 미리 보이는 행 수

// 수정 이벤트를 「한 동작」으로 묶는다. 일괄 바꾸기·되돌리기는 op 표를 달고 오고,
// 그 표가 없는 옛 이력은 잇달아 온 같은 갈래를 5초 창으로 묶는다.
// 수정이 아닌 이벤트(빌드·메모·복원)는 묶지 않고 제 차례에 그대로 선다.
let OPS = [];
function editOps(){
  const ops = [];
  for (const e of histAll()){
    if (e.type !== 'edit'){ ops.push({kind:'ev', t:e.t, ev:e}); continue; }
    const kind = e.via === 'bulk' ? 'bulk' : e.via === 'undo' ? 'undo' : 'one';
    const key = e.op ?? `${kind}:${Math.floor(Date.parse(e.t) / 5000)}`;
    const last = ops[ops.length - 1];
    if (last?.key === key) last.evs.push(e);
    else ops.push({key, kind, t: e.t, evs: [e]});
  }
  return ops.reverse();                                    // 최근 것부터
}
// 그 뒤에 딴 수정이 덮은 행은 되돌리지 않는다 — 남의 고침을 지우게 된다
const histRow = id => S.rows.find(r => rid(r) === id);
const undoable = e => (S.edits.get(e.rid)?.v ?? histRow(e.rid)?.v) === e.new;

function undoOp(i){
  const op = OPS[i];
  if (!op?.evs) return;
  const live = op.evs.filter(undoable);
  if (!live.length){ toast('되돌릴 게 없어요 — 이미 되돌렸거나 그 뒤에 다시 고친 행이에요'); return; }
  opBegin('undo');
  for (const e of live){
    const r = histRow(e.rid);
    if (r) applyEdit(r, e.old, 'undo');
  }
  opEnd();
  persist(); updateDirty(); showHist();
  const skipped = op.evs.length - live.length;
  toast(`${live.length}행을 되돌렸어요` + (skipped ? ` — ${skipped}행은 그 뒤에 다시 고쳐져 그대로 뒀어요` : ''));
}

function opCard(op, i){
  const when = `<span class=chip>${new Date(op.t).toLocaleString('ko-KR')}</span>`;
  if (op.kind === 'ev'){
    const e = op.ev;
    return `<div class=card>${when}<span class=chip>${HIST_LABEL[e.type] ?? e.type}</span>
      ${e.k ? `<div class=es>${esc(e.k)}</div>` : ''}${histBody(e)}</div>`;
  }
  const live = op.evs.some(undoable);
  const rows = op.evs.slice(0, OP_ROWS).map(e =>
    `${e.k ? `<div class=es>${esc(e.k)}</div>` : ''}<div>${esc(e.old)} → ${esc(e.new)}</div>`).join('');
  return `<div class=card>${when}<span class=chip>${OP_LABEL[op.kind]}</span><span class=chip>${op.evs.length}행</span>
    <button class=ghost style="float:right" onclick=undoOp(${i})
      ${live ? '' : 'disabled title="이미 되돌렸거나 그 뒤에 다시 고친 동작이에요"'}>되돌리기</button>
    ${rows}${op.evs.length > OP_ROWS ? `<div class=es>… 그 밖 ${op.evs.length - OP_ROWS}행</div>` : ''}</div>`;
}

function histBody(e){
  if (e.type === 'edit') return `<div class=es>${esc(e.old)}</div><div>→ ${esc(e.new)}</div>`;
  if (e.type === 'memo' || e.type === 'memo-del') return `<div>${esc(e.text)}</div>`;
  if (e.type === 'build') return `<div>${e.n}건 반영</div>`;
  if (e.type === 'import') return `<div>${e.n}건 병합</div>`;
  if (e.type === 'restore') return `<div>${esc(e.src)}</div>`;
  return '';
}

function showHist(){
  const n = histAll().length;
  OPS = editOps();
  $('meta').textContent = `이력 ${n}건 · 동작 ${OPS.length}개 (순정 기준 ${S.base})`;
  $('out').innerHTML = OPS.length
    ? OPS.slice(0, HIST_OPS).map(opCard).join('') +
      (OPS.length > HIST_OPS ? `<div class=empty>… 그 밖 ${OPS.length - HIST_OPS}개는 안 그렸어요</div>` : '')
    : '<div class=empty>아직 이력이 없어요 — 수정·메모·빌드가 여기에 쌓여요.</div>';
}
