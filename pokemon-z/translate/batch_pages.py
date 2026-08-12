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

`--npc`를 붙이면 사정권이 **이름표 없는 컷신·대화**(Z-4 3갈래)로 바뀐다 — 이름표가
한 줄도 없는 페이지의 스프라이트 귀속(how='그림') 행만 담고, 화자·말투는 페르소나표
(sprite 키)가 정본이다. 산출은 batch/npc[-pilot]-chunks.jsonl · batch/npc-out[-pilot]/.
페르소나표에 없는 스프라이트(포켓몬 번호·연출물)는 행째 빠진다 — 그 수는 plan이 찍는다.

산출: batch/page-out[-pilot]/<cid>.jsonl — {"id","who","es","old","new","ok","why"}
"""

import collections
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
LEDGER = HERE.parent / "docs" / "ledger"   # 판정 대장 (glossary·voices)
sys.path.insert(0, str(HERE))
import mapname  # noqa: E402
from mend_newlines import mend  # noqa: E402
from pilot_npc import ask_npc, key_of, npc_line  # noqa: E402
from validate import check  # noqa: E402

ATTR = HERE / "data/speaker-attr.jsonl.gz"
ANON = HERE / "data/2026-08-06-anon-speakers.jsonl"
APPROVED = HERE / "data/approved-lines.jsonl"
PERSONAS = HERE / "persona-table.jsonl"     # 무태그 NPC 페르소나표(스프라이트 단위)
PROMPTS = HERE / "voice-prompts.jsonl"      # 프롬프트에 실리는 말투 정본
PROTECTED = HERE / "data/protected.jsonl"
MAPS = HERE / "ko" / "00-maps.jsonl"
BATCH = HERE / "batch"
from batch import MODEL  # 백엔드 전환(Z_BACKEND)을 한 곳에서
PAGE_CAP = 90          # 실측: 확정 페이지 835개 중 이 값을 넘는 페이지가 없다
PILOT_PAGES = 20
PILOT_MAP_MAX = 90     # 파일럿은 초반부에서만 뽑는다 — 유지자가 판정할 수 있는 구간
PILOT_EXTRA = ()              # 초반부 밖이라도 꼭 넣을 장면
# 지정 파일럿 표본 — 있으면 이것만 뽑는다. 3차(2026-08-06): 1·2차와 안 겹치는
# 초반 일곱 장면 107행(남은 미판정 장면이 이게 전부다). 2차 표본은 pilot2-chunks.jsonl.
PILOT2 = ("p024-43-0", "p024-51-0", "p025-20-0", "p036-45-0", "p040-17-0",
          "p061-6-1", "p075-1-0")

# 화자로 잡히지만 사람 말이 아닌 이름표 (안내판·표지·트레이너 팁 따위)
SYS = {"PISTA DE ENTRENADOR", "Notas del Team Azoth", "\\PN", "AVISO", "Oeste",
       "Sur", "Este", "Norte", "Movimientos de patada", "Movimientos de viento",
       "ATENCIÓN", "Gran Hotel Luminalia", "1ºRegente",
       "Contrincante"}   # 블랙잭 미니게임의 진행 문구다 — 사람 대사가 아니다
# 유지자가 어투를 이미 확정한 인물 — 재번역이 덮으면 안 된다
VOICE_FIXED = {"Barquero", "Zafra", "Núbila", "Camarero",
               "cocineroOW"}   # 요리사 — 사프라와 같은 자리에서 함께 판정됐다


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
    """voices.md의 표에서 한국어 이름 → 말투 셀.

    표가 두 가지다 — 인물표는 「이름|행수|소개|말투」 넉 칸, 집단 화자표는
    「태그|말투」 두 칸. **두 칸짜리를 안 읽으면 총사·아조스단 신병·경관처럼
    자주 나오는 화자가 통째로 빠진다**(2026-08-06 실측).
    """
    table = {}
    for line in (LEDGER / "voices.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        name = cells[1] if len(cells) > 2 else ""
        if not name or name in ("인물", "갈래", "태그") or set(name) <= set("-"):
            continue
        if len(cells) >= 5 or len(cells) == 4:
            table[name] = cells[-2]
    return table


MAPCOND = re.compile(r"\[맵(<|>=)(\d+)\]\s*")


def resolve_conditions(text, map_id):
    """`[맵<147] …` / `[맵>=147] …` 절을 **그 장면에 맞는 것만** 남긴다.

    받는 쪽은 이야기의 전후를 모른다 — 「맵147 이후로는 반말」이라고 적어 봐야
    지금이 그 뒤인지 알 수 없다. 조건은 여기서 풀어서 해당 절만 보낸다.
    """
    out = []
    for part in re.split(r"(?=\[맵)", text):
        m = MAPCOND.match(part)
        if not m:
            out.append(part)
            continue
        op, n = m.group(1), int(m.group(2))
        if (map_id < n) if op == "<" else (map_id >= n):
            out.append(part[m.end():])
    return re.sub(r"\s{2,}", " ", "".join(out)).strip()


def voice_prompts():
    """프롬프트에 실리는 말투 정본. 없으면 말투표에서 뽑아 쓴다(과도기)."""
    if not PROMPTS.exists():
        return {}
    out = {}
    for line in PROMPTS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["name"]] = r
    return out


def personas():
    """스프라이트 → 페르소나표 행. 말투 지시가 아예 없는 조연에게 쓰는 보충이다.

    사람 NPC 스프라이트 64종만 올라 있다는 점이 그대로 안전장치다. 화살표
    (`flecha`)나 포켓몬 번호(`199`·`477`)처럼 사람이 아닌 스프라이트는 표에
    없으니 붙지 않는다 — 2026-08-06 실측에서 Bruja의 14행이 `flecha`였다.
    """
    return {r["sprite"]: r for r in
            (json.loads(l) for l in
             PERSONAS.read_text(encoding="utf-8").splitlines() if l.strip())}


def attach_personas(cast, take, names):
    """말투 지시가 빈 화자에게 그 자리의 스프라이트로 페르소나를 얹는다.

    **한 스프라이트를 두 화자가 나눠 쓰면 붙이지 않는다.** 스프라이트는 화자가
    아니라 이벤트 페이지의 속성이라, 한 페이지에서 두 사람이 말하면 둘 다 같은
    값을 받는다(2026-08-06 실측: p331-7-0에서 Briof와 「유죄 판결을 받은 남성」이
    함께 `burguesow`, p327-15-0에서 Druida 1이 대드루이드 피쿠스의 스프라이트를
    물려받았다). 후보가 둘 이상인 화자도 마찬가지로 건너뛴다.
    """
    per = personas()
    # 페르소나표가 낡았거나 장면과 안 맞는 화자 — 붙은 17건 전수 검토에서 적발
    # (2026-08-06: 혁명가는 대사가 정중한데 표는 「반말·단호」, 유죄남은 「재산 과시」가
    #  결백 호소 장면과 상충, 나카르는 표가 이전 시점 스냅숏)
    bad = {"Revolucionaria", "유죄 판결을 받은 남성", "나카르", "Nácar"}
    by = defaultdict(set)
    for r, w, _, _ in take:
        by[resolve(w, names)].add(r.get("sprite") or "")
    for x in cast:
        if x["voice"] or x["name"] in bad:
            continue
        cand = {s for s in by[x["name"]] if s in per
                and not any(s in by[o] for o in by if o != x["name"])}
        if len(cand) == 1:
            x["persona"] = npc_line(per[cand.pop()])


def voice_instruction(cell):
    """말투표 셀에서 **지시만** 남긴다.

    표는 사람이 읽는 정본이라 판정 근거·이력이 함께 적힌다. 프롬프트에 그대로
    넣으면 말투보다 역사가 길어진다(2026-08-06: 크리산토 칸 791자 중 지시는 절반).
    규약은 「지시 … 근거: …」 — `근거:` 뒤는 사람 몫이다.
    """
    return strip_evidence(re.split(r"\s*근거:\s*", cell)[0])


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


NUMBERED = re.compile(r"^(아조스단 신병|Recluta Azoth)\s*\d+호?$")


def resolve(who, names):
    """이름표에서 한국어 이름을 찾는다 — 직함이 앞에 붙은 이름표가 흔하다.

    아조스단 신병 1·2·3호는 매번 다른 사람이지만 **말투는 한 벌**이라 이름 하나로
    접는다(유지자 판정 2026-08-06) — 갈라 두면 본보기 풀만 얇아진다.
    """
    if NUMBERED.match(who):
        who = "아조스단 신병"
    if who in names:
        return names[who]
    parts = who.split()
    while len(parts) > 1 and parts[0] in TITLE:
        parts = parts[1:]
        if " ".join(parts) in names:
            return names[" ".join(parts)]
    return who


def approved_set():
    """유지자가 견주어 고른 줄 — 재번역해도 **자동 채택 금지, 반드시 견줘서 고른다.**

    둘이 모여 있다. 2026-08-03 크리산토 블렌드 패스(3단 대조 승인) 439행과,
    2026-08-06 파일럿에서 현행·교정·새번역을 나란히 놓고 고른 366행이다.
    보호(재번역 제외)와는 다르다 — 이 줄은 사정권에 남기되 표시만 달고, 말투
    본보기의 원천이 된다.
    """
    out = set()
    if APPROVED.exists():
        for line in APPROVED.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                out.add((r["map"], fold(r["es"])))
    return out


def approved_samples(limit=5):
    """승인된 줄에서 화자별 **본보기**를 뽑는다.

    말투를 형용사로 설명하면 모델이 한쪽으로 쏠린다(2026-08-06: 어미를 누르면
    평평해지고, 살리라 하면 하게체까지 올라갔다). 이미 승인된 실물을 몇 줄 보여
    주는 편이 어떤 서술보다 정확하다.
    """
    from register import axis
    if not APPROVED.exists():
        return {}
    names = ko_names()
    pool = collections.defaultdict(lambda: collections.defaultdict(list))
    pinned = collections.defaultdict(list)
    for line in APPROVED.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        who = r.get("who")
        if not who or r.get("본보기") is False:      # 손으로 뺀 줄
            continue
        ko = split_head(r["ko"])[1].replace("\n", " ").strip()
        name = resolve(who, names)
        if r.get("본보기") is True:                  # 손으로 박은 줄은 무조건 실린다
            pinned[name].append((axis(ko)[0] or "—", ko))
            continue
        if not (15 <= len(ko) <= 50) or "\\" in ko:
            continue
        pool[name][axis(ko)[0] or "—"].append(ko)

    def score(s):
        """고를 만한 줄인가 — 고유명이 적고 평범한 길이일수록 옮겨 쓰기 좋다."""
        return (s.count("<b>"), abs(len(s) - 30))

    out = {}
    for name in set(pool) | set(pinned):
        picked = list(pinned.get(name, []))
        tails = {p[1][-2:] for p in picked}
        # 존대·하대를 번갈아 뽑고, **어미가 겹치는 줄은 건너뛴다** — 같은 끝을 여러 번
        # 보이면 그 어미로 쏠린다.
        ranked = {ax: sorted(v, key=score) for ax, v in pool.get(name, {}).items()}
        order = ("하대", "존대", "—")
        while len(picked) < limit:
            added = False
            for ax in order:
                for s in ranked.get(ax, []):
                    if s[-2:] in tails:
                        continue
                    picked.append((ax, s))
                    tails.add(s[-2:])
                    ranked[ax].remove(s)
                    added = True
                    break
                if len(picked) >= limit:
                    break
            if not added:
                break
        out[name] = picked[:limit]
    return out


def anon_index():
    """이름표가 「???」인 자리의 판정 — 정체와 말투 지침을 자리(맵:이벤트:페이지:명령)로 건다.

    전수 판정(2026-08-06) 256자리. 「비인물」과 「익명의도」는 정체를 밝히면 안 되는
    자리이므로 이름은 「???」로 두고 지침만 싣는다.
    """
    out = {}
    if not ANON.exists():
        return out
    for line in ANON.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        key = (r["map"], r["event"], r["page"], r["cmd"])
        hide = r.get("판정") in ("비인물", "익명의도")
        out[key] = {"who": "???" if hide else (r.get("정체") or "???"),
                    "hint": r.get("말투지침") or "",
                    "sure": r.get("판정") or ""}
    return out


def pages():
    """이벤트 페이지 → 귀속표 행. 맵 순서·명령 순서를 보존한다."""
    out = defaultdict(list)
    for line in gzip.open(ATTR, "rt", encoding="utf-8"):
        r = json.loads(line)
        out[(r["map"], r["event"], r["page"])].append(r)
    for rows in out.values():
        rows.sort(key=lambda r: r.get("cmd", 0))
    return out


def approved_events():
    """판정이 끝난 이벤트 — 다시 보내지 않는다(유지자 판정 2026-08-06, 승인은 이벤트 단위)."""
    p = HERE / "data/approved-events.jsonl"
    if not p.exists():
        return set()
    return {(json.loads(l)["map"], json.loads(l)["event"])
            for l in p.read_text(encoding="utf-8").splitlines() if l.strip()}


def excluded_pages(pg):
    """재번역이 건드리면 안 되는 페이지 — 보호·승인 이벤트·극초반·인트로."""
    ex = {tuple(json.loads(l)[k] for k in ("map", "event", "page"))
          for l in PROTECTED.read_text(encoding="utf-8").splitlines() if l.strip()}
    done = approved_events()
    for key, rows in pg.items():
        if (key[0], key[1]) in done:                       # 판정 끝난 이벤트
            ex.add(key)
        elif key[0] == 65:                                 # 인트로 맵
            ex.add(key)
        elif key[0] <= 16 and any(r.get("who") in ("Crisanto", "Olivier") for r in rows):
            ex.add(key)                                    # 극초반 유지자 손질 구간
    return ex


def chunks_path(pilot, npc):
    stem = ("npc-pilot-chunks" if npc and pilot else "npc-chunks" if npc
            else "pilot-chunks" if pilot else "page-chunks")
    return BATCH / (stem + ".jsonl")


def plan(pilot=False, npc=False):
    pg = pages()
    ex = excluded_pages(pg)
    ko = ko_index()
    vlines, names, anon = voice_lines(), ko_names(), anon_index()
    approved = approved_set()
    per = personas() if npc else {}
    npc_skipped = 0
    chunks = []
    for key in sorted(pg):
        if key in ex:
            continue
        rows, take = pg[key], []
        if npc and (rows[0].get("scene") not in ("컷신", "대화")
                    or any(x.get("how") == "태그" for x in rows)):
            continue                     # 이름표가 한 줄이라도 있으면 주연 갈래 몫
        for r in rows:
            if npc:
                if r["kind"] != "text" or r["how"] != "그림":
                    continue
                sprite = r.get("sprite") or ""
                if sprite not in per:    # 사람 아님(포켓몬 번호·연출물) 또는 미등재
                    npc_skipped += 1
                    continue
                cur = ko.get((r["map"], fold(r["k"])))
                if cur is None:
                    continue
                take.append((r, sprite, cur, ""))
                continue
            if r["kind"] != "text" or r["how"] not in ("태그", "상속"):
                continue
            who = r.get("who") or ""
            if not who or who in SYS or who in VOICE_FIXED:
                continue
            cur = ko.get((r["map"], fold(r["k"])))
            if cur is None:                                # 정본에 없는 자리
                continue
            hint = ""
            if who == "???":
                a = anon.get((r["map"], r["event"], r["page"], r["cmd"]))
                if a:
                    who = a["who"]
                    hint = a["hint"] + (" [정체 판정: 추정]" if a["sure"] == "추정" else "")
            take.append((r, who, cur, hint))
        if not take:
            continue
        assert len(take) <= PAGE_CAP, f"{key}: {len(take)}행 — 페이지 캡 초과"
        cast, hints = [], {}
        for _, w, _, h in take:
            if h and w not in hints:
                hints[w] = h
        seen_cast = {}
        for who in dict.fromkeys(w for _, w, _, _ in take):
            name = resolve(who, names)
            voice = vlines.get(name, "")
            if hints.get(who):
                voice = (voice + " " if voice else "") + hints[who]
            if name in seen_cast:            # ??? 판정으로 같은 인물이 두 번 서지 않게
                if hints.get(who) and hints[who] not in seen_cast[name]["voice"]:
                    seen_cast[name]["voice"] += " " + hints[who]
                    seen_cast[name]["hint"] = (seen_cast[name].get("hint", "")
                                               + " " + hints[who]).strip()
                continue
            # 익명(???) 자리의 말투지침은 따로도 든다 — 말투 정본에 있는 인물이면
            # scene_header가 voice를 안 읽어서 지침이 버려졌다(2026-08-06 티켓④ 적발)
            seen_cast[name] = {"name": name, "voice": voice,
                               **({"hint": hints[who]} if hints.get(who) else {})}
            cast.append(seen_cast[name])
        if npc:
            for x in cast:               # 스프라이트 페르소나가 곧 말투 정본
                x["voice"] = npc_line(per[x["name"]])
        else:
            attach_personas(cast, take, names)
        m, e, p = key
        chunks.append({
            "cid": f"p{m:03d}-{e}-{p}",
            "map": m, "map_name": mapname.ko(m) or rows[0].get("map_name", ""),
            "event": e, "page": p, "event_name": rows[0].get("event_name", ""),
            "cast": cast,
            "rows": [{"id": f"{m}:{e}:{p}:{r['cmd']}",
                      "who": resolve(w, names), "es": r["k"], "ko": cur,
                      **({"approved": True} if (m, fold(r["k"])) in approved else {})}
                     for r, w, cur, _ in take],
        })

    chunks = dedupe(chunks)
    if pilot:
        chunks = pick_pilot(chunks, npc)
    if npc and npc_skipped:
        print(f"페르소나표 밖 스프라이트로 빠진 행: {npc_skipped} — 사람 스프라이트라면 표에 등재 후 재plan")
    out = chunks_path(pilot, npc)
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


def unified_originals():
    """여러 맵에 복제됐고 현재 전 맵 동일한 원문 — **하나로 관리하는 단위다**.

    Z-28이 통일한 상태의 정의이자 verify `check_unified`가 지키는 불변량. 이 집합은
    맵 경계 너머 한 번만 번역하고, 반영은 전 자리에 퍼진다(apply_verdicts).
    의도된 갈림(data/divergence-allowed.jsonl)은 애초에 「전 맵 동일」이 아니라 안 잡힌다.
    통일판 원장(data/unified-phrases.jsonl) 등재분은 정본이 실수로 갈려 있어도 관리
    단위이므로 합집합으로 든다.
    """
    groups = defaultdict(set)
    seen = defaultdict(set)
    cur = None
    for line in MAPS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if "map" in r:
            cur = r["map"]
            continue
        k = fold(r["k"])
        groups[k].add(r["v"])
        seen[k].add(cur)
    out = {k for k, vs in groups.items() if len(vs) == 1 and len(seen[k]) > 1}
    led = HERE / "data" / "unified-phrases.jsonl"
    if led.exists():
        out |= {json.loads(l)["es"] for l in led.read_text(encoding="utf-8").splitlines()
                if l.strip()}
    return out


def dedupe(chunks):
    """같은 (맵, 원문)은 정본에 **한 줄뿐**이라 한 번만 번역한다.

    남길 자리는 **가장 큰 페이지** — 문맥이 많은 쪽이 판단 재료가 낫다.
    복제가 만드는 여분은 실측 1,730행(전체의 26%)이고, 복제된 자리끼리 화자가
    갈리는 것은 4개뿐이다(셋은 「...」, 하나는 남/여 짝) — 어차피 정본이 한 줄이라
    갈래를 살릴 수도 없다.

    **통일 원문(여러 맵 복제·전 맵 동일)은 맵 경계 너머로도 한 번만 번역한다** —
    자리마다 따로 물으면 통일이 도로 갈라진다(2026-08-12 파일럿 실사고: 27개 맵
    동일하던 「안녕, 후보생!」을 맵68에서만 갈랐다).

    **의도된 갈림도 최소 (화자/원문) 단위로 접는다**(유지자 방침 2026-08-12: 「최소한
    (스프라이트/원문) 단위로」) — 기술 떠올리기 정형구처럼 여러 맵에 복제된 그룹을
    자리마다 물으면 파일럿·전량이 같은 장면 복제로 채워진다. 같은 화자(npc 갈래에선
    스프라이트)의 같은 원문은 한 번만 묻고, 접힌 자리들은 대표 행의 `covers`(맵 목록)
    로 남아 반영 때 함께 간다(apply_verdicts).
    """
    uni = unified_originals()
    best, members = {}, defaultdict(set)
    def key_of_row(c, r):
        kf = fold(r["es"])
        if kf in uni:
            return kf
        return (kf, r.get("who") or c["map"])   # 화자 없는 행만 맵 단위로 남는다
    for c in chunks:
        for r in c["rows"]:
            k = key_of_row(c, r)
            members[k].add(c["map"])
            if k not in best or len(c["rows"]) > best[k][1]:
                best[k] = (c["cid"], len(c["rows"]))
    out, seen = [], set()
    for c in chunks:
        rows = []
        for r in c["rows"]:
            k = key_of_row(c, r)
            if best[k][0] != c["cid"] or k in seen:   # 같은 페이지 안의 반복도 한 번만
                continue
            seen.add(k)
            spread = sorted(members[k] - {c["map"]})
            if spread:
                r = {**r, "covers": spread}
            rows.append(r)
        if not rows:
            continue
        keep = {r["who"] for r in rows}
        out.append({**c, "rows": rows,
                    "cast": [x for x in c["cast"] if x["name"] in keep]})
    dropped = sum(len(c["rows"]) for c in chunks) - sum(len(c["rows"]) for c in out)
    print(f"복제 정리: {dropped}행 뺌 · 빈 페이지 {len(chunks) - len(out)}개 뺌")
    return out


def route(c):
    """이 장면을 어느 쪽으로 돌릴 것인가.

    승인 줄이 있는 장면은 이미 유지자가 견주어 고른 자리라 **교정판(A)**으로 —
    현행을 재료로 어긋난 데만 고친다. 손 안 탄 장면은 **새 번역(B)**이 낫다
    (2026-08-06 파일럿 판정: 승인 줄이 모인 장면에서는 A가 전반적으로 나았다).
    """
    return "a" if any(r.get("approved") for r in c["rows"]) else "b"


def pick_pilot(chunks, npc=False):
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
    if not npc:                      # 지정 표본은 주연 파일럿 회차의 것 — npc 갈래는 안 탄다
        if PILOT2:                   # 지정 표본이 있으면 그것만
            byid = {c["cid"]: c for c in chunks}
            return [byid[cid] for cid in PILOT2 if cid in byid]
        for cid in PILOT_EXTRA:      # 유지자가 지정한 장면
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
  modernize. French/Russian exclamations stay Latin (Mon Dieu!, Sacrebleu!,
  Merci beaucoup!, Blyat); phrases woven into the sentence (a mid-sentence
  s'il vous plait) are translated. Address titles are transliterated:
  monsieur→무슈, madame→마담, mademoiselle→마드모아젤. Italian `Mamma mia`→「맘마미아」.
- máscara → 마스크 (not 가면).
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
TERM_SECTIONS = ("## 고정 용어표", "### 2026-08-05 판정", "### 2026-08-06 판정")
TERMS = HERE / "term-pairs.jsonl"      # 프롬프트에 실리는 용어 정본 — glossary.md는 사람용


def term_pairs():
    """프롬프트에 실리는 (원문, 표기) 쌍. 정본은 term-pairs.jsonl.

    voice-prompts와 같은 갈래다 — md는 근거·이력이 붙는 사람용 문서고, 기계는
    표를 md에서 캐다가 짝이 밀리는 사고를 냈다(2026-08-06 「Team Azoth 미탑재」).
    새 판정은 두 곳에 다 적는다. 파일이 없으면 md 파싱으로 돌아간다(과도기).
    """
    if TERMS.exists():
        return [(r["es"], r["ko"]) for r in
                (json.loads(l) for l in TERMS.read_text(encoding="utf-8").splitlines()
                 if l.strip())]
    return _term_pairs_md()


def _term_pairs_md():
    pairs, on = [], False
    for line in (LEDGER / "glossary.md").read_text(encoding="utf-8").splitlines():
        if line.startswith(("#", "##", "###")):
            on = line.startswith(TERM_SECTIONS)
        if not on or not line.startswith("|"):
            continue
        # 표가 「원문|표기 | |원문|표기」꼴이라 빈 칸이 자리를 가른다 — 빈 칸으로 끊어서
        # 짝을 맞춘다. 예전엔 짝수/홀수 칸으로 잘라 한 칸씩 밀렸고, 그 바람에
        # 「Team Azoth → 아조스단」이 프롬프트에 한 번도 실리지 않았다(2026-08-06 실측).
        cells = [c.strip() for c in line.strip("|").split("|")]
        group = []
        for cell in cells + [""]:
            if not cell:
                if len(group) >= 2:
                    a, b = group[0], group[1]
                    if a not in ("원문", "표기", "근거") and not set(a) <= set("-") \
                            and len(a) < 40:
                        ko = re.sub(r"\s*\([^)]{12,}\)", "", strip_evidence(b))
                        ko = re.split(r"\s+—\s+", ko)[0]
                        ko = re.sub(r"\*\*", "", ko).strip("* ")   # 뒤에 붙은 근거·강조 표시를 뗀다
                        if ko:
                            pairs.append((a, ko))
                group = []
            else:
                group.append(cell)
    return pairs


def ledger_pairs():
    """고유명 표기표 — 이 장면에 나오는 이름을 못박는다.

    셋을 합친다: 고유명 원장(인물·조직) · 지명표(절19) · 맵 이름표(절21).
    **지명도 고유명이다** — 원장에만 기대면 표에 없는 지명이 새 번역에서 다시
    음차된다(2026-08-06 실측: 그리사야시티→그리자유시티 · 비탈 숲→라데라 숲).
    """
    out = []
    for line in (HERE / "canon/names.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out.append((r["es"], r["ko"]))
    for sec in ("19-place-names.jsonl", "21-map-names.jsonl"):
        for line in (HERE / "ko" / sec).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            es, ko = r.get("k") or r.get("es"), r.get("v")
            if es and ko and len(es) < 40:
                out.append((es, ko))
    return out


BOLD = re.compile(r"<b>(.*?)</b>", re.S)
# 줄머리 화자 표기 — 「\c[3]<b>이름:</b>\c[0] 」. 뜻이 없는 장식이라 모델이 잘 흘린다.
HEAD = re.compile(r"^(?:\\c\[\d+\])?<b>[^<]{1,40}:</b>(?:\\c\[\d+\])?\s*")
def strip_fake_head(body, who):
    """모델이 스스로 지어 붙인 화자 표기를 걷어 낸다.

    앞머리를 빼고 보냈는데도 「\\c[3]크리산토:\\c[0] …」처럼 흉내 내는 자리가 있다.
    **그 화자의 이름일 때만** 뗀다 — 「오늘:」 같은 평범한 콜론까지 물면 안 된다.
    """
    m = re.match(r"^(?:\\c\[\d+\])?(?:<b>)?\s*([^<:\n]{1,20}):(?:</b>)?(?:\\c\[\d+\])?\s*", body)
    return body[m.end():] if m and m.group(1).strip() == (who or "").strip() else body


TAGGED = re.compile(r"<(b|i)>(.*?)</\1>", re.S)
INLINE_C = re.compile(r"\\c\[\d+\]")


def unmark(s):
    """서식 태그를 떼고 (민글, 표시목록)으로. 표시목록은 (태그, 속 내용) 순서 그대로."""
    spans = []

    def take(m):
        spans.append((m.group(1), m.group(2)))
        return m.group(2)

    return TAGGED.sub(take, s or ""), spans


def remark(text, spans, pairs):
    """민글에 서식을 도로 입힌다.

    `spans`는 **원문 쪽 표시**(태그, 스페인어 내용)이고 `pairs`는 이 장면의 표기표
    (스페인어 → 한국어)다. 각 표시의 한국어를 글에서 찾아 앞에서부터 한 번씩 감싼다.
    못 찾은 표시는 건너뛴다 — 억지로 끼우면 엉뚱한 자리를 감싼다.
    """
    out, at = text, 0
    for tag, es in spans:
        # 후보를 순서대로 본다 — 표기표의 한국어, 그리고 **원문 그대로**. 옮기지 않고
        # 남겨 둔 삽입구(`S'il vous plait`·`*Ejem*`)는 표기표를 따라가면 못 찾는다.
        cands = [pairs.get(es.strip()), pairs.get(es.strip().rstrip(":")), es.strip()]
        i, ko = -1, None
        for cand in cands:
            if not cand:
                continue
            i = out.find(cand, at)
            if i < 0:
                i = out.find(cand)
            if i >= 0:
                ko = cand
                break
        if ko is None:
            continue
        out = out[:i] + f"<{tag}>{ko}</{tag}>" + out[i + len(ko):]
        at = i + len(ko) + len(tag) * 2 + 5
    return out


def split_head(s):
    """줄머리 화자 표기를 떼어 (앞머리, 본문)으로. 없으면 앞머리는 빈 문자열."""
    m = HEAD.match(s or "")
    return (m.group(0), s[m.end():]) if m else ("", s or "")
TITLES = [("monsieur", "무슈"), ("madame", "마담"), ("mademoiselle", "마드모아젤"),
          ("profesora", "교수"), ("profesor", "교수"), ("maese", "선생"),
          ("capitán", "대장"), ("capitana", "대장"), ("regente", "섭정")]


def scene_names(rows):
    """이 장면에 나오는 고유명을 **현행 번역에서 직접 짝지어** 캔다.

    원장·용어집만 보면 그 표에 없는 지명·인명이 새 번역에서 새로 음차된다
    (2026-08-06 실측: 「그리사야시티→그리자유시티」·「히소포→이소포」·「비탈 숲→라데라 숲」).
    정본의 굵은 글씨는 이미 원장으로 통일돼 있으므로, 원문과 번역의 <b> 자리를
    순서대로 맞추면 그 장면에 필요한 표기표가 공짜로 나온다. 개수가 다르면 버린다.
    """
    out = {}
    for r in rows:
        es, ko = BOLD.findall(r["es"]), BOLD.findall(r["ko"])
        if len(es) != len(ko):
            continue
        for a, b in zip(es, ko):
            a, b = a.strip(), b.strip()
            if a and b and a != b and not a.endswith(":") and len(a) < 40:
                out.setdefault(a, b)
    return out


def glossary_for(rows):
    """이 장면에 실제로 나오는 용어·고유명만 고른다 — 전문은 9천 자라 매번 실을 것이 못 된다."""
    es_all = " ".join(r["es"] for r in rows).lower()
    ko_all = " ".join(r["ko"] for r in rows)
    hits = []
    for a, b in term_pairs() + ledger_pairs() + list(scene_names(rows).items()):
        keys = [k.strip().lower() for k in re.split(r"[/·]", a) if k.strip()]
        if any(k in es_all for k in keys) or b.split("(")[0].strip() in ko_all:
            hits.append(f"- {a} → {b}")
    for a, b in TITLES:                       # 호칭은 프롬프트 본문에도 있지만 잘 샌다
        if a in es_all:
            hits.append(f"- {a} → {b}")
    return CORE_TERMS + ("\n" + "\n".join(dict.fromkeys(hits)) if hits else "")


def build_prompt(fresh=False):
    """교정판(A)은 현행 번역을 함께 주고, 새로 번역(B)은 안 준다."""
    body = (HERE / "prompt-pages.md").read_text(encoding="utf-8")
    if fresh:
        return body.split("## 시스템 프롬프트 본문 (새로 번역)", 1)[1].split("---", 1)[1]
    return body.split("## 시스템 프롬프트 본문", 1)[1].split("## 시스템 프롬프트 본문 (새로 번역)")[0]


def scene_header(c):
    vp, fallback = voice_prompts(), approved_samples()
    lines = []
    for x in c["cast"]:
        rec = vp.get(x["name"])
        if rec:
            instr = resolve_conditions(rec.get("지시", ""), c["map"])
            if x.get("hint"):                  # 익명 자리 지침은 정본 지시에 덧댄다
                instr = (instr + " " if instr else "") + x["hint"]
            samples = [(s.get("격", "—"), s["글"]) for s in rec.get("본보기", [])]
        else:
            instr = voice_instruction(x["voice"]) if x["voice"] else ""
            samples = fallback.get(x["name"], [])
        lines.append(f"- {x['name']}: "
                     + (instr or x.get("persona")
                        or "not in the style guide — keep the current level"))
        for ax, ex in samples:
            lines.append(f"    · 본보기({ax}): {ex}")
    return (f"Scene: {c['map_name']} (map {c['map']}), event 「{c['event_name']}」\n"
            f"Speakers and how each talks (「본보기」 lines are approved translations — "
            f"match their texture):\n" + "\n".join(lines) + "\n")


def render(c, fresh=False):
    """요청 하나의 시스템 프롬프트 — 본문 + 이 장면의 용어 + 장면 머리말."""
    return (build_prompt(fresh).replace("[용어 규칙 — 장면별 발췌 삽입]",
                                        glossary_for(c["rows"]))
            + "\n\n" + scene_header(c))


def run(pilot=False, limit=None, workers=4, fresh=False, effort="low", npc=False):
    src = chunks_path(pilot, npc)
    base = ("npc-out-pilot" if npc and pilot else "npc-out" if npc
            else "page-out-pilot" if pilot else "page-out")
    out_dir = BATCH / (base + ("-fresh" if fresh else ""))
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
        # 줄머리 화자 표기는 **보내지 않는다** — 색 코드는 뜻이 없어 새로 쓰는 쪽이
        # 잘 흘린다(실측: B 반려 26행 중 9행이 앞머리). 답을 받은 뒤 그대로 도로 붙인다.
        # 서식 태그(<b>·<i>·줄 안 \c[n])도 **보내지 않는다** — 뜻이 없는 자리라 모델이
        # 빠뜨리거나 없던 곳에 새로 붙인다(실측: 새 번역이 「후보생」·「무슈」에 강조를
        # 지어 붙였다). 원문 쪽 표시를 기억해 뒀다가 답에 도로 입힌다.
        scene = dict(scene_names(c["rows"]))
        scene.update({"monsieur": "무슈", "madame": "마담", "mademoiselle": "마드모아젤"})
        heads, marks = {}, {}
        reqrows = []
        for r in c["rows"]:
            he, es = split_head(r["es"])
            hk, ko = split_head(r["ko"])
            heads[r["id"]] = hk or he
            es_plain, es_spans = unmark(es)
            ko_plain, ko_spans = unmark(ko)
            # 표기는 **그 줄 자신의 현행 번역**에서 먼저 가져온다 — 자리 수가 맞으면
            # 순서대로 짝지으면 되고, 장면 표기표는 그것이 어긋날 때의 보조다.
            pairs = dict(scene)
            if len(es_spans) == len(ko_spans):
                pairs.update({a[1].strip(): b[1].strip()
                              for a, b in zip(es_spans, ko_spans)})
            marks[r["id"]] = (es_spans, pairs)
            reqrows.append({"id": r["id"], "who": r["who"], "es": es_plain,
                            **({} if fresh else {"ko": ko_plain})})
        sys_prompt = render(c, fresh)
        (out_dir / (c["cid"] + ".req.json")).write_text(
            json.dumps({"system": sys_prompt, "user": reqrows},
                       ensure_ascii=False, indent=1), encoding="utf-8")
        got, cost = ask_npc(key, MODEL, sys_prompt, reqrows, effort=effort)
        missing = [r for r in reqrows if r["id"] not in got]
        if missing:
            got2, c2 = ask_npc(key, MODEL, sys_prompt, missing, effort=effort)
            got.update(got2)
            cost += c2
        lines, rej = [], 0
        for r in c["rows"]:
            new, why = got.get(r["id"]), None
            if new is not None:
                spans, pairs = marks[r["id"]]
                new = remark(unmark(new)[0], spans, pairs)
                head = heads[r["id"]]
                if head:                       # 떼어 둔 앞머리를 도로 붙인다
                    new = head + strip_fake_head(split_head(new)[1], r["who"])
            if new is None:
                why = "누락"
            else:
                # 개행만 어긋난 자리는 여기서 수선한다 — 검수까지 안 세운다(유지자 2026-08-12).
                # 회차마다 mend_newlines를 따로 돌리는 방식은 빠뜨리기 쉬웠다(3차 실측).
                m = mend(r["ko"], new)
                if m is not None and not check(r["ko"], m, 0):
                    new = m
                bad = check(r["ko"], new, 0)
                if bad:
                    why = "검증:" + bad[0][:40]
            if why:
                rej += 1
            lines.append({"id": r["id"], "who": r["who"], "es": r["es"],
                          "old": r["ko"], "new": new, "ok": not why, "why": why})
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


def report(pilot=False, npc=False):
    src = chunks_path(pilot, npc)
    out_dir = BATCH / ("npc-out-pilot" if npc and pilot else "npc-out" if npc
                       else "page-out-pilot" if pilot else "page-out")
    chunks = {json.loads(l)["cid"]: json.loads(l)
              for l in src.read_text(encoding="utf-8").splitlines() if l}
    md = ["# 재번역 파일럿 — 현행과 신판 나란히", ""]
    tot = same = rej = 0
    for p in sorted(out_dir.glob("*.jsonl")):
        if p.stem not in chunks:     # 선별 산출물(screen*.jsonl)은 장면이 아니다
            continue
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
    # 이 대조표는 회차마다 덮어쓰는 **작업 산출**이라 batch/에 산다 — 기록층(docs/log)은
    # 박제라 덮어쓰는 파일을 두지 않는다(2026-08-11 npc report가 옛 박제를 덮은 사고,
    # 2026-08-12 회차 덮어쓰기 재발로 자리 이동). 박제가 필요하면 회차 결산 때 복사한다.
    dst = BATCH / ("npc-report.md" if npc else "page-report.md")
    md.insert(2, f"행 {tot} · 그대로 둔 행 {same} · 기계 반려 {rej}\n")
    dst.write_text("\n".join(md), encoding="utf-8")
    print(f"{tot}행 (그대로 {same} · 반려 {rej}) → {dst}")


if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = args[0] if args else "plan"
    pilot = "--pilot" in args
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    fresh = "--fresh" in args
    npc = "--npc" in args
    if cmd == "plan":
        plan(pilot, npc)
    elif cmd == "run":
        effort = args[args.index("--effort") + 1] if "--effort" in args else "low"
        run(pilot, limit, fresh=fresh, effort=effort, npc=npc)
    elif cmd == "report":
        report(pilot, npc)
    elif cmd == "samples":
        s = approved_samples()
        who = args[1] if len(args) > 1 and not args[1].startswith("--") else None
        for name in ([who] if who else sorted(s, key=lambda k: -len(s[k]))):
            print(f"— {name}")
            for ax, ex in s.get(name, []):
                print(f"    ({ax}) {ex}")
    else:
        print(__doc__)
