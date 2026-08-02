# /// script
# requires-python = ">=3.12"
# ///
"""발굴(3단) 후보 모델 재현율 측정.

파일럿 판정(2026-08-02-z-pilot-adjudication.md)의 결격 실례 10행을 정답지로 심고
깨끗한 행 20행과 섞어, 후보 모델이 「원문 대조 오역」을 얼마나 잡는지 잰다.

usage: uv run recall_probe.py <model> [<model> ...]
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

URL = "https://api.llmgateway.io/v1/chat/completions"
KEY = os.environ.get("LLMGATEWAY_API_KEY") or sys.exit("LLMGATEWAY_API_KEY 없음")

# (row id, 결함 판, 결함 요지) — 판정 문서의 결격 사례 절에서
PLANTED = [
    (57, "gemini36", "비문 「속았습니다」"),
    (5, "gemini35", "동사 교체 imito→비춘다"),
    (147, "gemini36", "수량 축소 lustros→수년"),
    (58, "current", "수 일치 su→그들의"),
    (2, "gemini35", "무근거 수식 「짜릿한」"),
    (24, "gemini35", "무근거 수식 「치열하게」"),
    (72, "current", "문장 파손"),
    (20, "opus", "용어 medallas→메달"),
    (87, "gemini35", "cimientos→뼈대까지"),
    (98, "gemini36", "무근거 훈계조 「~는 법이다」"),
]
# 깨끗한 행: 그 id의 판정 승자 판
CLEAN = {3: "gemini36", 13: "gemini35", 17: "gemini35", 37: "opus", 50: "gemini36",
         54: "gemini36", 65: "gemini35", 68: "opus", 79: "gemini36", 84: "gemini35",
         86: "gemini35", 130: "opus", 140: "gemini36", 141: "gemini36", 142: "gemini35",
         150: "opus", 161: "gemini35", 173: "gemini35", 181: "opus", 186: "gemini35"}

PROMPT = """스페인어 포켓몬 팬게임의 한국어 번역을 검수한다. 각 행의 es(원문)와 ko(번역)를
대조해 **뜻 층위의 결함**만 찾아라: 오역, 뜻 누락, 원문에 없는 내용 추가, 비문·오타,
수(단수/복수)·성별 불일치, 수량 왜곡, 문장 구조 파손. 말투·문체 취향은 결함이 아니다.
마크업(\\c[n], \\PN, <b> 등)은 무시해라 — 따로 검사한다.

출력은 JSON 배열만: [{"id": <행 id>, "flag": true/false, "why": "<결함 요지, 없으면 빈 문자열>"}]
모든 행에 대해 하나씩. 코드펜스·설명 금지."""

PROMPT_CHECKLIST = """스페인어 포켓몬 팬게임의 한국어 번역을 검수한다. 각 행의 es(원문)와
ko(번역)를 대조하되, 행마다 아래 다섯 항목을 **하나씩 순서대로** 점검해라.

1. 추가: ko에 있는 형용사·부사·뉘앙스 중 es에 근거가 없는 것이 있는가?
   (예: 원문 una sorpresa(놀랄 일)를 「엄청나게 놀랄 일」로 부풀림)
2. 누락·왜곡: es의 내용어(명사·동사·수량 표현)가 ko에서 빠지거나 다른 뜻으로 바뀌었는가?
   (예: correr(달리다)를 「걷다」로, semanas(몇 주)를 「며칠」로)
3. 수·성: es의 단수/복수, 남성/여성이 ko에서 유지되는가?
   (지시 대상이 한 명인지 여럿인지, 남성 화법인지 여성 화법인지)
4. 문법: ko 자체가 비문이거나 오타·활용 오류가 있는가?
   (예: 목적어에 피동 활용이 붙는 류의 주술 어긋남)
5. 관례: 포켓몬 시리즈 정식 명칭과 어긋나는 역어가 있는가?
   (게임 용어는 한국어 정식 발매판 명칭이 기준이다)

말투·문체 취향은 결함이 아니다. 마크업(\\c[n], \\PN, <b> 등)은 무시해라.

출력은 JSON 배열만: [{"id": <행 id>, "flag": true/false, "why": "<위반 항목 번호와 요지, 없으면 빈 문자열>"}]
모든 행에 대해 하나씩. 코드펜스·설명 금지."""


def call(model, rows, prompt=PROMPT):
    payload = {
        "model": model, "temperature": 0.0,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": json.dumps(rows, ensure_ascii=False)},
        ],
    }
    req = urllib.request.Request(URL, data=json.dumps(payload).encode(),
                                 headers={"Authorization": f"Bearer {KEY}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.load(r)
    text = resp["choices"][0]["message"]["content"]
    cost = resp.get("usage", {}).get("cost") or resp.get("cost")
    start = text.find("[")
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1]), cost
    raise ValueError(f"JSON 배열 못 찾음: {text[:200]}")


def main():
    src = {r["id"]: r for r in map(json.loads,
           open(Path(__file__).with_name("contentious-30.jsonl"), encoding="utf-8"))}
    rows = []
    truth = {}
    for rid, variant, why in PLANTED:
        rows.append({"id": rid, "es": src[rid]["es"], "ko": src[rid][variant]})
        truth[rid] = why
    for rid, variant in CLEAN.items():
        rows.append({"id": rid, "es": src[rid]["es"], "ko": src[rid][variant]})
    rows.sort(key=lambda r: r["id"])

    use_checklist = "--checklist" in sys.argv
    models = [a for a in sys.argv[1:] if not a.startswith("--")]
    for model in models:
        try:
            verdicts, cost = call(model, rows,
                                  PROMPT_CHECKLIST if use_checklist else PROMPT)
        except Exception as e:
            print(f"\n== {model}: 실패 {e}")
            continue
        v = {x["id"]: x for x in verdicts}
        hits = [(rid, truth[rid], v.get(rid, {}).get("why", "")) for rid in truth
                if v.get(rid, {}).get("flag")]
        misses = [(rid, truth[rid]) for rid in truth if not v.get(rid, {}).get("flag")]
        false_flags = [(rid, v[rid].get("why", "")) for rid in CLEAN
                       if v.get(rid, {}).get("flag")]
        print(f"\n== {model} — 재현 {len(hits)}/{len(truth)} · 오탐 {len(false_flags)}/{len(CLEAN)} · ${cost}")
        for rid, why, mwhy in hits:
            print(f"  잡음 #{rid} [{why}] → {mwhy[:70]}")
        for rid, why in misses:
            print(f"  놓침 #{rid} [{why}]")
        for rid, mwhy in false_flags:
            print(f"  오탐 #{rid} → {mwhy[:70]}")


main()
