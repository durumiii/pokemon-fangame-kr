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

import html
import json
import subprocess
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).parent
KO = HERE / "ko"
NOTES = HERE / "fixnotes.jsonl"

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
 </div>
 <span id=dirty></span>
 <button onclick=build() id=buildbtn>빌드 → 게임 반영</button>
 <button class=ghost onclick=notes()>메모</button>
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
   <span class=chip>${esc(h.file)}:${h.line}</span>${h.map!==null?`<span class=chip>맵 ${h.map}</span>`:''}
   <div class=es>${esc(h.es)}</div>
   <textarea id=v${i} data-orig="${esc(h.v)}"
     onkeydown="if(event.ctrlKey&&event.key==='Enter')save(${i},'${h.file}',${h.line})">${esc(h.v)}</textarea>
   <div class=rowbar>
    <button class=primary onclick=save(${i},'${h.file}',${h.line})>저장</button>
    <input class=memoin id=m${i} placeholder="메모 — 나중에 배치로 손볼 내용">
    <button onclick=memo(${i})>메모</button>
    <span class=st id=st${i}></span>
   </div>
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
   ${n.done?'':`<button onclick=doneNote(${i+1})>완료 처리</button>`}
  </div>`).join('')||'<div class=empty>메모가 없습니다.</div>';
}
async function doneNote(i){
 await fetch('/done',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({i})});
 notes();
}
</script></body></html>"""


def search(q, only_file=""):
    hits = []
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
            es = d.get("k") or d.get("es") or ""
            if q in v or q in es:
                hits.append({"file": p.name, "line": i, "map": cur_map, "es": es, "v": v})
            if len(hits) >= 500:
                return hits, True
    return hits, False


def save_row(file, line, new_v):
    p = KO / file
    if not p.is_file() or p.parent != KO:
        return "잘못된 파일"
    lines = p.read_text(encoding="utf-8").splitlines()
    d = json.loads(lines[line - 1])
    if "v" not in d:
        return "이 행에는 v가 없음"
    d["v"] = new_v
    lines[line - 1] = json.dumps(d, ensure_ascii=False)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return None


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
            notes[int(b["i"]) - 1]["done"] = True
            save_notes(notes)
            self._json({"ok": True})
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
