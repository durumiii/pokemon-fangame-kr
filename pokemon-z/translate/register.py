#!/usr/bin/env python3
"""어미 급 검사 — 한 줄의 존대/하대가 그 화자의 평소 급과 어긋나는지 본다.

`reg.py`의 분류기를 쓰되 **문장 조각에 속지 않게** 감싼다. reg.classify는
「마지막 문장의 마지막 어절」로 판정하는데, 대사가 말줄임이나 나열로 끝나면
그 마지막 조각이 종결형이 아니라서 엉뚱한 급이 나온다(2026-08-06 실측:
맵305 루피코 「…금지하라느니...」가 해요체 대사인데 해체로 잡혔다).
그래서 뒤에서부터 **종결형이 분명한 문장**을 찾아 그것으로 판정한다.

화자는 `speaker.py`의 귀속표를 쓴다. 이름표가 붙은 줄로 그 인물의 평소 급을
정하고, 확정된 줄(태그+상속)이 그 급과 어긋나는지 본다.

⚠ 어긋남은 관측이지 처방이 아니다. 어미를 고칠 자리와 귀속이 틀린 자리가
섞여 있어 사람이 갈라야 한다.

usage:
  uv run translate/register.py scan            어긋난 자리를 표로 뽑는다
  uv run translate/register.py who <이름>       한 인물의 급 분포
  uv run translate/register.py selftest
"""
import gzip
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from reg import classify, clean  # noqa: E402

HERE = Path(__file__).parent
ATTR = HERE / "data/speaker-attr.jsonl.gz"
KO_MAPS = HERE / "ko/00-maps.jsonl"
OUT = HERE.parent / "docs/log/research/2026-08-06-register-mismatch.md"

# 존대 / 하대 두 축. 나머지는 판정 보류.
HIGH = {"합쇼", "해요"}
LOW = {"평서다", "해라친근", "명령라", "하게", "해체"}

# 해체로 잡혔더라도 이 꼬리는 종결이 아니라 연결·나열일 수 있다.
# 「…느니」·「…는데」·「…지」로 끊긴 조각에 속지 않으려고 뒤 문장으로 물러난다.
AMBIG = re.compile(r"(니|지|까|데|든|고|며|면|서|나)$")

# 「~다」 종결이라도 1·2인칭 표지가 있으면 지문이 아니라 청자를 앞에 둔 딱딱한
# 반말이다(사냥꾼·군인 단정체). 표지가 없으면 지문평서로 남는다.
SPEECHY = re.compile(r"(?<![가-힣])(나|난|내|내가|나도|우리|너|너희|네가|네게|네겐|넌|널|니가|당신|자네|그대)(?![가-힣])")


def speechy(text):
    """지문 꼴 문장이 실은 대화인가 — 1·2인칭 표지 유무."""
    return bool(SPEECHY.search(clean(text or "")))

# 상대에 따라 급을 바꾸는 것이 정체성인 인물들. 어미만으로 어긋남을 말할 수 없다.
DUAL = {"Lanto", "Crisanto", "Melia", "Olivier", "Aure", "Merlot",
        "Hisopo", "Cendera", "Pinot"}


def sentences(text):
    """문장 단위로 자른다. 종결부호를 남긴다 — classify가 느낌표 명령을 알아보게."""
    t = clean(text).strip()
    return [p.strip() for p in re.split(r"(?<=[.!?…])\s+|(?<=[.!?…])(?=[가-힣])", t) if p.strip()]


def axis(text):
    """(축, 근거어절, 물러난 횟수) — 뒤에서부터 종결이 분명한 문장을 찾는다."""
    parts = sentences(text)
    for back, part in enumerate(reversed(parts)):
        bucket, last = classify(part)
        if bucket in HIGH:
            return "존대", last, back
        if bucket in LOW:
            if bucket == "해체" and AMBIG.search(last) and back + 1 < len(parts):
                continue  # 조각일 수 있다 — 앞 문장을 본다
            return "하대", last, back
    return "", "", 0


def ko_key(s):
    return re.sub(r"\s+", " ", s or "").strip()


def load():
    rows = [json.loads(l) for l in gzip.open(ATTR, "rt", encoding="utf-8") if l.strip()]
    ko = {}
    for line in KO_MAPS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if "map" not in r:
            ko.setdefault(ko_key(r["k"]), r["v"])
    return rows, ko


def dominant(rows, ko):
    """이름표가 붙은 줄로 각 인물의 평소 급을 정한다."""
    tally = defaultdict(Counter)
    for r in rows:
        if r["how"] != "태그" or not r["who"]:
            continue
        v = ko.get(ko_key(r["k"]))
        if not v:
            continue
        a, _, _ = axis(v)
        if a:
            tally[r["who"]][a] += 1
    return tally


def scan():
    rows, ko = load()
    tally = dominant(rows, ko)
    out, skipped = [], Counter()
    for r in rows:
        who = r["who"]
        if r["kind"] != "text" or r["how"] not in ("태그", "상속") or not who:
            continue
        if who in DUAL:
            skipped["이중말투"] += 1
            continue
        v = ko.get(ko_key(r["k"]))
        if not v:
            skipped["번역 못 찾음"] += 1
            continue
        a, last, back = axis(v)
        if not a:
            skipped["급 판정 불가"] += 1
            continue
        c = tally.get(who)
        if not c or sum(c.values()) < 3:
            skipped["표본 부족"] += 1
            continue
        usual, n = c.most_common(1)[0]
        share = n / sum(c.values())
        if a == usual:
            continue
        if share < 0.7:
            skipped["평소 급이 갈림"] += 1
            continue
        out.append(dict(map=r["map"], event=r["event"], cmd=r["cmd"], who=who,
                        how=r["how"], now=a, usual=usual, last=last, back=back,
                        share=round(share, 2), n=sum(c.values()), ko=v))
    out.sort(key=lambda x: (-x["share"], x["map"], x["event"], x["cmd"]))
    return out, skipped, tally


def write(out, skipped, tally):
    L = ["# 어미 급이 어긋난 자리 (2026-08-06 재생성)", "",
         "화자의 평소 급은 **이름표가 붙은 줄**로 정하고, 확정된 줄이 그와 어긋나는지 본다.",
         "⚠ 어긋남은 관측이지 처방이 아니다 — 어미를 고칠 자리와 귀속이 틀린 자리가 섞여 있다.",
         "이중 말투가 정체성인 인물 아홉은 판정에서 뺐다.", "",
         f"어긋난 자리 **{len(out)}곳**. 세지 않은 것: " +
         " · ".join(f"{k} {v}" for k, v in skipped.most_common()), "",
         "| 맵:이벤트:명령 | 화자 | 귀속 | 지금 | 평소 | 평소 비율 | 근거 어절 | 현행 번역 |",
         "|---|---|---|---|---|--:|---|---|"]
    for r in out:
        L.append(f"| {r['map']}:{r['event']}:{r['cmd']} | {r['who']} | {r['how']} | "
                 f"{r['now']} | {r['usual']} | {r['share']} ({r['n']}줄) | {r['last']} | "
                 f"{r['ko'][:120].replace('|', '｜')} |")
    L += ["", "## 인물별 급 분포 (이름표 줄 기준, 10줄 이상)", "",
          "| 화자 | 존대 | 하대 | 평소 |", "|---|--:|--:|---|"]
    for who, c in sorted(tally.items(), key=lambda x: -sum(x[1].values())):
        if sum(c.values()) < 10:
            continue
        L.append(f"| {who} | {c['존대']} | {c['하대']} | {c.most_common(1)[0][0]} |")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(out)}곳 → {OUT}")


def selftest():
    # 조각에 속지 않는가 — 실측된 오판 넷
    assert axis("우두머리가 된 이후로 이상한 명령만 내리고 있어요. 책을 파기하라느니, "
                "이것저것 금지하라느니...")[0] == "존대"
    assert axis("제가 아는 거라곤 특별한 상징이라는 것뿐이죠. 보세요, 얼마나 오래됐는지!")[0] == "존대"
    assert axis("그의 의도가 적대적이라고 판단되나, 완전히 확신할 수는 없습니다. "
                "당신의 의견은 어떠합니까?")[0] == "존대"
    # 평범한 자리는 그대로
    assert axis("이것을 증표로 받아주십시오.")[0] == "존대"
    assert axis("나랑 같이 가자!")[0] == "하대"
    assert axis("우리 마을은 항상 평화롭단다.")[0] == "하대"
    assert axis("포켓몬 도감을 받았다!")[0] == "하대"
    # 물러나기는 마지막 문장이 조각일 때만
    assert axis("고마워!")[2] == 0
    # 2026-08-09 보강: 문미 호칭 「군」은 종결어미가 아니다 (구 Z-29)
    assert axis("아, 혹시 체육 관련 분야를 공부했나요, 크리산토 군?")[0] == "존대"
    # 하게체 의문 「~겠나」
    assert classify("내 악비아르와 바꾸지 않겠나?")[0] == "하게"
    # 느낌표 명령의 연결어미 꼴·ㄹ-축약 명령
    assert axis("서둘러! 한 손을 골라!")[0] == "하대"
    assert classify("서둘러!")[0] == "해체"
    # 종결어미 없는 정형구는 그대로 판정 보류
    assert axis("그렇다면 다음 기회에.")[0] == ""
    # 「~다」 지문 꼴의 대화 판별 — 인칭 표지
    assert speechy("나쁘게 듣진 마라, 하지만 난 너희 쪽 녀석들 손에 많은 전우를 잃었다.")
    assert not speechy("전기 장벽이 길을 막고 있다!")
    assert not speechy("포켓몬이 도망갔다!")
    assert not speechy("나무열매가 주렁주렁 열려 있다.")  # 「나무」의 「나」에 안 속는다
    print("selftest 통과")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "selftest":
        selftest()
    elif cmd == "scan":
        write(*scan())
    elif cmd == "who" and len(sys.argv) > 2:
        rows, ko = load()
        t = dominant(rows, ko)
        q = sys.argv[2]
        for who, c in t.items():
            if q.lower() in who.lower():
                print(f"{who}: 존대 {c['존대']} · 하대 {c['하대']}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
