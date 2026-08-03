// ─── 설정 (유지자가 채움) ─────────────────────────────
const REPORT_FORM = {
  id: "1FAIpQLSfRZcs1AE9O9KvJZx5jpR-eQWm4ZKm4TCeHa759-M_ns5sGSg",
  entries: { sec:"entry.908760751", idx:"entry.1569162646", k:"entry.360216311",
             v:"entry.1404070622", suggest:"entry.538219219", patch:"entry.266338952" },
};
const APP_VER = "studio-1";
const SEC_LABEL = {0:"맵 대사",1:"포켓몬 이름",2:"분류",3:"도감 설명",4:"폼",
 5:"기술 이름",6:"기술 설명",7:"도구 이름",8:"도구 복수형",9:"도구 설명",
 10:"특성 이름",11:"특성 설명",12:"타입",13:"트레이너 직함",14:"트레이너 이름",
 15:"대전 시작 대사",16:"승리 대사",17:"패배 대사",18:"지방",19:"장소 이름",
 20:"장소 설명",21:"맵 이름",22:"전화",23:"시스템 문구"};

const $ = id => document.getElementById(id);
// edits = 아직 빌드 안 된 수정, applied = 이미 dat에 반영된 수정(내보내기용으로 남긴다)
const S = { dir:null, rows:[], sha:"", base:"", meta:null, edits:new Map(), applied:new Map(), py:null, core:null };
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
// core.py의 sha와 같은 모양(sha256 앞 12자) — 순정 원본을 저장 키로 삼는다
async function sha12(bytes){
  const h = await crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(h)].map(b=>b.toString(16).padStart(2,'0')).join('').slice(0,12);
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

// ─── 폴더 핸들 보존 ────────────────────────────────────
// FileSystemHandle은 localStorage(문자열)에 못 넣는다 — 구조화 복제가 되는 IndexedDB로
function idbDo(mode, fn){
  return new Promise((res, rej) => {
    const rq = indexedDB.open('zstudio', 1);
    rq.onupgradeneeded = () => rq.result.createObjectStore('kv');
    rq.onerror = () => rej(rq.error);
    rq.onsuccess = () => {
      const tx = rq.result.transaction('kv', mode);
      const r = fn(tx.objectStore('kv'));
      tx.oncomplete = () => res(r.result);
      tx.onerror = () => rej(tx.error);
    };
  });
}
const idbGet = k => idbDo('readonly', s => s.get(k));
const idbSet = (k, v) => idbDo('readwrite', s => s.put(v, k));

async function openFolder(){
  if (!window.showDirectoryPicker){ toast('이 브라우저는 지원하지 않아요 — Chrome/Edge로 열어주세요', 5000); return; }
  let dir;
  try { dir = await showDirectoryPicker({mode:'readwrite'}); } catch { return; }
  await useFolder(dir);
}

// 지난 폴더 재연결 — 권한이 없으면 조용히 일반 선택으로 안내한다
async function reopenFolder(){
  const h = await idbGet('dirHandle');
  if (!h){ toast('저장된 폴더가 없어요 — [게임 폴더 선택]을 눌러주세요', 5000); return; }
  if (await h.requestPermission({mode:'readwrite'}) !== 'granted'){
    toast('폴더 접근 권한이 없어요 — [게임 폴더 선택]으로 다시 골라주세요', 5000); return;
  }
  await useFolder(h);
}

async function useFolder(dir){
  S.dir = dir;
  if (!await exists(S.dir, 'Data/korean.dat')){
    toast('선택한 폴더에 Data\\korean.dat가 없어요 — 게임 폴더를 선택해 주세요', 5000); return;
  }
  // 검증을 통과한 폴더만 기억한다. 저장 실패가 작업을 막으면 안 된다(시크릿 모드 등)
  try { await idbSet('dirHandle', S.dir); } catch {}
  await bootPy();
  $('meta').textContent = '번역 데이터 읽는 중...';
  const dat = await readFile(S.dir, 'Data/korean.dat');
  // 순정 원본 1회 보존 — 이미 있으면 절대 덮어쓰지 않는다
  const hadBak = await exists(S.dir, 'Data/korean.dat.bak');
  if (!hadBak) await writeFile(S.dir, 'Data/korean.dat.bak', dat);
  await loadCore(dat);
  // 저장 키는 빌드마다 바뀌는 현재 sha가 아니라 순정 원본 sha로 고정한다
  S.base = hadBak ? await sha12(await readFile(S.dir, 'Data/korean.dat.bak')) : S.sha;
  migrateEdits();
  const dropped = restoreEdits();
  for (const id of ['q','secf','searchbtn','buildbtn','exportbtn','importbtn','restorebtn','histbtn'])
    $(id).disabled = false;
  $('secf').innerHTML = '<option value="">전체 분류</option>' +
    Object.entries(SEC_LABEL).map(([s,l])=>`<option value=${s}>${l}</option>`).join('');
  $('meta').textContent = `${S.rows.length.toLocaleString()}행 로드 · 패치 ${S.meta ?? '(표식 없음 · '+S.sha+')'}` +
    (S.edits.size ? ` · 이어서 작업: 저장 ${S.edits.size}건 복원됨` : '') +
    (dropped ? ` · 패치 판이 바뀌어 ${dropped}건 제외` : '');
  if (dropped) toast(`패치 판이 바뀌어 옛 수정 ${dropped}건을 제외했어요 — 그 행들은 다시 고쳐주세요`, 6000);
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
    <span class=chip>${SEC_LABEL[r.sec]??('절'+r.sec)}</span>${r.map!=null?`<span class=chip>맵 ${r.map}</span>`:''}${!e&&S.applied.has(id)?'<span class=chip>반영됨</span>':''}
    ${REPORT_FORM.id?`<button class=ghost style="float:right" onclick=report(${i})>🚩 제보</button>`:''}
    ${r.k?`<div class=es>${esc(r.k)}</div>`:''}
    <textarea id=v${i} data-orig="${esc(r.v)}"
      onkeydown="if(event.ctrlKey&&event.key==='Enter')save(${i})">${esc(v)}</textarea>
    <div class=rowbar>
      <button class=primary onclick=save(${i})>저장</button>
      <button class=ghost onclick="$('v'+${i}).value=$('v'+${i}).dataset.orig">원래대로</button>
      <span class=st id=st${i}></span>
    </div>
    <div class=rowbar>
      <input type=text class=memoin id=m${i} placeholder="메모 — 이력에만 남아요"
        onkeydown="if(event.key==='Enter')memo(${i})">
      <button class=ghost onclick=memo(${i})>메모</button>
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
  const prev = S.edits.get(rid(r));
  if (v === r.v.replace(/\r\n?/g, '\n')) S.edits.delete(rid(r));
  else S.edits.set(rid(r), {sec:r.sec, map:r.map, idx:r.idx, k:r.k, v});
  hist({type:'edit', rid:rid(r), k:r.k, old:prev ? prev.v : r.v, new:v});
  persist(); updateDirty();
  $('st'+i).className='st ok'; $('st'+i).textContent='저장됨';
  $('card'+i).classList.add('saved');
  toast('저장됨 — [빌드]를 누르면 게임에 반영돼요');
}
// 원버튼 제보 — 구글폼에 no-cors로 던진다(응답 확인 불가, 실패해도 toast로만 알림)
async function report(i){
  const r = HITS[i], val = $('v'+i).value;
  const suggest = val !== r.v.replace(/\r\n?/g, '\n') ? val
    : (prompt('제안 번역이나 한 줄 코멘트 (그냥 제보만 하려면 비워두세요)') ?? '');
  const fd = new FormData();
  const E = REPORT_FORM.entries;
  fd.append(E.sec, `${r.sec}:${SEC_LABEL[r.sec] ?? ''}`);
  fd.append(E.idx, `${r.map ?? ''}:${r.idx}`);
  fd.append(E.k, r.k ?? '');
  fd.append(E.v, r.v);
  fd.append(E.suggest, suggest);
  fd.append(E.patch, `${S.meta ?? 'hash:'+S.sha} / ${APP_VER}`);
  try {
    await fetch(`https://docs.google.com/forms/d/e/${REPORT_FORM.id}/formResponse`,
      {method:'POST', mode:'no-cors', body:fd});
    toast('제보를 보냈어요 — 고마워요! 다음 판에 반영을 검토합니다', 4000);
  } catch {
    toast('전송이 안 됐어요 — 인터넷 연결을 확인해 주세요', 5000);
  }
}
function persist(){
  localStorage.setItem('edits:'+S.base, JSON.stringify([...S.edits.values()]));
  localStorage.setItem('applied:'+S.base, JSON.stringify([...S.applied.values()]));
}
// 기준 키는 .bak에 고정돼 있어 dat만 새 판으로 갈아끼우면 옛 수정이 남는다.
// 행 인덱스가 밀렸을 수 있으므로 가져오기와 같은 원문 대조로 거른다.
// applied도 같은 대조를 쓴다 — 원문 k는 빌드해도 안 바뀌므로 판이 바뀐 것만 걸린다
function loadStore(prefix){
  const byId = new Map(S.rows.map(r=>[rid(r), r]));
  const m = new Map();
  let dropped = 0;
  for (const e of JSON.parse(localStorage.getItem(prefix+':'+S.base) ?? '[]')){
    const row = byId.get(rid(e));
    if (!row || (e.k && row.k !== e.k)){ dropped++; continue; }
    m.set(rid(e), e);
  }
  return {m, dropped};
}
// 버린 건수를 돌려준다
function restoreEdits(){
  const {m, dropped} = loadStore('edits');
  S.edits = m;
  S.applied = loadStore('applied').m;
  return dropped;
}
// 옛 판(현재 dat sha 기준)의 저장분을 순정 기준 키로 1회 옮긴다
function migrateEdits(){
  const old = 'edits:'+S.sha;
  if (S.sha === S.base || !localStorage.getItem(old)) return;
  if (!localStorage.getItem('edits:'+S.base)) localStorage.setItem('edits:'+S.base, localStorage.getItem(old));
  localStorage.removeItem(old);
}

// ─── 이력 원장 ────────────────────────────────────────
// append-only — 같은 행을 여러 번 고치면 이벤트도 그만큼 쌓인다
function histAll(){ try { return JSON.parse(localStorage.getItem('hist:'+S.base) ?? '[]'); } catch { return []; } }
function hist(ev){
  const a = histAll();
  a.push({t:new Date().toISOString(), ...ev});
  try { localStorage.setItem('hist:'+S.base, JSON.stringify(a)); } catch {}
}
function memo(i){
  const r = HITS[i], text = $('m'+i).value.trim();
  if (!text){ toast('메모 내용을 적어주세요'); return; }
  hist({type:'memo', rid:rid(r), k:r.k, text});
  $('m'+i).value = '';
  $('st'+i).className='st ok'; $('st'+i).textContent='메모 남김';
  toast('메모를 이력에 남겼어요 — 빌드에는 들어가지 않아요');
}
const HIST_LABEL = {edit:'수정', memo:'메모', build:'빌드', restore:'복원', import:'가져오기'};
function histBody(e){
  if (e.type === 'edit') return `<div class=es>${esc(e.old)}</div><div>→ ${esc(e.new)}</div>`;
  if (e.type === 'memo') return `<div>${esc(e.text)}</div>`;
  if (e.type === 'build') return `<div>${e.n}건 반영</div>`;
  if (e.type === 'import') return `<div>${e.n}건 병합</div>`;
  if (e.type === 'restore') return `<div>${esc(e.src)}</div>`;
  return '';
}
function showHist(){
  const all = histAll();
  $('meta').textContent = `이력 ${all.length}건 (순정 기준 ${S.base})`;
  $('out').innerHTML = all.length ? [...all].reverse().map(e=>`<div class=card>
    <span class=chip>${new Date(e.t).toLocaleString('ko-KR')}</span><span class=chip>${HIST_LABEL[e.type] ?? e.type}</span>
    ${e.k?`<div class=es>${esc(e.k)}</div>`:''}${histBody(e)}</div>`).join('')
    : '<div class=empty>아직 이력이 없어요 — 수정·메모·빌드가 여기에 쌓여요.</div>';
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
  const n = S.edits.size;
  let wrote = false;
  try {
    const out = await pyBuild([...S.edits.values()]);
    // 직전본 백업 → 본체 기록 (원본 .bak은 openFolder에서 이미 보존)
    const cur = await readFile(S.dir, 'Data/korean.dat');
    await writeFile(S.dir, 'Data/korean.dat.prev', cur);
    await writeFile(S.dir, 'Data/korean.dat', out);
    wrote = true;
    // 빌드 산출물로 상태 재동기화 — 반영 끝난 edits는 applied로 옮긴다(중복 적용 방지 + 내보내기엔 남김)
    await loadCore(out);
    for (const [id, e] of S.edits) S.applied.set(id, e);
    S.edits = new Map();
    persist();
    updateDirty();
    hist({type:'build', n});
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
  // 빌드로 이미 반영된 것까지 함께 — 원본과 달라졌으면 언제든 내보낼 수 있어야 한다. 같은 행은 미빌드분이 이긴다
  const all = new Map([...S.applied, ...S.edits]);
  if (!all.size){ toast('내보낼 수정이 없어요'); return; }
  // 표식은 순정 기준으로 — S.sha는 빌드마다 바뀌어 받는 쪽에 "다른 패치판"으로 보인다
  const lines = [JSON.stringify({app:APP_VER, patch:S.meta ?? S.base}),
    ...[...all.values()].map(e=>JSON.stringify(e))];
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([lines.join('\n')+'\n'], {type:'application/x-ndjson'}));
  a.download = `z-kr-고침-${new Date().toISOString().slice(0,10)}-${all.size}건.jsonl`;
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
    hist({type:'import', n:applied});
    $('meta').textContent = `가져오기: ${applied}건 병합 · ${skipped}건 건너뜀(원문 불일치)` +
      (head?.patch && head.patch !== (S.meta ?? S.base) ? ` · 주의: 다른 패치판(${head.patch})의 고침` : '');
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
  hist({type:'restore', src});
  toast('복원 완료 — 페이지를 새로고침해 다시 불러오세요', 5000);
}

// 지난 폴더가 남아 있을 때만 재연결 버튼을 드러낸다
idbGet('dirHandle').then(h => { if (h) $('reopenbtn').style.display = ''; }).catch(()=>{});
