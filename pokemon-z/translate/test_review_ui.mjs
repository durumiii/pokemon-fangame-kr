// 검수·판정 요청 화면의 동작 시험 — 서버 응답이 아니라 **화면**을 잰다.
//
//   (준비, 한 번) mkdir -p /tmp/uitest && cd /tmp/uitest && npm i happy-dom
//   (띄우고)      uv run translate/review_gui.py --out <산출폴더> --port 8793 --no-skip
//   (돌린다)      cd /tmp/uitest && node <저장소>/pokemon-z/translate/test_review_ui.mjs
//
// ⚠ 엔드포인트가 답하는 것과 화면이 도는 것은 다르다 — 「버튼이 안 눌린다」는 제보를
// 두 번 받고서야 이 시험을 세웠다(2026-08-18). 화면 코드를 고치면 이것을 돌려라.
// ⚠ 판정 버튼을 실제로 누르므로 **시험용 산출 폴더**에 대고 돌린다 — 판정 기록에 줄이 쌓인다.
// happy-dom은 이 저장소가 아니라 **돌리는 자리**의 node_modules에서 찾는다
// (repo는 uv·python 살림이라 node 의존을 안 들인다).
import { createRequire } from 'node:module';
const { Window } = createRequire(process.cwd() + '/')('happy-dom');

const base = process.env.REVIEW_URL || 'http://localhost:8793';
const html = await (await fetch(base + '/')).text();
const win = new Window({ url: base });
win.happyDOM.setURL(base);
win.document.write(html);
win.document.close();
await new Promise(r => setTimeout(r, 300));
if (win.document.querySelectorAll('.ask,.card').length === 0)   // doc.write는 스크립트를 안 돌린다
  win.eval([...win.document.querySelectorAll('script')].map(s => s.textContent).join('\n'));
await new Promise(r => setTimeout(r, 1200));

const doc = win.document;
const fail = [];
const ok = (cond, msg) => { console.log((cond ? '  ok   ' : '  FAIL ') + msg); if (!cond) fail.push(msg); };
const wait = ms => new Promise(r => setTimeout(r, ms));

const scenes = doc.querySelectorAll('#scenes .card').length;
ok(scenes > 0, `장면 카드가 선다 (${scenes})`);

const ask = doc.querySelector('.ask');
if (ask) {
  ok(!!ask.querySelector('h2'), '요청 제목이 있다');
  const heads = [...ask.querySelectorAll('h3')].map(h => h.textContent.trim());
  ok(heads.length >= 2, `요청 절 제목 ${heads.length}개 — ${heads.join(' · ')}`);
  ok(!/\d+:\d+:\d+:\d+/.test(ask.textContent), '자리 열쇠를 날것으로 뿌리지 않는다');

  const btn = [...ask.querySelectorAll('[data-b]')].find(b => b.getAttribute('data-b') === '보류');
  btn.click(); await wait(900);
  ok(btn.classList.contains('on'), '누른 판정 버튼이 켜진다');
  ok(ask.getAttribute('data-v') === '보류', '카드가 판정 색을 든다');
  ok(/저장했어요/.test(ask.querySelector('.st').textContent), '상태줄이 저장을 알린다');
  btn.click(); await wait(900);
  ok(!btn.classList.contains('on') && /물렀어요/.test(ask.querySelector('.st').textContent),
     '같은 버튼을 다시 누르면 무른다');

  const filt = [...ask.querySelectorAll('button')].find(b => /재료만/.test(b.textContent));
  if (filt) {
    filt.click(); await wait(300);
    const few = doc.querySelectorAll('#scenes .card').length;
    ok(doc.querySelector('.ask') === ask, '재료를 걸러도 요청 카드는 그대로다');
    ok(few < scenes, `재료만 남는다 (${scenes} → ${few})`);
    filt.click(); await wait(300);
    ok(doc.querySelectorAll('#scenes .card').length === scenes, '한 번 더 누르면 전체로 돌아온다');
  }
  const memo = [...ask.querySelectorAll('button')].find(b => b.textContent.trim() === '메모');
  memo.click(); await wait(200);
  ok(/메모 칸/.test(ask.querySelector('.st').textContent), '메모 여닫기도 알린다');
} else {
  console.log('  (요청 카드 없음 — brief.json 없는 산출이면 정상)');
}
console.log(fail.length ? `\n실패 ${fail.length}건` : '\n화면 시험 ok');
process.exit(fail.length ? 1 : 0);
