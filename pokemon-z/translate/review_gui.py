# /// script
# requires-python = ">=3.12"
# ///
"""선별분 검수 스튜디오 — 로컬 서버로 띄우고 판정을 그때그때 저장한다.

정적 HTML은 판정이 브라우저에만 남아 새로고침 한 번에 날아간다. 여기서는 데이터만
주고받고, 판정은 누를 때마다 서버가 jsonl에 덧붙인다 — 창을 닫았다 열어도 이어서 본다.

    uv run translate/review_gui.py --out translate/batch/page-out-pilot-fresh [--port 8788]

  GET  /         검수 UI
  GET  /data     {"scenes":[...], "verdicts":{id:{판정,텍스트,메모}}}
  GET  /req      ?cid=<장면 파일 이름> → 그 장면이 모델에 보낸 요청 원문
  POST /verdict  {"id","판정","텍스트","메모"} → 덧붙임 저장, 같은 id는 마지막 것이 이긴다

판정 기록은 `translate/batch/verdicts-<out이름>.jsonl`. 화면 오른쪽 위 「판정 TSV」는
예비 내보내기고, 그 기록이 정본이다.

장면·선별 사유를 모으는 일은 `review_page.py`(정적 생성판)와 같은 코드를 쓴다.
"""

import json
import re
import sys
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from review_page import HEAD, approved_ids, collect  # noqa: E402

BODY = r"""<style>.tag.alt{background:#7d5bd6;color:#fff}
.rqh{font-size:11.5px;color:var(--sub);margin:14px 0 5px;font-weight:700}
.rqh:first-child{margin-top:0}
.rq{font-size:12.5px;line-height:1.5;background:var(--card);border:1px solid var(--line);
  border-radius:8px;padding:9px 12px}</style>
<script>
let DATA = [], V = {}, M = {}, NOTE = {}, STAT = null, BRIEF = null;
const HUMAN = new Set();   // 사람이 손댄 자리 — 기계 수선 채움과 가른다
const esc = s => (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])).replace(/\n/g,'<br>');
function diff(a,b){
  let s=0; while(s<a.length&&s<b.length&&a[s]===b[s])s++;
  let e=0; while(e<a.length-s&&e<b.length-s&&a[a.length-1-e]===b[b.length-1-e])e++;
  return [a.slice(0,s),a.slice(s,a.length-e),b.slice(s,b.length-e),a.slice(a.length-e)];
}
const mark=(base,cand)=>{const[p,,m,sf]=diff(base,cand);return esc(p)+'<ins>'+esc(m)+'</ins>'+esc(sf);};
const LABEL={cur:'현행',new:'B새번역',own:'직접',hold:'보류'};
const ROW={};                       // id → 원자료 (저장할 때 텍스트를 뽑는다)
const timer={};
function post(rec){                 // 판정 기록에 한 줄 — 이게 정본이다
  return fetch('/verdict',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify(rec)})
    .then(x=>{if(!x.ok) flag('저장 실패 — ' + (rec.id||rec.event));})
    .catch(()=>flag('서버 끊김 — ' + (rec.id||rec.event)));
}
function save(id){                  // 판정 하나를 서버에 넘긴다
  const v=V[id], r=ROW[id];
  const txt=v==='new'?r.new:v==='own'?(M[id]||''):v==='cur'?r.ko:'';
  post({id, 판정:v?LABEL[v]:'', 텍스트:txt, 메모:(NOTE[id]||'')});
}
function later(id){clearTimeout(timer[id]); timer[id]=setTimeout(()=>save(id),600);}
function flag(msg){const e=document.getElementById('err'); e.textContent=msg; e.style.display='';}

// 카드 하나 — 선별 행과 「이벤트 전체 보기」로 펼친 행이 같은 것을 쓴다
function makeCard(r, sc){
      ROW[r.id]=r;
      const card=document.createElement('div'); card.className='card';
      card.innerHTML=`<div class="hd"><span class="who">${esc(r.who)}</span>
          <span class="rid">${r.id}</span>
          ${r.approved?'<span class="chip" title="유지자가 이미 판정한 줄">승인 줄</span>':''}
          ${r.covers?`<span class="chip" title="같은 화자의 같은 원문이 접힌 자리 — 판정이 맵 ${r.covers.join(', ')}에 함께 반영돼요">복제 ${r.covers.length}맵 함께</span>`:''}
          ${r.persona?`<span class="chip" title="말투 등재 — 페르소나표·말투 대장">${esc(r.persona)}</span>`:''}
          ${r.layer?`<span class="chip" title="층 — 정본 인물(PS) · 이름표 없는 인물(PC) · 지문·시스템(N)">층 ${esc(r.layer)}</span>`:''}
          ${r.dups?`<span class="chip" title="같은 원문이 선 다른 자리 — 값이 갈릴 수 있어요">다른 자리 ${r.dups}</span>`:''}
          ${(r.marks||[]).map(m=>`<span class="chip" title="사람 손이 지나간 자리">⚑ ${esc(m)}</span>`).join('')}
          <button class="ctxbtn" style="margin-left:auto">문맥</button></div>
        <div class="why">${(r.why||[]).map(w=>`<div><b>${esc(w['유형'])}</b>
          <span class="lay">· ${esc(w['층'])}</span>${w['근거']?' — '+esc(w['근거']):''}</div>`).join('')}</div>
        <div class="es">${esc(r.es)}</div>
        <div class="opt"><span class="tag cur">현행</span><span class="txt" data-v="cur">${esc(r.ko)}</span></div>
        <div class="opt"><span class="tag new">새</span><span class="txt" data-v="new">${mark(r.ko,r.new)}</span></div>
        ${r.alt?`<div class="opt"><span class="tag alt">minimal</span><span class="txt" data-alt="1" title="누르면 「직접」 판정에 이 문안이 채워져요">${mark(r.ko,r.alt)}</span></div>`:''}
        <div class="tools"><button data-v="own">직접</button><button data-v="hold">보류</button>
          <button data-memo="1">메모</button></div>
        <div class="mine"><textarea rows="2" placeholder="고친 문장을 여기에"></textarea>
          <p class="fill">넣기: <button type="button" data-fill="cur">현행</button>
            <button type="button" data-fill="new">새 번역</button>${
            r.alt?` <button type="button" data-fill="alt">minimal</button>`:''}</p></div>
        <div class="memo"><textarea rows="2" placeholder="메모 — 무엇을 골랐든 따로 남아요"></textarea></div>`;
      const mine=card.querySelector('.mine'), ta=mine.querySelector('textarea');
      const memo=card.querySelector('.memo'), na=memo.querySelector('textarea');
      ta.value=M[r.id]||''; na.value=NOTE[r.id]||'';
      if(na.value) memo.classList.add('open');
      const paint=()=>{
        // V가 비면(미판정) 아무 줄도 고르지 않는다 — undefined===undefined 매칭이
        // 값 없는 줄(alt)을 기본 선택처럼 칠했던 사고(2026-08-12)
        card.querySelectorAll('.txt[data-v]').forEach(x=>x.classList.toggle('sel',!!V[r.id]&&x.dataset.v===V[r.id]));
        card.querySelectorAll('.tools button[data-v]').forEach(x=>x.classList.toggle('on',x.dataset.v===V[r.id]));
        mine.classList.toggle('open',V[r.id]==='own');
        card.classList.toggle('done',!!V[r.id]&&!(V[r.id]==='own'&&!ta.value.trim()));
      };
      const set=(v,force)=>{V[r.id]=(!force&&V[r.id]===v)?undefined:v; paint(); count(); refold(); save(r.id);};
      card.querySelector('.ctxbtn').onclick=()=>openFlow(sc, r.id);
      card.querySelectorAll('.txt[data-v]').forEach(el=>el.onclick=()=>set(el.dataset.v));
      const altEl=card.querySelector('.txt[data-alt]');
      if(altEl) altEl.onclick=()=>{           // minimal 채택 = 「직접」 판정 + 그 문안
        ta.value=r.alt; M[r.id]=ta.value; set('own',true);
      };
      card.querySelectorAll('.tools button[data-v]').forEach(el=>el.onclick=()=>set(el.dataset.v));
      card.querySelector('[data-memo]').onclick=e=>{
        memo.classList.toggle('open'); e.target.classList.toggle('on',memo.classList.contains('open'));
        if(memo.classList.contains('open')) na.focus();
      };
      ta.oninput=()=>{M[r.id]=ta.value; paint(); count(); later(r.id);};
      na.oninput=()=>{NOTE[r.id]=na.value; count(); later(r.id);};
      mine.querySelectorAll('[data-fill]').forEach(b=>b.onclick=()=>{
        ta.value=b.dataset.fill==='cur'?r.ko:b.dataset.fill==='alt'?r.alt:r.new;
        M[r.id]=ta.value; ta.focus(); paint(); count(); later(r.id);
      });
      paint();
      return {card, set:v=>set(v,true)};
}

function render(){
  const body=document.getElementById('body');
  body.innerHTML='';
  if(BRIEF){
    const b=document.createElement('section');
    b.innerHTML=`<div class="scene"><h2>${esc(BRIEF.title||'판정 요청')}</h2>
      <span class="meta">자리 ${BRIEF.hits||0} · 장면 ${BRIEF.scenes||0}${
        BRIEF.by?` · ${esc(BRIEF.by)}`:''}</span></div>
      ${BRIEF.note?`<div class="card"><div class="es" style="white-space:pre-wrap">${esc(BRIEF.note)}</div></div>`:''}`;
    for(const q of (BRIEF.asks||[])){
      const id='bucket:'+q.id;
      const c=document.createElement('div'); c.className='card';
      c.innerHTML=`<div class="hd"><span class="who">${esc(q.title||q.id)}</span>
          <span class="rid">${id}</span>
          ${q.rows?`<span class="chip">자리 ${q.rows}</span>`:''}
          <span class="chip verdict" style="margin-left:auto"></span></div>
        ${q.ask?`<div class="opt"><span class="tag cur">정해 달라는 것</span>
          <span class="txt" style="white-space:pre-wrap">${esc(q.ask)}</span></div>`:''}
        ${q.split?`<div class="opt"><span class="tag alt">갈림</span>
          <span class="txt" style="white-space:pre-wrap">${esc(q.split)}</span></div>`:''}
        ${q.rec?`<div class="opt"><span class="tag new">추천</span>
          <span class="txt" style="white-space:pre-wrap">${esc(q.rec)}</span></div>`:''}
        ${(q.keep||[]).length?`<div class="opt"><span class="tag cur">손대지 않는 자리</span>
          <span class="txt" style="white-space:pre-wrap">${esc(q.keep.join('\n'))}</span></div>`:''}
        <div class="tools"><button data-b="승인">승인</button>
          <button data-b="기각">기각</button><button data-b="보류">보류</button>
          ${q.rows&&q.rows.length?`<button data-only="1">이 건의 자리만 (${q.rows.length})</button>`:''}
          <button data-bmemo="1">메모</button></div>
        <div class="mine open"><textarea rows="2" placeholder="답 — 등재할 한 줄이나 고른 갈래를 여기에"></textarea></div>
        <div class="memo"><textarea rows="2" placeholder="판정 메모 — 왜 그렇게 정했나"></textarea></div>`;
      const chip=c.querySelector('.verdict'), memo=c.querySelector('.memo');
      const ta=memo.querySelector('textarea');
      const ans=c.querySelector('.mine textarea');
      if(ans){ans.value=M[id]||'';
        ans.oninput=()=>{M[id]=ans.value; clearTimeout(timer[id]);
          timer[id]=setTimeout(()=>post({id, 판정:(V[id]||''), 텍스트:ans.value,
                                         메모:(NOTE[id]||'')}), 600);};}
      const only=c.querySelector('[data-only]');
      if(only) only.onclick=()=>{
        const want=new Set(q.rows);
        const kept=DATA.map(sc=>({...sc, rows:sc.rows.filter(r=>want.has(r.id))}))
                       .filter(sc=>sc.rows.length);
        const all=DATA; DATA=kept; render(); count(); DATA=all;
      };
      const paint=()=>{chip.textContent=V[id]?('판정 '+V[id]):''};
      if(NOTE[id]){ta.value=NOTE[id]; memo.classList.add('open');}
      paint();
      c.querySelectorAll('[data-b]').forEach(btn=>btn.onclick=()=>{
        V[id]=btn.dataset.b; paint();
        post({id, 판정:btn.dataset.b, 텍스트:(M[id]||''), 메모:(NOTE[id]||'')});
      });
      c.querySelector('[data-bmemo]').onclick=()=>memo.classList.toggle('open');
      ta.oninput=()=>{NOTE[id]=ta.value;
        clearTimeout(timer[id]); timer[id]=setTimeout(()=>
          post({id, 판정:(V[id]||''), 텍스트:'', 메모:ta.value}), 600);};
      b.appendChild(c);
    }
    body.appendChild(b);
  }
  if(!DATA.length){
    const e=document.createElement('section');
    e.innerHTML=`<div class="scene"><h2>선별된 자리가 없어요</h2></div>
      <div class="card"><div class="es">승인 이벤트·승인 줄로 숨긴 자리가 있으면
      <b>--no-skip</b>으로 다시 띄우세요. 산출 폴더에 제안이 없으면 재료 도구의
      <b>--proposals</b>부터 확인하고요.</div></div>`;
    body.appendChild(e); return;
  }
  for (const sc of DATA){
    const sec=document.createElement('section');
    sec.dataset.ev=sc.file;
    sec.innerHTML=`<div class="scene"><h2>${esc(sc.name)}</h2>
      <span class="fin" style="display:none">완료</span>
      <span class="meta">맵 ${sc.map} · 이벤트 ${esc(sc.event)}-${esc(sc.page)} ·
        ${esc(sc.cast.join(' · '))} · ${sc.rows.length>=sc.total
          ?`<b>전 행 ${sc.total}행</b>`
          :`장면 ${sc.total}행 중 <b>${sc.rows.length}행 선별</b>`}${
        sc.hidden?` · 승인 줄 ${sc.hidden}행 숨김`:''}</span>
      <span class="act" style="margin-left:auto">
        <label class="donelbl"><input type="checkbox" class="donebox"> 완료</label>
        <button data-ask="1">조사 요청</button>
        ${sc.rows.length>=sc.total?'':'<button data-open="1">이벤트 전체 보기</button>'}
        <button data-all="1">이벤트 일괄 승인</button>
        <button data-flow="1">장면 흐름</button>
        ${sc.req?'<button data-req="1">프롬프트 전문</button>':''}</span></div>`;
    const setters=[];
    for (const r of sc.rows){
      const c=makeCard(r, sc); setters.push(c.set); sec.appendChild(c.card);
    }
    sec.querySelector('[data-flow]').onclick=()=>openFlow(sc, null);
    const rq=sec.querySelector('[data-req]'); if(rq) rq.onclick=()=>openReq(sc);
    sec.querySelector('[data-all]').onclick=()=>{
      setters.forEach(f=>f('new'));
      // 승인은 이벤트 단위 — 행 판정과 별도로 판정 기록에 한 줄 남긴다
      post({event:`${sc.map}:${sc.event}-${sc.page}`, 판정:'승인', 텍스트:'',
            메모:`${sc.name} 이벤트 ${sc.event}-${sc.page} — ${sc.rows.length}행 일괄`});
    };
    sec.querySelector('[data-ask]').onclick=e=>{
      const q=prompt(`「${sc.name}」에 무엇을 조사할까요?`, '');
      if(q===null) return;
      fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({event:`${sc.map}:${sc.event}`, 장면:sc.name, 물음:q})})
        .then(x=>{ e.target.classList.add('on'); e.target.textContent='조사 요청함'; })
        .catch(()=>flag('요청을 못 보냈어요'));
    };
    sec.querySelector('.donebox').onchange=e=>{
      const key=`${sc.map}:${sc.event}-${sc.page}`;
      if(e.target.checked){ DONE.add(key);
        post({event:key, 판정:'완료', 텍스트:'',
              메모:`${sc.name} 이벤트 ${sc.event}-${sc.page} — 유지자 완료 표시`});
      } else { DONE.delete(key);
        post({event:key, 판정:'', 텍스트:'', 메모:'완료 표시 해제'}); }
      refold();
    };
    const ob=sec.querySelector('[data-open]'); if(ob) ob.onclick=e=>openEvent(sc, sec, e.target);
    body.appendChild(sec);
  }
}

// 이벤트의 안 걸린 행까지 그 자리에 펼친다 — 걸린 행은 이미 위에 있으니 뺀다
function openEvent(sc, sec, btn){
  if(sec.querySelector('.expand')){ sec.querySelector('.expand').remove();
    btn.classList.remove('on'); return; }
  btn.classList.add('on'); btn.disabled=true;
  fetch(`/event?map=${sc.map}&event=${encodeURIComponent(sc.event)}`)
    .then(r=>r.json()).then(d=>{
      const shown=new Set(sc.rows.map(r=>r.id));
      const box=document.createElement('div'); box.className='expand';
      const rest=d.rows.filter(r=>!shown.has(r.id));
      box.innerHTML=`<p class="intro" style="margin:2px 2px 10px">이벤트 전체 ${d.rows.length}행 —
        선별 ${sc.rows.length}행은 위에 있고, 나머지 <b>${rest.length}행</b>이에요.</p>`;
      for(const r of rest) box.appendChild(makeCard(r, sc).card);
      sec.appendChild(box); btn.disabled=false; count();
    }).catch(()=>{flag('이벤트를 못 읽었어요'); btn.disabled=false;});
}
// 이 장면이 모델에 실제로 넘어간 요청 원문 — 문맥 모달을 그대로 빌려 쓴다
function openReq(sc){
  fetch('/req?cid='+encodeURIComponent(sc.file)).then(r=>r.json()).then(d=>{
    if(d.err) return flag('프롬프트 원문이 없어요 — ' + sc.file);
    document.getElementById('ctxT').textContent=`${sc.name} — 모델이 받은 그대로`;
    document.getElementById('ctxM').textContent=
      `맵 ${sc.map} · 이벤트 ${sc.event}-${sc.page} · ${sc.file}.req.json`;
    document.getElementById('ctxB').innerHTML=
      `<div class="rqh">시스템 프롬프트</div><div class="rq">${esc(d.system)}</div>
       <div class="rqh">보낸 대사 묶음${d.n?` (${d.n}행)`:''}</div><div class="rq">${esc(d.user)}</div>`;
    document.getElementById('ctx').showModal();
  }).catch(()=>flag('프롬프트를 못 읽었어요 — ' + sc.file));
}
function openFlow(sc, id){
  document.getElementById('ctxT').textContent=sc.name;
  document.getElementById('ctxM').textContent=
    `맵 ${sc.map} · 이벤트 ${sc.event}-${sc.page} · ${sc.total}행 — 장면 흐름 (고쳐진 자리는 지움·새김 표시)`;
  document.getElementById('ctxB').innerHTML=sc.flow.map(r=>
    `<div class="line${r.id===id?' here':''}" id="fl-${r.id}">
       <span class="nm">${esc(r.who)}${r.hit?' ●':''}</span><span>${r.new?mark(r.ko,r.new):esc(r.ko)}</span>
       <span class="sp">${esc(r.es)}</span></div>`).join('');
  document.getElementById('ctx').showModal();
  if(id){const el=document.getElementById('fl-'+id); if(el) el.scrollIntoView({block:'center'});}
}
let DONE = new Set();               // 「완료」 체크한 이벤트 — 판정 기록에도 남는다
// 접는 기준은 「내가 본 데까지」다. 안 고른 행은 새 번역 채택이라 판정이 안 남으므로
// 「모두 판정됨」으로는 읽을 수 없다 — 사람이 손댄 마지막 장면까지를 지나온 것으로 본다.
function frontier(){
  let last=-1;
  DATA.forEach((sc,i)=>{ if(sc.rows.some(r=>HUMAN.has(r.id))) last=i; });
  return last;
}
function refold(){
  const on=document.getElementById('fold').classList.contains('on');
  const fr=frontier();
  document.querySelectorAll('section[data-ev]').forEach((sec,i)=>{
    const sc=DATA[i];
    const done=DONE.has(`${sc.map}:${sc.event}-${sc.page}`);
    sec.classList.toggle('folded', done || (on && i<=fr));
    const b=sec.querySelector('.fin'); if(b) b.style.display=done?'':'none';
    const c=sec.querySelector('.donebox'); if(c) c.checked=done;
  });
}
function count(){
  const tot=DATA.reduce((n,s)=>n+s.rows.length,0);
  const t={cur:0,new:0,own:0,hold:0};
  Object.values(V).forEach(v=>{if(v)t[v]++;});
  const notes=Object.values(NOTE).filter(x=>x&&x.trim()).length;
  const st=STAT||{}, done=st['끝남']||0, all=st['물을것']||tot;
  const pct=all?Math.round(done*100/all):0;
  document.getElementById('cnt').innerHTML=
    `끝마침 <b>${done}</b> / ${all}행 (${pct}%) · 남은 ${st['남음']??tot}행 · ` +
    `이 화면 판정 ${Object.values(V).filter(Boolean).length} ` +
    `(현행 ${t.cur} · 직접 ${t.own} · 보류 ${t.hold} · 새번역 ${t.new}) · 메모 ${notes}`;
}
document.getElementById('fold').onclick=e=>{
  e.target.classList.toggle('on');
  e.target.textContent=e.target.classList.contains('on')?'끝낸 이벤트 펴기':'끝낸 이벤트 접기';
  refold();
};
document.getElementById('dump').onclick=()=>{
  const L=[];
  for(const sc of DATA) for(const r of sc.rows){
    const v=V[r.id], note=(NOTE[r.id]||'').trim();
    if(!v&&!note) continue;
    const txt=v==='new'?r.new:v==='own'?(M[r.id]||''):v==='cur'?r.ko:'';
    L.push([r.id,v?LABEL[v]:'메모만',r.who,(txt||'').replace(/\n/g,'\\n'),note.replace(/\n/g,' ')].join('\t'));
  }
  document.getElementById('txt').value=L.length?L.join('\n'):'아직 고르거나 적은 것이 없어요.';
  document.getElementById('out').showModal();
};
const BACK={};
Object.entries(LABEL).forEach(([k,v])=>BACK[v]=k);
fetch('/data').then(r=>r.json()).then(d=>{
  DATA=d.scenes;
  for(const [id,x] of Object.entries(d.verdicts||{})){
    if(x['판정']) V[id]=id.startsWith('bucket:')?x['판정']:BACK[x['판정']];
    if(x['ts']!=='auto') HUMAN.add(id);
    if(x['판정']==='직접'||id.startsWith('bucket:')) M[id]=x['텍스트']||'';
    if(x['메모']) NOTE[id]=x['메모'];
  }
  STAT=d.stat||null; BRIEF=d.brief||null;
  for(const [k,x] of Object.entries(d.verdicts||{}))     // event:<맵>:<이벤트> 열쇠
    if(k.startsWith('event:') && x['판정']==='완료') DONE.add(k.slice(6));
  render(); count(); refold();
}).catch(()=>flag('데이터를 못 읽었어요 — 서버가 떠 있나요?'));
</script>
"""


def event_rows(out_dir, mapno, event):
    """한 이벤트의 모든 페이지, 모든 행 — 선별에 걸렸든 아니든.

    이상한 게 많이 나온 장면은 걸린 행만 봐선 판정이 안 선다. 페이지가 여럿으로
    갈린 이벤트도 있어 `p{맵:03d}-{이벤트}-*`를 다 긁는다.
    """
    if not str(mapno).isdigit() or not event.isdigit():   # 경로 조작 차단
        return []
    ok = approved_ids()
    out = []
    d = Path(out_dir)
    # 주연 산출은 p<맵>-<이벤트>-<페이지>, 트레이너 산출은 t<맵>-<이벤트> 꼴이다
    files = sorted(d.glob(f"p{int(mapno):03d}-{int(event)}-*.jsonl")) \
        + sorted(d.glob(f"t{int(mapno):03d}-{int(event)}.jsonl"))
    for fp in files:
        for line in fp.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("new"):
                    out.append({"id": r["id"], "who": r["who"], "es": r["es"],
                                "ko": r["old"], "new": r["new"],
                                "approved": r["id"] in ok})
    return out


def req_path(out_dir, cid):
    """장면이 모델에 보낸 요청 원문 파일 — `batch_pages.py`가 페이지마다 덤프한다."""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", cid or ""):     # 경로 조작 차단
        return None
    return Path(out_dir) / (cid + ".req.json")


def read_req(out_dir, cid):
    """`<cid>.req.json` → {system, user(보기 좋게 편 JSON), n}. 없으면 err."""
    p = req_path(out_dir, cid)
    if p is None or not p.exists():
        return {"err": "없음"}
    r = json.loads(p.read_text(encoding="utf-8"))
    msgs = r.get("user", r.get("messages", []))
    return {"system": r.get("system", ""),
            "user": msgs if isinstance(msgs, str)
                    else json.dumps(msgs, ensure_ascii=False, indent=1),
            "n": 0 if isinstance(msgs, str) else len(msgs)}


def verdict_path(out):
    return Path(out).parent / f"verdicts-{Path(out).name}.jsonl"


def load_verdicts(p):
    """같은 자리는 마지막 줄이 이긴다 — 덧붙이기만 하는 기록이라 고쳐 쓴 자국도 그대로 남는다.

    행 판정은 `id`로, 이벤트 일괄 승인은 `event`로 들어온다. 화면에 도로 채울 땐
    행 판정만 쓰므로 이벤트 기록은 `event:<map>:<event>` 열쇠로 따로 담는다.
    """
    out = {}
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                key = r.get("id") or ("event:" + r.get("event", ""))
                out[key] = r
    return out


def judged_rows(scenes, verdicts):
    """화면에서 끝난 행 수 — 내용 있는 행 판정, 또는 이벤트 「완료·승인」이 덮는 행.

    눌렀다 해제한 빈 레코드는 끝난 것이 아니다. 이벤트 표시가 있으면 그 장면의
    전 행을 끝난 것으로 본다(개별 판정과 겹쳐 세지 않는다).
    """
    done_ev = {k[6:] for k, x in verdicts.items()
               if k.startswith("event:") and x.get("판정") in ("완료", "승인")}
    n = 0
    for s in scenes:
        if f"{s['map']}:{s['event']}-{s['page']}" in done_ev:
            n += len(s["rows"])
            continue
        n += sum(1 for r in s["rows"]
                 if any(((verdicts.get(r["id"]) or {}).get(k) or "").strip()
                        for k in ("판정", "텍스트", "메모")))
    return n


def progress(out_dir, scenes, verdicts=None, all_rows=False):
    """검수가 어디까지 왔나 — 화면에서 빠진 행 + 화면에서 판정·완료된 행이 끝난 것이다.

    화면에서 빠지는 길은 셋: 이벤트가 반영돼 승인·보호로 갔거나, 수선 행이 먼저
    반영됐거나, 승인 줄이라 애초에 물을 것이 아니었거나. 화면에 남은 행은 판정
    기록(행 판정·이벤트 완료)이 진도다 — 반영 전이라 행이 안 빠지는 검수(최종
    반려 검토처럼)에서도 진도가 서게.
    """
    j = judged_rows(scenes, verdicts or {})
    if all_rows:
        shown = sum(len(s["rows"]) for s in scenes)
        return {"전체": shown, "승인줄": 0, "물을것": shown,
                "남음": shown - j, "끝남": j}
    from review_page import applied_rows, approved_ids, reasons
    d = Path(out_dir)
    ids = set(reasons(d))                       # 두 층이 처음 걸러 낸 자리 전부
    skip = ids & (approved_ids() | applied_rows())
    left = sum(len(s["rows"]) for s in scenes)
    ask = len(ids) - len(skip)
    return {"전체": len(ids), "승인줄": len(skip),
            "물을것": ask, "남음": left - j,
            "끝남": ask - left + j}


def append_verdict(p, rec):
    """자리마다 최종 판정 한 줄만 남긴다 — 같은 자리를 고쳐 누르면 그 줄을 갈아 끼운다."""
    rec["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    cur = load_verdicts(p)
    cur[rec.get("id") or ("event:" + rec.get("event", ""))] = rec
    tmp = p.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in cur.values()),
                   encoding="utf-8")
    tmp.replace(p)


def covers_map(out_dir):
    """id → 접힌 복제 맵 목록 — plan 청크 파일에서 읽는다(산출 파일에는 없다)."""
    stem = Path(out_dir).name.replace("-fresh", "")
    name = {"page-out": "page-chunks", "page-out-pilot": "pilot-chunks",
            "npc-out": "npc-chunks", "npc-out-pilot": "npc-pilot-chunks"}.get(stem)
    cf = Path(out_dir).parent / (name + ".jsonl") if name else None
    out = {}
    if cf and cf.exists():
        for line in cf.read_text(encoding="utf-8").splitlines():
            if line.strip():
                for r in json.loads(line)["rows"]:
                    if r.get("covers"):
                        out[r["id"]] = r["covers"]
    return out


def alt_map(alt_dir):
    """대조 산출(다른 effort 등)의 id → 신판. 없으면 빈 사전."""
    out = {}
    if not alt_dir:
        return out
    for fp in sorted(Path(alt_dir).glob("*.jsonl")):
        if fp.name.startswith("screen"):
            continue
        for line in fp.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("new"):
                    out[r["id"]] = r["new"]
    return out


def handler(out_dir, vpath, all_rows=False, alt=None, no_skip=False):
    alt = alt or {}
    page = (HEAD.format(title=f"선별분 검수 — {Path(out_dir).name}",
                        ledger=f"판정 저장 중 → {vpath}") + BODY).encode()

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

        def do_GET(self):
            u = urllib.parse.urlparse(self.path)
            if u.path == "/":
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(page)))
                self.end_headers()
                self.wfile.write(page)
            elif u.path == "/event":
                q = urllib.parse.parse_qs(u.query)
                self._json({"rows": event_rows(out_dir, q.get("map", [""])[0],
                                               q.get("event", [""])[0])})
            elif u.path == "/req":
                q = urllib.parse.parse_qs(u.query)
                self._json(read_req(out_dir, q.get("cid", [""])[0]))
            elif u.path == "/data":
                # 매번 다시 읽는다 — 선별을 다시 돌리고 새로고침하면 바로 반영된다
                # no_skip: 승인·보호에 걸린 자리도 그대로 보인다 — 유실 재검처럼
                # 이미 승인된 이벤트 안의 자리를 일부러 다시 보는 검수용
                sc = collect(out_dir, ok=set() if no_skip else None,
                             done=set() if no_skip else None, all_rows=all_rows)
                cov = covers_map(out_dir)
                for s in sc:                     # 대조 산출이 다른 답을 낸 행에 alt를 얹는다
                    p = req_path(out_dir, s["file"])
                    s["req"] = bool(p and p.exists())   # 없으면 버튼을 안 낸다
                    for r in s["rows"]:
                        a = alt.get(r["id"])
                        if a and a != r["new"]:
                            r["alt"] = a
                        if r["id"] in cov:
                            r["covers"] = cov[r["id"]]
                v = load_verdicts(vpath)
                bf = Path(out_dir) / "brief.json"
                brief = json.loads(bf.read_text(encoding="utf-8")) if bf.exists() else None
                self._json({"scenes": sc, "verdicts": v, "brief": brief,
                            "stat": progress(out_dir, sc, v, all_rows)})
            else:
                self._json({"err": "?"}, 404)

        def do_POST(self):
            if self.path == "/ask":            # 「조사 요청」 — 사람이 볼 물음을 쌓는다
                n = int(self.headers.get("Content-Length", 0))
                b = json.loads(self.rfile.read(n)) if n else {}
                if not b.get("event"):
                    return self._json({"err": "event 없음"}, 400)
                ask = vpath.parent / f"asks-{vpath.stem.removeprefix('verdicts-')}.jsonl"
                with ask.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(
                        {"event": b["event"], "장면": b.get("장면", ""),
                         "물음": b.get("물음", ""), "id": b.get("id", ""),
                         "ts": time.strftime("%Y-%m-%dT%H:%M:%S")},
                        ensure_ascii=False) + "\n")
                return self._json({"ok": True})
            if self.path != "/verdict":
                return self._json({"err": "?"}, 404)
            n = int(self.headers.get("Content-Length", 0))
            b = json.loads(self.rfile.read(n)) if n else {}
            if not b.get("id") and not b.get("event"):
                return self._json({"err": "id·event 없음"}, 400)
            keys = ("event", "판정", "텍스트", "메모") if b.get("event") else \
                   ("id", "판정", "텍스트", "메모")
            append_verdict(vpath, {k: b.get(k, "") for k in keys})
            self._json({"ok": True})

    return H


def selftest():
    import tempfile
    import threading
    import urllib.request
    with tempfile.TemporaryDirectory() as t:
        d = Path(t)
        (d / "p999-99-0.jsonl").write_text(
            json.dumps({"id": "999:99:0:0", "who": "기니아", "es": "Hola",
                        "old": "안녕", "new": "안녕하세요"}, ensure_ascii=False) + "\n"
            + json.dumps({"id": "999:99:0:1", "who": "기니아", "es": "Adios",
                          "old": "잘 가", "new": "잘 가요"}, ensure_ascii=False) + "\n",
            encoding="utf-8")
        (d / "screen.jsonl").write_text(
            json.dumps({"id": "999:99:0:0", "who": "기니아", "flags": ["존칭 변경:님"]},
                       ensure_ascii=False) + "\n", encoding="utf-8")
        v = verdict_path(d)
        srv = ThreadingHTTPServer(("127.0.0.1", 0), handler(d, v))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{srv.server_address[1]}"
        got = json.load(urllib.request.urlopen(base + "/data"))
        assert len(got["scenes"]) == 1 and got["verdicts"] == {}, got
        assert len(got["scenes"][0]["rows"]) == 1                 # 걸린 행만
        ev = json.load(urllib.request.urlopen(base + "/event?map=999&event=99"))["rows"]
        assert [r["id"] for r in ev] == ["999:99:0:0", "999:99:0:1"], ev   # 안 걸린 행까지
        assert ev[1]["ko"] == "잘 가" and ev[1]["new"] == "잘 가요"
        assert [r["approved"] for r in ev] == [False, False]
        assert json.load(urllib.request.urlopen(base + "/event?map=x&event=y"))["rows"] == []
        # 프롬프트 전문 — 파일이 있는 장면만 열리고, 없는 자리는 err로 닫힌다
        (d / "p999-99-0.req.json").write_text(
            json.dumps({"system": "SYS", "user": [{"id": "999:99:0:0", "es": "Hola"}]},
                       ensure_ascii=False), encoding="utf-8")
        rq = json.load(urllib.request.urlopen(base + "/req?cid=p999-99-0"))
        assert rq["system"] == "SYS" and rq["n"] == 1 and "Hola" in rq["user"], rq
        assert json.load(urllib.request.urlopen(base + "/req?cid=nope"))["err"]
        assert json.load(urllib.request.urlopen(base + "/req?cid=../x"))["err"]
        assert json.load(urllib.request.urlopen(base + "/data"))["scenes"][0]["req"] is True
        urllib.request.urlopen(urllib.request.Request(
            base + "/verdict", method="POST",
            data=json.dumps({"id": "999:99:0:0", "판정": "B새번역",
                             "텍스트": "안녕하세요", "메모": "ㅇㅋ"},
                            ensure_ascii=False).encode(),
            headers={"Content-Type": "application/json"}))
        urllib.request.urlopen(urllib.request.Request(
            base + "/verdict", method="POST",
            data=json.dumps({"event": "24:43", "판정": "승인", "텍스트": "",
                             "메모": "일괄"}, ensure_ascii=False).encode(),
            headers={"Content-Type": "application/json"}))
        got2 = json.load(urllib.request.urlopen(base + "/data"))
        back = got2["verdicts"]
        assert back["999:99:0:0"]["판정"] == "B새번역", back   # 새로고침하면 도로 채워진다
        assert back["999:99:0:0"]["ts"]
        assert back["event:24:43"]["판정"] == "승인", back    # 이벤트 승인은 따로 남는다
        # 진도 — 행이 화면에서 안 빠져도 판정 기록이 끝남으로 선다
        assert got2["stat"]["끝남"] == 1 and got2["stat"]["남음"] == 0, got2["stat"]
        srv.shutdown()
    print("selftest ok")


def main(argv):
    a = list(argv)
    out = a[a.index("--out") + 1] if "--out" in a else None
    port = int(a[a.index("--port") + 1]) if "--port" in a else 8788
    if not out:
        print(__doc__)
        return
    all_rows = "--all" in a          # 선별 무관 전 행 — 파일럿 전량 검수용
    no_skip = "--no-skip" in a       # 승인·보호 자리도 표시 — 유실 재검용
    alt = alt_map(a[a.index("--alt") + 1] if "--alt" in a else None)
    v = verdict_path(out)
    n = len(load_verdicts(v))
    print(f"http://localhost:{port}   판정 기록 {v}" + (f" (기존 {n}행)" if n else ""))
    print("중지: Ctrl+C", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), handler(out, v, all_rows, alt, no_skip)).serve_forever()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        selftest()
    else:
        main(sys.argv[1:])
