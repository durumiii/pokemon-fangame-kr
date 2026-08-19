# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml", "rubymarshal"]
# ///
"""전투 종료 대사(customTrainerBattle 둘째 인자) 새 번역 — 절23 추가 키 갈래.

이 대사는 이벤트 스크립트 안의 평문 리터럴이라 `_I()` 포장이 없고, 그래서 어느 절에도
안 담긴다(588호출 · 고유 26문구 · 15파일). 정본 합류 경로는 절23 추가 키(apply=kradd)와
`customTrainerBattle` 머리의 `_INTL` 수술이고, 이 도구는 그 경로에 실을 **번역값만** 낸다.

    uv run translate/batch_endspeech.py plan
    Z_BACKEND=openrouter uv run translate/batch_endspeech.py run [--effort low]

한 요청에 26행을 통째로 담는다(유지자 판정 2026-08-19). 화자가 열두 직군으로 흩어져
있어 **말투 지침은 행마다 실린다** — 행의 `화자`(직함)·`자리`(패배 직후·공용 대사 여부)와
같은 트레이너의 도전 대사 한 벌(`도전`·`도전_ko`)이 격의 근거다.
산출은 `batch/endspeech-out/<cid>.jsonl`.
"""

import concurrent.futures as cf
import json
import re
import sys
import time
import zlib
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "vendor"))
from batch import MODEL  # noqa: E402  (Z_BACKEND 전환을 함께 탄다)
from batch_pages import build_prompt, fold, glossary_for, ko_index  # noqa: E402
from datread import load  # noqa: E402
from mapname import ko as map_ko  # noqa: E402
from pilot_npc import ask_npc, key_of  # noqa: E402

GAME = Path("/mnt/d/Game/Pokemon Z/V2.18")   # probe.py·verify.py와 같은 상수
BATCH = HERE / "batch"
CHUNKS = BATCH / "endspeech-chunks.jsonl"
OUT = BATCH / "endspeech-out"
LOG = BATCH / "log.txt"
CALL = re.compile(r'customTrainerBattle\s*\(\s*\w+\s*,\s*"((?:[^"\\]|\\.)*)"')
MAKE = re.compile(r'createTrainer\(\s*(\d+)\s*,\s*"([^"]*)"')

# 본문(prompt-pages.md 「새로 번역」)은 입력이 한 장면인 것을 전제한다 — 이 요청은 그렇지
# 않으므로 batch_pages의 PACK_NOTE와 같은 자리에서 그 전제만 덮어쓴다.
NOTE = """\
**This request is not a scene.** The user message is a JSON array of unrelated
battle-defeat lines, each spoken by a different kind of trainer somewhere else in
the game. There is no scene header: **every item carries its own speaker
instruction**, and you must read each item's fields before translating it.

Each item is {"id", "who", "es", "자리", "도전", "도전_ko"}:
- `who` — the speaker's trainer class (Korean name, then the Spanish original).
- `자리` — where the line is spoken and how many trainers share it. Lines shared by
  dozens of trainers are stock lines for a whole unit: keep them general, and never
  write anything that fits only one individual.
- `도전` / `도전_ko` — the same trainer's pre-battle challenge line in Spanish and in
  its **approved Korean translation**. This pair is the register anchor: the defeat
  line is the same person speaking moments later, so match the speech level and the
  texture of `도전_ko` unless the item says otherwise.

Because the items are unrelated, never carry context, addressee or speech level
from one item into another.

**These are defeat lines, spoken the instant the trainer loses.** Many of them are
not addressed to the player at all — they are muttering, wailing or a remark to
someone absent. When an item has no listener marker (no 2nd person, no vocative, no
command, no question to the player), do **not** force it to the level of `도전_ko`;
write it as the natural Korean for talking to oneself. Rule C still decides the
level whenever a listener is actually addressed.

`도전_ko` is quoted context, not a template: it may carry `<b>…</b>` tags and a
`이름:` speaker prefix, and **none of that may appear in your output.** Your `es`
lines carry no markup at all, so your Korean must carry none either.

Output remains ONE flat JSON array of {"id", "ko"} covering every item, in the
order given."""


# 본문(prompt-pages.md 「새로 번역」)이 장면 머리를 전제하는 자리 셋.
SWAPS = [
    ('Input is a JSON array; each item is {"id", "who", "es"}. `who` is the\n'
     "speaker's name, `es` is the Spanish source.",
     'Input is a JSON array; each item is {"id", "who", "es", "자리", "도전",\n'
     '"도전_ko"} — the fields are described just below. `es` is the Spanish source.'),
    ("**The items are one complete event page, in game order — a single scene.** A scene\n"
     "header at the end of this prompt lists the speakers present and how each one talks.",
     NOTE),
    ("A. Follow the per-speaker style in the scene header, but **rewrite the sentence",
     "A. Follow each item's own `who` / `자리` / `도전_ko`, but **rewrite the sentence"),
    ("B. **Many characters change speech level by addressee.** When the header gives\n"
     '   branches ("존대 to A, 반말 to B"), decide **who the line is spoken to** from the\n'
     "   scene — the surrounding lines, who answers, what vocative is used. A character\n"
     "   who turns to a different listener changes level mid-scene.",
     "B. **Many characters change speech level by addressee.** Decide **who each line is\n"
     "   spoken to** — the defeated trainer may be talking to the player, to their own\n"
     "   Pokémon, to an absent superior, or to nobody. The listener decides the level,\n"
     "   and `도전_ko` only tells you how this speaker talks to the player."),
]


def _sections():
    for sec in load(open(GAME / "Data/Scripts.rxdata", "rb")):
        yield (bytes(sec[1]).decode("utf-8", "replace"),
               zlib.decompress(bytes(sec[2])).decode("utf-8", "replace"))


def class_names():
    """트레이너 직함 id → (한국어, 스페인어). PBS는 읽기만 한다(고치면 dat가 다시 구워진다)."""
    ko = {}
    for line in (HERE / "ko/13-trainer-classes.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            ko[r["i"]] = (r["v"], r.get("es") or r["v"])
    return ko


def b2s(v):
    return bytes(v).decode("utf-8", "replace") if isinstance(v, (bytes, bytearray)) else str(v)


def pages():
    """(파일명, 맵번호, 이벤트명, 페이지, 명령목록) — 맵과 공통 이벤트 전부."""
    files = sorted(p for p in (GAME / "Data").glob("Map[0-9]*.rxdata"))
    for f in files + [GAME / "Data/CommonEvents.rxdata"]:
        d = load(open(f, "rb"))
        if f.name.startswith("Map"):
            m = int(f.stem[3:])
            for _, e in d.attributes["@events"].items():
                for i, p in enumerate(e.attributes["@pages"]):
                    yield f.name, m, b2s(e.attributes["@name"]), i, p.attributes["@list"]
        else:
            for ce in d:
                if ce is not None:
                    yield f.name, 0, b2s(ce.attributes["@name"]), 0, ce.attributes["@list"]


def scan():
    """고유 원문 → {직함 id, 트레이너 이름 수, 파일, 호출 수, 도전 대사 후보}."""
    info = defaultdict(lambda: {"cls": set(), "names": set(), "files": set(),
                                "calls": 0, "pre": []})
    for fname, mapno, _ev, _pi, lst in pages():  # noqa
        msgs, scripts, buf = [], [], []
        for cmd in list(lst) + [None]:
            code = cmd.attributes["@code"] if cmd is not None else 0
            if code == 101:                    # 정본 열쇠는 101+401을 이어 붙인 전문이다
                msgs.append(b2s(cmd.attributes["@parameters"][0]))
            elif code == 401 and msgs:
                msgs[-1] += "\n" + b2s(cmd.attributes["@parameters"][0])
            if code in (355, 655):
                buf.append(b2s(cmd.attributes["@parameters"][0]))
                continue
            if buf:
                scripts.append("\n".join(buf))
                buf = []
            if code == 111:
                p = cmd.attributes["@parameters"]
                if p and p[0] == 12:
                    scripts.append(b2s(p[1]))
        blob = "\n".join(scripts)
        hits = CALL.findall(blob)
        if not hits:
            continue
        made = MAKE.findall(blob)
        for txt in hits:
            e = info[txt]
            e["calls"] += 1
            e["files"].add(f"{map_ko(mapno)}(맵 {mapno})" if mapno
                            else f"공통 이벤트 「{_ev}」")
            for cid, nm in made:
                e["cls"].add(int(cid))
                e["names"].add(nm)
            if msgs:
                e["pre"].append((mapno, fold(msgs[0])))
    return info


def plan():
    cls, ko = class_names(), ko_index()
    info = scan()
    rows = []
    for txt, e in sorted(info.items(), key=lambda kv: -kv[1]["calls"]):
        titles = sorted({cls.get(c, (f"직함 {c}", "?")) for c in e["cls"]})
        who = " / ".join(f"{k}({s})" for k, s in titles) or "미상"
        pre_es = pre_ko = ""
        for mapno, es in e["pre"]:                 # 현행 번역이 붙는 도전 대사를 고른다
            v = ko.get((mapno, es))
            if v:
                pre_es, pre_ko = es, v
                break
        n = len(e["names"])
        place = (f"전투에 진 직후 하는 말. 트레이너 {n}명이 함께 쓰는 대사"
                 if n > 3 else "전투에 진 직후 하는 말")
        if not re.search(r"[a-zA-ZáéíóúñÁÉÍÓÚÑ]{3}", txt.replace("!", "")) or txt == "¡Scriiiii!":
            place += ". 원문은 낱말이 아니라 비명·울음이고, 종명을 흉내 낸 꼴이 아니다"
        rows.append({"id": f"e{len(rows):02d}", "who": who, "es": txt,
                     "자리": f"{place}. 호출 {e['calls']}곳 · {', '.join(sorted(e['files']))}",
                     "도전": pre_es, "도전_ko": pre_ko})
    BATCH.mkdir(exist_ok=True)
    CHUNKS.write_text(json.dumps({"cid": "endspeech", "rows": rows},
                                 ensure_ascii=False) + "\n", encoding="utf-8")
    miss = sum(1 for r in rows if not r["도전_ko"])
    print(f"고유 원문 {len(rows)}행 · 호출 {sum(v['calls'] for v in info.values())}곳 · "
          f"도전 대사 앵커 없음 {miss}행 → {CHUNKS}")


def build():
    """B판(새로 번역) 본문 + 이 요청의 전제 덮어쓰기 + 26행에서 캔 용어 규칙."""
    rows = json.loads(CHUNKS.read_text(encoding="utf-8"))["rows"]
    body = build_prompt(fresh=True)
    gloss = glossary_for([{"es": r["es"] + " " + r["도전"], "ko": r["도전_ko"]} for r in rows])
    body = body.replace("[용어 규칙 — 장면별 발췌 삽입]", gloss)
    # 본문은 「한 장면 + 끝의 장면 머리」를 전제한다. 우리 요청에는 장면 머리가 없으므로
    # 그 전제를 말하는 자리 셋을 **전부** 갈아야 한다 — 하나만 덮으면 규칙 A·B가 없는
    # 머리를 가리킨 채로 남는다. 본문이 바뀌면 여기서 소리 내며 멈춘다(build_prompt의
    # 낡음 검사와 같은 규율).
    for old, new in SWAPS:
        if old not in body:
            raise SystemExit("prompt-pages.md 본문이 바뀌었다 — 갈 자리를 못 찾았다:\n" + old)
        body = body.replace(old, new, 1)
    return body, rows


def run(effort="low", workers=1):
    prompt, rows = build()
    OUT.mkdir(exist_ok=True)
    dst = OUT / "endspeech.jsonl"
    if dst.exists():
        print(f"이미 있다 — 건너뜀: {dst}")
        return
    (OUT / "endspeech.req.json").write_text(
        json.dumps({"system": prompt, "user": rows}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    t0 = time.time()
    print(f"요청 1건 · {len(rows)}행 · {MODEL} · effort={effort}", flush=True)
    got, cost = ask_npc(key_of(), MODEL, prompt, rows, effort=effort)
    out = [{"id": r["id"], "who": r["who"], "es": r["es"], "old": None,
            "new": got.get(r["id"]), "ok": got.get(r["id"]) is not None,
            "why": None if got.get(r["id"]) else "누락",
            "자리": r["자리"], "도전": r["도전"], "도전_ko": r["도전_ko"]}
           for r in rows]
    dst.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in out),
                   encoding="utf-8")
    miss = sum(1 for x in out if not x["ok"])
    line = (f"{time.strftime('%Y-%m-%d %H:%M')} endspeech · {len(out)}행 · "
            f"누락 {miss} · ${cost:.4f} · {time.time() - t0:.0f}s")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)
    print(f"→ {dst}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "plan":
        plan()
    elif a[0] == "run":
        run(effort=a[a.index("--effort") + 1] if "--effort" in a else "low")
    elif a[0] == "prompt":
        print(build()[0])
    else:
        print(__doc__)
