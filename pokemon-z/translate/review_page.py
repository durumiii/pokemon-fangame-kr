# /// script
# requires-python = ">=3.12"
# ///
"""선별분 검수 페이지 — 선별에 걸린 행만 장면 단위로 묶어 한 장의 HTML로 낸다.

전량 실행에서 행마다 사람이 볼 수는 없다(docs/guides/retranslation.md 「산출 선별」).
선별 두 층(screen.py·screen_llm.py)이 걸러 낸 행만 여기 실린다. 걸린 행 하나를
그 장면 안에서 읽을 수 있어야 판정이 서므로, 장면의 모든 줄을 문맥으로 함께 싣는다.

    uv run translate/review_page.py <out-dir> [-o <파일.html>] [--title "..."]
    예: uv run translate/review_page.py translate/batch/page-out-pilot-fresh -o review.html

읽는 것: <out-dir>/*.jsonl(페이지 산출) · <out-dir>/screen*.jsonl(선별 결과, 파일마다
따로 층 이름을 붙인다). 판정은 브라우저에 담기고 하단 버튼으로 TSV로 나온다 —
`id<TAB>판정<TAB>화자<TAB>텍스트<TAB>메모`, 파일럿 판정표와 같은 꼴이다.
"""

import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import mapname  # noqa: E402

# 선별 파일 이름 → 페이지에 보일 층 이름
LAYERS = {"screen": "휴리스틱", "screen-llm": "모델"}


def layer_of(stem):
    return LAYERS.get(stem) or "모델(" + stem.removeprefix("screen-llm-") + ")"


def read_jsonl(p):
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def reasons(d):
    """id → [{"층","유형","근거"}]. screen.jsonl은 flags 목록, 모델 층은 유형/근거."""
    out = {}
    # 휴리스틱을 먼저 — 이름순으로는 screen-llm이 앞선다(「-」 < 「.」)
    for fp in sorted(d.glob("screen*.jsonl"), key=lambda p: (p.stem != "screen", p.stem)):
        lay = layer_of(fp.stem)
        for r in read_jsonl(fp):
            if r.get("flags"):                      # 휴리스틱 층
                for f in r["flags"]:
                    kind, _, why = f.partition(":")
                    out.setdefault(r["id"], []).append(
                        {"층": lay, "유형": kind, "근거": why})
            elif r.get("유형"):                      # 모델 층
                out.setdefault(r["id"], []).append(
                    {"층": lay, "유형": r["유형"], "근거": r.get("근거", "")})
    return out


def approved_ids(chunks=None):
    """승인 줄 — 유지자가 이미 판정을 끝낸 자리(`page-chunks.jsonl`의 `approved`).

    선별에 걸려도 다시 물으면 안 된다. 없으면 빈 집합이라 이 파일이 없는 산출도 돈다.
    """
    p = Path(chunks or HERE / "batch/page-chunks.jsonl")
    if not p.exists():
        return set()
    return {r["id"] for line in p.read_text(encoding="utf-8").splitlines() if line.strip()
            for r in json.loads(line).get("rows", []) if r.get("approved")}


def scene_of(fp, why, ok=frozenset(), all_rows=False):
    """페이지 파일 하나 → 장면 하나. 승인 줄을 뺀 뒤 걸린 행이 없으면 None.

    all_rows면 선별과 무관하게 **전 행**을 싣는다 — 파일럿처럼 사람이 전량을
    보는 자리용. 신판이 없는(그대로) 행은 현행을 신판 칸에 그대로 세운다.
    """
    rows = read_jsonl(fp)
    if all_rows:
        hit = [r for r in rows if r["id"] not in ok]
    else:
        hit = [r for r in rows if r["id"] in why and r.get("new") and r["id"] not in ok]
    if not hit:
        return None
    # 파일 이름은 p<맵>-<이벤트>-<페이지>(주연) 또는 t<맵>-<이벤트>(트레이너) 꼴이다
    m = re.match(r"^[A-Za-z]*(\d+)-(\d+)(?:-(\d+))?$", fp.stem)
    if not m:
        return None
    mid, ev, pg = m.group(1), m.group(2), m.group(3) or "0"
    return {
        "file": fp.stem, "map": int(mid), "event": ev, "page": pg,
        "name": mapname.ko(int(mid)) or f"맵 {int(mid)}",
        "cast": list(dict.fromkeys(r["who"] for r in rows)),
        "total": len(rows),
        # 걸렸지만 승인 줄이라 숨긴 행 수 — 장면 머리에 알린다
        "hidden": sum(1 for r in rows if r["id"] in why and r.get("new") and r["id"] in ok),
        "rows": [{"id": r["id"], "who": r["who"], "es": r["es"], "ko": r["old"],
                  "new": r.get("new") or r["old"], "why": why.get(r["id"], [])}
                 for r in hit],
        # 문맥은 장면 전부 — 현행 번역으로 읽어야 흐름이 잡힌다
        "flow": [{"id": r["id"], "who": r["who"], "ko": r["old"], "es": r["es"],
                  "hit": r["id"] in why} for r in rows],
    }


def applied_events(path=None):
    """반영이 끝나 승인 이벤트로 올라간 것 — 다시 묻지 않는다."""
    p = Path(path or HERE / "data/approved-events.jsonl")
    if not p.exists():
        return set()
    return {(json.loads(l)["map"], json.loads(l)["event"])
            for l in p.read_text(encoding="utf-8").splitlines() if l.strip()}


def applied_rows(path=None):
    """이미 정본에 반영돼 다시 볼 것 없는 행(`batch/applied-rows.jsonl`)."""
    p = Path(path or HERE / "batch/applied-rows.jsonl")
    if not p.exists():
        return set()
    return {json.loads(l)["id"] for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip()}


def collect(d, ok=None, done=None, all_rows=False):
    d = Path(d)
    why = reasons(d)
    ok = (approved_ids() | applied_rows()) if ok is None else ok
    done = applied_events() if done is None else done
    out = []
    for fp in sorted(d.glob("*.jsonl")):
        if fp.name.startswith("screen"):
            continue
        sc = scene_of(fp, why, ok, all_rows)
        if sc and (sc["map"], int(sc["event"])) not in done:
            out.append(sc)
    return out


HEAD = """<title>{title}</title>
<style>
/* 팔레트·타이포는 웹 수정 스튜디오(webapp/index.html)를 그대로 따른다 — 다크 단일 */
:root{{--bg:#16171b;--panel:#1e2026;--card:#23252c;--line:#32343d;--tx:#e6e7ea;--sub:#9a9ca6;
  --acc:#5b8def;--acc2:#3d68c4;--ok:#4cc38a;--warn:#e5a54b;--err:#e5644b;--es:#93b8f2;
  --gold:#e9b64a;--gold2:#c99427}}
*{{box-sizing:border-box;scrollbar-width:thin;scrollbar-color:#3a3d47 transparent}}
::-webkit-scrollbar{{width:9px;height:9px}}
::-webkit-scrollbar-thumb{{background:#3a3d47;border-radius:5px;border:2px solid var(--bg)}}
::-webkit-scrollbar-track{{background:transparent}}
body{{font-family:'Pretendard','Malgun Gothic',system-ui,sans-serif;margin:0;
  background:var(--bg);color:var(--tx);line-height:1.6}}
header{{position:sticky;top:0;z-index:10;background:var(--panel);border-bottom:1px solid var(--line);
  display:flex;align-items:center;gap:10px;padding:10px 22px;flex-wrap:wrap}}
.logo{{font-weight:700;font-size:15px;letter-spacing:.3px;white-space:nowrap}}
.logo b{{color:var(--gold)}}
.count{{color:var(--sub);font-size:12.5px;font-variant-numeric:tabular-nums}}
.count b{{color:var(--acc)}}
#ledger{{font-size:11.5px;color:var(--ok);background:rgba(76,195,138,.12);
  border:1px solid rgba(76,195,138,.35);border-radius:20px;padding:4px 12px;white-space:nowrap}}
#ledger.off{{color:var(--sub);background:var(--card);border-color:var(--line)}}
#err{{display:none;font-size:12.5px;color:var(--err);background:rgba(229,100,75,.12);
  border:1px solid rgba(229,100,75,.35);border-radius:20px;padding:4px 12px}}
.act{{margin-left:auto;display:flex;gap:8px}}
input,select,textarea,button{{font-family:inherit;font-size:13.5px;color:var(--tx);
  background:var(--card);border:1px solid var(--line);border-radius:8px}}
button{{display:inline-flex;align-items:center;gap:6px;padding:8px 13px;cursor:pointer;
  transition:background .12s;white-space:nowrap}}
button:hover{{background:#2c2e37}}
button.on{{background:var(--acc);border-color:var(--acc);color:#fff;font-weight:600}}
button.gold{{background:linear-gradient(180deg,var(--gold),var(--gold2));border-color:var(--gold2);
  color:#231a05;font-weight:700}}
button.gold:hover{{background:linear-gradient(180deg,#f2c35e,var(--gold))}}
button:focus-visible{{outline:none;border-color:var(--acc)}}
main{{max-width:1100px;margin:20px auto;padding:0 22px 90px}}
.intro{{color:var(--sub);font-size:13px;max-width:70ch;margin:6px 2px 20px}}
.intro b{{color:var(--tx)}}
section{{margin-bottom:30px}}
.scene{{border-bottom:1px solid var(--line);padding-bottom:7px;margin-bottom:12px;
  display:flex;gap:9px;align-items:baseline;flex-wrap:wrap}}
.scene h2{{font-size:14.5px;margin:0;font-weight:700}}
.scene .meta{{color:var(--sub);font-size:12.5px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;
  padding:13px 16px;margin-bottom:12px}}
.card.done{{border-color:rgba(76,195,138,.5)}}
section.folded .card,section.folded .expand{{display:none}}
section.folded{{margin-bottom:10px;opacity:.62}}
section.folded .scene{{border-bottom-style:dashed}}
.fin{{font-size:11.5px;color:var(--ok);background:rgba(76,195,138,.12);
  border:1px solid rgba(76,195,138,.35);border-radius:5px;padding:2px 8px}}
.donelbl{{display:inline-flex;align-items:center;gap:5px;font-size:12.5px;color:var(--sub);
  background:var(--card);border:1px solid var(--line);border-radius:8px;padding:6px 11px;cursor:pointer}}
.donelbl:has(:checked){{color:var(--ok);border-color:rgba(76,195,138,.5)}}
.hd{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}}
.chip{{display:inline-flex;align-items:center;gap:4px;font-size:11.5px;color:var(--sub);
  background:var(--panel);border:1px solid var(--line);border-radius:5px;padding:2px 8px}}
.who{{font-size:11.5px;font-weight:700;color:var(--acc);background:rgba(91,141,239,.13);
  border:1px solid rgba(91,141,239,.3);border-radius:5px;padding:2px 8px}}
.rid{{font-size:11.5px;color:var(--sub);font-variant-numeric:tabular-nums}}
.why{{margin:8px 0 2px;display:flex;flex-direction:column;gap:3px}}
.why div{{font-size:12.5px;color:var(--warn);background:rgba(229,165,75,.1);
  border-left:3px solid rgba(229,165,75,.55);border-radius:0 6px 6px 0;padding:4px 9px}}
.why b{{font-weight:700}}
.why .lay{{color:var(--sub);font-weight:400}}
.es{{color:var(--es);font-size:13px;line-height:1.55;margin:9px 0 7px;white-space:pre-wrap}}
.opt{{display:flex;gap:8px;align-items:flex-start;margin:4px 0}}
.tag{{font-size:11px;font-weight:700;border-radius:5px;padding:2px 7px;margin-top:2px;flex:none;
  border:1px solid var(--line);background:var(--panel);color:var(--sub)}}
.tag.new{{color:var(--ok);border-color:rgba(76,195,138,.4);background:rgba(76,195,138,.1)}}
.txt{{cursor:pointer;border-radius:6px;padding:2px 6px;margin:-2px -6px;font-size:13px;line-height:1.55}}
.txt:hover{{background:var(--panel)}}
.txt.sel{{background:rgba(76,195,138,.12);box-shadow:inset 0 0 0 1px rgba(76,195,138,.5)}}
ins{{background:rgba(76,195,138,.22);color:var(--ok);text-decoration:none;border-radius:3px;padding:0 2px}}
.tools{{display:flex;gap:8px;margin-top:9px;flex-wrap:wrap}}
.tools button{{font-size:12.5px;padding:6px 11px}}
.mine,.memo{{display:none;margin-top:8px}}
.mine.open,.memo.open{{display:block}}
textarea{{width:100%;min-height:48px;padding:8px 10px;line-height:1.6;resize:vertical;white-space:pre-wrap}}
.fill{{margin:6px 0 0;font-size:12px;color:var(--sub)}}
.fill button{{font-size:12px;padding:4px 9px}}
dialog{{border:1px solid var(--line);border-radius:12px;background:var(--panel);color:var(--tx);
  max-width:min(900px,92vw);width:900px;padding:0}}
dialog::backdrop{{background:rgba(0,0,0,.6)}}
.dh{{display:flex;gap:10px;align-items:baseline;padding:13px 18px;border-bottom:1px solid var(--line);
  position:sticky;top:0;background:var(--panel)}}
.dh h3{{margin:0;font-size:14px}}
.dh .meta{{color:var(--sub);font-size:12.5px}}
.dh button{{margin-left:auto}}
.db{{padding:14px 18px;max-height:68vh;overflow:auto}}
.line{{display:grid;grid-template-columns:7rem 1fr;gap:4px 10px;padding:6px 9px;border-radius:7px}}
.line.here{{background:rgba(91,141,239,.14)}}
.line .nm{{font-size:11.5px;color:var(--acc);text-align:right}}
.line .sp{{grid-column:2;color:var(--es);font-size:12.5px}}
</style>
<header><span class="logo">Z <b>선별분 검수</b></span>
  <span class="count" id="cnt"></span>
  <span id="ledger">{ledger}</span><span id="err"></span>
  <span class="act"><button id="fold">끝낸 이벤트 접기</button>
    <button id="dump">판정 TSV</button></span></header>
<main>
<p class="intro">선별 두 층에 걸린 행만 실려 있어요. 각 행에 <b>왜 걸렸는지</b>가 붙고,
「문맥」을 열면 그 장면 전체를 현행 번역으로 읽을 수 있어요. 장면 머리의
<b>이벤트 일괄 승인</b>은 그 장면의 걸린 행을 모두 새 번역으로 잡아요 — 승인은
이벤트 단위라서요.</p>
<div id="body"></div></main>
<dialog id="ctx"><div class="dh"><h3 id="ctxT"></h3><span class="meta" id="ctxM"></span>
  <button onclick="ctx.close()">닫기</button></div><div class="db" id="ctxB"></div></dialog>
<dialog id="out"><div class="dh"><h3>판정 TSV (예비 — 정본은 저장된 판정 기록)</h3>
  <span class="meta">id · 판정 · 화자 · 텍스트 · 메모</span>
  <button onclick="out.close()">닫기</button></div>
  <div class="db"><textarea id="txt" rows="18"></textarea>
  <p class="fill"><button onclick="txt.select();document.execCommand('copy')">전체 복사</button></p>
  </div></dialog>
"""

BODY = r"""<script>
const DATA = __DATA__;
const V = {}, M = {}, NOTE = {};
const esc = s => (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])).replace(/\n/g,'<br>');
function diff(a,b){
  let s=0; while(s<a.length&&s<b.length&&a[s]===b[s])s++;
  let e=0; while(e<a.length-s&&e<b.length-s&&a[a.length-1-e]===b[b.length-1-e])e++;
  return [a.slice(0,s),a.slice(s,a.length-e),b.slice(s,b.length-e),a.slice(a.length-e)];
}
const mark=(base,cand)=>{const[p,,m,sf]=diff(base,cand);return esc(p)+'<ins>'+esc(m)+'</ins>'+esc(sf);};
const SET = [];   // 장면별 일괄 적용 훅

function render(){
  const body=document.getElementById('body');
  for (const sc of DATA){
    const sec=document.createElement('section');
    sec.innerHTML=`<div class="scene"><h2>${esc(sc.name)}</h2>
      <span class="meta">맵 ${sc.map} · 이벤트 ${esc(sc.event)}-${esc(sc.page)} ·
        ${esc(sc.cast.join(' · '))} · 장면 ${sc.total}행 중 <b>${sc.rows.length}행 선별</b></span>
      <span class="act" style="margin-left:auto"><button data-all="1">이벤트 일괄 승인</button>
        <button data-flow="1">장면 흐름</button></span></div>`;
    const setters=[];
    for (const r of sc.rows){
      const card=document.createElement('div'); card.className='card';
      card.innerHTML=`<div class="hd"><span class="who">${esc(r.who)}</span>
          <span class="rid">${r.id}</span>
          <button class="ctxbtn" style="margin-left:auto">문맥</button></div>
        <div class="why">${r.why.map(w=>`<div><b>${esc(w['유형'])}</b>
          <span class="lay">· ${esc(w['층'])}</span>${w['근거']?' — '+esc(w['근거']):''}</div>`).join('')}</div>
        <div class="es">${esc(r.es)}</div>
        <div class="opt"><span class="tag cur">현행</span><span class="txt" data-v="cur">${esc(r.ko)}</span></div>
        <div class="opt"><span class="tag new">새</span><span class="txt" data-v="new">${mark(r.ko,r.new)}</span></div>
        <div class="tools"><button data-v="own">직접</button><button data-v="hold">보류</button>
          <button data-memo="1">메모</button></div>
        <div class="mine"><textarea rows="2" placeholder="고친 문장을 여기에"></textarea>
          <p class="fill">넣기: <button type="button" data-fill="cur">현행</button>
            <button type="button" data-fill="new">새 번역</button></p></div>
        <div class="memo"><textarea rows="2" placeholder="메모 — 무엇을 골랐든 따로 남아요"></textarea></div>`;
      const mine=card.querySelector('.mine'), ta=mine.querySelector('textarea');
      const memo=card.querySelector('.memo'), na=memo.querySelector('textarea');
      const paint=()=>{
        card.querySelectorAll('.txt').forEach(x=>x.classList.toggle('sel',x.dataset.v===V[r.id]));
        card.querySelectorAll('.tools button[data-v]').forEach(x=>x.classList.toggle('on',x.dataset.v===V[r.id]));
        mine.classList.toggle('open',V[r.id]==='own');
        card.classList.toggle('done',!!V[r.id]&&!(V[r.id]==='own'&&!ta.value.trim()));
      };
      const set=(v,force)=>{V[r.id]=(!force&&V[r.id]===v)?undefined:v; paint(); count();};
      setters.push(v=>set(v,true));
      card.querySelectorAll('.txt').forEach(el=>el.onclick=()=>set(el.dataset.v));
      card.querySelectorAll('.tools button[data-v]').forEach(el=>el.onclick=()=>set(el.dataset.v));
      card.querySelector('[data-memo]').onclick=e=>{
        memo.classList.toggle('open'); e.target.classList.toggle('on',memo.classList.contains('open'));
        if(memo.classList.contains('open')) na.focus();
      };
      ta.oninput=()=>{M[r.id]=ta.value; paint(); count();};
      na.oninput=()=>{NOTE[r.id]=na.value; count();};
      mine.querySelectorAll('[data-fill]').forEach(b=>b.onclick=()=>{
        ta.value=b.dataset.fill==='cur'?r.ko:r.new;
        M[r.id]=ta.value; ta.focus(); paint(); count();
      });
      sec.appendChild(card);
    }
    sec.querySelectorAll('.ctxbtn').forEach((b,i)=>b.onclick=()=>openFlow(sc, sc.rows[i].id));
    sec.querySelector('[data-flow]').onclick=()=>openFlow(sc, null);
    sec.querySelector('[data-all]').onclick=()=>setters.forEach(f=>f('new'));
    SET.push(setters);
    body.appendChild(sec);
  }
}
function openFlow(sc, id){
  document.getElementById('ctxT').textContent=sc.name;
  document.getElementById('ctxM').textContent=
    `맵 ${sc.map} · 이벤트 ${sc.event}-${sc.page} · ${sc.total}행 — 현행 번역으로 읽는 장면`;
  document.getElementById('ctxB').innerHTML=sc.flow.map(r=>
    `<div class="line${r.id===id?' here':''}" id="fl-${r.id}">
       <span class="nm">${esc(r.who)}${r.hit?' ●':''}</span><span>${esc(r.ko)}</span>
       <span class="sp">${esc(r.es)}</span></div>`).join('');
  document.getElementById('ctx').showModal();
  if(id){const el=document.getElementById('fl-'+id); if(el) el.scrollIntoView({block:'center'});}
}
function count(){
  const tot=DATA.reduce((n,s)=>n+s.rows.length,0);
  const t={cur:0,new:0,own:0,hold:0};
  Object.values(V).forEach(v=>{if(v)t[v]++;});
  const notes=Object.values(NOTE).filter(x=>x&&x.trim()).length;
  document.getElementById('cnt').innerHTML=
    `<b>${Object.values(V).filter(Boolean).length}</b> / ${tot} 판정 · 새 번역 ${t.new} · 현행 ${t.cur} · 직접 ${t.own} · 보류 ${t.hold} · 메모 ${notes}`;
}
document.getElementById('dump').onclick=()=>{
  const L=[];
  const label={cur:'현행',new:'B새번역',own:'직접',hold:'보류'};
  for(const sc of DATA) for(const r of sc.rows){
    const v=V[r.id], note=(NOTE[r.id]||'').trim();
    if(!v&&!note) continue;
    const txt=v==='new'?r.new:v==='own'?(M[r.id]||''):v==='cur'?r.ko:'';
    L.push([r.id,v?label[v]:'메모만',r.who,(txt||'').replace(/\n/g,'\\n'),note.replace(/\n/g,' ')].join('\t'));
  }
  document.getElementById('txt').value=L.length?L.join('\n'):'아직 고르거나 적은 것이 없어요.';
  document.getElementById('out').showModal();
};
document.getElementById('ledger').className='off';   // 정적판은 저장하지 않는다
render(); count();
</script>
"""


def build(scenes, title, ledger="정적 페이지 — 판정은 TSV로 복사해 가세요"):
    return (HEAD.format(title=html.escape(title), ledger=html.escape(ledger))
            + BODY.replace("__DATA__", json.dumps(scenes, ensure_ascii=False)))


def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        (d / "p024-43-0.jsonl").write_text(
            json.dumps({"id": "24:43:0:0", "who": "기니아", "es": "Hola",
                        "old": "안녕", "new": "안녕하세요"}, ensure_ascii=False) + "\n"
            + json.dumps({"id": "24:43:0:1", "who": "기니아", "es": "Adios",
                          "old": "잘 가", "new": "잘 가요"}, ensure_ascii=False) + "\n",
            encoding="utf-8")
        (d / "screen.jsonl").write_text(
            json.dumps({"id": "24:43:0:0", "who": "기니아", "flags": ["존칭 변경:님"]},
                       ensure_ascii=False) + "\n", encoding="utf-8")
        (d / "screen-llm.jsonl").write_text(
            json.dumps({"id": "24:43:0:0", "유형": "제안-호칭", "근거": "경칭 근거 없음"},
                       ensure_ascii=False) + "\n", encoding="utf-8")
        sc = collect(d, ok=set(), done=set())
        assert len(sc) == 1, sc
        assert [r["id"] for r in sc[0]["rows"]] == ["24:43:0:0"]   # 걸린 행만
        assert sc[0]["hidden"] == 0
        # 승인 줄은 걸려도 안 보인다 — 그 장면에 남는 게 없으면 장면째 빠진다
        assert collect(d, ok={"24:43:0:0"}, done=set()) == []
        # 반영이 끝난 이벤트는 장면째 빠진다
        assert collect(d, ok=set(), done={(24, 43)}) == []
        chunks = d / "chunks.jsonl"
        chunks.write_text(json.dumps(
            {"rows": [{"id": "24:43:0:0", "approved": True}, {"id": "24:43:0:1"}]},
            ensure_ascii=False) + "\n", encoding="utf-8")
        assert approved_ids(chunks) == {"24:43:0:0"}
        assert sc[0]["total"] == 2 and len(sc[0]["flow"]) == 2     # 문맥은 장면 전부
        assert [w["층"] for w in sc[0]["rows"][0]["why"]] == ["휴리스틱", "모델"]
        h = build(sc, "t")
        assert "__DATA__" not in h and "24:43:0:1" in h and h.count("<script") == 1
    print("selftest ok")


def main(argv):
    a = list(argv)
    out = Path(a.pop(a.index("-o") + 1)) if "-o" in a else None
    if "-o" in a:
        a.remove("-o")
    title = a.pop(a.index("--title") + 1) if "--title" in a else None
    if "--title" in a:
        a.remove("--title")
    d = Path(a[0])
    scenes = collect(d)
    out = out or d / "review.html"
    out.write_text(build(scenes, title or f"선별분 검수 — {d.name}"), encoding="utf-8")
    rows = sum(len(s["rows"]) for s in scenes)
    print(f"{d.name}: 장면 {len(scenes)} · 선별 {rows}행 → {out} ({out.stat().st_size:,} bytes)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    elif sys.argv[1] == "selftest":
        selftest()
    else:
        main(sys.argv[1:])
