# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""문구 진단 한 방 도구 — 어느 층의 문제인지 즉시 판정.

실기 제보(스페인어 잔류·오역)를 받으면 이 도구부터. 주어진 문구로:
  ① korean.dat 절23 조회 (stringToKey — 루비 오라클 20,715키 검증판)
  ② 번역 정본 jsonl 검색 (원문·번역 양쪽)
  ③ 게임 Scripts.rxdata 소스 검색 — _INTL 포장 여부·루비 보간(#{}) 여부
  ④ canon(본가 정식명 대조표) 조회
를 한 번에 실행하고 층 판정을 요약한다.

usage: uv run probe.py "검색할 문구"
       uv run probe.py --es "Ciudad Luminalia"   # canon·jsonl 원문 검색 위주

층 판정 안내: dat MISS + _INTL 포장 → 키 어긋남(②층) / 미포장 리터럴 →
하드코딩(③층, UI Text KR) / 보간 포함 → ④층(patch_intl.py) / dat HIT인데
실기 스페인어 → 값 문제 아님, 다른 문구를 의심하라.
"""
import io
import json
import re
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "vendor"))
from rubymarshal.reader import load  # noqa: E402

GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data")


def string_to_key(s):
    if re.search(r"[\r\n\t\x01]|(?m:^\s+|\s+$)|\s{2,}", s):
        s = re.sub(r"(?m)^\s+", "", s)
        s = re.sub(r"(?m)\s+$", "", s)
        s = re.sub(r"\s{2,}", " ", s)
    return s


def inner_of(oh):
    return load(io.BytesIO(bytes(oh._private_data)))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    q = args[0]
    print(f"질의: {q!r}\n")

    # ① dat 조회
    d = load(open(GAME / "korean.dat", "rb"))
    ks, vs = inner_of(d[23])
    sec = {bytes(k).decode("utf-8", "replace"): bytes(v).decode("utf-8", "replace")
           for k, v in zip(ks, vs)}
    key = string_to_key(q)
    hit = sec.get(key)
    print(f"① dat 절23: {'HIT → ' + hit[:70]!r}" if hit else f"① dat 절23: MISS (키 {key[:60]!r})")
    partial = [(k, v) for k, v in sec.items() if q in k or q in v][:3]
    for k, v in partial:
        if k != key:
            print(f"   부분 일치: {k[:56]!r} → {v[:40]!r}")

    # ② jsonl
    n = 0
    for f in sorted((HERE / "ko").glob("*.jsonl")):
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            r = json.loads(line)
            k = r.get("k") or r.get("es") or ""
            v = r.get("v") or ""
            if q in k or q in v:
                n += 1
                if n <= 5:
                    print(f"② {f.name}:{i}  es={k[:44]!r}  ko={v[:36]!r}")
    print(f"② jsonl: {n}행 일치" if n else "② jsonl: 없음")

    # ③ Scripts.rxdata
    secs = load(open(GAME / "Scripts.rxdata", "rb"))
    shown = 0
    for s in secs:
        name = bytes(s[1]).decode("utf-8", "replace")
        src = zlib.decompress(bytes(s[2])).decode("utf-8", "replace")
        if q not in src:
            continue
        for ln, line in enumerate(src.splitlines(), 1):
            if q in line:
                wrapped = "_INTL(" in line
                interp = "#{" in line
                tag = ("_INTL" if wrapped else "미포장") + ("+보간" if interp else "")
                shown += 1
                if shown <= 6:
                    print(f"③ {name}:{ln} [{tag}] {line.strip()[:76]}")
    print(f"③ scripts: {shown}줄 일치" if shown else "③ scripts: 없음")

    # ④ canon (이름)
    hits = [json.loads(l) for l in open(HERE / "canon" / "canon.jsonl", encoding="utf-8")
            if q.lower() in l.lower()][:4]
    for r in hits:
        print(f"④ canon[{r['domain']}] es={r['es']!r} en={r['en']!r} ko={r['ko']!r}")
    if not hits:
        print("④ canon 이름: 없음 (창작 요소이거나 표기 상이 — 구세대명이면 aliases.jsonl 후보)")

    # ⑤ canon 문장(공식 덤프 16만 쌍) — es·ko 양방향 부분 검색.
    #    주의: Z의 스페인어는 Essentials 문구라 공식 es와 다른 경우가 많다(직격률 ~5%).
    #    자동 적용 금지 — 사람이 문맥을 보고 고르는 조회 코퍼스다.
    import gzip
    m = 0
    mz = HERE / "canon" / "messages.jsonl.gz"
    if mz.exists():
        ql = q.lower()
        for line in gzip.open(mz, "rt", encoding="utf-8"):
            if ql in line.lower():
                r = json.loads(line)
                m += 1
                if m <= 6:
                    print(f"⑤ 공식[{r['src']}] {r['es'][:52]!r} → {r['ko'][:44]!r}")
        print(f"⑤ 공식 문장: {m}쌍 일치" if m else "⑤ 공식 문장: 없음")


if __name__ == "__main__":
    main()
