# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal", "pyyaml"]
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

귀속 근거(`how`)는 아래와 같다:
  태그        그 줄에 이름표가 붙어 있다 — 확실
  상속        같은 페이지·같은 분기 깊이에서 앞 이름표를 물려받았다
  분기다름    분기 깊이를 넘어 물려받았다 — 미더운 정도가 떨어진다. 깊어지는 쪽과
              합류(닫힌 가지들의 이름표가 한 사람일 때)만 잇고, 여럿이면 끊는다
  명단1       페이지에 이름표가 한 종뿐이라 그 사람으로 본다
  그림        페이지에 이름표가 하나도 없다 — NPC 혼자 말하는 자리라 이벤트 그림이 화자다
  지문        그림이 사물·연출(표지판·책·화살표)이다 — 화자가 없고 평서 지문이 정답
  미상        이름표도 그림도 없다 — 지문이거나 시스템 문구
  선택지      주인공의 선택지. 주인공은 대사를 하지 않아 이름표가 붙지 않는다
  전투호출    `pbTrainerBattle`의 셋째 인자 — 같은 호출의 직함·이름이 곧 화자다. 확실
  스크립트    스크립트의 `_I("…")`인데 화자를 뽑을 인자가 없다(육아방 `pbDayCareChoose`)

뒤 둘은 메시지 명령이 아니라 **스크립트 명령**(355/655, 조건 분기 111 type 12)에서
온다. `kind="battle"`로 따로 서고 이름표 상속에 끼지 않는다 — 물려받지도 물려주지도
않고 `cast`·`n_msg`에도 안 들어간다. 직함 상수는 `tclass` 칸에 실린다.

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
import functools
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

# 전투 호출(`pbTrainerBattle`) 갈래의 정답 자리 — (맵, 이벤트, 기대 화자, 기대 근거).
# 셋째는 육아방 `pbDayCareChoose`다. 인자가 `_I` 하나뿐이라 **화자 없음이 정답**이고,
# 전투 호출과 같은 규칙으로 처리하면 안 된다.
KNOWN_BATTLE = [(90, 35, "Wolfram", "전투호출"), (20, 11, "Alexandre", "전투호출"),
                (48, 5, "", "스크립트")]

# 층 판정의 정답 자리 — 2026-08-13 감사 §3③④. 앞 다섯은 말투 정본 등재인데 이름표
# 행수가 50 미만이라 옛 규칙이 떨어뜨렸고, 뒤 둘은 어간 충돌로 정본 인물이 되던 무명 단원이다.
KNOWN_CLS = [("who", "Anturia", "PS"), ("who", "Capitán Merlot", "PS"),
             ("who", "Barquero", "PS"), ("who", "Nácar", "PS"), ("who", "Mimi", "PS"),
             ("sprite", "flareow", "PC"), ("sprite", "flaraow", "PC"),
             # 대문자 이름표 둘과 그것을 막던 안내판 딱지 — `person_tag`의 세 걸음이
             # 순서대로 서야 셋이 동시에 맞는다(2026-08-14).
             ("who", "F3", "PS"), ("who", "AZ", "PS"),
             ("who", "PISTA DE ENTRENADOR", "N"),
             ("sprite", "f3ow", "PS"),   # 어간을 한 단계씩 맞추지 않으면 `f`까지 깎인다
             # 그림 규칙의 예외 셋(2026-08-18) — 명단에서 뺀 다친 사냥꾼 · 기능 창구
             # 포켓몬 · 포켓몬마을 주민. 예외가 풀리면 셋 다 N으로 돌아간다.
             ("sprite", "cazadorHerido", "PC"), ("sprite", "115", "PC"),
             ("sprite", "242", "PC")]

# 분기 합류 꼬리의 정답 자리 (2026-08-18) — 닫힌 가지들의 이름표가 여럿이면 물려받지
# 않고(맵418 재도전 창구), 성별 분기처럼 한 사람이면 잇는다(맵97 뱃사공).
KNOWN_JOIN = [((418, 19), "Recibes 3", "", "미상"),
              ((97, 4), "persona acaudalada", "Barquero", "분기다름")]

# 1회 소비 판정의 정답 자리 — `docs/log/research/2026-08-13-audit-cells.jsonl`의 「1회소비」 값.
KNOWN_ONCE = [((22, 3, 7), True), ((2, 1, 0), True), ((163, 44, 1), False), ((3, 47, 0), False)]


def b2s(v):
    return v.decode("utf-8", errors="replace") if isinstance(v, bytes) else str(v)


def call_args(s, i):
    """`(` 바로 뒤 i에서 시작해 짝이 맞는 `)`까지, 최상위 콤마로 자른 인자 목록.

    돌려주는 것은 (시작 오프셋, 원문 조각) 쌍이다 — 인자 안의 문자열이 원본
    어디에 있었는지를 알아야 `_I(…)`가 셋째 인자인지 가릴 수 있다. 괄호 깊이와
    따옴표 상태를 함께 추적한다. 「문자열 앞의 가장 가까운 호출」 휴리스틱은
    이 코퍼스에서 우연히 맞을 뿐 구조가 보장하지 않는다.
    """
    args, depth, start, q, esc = [], 0, i, None, False
    for j in range(i, len(s)):
        c = s[j]
        if esc:
            esc = False
        elif q:
            if c == "\\":
                esc = True
            elif c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            if depth == 0:
                args.append((start, s[start:j]))
                return args
            depth -= 1
        elif c == "," and depth == 0:
            args.append((start, s[start:j]))
            start = j + 1
    return args                            # 괄호가 안 닫힌다 — 마지막 조각은 버린다


ILIT = re.compile(r'_I\(\s*"((?:[^"\\]|\\.)*)"\s*\)')
SLIT = re.compile(r'^\s*"((?:[^"\\]|\\.)*)"\s*$')
PBCLASS = re.compile(r"PBTrainers::(\w+)")
BATTLE_CALL = re.compile(r"\bpbTrainerBattle\s*\(")


def unquote(s):
    return s.replace('\\"', '"').replace("\\\\", "\\")


def script_battles(s):
    """`pbTrainerBattle` 호출의 셋째 인자 `_I(…)` 위치 → (직함 상수, 트레이너 이름)."""
    out = {}
    for m in BATTLE_CALL.finditer(s):
        args = call_args(s, m.end())
        if len(args) < 3:
            continue
        cls, name = PBCLASS.search(args[0][1]), SLIT.match(args[1][1])
        lit = ILIT.search(args[2][1])
        if not (cls and name and lit):
            continue
        out[args[2][0] + lit.start()] = (cls.group(1), unquote(name.group(1)))
    return out


def script_rows(s, i, indent):
    """스크립트 한 덩이 안의 `_I("…")` 전부 — 전투 호출의 것이면 화자를 달아서.

    `_I`는 게임이 화면에 띄우는 문자열이라 메시지 명령과 같은 번역 대상인데,
    명령 101/401에 안 실려 있어 옛 `scan`이 통째로 놓쳤다(Z-60).
    """
    battles = script_battles(s)
    return [(i if j == 0 else i + j / 100, indent, "battle",
             unquote(m.group(1)), *battles.get(m.start(), ("", "")))
            for j, m in enumerate(ILIT.finditer(s))]


def page_messages(cmdlist):
    """(cmd, indent, kind, text, 직함, 이름) — 101/401은 한 메시지로 잇고 102는 선택지로 편다.

    cmd는 명령 인덱스, indent는 조건 분기 깊이다. 이 둘이 화자 상속의 전부다.
    스크립트 명령(355/655와 조건 분기 111 type 12)의 `_I("…")`는 `kind="battle"`로
    따로 나온다 — 상속의 흐름에 끼면 안 되는 자리다(`attribute` 참조).
    직함·이름은 그 갈래에서만 차고 나머지는 빈 문자열이다.
    """
    out, buf, bi, bd = [], None, None, 0
    sbuf, si, sd = None, None, 0                  # 355 + 655…로 이어지는 스크립트 한 덩이
    for i, cmd in enumerate(cmdlist):
        ca = cmd.attributes
        code, params = ca["@code"], ca["@parameters"]
        if code != 655 and sbuf is not None:
            out.extend(script_rows(sbuf, si, sd))
            sbuf = None
        if code == 101:
            if buf is not None:
                out.append((bi, bd, "text", buf, "", ""))
            buf, bi, bd = b2s(params[0]), i, ca["@indent"]
        elif code == 401 and buf is not None:
            buf += "\n" + b2s(params[0])
        else:
            if buf is not None:
                out.append((bi, bd, "text", buf, "", ""))
                buf = None
            if code == 102:
                for j, c in enumerate(params[0]):
                    out.append((i + j / 100, ca["@indent"], "choice", b2s(c), "", ""))
            elif code == 355:
                sbuf, si, sd = b2s(params[0]), i, ca["@indent"]
            elif code == 655 and sbuf is not None:
                sbuf += "\n" + b2s(params[0])
            elif code == 111 and params and params[0] == 12:
                out.extend(script_rows(b2s(params[1]), i, ca["@indent"]))
    if buf is not None:
        out.append((bi, bd, "text", buf, "", ""))
    if sbuf is not None:
        out.extend(script_rows(sbuf, si, sd))
    return out


def sprite_groups():
    """스프라이트 묶음 — 정본은 stage0/groups.yaml(직접 편집, 2026-08-18 강등)."""
    import yaml
    return yaml.safe_load((HERE / "stage0" / "groups.yaml")
                          .read_text(encoding="utf-8"))["sprite_groups"]["groups"]


def object_sprites():
    """사물·연출 스프라이트 어간 — 이 그림이 붙은 이벤트의 말은 화자가 아니라 지문이다."""
    g = sprite_groups()
    return set(g.get("사물지문", [])) | set(g.get("포켓몬특수", []))


STEM = re.compile(r"(ow|w|TS[A-Za-z]*|\d+)$")


def stem(s):
    s, prev = s or "", None
    while s != prev:
        prev, s = s, STEM.sub("", s)
    return s


def stem_steps(s):
    """어간을 **긴 것부터** 한 단계씩 내놓는다(원시 이름은 뺀다).

    끝까지 깎은 것 하나만 맞춰 보면 답을 지나친다 — `f3ow` → `f3`(목록에 있다) →
    `f`로 한 번 더 깎여 F3가 사라졌다. 맞춰 보는 쪽이 처음 걸리는 데서 멈춘다.
    """
    s = s or ""
    while (nxt := STEM.sub("", s)) != s:
        s = nxt
        yield s


def voice_sprites():
    """정본 인물 스프라이트 어간 목록(`stage0/groups.yaml` sprite_groups의 voices)."""
    return set(sprite_groups().get("voices", []))


VOICES_STRIP = re.compile(r"(Montado|Montada|Reventada|Caduca|Vestido|Monigote|Pose|"
                          r"Pechamen|Dormido|Final|Salamence|Lira|Capucha|Herido|"
                          r"Cabeza|Borracha|Mapa|Musica|Baln|TS)")
# 한글 표기가 아니라 그대로 쓰는 둘 — 표기 판정 대상이 아니라 코드에 남는다.
# 한국어 표기가 필요한 화자는 groups.yaml의 `ko` 칸이 정본이다(group_names).
VOICES_SPECIAL = {"az": "AZ", "f3": "F3"}


def group_names():
    """화자 → 한국어 표기. 정본은 stage0/groups.yaml의 `ko` 칸(직접 편집)."""
    import yaml
    groups = yaml.safe_load((HERE / "stage0" / "groups.yaml")
                            .read_text(encoding="utf-8"))["groups"]
    return {g["match"]["speaker"]: g["ko"] for g in groups if g.get("ko")}


def deacc(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().lower()


def voices_map():
    """voices 그룹 스프라이트 이름 → 한국어 인물명 (names.json 조인).

    이름으로 이어지는 그림인지만 본다 — `stem_conflicts`가 「어간만 걸리고 이름은
    어디에도 없는」 그림을 가려내는 데 쓴다.
    """
    names = json.loads((HERE / "names.json").read_text(encoding="utf-8"))["names"]
    special = {**VOICES_SPECIAL, **group_names()}
    out = {}
    for s in sprite_groups()["voices"]:
        base = VOICES_STRIP.sub("", s)
        if base in special or s in special:
            out[s] = special.get(s, special.get(base))
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

    셀 6개(넉 칸 표) 미만은 버린다 — 대장의 판정 절에 든 3칸 예시표(정본줄|전|후)가
    5셀로 잡혀 가짜 인물 다섯(줄 번호 넷 + 머리글)이 섞였던 자리다(2026-08-18 실측).
    """
    table = {}
    for line in (HERE.parent / "docs" / "ledger" / "voices.md").read_text(
            encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 6 and cells[1] and cells[1] not in ("인물", "갈래", "태그") \
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
    for s in stem_steps(sprite):          # 가장 긴 일치에서 멈춘다
        if s in voices:
            return s not in STEM_CONFLICT
    return False


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
        if not sp or sp in voices:
            continue
        for s in stem_steps(sp):                 # `voice_sprite`와 같은 걸음으로 본다
            if s in voices:
                if not vmap.get(s) and s.lower() not in lower:
                    out.setdefault(s, []).append(sp)
                break
    return out


def canon_names(rows, threshold=50):
    """정본 인물 이름 — **말투 정본 등재가 행수 문턱보다 우선한다.**

    문턱(이름표 50행)은 대용품이라 등재 인물을 떨어뜨렸다(2026-08-13 감사 §3③:
    Anturia · Capitán Merlot · Barquero · Nácar · Mimi가 행수 미달로 잡담 층에
    갔다). 등재 명단은 **`docs/ledger/voices.md`의 인물 표**다 — 말투 정본
    (`stage0/voices.yaml`) 쪽은 `Aldeana`·`Gente`처럼 무리 이름표에 붙이는 말투
    지시까지 담고 있어 명단으로 쓰면 행인이 정본 인물이 된다. 이름표는 스페인어에 직함이 붙어 오므로
    `batch_pages.resolve`로 한국어 인물명까지 풀어 맞춘다.
    """
    from batch_pages import ko_names, resolve        # 이름표 → 한국어 인물명
    names, names_roster = ko_names(), roster()
    tagged = collections.Counter(r["who"] for r in rows if r["how"] == "태그")
    return {w for w, n in tagged.items() if n >= threshold} | \
           {w for w in tagged if resolve(w, names) in names_roster}


# 방위 이름표(Norte·Sur·Este·Oeste)는 표지판 안내라 `batch_pages.SYS`에 들어 있다.
# 색 낱말(Naranja·Lila·Menta)은 빼지 않는다 — 그 셋은 수수께끼 정령의 이름이고
# 실제로 말한다(2026-08-13 감사 §2 E2).
NONPERSON = ("trchar", "rayos")


@functools.cache
def tag_lists():
    """이름표를 가르는 두 명단 — 비인물 배제와 정본 인물 화이트리스트.

    배제 명단은 **`batch_pages.SYS`가 정본이다.** 여기에 따로 세우면 명단이 둘이 되고
    「어느 쪽이 이기나」 규칙이 따라 붙는다. 화이트리스트는 `roster()`(voices.md 넉 칸
    인물표)뿐이다 — 두 칸짜리 집단 화자표를 쓰면 시민·총사 같은 무리가 정본 인물이 된다.
    """
    from batch_pages import SYS, ko_names, resolve
    return SYS, ko_names(), roster(), resolve


def person_tag(name):
    """사람 이름 이름표인가 — 배제 목록 → 화이트리스트 → 대문자 가드 순으로 본다.

    대문자 가드만 두면 `F3`·`AZ`가 인물 목록 만드는 첫 줄에서 사라진다(둘 다
    `isupper()`가 참이다). 그렇다고 가드부터 풀면 안 된다 — `canon_names()`의 50행
    문턱이 `PISTA DE ENTRENADOR`(트레이너 안내판, 이름표 51행)를 이미 정본 인물
    명단에 넣어 두었고 지금은 이 가드만이 그것을 막고 있다. 그래서 순서가 전부다.
    """
    if not name:
        return False
    sysnames, names, ros, resolve = tag_lists()
    if name in sysnames:                    # 안내판·표지 딱지
        return False
    if resolve(name, names) in ros:         # 말투 정본 인물표에 있으면 사람이다
        return True
    return not name.isupper()


# 그림 규칙의 예외 — 포켓몬 그림이 사람 노릇을 하는 자리(2026-08-18 실행 3·4).
# 포켓몬마을(맵356)은 포켓몬이 「주민」으로 1인칭 대사를 하는 특수 맵이라 맵째로 열고,
# 아래 넷은 기능 창구 NPC다(돌봄센터 카랑코·기술 리마인더 둘·레스토랑 웨이터).
# 넷 다 한 이벤트에만 서는 것을 전수로 확인해 (스프라이트, 맵) 쌍으로 좁히지 않았다.
PERSON_MAPS = frozenset({356})
PERSON_SPRITES = frozenset({"115", "474", "181", "096"})


def person_sprite(sprite, objects, mid=None):
    """그림이 사람인가 — 숫자(포켓몬 번호)·전투 그림·사물 어간을 뺀다."""
    if not sprite:
        return False
    if sprite in PERSON_SPRITES or (mid in PERSON_MAPS and sprite[0].isdigit()):
        return True
    return not sprite.startswith(NONPERSON) \
        and not sprite[0].isdigit() and stem(sprite) not in objects


def classify(cast, sprite, objects, canon, voices, mid=None, person=False):
    """페이지의 층 — PS 정본 인물 · PC 이름표 없는 인물 · N 지문·시스템.

    신호는 둘뿐이다(표본 126페이지 모집단 가중 정확도 0.991): **그림이 사람인가**와
    **사람 이름 이름표가 붙었는가.** 대사 줄 수·연출 명령은 이 축에서 아무 일도 안 한다.

    `person=True`는 그 둘을 건너뛰고 사람 층으로 세운다 — 전투 호출 줄처럼 화자가
    호출 인자로 이미 확정돼 있어 **그림으로 판정할 자리가 아닌** 갈래다(Z-67).
    """
    people = [c for c in cast if person_tag(c)]
    if not people and not person and not person_sprite(sprite, objects, mid):
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
    battles = [m for m in msgs if m[2] == "battle"]
    msgs = [m for m in msgs if m[2] != "battle"]
    cast = {m for _, _, _, t, *_ in msgs if (m := (TAG.match(t).group(1) if TAG.match(t) else None))}
    obj = stem(sprite) in objects
    cur = cur_ind = None
    hist = []          # (이름표인가, 깊이, 이름) — 분기 합류 판정이 되짚는다
    for i, (cmdi, ind, kind, text, *_) in enumerate(msgs):
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
        elif cur is not None and ind > cur_ind:
            # 이름표보다 깊은 줄 — 같은 화자가 조건 안에서 말을 잇는 자리라 물려받되
            # 낮은 확신 표시를 단다.
            who, how = cur, "분기다름"
        else:
            if cur is not None:
                # 이름표보다 얕은 줄 — 이름표가 살던 분기가 닫혔다. 방금 닫힌 가지들의
                # 이름표가 **한 사람**이면 성별 분기류라 그 사람이 말을 잇는 것이고
                # (맵97 뱃사공), 여럿이면 딴 화자 가지들의 합류 꼬리라 물려받으면
                # 사고다(맵418 ev19: 도전자 분기 뒤 창구 문구 네 줄이 도전자 이름을
                # 받았다, 2026-08-18). 가지 경계는 「이 깊이 이하의 마지막 메시지」까지.
                names = set()
                for was_tag, d, nm in reversed(hist):
                    if d <= ind and not was_tag:
                        break
                    if was_tag and d > ind:
                        names.add(nm)
                if len(names) == 1:
                    cur, cur_ind = names.pop(), ind
                    who, how = cur, "분기다름"
                else:
                    cur = cur_ind = None
                    who = None
            else:
                who = None
            if who is None:
                if len(cast) == 1:
                    who, how = next(iter(cast)), "명단1"
                elif not cast and sprite:
                    who, how = ("", "지문") if obj else (sprite, "그림")
                else:
                    who, how = "", "미상"
        hist.append((bool(m), ind, m.group(1) if m else None))
        yield cmdi, ind, kind, text, who, how, sorted(cast), prompt, ""

    # 전투 호출의 대사는 **상속의 흐름 밖**이다 — 같은 페이지의 이름표를 물려받지도
    # 물려주지도 않고(`cur`를 안 건드린다), `cast`에도 안 들어간다. 화자는 호출
    # 인자가 직접 말해 준다. `cast`는 페이지 것을 그대로 싣되, 층은 이 갈래를 그림으로
    # 가리지 않는다(`classify(person=True)`) — 스크립트 인자에 있는 대사라 그림이 없는
    # 것이 정상이고, 없는 그림을 「사람 아님」으로 읽으면 인물 대사가 지문층에 갇힌다.
    for cmdi, ind, kind, text, tclass, name in battles:
        yield cmdi, ind, kind, text, name, "전투호출" if name else "스크립트", \
            sorted(cast), False, tclass


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
        n_msg = sum(1 for _, _, kind, *_ in msgs if kind == "text")
        codes = {c.attributes["@code"] for c in cmdlist}
        has_tag = any(TAG.match(m[3]) for m in msgs if m[2] == "text")
        sc = scene(trigger, n_msg, ename, codes, has_tag)
        on = sorted(page_sets(cmdlist)[0])
        for cmdi, ind, kind, text, who, how, cast, prompt, tclass in attribute(
                msgs, sprite, objects):
            rows.append({"map": mid, "map_name": mname, "event": eid, "event_name": ename,
                         "page": page, "cmd": cmdi, "ind": ind, "sprite": sprite,
                         "trigger": trigger, "n_msg": n_msg, "scene": sc,
                         "kind": kind, "who": who, "how": how, "cast": cast,
                         "prompt": prompt, "once": once, "flags": on, "k": text,
                         "tclass": tclass})

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
        r["cls"] = classify(r["cast"], r["sprite"], objects, canon, voices, r["map"],
                            person=r["how"] == "전투호출")
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

        for mid, eid, want, want_how in KNOWN_BATTLE:
            hit = next((r for r in rows if r["kind"] == "battle"
                        and (r["map"], r["event"]) == (mid, eid)), None)
            got = (hit["who"], hit["how"]) if hit else ("(못찾음)", "")
            mark = "O" if got == (want, want_how) else "X"
            ok, bad = ok + (got == (want, want_how)), bad + (got != (want, want_how))
            print(f"[{mark}] 전투 맵{mid} ev{eid} {want or '화자없음'}({want_how}) "
                  f"← {got[0] or '화자없음'}({got[1]})")

        for (mid, eid), frag, want, want_how in KNOWN_JOIN:
            hit = next((r for r in rows if (r["map"], r["event"]) == (mid, eid)
                        and frag in r["k"]), None)
            got = (hit["who"], hit["how"]) if hit else ("(못찾음)", "")
            mark = "O" if got == (want, want_how) else "X"
            ok, bad = ok + (got == (want, want_how)), bad + (got != (want, want_how))
            print(f"[{mark}] 합류 맵{mid} ev{eid} {want or '화자없음'}({want_how}) "
                  f"← {got[0] or '화자없음'}({got[1]})")

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

        # 전투 호출은 그림으로 층을 가리지 않는다(Z-67). 지문층이 남으면 회귀다.
        n_battle = sum(1 for r in rows if r["how"] == "전투호출" and r["cls"] == "N")
        print(f"[{'O' if not n_battle else 'X'}] 전투호출 지문층 0 ← {n_battle}")
        ok, bad = ok + (not n_battle), bad + bool(n_battle)

        # 맵 한정 예외는 그 맵에서만 듣는다 — 밖의 숫자 그림 층 분포가 기준선이다.
        # 전투 호출은 그림을 안 보는 갈래라 이 셈에서 뺀다(사냥꾼 그림 `235` 두 줄).
        outside = collections.Counter(
            r["cls"] for r in rows
            if r["sprite"][:1].isdigit() and r["map"] not in PERSON_MAPS
            and r["sprite"] not in PERSON_SPRITES and r["how"] != "전투호출")
        want = {"N": 180, "PS": 109}       # 2026-08-18 예외 도입 직전 실측
        mark = "O" if dict(outside) == want else "X"
        ok, bad = ok + (dict(outside) == want), bad + (dict(outside) != want)
        print(f"[{mark}] 맵356 밖 숫자 그림 {want} ← {dict(outside)}")

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
