# /// script
# requires-python = ">=3.12"
# ///
"""재번역 산출의 모델 선별 층 — 「이 행은 사람 눈이 필요한가」만 묻는다.

판별자(둘 중 어느 쪽이 나은가)는 낙제였다(docs/research/2026-08-06-discriminator-pilot.md).
여기서는 후보를 견주지 않는다. 한 벌만 놓고 **오류 자리를 먼저 짚게** 한다 —
그 문서가 재시도 설계로 적어 둔 GEMBA-MQM 꼴이다. 기계 휴리스틱(screen.py)이
못 보는 층, 곧 원문에 없는 낱말·비문·오역을 겨냥한다.

    uv run translate/screen_llm.py <out-dir> [--model gemini-3.6-flash] [--effort low]

산출: <out-dir>/screen-llm.jsonl — {"id","유형","근거"}. 비용은 stdout.

실측(1차 장면 13페이지 319행 · gemini-3.6-flash · effort=low · $0.12): 이 층 홀로 10행을
지적해 7행이 유지자가 새 번역을 안 고른 행이었다. 제안 갈래(호칭·격·직역투)가 그 몫의
대부분이다. 행당 약 $0.0004.

백엔드는 `batch.py`가 정한다 — `Z_BACKEND=openrouter`를 얹으면 URL·키·모델이 함께 바뀐다.
크레딧이 마르면(402) 재시도하지 않고 즉시 멈춘다 — 빈 산출을 쌓지 않기 위해서다.
"""

import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from batch import MODEL, URL, key_of  # noqa: E402

PROMPT = """\
너는 스페인어 원문과 그 한국어 번역을 대조해 **손볼 곳이 있는 행만** 골라내는 검수자다.
고르는 것이 아니라 거르는 일이다 — 어느 쪽이 나은지는 묻지 않는다.

입력은 JSON 배열이고 각 항목은 {"id", "who", "es", "ko"}이다.
아래 네 갈래 중 하나에 걸리는 행만 보고한다:

- `지어냄` — 원문에 근거가 없는 낱말·정보·호칭이 번역에 들어갔다(직업·성별·나이·경칭 포함).
- `누락` — 원문의 뜻 한 조각이 번역에서 사라졌다.
- `비문` — 한국어로 성립하지 않는다(조사·어미·띄어쓰기가 어긋나 뜻이 깨진 자리).
- `오역` — 원문과 뜻이 다르다.

위 넷은 **오류**다. 그와 별도로, 아래 네 갈래는 `제안`으로 보고한다 — 확신이 아니라
「사람이 한 번 보면 좋겠다」는 표시다. **제안은 의심스러우면 올려라.** 걸리는 데가
있는데 왜인지 딱 짚기 어려워도, 짚을 수 있는 만큼만 적어 올린다.

- `제안-호칭` — 호칭·경칭·2인칭이 관계와 안 맞아 보인다. 사람이 가장 자주 짚는 자리다:
  · 원문에 없는 존칭이 붙거나(「대장」→「대장님」), 있던 존칭이 빠졌다.
  · 부하가 상관을, 백성이 왕족을 부르는데 경칭이 없다(「메를로 대장님」·「국왕 폐하」꼴).
  · 적대하는 상대에게 존칭을 쓰거나, 손윗사람에게 낮춤말을 쓴다.
  · 장면 머리의 말투 지시가 「A에게 존대」라고 했는데 그 상대에게 반말이다.
  · 인명·직함의 한국어 표기가 장면 안에서 흔들린다.
- `제안-격` — 존대와 반말이 어긋난다:
  · 같은 상대에게 잇달아 말하는데 줄마다 격이 흔들린다.
  · 화자와 듣는 이의 관계에 견주어 격이 반대로 보인다.
  · 원문의 usted/vos 흔적(le·su·3인칭 동사·-áis/-éis·vuestro)이 있는데 반말로 갔다.
- `제안-직역투` — 스페인어 구문을 그대로 옮긴 티:
  · 「~에 대해(서)」, 「~를 통해」, 「~하는 것이 가능하다」, 이중 피동 「~되어진다」.
  · 관계절을 그대로 편 긴 수식, 「~에 의해」 피동.
  · 원문에는 자연스러운데 한국어로는 군더더기인 낱말(「사실」·「정말로」·「그것」 따위).
  · ¡Qué …! 를 「얼마나 ~한가!」로 옮긴 자리.
- `제안-어색` — 문장은 성립하지만 게임 대사로 소리 내 읽으면 걸린다(어미가 겉돌거나
  구어 리듬이 죽은 자리, 말맛이 밋밋해진 재작성). **문어투 어미 자체는 걸지 마라** —
  그 인물의 결일 수 있다.

**보고하지 않는 것**: 원문 그대로 두기로 한 프랑스어 감탄구, 서식 태그(<b>·<i>·\\c[n]·\\PN),
낱말 하나를 동의어로 바꾸면 되는 순수 취향.

오류는 의심스러우면 보고하지 마라 — 근거를 원문 낱말로 댈 수 있는 것만. 오류에는 수 제한이
없다. 제안은 **오류와 따로 세어** 한 페이지에 걸리는 것 다섯까지 — 오류가 몇이든 제안 몫
다섯은 그대로다.

출력은 JSON 배열 하나뿐. 문제 없는 행은 넣지 않는다. 형식:
[{"id": "<입력에 있던 id>", "유형": "지어냄", "근거": "원문에 없는 낱말 「…」이 들어갔다"},
 {"id": "<id>", "유형": "제안-호칭", "근거": "부하가 상관을 부르는데 경칭이 없다"},
 {"id": "<id>", "유형": "제안-격", "근거": "앞 줄은 존대인데 같은 상대에게 반말로 갔다"},
 {"id": "<id>", "유형": "제안-직역투", "근거": "「사실」이 원문 En realidad의 직역 군더더기다"}]
문제가 없으면 [] 를 낸다.
"""


def ask(key, model, effort, system, rows, attempt=0):
    payload = {"model": model, "temperature": 0, "reasoning_effort": effort,
               "messages": [{"role": "system", "content": system},
                            {"role": "user",
                             "content": json.dumps(rows, ensure_ascii=False)}]}
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode(),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                body = json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 402:                   # 크레딧 소진 — 재시도해도 같다, 즉시 멈춘다
                raise SystemExit(f"402 결제 필요 — 중단합니다: {e.read()[:200].decode('utf-8','replace')}")
            raise
        text = body["choices"][0]["message"]["content"]
        cost = float(body.get("usage", {}).get("cost") or 0)
        arr = json.loads(re.search(r"\[.*\]", text, re.S).group(0))
        return [a for a in arr if isinstance(a, dict) and a.get("id")], cost
    except Exception as e:
        if attempt < 2:
            time.sleep(8 * (attempt + 1))
            return ask(key, model, effort, system, rows, attempt + 1)
        print("에러:", type(e).__name__, e)
        return [], 0.0


def scene_system(fp):
    """그 페이지를 번역할 때 쓴 프롬프트를 장면 맥락으로 덧댄다 — 말투 지시·본보기가 거기 있다."""
    req = fp.with_suffix(".req.json")
    if not req.exists():
        return PROMPT
    head = json.loads(req.read_text(encoding="utf-8")).get("system", "")
    # 번역용 정적 지시(~1,100토큰)는 판정에 안 쓰인다 — 용어 규칙부터만 덧댄다.
    # 게이트웨이가 캐시 할인을 안 주는 걸 실측(2026-08-06)해서 중복 전송 자체를 자른다.
    i = head.find("### Term rules")
    if i > 0:
        head = head[i:]
    return PROMPT + "\n\n---\n참고 — 이 장면을 번역할 때 준 지시:\n" + head


def run(d, model, effort):
    key, out, total = key_of(), [], 0.0
    for fp in sorted(Path(d).glob("*.jsonl")):
        if fp.name.startswith("screen"):
            continue
        rows = [json.loads(l) for l in fp.read_text(encoding="utf-8").splitlines() if l.strip()]
        ask_rows = [{"id": r["id"], "who": r["who"], "es": r["es"],
                     "ko": r.get("new") or r["old"]} for r in rows if r.get("new")]
        if not ask_rows:
            continue
        hits, cost = ask(key, model, effort, scene_system(fp), ask_rows)
        total += cost
        ids = {r["id"] for r in ask_rows}
        out += [h for h in hits if h["id"] in ids]
        print(f"  {fp.name}: {len(ask_rows)}행 → {len(hits)}행 지적 (${cost:.4f})")
    p = Path(d) / "screen-llm.jsonl"
    p.write_text("".join(json.dumps(h, ensure_ascii=False) + "\n" for h in out),
                 encoding="utf-8")
    print(f"{d}: {len(out)}행 → {p}  합계 ${total:.4f}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit()
    model = a[a.index("--model") + 1] if "--model" in a else MODEL
    effort = a[a.index("--effort") + 1] if "--effort" in a else "low"
    for d in [x for x in a if not x.startswith("--")
              and x not in (model, effort)]:
        run(d, model, effort)
