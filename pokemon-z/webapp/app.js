// ─── 설정 (유지자가 채움) ─────────────────────────────
const REPORT_FORM = {
  id: "1FAIpQLSfRZcs1AE9O9KvJZx5jpR-eQWm4ZKm4TCeHa759-M_ns5sGSg",
  entries: { sec:"entry.908760751", idx:"entry.1569162646", k:"entry.360216311",
             v:"entry.1404070622", suggest:"entry.538219219", comment:"entry.266338952",
             patch:"entry.1352350096" },
};
// 행 무관 일반 제보(전반적 번역·렌더링 등) — 별도 구글폼, 같은 스프레드시트의 새 탭에 연결
// id가 비어 있으면 화면에서 숨긴다(유지자가 폼 생성 후 채움)
const GENERAL_FORM = {
  id: "1FAIpQLSed1vWYuQt14NNAGxhD-oGoS49Cxyf1MwmUia4Q_OmqrFN5Gw",
  entries: { kind:"entry.1761277727", text:"entry.1561553815", patch:"entry.825168505" },
};
// 인라인 SVG만 쓴다 — 이모지는 기기마다 다른 그림이고 외부 아이콘은 오프라인에서 깨진다
const ICON = {
  flag: '<svg width=13 height=13 viewBox="0 0 16 16" fill=none stroke=currentColor stroke-width=1.6 stroke-linejoin=round style="vertical-align:-1px"><path d="M3.5 14.5V1.5"/><path d="M3.5 2.5h8l-1.6 2.6 1.6 2.6h-8z" fill=currentColor fill-opacity=".25"/></svg>',
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

// ─── 드롭다운 패널 ────────────────────────────────────
// 기본 select 대신 쓰는 공용 패널 — 열림/닫힘과 자리만 여기서, 내용은 각자 채운다
const PANELS = ['tools','browse','sugg'];
function closePanels(){ for (const id of PANELS){ const p = $(id); if (p) p.hidden = true; } }
function togglePanel(id, btn){
  const p = $(id), wasOpen = !p.hidden;
  closePanels();
  if (wasOpen) return;
  if (id === 'browse') fillBrowse();
  p.hidden = false;
  // 앵커 버튼 바로 아래, 오른쪽이 화면을 넘으면 버튼 오른끝에 맞춘다 (header 기준 absolute)
  const hr = btn.closest('header').getBoundingClientRect(), br = btn.getBoundingClientRect();
  p.style.top = (br.bottom - hr.top + 6) + 'px';
  p.style.left = 'auto'; p.style.right = 'auto';
  if (br.left - hr.left + p.offsetWidth > hr.width - 12)
    p.style.right = Math.max(8, hr.right - br.right) + 'px';
  else p.style.left = (br.left - hr.left) + 'px';
}
addEventListener('click', e => {
  if (!e.target.closest?.('.menu,[data-menubtn],#q')) closePanels();
});
addEventListener('keydown', e => { if (e.key === 'Escape') closePanels(); });

// 로고 클릭 = 홈 — 로드 전에는 시작 화면 그대로 둔다
function goHome(){
  if (!S.dir) return;
  closePanels();
  $('q').value = '';
  $('meta').textContent = metaBase();
  renderHome();
}

// 페이지 로드 직후 미리 불러 두는 선시동과, 폴더를 고른 뒤의 실제 호출이 이 하나로 합류한다 —
// 진행 중 promise를 저장해 두 번째 호출도 같은 promise를 기다린다(다운로드 중복 없음).
// 실패하면 다음 호출이 재시도할 수 있게 저장을 비운다(오프라인 등으로 선시동만 실패한 경우).
let bootPromise = null, bootAnnounce = false;
async function bootPy({announce=false}={}){
  if (S.py) return S.py;
  if (announce) bootAnnounce = true;   // 선시동 뒤에 실제 호출이 합류해도 남은 단계는 화면에 뜨게
  if (bootPromise) return bootPromise;
  bootPromise = (async () => {
    if (bootAnnounce) $('meta').textContent = '엔진 내려받는 중(첫 방문 1회)...';
    console.time('boot:download');
    const py = await loadPyodide();
    console.timeEnd('boot:download');
    if (bootAnnounce) $('meta').textContent = '엔진 시동...';
    console.time('boot:init');
    try {
      // 파이썬 소스를 pyodide FS에 심는다
      const files = ["core.py","rubywrite.py",
        ...["__init__.py","reader.py","writer.py","classes.py","constants.py","utils.py"]
          .map(f=>"vendor/rubymarshal/"+f)];
      py.FS.mkdirTree('/app/rubymarshal');
      for (const f of files){
        const res = await fetch(f);
        // 404 HTML을 파이썬 소스로 심으면 한참 뒤 난해한 구문 오류로 터진다 — 받은 자리에서 막는다
        if (!res.ok) throw new Error('필수 파일을 못 받았어요: ' + f);
        const src = await res.text();
        const dst = f.startsWith('vendor/') ? '/app/rubymarshal/'+f.split('/').pop() : '/app/'+f;
        py.FS.writeFile(dst, src);
      }
      py.runPython("import sys; sys.path.insert(0, '/app')");
      S.core = py.pyimport("core");
      S.py = py;
      return py;
    } finally {
      console.timeEnd('boot:init');   // 실패해도 타이머는 닫는다 — 다음 재시도에서 이름 충돌 경고가 안 나게
    }
  })().catch(err => { bootPromise = null; throw err; });
  return bootPromise;
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
  MAPNAME = null;   // 21절이 새로 로드됐다 — 맵 이름 색인도 다시 만든다
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
  const spkPromise = loadSpeakers();   // 폴더 읽기와 겹치게 지금 시작(사용은 fillBrowse 직전에)
  console.time('data:read');
  await bootPy({announce:true});
  $('meta').textContent = '번역 데이터 읽는 중(3만 행)...';
  const dat = await readFile(S.dir, 'Data/korean.dat');
  // 순정 원본 1회 보존 — 이미 있으면 절대 덮어쓰지 않는다
  const hadBak = await exists(S.dir, 'Data/korean.dat.bak');
  if (!hadBak) await writeFile(S.dir, 'Data/korean.dat.bak', dat);
  await loadCore(dat);
  console.timeEnd('data:read');
  // 저장 키는 빌드마다 바뀌는 현재 sha가 아니라 순정 원본 sha로 고정한다
  S.base = hadBak ? await sha12(await readFile(S.dir, 'Data/korean.dat.bak')) : S.sha;
  migrateEdits();
  const dropped = restoreEdits();
  await spkPromise;
  for (const id of ['q','searchbtn','browsebtn','toolsbtn','buildbtn','replbtn','exportbtn','importbtn','restorebtn','histbtn','batchbtn','minebtn'])
    $(id).disabled = false;
  fillBrowse();
  $('meta').textContent = metaBase() +
    (S.edits.size ? ` · 이어서 작업: 저장 ${S.edits.size}건 복원됨` : '') +
    (dropped ? ` · 패치 판이 바뀌어 ${dropped}건 제외` : '');
  if (dropped) toast(`패치 판이 바뀌어 옛 수정 ${dropped}건을 제외했어요 — 그 행들은 다시 고쳐주세요`, 6000);
  updateDirty();
  renderHome();
}

// ─── 찾아보기 ─────────────────────────────────────────
// speakers.json은 있으면 좋은 곁들이다 — 못 받아도 맵별·분류별은 그대로 돌아간다
let SPK = null, MAPNAME = null, GROUPS = [];
const BROWSE = {map:'맵별', sec:'파일 분류별', sprite:'화자별', group:'화자 분류별'};
const BROWSE_CAP = 500;

async function loadSpeakers(){
  try {
    const res = await fetch('speakers.json');
    if (res.ok) SPK = await res.json();
  } catch {}
}
function fillBrowse(){
  $('browse').innerHTML =
    Object.entries(BROWSE).filter(([k]) => SPK || k === 'map' || k === 'sec')
      .map(([k,l]) => `<button data-value=${k} onclick="doBrowse('${k}')">${l}</button>`).join('');
}
// 맵 이름은 21절이 정본(번역돼 있다) — 조인표 이름은 21절에 빈 자리일 때의 폴백
function mapName(m){
  MAPNAME ??= new Map(S.rows.filter(r => r.sec === 21).map(r => [r.idx, r.v]));
  return MAPNAME.get(m) || SPK?.maps[m]?.name || '';
}
// 맵 대사 한 행의 화자 — [스프라이트, 분류]. 조인표에 없으면 null
function spkOf(r){
  const e = r.sec === 0 && SPK?.maps[r.map]?.rows[r.k];
  return e ? [SPK.sp[e[0]], SPK.gp[e[1]]] : null;
}

function browseGroups(by){
  const m = new Map();
  const put = (key, label, r) => {
    let g = m.get(key);
    if (!g) m.set(key, g = {label, rows:[]});
    g.rows.push(r);
  };
  for (const r of S.rows){
    if (by === 'sec'){ put(r.sec, `${r.sec} · ${SEC_LABEL[r.sec] ?? '절'+r.sec}`, r); continue; }
    if (r.sec !== 0) continue;                       // 화자·맵은 맵 대사에만 있다
    if (by === 'map'){ put(r.map, `맵 ${r.map} · ${mapName(r.map)}`, r); continue; }
    const s = spkOf(r);
    if (!s) continue;
    const k = by === 'sprite' ? s[0] : s[1];
    put(k, k, r);
  }
  const g = [...m.values()];
  // 절·맵은 번호 순(S.rows 순서 그대로), 화자·분류는 많은 것부터
  return by === 'sec' || by === 'map' ? g : g.sort((a,b) => b.rows.length - a.rows.length);
}
function doBrowse(by){
  closePanels();
  if (!by) return;
  GROUPS = browseGroups(by);
  $('meta').textContent = `${BROWSE[by]} — ${GROUPS.length}개 묶음`;
  $('out').innerHTML = GROUPS.length
    ? GROUPS.map((g,i) => `<div class=card style="cursor:pointer" onclick=openGroup(${i})>
        <b>${esc(g.label)}</b> <span class=chip>${g.rows.length}행</span></div>`).join('')
    : '<div class=empty>묶을 행이 없습니다.</div>';
}
function openGroup(i){
  const g = GROUPS[i];
  HITS = g.rows.slice(0, BROWSE_CAP); SHOWN = 0;
  $('meta').textContent = `${g.label} — ${g.rows.length}행` +
    (g.rows.length > BROWSE_CAP ? ` (앞 ${BROWSE_CAP}행만 보여줘요)` : '');
  $('out').innerHTML = '';
  more();
}

// ─── 검색·수정 ────────────────────────────────────────
let HITS=[], SHOWN=0; const STEP=50;

// 태그 검색 — 「분류:도구 맵:12 화자:간호사 상태:수정 나머지는 본문」.
// 값에 공백이 있으면 따옴표(분류:"도구 이름"). 태그 없는 낱말은 번역·원문 양쪽 AND 매칭.
const TAGS = {분류:'sec', 맵:'map', 화자:'spk', 원문:'k', 번역:'v', 상태:'state'};
const TAG_RE = /^(분류|맵|화자|원문|번역|상태):(.*)$/;
const unq = s => s.replace(/^"([^"]*)"?$/, '$1');
function parseQuery(q){
  const f = {sec:[], map:[], spk:[], k:[], v:[], state:[], text:[]};
  for (const part of q.match(/[^\s:"]+:(?:"[^"]*"?|\S*)|"[^"]*"?|\S+/g) ?? []){
    const m = part.match(TAG_RE);
    if (!m){ const t = unq(part); if (t) f.text.push(t); continue; }
    const val = unq(m[2]);
    if (val) f[TAGS[m[1]]].push(val);
  }
  return f;
}
function rowMatch(r, f){
  if (f.sec.length && !f.sec.some(s => String(r.sec) === s || (SEC_LABEL[r.sec] ?? '').includes(s))) return false;
  // 숫자는 맵 번호 정확 일치만 — 이름 부분일치로 흘리면 「맵:1」이 137이나 "1번도로"류 이름까지 쓸어 담는다
  if (f.map.length && !(r.map != null &&
    f.map.some(m => /^\d+$/.test(m) ? String(r.map) === m
                                    : (mapName(r.map) && mapName(r.map).includes(m))))) return false;
  if (f.spk.length){
    const s = spkOf(r);
    if (!s || !f.spk.some(x => s[0].includes(x) || s[1].includes(x))) return false;
  }
  if (!f.k.every(t => r.k && r.k.includes(t))) return false;
  if (!f.v.every(t => r.v && r.v.includes(t))) return false;
  if (f.state.length){
    const id = rid(r);
    const has = {수정:S.edits.has(id), 반영:S.applied.has(id), 메모:memoIndex().has(id)};
    if (!f.state.every(st => has[Object.keys(has).find(k => st.startsWith(k))] )) return false;
  }
  return f.text.every(t => (r.v && r.v.includes(t)) || (r.k && r.k.includes(t)));
}
function search(){
  closePanels();
  const q = $('q').value.trim();
  if (!q){ $('meta').textContent = metaBase(); renderHome(); return; }   // 검색어를 비우면 홈으로
  const f = parseQuery(q);
  HITS = S.rows.filter(r => rowMatch(r, f));
  SHOWN = 0;
  $('meta').textContent = `${HITS.length}행 매칭`;
  $('out').innerHTML = HITS.length ? '' : '<div class=empty>매칭되는 행이 없습니다.</div>';
  if (HITS.length) more();
}

// ─── 검색 자동완성 ────────────────────────────────────
// 커서가 놓인 낱말 기준: 태그 이름 → 그 태그의 값 후보 순으로 제안한다
let SUGN = -1;   // 방향키로 고른 항목 (−1 = 없음)
const STATE_VALS = ['수정','반영','메모'];
function tagValues(tag, part){
  const hit = s => s && s.includes(part);
  if (tag === '분류') return Object.values(SEC_LABEL).filter(hit);
  if (tag === '상태') return STATE_VALS.filter(v => v.startsWith(part));
  if (tag === '맵'){
    const seen = new Map();   // 맵번호 → 이름 (이름이 비어도 번호는 제안)
    for (const r of S.rows) if (r.sec === 0 && r.map != null && !seen.has(r.map)) seen.set(r.map, mapName(r.map));
    return [...seen].filter(([m, n]) => /^\d+$/.test(part) ? String(m) === part : hit(n))
      .map(([m, n]) => ({v:String(m), label:`${m} · ${n || '(이름 없음)'}`}));
  }
  if (tag === '화자' && SPK)
    return [...new Set([...SPK.gp, ...SPK.sp])].filter(hit);
  return [];
}
function suggest(){
  const q = $('q'), upto = q.value.slice(0, q.selectionStart ?? q.value.length);
  const word = upto.split(/\s+/).pop();
  const m = word.match(TAG_RE);
  let items = [];
  if (m && m[1] in TAGS)
    items = tagValues(m[1], unq(m[2])).slice(0, 12).map(x => {
      const v = x.v ?? x, label = x.label ?? x;
      const ins = /\s/.test(v) ? `"${v}"` : v;
      return {ins:`${m[1]}:${ins} `, label:`<b>${m[1]}:</b>${esc(label)}`};
    });
  else if (word)
    items = Object.keys(TAGS).filter(t => t.startsWith(word))
      .map(t => ({ins:`${t}:`, label:`<b>${t}:</b><span class=mi-d style="margin-left:6px">태그로 좁혀요</span>`, stay:true}));
  SUGN = -1;
  if (!items.length){ $('sugg').hidden = true; return; }
  $('sugg')._items = items;
  $('sugg').innerHTML = items.map((it, i) =>
    `<button class=si tabindex=-1 onmousedown="event.preventDefault();acceptSugg(${i})">${it.label}</button>`).join('') +
    '<div class=hint>Tab·클릭으로 채우고 Enter로 검색해요</div>';
  $('sugg').hidden = false;
}
function acceptSugg(i){
  const it = $('sugg')._items?.[i];
  if (!it) return;
  const q = $('q'), pos = q.selectionStart ?? q.value.length;
  const upto = q.value.slice(0, pos), word = upto.split(/\s+/).pop();
  q.value = upto.slice(0, upto.length - word.length) + it.ins + q.value.slice(pos);
  const at = upto.length - word.length + it.ins.length;
  q.setSelectionRange(at, at);
  q.focus();
  suggest();   // 태그 이름을 채웠으면 바로 값 후보로 넘어간다
}
$('q')?.addEventListener('input', suggest);
$('q')?.addEventListener('focus', suggest);
$('q')?.addEventListener('keydown', e => {
  const sg = $('sugg');
  if (!sg.hidden && (e.key === 'ArrowDown' || e.key === 'ArrowUp')){
    e.preventDefault();
    const n = sg._items.length;
    SUGN = (SUGN + (e.key === 'ArrowDown' ? 1 : n - 1) + n) % n;
    [...sg.querySelectorAll('.si')].forEach((b, i) => b.classList.toggle('on', i === SUGN));
    return;
  }
  if (!sg.hidden && (e.key === 'Tab' || (e.key === 'Enter' && SUGN >= 0))){
    e.preventDefault(); acceptSugg(SUGN >= 0 ? SUGN : 0); return;
  }
  if (e.key === 'Enter'){ sg.hidden = true; search(); }
});

// 빈 제보를 막는다 — 수정(미빌드·반영됨)도 메모도 없는 행은 보낼 내용이 없다
const canReport = id => !!(S.edits.has(id) || S.applied.has(id) || memoIndex().has(id));
// 카드를 다시 그리지 않고 제보 버튼만 현재 상태에 맞춘다(입력 중인 글이 날아가지 않게)
function syncReport(i){
  const b = $('rp'+i);
  if (!b) return;
  b.disabled = !canReport(rid(HITS[i]));
  b.title = b.disabled ? '수정하거나 메모를 남긴 행만 제보할 수 있어요' : '';
}
function card(r, i){
  const id = rid(r), e = S.edits.get(id), s = spkOf(r), ev = evOf(r);
  const v = e ? e.v : r.v;
  // 이벤트 칩은 누르면 그 이벤트의 대사를 순서대로 펼친다 — 자리가 여럿이면 목록부터
  const evChip = ev?.length
    ? `<span class="chip ev" onclick=evJump(${i}) title="이 대사가 속한 이벤트 보기">${esc(evName(ev[0]))}${ev.length>1?` 외 ${ev.length-1}곳`:''}</span>` : '';
  return `<div class="card ${e?'saved':''}" id=card${i}>
    <span class=chip>${SEC_LABEL[r.sec]??('절'+r.sec)}</span>${r.map!=null?`<span class=chip>맵 ${r.map}${mapName(r.map)?' · '+esc(mapName(r.map)):''}</span>`:''}${evChip}${s?`<span class=chip>${esc(s[0])} · ${esc(s[1])}</span>`:''}${!e&&S.applied.has(id)?'<span class=chip>반영됨</span>':''}
    ${REPORT_FORM.id?`<button class=ghost id=rp${i} style="float:right" onclick=report(${i})
      ${canReport(id)?'':'disabled title="수정하거나 메모를 남긴 행만 제보할 수 있어요"'}>${ICON.flag} 제보</button>`:''}
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
// 한 행에 새 값을 앉힌다 — 저장 버튼과 일괄 바꾸기가 같은 경로를 쓴다(persist/화면 갱신은 부르는 쪽 몫)
// via는 이 고침이 어느 화면에서 나왔는지다('bulk' = 일괄 바꾸기 화면). 저장 버튼과
// 같은 경로를 쓰므로 여기서 달아 두지 않으면 나중에 가릴 길이 없다.
function applyEdit(r, v, via){
  // textarea는 CR/CRLF를 LF로 접어 돌려준다 — 안 고친 행이 수정으로 잡히지 않게 같은 모양끼리 비교
  const id = rid(r), prev = S.edits.get(id);
  if (v === r.v.replace(/\r\n?/g, '\n')) S.edits.delete(id);
  else S.edits.set(id, {sec:r.sec, map:r.map, idx:r.idx, k:r.k, v, ...(via ? {via} : {})});
  hist({type:'edit', rid:id, k:r.k, old:prev ? prev.v : r.v, new:v, ...(via ? {via} : {})});
}
// 색·이름 코드를 삼키는 저장은 한 번 물어본다 — 지우면 화면이 깨진다
function confirmMarkup(r, v){
  const lost = (r.v.match(MARKUP)||[]).filter(t => !v.includes(t));
  return !lost.length ||
    confirm(`색·이름 코드가 사라졌어요: ${lost.join(' ')}\n지우면 화면이 깨질 수 있어요. 그래도 저장할까요?`);
}
function save(i){
  const r = HITS[i], v = $('v'+i).value;
  if (!confirmMarkup(r, v)) return;
  applyEdit(r, v);
  persist(); updateDirty();
  $('st'+i).className='st ok'; $('st'+i).textContent='저장됨';
  $('card'+i).classList.add('saved');
  syncReport(i);
  toast('저장됨 — [빌드]를 누르면 게임에 반영돼요');
}
// 로그인·지문 채집 없이 기기 단위로만 묶어보는 순수 난수 식별자 — localStorage 초기화 시 재발급됨을 수용
// crypto.randomUUID 미지원·localStorage 접근 실패(사생활 모드 등) 환경에서도 제보 자체는 살린다
function reporterId(){
  try {
    let id = localStorage.getItem('reporter');
    if (!id){
      id = (typeof crypto !== 'undefined' && crypto.randomUUID) ? crypto.randomUUID()
        : 'r' + Math.random().toString(36).slice(2) + Date.now().toString(36);
      localStorage.setItem('reporter', id);
    }
    return id;
  } catch {
    return 'unknown';
  }
}
// 보낸 제보를 기억한다 — 일괄 제보가 저장된 수정 전부를 매번 다시 던져 시트에 같은 행이
// 368행 중 134행 겹쳐 쌓인 적이 있다(2026-08-05 실측). 서명은 「제안+메모」라 값을 고치면
// 서명이 달라져 다시 나간다. no-cors라 전송 성패는 알 수 없으니 「보냈다고 표시한 것」이지
// 「도착한 것」이 아니다 — 놓친 건은 그 행에서 [제보]로 다시 보내면 된다.
let SENT = null;
// 가르는 문자는 본문에 못 들어가는 NUL — 「가 나」+「」와 「가」+「나」가 같아지지 않게
const sig =(suggest, comment) => `${suggest} ${comment}`;
function sentIndex(){
  if (SENT) return SENT;
  try { SENT = new Map(JSON.parse(localStorage.getItem('sent:'+S.base) ?? '[]')); }
  catch { SENT = new Map(); }
  return SENT;
}
function persistSent(){
  try { localStorage.setItem('sent:'+S.base, JSON.stringify([...sentIndex()])); } catch {}
}
function markSent(id, s){ sentIndex().set(id, s); persistSent(); }
// 지금 저장된 수정·메모를 통째로 「보냄」으로 찍는다 — 이 기능 이전에 이미 제보한 사람이
// 일괄 제보를 다시 눌러 수백 건을 겹쳐 보내는 걸 막는 한 번짜리 이주 수단
function markAllSent(){
  const all = new Map([...S.applied, ...S.edits]), memos = memoIndex();
  const ids = [...new Set([...all.keys(), ...memos.keys()])];
  if (!ids.length){ toast('표시할 수정이나 메모가 없어요'); return; }
  if (!confirm(`${ids.length}건을 이미 보낸 것으로 표시할까요?\n표시한 건은 내용을 고치기 전까지 일괄 제보에서 빠져요.`)) return;
  for (const id of ids) sentIndex().set(id, sig(all.get(id)?.v ?? '', memos.get(id)?.text ?? ''));
  persistSent();
  toast(`${ids.length}건을 보낸 것으로 표시했어요`);
}
// 구글폼에 no-cors로 던진다(응답 확인 불가, 실패해도 toast로만 알림)
// silent: 일괄 전송 중 매 건 toast 도배 방지(진행·완료 토스트는 호출부가 낸다)
// patch 칸 표시는 화면 버튼 이름을 그대로 쓴다 — 「모아서 제보」로 보냈으면 「모아서」,
// 「일괄 바꾸기」로 고친 줄이면 「일괄바꾸기」. 폼·시트는 손대지 않는다.
async function sendForm(vals, {batch=false, silent=false, via=null}={}){
  const fd = new FormData(), E = REPORT_FORM.entries;
  for (const [k, v] of Object.entries(vals)) fd.append(E[k], v);
  fd.append(E.patch, `${S.meta ?? 'hash:'+S.sha} / ${APP_VER} / u:${reporterId().slice(0,8)}` +
                     `${batch?' / 모아서':''}${via === 'bulk' ? ' / 일괄바꾸기' : ''}`);
  try {
    await fetch(`https://docs.google.com/forms/d/e/${REPORT_FORM.id}/formResponse`,
      {method:'POST', mode:'no-cors', body:fd});
    if (!silent) toast('제보를 보냈어요 — 고마워요! 다음 판에 반영을 검토합니다', 4000);
  } catch {
    if (!silent) toast('전송이 안 됐어요 — 인터넷 연결을 확인해 주세요', 5000);
  }
}
// 제안=내가 저장한 번역, 코멘트=그 행 메모(없으면 물어본다). 제보는 사본이라 보낸 뒤에도 데이터는 그대로다
async function report(i){
  const r = HITS[i], id = rid(r);
  const e = S.edits.get(id) ?? S.applied.get(id);
  const m = memoIndex().get(id);
  const comment = m ? m.text : prompt('이 행에 남길 한 줄 코멘트 (그냥 제보만 하려면 비워두세요)');
  if (comment === null) return;   // 취소 — 전송하지 않는다
  const s = sig(e ? e.v : '', comment);
  if (sentIndex().get(id) === s &&
      !confirm('이 행은 같은 내용으로 이미 제보했어요. 다시 보낼까요?')) return;
  await sendForm({sec:`${r.sec}:${SEC_LABEL[r.sec] ?? ''}`, idx:`${r.map ?? ''}:${r.idx}`,
                  k:r.k ?? '', v:r.v, suggest: e ? e.v : '', comment}, {via: e?.via ?? null});
  markSent(id, s);
}
// 폼 한 칸에 들어갈 수 있는 길이 — 넘치면 잘리는 대신 잘렸다고 알린다(단건에는 사실상 불필요하나 방어로 유지)
const FIELD_CAP = 30000;
const cut = s => s.length > FIELD_CAP ? s.slice(0, FIELD_CAP) + '…(이하 생략)' : s;
// 수정·메모가 있는 행마다 개별 제보와 같은 필드로 한 행씩 순차 전송한다(「모아서」 표기는 patch 칸에만)
let batchInFlight = false;   // 재진입 가드 — no-cors라 중복 전송을 감지할 길이 없어 시작부터 막는다
async function batchReport(){
  if (batchInFlight){ toast('일괄 제보가 진행 중이에요 — 끝날 때까지 기다려 주세요'); return; }
  const all = new Map([...S.applied, ...S.edits]);   // 같은 행은 미빌드분(edits)이 이긴다
  const memos = memoIndex();
  const byId = new Map(S.rows.map(r=>[rid(r), r]));
  const ids = [...new Set([...all.keys(), ...memos.keys()])];
  if (!ids.length){ toast('보낼 수정이나 메모가 없어요'); return; }
  // 이미 같은 내용으로 보낸 건은 뺀다 — 안 그러면 누를 때마다 저장분 전체가 시트에 겹쳐 쌓인다
  const sent = sentIndex();
  const sigs = new Map(ids.map(id => [id, sig(all.get(id)?.v ?? '', memos.get(id)?.text ?? '')]));
  const fresh = ids.filter(id => sent.get(id) !== sigs.get(id));
  const skipped = ids.length - fresh.length;
  if (!fresh.length){ toast(`이미 보낸 ${skipped}건뿐이에요 — 새로 보낼 게 없어요`, 4000); return; }
  batchInFlight = true;
  $('batchbtn').disabled = true;
  try {
    for (let i = 0; i < fresh.length; i++){
      const id = fresh[i], r = byId.get(id), e = all.get(id), m = memos.get(id);
      toast(`일괄 제보 중... ${i+1}/${fresh.length}건째`);
      await sendForm({sec: r ? `${r.sec}:${SEC_LABEL[r.sec] ?? ''}` : '',
                       idx: r ? `${r.map ?? ''}:${r.idx}` : '',
                       k: r?.k ?? '', v: r?.v ?? '',
                       suggest: e ? cut(e.v) : '', comment: m ? cut(m.text) : ''},
                      {batch:true, silent:true, via: e?.via ?? null});
      markSent(id, sigs.get(id));
    }
    toast(`${fresh.length}건 보냈어요${skipped ? ` (이미 보낸 ${skipped}건은 뺐어요)` : ''}`, 4000);
  } finally {
    batchInFlight = false;
    updateDirty();   // batchbtn 활성 상태를 실제 잔여 수정·메모 기준으로 되돌린다
  }
}
// ─── 문제 제보 (행 무관) ──────────────────────────────
// 특정 문구에 매이지 않는 문제 — 데이터 로드 전에도 보낼 수 있다(로드 실패 자체가 제보감)
const FB_KINDS = ['전반적 번역 문제', '화면·렌더링 문제', '게임 동작 문제', '기타'];
function feedbackMenu(){
  closePanels();
  $('meta').textContent = '문제 제보 — 특정 문구에 매이지 않는 문제를 보내요';
  $('out').innerHTML = `<div class=card>
    <div class=rowbar>${FB_KINDS.map((k, i) =>
      `<label class=chip style="cursor:pointer"><input type=radio name=fbkind value="${k}" ${i ? '' : 'checked'}>${k}</label>`).join('')}</div>
    <textarea id=fbtext style="min-height:120px;margin-top:8px"
      placeholder="어떤 문제인지 적어주세요 — 어디서(맵·화면), 무엇이, 어떻게 보였는지가 있으면 고치기 쉬워요"></textarea>
    <div class=rowbar><button class=primary onclick=sendFeedback()>보내기</button>
      <span class=es>특정 문구의 문제는 검색해서 그 행의 [제보]를 써주세요.</span></div></div>`;
}
async function sendFeedback(){
  const text = $('fbtext').value.trim();
  if (!text){ toast('내용을 적어주세요'); return; }
  const kind = document.querySelector?.('input[name=fbkind]:checked')?.value ?? FB_KINDS[0];
  const fd = new FormData(), E = GENERAL_FORM.entries;
  fd.append(E.kind, kind);
  fd.append(E.text, cut(text));
  fd.append(E.patch, `${S.meta ?? (S.sha ? 'hash:'+S.sha : '미로드')} / ${APP_VER} / u:${reporterId().slice(0,8)}`);
  try {
    await fetch(`https://docs.google.com/forms/d/e/${GENERAL_FORM.id}/formResponse`,
      {method:'POST', mode:'no-cors', body:fd});
    toast('제보를 보냈어요 — 고마워요! 다음 판에 반영을 검토합니다', 4000);
    $('fbtext').value = '';
  } catch {
    toast('전송이 안 됐어요 — 인터넷 연결을 확인해 주세요', 5000);
  }
}

let persistFailed = false;   // 연속 실패 시 토스트 도배 방지
function persist(){
  try {
    localStorage.setItem('edits:'+S.base, JSON.stringify([...S.edits.values()]));
    localStorage.setItem('applied:'+S.base, JSON.stringify([...S.applied.values()]));
    persistFailed = false;
  } catch {
    if (!persistFailed) toast('저장 공간이 가득 찼어요 — 수정 내역 저장이 실패했어요', 5000);
    persistFailed = true;
  }
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
  MEMOS = SENT = null;             // 기준(S.base)이 바뀌면 메모·제보 기록 캐시도 다른 기록의 것이다
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

// ─── 일괄 바꾸기 ──────────────────────────────────────
// 「메달→배지」 일괄 치환이 '배지을' 같은 조사 오류를 21곳 남긴 적이 있다 —
// 모두 바꾸기가 아니라 행별로 결과를 보고 고르는 것이 이 화면의 요점이다
let REPL = []; const REPL_CAP = 500;
// 검색·치환은 지금 값(미빌드 수정 반영) 기준. 원문 CR은 저장값과 같은 LF 모양으로 접는다
const curV = r => S.edits.get(rid(r))?.v ?? (r.v ?? '').replace(/\r\n?/g, '\n');
// 이스케이프한 조각 사이에만 강조를 끼운다 — 원문이 태그로 살아나지 않게
const hl = (parts, s) => parts.map(esc).join(`<mark>${esc(s)}</mark>`);

function replaceMenu(){
  $('meta').textContent = '일괄 바꾸기 — 찾을 문구와 바꿀 문구를 넣고 미리보기하세요';
  $('out').innerHTML = `<div class=card>
    <div class=rowbar>
      <input type=text id=rfind placeholder="찾을 문구" onkeydown="if(event.key==='Enter')replacePreview()">
      <input type=text id=rto placeholder="바꿀 문구 (비우면 삭제)" onkeydown="if(event.key==='Enter')replacePreview()">
    </div>
    <div class=rowbar><button class=primary onclick=replacePreview()>미리보기</button>
      <span class=es>글자 그대로 찾아요(정규식 아님). 고른 행만 적용돼요.</span></div>
  </div><div id=replout></div>`;
}

function replacePreview(){
  const find = $('rfind').value, to = $('rto').value;
  if (!find){ toast('찾을 문구를 넣어주세요'); return; }
  REPL = [];
  let total = 0;
  for (const r of S.rows){
    const v = curV(r);
    if (!v.includes(find)) continue;
    total++;
    if (REPL.length >= REPL_CAP) continue;
    const parts = v.split(find), nv = parts.join(to);
    // 치환이 색·이름 코드를 삼킨 행 — 적용은 할 수 있게 두되 기본 선택에서 뺀다
    const lost = (v.match(MARKUP)||[]).filter(t => !nv.includes(t));
    REPL.push({r, parts, nv, lost});
  }
  $('meta').textContent = `${total}행 매칭` +
    (total > REPL_CAP ? ` — 앞 ${REPL_CAP}행만 보여줘요. 찾을 문구를 더 좁혀주세요` : '');
  if (!total){ $('replout').innerHTML = '<div class=empty>매칭되는 행이 없습니다.</div>'; return; }
  $('replout').innerHTML =
    `<div class=rowbar><button class=ghost onclick=replAll(true)>모두 선택</button>
      <button class=ghost onclick=replAll(false)>모두 해제</button>
      <button class=primary onclick=replaceApply()>선택 적용</button></div>` +
    REPL.map((h, i) => `<div class="card ${h.lost.length?'notecard':''}">
      <label class=rowbar><input type=checkbox id=rc${i} ${h.lost.length?'':'checked'}>
        <span class=chip>${SEC_LABEL[h.r.sec]??('절'+h.r.sec)}</span>${h.r.map!=null?`<span class=chip>맵 ${h.r.map}</span>`:''}
        ${h.lost.length?`<span class="st warn">색·이름 코드가 사라져요: ${esc(h.lost.join(' '))}</span>`:''}</label>
      <div class=es>${hl(h.parts, find)}</div>
      <div class=nv>${hl(h.parts, to)}</div></div>`).join('');
}
// 모두 선택은 경고 행을 건드리지 않는다 — 코드가 깨지는 행은 하나씩 확인하고 켜야 한다
function replAll(on){ REPL.forEach((h, i) => {
  const c = $('rc'+i); if (c && !(on && h.lost.length)) c.checked = on; }); }

function replaceApply(){
  const sel = REPL.filter((_, i) => $('rc'+i)?.checked);
  if (!sel.length){ toast('적용할 행을 골라주세요'); return; }
  for (const h of sel) applyEdit(h.r, h.nv, 'bulk');
  persist(); updateDirty();
  replacePreview();   // 적용된 행은 새 값 기준이라 목록에서 빠진다
  $('meta').textContent = `${sel.length}행 적용 — [빌드]를 누르면 게임에 반영돼요`;
  toast(`${sel.length}행 적용했어요`);
}

// ─── 이력 기록 ────────────────────────────────────────
// append-only — 같은 행을 여러 번 고치면 이벤트도 그만큼 쌓인다
function histAll(){ try { return JSON.parse(localStorage.getItem('hist:'+S.base) ?? '[]'); } catch { return []; } }
function hist(ev){
  const a = histAll();
  a.push({t:new Date().toISOString(), ...ev});
  try { localStorage.setItem('hist:'+S.base, JSON.stringify(a)); } catch {}
}
// 메모는 이력 파생이 아니라 별도 목록이다 — 이력은 지울 수 없고, 지운 메모가 제보에 다시 실리면 안 된다
let MEMOS = null;
function memoIndex(){
  if (MEMOS) return MEMOS;
  const raw = localStorage.getItem('memos:'+S.base);
  if (raw !== null){ try { return MEMOS = new Map(JSON.parse(raw)); } catch {} }
  // 옛 판은 메모가 이력에만 있었다 — 첫 조회에서 한 번 옮긴다(같은 행은 최신 것이 남는다)
  MEMOS = new Map();
  for (const e of histAll()) if (e.type === 'memo') MEMOS.set(e.rid, {text:e.text, k:e.k});
  if (MEMOS.size) persistMemos();
  return MEMOS;
}
function persistMemos(){
  try { localStorage.setItem('memos:'+S.base, JSON.stringify([...memoIndex()])); } catch {}
}
function memoDel(id){
  const m = memoIndex().get(id);
  if (!m) return;
  memoIndex().delete(id);
  persistMemos();
  hist({type:'memo-del', rid:id, k:m.k, text:m.text});
  updateDirty();
}
function memo(i){
  const r = HITS[i], text = $('m'+i).value.trim();
  if (!text){ toast('메모 내용을 적어주세요'); return; }
  memoIndex().set(rid(r), {text, k:r.k});
  persistMemos();
  hist({type:'memo', rid:rid(r), k:r.k, text});
  $('m'+i).value = '';
  $('st'+i).className='st ok'; $('st'+i).textContent='메모 남김';
  syncReport(i);
  updateDirty();   // 메모만 남겨도 제보할 거리가 생긴다
  toast('메모를 이력에 남겼어요 — 빌드에는 들어가지 않아요');
}
const HIST_LABEL = {edit:'수정', memo:'메모', 'memo-del':'메모 삭제',
  build:'빌드', restore:'복원', import:'가져오기'};
function histBody(e){
  if (e.type === 'edit') return `<div class=es>${esc(e.old)}</div><div>→ ${esc(e.new)}</div>`;
  if (e.type === 'memo' || e.type === 'memo-del') return `<div>${esc(e.text)}</div>`;
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
  $('batchbtn').disabled = !(n || S.applied.size || memoIndex().size);
}

// ─── 홈 ───────────────────────────────────────────────
// 검색 전·검색어를 비웠을 때의 빈 화면 자리 — 지금 상태와 할 수 있는 일을 그대로 둔다
const metaBase = () => `${S.rows.length.toLocaleString()}행 로드 · 패치 ${S.meta ?? '(표식 없음 · '+S.sha+')'}`;
function renderHome(){
  const recent = histAll().slice(-5).reverse();
  const line = (label, desc, fn) =>
    `<div class=rowbar><button class=ghost onclick=${fn}>${label}</button><span class=es>${desc}</span></div>`;
  $('out').innerHTML = `<div class=card>
    <span style="cursor:pointer" onclick=showMine() title="저장한 수정과 메모를 보고 고쳐요"><span class=chip>대기 ${S.edits.size}건</span><span class=chip>반영됨 ${S.applied.size}건</span><span class=chip>메모 ${memoIndex().size}건</span></span>
    <div class=es>어색한 문구를 검색해 바로 고치세요. 고칠 자리가 정해지지 않았다면 위쪽 [찾아보기]로 맵·분류${SPK?'·화자':''}별로 훑어볼 수 있어요.</div></div>
    <div class=card><div>최근 이력</div>${
      recent.length ? recent.map(e=>`<div class=es>${new Date(e.t).toLocaleString('ko-KR')} · ${HIST_LABEL[e.type] ?? e.type}${e.k?' · '+esc(e.k):''}</div>`).join('')
        : '<div class=es>아직 이력이 없어요 — 수정·메모·빌드가 여기에 쌓여요.</div>'}</div>
    <div class=card><div>할 수 있는 일</div>
      ${line('내 수정', '저장해 둔 수정과 메모를 다시 고치거나 지워요.', 'showMine()')}
      ${line('모아서 제보', '저장한 수정과 메모를 한 번에 보내요.', 'batchReport()')}
      ${GENERAL_FORM.id ? line('문제 제보', '전반적 번역·화면 표시 문제처럼 특정 문구에 매이지 않는 제보예요.', 'feedbackMenu()') : ''}
      ${line('이미 보낸 것으로 표시', '예전에 제보한 수정을 일괄 제보에서 빼요.', 'markAllSent()')}
      ${line('내보내기', '고침 파일로 내려받아 다른 사람과 나눠요.', 'exportFix()')}
      ${line('이력', '지금까지의 수정·메모·빌드를 모두 봐요.', 'showHist()')}</div>`;
}

// ─── 빌드·복원 ────────────────────────────────────────
async function build(){
  if (!S.edits.size){ toast('저장된 수정이 없어요'); return; }
  // 복원과 맞잠금 — 빌드 중에 복원하면 이 빌드 산출물이 방금 되돌린 파일을 덮는다
  const b = $('buildbtn'); b.disabled = true; $('buildlabel').textContent = '빌드 중...';
  $('restorebtn').disabled = true;
  // rid까지 포함한 스냅샷 — 빌드 도는 사이 저장된 수정이 반영됨으로 잘못 넘어가는 걸 막는다
  const snapshot = [...S.edits];
  const n = snapshot.length;
  let wrote = false;
  try {
    const out = await pyBuild(snapshot.map(([, e]) => e));
    // 직전본 백업 → 본체 기록 (원본 .bak은 openFolder에서 이미 보존)
    const cur = await readFile(S.dir, 'Data/korean.dat');
    await writeFile(S.dir, 'Data/korean.dat.prev', cur);
    await writeFile(S.dir, 'Data/korean.dat', out);
    wrote = true;
    // 빌드 산출물로 상태 재동기화 — 반영 끝난 edits는 applied로 옮긴다(중복 적용 방지 + 내보내기엔 남김)
    await loadCore(out);
    // 스냅샷의 rid만 옮긴다 — 빌드 중 같은 rid가 다시 저장됐으면(참조가 바뀜) pending에 남겨 덮지 않는다
    for (const [id, e] of snapshot) {
      if (S.edits.get(id) === e) { S.applied.set(id, e); S.edits.delete(id); }
    }
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
    b.disabled = false; $('buildlabel').textContent = '빌드 → 게임 반영';
    $('restorebtn').disabled = false;
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
      // 이미 빌드된 내 수정(applied)도 충돌 재료다 — 안 그러면 조용히 덮인다
      const mine = S.edits.get(rid(e)) ?? S.applied.get(rid(e));
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

// 백업 파일의 시각·크기 — 표시용이라 못 읽으면 조용히 생략한다
async function fileInfo(dir, path){
  try {
    let h = dir;
    const parts = path.split('/');
    for (const p of parts.slice(0,-1)) h = await h.getDirectoryHandle(p);
    const f = await (await h.getFileHandle(parts.at(-1))).getFile();
    return `${new Date(f.lastModified).toLocaleString('ko-KR')} · ${Math.round(f.size/1024).toLocaleString()}KB`;
  } catch { return null; }
}

async function restoreMenu(){
  const hasPrev = await exists(S.dir, 'Data/korean.dat.prev');
  const [bakInfo, prevInfo] = await Promise.all([
    fileInfo(S.dir, 'Data/korean.dat.bak'),
    hasPrev ? fileInfo(S.dir, 'Data/korean.dat.prev') : null]);
  const cardOf = (title, desc, src, why) => `<div class=card>
    <div>${title}</div><div class=es>${esc(desc)}</div>
    <div class=rowbar>${why
      ? `<button disabled>복원할 수 없어요</button><span class=st>${esc(why)}</span>`
      : `<button class=primary onclick="doRestore('${src}')">이걸로 복원</button>`}</div></div>`;
  $('meta').textContent = '복원 — 되돌릴 파일을 고르세요';
  $('out').innerHTML =
    `<div class=meta>korean.dat을 백업으로 되돌려요. 저장해 둔 수정은 지워지지 않고 미반영 상태로 남아요.</div>` +
    cardOf('순정 원본으로', bakInfo ? `한글패치 설치 직후 상태 · 보존 ${bakInfo}` : '한글패치 설치 직후 상태',
           'Data/korean.dat.bak') +
    cardOf('직전 빌드 전으로', prevInfo ? `마지막 빌드 직전 상태 · 저장 ${prevInfo}` : '마지막 빌드 직전 상태',
           'Data/korean.dat.prev', hasPrev ? null : '아직 빌드한 적이 없어요') +
    `<div class=rowbar><button class=ghost onclick=cancelRestore()>취소</button></div>`;
}
function cancelRestore(){
  $('meta').textContent = metaBase();
  renderHome();
}

// 복원한 파일을 화면 상태에 반영하기 전까지 빌드·내보내기를 막는다 —
// 구 메모리 상태로 빌드하면 방금 되돌린 파일이 조용히 다시 덮인다
async function doRestore(src){
  for (const id of ['buildbtn','exportbtn','restorebtn']) $(id).disabled = true;
  try {
    await writeFile(S.dir, 'Data/korean.dat', await readFile(S.dir, src));
  } catch (err) {
    for (const id of ['buildbtn','exportbtn','restorebtn']) $(id).disabled = false;
    toast('복원 실패 — 파일은 그대로예요: ' + err.message, 6000);
    return;
  }
  hist({type:'restore', src});
  // dat에 반영돼 있던 수정이 파일에서 사라졌다 — "반영됨" 표시를 지우고 미빌드 수정으로 합류시킨다
  for (const [id, e] of S.applied) if (!S.edits.has(id)) S.edits.set(id, e);
  S.applied = new Map();
  persist(); updateDirty();
  $('out').innerHTML = '<div class=card><div>복원했어요 — 새 파일로 다시 불러오는 중...</div></div>';
  await reloadAfterRestore(src);
}

async function reloadAfterRestore(src){
  try {
    await loadCore(await readFile(S.dir, 'Data/korean.dat'));
    for (const id of ['buildbtn','exportbtn','restorebtn']) $(id).disabled = false;
    $('meta').textContent = `${S.rows.length.toLocaleString()}행 다시 로드 · 패치 ${S.meta ?? '(표식 없음 · '+S.sha+')'}`;
    $('out').innerHTML = `<div class=card><div>복원 완료 — ${esc(src)}</div>
      <div class=es>새로고침 없이 다시 불러왔어요. 게임을 재시작하면 화면에 보여요.</div>` +
      (S.edits.size ? `<div>미반영 수정 ${S.edits.size}건이 남아 있어요 — [빌드]를 누르면 다시 들어가요.</div>` : '') +
      '</div>';
    toast('복원 완료 — 게임을 재시작하면 보여요', 4000);
  } catch (err) {
    $('restorebtn').disabled = false;   // 빌드·내보내기는 계속 잠근다 — 화면이 아직 옛 파일 기준이다
    $('out').innerHTML = `<div class=card><div>파일은 복원했지만 다시 불러오기에 실패했어요.</div>
      <div class=es>${esc(err.message)}</div>
      <div>다시 불러오기 전에는 빌드·내보내기를 쓸 수 없어요.</div>
      <div class=rowbar><button class=primary onclick="reloadAfterRestore('${esc(src)}')">다시 불러오기</button></div></div>`;
  }
}

// 지난 폴더가 남아 있을 때만 재연결 버튼을 드러낸다
idbGet('dirHandle').then(h => { if (h) $('reopenbtn').style.display = ''; }).catch(()=>{});

// 일반 제보 폼이 아직 없으면 메뉴에서 숨긴다 (행 단위 제보와 별개 폼)
if (!GENERAL_FORM.id) $('fbbtn').style.display = 'none';

// 엔진 선시동 — 폴더를 고르는 동안 다운로드·시동이 겹치게 지금 시작한다.
// 실패(오프라인 등)는 조용히 묻는다 — 실제 폴더 열기 때 bootPy가 다시 시도한다.
bootPy().catch(()=>{});
