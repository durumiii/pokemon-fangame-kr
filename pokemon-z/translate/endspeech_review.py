# /// script
# requires-python = ">=3.12"
# ///
"""전투 종료 대사 배치 산출 → 검수 스튜디오 자리(절 묶음 꼴).

`batch_endspeech.py`의 산출은 절23 추가 키 갈래라 맵 좌표가 없다. 그래서 절 검수와
같은 꼴(`sec-<절이름>.jsonl`, 판정 id 「절#색인」)로 낸다 — apply_verdicts가 그 id를
못 읽는 것이 의도다(반영은 절23 창구로 사람이 넣는다).

    uv run translate/endspeech_review.py
    uv run translate/review_gui.py --out translate/batch/endspeech-review --all --port 8789
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "batch/endspeech-out/endspeech.jsonl"
DST = HERE / "batch/endspeech-review"
SEC = "23-endspeech"

# 화면에 띄우는 선별 사유 — 사람이 무엇을 봐야 하는지 한 줄로. 기계가 재는 것만 적는다.
LATIN = re.compile(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]")


def flags(r):
    f = [f"자리: {r['자리']}"]
    if r["도전_ko"]:
        f.append(f"도전 대사(현행): {r['도전_ko']}")
    else:
        f.append("도전 대사 앵커 없음 — 격의 근거가 원문뿐이다")
    if LATIN.search(r["new"] or ""):
        f.append("산출에 라틴 문자가 남았다")
    if not re.search(r"[가-힣]", r["new"] or ""):
        f.append("한글이 없다 — 의성어·비명일 수 있다")
    return f


def main():
    rows = [json.loads(l) for l in SRC.read_text(encoding="utf-8").splitlines() if l]
    DST.mkdir(parents=True, exist_ok=True)
    sec, scr = [], []
    for i, r in enumerate(rows):
        rid = f"{SEC}#{i}"
        sec.append({"id": rid, "who": r["who"], "es": r["es"],
                    "old": "", "new": r["new"]})       # old는 빈 값 — 미번역 자리다
        scr.append({"id": rid, "flags": flags(r)})
    (DST / f"sec-{SEC}.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in sec), encoding="utf-8")
    (DST / "screen.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in scr), encoding="utf-8")
    brief = {
        "title": "전투 종료 대사 26문구 — 정본 합류 승인",
        "note": ("이벤트 스크립트의 `customTrainerBattle(trainer, \"…\")` 둘째 인자다. "
                 "`_I()` 포장이 없어 어느 절에도 안 담겨 588곳 전부가 스페인어로 나온다. "
                 "26문구를 절23 추가 키(apply=kradd)로 등재하고 `customTrainerBattle` 머리에 "
                 "`endspeech=_INTL(endspeech)` 한 줄을 넣으면 588곳이 한꺼번에 풀린다. "
                 "행별 문안 판정과 별개로 아래 두 건을 정해 주세요."),
        "asks": [
            {"id": "surgery", "title": "소스 수술 한 줄",
             "ask": "`Generaentrenador` 절의 `customTrainerBattle` 머리에 "
                    "`endspeech=_INTL(endspeech)`를 넣는다(share/patch_intl.py EDITS).",
             "split": "넣으면 588호출이 절23 조회를 탄다. 안 넣으면 키를 얹어도 안 읽힌다 — "
                      "번역표만으로는 이 층에 닿는 길이 없다.",
             "rec": "승인. `_INTL`은 조회 실패 시 원문을 그대로 돌려주고, 26문구에 "
                    "`{1}` 자리표가 하나도 없어 치환 부작용이 없다. Z-18과 같은 경로다."},
            {"id": "kradd", "title": "절23 추가 키 26개 등재",
             "ask": "승인된 문안을 `translate/ko/23-script-texts.add.jsonl`에 얹고 "
                    "`gen.py`로 stage0에 흡수한다.",
             "split": "추가 키 채널은 Z-18에서 한 번 쓴 길이다. 대안은 맵 데이터를 직접 "
                      "고치는 것인데 빌드 파이프라인 밖이라 다음 빌드에 지워진다.",
             "rec": "승인."},
        ],
    }
    (DST / "brief.json").write_text(json.dumps(brief, ensure_ascii=False, indent=1),
                                    encoding="utf-8")
    print(f"{len(sec)}행 → {DST}")


if __name__ == "__main__":
    sys.exit(main())
