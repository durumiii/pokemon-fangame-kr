// ─── 이벤트 모아 보기 ─────────────────────────────────
// speakers.json의 rows[원문] = [화자, 분류, [[이벤트, 페이지, 명령순번, 이벤트이름], ...]]
// 셋째 칸이 이 대사가 게임 이벤트의 어디에 서 있는지다. 한 대사가 여러 자리에
// 걸리면(맵 하나에서만 2,606개) 자리를 다 담으므로 목록을 먼저 보여준다.

let SPOTS = [], FOCUS = '';    // 자리 목록 화면의 항목들, 이벤트 화면에서 테두리를 두를 원문

function evOf(r){
  const e = r.sec === 0 && SPK?.maps?.[r.map]?.rows?.[r.k];
  return (e && e[2]) || null;
}
// 자리 하나의 이름 — 이벤트 이름이 비어 있으면 번호로 부른다
function evName(p){ return SPK?.en?.[p[3]] || `이벤트 ${p[0]}`; }
function evLabel(map, p){
  const nm = mapName(map);
  return `맵 ${map}${nm ? ' · ' + nm : ''} · ${evName(p)}` + (p[1] ? ` · 페이지 ${p[1]}` : '');
}

// 한 이벤트 페이지의 대사를 명령 순서대로 — 원문으로 S.rows에서 되찾는다.
// (dat는 (맵, 원문)마다 한 줄이라 같은 페이지에 같은 대사가 두 번 나오면 한 행으로 합쳐진다)
function eventRows(map, ev, page){
  const rows = SPK?.maps?.[map]?.rows;
  if (!rows) return [];
  const ord = new Map();
  for (const k in rows)
    for (const p of rows[k][2] ?? [])
      if (p[0] === ev && p[1] === page) ord.set(k, Math.min(p[2], ord.get(k) ?? Infinity));
  return S.rows.filter(r => r.sec === 0 && r.map === map && ord.has(r.k))
               .sort((a, b) => ord.get(a.k) - ord.get(b.k));
}

// 카드의 이벤트 칩 — 자리가 하나면 곧장 열고, 여럿이면 어디로 갈지 먼저 묻는다
function evJump(i){
  const r = HITS[i], spots = evOf(r);
  if (!spots?.length) return;
  FOCUS = r.k;
  if (spots.length === 1) return openEvent(r.map, spots[0][0], spots[0][1]);
  SPOTS = spots.map(p => [r.map, p]);
  closePanels();
  $('meta').textContent = `이 대사가 나오는 자리 ${SPOTS.length}곳`;
  $('out').innerHTML = SPOTS.map(([m, p], j) =>
    `<div class=card style="cursor:pointer" onclick=openSpot(${j})>
      <b>${esc(evLabel(m, p))}</b> <span class=chip>${eventRows(m, p[0], p[1]).length}행</span></div>`).join('');
}
function openSpot(j){
  const [m, p] = SPOTS[j];
  openEvent(m, p[0], p[1]);
}

function openEvent(map, ev, page){
  closePanels();
  HITS = eventRows(map, ev, page); SHOWN = 0;
  const p = evOf({sec:0, map, k:FOCUS})?.find(x => x[0] === ev && x[1] === page) ?? [ev, page, 0, -1];
  $('meta').textContent = `${evLabel(map, p)} — ${HITS.length}행`;
  $('out').innerHTML = HITS.length ? '' : '<div class=empty>이 이벤트의 대사를 찾지 못했어요.</div>';
  if (!HITS.length) return;
  more();
  const at = HITS.findIndex(r => r.k === FOCUS);
  if (at < 0) return;
  const c = $('card' + at);
  c?.classList.add('focus');
  c?.scrollIntoView?.({block:'center'});
}
