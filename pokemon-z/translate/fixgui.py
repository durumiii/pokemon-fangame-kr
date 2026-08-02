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
<title>포켓몬Z 번역 수정</title>
<style>
 body{font-family:'Malgun Gothic',sans-serif;margin:20px auto;max-width:1100px;background:#1e1f24;color:#e8e8ea}
 input,textarea,button{font-family:inherit;font-size:14px;background:#2a2b31;color:#e8e8ea;border:1px solid #45464e;border-radius:6px}
 input[type=text]{padding:8px;width:480px} button{padding:7px 14px;cursor:pointer}
 button:hover{background:#3a3b44}
 .row{border:1px solid #34353c;border-radius:8px;padding:10px 14px;margin:10px 0;background:#26272d}
 .loc{color:#8a8b94;font-size:12px} .es{color:#a8c7fa;font-size:13px;margin:4px 0;white-space:pre-wrap}
 textarea{width:100%;box-sizing:border-box;min-height:52px;padding:6px;white-space:pre-wrap}
 .bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:6px}
 .note{background:#2d2a20;border-color:#5a5030}
 .ok{color:#7ed491} .warn{color:#f0b26b} #status{margin-left:8px;font-size:13px}
 .memoin{width:260px;padding:6px}
 h1{font-size:20px}
</style></head><body>
<h1>포켓몬Z 번역 즉석 수정</h1>
<div class=bar>
 <input type=text id=q placeholder="찾을 문구 (한국어 또는 스페인어 원문)" autofocus>
 <button onclick=search()>검색</button>
 <button onclick=build()>빌드(게임 반영)</button>
 <button onclick=notes()>메모 목록</button>
 <span id=status></span>
</div>
<div id=out></div>
<script>
const $=id=>document.getElementById(id);
$('q').addEventListener('keydown',e=>{if(e.key==='Enter')search()});
function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML}
async function search(){
 const q=$('q').value; if(!q)return;
 $('status').textContent='검색 중...';
 const r=await fetch('/search?q='+encodeURIComponent(q)); const js=await r.json();
 $('status').textContent=`${js.hits.length}행 매칭`+(js.truncated?' (앞 200행만 표시)':'');
 $('out').innerHTML=js.hits.map((h,i)=>`
  <div class=row id=row${i}>
   <div class=loc>${esc(h.file)}:${h.line}${h.map!==null?' · 맵'+h.map:''}</div>
   <div class=es>${esc(h.es)}</div>
   <textarea id=v${i}>${esc(h.v)}</textarea>
   <div class=bar>
    <button onclick=save(${i},'${h.file}',${h.line})>저장</button>
    <input class=memoin id=m${i} placeholder="메모 (나중에 배치 수정)">
    <button onclick=memo(${i})>메모 남기기</button>
    <span id=st${i}></span>
   </div>
  </div>`).join('');
}
async function save(i,file,line){
 const r=await fetch('/save',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({file,line,v:$('v'+i).value})});
 const js=await r.json();
 $('st'+i).innerHTML=js.ok?'<span class=ok>저장됨 — 빌드해야 게임에 반영</span>':'<span class=warn>'+esc(js.err)+'</span>';
}
async function memo(i){
 const note=$('m'+i).value||'(메모 없음)';
 const q=$('q').value;
 const v=$('v'+i).value;
 await fetch('/note',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({query:v.slice(0,60),note})});
 $('st'+i).innerHTML='<span class=ok>메모 기록됨</span>';
}
async function build(){
 $('status').textContent='빌드 중...';
 const r=await fetch('/build',{method:'POST'}); const js=await r.json();
 $('status').innerHTML=js.ok?'<span class=ok>'+esc(js.msg)+'</span>':'<span class=warn>'+esc(js.msg)+'</span>';
}
async function notes(){
 const r=await fetch('/notes'); const js=await r.json();
 $('status').textContent=`미결 메모 ${js.notes.filter(n=>!n.done).length}건`;
 $('out').innerHTML=js.notes.map((n,i)=>`
  <div class="row ${n.done?'':'note'}">
   [${i+1}] ${n.done?'✅':'📝'} 「${esc(n.query)}」 — ${esc(n.note)}
   ${n.done?'':`<button onclick=doneNote(${i+1})>완료</button>`}
  </div>`).join('')||'메모 없음';
}
async function doneNote(i){
 await fetch('/done',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({i})});
 notes();
}
</script></body></html>"""


def search(q):
    hits = []
    for p in sorted(KO.glob("*.jsonl")):
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
            if len(hits) >= 200:
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
            q = urllib.parse.parse_qs(u.query).get("q", [""])[0]
            hits, trunc = search(q)
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
