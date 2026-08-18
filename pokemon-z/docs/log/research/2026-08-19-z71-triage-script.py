"""Z-71 유보·창작 재분류 예선 — 저가 모델(vertex flex) 판별 + 배치별 저장(멱등).

usage: Z_BACKEND=openrouter uv run python z71_triage.py
"""
import json, re, sys, time, urllib.request
from pathlib import Path

sys.path.insert(0, "translate")
from batch import MODEL, URL, key_of, or_extras

S = Path("/tmp/claude-1000/-home-durumii-workspace-claude-native-pokemon-fangame-kr/e744c036-4496-412f-a1f6-af69b24a4da5/scratchpad")
OUT = S / "triage-out"; OUT.mkdir(exist_ok=True)

rows = []
for name, tag in (("sec23-unsure.jsonl", "유보"), ("sec23-creative.jsonl", "창작추정")):
    for l in open(S / name, encoding="utf-8"):
        r = json.loads(l)
        rows.append({"i": r["i"], "es": r["원문"], "ko": r["현행"], "출신": tag})
print(f"대상 {len(rows)}행")

SYS_PROMPT = """포켓몬 본가 시리즈에 정통한 판별기다. 각 항목은 팬게임의 전투·시스템 문구다
(es=원문 스페인어/영어, ko=현행 한국어 번역). 항목마다 하나를 판정하라:
- "본가": 본가 시리즈(적녹~SV)에 실재하는 문구·용어·아이템·기술·리본·시설 문구다.
  이때 canonical 영어명(en)과 공식 한국어 표기(oko)를 아는 만큼 함께 적어라.
- "시스템": 게임 엔진·그래픽 설정·키 설정·개발 도구 등 본가 무관 시스템/UI 문구.
- "창작": 팬게임 고유(자체 인물·커스텀 기술·자체 대화·자체 시설).
확신이 없으면 "모름". JSON 배열만 출력: [{"i":숫자,"cls":"본가|시스템|창작|모름","en":"...","oko":"..."}]
en·oko는 본가일 때만, 모르면 생략."""

def ask(key, batch, attempt=0):
    payload = {"model": MODEL, "temperature": 0.1, "reasoning_effort": "minimal",
               "messages": [{"role": "system", "content": SYS_PROMPT},
                            {"role": "user", "content": json.dumps(batch, ensure_ascii=False)}],
               **or_extras()}
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + key,
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            body = json.load(r)
        text = body["choices"][0]["message"]["content"]
        cost = float(body.get("usage", {}).get("cost") or 0)
        m = re.search(r"\[.*\]", text, re.S)
        return json.loads(m.group(0)), cost
    except Exception as e:
        if attempt < 2:
            time.sleep(8 * (attempt + 1))
            return ask(key, batch, attempt + 1)
        return {"__error__": f"{type(e).__name__}: {e}"}, 0.0

import threading
from concurrent.futures import ThreadPoolExecutor

key = key_of()
B = 40
pend = [bi for bi in range(0, len(rows), B) if not (OUT / f"b{bi:05d}.jsonl").exists()]
lock = threading.Lock()
st = {"done": 0, "cost": 0.0, "t0": time.time()}
log = open(S / "triage-log.txt", "a", encoding="utf-8")
print(f"대기 {len(pend)}배치 (전체 {(len(rows)+B-1)//B})", flush=True)

def work(bi):
    batch = [{"i": r["i"], "es": r["es"][:200], "ko": r["ko"][:200]} for r in rows[bi:bi+B]]
    got, cost = ask(key, batch)
    with lock:
        st["done"] += 1; st["cost"] += cost
        el = time.time() - st["t0"]
        eta = el / st["done"] * (len(pend) - st["done"])
        if isinstance(got, dict):
            msg = f"b{bi}: 오류 {got['__error__']}"
        else:
            with (OUT / f"b{bi:05d}.jsonl").open("w", encoding="utf-8") as f:
                for a in got:
                    if isinstance(a, dict) and "i" in a:
                        f.write(json.dumps(a, ensure_ascii=False) + "\n")
            msg = f"{st['done']}/{len(pend)}배치 누적 ${st['cost']:.4f} ETA {eta:.0f}초"
        print(msg, flush=True)
        log.write(f"{time.strftime('%F %T')} b{bi} rows={len(batch)} cost={cost:.5f}\n")
        log.flush()

with ThreadPoolExecutor(max_workers=8) as ex:
    list(ex.map(work, pend))
print(f"끝 — 이번 실행 비용 ${st['cost']:.4f}", flush=True)
