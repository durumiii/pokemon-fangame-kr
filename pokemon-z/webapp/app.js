// ─── 설정 (유지자가 채움) ─────────────────────────────
const REPORT_FORM = {
  id: "",          // 구글폼 ID — 비어 있으면 제보 버튼 숨김
  entries: { sec:"", idx:"", k:"", v:"", suggest:"", patch:"" },
};
const APP_VER = "studio-1";
const SEC_LABEL = {0:"맵 대사",1:"포켓몬 이름",2:"분류",3:"도감 설명",4:"폼",
 5:"기술 이름",6:"기술 설명",7:"도구 이름",8:"도구 복수형",9:"도구 설명",
 10:"특성 이름",11:"특성 설명",12:"타입",13:"트레이너 직함",14:"트레이너 이름",
 15:"대전 시작 대사",16:"승리 대사",17:"패배 대사",18:"지방",19:"장소 이름",
 20:"장소 설명",21:"맵 이름",22:"전화",23:"시스템 문구"};

const $ = id => document.getElementById(id);
const S = { dir:null, rows:[], sha:"", meta:null, edits:new Map(), py:null, core:null };
const rid = r => `${r.sec}:${r.map ?? -1}:${r.idx}`;

function toast(m, ms=2600){ const t=$('toast'); t.textContent=m; t.classList.add('show');
  clearTimeout(t._h); t._h=setTimeout(()=>t.classList.remove('show'), ms); }
// 속성값 자리에도 그대로 쓰므로 따옴표까지 막는다
function esc(s){ const d=document.createElement('div'); d.textContent=s ?? '';
  return d.innerHTML.replace(/"/g,'&quot;'); }

// 비동기 경로의 예외가 콘솔에만 남고 화면은 멀쩡해 보이는 일을 막는다
addEventListener('unhandledrejection', e => toast('오류: ' + (e.reason?.message ?? e.reason), 6000));

async function bootPy(){
  if (S.py) return S.py;
  $('meta').textContent = '엔진 로드 중... (첫 방문은 수십 초, 이후 캐시)';
  const py = await loadPyodide();
  // 파이썬 소스를 pyodide FS에 심는다
  const files = ["core.py","rubywrite.py",
    ...["__init__.py","reader.py","writer.py","classes.py","constants.py","utils.py"]
      .map(f=>"vendor/rubymarshal/"+f)];
  py.FS.mkdirTree('/app/rubymarshal');
  for (const f of files){
    const src = await (await fetch(f)).text();
    const dst = f.startsWith('vendor/') ? '/app/rubymarshal/'+f.split('/').pop() : '/app/'+f;
    py.FS.writeFile(dst, src);
  }
  py.runPython("import sys; sys.path.insert(0, '/app')");
  S.core = py.pyimport("core");
  S.py = py;
  return py;
}

// Task 5(빌드)가 쓰는 진입점 — edits 배열 → korean.dat 바이트
async function pyBuild(editsArr){
  await bootPy();
  const r = S.core.build_dat(JSON.stringify(editsArr));
  if (r instanceof Uint8Array) return r;
  const u8 = r.toJs();
  r.destroy();
  return u8;
}

async function readFile(dir, path){
  let h = dir;
  const parts = path.split('/');
  for (const p of parts.slice(0,-1)) h = await h.getDirectoryHandle(p);
  const fh = await h.getFileHandle(parts.at(-1));
  return new Uint8Array(await (await fh.getFile()).arrayBuffer());
}
async function writeFile(dir, path, bytes){
  let h = dir;
  const parts = path.split('/');
  for (const p of parts.slice(0,-1)) h = await h.getDirectoryHandle(p);
  const fh = await h.getFileHandle(parts.at(-1), {create:true});
  const w = await fh.createWritable();
  await w.write(bytes); await w.close();
}
// 핸들만 확인한다 — 내용을 읽어 판정하면 잠긴 파일이 "없음"이 되어 백업을 덮어쓴다
async function exists(dir, path){
  const parts = path.split('/');
  try {
    let h = dir;
    for (const p of parts.slice(0,-1)) h = await h.getDirectoryHandle(p);
    await h.getFileHandle(parts.at(-1));
    return true;
  } catch(e){ if (e.name === 'NotFoundError') return false; throw e; }
}

// dat 바이트 → S.rows/sha/meta 갱신 (최초 로드·빌드 성공·빌드 실패 복구 셋 다 공용)
async function loadCore(datBytes){
  let msg = null;
  try { msg = await readFile(S.dir, 'Data/messages.dat'); } catch {}
  const res = JSON.parse(S.core.load_dat(S.py.toPy(datBytes), msg && S.py.toPy(msg)));
  S.rows = res.rows; S.sha = res.sha; S.meta = res.meta;
  return res;
}

async function openFolder(){
  if (!window.showDirectoryPicker){ toast('이 브라우저는 지원하지 않아요 — Chrome/Edge로 열어주세요', 5000); return; }
  try { S.dir = await showDirectoryPicker({mode:'readwrite'}); } catch { return; }
  if (!await exists(S.dir, 'Data/korean.dat')){
    toast('선택한 폴더에 Data\\korean.dat가 없어요 — 게임 폴더를 선택해 주세요', 5000); return;
  }
  await bootPy();
  $('meta').textContent = '번역 데이터 읽는 중...';
  const dat = await readFile(S.dir, 'Data/korean.dat');
  // 순정 원본 1회 보존 — 이미 있으면 절대 덮어쓰지 않는다
  if (!await exists(S.dir, 'Data/korean.dat.bak')){
    await writeFile(S.dir, 'Data/korean.dat.bak', dat);
  }
  await loadCore(dat);
  restoreEdits();
  for (const id of ['q','secf','searchbtn','buildbtn','exportbtn','importbtn','restorebtn'])
    $(id).disabled = false;
  $('secf').innerHTML = '<option value="">전체 분류</option>' +
    Object.entries(SEC_LABEL).map(([s,l])=>`<option value=${s}>${l}</option>`).join('');
  $('meta').textContent = `${S.rows.length.toLocaleString()}행 로드 · 패치 ${S.meta ?? '(표식 없음 · '+S.sha+')'}` +
    (S.edits.size ? ` · 이어서 작업: 저장 ${S.edits.size}건 복원됨` : '');
  $('out').innerHTML = '<div class=empty>어색한 문구를 검색해 바로 고치세요.</div>';
  updateDirty();
}

// ─── 검색·수정 ────────────────────────────────────────
let HITS=[], SHOWN=0; const STEP=50;
$('q')?.addEventListener('keydown', e=>{ if(e.key==='Enter') search(); });

function search(){
  const q = $('q').value.trim(); if(!q) return;
  const sec = $('secf').value;
  HITS = S.rows.filter(r =>
    (sec==='' || r.sec===+sec) &&
    ((r.v && r.v.includes(q)) || (r.k && r.k.includes(q))));
  SHOWN = 0;
  $('meta').textContent = `${HITS.length}행 매칭`;
  $('out').innerHTML = HITS.length ? '' : '<div class=empty>매칭되는 행이 없습니다.</div>';
  if (HITS.length) more();
}

function card(r, i){
  const id = rid(r), e = S.edits.get(id);
  const v = e ? e.v : r.v;
  return `<div class="card ${e?'saved':''}" id=card${i}>
    <span class=chip>${SEC_LABEL[r.sec]??('절'+r.sec)}</span>${r.map!=null?`<span class=chip>맵 ${r.map}</span>`:''}
    ${REPORT_FORM.id?`<button class=ghost style="float:right" onclick=report(${i})>🚩 제보</button>`:''}
    ${r.k?`<div class=es>${esc(r.k)}</div>`:''}
    <textarea id=v${i} data-orig="${esc(r.v)}"
      onkeydown="if(event.ctrlKey&&event.key==='Enter')save(${i})">${esc(v)}</textarea>
    <div class=rowbar>
      <button class=primary onclick=save(${i})>저장</button>
      <button class=ghost onclick="$('v'+${i}).value=$('v'+${i}).dataset.orig">원래대로</button>
      <span class=st id=st${i}></span>
    </div></div>`;
}
function more(){
  const frag = HITS.slice(SHOWN, SHOWN+STEP).map((r,k)=>card(r, SHOWN+k)).join('');
  SHOWN = Math.min(SHOWN+STEP, HITS.length);
  $('morebtn')?.remove();
  $('out').insertAdjacentHTML('beforeend', frag);
  if (SHOWN < HITS.length) $('out').insertAdjacentHTML('beforeend',
    `<button class=more id=morebtn onclick=more()>더 보기 (${HITS.length-SHOWN}행 남음)</button>`);
}

const MARKUP = /\\c\[\d+\]|\\[A-Za-z]+|\{\d+\}|<[^>]+>/g;
function save(i){
  const r = HITS[i], v = $('v'+i).value;
  const lost = (r.v.match(MARKUP)||[]).filter(t => !v.includes(t));
  if (lost.length && !confirm(`색·이름 코드가 사라졌어요: ${lost.join(' ')}\n지우면 화면이 깨질 수 있어요. 그래도 저장할까요?`))
    return;
  // textarea는 CR/CRLF를 LF로 접어 돌려준다 — 안 고친 행이 수정으로 잡히지 않게 같은 모양끼리 비교
  if (v === r.v.replace(/\r\n?/g, '\n')) S.edits.delete(rid(r));
  else S.edits.set(rid(r), {sec:r.sec, map:r.map, idx:r.idx, k:r.k, v});
  persist(); updateDirty();
  $('st'+i).className='st ok'; $('st'+i).textContent='저장됨';
  $('card'+i).classList.add('saved');
  toast('저장됨 — [빌드]를 누르면 게임에 반영돼요');
}
function persist(){
  localStorage.setItem('edits:'+S.sha, JSON.stringify([...S.edits.values()]));
}
function restoreEdits(){
  S.edits = new Map();
  for (const e of JSON.parse(localStorage.getItem('edits:'+S.sha) ?? '[]'))
    S.edits.set(rid(e), e);
}
function updateDirty(){
  const d = $('dirty'), n = S.edits.size;
  d.style.display = n ? 'inline-block' : 'none';
  if (n) d.textContent = `저장 ${n}건 — 빌드 필요`;
}

// ─── 빌드·복원 ────────────────────────────────────────
async function build(){
  if (!S.edits.size){ toast('저장된 수정이 없어요'); return; }
  const b = $('buildbtn'); b.disabled = true; b.textContent = '빌드 중...';
  const n = S.edits.size, prevSha = S.sha;
  let wrote = false;
  try {
    const out = await pyBuild([...S.edits.values()]);
    // 직전본 백업 → 본체 기록 (원본 .bak은 openFolder에서 이미 보존)
    const cur = await readFile(S.dir, 'Data/korean.dat');
    await writeFile(S.dir, 'Data/korean.dat.prev', cur);
    await writeFile(S.dir, 'Data/korean.dat', out);
    wrote = true;
    // 빌드 산출물로 상태 재동기화 — sha가 바뀌므로 반영 끝난 edits는 비운다(중복 적용 방지)
    await loadCore(out);
    localStorage.removeItem('edits:'+prevSha);
    S.edits = new Map();
    persist();
    updateDirty();
    toast(`빌드 완료 (${n}건 반영) — 게임을 재시작하면 보여요`, 4000);
  } catch (err) {
    if (wrote) {
      // 파일은 이미 새 내용으로 갱신됨 — 화면 상태 갱신만 실패한 것
      toast('파일은 갱신됐지만 화면 상태 갱신에 실패했어요 — 새로고침해 주세요: ' + err.message, 6000);
    } else {
      toast('빌드 실패 — 파일은 그대로예요: ' + err.message, 6000);
      // core.build_dat 실패 시 파이썬 쪽 상태에 부분 변형이 남을 수 있어 디스크 원본으로 재로드
      try { await loadCore(await readFile(S.dir, 'Data/korean.dat')); } catch {}
    }
  } finally {
    b.disabled = false; b.textContent = '빌드 → 게임 반영';
  }
}

// ─── 고침 파일 내보내기/가져오기 ────────────────────────
let CONFLICTS = [];
function exportFix(){
  if (!S.edits.size){ toast('내보낼 수정이 없어요'); return; }
  const lines = [JSON.stringify({app:APP_VER, patch:S.meta ?? S.sha}),
    ...[...S.edits.values()].map(e=>JSON.stringify(e))];
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([lines.join('\n')+'\n'], {type:'application/x-ndjson'}));
  a.download = `z-kr-고침-${new Date().toISOString().slice(0,10)}-${S.edits.size}건.jsonl`;
  a.click(); URL.revokeObjectURL(a.href);
  toast('고침 파일을 내려받았어요 — 커뮤니티에 첨부해 공유하세요');
}

function importFix(){
  $('importfile').onchange = async ev => {
    const f = ev.target.files[0]; ev.target.value = ''; if (!f) return;
    const rawLines = (await f.text()).split('\n').filter(Boolean);
    const lines = []; let badLines = 0;
    for (const l of rawLines){ try { lines.push(JSON.parse(l)); } catch { badLines++; } }
    if (rawLines.length && !lines.length){ toast('고침 파일 형식이 아니에요', 4000); return; }
    const head = lines[0]?.app ? lines.shift() : null;
    const byId = new Map(S.rows.map(r=>[rid(r), r]));
    let applied = 0, skipped = badLines; const conflicts = [];
    for (const e of lines){
      const row = byId.get(rid(e));
      if (!row || (e.k && row.k !== e.k) || typeof e.v !== 'string'
          || !Number.isInteger(e.sec) || !Number.isInteger(e.idx)){ skipped++; continue; }   // 원문 불일치·형식 이상 → 버전 다름
      const mine = S.edits.get(rid(e));
      if (mine && mine.v !== e.v){ conflicts.push({row, mine, theirs:e}); continue; }
      S.edits.set(rid(e), {sec:row.sec, map:row.map, idx:row.idx, k:row.k, v:e.v});
      applied++;
    }
    persist(); updateDirty();
    $('meta').textContent = `가져오기: ${applied}건 병합 · ${skipped}건 건너뜀(원문 불일치)` +
      (head?.patch && head.patch !== (S.meta ?? S.sha) ? ` · 주의: 다른 패치판(${head.patch})의 고침` : '');
    if (conflicts.length) showConflicts(conflicts);
    else toast(`병합 완료 — ${applied}건. 빌드하면 반영돼요`, 4000);
  };
  $('importfile').click();
}

function showConflicts(cs){
  $('out').innerHTML = `<div class=meta>내 수정과 겹치는 ${cs.length}행 — 남길 쪽을 고르세요</div>` +
    cs.map((c,i)=>`<div class=card id=cf${i}>
      ${c.row.k?`<div class=es>${esc(c.row.k)}</div>`:''}
      <div class=rowbar><button class=primary onclick=pickConflict(${i},0)>내 것: ${esc(c.mine.v)}</button></div>
      <div class=rowbar><button onclick=pickConflict(${i},1)>가져온 것: ${esc(c.theirs.v)}</button></div>
    </div>`).join('');
  CONFLICTS = cs;
}
function pickConflict(i, theirs){
  const c = CONFLICTS[i];
  if (theirs) S.edits.set(rid(c.row), {sec:c.row.sec, map:c.row.map, idx:c.row.idx, k:c.row.k, v:c.theirs.v});
  persist(); updateDirty();
  $('cf'+i).style.opacity = .4; $('cf'+i).style.pointerEvents = 'none';
}

async function restoreMenu(){
  const hasPrev = await exists(S.dir, 'Data/korean.dat.prev');
  const pick = prompt(
    `복원할 대상 번호를 입력하세요:\n 1 = 순정 원본(korean.dat.bak)` +
    (hasPrev ? `\n 2 = 직전 빌드 전(korean.dat.prev)` : ''), '1');
  const src = pick === '1' ? 'Data/korean.dat.bak' : pick === '2' && hasPrev ? 'Data/korean.dat.prev' : null;
  if (!src) return;
  await writeFile(S.dir, 'Data/korean.dat', await readFile(S.dir, src));
  toast('복원 완료 — 페이지를 새로고침해 다시 불러오세요', 5000);
}
