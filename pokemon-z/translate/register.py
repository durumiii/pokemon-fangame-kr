#!/usr/bin/env python3
"""어미 급 검사 — 한 줄의 존대/하대가 그 화자의 평소 급과 어긋나는지 본다.

⚠ **이 도구는 프리필터다 — 감사 도구가 아니다**(유지자 판정 2026-08-19, Z-66).
위양성을 줄여 정말 명확한 후보만 걸러 LLM·사람의 검토 부하를 선제적으로 살짝
줄이는 것까지가 역할이다. 놓침(재현율)은 책임 범위 밖이니 「스캔이 비었다」를
「어긋남이 없다」로 읽지 마라. 빈틈을 메워 완전 커버로 가는 방향은 걷었다.

`reg.py`의 분류기를 쓰되 **문장 조각에 속지 않게** 감싼다. reg.classify는
「마지막 문장의 마지막 어절」로 판정하는데, 대사가 말줄임이나 나열로 끝나면
그 마지막 조각이 종결형이 아니라서 엉뚱한 급이 나온다(2026-08-06 실측:
맵305 루피코 「…금지하라느니...」가 해요체 대사인데 해체로 잡혔다).
그래서 뒤에서부터 **종결형이 분명한 문장**을 찾아 그것으로 판정한다.

화자는 `speaker.py`의 귀속표를 쓴다. 이름표가 붙은 줄로 그 인물의 평소 급을
정하고, 확정된 줄(태그+상속+전투호출)이 그 급과 어긋나는지 본다. 전투 호출 줄은
**검사만 받고 평소 급 계산에는 안 들어간다**(`CHECKED` 옆 주석).

⚠ 어긋남은 관측이지 처방이 아니다. 어미를 고칠 자리와 귀속이 틀린 자리가
섞여 있어 사람이 갈라야 한다.

usage:
  uv run translate/register.py scan [출력경로] [--dual]
                                               어긋난 자리를 표로 뽑는다
                                               (기본: docs/log/research/<오늘>-register-mismatch.md)
                                               --dual: 이중 말투 인물도 검사에 넣는다(SCAN_DUAL 주석 참조)
  uv run translate/register.py who <이름>       한 인물의 급 분포
  uv run translate/register.py selftest
"""
import gzip
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from reg import classify, clean  # noqa: E402

HERE = Path(__file__).parent
ATTR = HERE / "data/speaker-attr.jsonl.gz"
KO_MAPS = HERE / "ko/00-maps.jsonl"
RESEARCH = HERE.parent / "docs/log/research"


def out_path(argv):
    """기록층은 날짜 박제다 — 돌릴 때마다 그날 파일로 낸다. 상수로 잡아 두면
    2026-08-06 판을 덮어썼다(2026-08-17에 실측·수선)."""
    rest = [a for a in argv[2:] if not a.startswith("--")]
    if rest:
        return Path(rest[0])
    return RESEARCH / f"{date.today():%Y-%m-%d}-register-mismatch.md"

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

# 상대에 따라 급을 바꾸는 것이 정체성인 인물들. 기본값은 **검사에서 뺀다**.
#
# 「청자를 모르는 것은 이들만의 사정이 아니니 일단 잡고 아닌 자리는 판정으로 내린다」는
# 길이 있고, `scan --dual`로 그 길을 갈 수 있다(그때는 빼는 대신 `(이중)` 표시만 붙는다).
# 다만 이 도구가 아직 채점을 안 거쳐(혼잣말·말흐림·세부 어미·청자 미고려 오탐) 넓히면
# 오탐이 같이 늘므로, 켜는 것은 유지자 판정을 받고 이 상수를 뒤집는다.
# 넓혔을 때의 델타는 docs/log/research/2026-08-17-register-dual-delta.md.
SCAN_DUAL = False

DUAL = {"Lanto", "Crisanto", "Melia", "Olivier", "Aure", "Merlot",
        "Hisopo", "Cendera", "Pinot"}

OK = HERE / "data/register-ok.jsonl"          # 사람 직접 편집 원천
SITES = HERE / "stage0" / "sites.jsonl"       # gen이 원천을 자리 칸(register_ok)으로 편 것


def is_dual(who):
    """귀속표의 이름표는 직함을 달고 온다 — `Alcaide Pinot`·`Capitán Merlot`·
    `Capitana Cendera`·`Auretosk`. 맨이름으로만 맞추면 160행이 샌다
    (2026-08-16 실측)."""
    return any(n in (who or "") for n in DUAL)


def load_ok(path=None):
    """원천(register-ok.jsonl) 원본 줄들 — 등재 위생 검사(selftest)용.

    등재 꼴: 줄마다 `map`은 필수, `event`·`page`·`cmd`·`who`는 있는 것만 맞춘다 —
    이벤트 통째·페이지 통째·명령 하나를 같은 꼴로 적는다.
    ⚠ 한 이벤트에 화자가 여럿 서는 자리가 흔하니(맵90 ev35는 볼프람과 올리비에가
    같이 선다) 이벤트 통째로 적을 때는 `who`를 함께 적어 남의 줄까지 덮지 마라.
    `이유` 칸은 근거 없는 제외가 쌓이지 않게 비워 두지 마라."""
    p = Path(path) if path else OK
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def load_ok_ids():
    """어긋남 아님 판정이 찍힌 자리 id → 이유. 좌표 조건의 펴기는 stage0 gen이 했다
    (`stamp_register_ok`) — **원천에 등재한 뒤에는 gen을 다시 돌려야 여기 보인다.**"""
    out = {}
    for l in SITES.read_text(encoding="utf-8").splitlines():
        if '"register_ok"' in l:
            r = json.loads(l)
            out[r["id"]] = r.get("register_ok", "")
    return out


def sentences(text):
    """문장 단위로 자른다. 종결부호를 남긴다 — classify가 느낌표 명령을 알아보게."""
    t = clean(text).strip()
    return [p.strip() for p in re.split(r"(?<=[.!?…])\s+|(?<=[.!?…])(?=[가-힣])", t) if p.strip()]


# B1~B7 급 판정 (speech-style 「이름표 없는 잡담 NPC」 표가 정본, 2026-08-09 확장)
# 코드↔이름의 정본은 이 표 하나다 — 라벨을 다른 파일에 다시 적지 마라.
BUCKET_NAMES = {"B1": "반말", "B2": "해요", "B3": "합쇼", "B4": "어른말",
                "B5": "지문평서", "B6": "하게", "B7": "대화단정"}
B = {k: k + v for k, v in BUCKET_NAMES.items()}      # "B1" → "B1반말"
BUCKET7 = {"합쇼": B["B3"], "해요": B["B2"], "해라친근": B["B4"],
           "하게": B["B6"], "해체": B["B1"]}
BCODE = re.compile(r"B([1-7])(?:" + "|".join(BUCKET_NAMES.values()) + r")?")
B4_CMD = re.compile(r"(거라|렴|려무나)$")
UNDET = {"체언기타", "비한글", "empty", "연결미완"}


def spell(text):
    """버킷 표기의 B코드를 이름으로 편다 — 프롬프트를 읽는 모델은 내부 코드를 모른다.

    「B1(어른 상대만 B2)」 → 「반말(어른 상대만 해요)」. 이름이 이미 붙은 「B6하게」는
    이름 하나로 접는다. 코드가 없는 표기(「인물 정본」·「제외(사물 …)」)는 그대로.
    """
    return BCODE.sub(lambda m: BUCKET_NAMES["B" + m.group(1)], text or "")


def grade(text, lenient=False):
    """(급 B1~B7, 근거어절, 물러난 문장 수). 판정 불가면 ('', last, 0).

    말줄임·나열 조각은 앞 문장으로 물러난다. lenient=True면 물러나기가
    빈손일 때 처음 만난 해체 조각을 받는다. 표지 없는 행의 급 단정은
    피하라 — 화자 단위 집계가 정본(지침 참조).
    """
    parts = sentences(text or "")
    fallback = None
    for back, part in enumerate(reversed(parts)):
        b, last = classify(part)
        if b in UNDET:
            continue
        if b == "명령라":
            return (B["B4"] if B4_CMD.search(last) else B["B1"]), last, back
        if b == "해체" and AMBIG.search(last) and back + 1 < len(parts):
            fallback = fallback or (B["B1"], last, back)
            continue
        if b == "평서다":
            return (B["B7"] if speechy(text) else B["B5"]), last, back
        return BUCKET7[b], last, back
    if lenient and fallback:
        return fallback
    return "", "", 0


def axis(text):
    """(축, 근거어절, 물러난 횟수) — 뒤에서부터 종결이 분명한 문장을 찾는다.

    「~다」 종결은 인칭 표지가 있어야 대화(하대)다 — 표지 없는 지문평서(B5)는
    청자를 앞에 둔 말이 아니라서 급 판정을 보류한다(Z-66 할 일 1: grade()의
    SPEECHY 구분을 급 검사도 쓴다. 2026-08-18)."""
    parts = sentences(text)
    for back, part in enumerate(reversed(parts)):
        bucket, last = classify(part)
        if bucket in HIGH:
            return "존대", last, back
        if bucket in LOW:
            if bucket == "해체" and AMBIG.search(last) and back + 1 < len(parts):
                continue  # 조각일 수 있다 — 앞 문장을 본다
            if bucket == "평서다" and not speechy(text):
                continue  # 지문평서 — 대화가 아니다
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


# 검사는 하되 **평소 급 계산에는 안 넣는** 근거. 전투 호출(`pbTrainerBattle`)의 대사는
# 화자가 호출 인자로 확정되지만, 트레이너 이름 322종 중 38종이 기존 이름표와 같은
# 문자열이라 평소 급 표에 섞으면 확정된 인물의 급이 흔들린다(Z-60).
CHECKED = ("태그", "상속", "전투호출")


def dominant(rows, ko):
    """이름표가 붙은 줄로 각 인물의 평소 급을 정한다 — `how="태그"`만 센다."""
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


def scan(scan_dual=SCAN_DUAL):
    rows, ko = load()
    tally = dominant(rows, ko)
    oks = load_ok_ids()
    out, skipped = [], Counter()
    for r in rows:
        who = r["who"]
        if r["kind"] not in ("text", "battle") or r["how"] not in CHECKED or not who:
            continue
        if is_dual(who) and not scan_dual:
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
        if f"m{r['map']}.e{r['event']}.p{r['page']}.c{r['cmd']}" in oks:
            skipped["판정됨"] += 1
            continue
        out.append(dict(map=r["map"], event=r["event"], page=r["page"], cmd=r["cmd"],
                        who=who, dual=is_dual(who),
                        how=r["how"], now=a, usual=usual, last=last, back=back,
                        share=round(share, 2), n=sum(c.values()), ko=v))
    out.sort(key=lambda x: (-x["share"], x["map"], x["event"], x["page"], x["cmd"]))
    return out, skipped, tally


def write(out, skipped, tally, path, dual=False):
    L = [f"# 어미 급이 어긋난 자리 ({date.today():%Y-%m-%d} 생성)", "",
         "화자의 평소 급은 **이름표가 붙은 줄**로 정하고, 확정된 줄이 그와 어긋나는지 본다.",
         "⚠ 어긋남은 관측이지 처방이 아니다 — 어미를 고칠 자리와 귀속이 틀린 자리가 섞여 있다.",
         ("상대에 따라 격을 갈아입는 인물 아홉도 검사에 넣었다 — 화자 칸의 **(이중)** 표시가 그것이다."
          if dual else "상대에 따라 격을 갈아입는 인물 아홉은 판정에서 뺐다(`scan --dual`로 넣을 수 있다)."),
         "어긋남이 아니라고 판정한 자리는 `translate/data/register-ok.jsonl`에 근거와 함께 등재하고",
         "`stage0/gen.py`를 다시 돌리면(자리 칸으로 펴진다) 다음 실행부터 「판정됨」으로 세어진다.", "",
         f"어긋난 자리 **{len(out)}곳**. 세지 않은 것: " +
         " · ".join(f"{k} {v}" for k, v in skipped.most_common()), "",
         "| 맵:이벤트:페이지:명령 | 화자 | 귀속 | 지금 | 평소 | 평소 비율 | 근거 어절 | 현행 번역 |",
         "|---|---|---|---|---|--:|---|---|"]
    for r in out:
        L.append(f"| {r['map']}:{r['event']}:{r['page']}:{r['cmd']} | "
                 f"{r['who']}{' (이중)' if r['dual'] else ''} | {r['how']} | "
                 f"{r['now']} | {r['usual']} | {r['share']} ({r['n']}줄) | {r['last']} | "
                 f"{r['ko'][:120].replace('|', '｜')} |")
    L += ["", "## 인물별 급 분포 (이름표 줄 기준, 10줄 이상)", "",
          "| 화자 | 존대 | 하대 | 평소 |", "|---|--:|--:|---|"]
    for who, c in sorted(tally.items(), key=lambda x: -sum(x[1].values())):
        if sum(c.values()) < 10:
            continue
        L.append(f"| {who} | {c['존대']} | {c['하대']} | {c.most_common(1)[0][0]} |")
    path.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(out)}곳 → {path}")


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
    # 지문평서는 급 판정 보류 — 인칭 표지가 있으면 대화단정으로 하대 (Z-66 할 일 1)
    assert axis("포켓몬 도감을 받았다!")[0] == ""
    assert axis("전기 장벽이 길을 막고 있다!")[0] == ""
    assert axis("나쁘게 듣진 마라, 하지만 난 너희 쪽 녀석들 손에 많은 전우를 잃었다.")[0] == "하대"
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
    # B1~B7 급 판정 (2026-08-09 확장)
    assert grade("한마디만 해 두지. 나한텐 총이 두 자루 있다네.")[0] == "B6하게"
    assert grade("내 악비아르와 바꾸지 않겠나?")[0] == "B6하게"
    assert grade("우리 마을은 항상 평화롭단다.")[0] == "B4어른말"
    assert grade("나쁘게 듣진 마라, 하지만 난 너희 쪽 녀석들 손에 많은 전우를 잃었다.")[0] == "B7대화단정"
    assert grade("전기 장벽이 길을 막고 있다!")[0] == "B5지문평서"
    assert grade("포켓몬센터에 오신 것을 환영해요.")[0] == "B2해요"
    assert grade("이것을 증표로 받아주십시오.")[0] == "B3합쇼"
    assert grade("나랑 같이 가자!")[0] == "B1반말"
    # 버킷 표기 펴기 — 프롬프트에 B코드가 새지 않는다
    assert spell("B1(어른 상대만 B2)") == "반말(어른 상대만 해요)"
    assert spell("B6하게(배틀 도발·혼잣말은 B1)") == "하게(배틀 도발·혼잣말은 반말)"
    assert spell("B1+B7(총사 계열)") == "반말+대화단정(총사 계열)"
    assert spell("제외(사물 — 잠긴 문 안내는 지문 규칙)").startswith("제외")
    # 출력 경로 — 기본은 오늘 날짜, 인자가 있으면 그것
    assert out_path(["register.py", "scan"]).name == f"{date.today():%Y-%m-%d}-register-mismatch.md"
    assert out_path(["register.py", "scan", "/tmp/x.md"]) == Path("/tmp/x.md")
    assert out_path(["register.py", "scan", "--dual"]).name.endswith("-register-mismatch.md")
    assert out_path(["register.py", "scan", "--dual", "/tmp/x.md"]) == Path("/tmp/x.md")
    # 자리 칸 펴기(gen.stamp_register_ok)가 실물 사이트에 서 있는가
    oki = load_ok_ids()
    assert "m112.e4.p0.c254" in oki and oki["m112.e4.p0.c254"]   # 낱 명령 등재
    # 이벤트 통째 + who 등재(맵90 ev35 Wolfram)가 남의 줄(올리비에)을 안 덮는가
    m90 = [json.loads(l) for l in SITES.read_text(encoding="utf-8").splitlines()
           if l.startswith('{"id": "m90.e35.')]
    assert any("register_ok" in r for r in m90)
    assert all(r.get("who") == "Wolfram" for r in m90 if "register_ok" in r)
    # 원천 등재 위생 — 이유 칸이 비지 않았는가
    real = load_ok()
    assert real and all(o.get("이유") and o.get("map") is not None for o in real)
    print("selftest 통과")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "selftest":
        selftest()
    elif cmd == "scan":
        dual = "--dual" in sys.argv
        write(*scan(dual or SCAN_DUAL), out_path(sys.argv), dual=dual or SCAN_DUAL)
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
