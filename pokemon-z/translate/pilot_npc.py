# /// script
# requires-python = ">=3.12"
# ///
"""NPC 어투 재번역 파일럿 — 페르소나 층을 실은 표본 배치.

표본: 페르소나표 64종에서 층화 추출한 이벤트 통째(장면 유지) + 지문 소량.
    uv run translate/pilot_npc.py plan   # 표본 산출 → pilot/npc-sample.jsonl
    uv run translate/pilot_npc.py run [모델]  # 기본 gemini-3.6-flash
산출: pilot/npc-out-<모델>.jsonl (원문·현행·신판 나란히 — 검수용)
"""

import gzip
import json
import random
import re as _re
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from batch import URL, key_of, worth_rewriting  # noqa: E402

JOIN = HERE.parent / "docs/research/map-speaker-join.jsonl.gz"
PERSONA = HERE / "persona-table.jsonl"
SAMPLE = HERE / "pilot" / "npc-sample.jsonl"

# 파일럿에 꼭 넣을 대표 스프라이트(버킷·성별·나이·직능 골고루)
MUST = ["campesinaw", "burguesow", "burguesaow", "burguesaow2", "mosqueterow",
        "hombre1", "mujer2", "anciano", "anciana", "nina", "brujita",
        "enfermera2", "metre", "ilustrado", "monjeYantra", "prisionero1",
        "ladrona", "gitana", "payaso", "alma"]
TARGET_ROWS = 260


def load_personas():
    return {json.loads(l)["sprite"]: json.loads(l)
            for l in PERSONA.read_text(encoding="utf-8").splitlines() if l}


def plan():
    personas = load_personas()
    rows = [json.loads(l) for l in gzip.open(JOIN, "rt", encoding="utf-8")]
    import re
    spk = re.compile(r"^(\\c\[\d+\])?<b>[^<:]{1,40}:</b>")
    ev = defaultdict(list)
    for r in rows:
        if "sprite" not in r or r.get("kind") != "text":
            continue
        if spk.match(r["k"]) or not worth_rewriting(r["v"]):
            continue
        if r["sprite"] in personas:
            ev[(r["map"], r["event"], r["sprite"])].append(r)

    random.seed(11)
    picked, used = [], set()

    def take(sprite, n_events):
        cands = sorted([k for k in ev if k[2] == sprite and k not in used],
                       key=lambda k: -len(ev[k]))
        for k in cands[:n_events]:
            used.add(k)
            picked.extend(ev[k])

    for s in MUST:
        take(s, 1)
    pool = [s for s in personas if s not in MUST]
    random.shuffle(pool)
    for s in pool:
        if len(picked) >= TARGET_ROWS:
            break
        take(s, 1)

    SAMPLE.parent.mkdir(exist_ok=True)
    with open(SAMPLE, "w", encoding="utf-8") as f:
        for r in picked:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    sprites = {r["sprite"] for r in picked}
    print(f"표본 {len(picked)}행 / 스프라이트 {len(sprites)}종 / "
          f"이벤트 {len(used)}개 → {SAMPLE}")


def npc_line(p):
    return f"{p['페르소나']} [어미: {p['버킷']}]"


def build_prompt():
    body = (HERE / "prompt-npc.md").read_text(encoding="utf-8")
    body = body.split("## 시스템 프롬프트 본문", 1)[1]
    gloss = (HERE / "glossary.md").read_text(encoding="utf-8")
    return body.replace("[용어 규칙 — glossary.md 본문 삽입]", gloss)


def ask_npc(key, model, prompt, reqrows, attempt=0, effort="minimal"):
    """batch.ask의 npc 필드 포함판(원본은 speaker/es/ko만 직렬화한다)."""
    payload = {"model": model, "temperature": 0.3, "reasoning_effort": effort,
               "messages": [
                   {"role": "system", "content": prompt},
                   {"role": "user", "content": json.dumps(reqrows, ensure_ascii=False)}]}
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + key,
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            body = json.load(r)
        text = body["choices"][0]["message"]["content"]
        cost = float(body.get("usage", {}).get("cost") or 0)
        arr = json.loads(_re.search(r"\[.*\]", text, _re.S).group(0))
        return {str(a["id"]): a["ko"] for a in arr
                if isinstance(a, dict) and isinstance(a.get("ko"), str)}, cost
    except Exception as e:
        if attempt < 2:
            time.sleep(8 * (attempt + 1))
            return ask_npc(key, model, prompt, reqrows, attempt + 1, effort)
        print("에러:", type(e).__name__, e)
        return {}, 0.0


def run(model):
    personas = load_personas()
    sample = [json.loads(l) for l in SAMPLE.read_text(encoding="utf-8").splitlines() if l]
    # 장면(맵) 단위 청크, 40행 캡
    chunks, cur, cur_map = [], [], None
    for r in sample:
        if r["map"] != cur_map or len(cur) >= 40:
            if cur:
                chunks.append(cur)
            cur, cur_map = [], r["map"]
        cur.append(r)
    if cur:
        chunks.append(cur)

    key = key_of()
    prompt = build_prompt()
    out_p = HERE / "pilot" / f"npc-out-{model.replace('/', '_')}.jsonl"
    n_ok, cost_sum = 0, 0.0
    with open(out_p, "w", encoding="utf-8") as f:
        for ci, ch in enumerate(chunks):
            reqrows = [{"id": f"{r['map']}:{i}",
                        "npc": npc_line(personas[r["sprite"]]),
                        "es": r["k"], "ko": r["v"]}
                       for i, r in enumerate(ch)]
            got, cost = ask_npc(key, model, prompt, reqrows)
            cost_sum += cost
            for i, r in enumerate(ch):
                new = got.get(f"{r['map']}:{i}")
                if new:
                    n_ok += 1
                f.write(json.dumps({
                    "sprite": r["sprite"], "map": r["map_name"],
                    "persona": personas[r["sprite"]]["페르소나"],
                    "bucket": personas[r["sprite"]]["버킷"],
                    "es": r["k"], "old": r["v"], "new": new,
                }, ensure_ascii=False) + "\n")
            print(f"청크 {ci+1}/{len(chunks)} 누적 {n_ok}행 ${cost_sum:.3f}")
    print(f"{out_p}: 응답 {n_ok}/{len(sample)}행, 비용 ${cost_sum:.3f}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "plan":
        plan()
    else:
        run(sys.argv[2] if len(sys.argv) > 2 else "gemini-3.6-flash")
