# /// script
# requires-python = ">=3.12"
# ///
"""본가 정식명 대조표(canon.jsonl) 빌드 — PKHeX 텍스트 리소스에서.

「본가에 있는 것은 판정하지 않고 조회한다」(2026-08-02 사용자 방침)의 재료.
PKHeX(kwsch/PKHeX)는 현행 세대까지 관리되는 언어별 정렬 리스트를 리포에
두고 있어(2020 대개명 반영), PokeAPI CSV의 구세대 한국어 함정이 없다.

산출: canon.jsonl — {"domain","i","es","en","ko"} 한 줄 = 한 항목.
빈 값·자리표시자(?, ---)는 제외. es는 유럽 스페인어(text/other/es, items/es).

usage: uv run build_canon.py            # 새로 받아서 만들기
       uv run build_canon.py --offline  # 받아둔 raw/ 캐시로만 만들기
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw"
BASE = "https://raw.githubusercontent.com/kwsch/PKHeX/master/PKHeX.Core/Resources/text"

DOMAINS = {  # domain → (경로 틀, 파일 틀)
    "species":   "other/{lang}/text_Species_{lang}.txt",
    "moves":     "other/{lang}/text_Moves_{lang}.txt",
    "abilities": "other/{lang}/text_Abilities_{lang}.txt",
    "natures":   "other/{lang}/text_Natures_{lang}.txt",
    "types":     "other/{lang}/text_Types_{lang}.txt",
    "items":     "items/text_Items_{lang}.txt",
    # 리본은 줄 모양이 다르다 — 「열쇠<탭>이름」이고, 열쇠가 세대를 들고 있다
    # (RibbonG3CoolSuper·RibbonG4CoolGreat). 3·4세대 콘테스트 리본은 본가 문장
    # 덤프(XY 이후)에 없어서 이 파일이 유일한 전거다.
    "ribbons":   "other/{lang}/text_Ribbons_{lang}.txt",
}
LANGS = ["es", "en", "ko"]
PLACEHOLDER = {"", "?", "??", "???", "----", "-----", "(None)", "None"}


def fetch(rel: str) -> list[str]:
    cache = RAW / rel.replace("/", "__")
    if not cache.exists():
        if "--offline" in sys.argv:
            sys.exit(f"오프라인인데 캐시 없음: {cache}")
        RAW.mkdir(exist_ok=True)
        with urllib.request.urlopen(f"{BASE}/{rel}") as r:
            cache.write_bytes(r.read())
    return cache.read_text(encoding="utf-8-sig").splitlines()


def main():
    out = HERE / "canon.jsonl"
    n = 0
    with open(out, "w", encoding="utf-8") as f:
        for domain, tpl in DOMAINS.items():
            cols = {lang: fetch(tpl.format(lang=lang)) for lang in LANGS}
            length = min(len(c) for c in cols.values())
            for i in range(length):
                row = {lang: cols[lang][i].strip() for lang in LANGS}
                key = None
                if domain == "ribbons":
                    key = row["en"].split("\t")[0]
                    row = {lang: v.split("\t")[-1].strip() for lang, v in row.items()}
                    # 「쿨리본 (3세대)」의 꼬리는 PKHeX가 목록에서 세대를 가르려고 붙인
                    # 것이지 게임 안 표기가 아니다.
                    row = {lang: re.sub(r"\s*\((G3|G4|Gen3|Gen4|ORAS|\d세대)\)$", "", v)
                           for lang, v in row.items()}
                if any(v in PLACEHOLDER for v in row.values()):
                    continue
                rec = {"domain": domain, "i": i, **row}
                if key:
                    rec["key"] = key
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n += 1
    print(f"{out}: {n}행")


if __name__ == "__main__":
    main()
