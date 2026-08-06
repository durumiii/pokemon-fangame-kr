# /// script
# requires-python = ">=3.12"
# ///
"""본가 정식 문장 대응표(messages.jsonl.gz) 빌드 — 공식 게임 텍스트 덤프에서.

이름(canon.jsonl)에 이어 문장 층: 특성 발동·배틀·시스템 문구 전부.
전거는 tanripj/pokemon_text_dumps — 게임·버전이 같으면 언어 파일의 줄
번호가 정확히 일치한다(2026-08-02 실측: sv 스페인어·한국어 둘 다 61,044줄).
스페인어 줄과 한국어 줄을 짝지어 es→ko 사전으로 만든다. 같은 es가 여러
게임에 있으면 최신 게임이 이긴다(대개명·현행 문구 반영).

사용법:
  gh repo clone tanripj/pokemon_text_dumps <경로>   # 653MB, 커밋하지 않는다
  DUMPS=<경로> uv run build_messages.py

산출: messages.jsonl.gz — {"es","ko","src","kind","file"}.
src = 게임 코드, kind = gametext(시스템)/storytext(대사),
file = 덤프 내 텍스트 파일 라벨(도메인 힌트: cafe·shop·taxi·trmsg 등 —
언어 간 헤더 행번호·라벨 완전 일치 실측, za 1.0.0 diff 무출력).
"""
import gzip
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).parent
DUMPS = Path(os.environ.get("DUMPS", ""))
if not DUMPS.is_dir():
    sys.exit("DUMPS=<pokemon_text_dumps clone 경로> 를 지정하세요")

GAMES = ["xy", "oras", "sm", "usum", "lgpe", "swsh", "la", "sv", "za"]  # 뒤가 최신
SKIP = {"", "​"}


def pairs(game: Path):
    for kind in ("gametext", "storytext"):
        d = game / kind
        if not d.is_dir():
            # 버전 하위 폴더 구조(sv/3.0.1/gametext …)
            subs = [p for p in sorted(game.iterdir()) if (p / kind).is_dir()]
            d = subs[-1] / kind if subs else None
        if not d:
            continue
        es_f = next(iter(d.glob("*_spanish.txt")), None)
        ko_f = next(iter(d.glob("*_korean.txt")), None)
        en_f = next(iter(d.glob("*_english.txt")), None)
        if not es_f or not ko_f:
            continue
        es = es_f.read_text(encoding="utf-8", errors="replace").splitlines()
        ko = ko_f.read_text(encoding="utf-8", errors="replace").splitlines()
        # 영어 칸도 같은 줄 번호로 짝짓는다 — 게임 스크립트가 영어 리터럴을
        # 쓰는 자리(절23 리본·시스템 문구)를 원문 키로 대조하려면 필요하다.
        en = en_f.read_text(encoding="utf-8", errors="replace").splitlines() if en_f else []
        n = min(len(es), len(ko))
        if abs(len(es) - len(ko)) > 0:
            print(f"경고: {d} 줄 수 불일치 es {len(es)} ko {len(ko)} — 앞 {n}줄만")
        if en and len(en) != len(ko):
            print(f"경고: {d} 영어 줄 수 불일치 en {len(en)} ko {len(ko)} — 영어 버림")
            en = []
        label = ""
        for i, (a, b) in enumerate(zip(es[:n], ko[:n])):
            if b.startswith("Text File : "):
                label = b[len("Text File : "):].strip()
                continue
            if b.startswith("~~~~~"):
                continue
            yield a.strip(), b.strip(), (en[i].strip() if en else ""), kind, label


def main():
    table = {}
    for g in GAMES:
        gd = DUMPS / g
        if not gd.is_dir():
            print(f"건너뜀(없음): {g}")
            continue
        n = 0
        for es, ko, en, kind, label in pairs(gd):
            if es in SKIP or ko in SKIP or es == ko:
                continue
            table[es] = (ko, en, g, kind, label)  # 뒤 게임이 덮어씀 = 최신 우선
            n += 1
        print(f"{g}: {n}쌍 처리 (누적 고유 {len(table)})")
    out = HERE / "messages.jsonl.gz"
    with gzip.open(out, "wt", encoding="utf-8") as f:
        for es, (ko, en, g, kind, label) in table.items():
            f.write(json.dumps(
                {"es": es, "ko": ko, "en": en, "src": g, "kind": kind, "file": label},
                ensure_ascii=False) + "\n")
    print(f"{out}: 고유 {len(table)}쌍")


if __name__ == "__main__":
    main()
