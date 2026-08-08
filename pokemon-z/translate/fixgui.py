# /// script
# requires-python = ">=3.12"
# ///
"""번역 즉석 수정 GUI — 검색·행 수정·메모·재빌드를 브라우저에서.

    uv run translate/fixgui.py          # http://localhost:8787
    uv run translate/fixgui.py 8899     # 포트 지정

Windows 브라우저에서 localhost로 바로 열린다(WSL 포트 공유).
수정 저장은 jsonl 행 단위 교체이고, [빌드] 버튼이 build.py를 돌려
보관소·게임 양쪽 korean.dat까지 갱신한다. 메모는 fixnotes.jsonl 축적
(fix.py --notes와 같은 파일).
"""

import json
import subprocess
import sys
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).parent
LEDGER = HERE.parent / "docs" / "ledger"   # 판정 대장 (glossary·voices)
KO = HERE / "ko"
NOTES = HERE / "fixnotes.jsonl"
JOIN = HERE / "data" / "map-speaker-join.jsonl.gz"
GROUPS = HERE / "sprite-groups.json"

_ctx = None  # (map,k) → {"sprite","group","map_name"} 지연 로드


def ctx():
    global _ctx
    if _ctx is None:
        import gzip
        import re
        _ctx = {"row": {}, "mapname": {}}
        try:
            g = json.loads(GROUPS.read_text(encoding="utf-8"))["groups"]
            s2g = {s: grp for grp, ss in g.items() for s in ss}
            stem = lambda s: re.sub(r"(ow|OW|TS|w)?\d*$", "", s) or "(없음)"
            for line in gzip.open(JOIN, "rt", encoding="utf-8"):
                d = json.loads(line)
                if "sprite" not in d:
                    continue
                key = (d["map"], d["k"])
                if key not in _ctx["row"]:
                    _ctx["row"][key] = {"sprite": d["sprite"] or "(없음)",
                                        "group": s2g.get(stem(d["sprite"]), "?")}
                _ctx["mapname"].setdefault(d["map"], d.get("map_name", ""))
        except Exception as e:
            print("조인표 로드 실패(찾아보기 축소):", e)
    return _ctx

PAGE = """<!doctype html><html lang=ko><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Z 번역 스튜디오</title>
<style>
 :root{--bg:#16171b;--panel:#1e2026;--card:#23252c;--line:#32343d;--tx:#e6e7ea;--sub:#9a9ca6;
   --acc:#5b8def;--acc2:#3d68c4;--ok:#4cc38a;--warn:#e5a54b;--err:#e5644b;--es:#93b8f2}
 *{box-sizing:border-box}
 body{font-family:'Pretendard','Malgun Gothic',system-ui,sans-serif;margin:0;background:var(--bg);color:var(--tx)}
 header{position:sticky;top:0;z-index:10;background:var(--panel);border-bottom:1px solid var(--line);
   display:flex;align-items:center;gap:14px;padding:12px 22px;flex-wrap:wrap}
 .logo{font-weight:700;font-size:15px;letter-spacing:.3px;white-space:nowrap}
 .logo b{color:var(--acc)}
 .searchwrap{flex:1;display:flex;gap:8px;min-width:280px;max-width:640px}
 input,select,textarea,button{font-family:inherit;font-size:13.5px;color:var(--tx);
   background:var(--card);border:1px solid var(--line);border-radius:8px}
 input[type=text]{flex:1;padding:9px 12px}
 input:focus,textarea:focus{outline:none;border-color:var(--acc)}
 select{padding:8px 10px}
 button{padding:8px 14px;cursor:pointer;transition:background .12s}
 button:hover{background:#2c2e37}
 button.primary{background:var(--acc);border-color:var(--acc);color:#fff;font-weight:600}
 button.primary:hover{background:var(--acc2)}
 button.ghost{background:transparent}
 #dirty{display:none;font-size:12.5px;color:var(--warn);background:rgba(229,165,75,.12);
   border:1px solid rgba(229,165,75,.35);border-radius:20px;padding:4px 12px}
 main{max-width:1060px;margin:18px auto;padding:0 22px 80px}
 .meta{color:var(--sub);font-size:13px;margin:6px 2px 14px}
 .card{background:var(--card);border:1px solid var(--line);border-radius:10px;
   padding:12px 16px;margin-bottom:12px}
 .card.saved{border-color:rgba(76,195,138,.5)}
 .chip{display:inline-block;font-size:11.5px;color:var(--sub);background:var(--panel);
   border:1px solid var(--line);border-radius:5px;padding:2px 8px;margin-right:6px}
 .es{color:var(--es);font-size:13px;line-height:1.55;margin:8px 0 6px;white-space:pre-wrap}
 textarea{width:100%;min-height:48px;padding:8px 10px;line-height:1.6;resize:vertical;white-space:pre-wrap}
 .rowbar{display:flex;gap:8px;align-items:center;margin-top:8px;flex-wrap:wrap}
 .memoin{flex:1;min-width:160px;padding:7px 10px}
 .st{font-size:12.5px} .st.ok{color:var(--ok)} .st.warn{color:var(--err)}
 .empty{color:var(--sub);text-align:center;padding:60px 0;font-size:14px}
 .notecard{border-left:3px solid var(--warn)}
 .notecard.done{border-left-color:var(--ok);opacity:.55}
 #toast{position:fixed;right:22px;bottom:22px;background:var(--panel);border:1px solid var(--line);
   border-radius:10px;padding:11px 18px;font-size:13.5px;box-shadow:0 6px 24px rgba(0,0,0,.45);
   opacity:0;transition:opacity .2s;pointer-events:none}
 #toast.show{opacity:1}
 kbd{font-size:11px;color:var(--sub);border:1px solid var(--line);border-radius:4px;padding:1px 5px;background:var(--panel)}
 .more{width:100%;padding:11px}
</style></head><body>
<header>
 <div class=logo>Z <b>번역 스튜디오</b></div>
 <div class=searchwrap>
  <input type=text id=q placeholder="문구 검색 — 한국어 번역 또는 스페인어 원문" autofocus>
  <select id=filef><option value="">전체 파일</option></select>
  <button class=primary onclick=search()>검색</button>
  <select id=browseby onchange=doBrowse()>
   <option value="">찾아보기…</option>
   <option value=map>맵별</option>
   <option value=sprite>화자별</option>
   <option value=group>분류별</option>
   <option value=file>파일별</option>
  </select>
 </div>
 <span id=dirty></span>
 <button onclick=build() id=buildbtn>빌드 → 게임 반영</button>
 <button class=ghost onclick=replUI()>바꾸기</button>
 <button class=ghost onclick=refSearch()>참고</button>
 <button class=ghost onclick=notes()>메모</button>
 <button class=ghost onclick=histView()>이력</button>
</header>
<main>
 <div class=meta id=meta>검색어를 입력하세요. 저장 <kbd>Ctrl+Enter</kbd> · 검색 <kbd>Enter</kbd></div>
 <div id=out><div class=empty>어색한 문구를 발견하면 여기서 찾아 바로 고치세요.<br>
  확신이 없으면 메모로 남겨 두면 됩니다 — 나중에 한꺼번에 처리해요.</div></div>
</main>
<div id=toast></div>
<script>
const $=id=>document.getElementById(id);
let HITS=[],SHOWN=0,DIRTY=0;const STEP=50;
$('q').addEventListener('keydown',e=>{if(e.key==='Enter')search()});
function toast(m,ms=2200){const t=$('toast');t.textContent=m;t.classList.add('show');
 clearTimeout(t._h);t._h=setTimeout(()=>t.classList.remove('show'),ms)}
function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML}
function dirty(n){DIRTY+=n;const d=$('dirty');
 if(DIRTY>0){d.style.display='inline-block';d.textContent=`저장 ${DIRTY}건 — 빌드 필요`}
 else d.style.display='none'}
async function search(){
 const q=$('q').value.trim(); if(!q)return;
 $('meta').textContent='검색 중...';
 const f=$('filef').value;
 const r=await fetch('/search?q='+encodeURIComponent(q)+(f?'&file='+encodeURIComponent(f):''));
 const js=await r.json(); HITS=js.hits; SHOWN=0;
 $('meta').textContent=`${js.hits.length}행 매칭`+(js.truncated?' (상한 500행)':'');
 if(!js.hits.length){$('out').innerHTML='<div class=empty>매칭되는 행이 없습니다.</div>';return}
 $('out').innerHTML=''; more();
 const files=[...new Set(js.hits.map(h=>h.file))];
 $('filef').innerHTML='<option value="">전체 파일</option>'+files.map(f=>`<option>${f}</option>`).join('');
}
function more(){
 const frag=HITS.slice(SHOWN,SHOWN+STEP).map((h,k)=>{const i=SHOWN+k;return `
  <div class=card id=card${i}>
   <span class=chip>${esc(h.file)}:${h.line}</span>${h.map!==null&&h.map!==undefined?`<span class=chip>맵 ${h.map}</span>`:''}${h.sprite&&h.sprite!=='?'?`<span class=chip>${esc(h.sprite)}</span>`:''}${h.group&&h.group!=='?'?`<span class=chip>${esc(h.group)}</span>`:''}
   <div class=es>${esc(h.es)}</div>
   <textarea id=v${i} data-orig="${esc(h.v)}"
     onkeydown="if(event.ctrlKey&&event.key==='Enter')save(${i},'${h.file}',${h.line})">${esc(h.v)}</textarea>
   <div class=rowbar>
    <button class=primary onclick=save(${i},'${h.file}',${h.line})>저장</button>
    <button class=ghost onclick=showOrig(${i})>원본</button>
    <input class=memoin id=m${i} placeholder="메모 — 나중에 배치로 손볼 내용">
    <button onclick=memo(${i})>메모</button>
    <span class=st id=st${i}></span>
   </div>
   <div class=es id=orig${i} style="display:none"></div>
  </div>`}).join('');
 SHOWN=Math.min(SHOWN+STEP,HITS.length);
 const btn=$('morebtn');if(btn)btn.remove();
 $('out').insertAdjacentHTML('beforeend',frag);
 if(SHOWN<HITS.length)$('out').insertAdjacentHTML('beforeend',
  `<button class=more id=morebtn onclick=more()>더 보기 (${HITS.length-SHOWN}행 남음)</button>`);
}
async function save(i,file,line){
 const v=$('v'+i).value;
 const r=await fetch('/save',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({file,line,v})});
 const js=await r.json();
 if(js.ok){$('st'+i).className='st ok';$('st'+i).textContent='저장됨';
  $('card'+i).classList.add('saved');dirty(1);toast('저장됨 — 빌드하면 게임에 반영돼요')}
 else{$('st'+i).className='st warn';$('st'+i).textContent=js.err}
}
async function memo(i){
 const note=$('m'+i).value.trim()||'(내용 없음)';
 await fetch('/note',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({query:$('v'+i).value.slice(0,80),note})});
 $('st'+i).className='st ok';$('st'+i).textContent='메모 기록됨';toast('메모에 쌓아 뒀어요')
}
async function build(){
 const b=$('buildbtn');b.disabled=true;b.textContent='빌드 중...';
 const r=await fetch('/build',{method:'POST'});const js=await r.json();
 b.disabled=false;b.textContent='빌드 → 게임 반영';
 if(js.ok){DIRTY=0;dirty(0);toast('빌드 완료 — 게임을 재시작하면 반영됩니다',3200)}
 else toast('빌드 실패: '+js.msg,5000);
}
async function notes(){
 const r=await fetch('/notes');const js=await r.json();
 const pend=js.notes.filter(n=>!n.done).length;
 $('meta').textContent=`메모 — 미결 ${pend}건 / 전체 ${js.notes.length}건`;
 $('out').innerHTML=js.notes.map((n,i)=>`
  <div class="card notecard ${n.done?'done':''}">
   <span class=chip>${i+1}</span> 「${esc(n.query)}」
   <div class=es>${esc(n.note)}</div>
   <div class=rowbar>
    <button onclick=gotoNote(${JSON.stringify(n.query).replace(/"/g,'&quot;')})>대상 찾아가기</button>
    <button onclick=doneNote(${i+1},${n.done?'false':'true'})>${n.done?'완료 취소':'완료 처리'}</button>
    <button class=ghost onclick=delNote(${i+1})>삭제</button>
   </div>
  </div>`).join('')||'<div class=empty>메모가 없습니다.</div>';
}
function gotoNote(q){$('q').value=q;search()}
async function doneNote(i,done){
 await fetch('/done',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({i,done})});
 notes();
}
async function delNote(i){
 await fetch('/notedel',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({i})});
 notes();
}
function showOrig(i){
 const el=$('orig'+i);const ta=$('v'+i);
 if(el.style.display==='none'){
  el.innerHTML='저장 전 원본: '+esc(ta.dataset.orig)+' &nbsp;<button class=ghost onclick="restoreOrig('+i+')">이 값으로 되돌리기</button>';
  el.style.display='block';
 }else el.style.display='none';
}
function restoreOrig(i){$('v'+i).value=$('v'+i).dataset.orig;toast('되돌렸어요 — 저장을 눌러야 반영됩니다')}
const KIND={row:'행 수정',bulk:'일괄 바꾸기',revert:'되돌리기'};
async function histView(){
 const r=await fetch('/history');const js=await r.json();
 $('meta').textContent=`이력 — 동작 ${js.ops.length}묶음`;
 $('out').innerHTML=js.ops.map(o=>`
  <div class=card>
   <span class=chip>${KIND[o.kind]||o.kind}</span><span class=chip>${o.rows.length}행</span>
   ${o.label?`<span class=chip>${esc(o.label)}</span>`:''}
   ${o.rows.slice(0,5).map(h=>`<div class=es>${esc(h.file)}:${h.line} · 구: ${esc(h.old)}<br>&nbsp;&nbsp;신: ${esc(h.new)}</div>`).join('')}
   ${o.rows.length>5?`<div class=chip>외 ${o.rows.length-5}행</div>`:''}
   <div class=rowbar><button onclick="revertOp('${esc(o.op)}')">이 묶음 되돌리기</button></div>
  </div>`).join('')||'<div class=empty>저장 이력이 없습니다.</div>';
}
async function revertOp(op){
 const r=await fetch('/revert',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({op})});
 const js=await r.json();
 dirty(js.done);
 toast(`${js.done}행 되돌림`+(js.skipped?` · ${js.skipped}행 건너뜀(뒤에 다시 고쳐진 자리)`:'')
   +(js.errs&&js.errs.length?` · 실패 ${js.errs.length}`:''),4000);
 histView();
}
let PLAN=[];
function replUI(){
 $('meta').textContent='일괄 바꾸기 — 미리보기로 대상을 확인하고 고른 자리만 적용합니다.';
 $('out').innerHTML=`<div class=card>
  <div class=rowbar><input type=text id=rfind placeholder="찾을 문구 (번역 칸) — 비우면 원문 기준">
   <input type=text id=rrepl placeholder="바꿀 문구"></div>
  <div class=rowbar><input type=text id=rsrc placeholder="원문(스페인어) 조건 — 선택">
   <input type=text id=rfile placeholder="파일 이름 — 선택 (예: 00-maps.jsonl)">
   <button class=primary onclick=replPlan()>미리보기</button></div>
  <div class=meta>찾을 문구를 비우고 원문 조건만 주면 그 원문을 가진 행의 번역을 통째로 갈아 끼웁니다.</div>
 </div><div id=plan></div>`;
}
async function replPlan(){
 const body={find:$('rfind').value,repl:$('rrepl').value,src:$('rsrc').value,file:$('rfile').value};
 $('plan').innerHTML='<div class=empty>찾는 중...</div>';
 const r=await fetch('/replan',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify(body)});
 const js=await r.json();
 if(!js.ok){$('plan').innerHTML=`<div class=empty>${esc(js.err)}</div>`;return}
 PLAN=js.hits;
 if(!PLAN.length){$('plan').innerHTML='<div class=empty>바뀔 행이 없습니다.</div>';return}
 $('plan').innerHTML=`<div class=card><b>${PLAN.length}행 바뀝니다</b>${PLAN.length>=500?' (상한 500)':''}
   <div class=rowbar><button class=primary onclick=replApply()>선택 적용</button>
    <button class=ghost onclick="planAll(true)">전체 선택</button>
    <button class=ghost onclick="planAll(false)">전체 해제</button></div></div>`
  +PLAN.map((h,i)=>`<div class=card id=pc${i}>
    <label class=rowbar><input type=checkbox id=pk${i} checked>
     <span class=chip>${esc(h.file)}:${h.line}</span></label>
    <div class=es>${esc(h.es)}</div>
    <div class=es>구: ${esc(h.v)}</div><div>신: ${esc(h.new)}</div>
   </div>`).join('')
  +(js.skipped.length?`<div class=card><b>원문 조건에 걸려 뺀 행 ${js.skipped.length}</b>`
    +js.skipped.map(h=>`<div class=es>${esc(h.file)}:${h.line} · ${esc(h.es)}<br>${esc(h.v)}</div>`).join('')
    +'</div>':'');
}
function planAll(on){PLAN.forEach((_,i)=>{const c=$('pk'+i);if(c)c.checked=on})}
async function replApply(){
 const items=PLAN.filter((_,i)=>$('pk'+i)&&$('pk'+i).checked);
 if(!items.length){toast('고른 자리가 없어요');return}
 const label=`「${$('rfind').value||'(원문 기준)'}」→「${$('rrepl').value}」`;
 const r=await fetch('/replace',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({items,label})});
 const js=await r.json();
 dirty(js.done);
 toast(`${js.done}행 반영`+(js.errs.length?` · 실패 ${js.errs.length}`:'')+' — 빌드하면 게임에 반영돼요',4000);
 histView();
}
async function refSearch(){
 const q=$('q').value.trim(); if(!q){toast('검색창에 찾을 용어를 입력하세요');return}
 $('meta').textContent='참고 자료 검색 중... (첫 실행은 코퍼스 로드로 수십 초)';
 const r=await fetch('/ref?q='+encodeURIComponent(q)); const js=await r.json();
 $('meta').textContent=`참고 — 「${q}」`;
 const sec=(t,rows)=>rows.length?`<div class=card><b>${t}</b>${rows}</div>`:'';
 $('out').innerHTML=
  sec('용어집 (glossary.md)', js.glossary.map(l=>`<div class=es>${esc(l)}</div>`).join(''))+
  sec('본가 정식명 (canon)', js.canon.map(c=>`<div class=es>${esc(c.es||'')} · ${esc(c.en||'')} → <b>${esc(c.ko||'')}</b> <span class=chip>${esc(c.domain||'')}</span></div>`).join(''))+
  sec('공식 문장 코퍼스 (참고용 — 자동 적용 금지)', js.messages.map(m=>`<div class=es>[${esc(m.src||'')}·${esc(m.file||'')}] ${esc(m.es||'')}<br>→ ${esc(m.ko||'')}</div>`).join(''))
  ||'<div class=empty>참고 자료에 매칭이 없습니다.</div>';
}
async function doBrowse(){
 const by=$('browseby').value; if(!by)return;
 $('meta').textContent='불러오는 중...';
 const r=await fetch('/browse?by='+by); const js=await r.json();
 const names={map:'맵',sprite:'화자',group:'분류',file:'파일'};
 $('meta').textContent=`${names[by]}별 — ${js.groups.length}개 묶음`;
 $('out').innerHTML=js.groups.map(g=>`
  <div class=card style="cursor:pointer" onclick="openGroup('${by}','${esc(g.key)}')">
   <b>${esc(g.label)}</b> <span class=chip>${g.count}행</span>
  </div>`).join('');
}
async function openGroup(by,key){
 $('meta').textContent='불러오는 중...';
 const r=await fetch('/list?by='+by+'&key='+encodeURIComponent(key)); const js=await r.json();
 HITS=js.hits; SHOWN=0;
 $('meta').textContent=`${key} — ${js.hits.length}행`+(js.hits.length>=500?' (상한 500)':'');
 $('out').innerHTML=''; more();
}
</script></body></html>"""


def iter_rows(only_file=""):
    """정본 전 행(v를 가진 행만) — {file,line,map,es,v}."""
    for p in sorted(KO.glob("*.jsonl")):
        if only_file and p.name != only_file:
            continue
        cur_map = None
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            d = json.loads(line)
            if "map" in d and "n" in d:
                cur_map = d["map"]
                continue
            v = d.get("v")
            if v is None:
                continue
            yield {"file": p.name, "line": i, "map": cur_map,
                   "es": d.get("k") or d.get("es") or "", "v": v}


def search(q, only_file=""):
    hits = []
    for r in iter_rows(only_file):
        if q in r["v"] or q in r["es"]:
            hits.append(r)
            if len(hits) >= 500:
                return hits, True
    return hits, False


def plan_replace(rows, find, repl, src=""):
    """세 갈래 일괄 바꾸기의 대상 산정.

    find 있음 → 번역 칸에서 찾는다(src를 주면 그 말이 원문에 있는 행만).
    find 없음 → 원문 기준: src를 가진 행의 번역을 repl로 통째 갈아 끼운다.
    돌려주는 skipped는 **원문 조건에 걸려 빠진 행** — 개수만 알리면 조건이 좁아
    놓친 자리를 확인할 길이 없다.
    """
    if not find and not src:
        return [], [], "찾을 문구나 원문 조건 중 하나는 필요합니다"
    hits, skipped = [], []
    for r in rows:
        if find:
            if find not in r["v"]:
                continue
            if src and src not in r["es"]:
                skipped.append(r)
                continue
            new = r["v"].replace(find, repl)
        else:
            if src not in r["es"]:
                continue
            new = repl
        if new == r["v"]:
            continue
        hits.append({**r, "new": new})
        if len(hits) >= 500:
            break
    return hits, skipped[:200], None


FIXLOG = HERE / "fixlog.jsonl"


def new_op():
    return str(time.time_ns())


def save_row(file, line, new_v, op=None, kind="row", label=""):
    p = KO / file
    if not p.is_file() or p.parent != KO:
        return "잘못된 파일"
    lines = p.read_text(encoding="utf-8").splitlines()
    d = json.loads(lines[line - 1])
    if "v" not in d:
        return "이 행에는 v가 없음"
    old = d["v"]
    if old == new_v:
        return None
    d["v"] = new_v
    lines[line - 1] = json.dumps(d, ensure_ascii=False)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with open(FIXLOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({"file": file, "line": line, "es": d.get("k", ""),
                            "old": old, "new": new_v,
                            "op": op or new_op(), "kind": kind, "label": label},
                           ensure_ascii=False) + "\n")
    return None


def apply_replace(items, label):
    """고른 자리를 한 동작으로 묶어 적용 — (반영 수, 실패 목록)."""
    op, done, errs = new_op(), 0, []
    for it in items:
        err = save_row(it["file"], int(it["line"]), it["new"], op=op,
                       kind="bulk", label=label)
        if err:
            errs.append(f"{it['file']}:{it['line']} {err}")
        else:
            done += 1
    return done, errs


def log_rows():
    if not FIXLOG.exists():
        return []
    return [json.loads(l) for l in FIXLOG.read_text(encoding="utf-8").splitlines() if l]


def history(limit=60):
    """이력을 동작 묶음으로 세운다 — op가 없는 옛 줄은 한 줄이 곧 한 묶음."""
    ops, order = {}, []
    for i, r in enumerate(log_rows()):
        key = r.get("op") or f"legacy{i}"
        if key not in ops:
            ops[key] = {"op": key, "kind": r.get("kind", "row"),
                        "label": r.get("label", ""), "rows": []}
            order.append(key)
        ops[key]["rows"].append(r)
    return [ops[k] for k in order[::-1][:limit]]


def revert_op(opid):
    """묶음째 되돌린다. 그 뒤에 다시 고쳐진 행은 건너뛴다 — 남의 고침을 지우게 된다."""
    rows = next((g["rows"] for g in history(10**9) if g["op"] == opid), [])
    if not rows:
        return 0, 0, ["그 묶음이 이력에 없습니다"]
    cur = {(r["file"], r["line"]): r["v"] for r in iter_rows()}
    op, done, skipped, errs = new_op(), 0, 0, []
    for r in rows[::-1]:
        if cur.get((r["file"], r["line"])) != r["new"]:
            skipped += 1
            continue
        err = save_row(r["file"], r["line"], r["old"], op=op, kind="revert",
                       label=f"{opid} 되돌리기")
        if err:
            errs.append(f"{r['file']}:{r['line']} {err}")
        else:
            done += 1
    return done, skipped, errs


_ref = None  # 참고 자료 지연 로드


def ref_search(q):
    global _ref
    if _ref is None:
        import gzip
        _ref = {"gloss": (LEDGER / "glossary.md").read_text(encoding="utf-8").splitlines(),
                "canon": [], "msgs": []}
        cp = HERE / "canon" / "canon.jsonl"
        if cp.exists():
            _ref["canon"] = [json.loads(l) for l in cp.read_text(encoding="utf-8").splitlines() if l]
        mp = HERE / "canon" / "messages.jsonl.gz"
        if mp.exists():
            _ref["msgs"] = [json.loads(l) for l in gzip.open(mp, "rt", encoding="utf-8")]
    gl = [ln for ln in _ref["gloss"] if q in ln][:20]
    ca = [r for r in _ref["canon"]
          if any(q in str(r.get(k, "")) for k in ("es", "ko", "en"))][:20]
    ms = [r for r in _ref["msgs"] if q in r.get("es", "") or q in r.get("ko", "")][:20]
    return {"glossary": gl, "canon": ca, "messages": ms}


def maps_rows():
    """00-maps 행 전수 — 검색과 같은 형태 + sprite·group 부착."""
    c = ctx()
    p = KO / "00-maps.jsonl"
    cur_map = None
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        d = json.loads(line)
        if "map" in d and "n" in d:
            cur_map = d["map"]
            continue
        info = c["row"].get((cur_map, d.get("k", "")), {})
        yield {"file": p.name, "line": i, "map": cur_map,
               "es": d.get("k", ""), "v": d.get("v", ""),
               "sprite": info.get("sprite", "?"), "group": info.get("group", "?")}


def browse(by):
    from collections import Counter
    c = ctx()
    if by == "file":
        out = []
        for p in sorted(KO.glob("*.jsonl")):
            n = sum(1 for l in p.read_text(encoding="utf-8").splitlines()
                    if l and "\"v\"" in l)
            out.append({"key": p.name, "label": p.name, "count": n})
        return out
    cnt = Counter()
    for r in maps_rows():
        if by == "map":
            cnt[r["map"]] += 1
        elif by == "sprite":
            cnt[r["sprite"]] += 1
        elif by == "group":
            cnt[r["group"]] += 1
    if by == "map":
        return [{"key": str(k), "label": f"맵 {k} · {c['mapname'].get(k, '')}",
                 "count": n} for k, n in sorted(cnt.items(), key=lambda x: x[0] or 0)]
    return [{"key": str(k), "label": str(k), "count": n}
            for k, n in cnt.most_common()]


def listing(by, key):
    if by == "file":
        p = KO / key
        cur_map = None
        out = []
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            d = json.loads(line)
            if "map" in d and "n" in d:
                cur_map = d["map"]
                continue
            if "v" in d:
                out.append({"file": p.name, "line": i, "map": cur_map,
                            "es": d.get("k") or d.get("es") or "", "v": d["v"]})
            if len(out) >= 500:
                break
        return out
    out = []
    for r in maps_rows():
        val = str(r["map"]) if by == "map" else r.get(by, "?")
        if val == key:
            out.append(r)
        if len(out) >= 500:
            break
    return out


def load_notes():
    if not NOTES.exists():
        return []
    return [json.loads(l) for l in NOTES.read_text(encoding="utf-8").splitlines() if l]


def save_notes(notes):
    NOTES.write_text("\n".join(json.dumps(n, ensure_ascii=False) for n in notes) + "\n",
                     encoding="utf-8")


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n)) if n else {}

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            body = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif u.path == "/search":
            qs = urllib.parse.parse_qs(u.query)
            hits, trunc = search(qs.get("q", [""])[0], qs.get("file", [""])[0])
            self._json({"hits": hits, "truncated": trunc})
        elif u.path == "/notes":
            self._json({"notes": load_notes()})
        elif u.path == "/browse":
            by = urllib.parse.parse_qs(u.query).get("by", ["map"])[0]
            self._json({"groups": browse(by)})
        elif u.path == "/list":
            qs = urllib.parse.parse_qs(u.query)
            self._json({"hits": listing(qs.get("by", ["map"])[0],
                                        qs.get("key", [""])[0])})
        elif u.path == "/history":
            self._json({"ops": history()})
        elif u.path == "/ref":
            q = urllib.parse.parse_qs(u.query).get("q", [""])[0]
            self._json(ref_search(q))
        else:
            self._json({"err": "?"}, 404)

    def do_POST(self):
        if self.path == "/save":
            b = self._body()
            err = save_row(b["file"], int(b["line"]), b["v"])
            self._json({"ok": err is None, "err": err})
        elif self.path == "/note":
            b = self._body()
            notes = load_notes()
            notes.append({"query": b["query"], "note": b["note"]})
            save_notes(notes)
            self._json({"ok": True})
        elif self.path == "/done":
            b = self._body()
            notes = load_notes()
            notes[int(b["i"]) - 1]["done"] = bool(b.get("done", True))
            save_notes(notes)
            self._json({"ok": True})
        elif self.path == "/notedel":
            b = self._body()
            notes = load_notes()
            del notes[int(b["i"]) - 1]
            save_notes(notes)
            self._json({"ok": True})
        elif self.path == "/replan":
            b = self._body()
            hits, skipped, err = plan_replace(iter_rows(b.get("file", "")),
                                              b.get("find", ""), b.get("repl", ""),
                                              b.get("src", ""))
            self._json({"ok": err is None, "err": err,
                        "hits": hits, "skipped": skipped})
        elif self.path == "/replace":
            b = self._body()
            done, errs = apply_replace(b["items"], b.get("label", ""))
            self._json({"ok": not errs, "done": done, "errs": errs})
        elif self.path == "/revert":
            b = self._body()
            done, skipped, errs = revert_op(b["op"])
            self._json({"ok": not errs, "done": done, "skipped": skipped, "errs": errs})
        elif self.path == "/build":
            r = subprocess.run(["uv", "run", str(HERE / "build.py")],
                               capture_output=True, text=True)
            last = (r.stdout.strip().splitlines() or ["(출력 없음)"])[-1]
            self._json({"ok": r.returncode == 0,
                        "msg": last if r.returncode == 0 else r.stderr[-200:]})
        else:
            self._json({"err": "?"}, 404)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    print(f"http://localhost:{port}  (중지: Ctrl+C)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()


if __name__ == "__main__":
    main()
