import json
from pathlib import Path

SRC_RANK = {"za": 0, "sv": 1, "la": 2, "swsh": 3, "lgpe": 4, "usum": 5, "sm": 6, "oras": 7, "xy": 8}
SCRATCH = Path("/tmp/claude-1000/-home-durumii-workspace-claude-native-pokemon-fangame-kr/1ccee530-bae2-4a7c-ae3e-e56f04e9fdb0/scratchpad")

# 뜻이 다른 동형(보조용언/의존명사 결합, 관용구) — 코퍼스 세대로 판정할 대상이 아니다.
# 표기A 문자열 기준으로 표시. 판단 근거는 최종 보고에 병기.
AMBIGUOUS = {
    "수없이": "수없이(부사,무수히) vs 수 없이(~할 방법이 없이) — 예시 제시된 유형",
    "못하는": "못하다(서투르다/불가) vs 못 하다(부정+하다) — 예시 제시된 유형",
    "못해!": "못하다 vs 못 하다",
    "못했을": "못하다 vs 못 하다",
    "못했거든.": "못하다 vs 못 하다",
    "못하겠어.": "못하다 vs 못 하다",
    "못하게": "못하다 vs 못 하다 — 예시 제시된 유형",
    "못하고": "못하다 vs 못 하다",
    "앞에서": "~에서(장소 조사, 있다) vs ~에 서다(서 있다) — 예시 제시된 유형(위에서/위에 서 있다)",
    "땅에서": "~에서 vs ~에 서다",
    "편에서": "~에서 vs ~에 서다",
    "자리에서": "~에서 vs ~에 서다",
    "옆에서": "~에서 vs ~에 서다",
    "위에서": "~에서 vs ~에 서다 — 예시 제시된 유형",
    "제목이": "제목(title,명사) vs 제 목이(나의 목+주격) — 전혀 다른 뜻",
    "제정신이": "제정신(이성) vs 제 정신(그의 정신) — 예시 제시된 유형",
    "제작은": "제작(production,명사) vs 제 작은(나의 작은) — 전혀 다른 뜻",
    "만드는데": "~는데(연결어미) vs ~는 데(의존명사,장소/일)",
    "하는데": "~는데(연결어미) vs ~는 데(의존명사)",
    "두는데": "~는데(연결어미) vs ~는 데(의존명사)",
    "볼일이": "볼일(용무,명사) vs 볼 일(볼+의존명사 일) — 문맥별 뜻 갈림",
    "이상할": "이상하다(형용사,strange) vs 이상+할(그 이상을 하다) — 조각 추출 의심",
    "지금이": "지금+이(주격조사) vs 지금 이(관형사+지시대명사) — 조각 추출 의심",
    "사실이": "사실+이(주격조사) vs 사실 이(부사+지시대명사) — 조각 추출 의심",
    "아이가": "아이+가(주격조사) vs 아이 가(동사 가- 명령형?) — 조각 추출 의심",
    "이상이": "이상+이(주격조사) vs 이상 이(관형사+지시대명사) — 조각 추출 의심",
    "내일은": "내일(tomorrow) vs 내 일은(나의 일) — 전혀 다른 뜻",
}

def load_raw():
    return [json.loads(l) for l in (SCRATCH / "z70_raw_counts.jsonl").read_text(encoding="utf-8").splitlines()]

def latest_gen(counts):
    """counts: {src:int}. Returns (best_src, best_rank) or (None, None) if empty."""
    present = [(SRC_RANK[s], s) for s, c in counts.items() if c > 0 and s in SRC_RANK]
    if not present:
        return None, None
    present.sort()
    return present[0][1], present[0][0]

def main():
    raw = load_raw()
    out = []
    stats = {"채택O": 0, "고칠줄합": 0, "근거없음": [], "동세대공존": [], "오탐": []}
    for r in raw:
        a, b = r["표기A"], r["표기B"]
        ca, cb = r["A_세대별횟수"], r["B_세대별횟수"]
        rec = {"표기A": a, "표기B": b, "A_세대별횟수": ca, "B_세대별횟수": cb}

        if a in AMBIGUOUS:
            rec["채택안"] = "오탐/보류"
            rec["오탐근거"] = AMBIGUOUS[a]
            rec["정본에서_고칠_줄수"] = None
            rec["고칠_자리"] = None
            stats["오탐"].append(a + " | " + b)
            out.append(rec)
            continue

        gsa, ra = latest_gen(ca)
        gsb, rb = latest_gen(cb)

        if ra is None and rb is None:
            rec["채택안"] = "근거없음"
            rec["정본에서_고칠_줄수"] = None
            rec["고칠_자리"] = None
            stats["근거없음"].append(a + " | " + b)
            out.append(rec)
            continue

        if ra is not None and rb is not None and ra == rb:
            rec["채택안"] = "동세대공존"
            rec["동세대"] = gsa
            rec["정본에서_고칠_줄수"] = None
            rec["고칠_자리"] = None
            stats["동세대공존"].append(f"{a} | {b} (둘 다 {gsa})")
            out.append(rec)
            continue

        # ra < rb means A's best generation is newer (lower rank = newer)
        if ra is not None and (rb is None or ra < rb):
            rec["채택안"] = "표기A"
            fix_locs = r["B출현"]
        else:
            rec["채택안"] = "표기B"
            fix_locs = r["A출현"]
        n_fix = len(fix_locs)
        rec["정본에서_고칠_줄수"] = n_fix
        rec["고칠_자리"] = [{"절": x["절"], "i": x["i"]} for x in fix_locs]
        stats["채택O"] += 1
        stats["고칠줄합"] += n_fix
        out.append(rec)

    with open(SCRATCH / "z70-latestgen.jsonl", "w", encoding="utf-8") as f:
        for rec in out:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("채택 건수:", stats["채택O"], "고칠 줄 합계:", stats["고칠줄합"])
    print("근거없음 건수:", len(stats["근거없음"]))
    for x in stats["근거없음"]:
        print("  -", x)
    print("동세대공존 건수:", len(stats["동세대공존"]))
    for x in stats["동세대공존"]:
        print("  -", x)
    print("오탐/보류 건수:", len(stats["오탐"]))
    for x in stats["오탐"]:
        print("  -", x)
    print("총 검토건수:", len(out))

if __name__ == "__main__":
    main()
