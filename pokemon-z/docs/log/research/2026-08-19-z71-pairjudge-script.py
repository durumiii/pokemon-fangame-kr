"""Z-71 짝 판별 예선 — 재료 956행마다 변형/재서술/오짝/유보 판정 (vertex flex).
표준 장비: 8워커 병렬 · 배치별 저장(멱등) · ETA · 로그.
"""
import json, re, sys, threading, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, "translate")
from batch import MODEL, URL, key_of, or_extras

S = Path("/tmp/claude-1000/-home-durumii-workspace-claude-native-pokemon-fangame-kr/e744c036-4496-412f-a1f6-af69b24a4da5/scratchpad")
OUT = S / "pairjudge-out"; OUT.mkdir(exist_ok=True)
R = Path("docs/log/research")

rows, seen = [], set()
def add(path, pool):
    for l in open(path, encoding="utf-8"):
        r = json.loads(l)
        key = (r["절"], r["i"])
        if key in seen or "본가" not in r:
            continue
        seen.add(key)
        rows.append({"uid": f"{r['절']}#{r['i']}", "es": r["원문"][:300],
                     "ko": r["현행"][:300], "canon": r["본가"][:300], "pool": pool})
add(R / "2026-08-19-z71-split.jsonl".replace("z71-split", "z71-split"), "기존")  # cls 필터 아래에서
rows = [x for x in rows if True]
# 기존 어긋남 410만 남긴다 — split 파일에는 cls가 있으니 다시 읽는다
rows.clear(); seen.clear()
for l in open(R / "2026-08-19-z71-split.jsonl", encoding="utf-8"):
    r = json.loads(l)
    if r["cls"].startswith("어긋남"):
        seen.add((r["절"], r["i"]))
        rows.append({"uid": f"{r['절']}#{r['i']}", "es": r["원문"][:300],
                     "ko": r["현행"][:300], "canon": r["본가"][:300], "pool": "기존"})
add(R / "2026-08-19-sec23-missed-candidates.jsonl", "잔여")
add(R / "2026-08-19-z71-triage-confirmed.jsonl", "확정")
print(f"대상 {len(rows)}행 (중복 접기 후)", flush=True)

SYS_PROMPT = """포켓몬 본가 시리즈 번역 표준에 정통한 짝 판별기다. 각 항목: es=팬게임 원문(스페인어/영어),
ko=팬게임의 현행 한국어, canon=대조 도구가 짝지은 본가 공식 한국어. 항목마다 판정하라:
- "변형": es가 본가에 실재하는 그 문구와 사실상 같은 문장이고 canon이 그 문구의 공식 번역이 맞다.
- "재서술": es는 본가의 그 내용을 팬게임이 다른 문장으로 다시 쓴 것이다(내용 같고 문장 다름).
- "오짝": canon은 es와 다른 문구의 번역이다(계열만 같고 대상이 다르거나 무관 — 리본 이름류 오매칭 등).
- "유보": 확신이 없다.
JSON 배열만 출력: [{"uid":"...","v":"변형|재서술|오짝|유보","why":"열 자 내외 근거"}]"""

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
        return json.loads(re.search(r"\[.*\]", text, re.S).group(0)), cost
    except Exception as e:
        if attempt < 2:
            time.sleep(8 * (attempt + 1))
            return ask(key, batch, attempt + 1)
        return {"__error__": f"{type(e).__name__}: {e}"}, 0.0

key = key_of()
B = 30
pend = [bi for bi in range(0, len(rows), B) if not (OUT / f"b{bi:05d}.jsonl").exists()]
lock = threading.Lock()
st = {"done": 0, "cost": 0.0, "t0": time.time()}
log = open(S / "pairjudge-log.txt", "a", encoding="utf-8")
print(f"대기 {len(pend)}배치 (전체 {(len(rows)+B-1)//B})", flush=True)

def work(bi):
    batch = [{k: r[k] for k in ("uid", "es", "ko", "canon")} for r in rows[bi:bi+B]]
    got, cost = ask(key, batch)
    with lock:
        st["done"] += 1; st["cost"] += cost
        eta = (time.time() - st["t0"]) / st["done"] * (len(pend) - st["done"])
        if isinstance(got, dict):
            print(f"b{bi}: 오류 {got['__error__']}", flush=True)
        else:
            with (OUT / f"b{bi:05d}.jsonl").open("w", encoding="utf-8") as f:
                for a in got:
                    if isinstance(a, dict) and "uid" in a:
                        f.write(json.dumps(a, ensure_ascii=False) + "\n")
            print(f"{st['done']}/{len(pend)}배치 누적 ${st['cost']:.4f} ETA {eta:.0f}초", flush=True)
        log.write(f"{time.strftime('%F %T')} b{bi} rows={len(batch)} cost={cost:.5f}\n"); log.flush()

with ThreadPoolExecutor(max_workers=8) as ex:
    list(ex.map(work, pend))
print(f"끝 — 이번 실행 비용 ${st['cost']:.4f}", flush=True)
