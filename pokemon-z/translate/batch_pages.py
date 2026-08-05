# /// script
# requires-python = ">=3.12"
# ///
"""주연 대사 재번역 배치 — 이벤트 페이지 단위.

`batch_npc.py`와 갈라지는 점 셋:
  1. 대상이 **이름표가 붙거나 물려받은 줄**(주연 대사)이지 무태그 NPC가 아니다.
  2. 화자를 옛 조인표가 아니라 **화자 귀속표**(speaker.py scan 산출)에서 읽는다.
  3. 묶음이 맵+40행이 아니라 **이벤트 페이지 하나**다 — 모델이 장면을 온전히 본다.

    uv run translate/batch_pages.py plan          # 사정권 전량 → batch/page-chunks.jsonl
    uv run translate/batch_pages.py plan --pilot  # 표본 20페이지 → batch/pilot-chunks.jsonl
    uv run translate/batch_pages.py run [--pilot] [--limit N]
    uv run translate/batch_pages.py report [--pilot]   # 원문·현행·신판 나란히 (md)

산출: batch/page-out[-pilot]/<cid>.jsonl — {"id","who","es","old","new","ok","why"}
"""

import gzip
import json
import random
import re
import sys
import threading
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import mapname  # noqa: E402
from pilot_npc import ask_npc, key_of  # noqa: E402
from validate import check  # noqa: E402

ATTR = HERE.parent / "docs/research/speaker-attr.jsonl.gz"
PROTECTED = HERE.parent / "docs/research/protected.jsonl"
MAPS = HERE / "ko" / "00-maps.jsonl"
BATCH = HERE / "batch"
MODEL = "gemini-3.6-flash"
PAGE_CAP = 90          # 실측: 확정 페이지 835개 중 이 값을 넘는 페이지가 없다
PILOT_PAGES = 20
PILOT_MAP_MAX = 90     # 파일럿은 초반부에서만 뽑는다 — 유지자가 판정할 수 있는 구간
PILOT_EXTRA = ("p112-4-0",)   # 초반부 밖이라도 꼭 넣을 장면 (란토 저택 65행 대면)

# 화자로 잡히지만 사람 말이 아닌 이름표 (안내판·표지·트레이너 팁 따위)
SYS = {"PISTA DE ENTRENADOR", "Notas del Team Azoth", "\\PN", "AVISO", "Oeste",
       "Sur", "Este", "Norte", "Movimientos de patada", "Movimientos de viento",
       "ATENCIÓN", "Gran Hotel Luminalia", "1ºRegente"}
# 유지자가 어투를 이미 확정한 인물 — 재번역이 덮으면 안 된다
VOICE_FIXED = {"Barquero", "Zafra", "Núbila", "Camarero"}


def fold(s):
    return re.sub(r"\s+", " ", s or "").strip()


def ko_index():
    """(맵, 접힌 원문) → 현행 번역. 정본이 이 열쇠 모양으로 서 있다."""
    out, cur = {}, None
    for line in MAPS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if "map" in r:
            cur = r["map"]
            continue
        out[(cur, fold(r["k"]))] = r["v"]
    return out


def voice_lines():
    """voices.md 표에서 한국어 인물명 → 말투 셀."""
    table = {}
    for line in (HERE / "voices.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 5 and cells[1] and cells[1] not in ("인물", "갈래", "태그") \
                and not cells[1].startswith("-"):
            table[cells[1]] = cells[-2]
    return table


def ko_names():
    """원문 이름 → 한국어. 고유명 원장이 정본이고 옛 조인표 이름은 보충이다."""
    out = dict(json.loads((HERE / "names.json").read_text(encoding="utf-8"))["names"])
    for line in (HERE / "canon/names.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["es"]] = r["ko"]
    return out


TITLE = ("Capitán", "Capitana", "Alcaide", "Archidruida", "Enfermera", "Enfermero",
         "Teniente", "Maese", "Profesora", "Profesor", "Doctor", "Doctora", "Rey",
         "Reina", "Recluta", "Sargento", "General", "Legislador", "Regente")


def resolve(who, names):
    """이름표에서 한국어 이름을 찾는다 — 직함이 앞에 붙은 이름표가 흔하다."""
    if who in names:
        return names[who]
    parts = who.split()
    while len(parts) > 1 and parts[0] in TITLE:
        parts = parts[1:]
        if " ".join(parts) in names:
            return names[" ".join(parts)]
    return who


def pages():
    """이벤트 페이지 → 귀속표 행. 맵 순서·명령 순서를 보존한다."""
    out = defaultdict(list)
    for line in gzip.open(ATTR, "rt", encoding="utf-8"):
        r = json.loads(line)
        out[(r["map"], r["event"], r["page"])].append(r)
    for rows in out.values():
        rows.sort(key=lambda r: r.get("cmd", 0))
    return out


def excluded_pages(pg):
    """재번역이 건드리면 안 되는 페이지 — 보호·극초반·인트로."""
    ex = {tuple(json.loads(l)[k] for k in ("map", "event", "page"))
          for l in PROTECTED.read_text(encoding="utf-8").splitlines() if l.strip()}
    for key, rows in pg.items():
        if key[0] == 65:                                   # 인트로 맵
            ex.add(key)
        elif key[0] <= 16 and any(r.get("who") in ("Crisanto", "Olivier") for r in rows):
            ex.add(key)                                    # 극초반 유지자 손질 구간
    return ex


def plan(pilot=False):
    pg = pages()
    ex = excluded_pages(pg)
    ko = ko_index()
    vlines, names = voice_lines(), ko_names()
    chunks = []
    for key in sorted(pg):
        if key in ex:
            continue
        rows, take = pg[key], []
        for r in rows:
            if r["kind"] != "text" or r["how"] not in ("태그", "상속"):
                continue
            who = r.get("who") or ""
            if not who or who in SYS or who in VOICE_FIXED:
                continue
            cur = ko.get((r["map"], fold(r["k"])))
            if cur is None:                                # 정본에 없는 자리
                continue
            take.append((r, who, cur))
        if not take:
            continue
        assert len(take) <= PAGE_CAP, f"{key}: {len(take)}행 — 페이지 캡 초과"
        cast = []
        for who in dict.fromkeys(w for _, w, _ in take):
            name = resolve(who, names)
            cast.append({"name": name, "voice": vlines.get(name, "")})
        m, e, p = key
        chunks.append({
            "cid": f"p{m:03d}-{e}-{p}",
            "map": m, "map_name": mapname.ko(m) or rows[0].get("map_name", ""),
            "event": e, "page": p, "event_name": rows[0].get("event_name", ""),
            "cast": cast,
            "rows": [{"id": f"{m}:{e}:{p}:{r['cmd']}",
                      "who": resolve(w, names), "es": r["k"], "ko": cur}
                     for r, w, cur in take],
        })

    chunks = dedupe(chunks)
    if pilot:
        chunks = pick_pilot(chunks)
    out = BATCH / ("pilot-chunks.jsonl" if pilot else "page-chunks.jsonl")
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in chunks) + "\n",
                   encoding="utf-8")
    n = sum(len(c["rows"]) for c in chunks)
    sizes = sorted(len(c["rows"]) for c in chunks)
    print(f"{len(chunks)}페이지 · {n}행 → {out}")
    print(f"페이지 크기: 중앙 {sizes[len(sizes)//2]}행 · 최대 {sizes[-1]}행 · "
          f"1행짜리 {sum(1 for s in sizes if s == 1)}개")
    cast_n = defaultdict(int)
    for c in chunks:
        for x in c["cast"]:
            cast_n[x["name"]] += 1
    print("화자 상위:", ", ".join(f"{k}({v})" for k, v in
                                sorted(cast_n.items(), key=lambda x: -x[1])[:10]))


def dedupe(chunks):
    """같은 (맵, 원문)은 정본에 **한 줄뿐**이라 한 번만 번역한다.

    남길 자리는 **가장 큰 페이지** — 문맥이 많은 쪽이 판단 재료가 낫다.
    복제가 만드는 여분은 실측 1,730행(전체의 26%)이고, 복제된 자리끼리 화자가
    갈리는 것은 4개뿐이다(셋은 「...」, 하나는 남/여 짝) — 어차피 정본이 한 줄이라
    갈래를 살릴 수도 없다.
    """
    best = {}
    for c in chunks:
        for r in c["rows"]:
            k = (c["map"], fold(r["es"]))
            if k not in best or len(c["rows"]) > best[k][1]:
                best[k] = (c["cid"], len(c["rows"]))
    out, seen = [], set()
    for c in chunks:
        rows = []
        for r in c["rows"]:
            k = (c["map"], fold(r["es"]))
            if best[k][0] != c["cid"] or k in seen:   # 같은 페이지 안의 반복도 한 번만
                continue
            seen.add(k)
            rows.append(r)
        if not rows:
            continue
        keep = {r["who"] for r in rows}
        out.append({**c, "rows": rows,
                    "cast": [x for x in c["cast"] if x["name"] in keep]})
    dropped = sum(len(c["rows"]) for c in chunks) - sum(len(c["rows"]) for c in out)
    print(f"복제 정리: {dropped}행 뺌 · 빈 페이지 {len(chunks) - len(out)}개 뺌")
    return out


def pick_pilot(chunks):
    """표본 20페이지 — 초반부에서, 말투표가 실리는 장면으로, 화자를 골고루.

    초반부만 뽑는 이유는 유지자가 실제로 지나온 구간이라야 판정할 수 있어서다
    (진행 순서의 대용은 맵 번호 — 조사에서 순위상관 0.988).
    """
    random.seed(20260806)
    pool = [c for c in chunks
            if len(c["rows"]) >= 5
            and c["map"] <= PILOT_MAP_MAX
            and any(x["voice"] for x in c["cast"])]   # 말투표가 실리는 장면
    by_lead = defaultdict(list)
    for c in pool:
        by_lead[c["cast"][0]["name"]].append(c)
    for v in by_lead.values():
        random.shuffle(v)
    picked, used_ev, leads = [], set(), sorted(by_lead, key=lambda k: -len(by_lead[k]))
    while len(picked) < PILOT_PAGES and any(by_lead.values()):
        for lead in leads:                            # 화자 한 명씩 돌아가며 한 장면
            if len(picked) >= PILOT_PAGES:
                break
            while by_lead[lead]:
                c = by_lead[lead].pop()
                if (c["map"], c["event"]) in used_ev:
                    continue
                used_ev.add((c["map"], c["event"]))
                picked.append(c)
                break
    for cid in PILOT_EXTRA:          # 유지자가 지정한 장면 (2026-08-06: 란토 저택 대면)
        c = next((x for x in chunks if x["cid"] == cid), None)
        if c and c not in picked:
            picked.append(c)
    return sorted(picked, key=lambda c: (c["map"], c["event"], c["page"]))


# 언제나 실리는 핵심 규칙 — 용어집에서 근거·이력을 뺀 뼈대만
CORE_TERMS = """\
- Never touch proper nouns: person, place, species, move, item and ability names keep
  their current Korean spelling even if the transliteration looks odd.
- damage is 「데미지」 (not 대미지). Franchise vocabulary: 배틀 · 트레이너 · 체육관 ·
  기술머신 · 몬스터볼 · 도감. Status: 독/맹독/화상/마비/잠듦/얼음.
- The currency pokécuartos/pokéfrancos is 「포켓프랑」.
- Setting is monarchic Kalos: keep rank address (폐하·전하·경·마담·무슈); do not
  modernize. French/Russian interjections stay (Merci beaucoup, Mon coeur, Blyat);
  but address titles are transliterated: monsieur→무슈, madame→마담,
  mademoiselle→마드모아젤. Italian `Mamma mia`→「맘마미아」.
- Kill translationese: 「~에 대해」→ object particle; 「~하는 것이 가능하다」→
  「~할 수 있다」; no double passive 「~되어진다」; ¡Qué …! becomes 「정말 ~구나!」
  not 「얼마나 ~한가!」."""

# 괄호 안이 **짧고** 판정 이력으로만 이뤄진 것만 뗀다. 길게 물면 지시까지 먹는다
# (실측 사고: 크리산토 셀에서 「반말은 …에게만 쓴다」가 통째로 지워졌다).
EVIDENCE = re.compile(r"\((?=[^()]{0,60}\))[^()]*?"
                      r"(?:20\d\d-\d\d-\d\d|사용자 판정|실측|추정)[^()]*\)")


def strip_evidence(s):
    """말투표·용어표 셀에서 판정 이력 괄호만 뗀다 — 모델에게 필요한 것은 지시뿐이다."""
    prev = None
    while prev != s:
        prev, s = s, EVIDENCE.sub("", s)
    return re.sub(r"\s{2,}", " ", s).replace(" .", ".").strip(" ·—")


# 용어 쌍을 캘 절 — 다른 표(지명 대조 따위)는 칸 구성이 달라 잘못 읽힌다
TERM_SECTIONS = ("## 고정 용어표", "### 2026-08-05 판정")


def term_pairs():
    """용어집의 용어표 절에서 (원문, 표기) 쌍. 표기 칸의 근거 괄호는 뗀다."""
    pairs, on = [], False
    for line in (HERE / "glossary.md").read_text(encoding="utf-8").splitlines():
        if line.startswith(("#", "##", "###")):
            on = line.startswith(TERM_SECTIONS)
        if not on or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        for a, b in zip(cells[::2], cells[1::2]):
            if not a or not b or a in ("원문", "---") or set(a) <= set("-"):
                continue
            ko = strip_evidence(b).strip("*")
            if ko and len(a) < 40:
                pairs.append((a, ko))
    return pairs


def glossary_for(rows):
    """이 장면에 실제로 나오는 용어만 고른다 — 전문은 9천 자라 요청마다 실을 것이 못 된다."""
    es_all = " ".join(r["es"] for r in rows).lower()
    ko_all = " ".join(r["ko"] for r in rows)
    hits = []
    for a, b in term_pairs():
        keys = [k.strip().lower() for k in re.split(r"[/·]", a) if k.strip()]
        if any(k in es_all for k in keys) or b.split("(")[0].strip() in ko_all:
            hits.append(f"- {a} → {b}")
    return CORE_TERMS + ("\n" + "\n".join(dict.fromkeys(hits)) if hits else "")


def build_prompt():
    body = (HERE / "prompt-pages.md").read_text(encoding="utf-8")
    return body.split("## 시스템 프롬프트 본문", 1)[1]


def scene_header(c):
    cast = "\n".join(
        f"- {x['name']}: {strip_evidence(x['voice']) if x['voice'] else 'not in the style guide — keep the current level'}"
        for x in c["cast"])
    return (f"Scene: {c['map_name']} (map {c['map']}), event 「{c['event_name']}」\n"
            f"Speakers and how each talks:\n{cast}\n")


def render(c):
    """요청 하나의 시스템 프롬프트 — 본문 + 이 장면의 용어 + 장면 머리말."""
    return (build_prompt().replace("[용어 규칙 — 장면별 발췌 삽입]",
                                   glossary_for(c["rows"]))
            + "\n\n" + scene_header(c))


def run(pilot=False, limit=None, workers=4):
    src = BATCH / ("pilot-chunks.jsonl" if pilot else "page-chunks.jsonl")
    out_dir = BATCH / ("page-out-pilot" if pilot else "page-out")
    out_dir.mkdir(parents=True, exist_ok=True)
    chunks = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l]
    pending = [c for c in chunks if not (out_dir / (c["cid"] + ".jsonl")).exists()]
    if limit:
        pending = pending[:limit]
    print(f"대기 {len(pending)}/{len(chunks)}페이지 · {sum(len(c['rows']) for c in pending)}행")
    key = key_of()
    lock = threading.Lock()
    st = {"n": 0, "rows": 0, "cost": 0.0, "rej": 0}

    def work(c):
        reqrows = [{"id": r["id"], "who": r["who"], "es": r["es"], "ko": r["ko"]}
                   for r in c["rows"]]
        sys_prompt = render(c)
        got, cost = ask_npc(key, MODEL, sys_prompt, reqrows)
        missing = [r for r in reqrows if r["id"] not in got]
        if missing:
            got2, c2 = ask_npc(key, MODEL, sys_prompt, missing)
            got.update(got2)
            cost += c2
        lines, rej = [], 0
        for r in c["rows"]:
            new, why = got.get(r["id"]), None
            if new is None:
                why = "누락"
            else:
                bad = check(r["ko"], new, 0)
                if bad:
                    why = "검증:" + bad[0][:40]
            if why:
                rej += 1
            lines.append({"id": r["id"], "who": r["who"], "es": r["es"],
                          "old": r["ko"], "new": new if not why else None,
                          "ok": not why, "why": why})
        (out_dir / (c["cid"] + ".jsonl")).write_text(
            "\n".join(json.dumps(x, ensure_ascii=False) for x in lines) + "\n",
            encoding="utf-8")
        with lock:
            st["n"] += 1
            st["rows"] += len(lines)
            st["cost"] += cost
            st["rej"] += rej
            print(f"[{st['n']}/{len(pending)}] {c['cid']} {len(lines)}행 "
                  f"누적 {st['rows']}행 반려 {st['rej']} ${st['cost']:.3f}")

    threads = []
    for c in pending:
        while sum(t.is_alive() for t in threads) >= workers:
            time.sleep(0.2)
        t = threading.Thread(target=work, args=(c,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    print(f"끝. {st['rows']}행 · 반려 {st['rej']} · 실비용 ${st['cost']:.3f}")


def report(pilot=False):
    src = BATCH / ("pilot-chunks.jsonl" if pilot else "page-chunks.jsonl")
    out_dir = BATCH / ("page-out-pilot" if pilot else "page-out")
    chunks = {json.loads(l)["cid"]: json.loads(l)
              for l in src.read_text(encoding="utf-8").splitlines() if l}
    md = ["# 재번역 파일럿 — 현행과 신판 나란히", ""]
    tot = same = rej = 0
    for p in sorted(out_dir.glob("*.jsonl")):
        c = chunks[p.stem]
        md += [f"## {c['map_name']}(맵{c['map']}) · 이벤트 「{c['event_name']}」 — `{p.stem}`", "",
               "화자: " + " · ".join(x["name"] for x in c["cast"]), "",
               "| 화자 | 원문 | 현행 | 신판 |", "|---|---|---|---|"]
        for line in p.read_text(encoding="utf-8").splitlines():
            d = json.loads(line)
            tot += 1
            new = d["new"]
            if not d["ok"]:
                rej += 1
                new = f"⚠ {d['why']}"
            elif new == d["old"]:
                same += 1
                new = "(그대로)"
            cell = lambda s: (s or "").replace("|", "\\|").replace("\n", "<br>")
            md.append(f"| {d['who']} | {cell(d['es'])} | {cell(d['old'])} | {cell(new)} |")
        md.append("")
    dst = HERE.parent / "docs/research/2026-08-06-retranslate-pilot.md"
    md.insert(2, f"행 {tot} · 그대로 둔 행 {same} · 기계 반려 {rej}\n")
    dst.write_text("\n".join(md), encoding="utf-8")
    print(f"{tot}행 (그대로 {same} · 반려 {rej}) → {dst}")


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else "plan"
    pilot = "--pilot" in args
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    if cmd == "plan":
        plan(pilot)
    elif cmd == "run":
        run(pilot, limit)
    elif cmd == "report":
        report(pilot)
    else:
        print(__doc__)
