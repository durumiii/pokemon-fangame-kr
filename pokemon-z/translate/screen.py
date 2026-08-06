# /// script
# requires-python = ">=3.12"
# ///
"""재번역 산출의 「뭔가 이상함」 선별 — 사람이 봐야 할 행만 추린다.

판별자(어느 쪽이 낫나)는 실측 낙제였지만(2026-08-06 discriminator-pilot), 「이 행은
사람 눈이 필요하다」는 훨씬 쉬운 문제다. 기계가 잡을 수 있는 이상 신호만 문다 —
밋밋한 재작성 같은 취향 층은 여기 못 걸리며, 그건 승인 줄·실기·제보 몫이다.

    uv run translate/screen.py <out-dir> [<out-dir> ...]
    예: uv run translate/screen.py translate/batch/page-out-pilot-fresh

산출: <out-dir>/screen.jsonl — {"id","who","flags",...}. 요약은 stdout.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import batch_pages as B  # noqa: E402

# 원문에 없는데 지어 붙이기 쉬운 성별·나이 호칭 (프롬프트 규칙 I의 감시 짝)
BANNED_ADDRESS = ("오빠", "누나", "언니", "아가씨", "총각")
# 새로 끼면 근거를 봐야 하는 경칭
TITLES = ("무슈", "마담", "마드모아젤", "폐하", "전하")
PLACEHOLDER = re.compile(r"\\[A-Za-z]+(\[[^\]]*\])?|<[^>]+>|\{\d+\}")
LATIN = re.compile(r"[A-Za-zÀ-ÿ']{3,}")
HANGUL2 = re.compile(r"[가-힣]{2,}")
AST = re.compile(r"\*([^*\n]+)\*")


def plain(s):
    s = re.sub(r"</?[bi]>", "", s or "")   # 서식 태그는 붙여서 — 낱말을 가르면 안 된다
    return PLACEHOLDER.sub(" ", s)


def latin_words(s):
    return {w.lower() for w in LATIN.findall(plain(s))}


def check_row(r, terms):
    old, new, es = r["old"], r.get("new"), r["es"]
    if not new or B.fold(new) == B.fold(old):
        return []
    f = []
    p = plain(new)
    toks = HANGUL2.findall(p)
    for a, b in zip(toks, toks[1:]):
        if a == b:
            f.append(f"중복어:{a}")
    m = re.search(r"([가-힣]{2,}) ?같은 \1", p)
    if m:
        f.append(f"중복어:{m.group(1)}")
    oa, na = AST.findall(old), AST.findall(new)
    if oa and na != oa:
        f.append(f"의성어 변경:{oa[0]}→{na[0] if na else '없음'}")
    es_l = es.lower()
    for es_t, ko_t in terms:
        if len(es_t) < 4 or es_t.lower() not in es_l:
            continue
        ko_base = ko_t.split("(")[0].strip()
        if ko_base and ko_base not in new and ko_base in old:
            f.append(f"용어 이탈:{es_t}→{ko_base} 소실")
    for w in BANNED_ADDRESS:
        if w in p and w not in plain(old):
            f.append(f"금지 호칭:{w}")
    for w in TITLES:
        if w in new and w not in old:
            f.append(f"경칭 추가:{w}")
    # 존칭 「~님」이 현행과 달라진 자리 (대장→대장님 따위) — 태그를 떼고 본다
    nim = re.compile(r"[가-힣]{1,6}님")
    diff = set(nim.findall(p)) ^ set(nim.findall(plain(old)))
    for w in sorted(diff):
        f.append(f"존칭 변경:{w}")
    new_lat, old_lat = latin_words(new), latin_words(old)
    for w in sorted(new_lat - old_lat):
        f.append(f"라틴 추가:{w}")
    for w in sorted(old_lat - new_lat):
        f.append(f"라틴 소실:{w}")
    if len(plain(new).strip()) < 0.45 * len(plain(old).strip()):
        f.append("내용 소실 의심(길이)")
    if not r.get("ok", True):
        f.append("기계 반려:" + (r.get("why") or ""))
    return sorted(set(f))


def main(dirs):
    terms = list(dict.fromkeys(B.term_pairs() + B.ledger_pairs()))
    for d in dirs:
        d = Path(d)
        rows, flagged = 0, []
        for fp in sorted(d.glob("*.jsonl")):
            if fp.name == "screen.jsonl":
                continue
            for line in fp.read_text(encoding="utf-8").splitlines():
                r = json.loads(line)
                rows += 1
                fl = check_row(r, terms)
                if fl:
                    flagged.append({"id": r["id"], "who": r["who"], "flags": fl,
                                    "es": r["es"], "old": r["old"], "new": r["new"]})
        out = d / "screen.jsonl"
        out.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in flagged)
                       + ("\n" if flagged else ""), encoding="utf-8")
        kinds = {}
        for x in flagged:
            for fl in x["flags"]:
                kinds[fl.split(":")[0]] = kinds.get(fl.split(":")[0], 0) + 1
        print(f"{d.name}: {rows}행 중 {len(flagged)}행 선별 → {out}")
        for k, v in sorted(kinds.items(), key=lambda x: -x[1]):
            print(f"  {k} {v}")


def selftest():
    t = [("máscara", "마스크")]
    row = lambda o, n: {"id": "x", "who": "w", "es": "la máscara", "old": o, "new": n, "ok": True}
    assert any("중복어" in x for x in check_row(row("어둠 속", "칠흑 같은 칠흑 속"), t))
    assert any("의성어" in x for x in check_row(row("<i>*에헴*</i>", "<i>*흠흠*</i>"), t))
    assert any("용어 이탈" in x for x in check_row(row("마스크를 써", "가면을 써"), t))
    assert any("존칭 변경" in x for x in check_row(row("<b>메를로 대장</b>의 딸", "<b>메를로 대장</b>님의 딸"), t))
    assert not check_row(row("그대로다", "그대로다"), t)
    print("selftest ok")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    elif sys.argv[1] == "selftest":
        selftest()
    else:
        main(sys.argv[1:])
