# /// script
# requires-python = ">=3.12"
# ///
"""NPC 어투 전량 재번역 배치 — 화자 문맥(페르소나/말투표/버킷) 탑재판.

대상: 조인표의 무태그 발화 중 재작성 가치가 있는 행 전량(≈8,100행).
태그 대사·사물지문·선택지·미조인은 건드리지 않는다.

    uv run translate/batch_npc.py plan   # 청크 산출 → batch/npc-chunks.jsonl
    uv run translate/batch_npc.py run    # 실행(재개 가능 — 완료 청크는 건너뜀)
    uv run translate/batch_npc.py apply  # 검증 통과분을 ko/00-maps.jsonl에 반영

산출: batch/npc-out/<cid>.jsonl — {"id","es","old","new","ok","why"}
"""

import gzip
import json
import re
import sys
import threading
import time
import unicodedata
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from batch import worth_rewriting  # noqa: E402
from pilot_npc import ask_npc, build_prompt, key_of, load_personas  # noqa: E402
from validate import check  # noqa: E402

JOIN = HERE.parent / "docs/research/map-speaker-join.jsonl.gz"
CHUNKS = HERE / "batch" / "npc-chunks.jsonl"
OUT = HERE / "batch" / "npc-out"
MODEL = "gemini-3.6-flash"
CHUNK_ROWS = 40

SPK = re.compile(r"^(\\c\[\d+\])?<b>[^<:]{1,40}:</b>")
PERSONS = {"서민", "귀족", "군인", "성직", "학자", "접객", "공연",
           "어린이", "노인", "일반", "적대"}

# 그룹 기본값 (페르소나 없는 롱테일 스프라이트)
GROUP_DEFAULT = {
    "서민": "서민 행인. 허물없는 반말",
    "귀족": "귀족. 정중하지만 오만한 해요체",
    "군인": "군인. 시원시원한 반말, 통보·절차 문장만 합쇼체",
    "성직": "수도자. 경건한 합쇼체",
    "학자": "학자. 반말 기본, 격식 자리만 존대",
    "접객": "접객 직원. 해요체 인사, 절차 안내는 합쇼체",
    "공연": "공연인. 들뜬 해요체",
    "어린이": "아이. 또래엔 반말, 어른에게는 해요체",
    "노인": "노인. 어른말(「~라네」「~단다」)",
    "일반": "마을 행인. 담백한 반말",
    "적대": "불량배·적대 인물. 거친 반말",
}
UNKNOWN_NPC = ("화자 미상(연출·시스템 혼재 구간). 어투를 바꾸지 말고 현행 급을"
               " 유지한 채 직역투·어색한 문장만 다듬어라. 지문은 평서 유지")


def stem(s):
    return re.sub(r"(ow|OW|TS|w)?\d*$", "", s) or "(없음)"


def deacc(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()


def voices_map():
    """voices 그룹 스프라이트 어간 → 한국어 인물명 (names.json 조인)."""
    names = json.loads((HERE / "names.json").read_text(encoding="utf-8"))["names"]
    strip = re.compile(r"(Montado|Montada|Reventada|Caduca|Vestido|Monigote|Pose|"
                       r"Pechamen|Dormido|Final|Salamence|Lira|Capucha|Herido|"
                       r"Cabeza|Borracha|Mapa|Musica|Baln|TS)")
    special = {"az": "AZ", "f3": "F3", "druidaFicus": "대드루이드 피쿠스"}
    out = {}
    groups = json.loads((HERE / "sprite-groups.json").read_text(encoding="utf-8"))["groups"]
    for s in groups["voices"]:
        base = strip.sub("", s)
        if base in special or s in special:
            out[s] = special.get(s, special.get(base))
            continue
        ds = deacc(base)
        hit = next((ko for es, ko in names.items()
                    if deacc(es) == ds or (len(ds) >= 4 and (deacc(es).startswith(ds) or ds.startswith(deacc(es))))), None)
        out[s] = hit
    return out


def voice_lines():
    """voices.md 표에서 인물명 → 말투 셀."""
    table = {}
    for line in (HERE / "voices.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 5 and cells[1] and cells[1] not in ("인물", "갈래", "태그") \
                and not cells[1].startswith("-"):
            table[cells[1]] = cells[-2]
    return table


def npc_of(r, personas, groups_s2g, vmap, vlines):
    s = r["sprite"]
    st = stem(s)
    grp = groups_s2g.get(st)
    if s in personas:
        p = personas[s]
        return f"{p['페르소나']} [어미: {p['버킷']}]"
    if grp == "voices":
        name = vmap.get(st) or vmap.get(s)
        if name and name in vlines:
            return f"명명 인물 「{name}」. 말투: {vlines[name]}"
        return f"명명 인물 「{name or st}」. 기존 어투 급을 유지하고 직역투만 다듬어라"
    if grp in PERSONS:
        return GROUP_DEFAULT[grp]
    return UNKNOWN_NPC


def plan():
    personas = load_personas()
    groups = json.loads((HERE / "sprite-groups.json").read_text(encoding="utf-8"))["groups"]
    s2g = {s: g for g, ss in groups.items() for s in ss}
    vmap, vlines = voices_map(), voice_lines()
    rows = [json.loads(l) for l in gzip.open(JOIN, "rt", encoding="utf-8")]
    target = []
    for r in rows:
        if "sprite" not in r or r.get("kind") != "text":
            continue
        if SPK.match(r["k"]) or not worth_rewriting(r["v"]):
            continue
        grp = s2g.get(stem(r["sprite"]))
        if grp in ("사물지문", "포켓몬특수"):
            continue
        target.append(r)

    # 맵 순서 보존, 이벤트 연속 유지, 40행 캡
    chunks, cur, cur_map = [], [], None
    for r in target:
        if r["map"] != cur_map or len(cur) >= CHUNK_ROWS:
            if cur:
                chunks.append(cur)
            cur, cur_map = [], r["map"]
        cur.append(r)
    if cur:
        chunks.append(cur)

    CHUNKS.parent.mkdir(exist_ok=True)
    with open(CHUNKS, "w", encoding="utf-8") as f:
        for i, ch in enumerate(chunks):
            reqrows = [{"id": f"{r['map']}:{r['event']}:{j}",
                        "npc": npc_of(r, personas, s2g, vmap, vlines),
                        "es": r["k"], "ko": r["v"]}
                       for j, r in enumerate(ch)]
            f.write(json.dumps({"cid": f"n{i:04d}", "rows": reqrows},
                               ensure_ascii=False) + "\n")
    kinds = defaultdict(int)
    for ch in chunks:
        for r in ch:
            g = s2g.get(stem(r["sprite"]))
            kinds["페르소나" if r["sprite"] in personas else
                  ("voices" if g == "voices" else ("미상" if g == "내용판정" else "그룹기본"))] += 1
    print(f"대상 {sum(len(c) for c in chunks)}행 / {len(chunks)}청크 → {CHUNKS}")
    print("문맥 출처:", dict(kinds))


def run(workers=4):
    key = key_of()
    prompt = build_prompt()
    chunks = [json.loads(l) for l in CHUNKS.read_text(encoding="utf-8").splitlines() if l]
    OUT.mkdir(exist_ok=True)
    pending = [c for c in chunks if not (OUT / (c["cid"] + ".jsonl")).exists()]
    print(f"대기 {len(pending)}/{len(chunks)}청크 · {sum(len(c['rows']) for c in pending)}행")
    lock = threading.Lock()
    state = {"rows": 0, "chunks": 0, "cost": 0.0, "rej": 0, "t0": time.time()}

    def work(c):
        got, cost = ask_npc(key, MODEL, prompt, c["rows"])
        missing = [r for r in c["rows"] if r["id"] not in got]
        if missing:
            got2, cost2 = ask_npc(key, MODEL, prompt, missing)
            got.update(got2)
            cost += cost2
        out_rows, rej = [], 0
        for r in c["rows"]:
            new = got.get(r["id"])
            why = None
            if new is None:
                why = "누락"
            else:
                bad = check(r["ko"], new, 0)
                if bad:
                    why = "검증:" + bad[0][:40]
            ok = why is None
            if not ok:
                rej += 1
            out_rows.append({"id": r["id"], "es": r["es"], "old": r["ko"],
                             "new": new if ok else None, "ok": ok, "why": why})
        (OUT / (c["cid"] + ".jsonl")).write_text(
            "\n".join(json.dumps(x, ensure_ascii=False) for x in out_rows) + "\n",
            encoding="utf-8")
        with lock:
            state["rows"] += len(c["rows"])
            state["chunks"] += 1
            state["cost"] += cost
            state["rej"] += rej
            el = time.time() - state["t0"]
            print(f"[{state['chunks']}/{len(pending)}] {state['rows']}행 "
                  f"반려{state['rej']} ${state['cost']:.2f} {el:.0f}s", flush=True)

    import concurrent.futures as cf
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(work, pending))
    print(f"완료: 반려 {state['rej']}행, 비용 ${state['cost']:.2f}")


def apply():
    """검증 통과분을 ko/00-maps.jsonl에 반영 (es키+현행값 일치 행만)."""
    news = {}
    for p in sorted(OUT.glob("n*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            d = json.loads(line)
            if d["ok"] and d["new"] and d["new"] != d["old"]:
                news[(d["es"], d["old"])] = d["new"]
    src = HERE / "ko" / "00-maps.jsonl"
    out_lines, n = [], 0
    for line in src.read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        if "k" in d and (d["k"], d.get("v")) in news:
            d["v"] = news[(d["k"], d["v"])]
            n += 1
        out_lines.append(json.dumps(d, ensure_ascii=False))
    src.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    print(f"반영 {n}행 / 후보 {len(news)}행 (중복 원문은 동일 신판 적용)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    {"plan": plan, "run": run, "apply": apply}[cmd]()
