"""Z-71 판정 재반영 v2 — 내용 일치 검증 없이는 한 줄도 안 쓴다.

대상: 행별 판정(B새번역·직접) + 승인 일괄(도감·기술·작은 절). 절23 일괄은 제외(유지자
유보). 제외 명단: 오입력 1 · 분류 제안 결함 2 · 상점 갈래 1.
usage: uv run --with pyyaml python z71_apply2.py [--write]
"""
import json, sys
from pathlib import Path

WRITE = "--write" in sys.argv
sys.path.insert(0, "translate/stage0")

S = Path("/tmp/claude-1000/-home-durumii-workspace-claude-native-pokemon-fangame-kr/e744c036-4496-412f-a1f6-af69b24a4da5/scratchpad")
R = Path("docs/log/research")
EXCLUDE = {"23-script-texts#3454",   # 메모가 문안 칸에 오입력
           "02-kinds#391", "02-kinds#674",  # 제안이 성격명 오매칭 — 현행이 정본
           "23-script-texts#3399",   # 상점 갈래(선택자 트리) — 갈래 창구 몫
           "09-item-descs#452"}      # 판정 문안 = 통일 전 값(2d1cf14 「특수공격」 되돌림)

data = {}
for p in (R/"2026-08-19-z71-preselect-sure.jsonl", R/"2026-08-19-z71-preselect-review.jsonl",
          S/"full-23.jsonl", S/"full-07.jsonl", S/"full-08.jsonl", S/"full-03.jsonl", S/"full-06.jsonl", S/"full-00.jsonl", S/"full-09.jsonl", S/"full-11.jsonl", S/"full-21.jsonl"):
    if p.exists() and p.stat().st_size:
        for l in open(p, encoding="utf-8"):
            r = json.loads(l)
            data.setdefault(r["id"], r)
# 감량 전 전 장면도 데이터 원천(행별 판정 자리의 es/old) — git 판이 이미 full-23에 있고,
# 00-maps 등 맵 절 행 판정은 pairjudge 차선 파일에서 온다
for p in (R/"2026-08-19-z71-pairjudge-변형.jsonl",):
    for l in open(p, encoding="utf-8"):
        r = json.loads(l)
        rid = f"{r['절']}#{r['i']}"
        data.setdefault(rid, {"id": rid, "es": r["원문"], "old": r["현행"], "new": r.get("본가","")})

byid = {}
for l in open("translate/batch/verdicts-z71-canon-review.jsonl", encoding="utf-8"):
    l = l.strip()
    if not l: continue
    try: r = json.loads(l)
    except Exception: continue
    if r.get("id"): byid[r["id"]] = r

brief = json.loads(open("translate/batch/z71-canon-review/brief.json", encoding="utf-8").read())
bulk_ids = set()
for a in brief["asks"]:
    if a["id"] in ("adopt-03-sure", "adopt-06-sure", "adopt-small"):
        bulk_ids |= set(a["rows"])

want = {}   # rid -> (val, 출처)
for rid, v in byid.items():
    if rid in EXCLUDE: continue
    p = v.get("판정", "")
    if p in ("B새번역", "직접") and v.get("텍스트", "").strip():
        want[rid] = (v["텍스트"].strip(), "행별:" + p)
for rid in bulk_ids:
    if rid in EXCLUDE or rid in byid and byid[rid].get("판정"): continue
    r = data.get(rid)
    if r and r["new"] != r["old"]:
        want.setdefault(rid, (r["new"], "일괄"))

# 자리 찾기 — 값-행 색인(표식 제외) + 내용 일치 필수
def value_lines(sec):
    lines = open(f"translate/ko/{sec}.jsonl", encoding="utf-8").read().splitlines()
    out = []
    for phys, l in enumerate(lines):
        row = json.loads(l)
        if "k" in row or "es" in row:
            out.append((phys, row))
    return out

# 행 번호는 출처마다 물리/값-행이 섞여 신뢰 불가(2026-08-19 실측) — 내용이 유일 열쇠다.
cache = {}
edits, fails = [], []
taken = set()          # 같은 물리 줄에 두 판정이 앉지 않게
for rid, (val, srcv) in sorted(want.items()):
    sec, _ = rid.split("#")
    if sec not in cache: cache[sec] = value_lines(sec)
    exp = data.get(rid)
    if not exp:
        fails.append((rid, srcv, "원자료 없음", 0)); continue
    hits = [(phys, row) for phys, row in cache[sec]
            if (row.get("es") or row.get("k")) == exp.get("es") and row.get("v") == exp.get("old")]
    if not hits:
        # 판정 화면의 현행값은 2026-08-17 표기 통일(2d1cf14·eae5fb2) 앞선 스냅샷에서 왔다.
        # 그 드리프트는 공백뿐이므로 공백을 걷고 한 번 더 본다 — 알맹이가 다르면 여전히 보류.
        sp = lambda s: "".join((s or "").split())
        hits = [(phys, row) for phys, row in cache[sec]
                if (row.get("es") or row.get("k")) == exp.get("es")
                and sp(row.get("v")) == sp(exp.get("old"))]
    if not hits:
        fails.append((rid, srcv, "내용 미발견", 0)); continue
    # 복제 쌍(내용 동일 다중 자리)은 같은 값을 전 자리에 — 값이 같으니 안전하다
    for phys, _row in hits:
        key = (sec, phys)
        if key in taken: continue
        taken.add(key)
        edits.append((sec + ".jsonl", phys + 1, val))

print(f"쓰기 대상 {len(edits)} · 검증 실패로 보류 {len(fails)}")
for f in fails[:12]: print("  보류:", f)
from collections import Counter
print("출처:", dict(Counter(s for _, (v, s) in sorted(want.items()) if True)))
if WRITE and edits and not fails:
    from edit import put_lines
    err = put_lines(edits)
    print("결과:", err or "OK")
elif WRITE:
    print("보류가 있어 쓰지 않았다 — 전체 아니면 무")
