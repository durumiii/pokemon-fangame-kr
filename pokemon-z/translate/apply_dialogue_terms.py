# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""korean.dat 용어 후속 수정 — 실기 제보(2026-08-01)와 대사 전수 스캔의 확정분.

셋을 고친다:
1. 기합의띠/기합의머리띠 맞바꿈 — 절7·8의 [113]과 [114]가 서로 바뀌어 있다
   (절9 설명으로 실체 확인: 113=Focus Band, 114=Focus Sash). 스페인어 가짜 친구
   (Cinta/Banda)에 지난 대조가 당한 자리.
2. 목록·설명 절의 잔존 라틴 인명 — 인명 치환이 대사 절만 훑어서 절7·8·9·19·21에
   Malvo·Lanto·Merlot·Hibis·Mimi·Crisanto가 남았다. names.json으로 마저 치환.
3. 대사·배틀 메시지 속 용어 불일치 — 스페인어 원문에 기술·도구명이 서는데 한국어가
   용어집과 다른 낱말을 쓴 확정 15자리(명예볼→프리미어볼 등). 문장은 그대로 두고
   용어만 바꾼다.

usage: uv run apply_dialogue_terms.py [--dry-run]
"""
import io
import re
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "vendor"))
from fanlib import rubywrite  # noqa: E402
from datread import load  # noqa: E402  (딱지를 떼 옛 도구가 그대로 읽는다)

STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 코어/Data/korean.dat")
GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data/korean.dat")
SPEC = Path(__file__).with_name("names.json")

# 대사·메시지 용어 확정 수정 (부분 문자열 → 부분 문자열, 전 대사 절에 적용)
TERM_SWAPS = [
    ("명예볼도 하나 더 받는다", "프리미어볼도 하나 더 받는다"),
    ("『<b>궁극병기설계</b>도』", "『<b>궁극병기설계도</b>』"),
    ("‘서프라이즈’ 기술", "‘속이기’ 기술"),
    ("마음껏 화염을 뿜어봐", "마음껏 불대문자를 뿜어봐"),
    ("루미날리아역의 비밀 열쇠", "루미날리아역의 비밀의열쇠"),
    ("특수한 풀 덕분에", "파워풀허브 덕분에"),
    ("불비에 갇혔다", "마그마스톰에 갇혔다"),
    ("진흙탕물을 흡수했다", "해감액을 흡수했다"),
    ("희망사항은 나중에 이루어진다", "파멸의소원은 나중에 이루어진다"),
    ("실드포스로 데미지를 막았다", "불가사의부적으로 데미지를 막았다"),
    ("해독제 덕분에", "포이즌힐 덕분에"),
    ("위압하는 존재감이 공격을 막았다", "여왕의위엄이 공격을 막았다"),
    ("자이언트해머는 연속으로 두 번", "거대해머는 연속으로 두 번"),
    ("이상한공간의 효과가 끝났다", "원더룸의 효과가 끝났다"),
]
DIALOGUE_SECTIONS = (0, 20, 22, 23)
NAME_SECTIONS = (1, 2, 3, 4, 6, 7, 8, 9, 11, 19, 21)  # 잔존 인명 청소 대상(목록형)
LATIN = "A-Za-zÀ-ÿ"
HANGUL = re.compile(r"[가-힣]")


def inner_of(oh):
    return load(io.BytesIO(bytes(oh._private_data)))


def main():
    dry = "--dry-run" in sys.argv
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    d = load(open(STORE, "rb"))

    # 1) 기합의띠/기합의머리띠 맞바꿈
    for sec in (7, 8):
        a, b = d[sec][113].decode("utf-8"), d[sec][114].decode("utf-8")
        if (a, b) == ("기합의띠", "기합의머리띠"):
            d[sec][113], d[sec][114] = d[sec][114], d[sec][113]
            print(f"절{sec}: [113]↔[114] 맞바꿈 (기합의머리띠 / 기합의띠)")
        else:
            assert (a, b) == ("기합의머리띠", "기합의띠"), f"절{sec} 예상 밖: {a!r}/{b!r}"
            print(f"절{sec}: 이미 맞바뀜")

    # 2) 목록·설명 절 잔존 인명
    excluded = set(spec["keep"]) | set(spec["fragments"])
    names = {k: v for k, v in spec["names"].items() if k not in excluded}
    pat = re.compile(
        f"(?<![{LATIN}])(" + "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True)) + f")(?![{LATIN}])"
    )
    cleaned = 0

    def sweep(values):
        nonlocal cleaned
        dirty = False
        for i, v in enumerate(values):
            t = v.decode("utf-8", "replace")
            if not HANGUL.search(t):
                continue
            new = pat.sub(lambda m: names[m.group(1)], t)
            if new != t:
                values[i] = new.encode("utf-8")
                cleaned += 1
                dirty = True
        return dirty

    for sec in NAME_SECTIONS:
        if isinstance(d[sec], list):
            sweep(d[sec])
        else:
            keys, values = inner_of(d[sec])
            if sweep(values):
                d[sec]._private_data = rubywrite.dumps([keys, values])
    print(f"잔존 인명 청소: 값 {cleaned}개")

    # 3) 대사·메시지 용어 수정
    hits = {}
    for sec in DIALOGUE_SECTIONS:
        targets = d[sec] if sec == 0 else [d[sec]]
        for oh in targets:
            keys, values = inner_of(oh)
            dirty = False
            for i, v in enumerate(values):
                t = v.decode("utf-8")
                new = t
                for old, rep in TERM_SWAPS:
                    if old in new:
                        hits[old] = hits.get(old, 0) + new.count(old)
                        new = new.replace(old, rep)
                if new != t:
                    values[i] = new.encode("utf-8")
                    dirty = True
            if dirty:
                oh._private_data = rubywrite.dumps([keys, values])
    print(f"용어 수정: {sum(hits.values())}회 —", {k[:14]: v for k, v in hits.items()})
    missing = [old for old, _ in TERM_SWAPS if old not in hits]
    if missing:
        print("주의 — 못 찾은 패턴(이미 적용됐거나 원문 변경):", missing)

    out = rubywrite.dumps(d)
    r = load(io.BytesIO(out))
    assert r[7][113] == "기합의머리띠".encode() and r[7][114] == "기합의띠".encode()
    for sec in NAME_SECTIONS:
        if isinstance(d[sec], list):
            assert r[sec] == d[sec], f"절{sec} 왕복 불일치"
        else:
            assert inner_of(r[sec]) == inner_of(d[sec]), f"절{sec} 왕복 불일치"
    for sec in DIALOGUE_SECTIONS:
        src = d[sec] if sec == 0 else [d[sec]]
        dst = r[sec] if sec == 0 else [r[sec]]
        for a, b in zip(src, dst):
            assert inner_of(a) == inner_of(b), f"절{sec} 왕복 불일치"
    print(f"왕복 검증 통과 · 산출 {len(out):,} bytes")

    if dry:
        print("dry-run — 파일에 쓰지 않음")
        return
    STORE.write_bytes(out)
    GAME.write_bytes(out)
    print(f"기록 완료: {STORE}\n           {GAME}")


if __name__ == "__main__":
    main()
