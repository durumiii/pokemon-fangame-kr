# /// script
# requires-python = ">=3.12"
# ///
"""전투 종료 대사(how="전투호출") 358좌표의 **사람 판정 재료**를 뽑는다.

    uv run translate/battle_materials.py <나갈 경로.jsonl>

산출은 저장소에 두지 않는다 — 정본이 바뀌면 곧 낡는다. 쓸 때마다 새로 뽑아라.

한 줄 = (맵, 원문) 좌표 하나. 페이지 전문(같은 페이지의 다른 대사 원문·번역)과
화자의 한국어 이름표, 그 화자가 이름표 줄에서 쓰는 말투 표본을 함께 싣는다.
격 검사기(register.py)의 판정은 **싣지 않는다** — 사람이 읽고 판정하는 재료다.
"""
import gzip, json, re, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
T = Path(__file__).resolve().parent
ATTR = T / "data" / "speaker-attr.jsonl.gz"
KO = T / "ko"
TTYPES = Path("/mnt/d/Game/Pokemon Z/V2.18/PBS/trainertypes.txt")

jl = lambda p: [json.loads(l) for l in p.open(encoding="utf-8")]

# 정본 — 맵 절마다 {"map": n, "n": k} 머리 뒤에 k줄
# ⚠ 귀속표의 원문 키는 이벤트에서 온 그대로라 꼬리 공백·줄바꿈이 붙는다. 공백을 접어 맞춘다
#   (접지 않으면 페이지 전문의 156줄이 「정본 없음」으로 잘못 뜬다 — 2026-08-17 실측).
fold = lambda s: re.sub(r"\s+", " ", s).strip()
canon = {}          # (map, 접은 es) -> ko
cur = None
for d in jl(KO / "00-maps.jsonl"):
    if "map" in d and "n" in d:
        cur = d["map"]
    else:
        canon[(cur, fold(d["k"]))] = d["v"]

# 화자 한국어 이름표
ko_cls = {d["i"]: d["v"] for d in jl(KO / "13-trainer-classes.jsonl")}
names = {d["k"]: d["v"] for d in jl(KO / "14-trainer-names.jsonl")}
tcls = {}
if TTYPES.exists():
    for line in TTYPES.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        p = line.split(",")
        if len(p) > 1 and p[0].strip().isdigit():
            tcls[p[1].strip()] = ko_cls.get(int(p[0]), "")

rows = [json.loads(l) for l in gzip.open(ATTR, "rt", encoding="utf-8")]

# 페이지별 대사 차례
pages = defaultdict(list)
for r in rows:
    pages[(r["map"], r["event"], r["page"])].append(r)
for v in pages.values():
    v.sort(key=lambda r: (r["cmd"], r.get("ind", 0)))

# 화자별 이름표 줄(how="태그") 표본 — 그 인물이 평소 어떻게 말하나
tagged = defaultdict(list)
for r in rows:
    if r.get("how") == "태그" and r.get("who"):
        ko = canon.get((r["map"], fold(r["k"])))
        if ko:
            tagged[r["who"]].append(ko)

seen, out = set(), []
for r in rows:
    if r.get("how") != "전투호출":
        continue
    key = (r["map"], r["k"])
    if key in seen:
        continue
    seen.add(key)
    ctx = []
    for q in pages[(r["map"], r["event"], r["page"])]:
        ctx.append({
            "cmd": q["cmd"],
            "화자": q.get("who") or "",
            "근거": q.get("how") or "",
            "es": q["k"],
            "ko": canon.get((q["map"], fold(q["k"])), "(정본 없음)"),
            "이줄": q["k"] == r["k"] and q["cmd"] == r["cmd"],
        })
    samples = tagged.get(r["who"], [])
    out.append({
        "맵": r["map"], "맵이름": r.get("map_name", ""),
        "이벤트": r["event"], "페이지": r["page"], "명령": r["cmd"],
        "화자원문": r.get("who", ""), "직함상수": r.get("tclass", ""),
        "화자": " ".join(filter(None, [tcls.get(r.get("tclass", ""), ""),
                                      names.get(r.get("who", ""), r.get("who", ""))])),
        "장면": r.get("scene", ""), "층": r.get("cls", ""),
        "es": r["k"], "ko": canon.get((r["map"], fold(r["k"])), "(정본 없음)"),
        "이름표표본수": len(samples), "이름표표본": samples[:12],
        "페이지전문": ctx,
    })

out.sort(key=lambda d: (d["화자원문"], d["맵"], d["이벤트"], d["명령"]))
dest = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("battle-materials.jsonl")
with dest.open("w", encoding="utf-8") as f:
    for d in out:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")

print(f"{len(out)}좌표 → {dest} ({dest.stat().st_size:,} bytes)")
print("정본 없음:", sum(1 for d in out if d["ko"] == "(정본 없음)"))
print("이름표 표본 있는 화자의 좌표:", sum(1 for d in out if d["이름표표본수"]))
print("화자 종수:", len({d["화자원문"] for d in out}))
