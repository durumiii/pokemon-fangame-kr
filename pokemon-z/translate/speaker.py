# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""화자 귀속 — 이벤트 명령 순서로 「이 대사는 누구 말인가」를 계산한다.

이름표(`<b>이름:</b>`)가 붙은 줄은 그대로 읽고, 붙지 않은 줄은 **같은 이벤트 페이지
안에서 분기 깊이가 같은 동안** 앞 이름표를 물려받는다. 답은 원본 이벤트 데이터에
이미 들어 있다 — 명령 순서(cmd)와 조건 분기 깊이(@indent)가 그것이다.

옛 방식(`mapscan.py` 조인표 + 이벤트 스프라이트)은 이 둘을 버려서, 컷신처럼 그림은
하나인데 화자가 여럿인 자리를 통째로 한 사람으로 봤다. 이름표 없는 줄 4,265행 중
4분의 3에서 그림과 실제 화자가 어긋났고, 962행이 그 판정 위에서 다시 쓰였다.

usage:
  uv run translate/speaker.py scan          이벤트를 훑어 귀속표를 만든다
                                            → translate/data/speaker-attr.jsonl.gz
  uv run translate/speaker.py who <검색어>   원문·번역에 그 말이 든 줄의 화자를 보인다
  uv run translate/speaker.py lines <이름>   그 인물의 대사를 전부 뽑는다(어투 감사용)
  uv run translate/speaker.py stats         판정 근거별 집계
  uv run translate/speaker.py selftest      정답을 아는 자리로 채점한다

귀속 근거(`how`)는 다섯이다:
  태그        그 줄에 이름표가 붙어 있다 — 확실
  상속        같은 페이지·같은 분기 깊이에서 앞 이름표를 물려받았다
  분기다름    분기 깊이를 넘어 물려받았다 — 미더운 정도가 떨어진다
  명단1       페이지에 이름표가 한 종뿐이라 그 사람으로 본다
  그림        페이지에 이름표가 하나도 없다 — NPC 혼자 말하는 자리라 이벤트 그림이 화자다
  지문        그림이 사물·연출(표지판·책·화살표)이다 — 화자가 없고 평서 지문이 정답
  미상        이름표도 그림도 없다 — 지문이거나 시스템 문구
  선택지      주인공의 선택지. 주인공은 대사를 하지 않아 이름표가 붙지 않는다

`prompt` 칸이 참이면 **바로 뒤가 선택지인 메시지**다. 인물의 물음일 수도 시스템
안내일 수도 있으니 어투를 갈기 전에 사람이 본다 — 이 도구는 「누구에게 붙어
있나」를 계산할 뿐 「사람 말인가」를 판정하지 않는다.

화자 귀속과 **축이 다른** 세 칸을 함께 싣는다. 전부 원본에서 재계산되고 사람 판정을
안 탄다(근거: `docs/log/research/2026-08-13-scene-signal-survey.md`·`-scene-kind-survey.md`).

  cls    PS 정본 인물 · PC 이름표 없는 인물 · N 지문·시스템 (페이지 단위)
  once   이 페이지를 실행하면 같은 이벤트의 더 높은 번호 페이지 조건이 채워지나
  flags  이 페이지가 켜는 전역 스위치 중 **어딘가의 페이지 조건으로 쓰이는 것**
"""
import collections
import gzip
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "vendor"))
from datread import load  # noqa: E402  (딱지를 떼 옛 도구가 그대로 읽는다)

GAME = Path("/mnt/d/Game/Pokemon Z/V2.18/Data")
OUT = HERE / "data" / "speaker-attr.jsonl.gz"
KO_MAPS = HERE / "ko" / "00-maps.jsonl"

TAG = re.compile(r"^(?:\\c\[\d+\])?<b>([^<:]{1,24}):</b>")

# 정답을 아는 자리 — 유지자가 실기·제보로 확정한 것들 (원문 조각, 기대 화자, 출처)
KNOWN = [
    ("Para nosotros, se parecen mucho a las letras", "Mirra", "맵119 손수정"),
    ("En este sorprendente lugar enterraban a los druidas", "Mirra", "맵119 손수정"),
    ("He tratado con esmero de encontrar a un intérprete", "Mirra", "맵119 손수정"),
    ("Los druidas son la primera civilización", "Crisanto", "맵119 손수정"),
    ("Pero... ya nos han engañado antes", "Crisanto", "맵113 제보"),
    ("Un Pokémon estaba vivo y el otro", "Crisanto", "맵111 제보(누빌라 오판)"),
    ("¿Y <b>Lanto</b> es quien ha financiado", "Crisanto", "맵111 제보"),
]

# 층 판정의 정답 자리 — 2026-08-13 감사 §3③④. 앞 다섯은 말투 정본 등재인데 이름표
# 행수가 50 미만이라 옛 규칙이 떨어뜨렸고, 뒤 둘은 어간 충돌로 정본 인물이 되던 무명 단원이다.
KNOWN_CLS = [("who", "Anturia", "PS"), ("who", "Capitán Merlot", "PS"),
             ("who", "Barquero", "PS"), ("who", "Nácar", "PS"), ("who", "Mimi", "PS"),
             ("sprite", "flareow", "PC"), ("sprite", "flaraow", "PC")]

# 1회 소비 판정의 정답 자리 — `docs/log/research/2026-08-13-audit-cells.jsonl`의 「1회소비」 값.
KNOWN_ONCE = [((22, 3, 7), True), ((2, 1, 0), True), ((163, 44, 1), False), ((3, 47, 0), False)]


def b2s(v):
    return v.decode("utf-8", errors="replace") if isinstance(v, bytes) else str(v)


def page_messages(cmdlist):
    """(cmd, indent, kind, text) — 101/401은 한 메시지로 잇고 102는 선택지로 편다.

    cmd는 명령 인덱스, indent는 조건 분기 깊이다. 이 둘이 화자 상속의 전부다.
    """
    out, buf, bi, bd = [], None, None, 0
    for i, cmd in enumerate(cmdlist):
        ca = cmd.attributes
        code, params = ca["@code"], ca["@parameters"]
        if code == 101:
            if buf is not None:
                out.append((bi, bd, "text", buf))
            buf, bi, bd = b2s(params[0]), i, ca["@indent"]
        elif code == 401 and buf is not None:
            buf += "\n" + b2s(params[0])
        else:
            if buf is not None:
                out.append((bi, bd, "text", buf))
                buf = None
            if code == 102:
                for j, c in enumerate(params[0]):
                    out.append((i + j / 100, ca["@indent"], "choice", b2s(c)))
    if buf is not None:
        out.append((bi, bd, "text", buf))
    return out


def object_sprites():
    """사물·연출 스프라이트 어간 — 이 그림이 붙은 이벤트의 말은 화자가 아니라 지문이다."""
    g = json.loads((HERE / "sprite-groups.json").read_text(encoding="utf-8"))["groups"]
    return set(g.get("사물지문", [])) | set(g.get("포켓몬특수", []))


STEM = re.compile(r"(ow|w|TS[A-Za-z]*|\d+)$")


def stem(s):
    s, prev = s or "", None
    while s != prev:
        prev, s = s, STEM.sub("", s)
    return s


def voice_sprites():
    """정본 인물 스프라이트 어간 목록(`sprite-groups.json`의 voices)."""
    g = json.loads((HERE / "sprite-groups.json").read_text(encoding="utf-8"))["groups"]
    return set(g.get("voices", []))


VOICES_STRIP = re.compile(r"(Montado|Montada|Reventada|Caduca|Vestido|Monigote|Pose|"
                          r"Pechamen|Dormido|Final|Salamence|Lira|Capucha|Herido|"
                          r"Cabeza|Borracha|Mapa|Musica|Baln|TS)")
VOICES_SPECIAL = {"az": "AZ", "f3": "F3", "druidaFicus": "대드루이드 피쿠스"}


def deacc(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()


def voices_map():
    """voices 그룹 스프라이트 이름 → 한국어 인물명 (names.json 조인).

    이름으로 이어지는 그림인지만 본다 — `stem_conflicts`가 「어간만 걸리고 이름은
    어디에도 없는」 그림을 가려내는 데 쓴다.
    """
    names = json.loads((HERE / "names.json").read_text(encoding="utf-8"))["names"]
    out = {}
    groups = json.loads((HERE / "sprite-groups.json").read_text(encoding="utf-8"))["groups"]
    for s in groups["voices"]:
        base = VOICES_STRIP.sub("", s)
        if base in VOICES_SPECIAL or s in VOICES_SPECIAL:
            out[s] = VOICES_SPECIAL.get(s, VOICES_SPECIAL.get(base))
            continue
        ds = deacc(base)
        hit = next((ko for es, ko in names.items()
                    if deacc(es) == ds or (len(ds) >= 4 and (deacc(es).startswith(ds)
                                                             or ds.startswith(deacc(es))))), None)
        out[s] = hit
    return out


def roster():
    """말투 정본 인물 명단 — `voices.md`의 **인물표(넉 칸)만** 읽는다.

    ⚠ `batch_pages.voice_lines`를 여기에 쓰면 안 된다 — 그쪽은 프롬프트에 실을
    말투를 모으느라 두 칸짜리 집단 화자표(시민·총사·아자하라 …)까지 읽는다.
    그 명단으로 층을 가르면 잔부·집단 화자가 정본 인물(PS)로 승격한다.
    """
    table = {}
    for line in (HERE.parent / "docs" / "ledger" / "voices.md").read_text(
            encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 5 and cells[1] and cells[1] not in ("인물", "갈래", "태그") \
                and not cells[1].startswith("-"):
            table[cells[1]] = cells[-2]
    return table


# 어간 축약이 이름 없는 그림을 정본 인물 명단으로 끌어올리는 자리. `stem("flareow")`가
# `flare`가 되어 voices에 걸리는데(`flaraow`도 같다) 플레어단 무명 단원의 그림이고,
# `luigiow`는 페르소나표가 다스리는 카메오다 — 셋 다 고유명 표기 목록에도 이름표에도
# 그 이름이 없다. 전 스프라이트 전수 검사(`stem_conflicts`)로 고른 목록이고
# `selftest`가 같은 검사를 다시 돌려 새 충돌이 생기면 떨어뜨린다.
STEM_CONFLICT = frozenset({"flare", "flara", "luigi"})


def voice_sprite(sprite, voices):
    """이 그림이 정본 인물의 것인가 — **원시 이름 정확 일치가 먼저**다.

    어간 일치는 그다음이고 충돌 목록을 통과한 것만 인정한다. 어간을 먼저 보면
    `flareow`(무명 단원)가 `flare`로 접혀 정본 인물이 된다(2026-08-13 감사 §3④).
    """
    if not sprite:
        return False
    if sprite in voices:
        return True
    s = stem(sprite)
    return s in voices and s not in STEM_CONFLICT


def stem_conflicts(sprites, voices, tags=frozenset()):
    """어간으로만 voices에 걸리는데 **이름이 어디에도 없는** 스프라이트 전수.

    원시 이름이 목록에 없고 어간만 걸리는 자리를 모아, 그 어간이 고유명 표기
    목록(names.json)으로도 이름표(`tags`)로도 이어지지 않는 것만 남긴다. 어느
    쪽으로도 안 이어진다는 것은 「이름 없는 그림이 이름 있는 인물 자리에
    들어왔다」는 뜻이고, 그것이 `STEM_CONFLICT`에 박히는 근거다.
    """
    vmap = voices_map()                          # 어간 → 한국어 인물명 조인(정본 규칙)
    lower = {t.lower() for t in tags}
    out = {}
    for sp in sprites:
        s = stem(sp)
        if sp and sp not in voices and s in voices \
                and not vmap.get(s) and s.lower() not in lower:
            out.setdefault(s, []).append(sp)
    return out


def canon_names(rows, threshold=50):
    """정본 인물 이름 — **말투 정본 등재가 행수 문턱보다 우선한다.**

    문턱(이름표 50행)은 대용품이라 등재 인물을 떨어뜨렸다(2026-08-13 감사 §3③:
    Anturia · Capitán Merlot · Barquero · Nácar · Mimi가 행수 미달로 잡담 층에
    갔다). 등재 명단은 **`docs/ledger/voices.md`의 인물 표**다 — `voice-prompts.jsonl`
    쪽은 `Aldeana`·`Gente`처럼 무리 이름표에 붙이는 말투 지시까지 담고 있어 명단으로
    쓰면 행인이 정본 인물이 된다. 이름표는 스페인어에 직함이 붙어 오므로
    `batch_pages.resolve`로 한국어 인물명까지 풀어 맞춘다.
    """
    from batch_pages import ko_names, resolve        # 이름표 → 한국어 인물명
    names, names_roster = ko_names(), roster()
    tagged = collections.Counter(r["who"] for r in rows if r["how"] == "태그")
    return {w for w, n in tagged.items() if n >= threshold} | \
           {w for w in tagged if resolve(w, names) in names_roster}


COMPASS = frozenset({"Norte", "Sur", "Este", "Oeste"})
# 방위 이름표는 표지판 안내다. 색 낱말(Naranja·Lila·Menta)은 빼지 않는다 —
# 그 셋은 수수께끼 정령의 이름이고 실제로 말한다(2026-08-13 감사 §2 E2).
NONPERSON = ("trchar", "rayos")


def person_tag(name):
    """사람 이름 이름표인가 — 전부 대문자는 표지·안내 딱지(`AVISO`·`PISTA DE …`)다."""
    return bool(name) and not name.isupper() and name not in COMPASS


def person_sprite(sprite, objects):
    """그림이 사람인가 — 숫자(포켓몬 번호)·전투 그림·사물 어간을 뺀다."""
    return bool(sprite) and not sprite.startswith(NONPERSON) \
        and not sprite[0].isdigit() and stem(sprite) not in objects


def classify(cast, sprite, objects, canon, voices):
    """페이지의 층 — PS 정본 인물 · PC 이름표 없는 인물 · N 지문·시스템.

    신호는 둘뿐이다(표본 126페이지 모집단 가중 정확도 0.991): **그림이 사람인가**와
    **사람 이름 이름표가 붙었는가.** 대사 줄 수·연출 명령은 이 축에서 아무 일도 안 한다.
    """
    people = [c for c in cast if person_tag(c)]
    if not people and not person_sprite(sprite, objects):
        return "N"
    if any(c in canon for c in people) or voice_sprite(sprite, voices):
        return "PS"
    return "PC"


def page_sets(cmdlist):
    """이 페이지가 켜는 것 — (전역 스위치 id, 셀프스위치 문자, 변수 id). 값 0이 ON이다."""
    sw, selfsw, var = set(), set(), set()
    for c in cmdlist:
        a = c.attributes
        code, p = a["@code"], a["@parameters"]
        if code == 121 and p[2] == 0:
            sw.update(range(p[0], p[1] + 1))
        elif code == 123 and p[1] == 0:
            selfsw.add(b2s(p[0]))
        elif code == 122:
            var.update(range(p[0], p[1] + 1))
    return sw, selfsw, var


def page_cond(page):
    """페이지 조건 — (스위치 id 집합, 셀프스위치 문자 또는 None, 변수 id 또는 None)."""
    c = page.attributes["@condition"].attributes
    sw = {c[f"@switch{i}_id"] for i in (1, 2) if c[f"@switch{i}_valid"]}
    return (sw,
            b2s(c["@self_switch_ch"]) if c["@self_switch_valid"] else None,
            c["@variable_id"] if c["@variable_valid"] else None)


def one_shot(pages, pi):
    """이 페이지가 한 번 쓰이고 덮이나.

    RPG Maker XP는 조건을 만족하는 페이지 중 **번호가 가장 큰 것**을 띄운다. 그래서
    1회성의 기계 정의는 「실행하면 더 높은 번호 페이지의 조건이 채워지는가」다
    (2026-08-13 장면 종류 조사 §3.2 — 이 신호 하나로 1회성/상시 2치 정확도 0.94).

    ⚠ 변수 조건은 id만 맞춰 본다 — `@variable_value` 이상인지까지는 안 센다.
    """
    sw, selfsw, var = page_sets(pages[pi].attributes["@list"])
    for later in pages[pi + 1:]:
        csw, cself, cvar = page_cond(later)
        if (csw & sw) or (cself and cself in selfsw) or (cvar and cvar in var):
            return True
    return False


def attribute(msgs, sprite="", objects=frozenset()):
    """페이지 하나의 메시지 목록에 화자를 붙인다. msgs는 cmd 순으로 정렬돼 있어야 한다.

    이름표가 하나도 없는 페이지는 **NPC 하나가 혼자 말하는 자리**이므로 이벤트
    그림이 곧 화자다 — 옛 방식이 이 구간에서 맞았던 이유이기도 하다.

    이 함수가 정하는 것은 「이 메시지가 이벤트 흐름에서 누구에게 붙어 있나」이지
    「이게 사람 말인가」가 아니다. 축이 다른 두 가지라 뒤섞으면 시스템 문구까지
    인물 어투로 갈아엎게 된다(2026-08-06: 조리 안내 「어떻게 할까요?」 9행이
    사프라 대사로 잡혔다). 그래서 판단이 필요한 자리를 따로 표시한다:

    - `prompt=True` — 바로 뒤가 선택지인 메시지. 인물의 물음일 수도, 시스템
      안내일 수도 있다. **표시일 뿐 판정이 아니다** — 실제로 지니아의 물음인
      자리와 스타팅 포켓몬 선택 안내가 둘 다 여기 들어온다.
    - `how="지문"` — 그림이 사물·연출(표지판·책·화살표 등)이다. 화자가 없고
      평서 지문이 정답인 자리다.
    """
    cast = {m for _, _, _, t in msgs if (m := (TAG.match(t).group(1) if TAG.match(t) else None))}
    obj = stem(sprite) in objects
    cur = cur_ind = None
    for i, (cmdi, ind, kind, text) in enumerate(msgs):
        nxt = msgs[i + 1] if i + 1 < len(msgs) else None
        prompt = bool(kind == "text" and nxt and nxt[2] == "choice" and abs(nxt[0] - cmdi) < 3)
        m = TAG.match(text)
        if m:
            cur, cur_ind = m.group(1), ind
            who, how = cur, "태그"
        elif kind == "choice":
            who, how = "", "선택지"
        elif cur is not None and ind == cur_ind:
            who, how = cur, "상속"
        elif cur is not None:
            who, how = cur, "분기다름"
        elif len(cast) == 1:
            who, how = next(iter(cast)), "명단1"
        elif not cast and sprite:
            who, how = ("", "지문") if obj else (sprite, "그림")
        else:
            who, how = "", "미상"
        yield cmdi, ind, kind, text, who, how, sorted(cast), prompt


TRIGGER = {0: "말걸기", 1: "플레이어접촉", 2: "이벤트접촉", 3: "자동실행", 4: "병렬처리"}


TRAINER = re.compile(r"^Trainer\(\d+\)$")

# 페이지가 「연출」을 하고 있다는 신호 — 인물을 걸어 다니게 하고(209) 화면·소리를 만진다.
MOVE = 209                                    # 이동 루트 설정
STAGE = frozenset({203, 204, 223, 224, 231, 232, 241})
# 203 화면 스크롤 · 204 지도 스크롤 · 223 화면 색조 · 224 화면 플래시
# 231/232 그림 표시·이동 · 241 BGM 연주
# ⚠ SE 연주(250)와 회복(314)은 뺐다 — 「명상하여 포켓몬을 치료하시겠습니까?」 같은
#   기능 이벤트가 이 둘 때문에 컷신으로 샜다(2026-08-08 표본 검증).


def scene(trigger, n_msg, event_name="", codes=frozenset(), has_tag=False):
    """이 페이지가 「스토리 장면」인가 「지나가며 거는 말」인가.

    `@trigger` 하나로는 갈리지 않는다(2026-08-08 실측) — 이벤트 접촉(2)은 컷신이 아니라
    **트레이너 시야 도발**이었고(대사 있는 256페이지 전부가 `Trainer(n)` 이름), 반대로
    말걸기(0)로 시작하는 스토리 장면도 있다. 그래서 게임이 이미 갖고 있는 두 답을 쓴다.

    - **제작자가 붙인 이벤트 이름** — `Trainer(n)`은 도발 대사다. 기본 이름(EV0xx)만
      쓰는 게임이라 이름으로 알 수 있는 것은 여기까지다.
    - **명령 구성** — 컷신은 인물을 걸어 다니게 하고(이동 루트 209) 화면 색조·BGM·
      스크롤을 만진다. 자동실행 페이지의 87%가 이동 루트를 쓰는 반면 말걸기는 16%다.

    자동실행·병렬은 플레이어가 고르지 않았는데 열리므로 그대로 컷신이다.
    """
    if trigger < 0:
        return "공통"
    if trigger == 2 or TRAINER.match(event_name or ""):
        return "트레이너"
    if trigger in (3, 4):
        return "컷신"
    if MOVE in codes and codes & STAGE and (has_tag or n_msg > 6):
        return "컷신"
    return "대화" if n_msg > 6 else "잡담"


def scan():
    rows = []
    objects, voices = object_sprites(), voice_sprites()
    cond_sw = set()                 # 어딘가의 페이지 조건으로 쓰이는 전역 스위치
    infos = load(open(GAME / "MapInfos.rxdata", "rb"))
    names = {k: b2s(v.attributes["@name"]) for k, v in infos.items()}

    def emit(mid, mname, eid, ename, page, sprite, cmdlist, trigger=-1, once=False):
        msgs = page_messages(cmdlist)
        n_msg = sum(1 for _, _, kind, _ in msgs if kind == "text")
        codes = {c.attributes["@code"] for c in cmdlist}
        has_tag = any(TAG.match(t) for _, _, kind, t in msgs if kind == "text")
        sc = scene(trigger, n_msg, ename, codes, has_tag)
        on = sorted(page_sets(cmdlist)[0])
        for cmdi, ind, kind, text, who, how, cast, prompt in attribute(msgs, sprite, objects):
            rows.append({"map": mid, "map_name": mname, "event": eid, "event_name": ename,
                         "page": page, "cmd": cmdi, "ind": ind, "sprite": sprite,
                         "trigger": trigger, "n_msg": n_msg, "scene": sc,
                         "kind": kind, "who": who, "how": how, "cast": cast,
                         "prompt": prompt, "once": once, "flags": on, "k": text})

    for ce in load(open(GAME / "CommonEvents.rxdata", "rb")):
        if ce is None:
            continue
        ca = ce.attributes
        emit(0, "(공통 이벤트)", ca["@id"], b2s(ca["@name"]), 0, "", ca["@list"])

    for p in sorted(GAME.glob("Map[0-9][0-9][0-9].rxdata")):
        mid = int(p.stem[3:])
        m = load(open(p, "rb"))
        for ev in m.attributes["@events"].values():
            ea = ev.attributes
            pages = ea["@pages"]
            for pi, page in enumerate(pages):
                cond_sw |= page_cond(page)[0]
                g = page.attributes["@graphic"].attributes
                emit(mid, names.get(mid, ""), ea["@id"], b2s(ea["@name"]), pi,
                     b2s(g["@character_name"]), page.attributes["@list"],
                     page.attributes["@trigger"], one_shot(pages, pi))

    # 층과 플래그는 전량을 본 뒤에 정해진다 — 이름표 행수는 코퍼스 전체를 세야 나오고,
    # 「진행 플래그」는 다른 맵의 페이지 조건에 쓰이는지로 갈린다.
    canon = canon_names(rows)
    for r in rows:
        r["cls"] = classify(r["cast"], r["sprite"], objects, canon, voices)
        r["flags"] = [i for i in r["flags"] if i in cond_sw]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT, "wt", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(rows)}행 → {OUT.relative_to(HERE.parent)}")
    return rows


def load_attr():
    if not OUT.exists():
        sys.exit(f"귀속표가 없어요 — 먼저 만드세요: uv run {Path(__file__).name} scan")
    with gzip.open(OUT, "rt", encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def ko_key(s):
    """조회 열쇠 — 공백류를 하나로 접는다.

    귀속표는 이벤트 원문의 줄바꿈을 그대로 담는데 00-maps.jsonl의 k는 그 자리가
    공백으로 접혀 있다. strip()만으로는 이 차이를 못 메워 확정 원문 5,892개 중
    343개가 조회에 실패했다(2026-08-06 실측) — 그 자리엔 번역 대신 원문이 나왔다.
    """
    return re.sub(r"\s+", " ", s or "").strip()


def ko_index():
    """원문 → 현행 한국어. 맵 대사 정본에서 뽑는다."""
    idx = {}
    for line in KO_MAPS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if "map" not in r:
            idx.setdefault(ko_key(r["k"]), r["v"])
    return idx


def show(rows, ko, limit=None):
    for i, r in enumerate(rows):
        if limit and i >= limit:
            print(f"… 그 밖 {len(rows) - limit}행")
            break
        v = ko.get(ko_key(r["k"]), "")
        print(f"맵{r['map']}:ev{r['event']}:p{r['page']}:cmd{r['cmd']} "
              f"[{r['how']}]{'[선택지앞]' if r.get('prompt') else ''} {r['who'] or '—'}")
        print(f"    {v or r['k']}")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]

    if cmd == "scan":
        scan()
    elif cmd == "stats":
        rows = load_attr()
        import collections
        c = collections.Counter(r["how"] for r in rows)
        print(f"총 {len(rows)}행")
        for k, n in c.most_common():
            print(f"  {k:6s} {n:6d}")
    elif cmd == "who" and len(sys.argv) > 2:
        q = sys.argv[2]
        rows, ko = load_attr(), ko_index()
        hit = [r for r in rows
               if q in r["k"] or q in ko.get(ko_key(r["k"]), "")]
        print(f"{len(hit)}행")
        show(hit, ko, 40)
    elif cmd == "lines" and len(sys.argv) > 2:
        name = sys.argv[2]
        rows, ko = load_attr(), ko_index()
        hit = [r for r in rows if name.lower() in (r["who"] or "").lower()]
        import collections
        print(f"{name}: {len(hit)}행 · 근거별 "
              f"{dict(collections.Counter(r['how'] for r in hit))}")
        show(hit, ko)
    elif cmd == "selftest":
        rows = load_attr()
        ok = bad = 0
        for frag, want, src in KNOWN:
            hit = next((r for r in rows if frag in r["k"]), None)
            if hit is None:
                print(f"[못찾음] {frag[:40]!r}")
                bad += 1
                continue
            mark = "O" if hit["who"] == want else "X"
            ok += hit["who"] == want
            bad += hit["who"] != want
            print(f"[{mark}] {want:10s} ← {hit['who']:10s} ({hit['how']}) "
                  f"맵{hit['map']} ev{hit['event']} · {src}")

        for field, val, want in KNOWN_CLS:
            got = sorted({r["cls"] for r in rows if r[field] == val})
            mark = "O" if got == [want] else "X"
            ok, bad = ok + (got == [want]), bad + (got != [want])
            print(f"[{mark}] {field}={val:16s} {want} ← {'·'.join(got) or '없음'}")

        for (mid, eid, pi), want in KNOWN_ONCE:
            hit = next((r for r in rows
                        if (r["map"], r["event"], r["page"]) == (mid, eid, pi)), None)
            got = hit and hit["once"]
            mark = "O" if got == want else "X"
            ok, bad = ok + (got == want), bad + (got != want)
            print(f"[{mark}] once 맵{mid} ev{eid} p{pi} {want} ← {got}")

        # 어간 충돌은 목록을 박아 두는 것이라, 원본이 바뀌면 새 충돌이 조용히 샌다.
        conflicts = stem_conflicts({r["sprite"] for r in rows}, voice_sprites(),
                                   {r["who"] for r in rows if r["how"] == "태그"})
        leaked = {s: v for s, v in conflicts.items() if s not in STEM_CONFLICT}
        print(f"[{'O' if not leaked else 'X'}] 어간 충돌 목록 밖 {leaked or '없음'}"
              f" (전수 {sorted(conflicts)})")
        bad += bool(leaked)
        ok += not leaked

        print(f"\n채점 {ok}/{ok + bad}")
        sys.exit(1 if bad else 0)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
