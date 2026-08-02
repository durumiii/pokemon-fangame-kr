# /// script
# requires-python = ">=3.12"
# ///
"""번역 정본(ko/)의 규모·상태·마크업 전수 집계.

usage: uv run survey.py [--json]
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

KO = Path(__file__).with_name("ko")

# 게임 마크업. 지우고 남는 라틴 글자만 「원문 잔존」으로 센다.
MARKUP = [
    ("\\c[n]", re.compile(r"\\[cC]\[\d+\]")),
    ("\\j[..]", re.compile(r"\\j\[[^\]]*\]")),
    ("\\se[..]", re.compile(r"\\se\[[^\]]*\]", re.I)),
    ("\\wt[..]", re.compile(r"\\wt?\[[^\]]*\]", re.I)),
    ("\\v[n]", re.compile(r"\\[vVnN]\[\d+\]")),
    ("<b>", re.compile(r"</?b>", re.I)),
    ("<i>", re.compile(r"</?i>", re.I)),
    ("<c2=..>", re.compile(r"<[^<>]{1,40}>")),          # 그 밖의 태그 일반
    ("{n}", re.compile(r"\{\d+\}")),
    ("\\PN", re.compile(r"\\(PN|TP|TE|TM|PL)\b")),
    ("\\1 등 제어", re.compile(r"\\[1-9lmb!.|^>< ]")),
]
STRIP = re.compile("|".join(p.pattern for _, p in MARKUP))

HANGUL = re.compile(r"[가-힣ㄱ-ㅎㅏ-ㅣ]")
LATIN = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]")
# 스페인어 표지: 고유 문자 또는 흔한 기능어
ES_MARK = re.compile(r"[¿¡ñÑáéíóúüÁÉÍÓÚÜ]|\b(el|la|los|las|un|una|de|del|que|con|para|por|no|sí|es|está|tu|te|se|y|en|al|lo|más|qué|cómo)\b", re.I)
# 개발용으로 보이는 절23 문자열(플레이어가 못 보는 것) 어림 표지
DEV_MARK = re.compile(r"(Debug|debug|RGSS|Error|error|\.rb\b|\.png\b|\.ogg\b|nil\b|Script|Graphics/|Audio/|^[a-z_]+$|^[A-Z_]+$)")


def rows_of(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        o = json.loads(line)
        if "map" in o:      # 절0 맵 헤더
            continue
        yield o


def classify(src, v):
    """(상태, 마크업 제거 후 잔존 라틴 여부)"""
    if not v.strip():
        return "빈 값"
    if src and v == src:
        return "미번역(원문 그대로)"
    bare = STRIP.sub(" ", v)
    ko = bool(HANGUL.search(bare))
    la = bool(LATIN.search(bare))
    if ko and not la:
        return "완역(한글만)"
    if ko and la:
        return "혼합(한글+라틴)" if ES_MARK.search(bare) else "혼합(한글+영문)"
    if la:
        return "라틴만(스페인어)" if ES_MARK.search(bare) else "라틴만(영문/고유명사)"
    return "글자 없음(기호·수치)"


SECTION_KIND = {0: "맵 대사", 22: "맵 대사", 23: "시스템 문구",
                15: "맵 대사", 16: "맵 대사", 17: "맵 대사",
                3: "설명문", 6: "설명문", 9: "설명문", 11: "설명문", 20: "설명문"}


def main():
    out = []
    mk_total = Counter()
    mk_by_sec = {}
    for path in sorted(KO.glob("*.jsonl")):
        sec = int(path.name[:2])
        kind = SECTION_KIND.get(sec, "이름류")
        st = Counter()
        n = es_ch = ko_ch = 0
        retr_rows = retr_ch = retr_src_ch = 0
        mk = Counter()
        for o in rows_of(path):
            n += 1
            src = o.get("k") or o.get("es") or ""
            v = o.get("v", "")
            es_ch += len(src)
            ko_ch += len(v)
            c = classify(src, v)
            st[c] += 1
            if c.startswith("완역") or c.startswith("혼합"):
                retr_rows += 1
                retr_ch += len(v)
                retr_src_ch += len(src)
            for name, pat in MARKUP:
                h = len(pat.findall(v))
                if h:
                    mk[name] += h
                    mk_total[name] += h
        mk_by_sec[path.name] = mk
        out.append(dict(file=path.name, sec=sec, kind=kind, n=n, es_ch=es_ch,
                        ko_ch=ko_ch, retr_rows=retr_rows, retr_ch=retr_ch,
                        retr_src_ch=retr_src_ch, status=dict(st)))
    if "--json" in sys.argv:
        print(json.dumps(dict(sections=out, markup=dict(mk_total),
                              markup_by_file={k: dict(v) for k, v in mk_by_sec.items()}),
                         ensure_ascii=False, indent=1))
        return
    print(f"{'파일':28} {'행':>6} {'ES자':>8} {'KO자':>8} {'재번역행':>7} {'재번역KO자':>9}")
    for r in out:
        print(f"{r['file']:28} {r['n']:6} {r['es_ch']:8} {r['ko_ch']:8} "
              f"{r['retr_rows']:7} {r['retr_ch']:9}")
    tot = {k: sum(r[k] for r in out) for k in ("n", "es_ch", "ko_ch", "retr_rows", "retr_ch", "retr_src_ch")}
    print(f"{'합계':28} {tot['n']:6} {tot['es_ch']:8} {tot['ko_ch']:8} "
          f"{tot['retr_rows']:7} {tot['retr_ch']:9}")
    print("\n상태 분포(전체):")
    all_st = Counter()
    for r in out:
        all_st.update(r["status"])
    for k, v in all_st.most_common():
        print(f"  {k:22} {v:6}")
    print("\n마크업 출현:")
    for k, v in mk_total.most_common():
        print(f"  {k:12} {v:7}")


if __name__ == "__main__":
    main()
