#!/usr/bin/env python3
"""출처 장부 — 어느 줄이 「사람이 자리를 보고 고친 것」인지 가린다.

재번역이 덮어쓰면 안 되는 자리를 정하는 데 쓴다. 2026-08-06에 이걸 손으로
하느라 커밋 53개를 읽고 갈래를 나누고 반복 문장을 걷어냈다. 그 판단을 규칙으로
옮긴 것이 이 도구다.

출처는 세 곳에서 온다.

① **제보 시트** — 유지자가 웹 스튜디오로 고친 것. 경로가 스튜디오→제보로 고정돼
   있으므로 이 시트가 「사람이 직접 고친 것」의 정본이다. `patch` 칸의 조각으로
   낱건인지 일괄 바꾸기인지도 갈린다(patch 칸의 「일괄바꾸기」 표시, 2026-08-06 스튜디오 개정).
② **커밋 꼬리표** — 대화에서 판정하고 반영한 것. 스튜디오를 안 지나가므로
   `Edit-Source:` 꼬리표로 남긴다. 값은 human / batch / bulk-term.
③ **최소 고침의 반복** — 꼬리표가 없는 옛 커밋용 보정. 같은 고침이 한 커밋 안에서
   세 번 이상 나오면 낱건 판정이 아니라 일괄 치환이거나 같은 문장이 여러 맵에
   퍼진 것이다(실측: 「궁극→최종」 138 · 「잠시만 기다려 주십시오」 34).

⚠ ③만으로는 사람과 모델을 못 가른다. 문장을 통째로 다시 쓴 것은 배치도 사람도
똑같이 「고침이 매번 다른」 모습이라 텍스트로는 구분되지 않는다. 그래서 ①②가 있다.

usage:
  uv run translate/provenance.py build     보호 목록을 만든다
  uv run translate/provenance.py stats     갈래별 집계
  uv run translate/provenance.py selftest
"""
import collections
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
REPO = ROOT.parent
KO_MAPS = "pokemon-z/translate/ko/00-maps.jsonl"
REPORTS = ROOT / "docs/log/reports/설문지 응답 시트1.jsonl"
ATTR = ROOT / "translate/data/speaker-attr.jsonl.gz"
OUT = ROOT / "translate/data/protected.jsonl"

# 꼬리표가 없던 시절의 커밋 갈래 (2026-08-06 손판정, 한 번만 채우면 된다)
LEGACY = {
    "human": """b604fd5 8f4dde2 7da1748 473a5b3 6014142 d0b9e3a 0cc88a7 eba6bca
                df299a4 7d54925 6b765d1 82b777c""".split(),
    "batch": """f9d93f3 f8d300d ae8d919 af9e7fb""".split(),
}
REPEAT = 3   # 같은 고침이 한 커밋 안에서 이만큼 나오면 낱건 판정이 아니다


def fold(s):
    return re.sub(r"\s+", " ", s or "").strip()


def sig(a, b):
    """두 문장의 최소 고침 — 「궁극→최종」처럼 바뀐 조각만 남긴다."""
    sm = difflib.SequenceMatcher(None, a, b)
    return "\x1e".join(f"{a[i:j]}\x1f{b[k:l]}"
                       for t, i, j, k, l in sm.get_opcodes() if t != "equal")


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, cwd=REPO).stdout


def snapshot(sha):
    d, cur = {}, None
    for line in git("show", f"{sha}:{KO_MAPS}").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if "map" in r:
            cur = r["map"]
            continue
        d[(cur, fold(r["k"]))] = r["v"]
    return d


def source_of(sha, body):
    """커밋의 출처 — 꼬리표가 있으면 그것, 없으면 옛 판정표."""
    m = re.search(r"^Edit-Source:\s*(\S+)", body, re.M)
    if m:
        return m.group(1)
    short = sha[:7]
    for kind, shas in LEGACY.items():
        if short in shas:
            return kind
    return "bulk-term"   # 나머지는 용어·표기 일괄로 본다


def walk():
    """(맵, 원문) → 마지막 커밋의 출처 + **사람 낱건 이력의 누적**.

    마지막 커밋만 보면 사람 낱건 뒤에 온 기계 일괄(표기 통일·값 수리)이 그 흔적을
    지운다 — 2026-08-18 실측: 재생성이 보호 219페이지를 잃었고 그중 191이 45행짜리
    기계 수리 커밋(2b1451b) 하나가 마지막 손이 된 자리였다. 그래서 human_solo는
    이력 전체에서 누적한다: 한 번이라도 사람이 낱건으로 고쳤으면 값이 남는다.
    """
    # 커밋 사이에 줄바꿈이 끼므로 레코드 구분자를 따로 둔다(널 둘로 자르면 안 붙는다)
    log = git("log", "--no-merges", "--reverse", "--format=%H%x1f%B%x1e", "--", KO_MAPS)
    prev, mark, solo = None, {}, {}
    for c in log.split("\x1e"):
        c = c.strip()
        if not c:
            continue
        sha, _, body = c.partition("\x1f")
        sha = sha.strip()
        if len(sha) != 40:
            continue
        cur = snapshot(sha)
        if prev is not None:
            ch = [(k, prev[k], cur[k]) for k in cur if k in prev and prev[k] != cur[k]]
            n = collections.Counter(sig(o, v) for _, o, v in ch)
            src = source_of(sha, body)
            for k, o, v in ch:
                spread = spread_of(o, v, n[sig(o, v)])
                mark[k] = (src, spread, sha[:7])
                if src == "human" and not spread:
                    solo[k] = sha[:7]        # 마지막 사람 낱건 커밋
        prev = cur
    return mark, solo


# 문장 끝을 바꾼 고침은 어미 손질이다. 사람이 인물 격을 손보면 같은 최소 고침
# (「~다」→「~습니다」 따위)이 수십 번 반복되므로, 반복만 보고 일괄 치환으로 몰면
# **사람의 격 손질이 통째로 보호 밖으로 떨어진다** — 2026-08-06 실측: 맵112(란토
# 저택) 유지자 제보 25건이 전량 이 함정에 걸려 보호되지 않았고, 재번역 파일럿이
# 그 페이지를 다시 썼다.
TAIL = 8


def is_ending(old, new):
    """최소 고침이 문장 끝 언저리에서만 일어났나."""
    sm = difflib.SequenceMatcher(None, old, new)
    spans = [(i, j) for tag, i, j, _, _ in sm.get_opcodes() if tag != "equal"]
    if not spans:
        return False
    return min(i for i, _ in spans) >= max(0, len(old) - TAIL)


def spread_of(old, new, n):
    """이 고침을 「퍼진 것」으로 볼 것인가.

    아니라고 보는 자리 둘:
    - **최소 고침이 비었을 때.** 제보 시트의 「현재 번역」 칸은 스튜디오에서 고친 뒤의
      글이라 「제안」과 같은 행이 많다. 차이가 없는 것은 「무엇이 바뀌었는지 모른다」는
      뜻이지 일괄 치환이라는 뜻이 아니다 — 이 자리를 반복으로 세면 **한 번에 보낸 제보가
      통째로 보호 밖으로 떨어진다**(2026-08-06 실측: 맵112 란토 저택 25건 전량).
    - **문장 끝만 바뀐 것.** 사람이 인물 격을 손보면 같은 고침(「~다」→「~습니다」)이
      수십 번 반복된다. 어미 손질은 반복해도 퍼진 것이 아니다.
    """
    if old.strip() == new.strip():
        return False
    return n >= REPEAT and not is_ending(old, new)


def protected(solo):
    """사람이 자리를 보고 고친 것 = 이력 어딘가에 human 낱건이 있는 것(누적)."""
    return set(solo)


def from_reports():
    """제보 시트에서 온 것 — 「일괄바꾸기」 표시가 붙은 것은 뺀다."""
    if not REPORTS.exists():
        return set(), 0
    per, cur = collections.defaultdict(list), None
    for line in (HERE / "ko/00-maps.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if "map" in r:
            cur = r["map"]
            continue
        per[cur].append(r)
    rows = [json.loads(l) for l in REPORTS.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = [e for e in rows if (e.get("분류") or "").startswith("0:")]
    # 「일괄바꾸기」 표시가 없던 옛 제보는 최소 고침의 반복으로 가른다 — 스튜디오가 표시를
    # 달기 전(2026-08-06 이전) 것들이라, 표시가 붙기 시작하면 이 보정은 저절로 놀게 된다.
    n = collections.Counter(sig(e.get("현재 번역") or "", e.get("제안") or "")
                            for e in rows if (e.get("제안") or "").strip())
    keys, dropped = set(), 0
    for e in rows:
        prop = (e.get("제안") or "").strip()
        cur_ko = e.get("현재 번역") or ""
        if "일괄바꾸기" in (e.get("패치 버전") or "") or \
           (prop and spread_of(cur_ko, prop, n[sig(cur_ko, prop)])):
            dropped += 1
            continue
        try:
            mid, i = (int(x) for x in e["자리"].split(":"))
            keys.add((mid, fold(per[mid][i]["k"])))
        except Exception:
            continue
    return keys, dropped


def events(keys):
    """줄을 품은 이벤트 페이지 — 보호는 이벤트 단위로 넓힌다."""
    import gzip
    loc = collections.defaultdict(set)
    with gzip.open(ATTR, "rt", encoding="utf-8") as f:
        for line in f:
            a = json.loads(line)
            if a["kind"] == "text":
                loc[(a["map"], fold(a["k"]))].add((a["map"], a["event"], a["page"]))
    ev = set()
    for k in keys:
        ev |= loc.get(k, set())
    return ev


LINES_OUT = ROOT / "translate/data/provenance-lines.jsonl"


def build():
    mark, solo = walk()
    git_keys = protected(solo)
    rep_keys, dropped = from_reports()
    keys = git_keys | rep_keys
    ev = events(keys)
    OUT.write_text("\n".join(json.dumps(
        {"map": m, "event": e, "page": p}, ensure_ascii=False)
        for m, e, p in sorted(ev)) + "\n", encoding="utf-8")
    # 행 단위 출처 목록 — stage0 gen이 읽어 값에 state·by를 찍는다(Z-53 주도권 이전).
    # 페이지 목록(OUT)은 이 목록의 파생이다.
    rows = [{"map": m, "es": k, "by": f"human/{solo[(m, k)]}"} for m, k in sorted(git_keys)]
    rows += [{"map": m, "es": k, "by": "human/report"}
             for m, k in sorted(rep_keys - git_keys)]
    LINES_OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n"
                                 for r in sorted(rows, key=lambda r: (r["map"], r["es"]))),
                         encoding="utf-8")
    print(f"이력에서 {len(git_keys)}행 · 제보에서 {len(rep_keys)}행"
          f"(일괄 바꾸기 {dropped}행 뺌) → 합 {len(keys)}행 · 이벤트 {len(ev)}개")
    print(f"→ {OUT}")
    print(f"→ {LINES_OUT} ({len(rows)}행)")


def stats():
    mark, _ = walk()
    c = collections.Counter((src, spread) for src, spread, _ in mark.values())
    print(f"{'출처':<12}{'반복?':<8}{'행':>7}")
    for (src, spread), n in sorted(c.items(), key=lambda x: -x[1]):
        print(f"{src:<12}{'퍼짐' if spread else '낱건':<8}{n:>7}")


def selftest():
    assert sig("궁극병기가 온다", "최종병기가 온다") == "궁극\x1f최종"
    assert sig("같다", "같다") == ""
    # 문장을 통째로 다시 쓰면 고침이 하나로 뭉친다 — 반복으로 잡히지 않는다
    assert len(sig("아주 다른 문장", "완전히 새로 쓴 말").split("\x1e")) >= 1
    assert source_of("b604fd5" + "0" * 33, "제목만 있는 본문") == "human"
    assert source_of("0" * 40, "제목\n\nEdit-Source: batch") == "batch"
    assert source_of("0" * 40, "제목만") == "bulk-term"
    print("selftest 통과")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "build":
        build()
    elif cmd == "stats":
        stats()
    elif cmd == "selftest":
        selftest()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
