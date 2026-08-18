# /// script
# requires-python = ">=3.12"
# ///
"""공용 구분 로더 — 「이 페이지의 층·장면은」과 「이 행의 말투는 어느 표로 가나」.

도구마다 다른 칸 조합으로 같은 구분을 재계산하던 것을 여기로 모은다(Z-53 설계 2절).
경계는 하나다 — **페이지 판정은 이 로더가, 행 사실(who·how·kind·sprite)은 호출자가
든 행이 준다.** 층·장면은 `pages.jsonl`(+overrides)이 정본이고, 말투 표 연결은 칸이
아니라 규칙이라 `voice_ref` 한 함수가 정본이다.

    from structure import layer, scene, voice_ref
    scene(26, 4, 0)            # '잡담'      — (맵, 이벤트, 페이지)
    layer("m3.e2.p0.c1")       # 'PS'        — 사이트 id를 줘도 그 페이지로 접힌다
    voice_ref({"how": "그림", "sprite": "campesinaw"})   # ('groups', 'campesinaw')

⚠ 페이지 판정은 페이지 단위다 — 접기에서 층이 갈린 21페이지(`mixed: true`)에서는
행별 옛 값과 다를 수 있고, **그때는 페이지 판정이 정본이다**(설계 2절).
"""
import functools
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (OUT, OVERRIDES, apply_page_overrides, read_jsonl,  # noqa: E402
                    read_overrides)

# 자리 id → 그 자리가 놓인 페이지. 끝을 잠그지 않는다 — 선택지 갈래는 `.c3.0`처럼
# 명령 아래 한 칸이 더 붙고(2,229자리), 그것도 같은 페이지의 자리다(gate.PAGE_OF와 같은 꼴).
SITE_ID = re.compile(r"^(m\d+\.e\d+\.p\d+)\.c")
PAGES = OUT / "pages.jsonl"
VOICES, GROUPS = "voices", "groups"      # 말투가 사는 두 표 — 이름표 쪽과 그림 쪽


def _stamp():
    """읽는 파일들의 지금 모습 — 밖에서 갈리면(스튜디오·gen·git) 캐시가 깨진다."""
    return tuple((p.stat().st_mtime_ns, p.stat().st_size) if p.exists() else None
                 for p in (PAGES, OVERRIDES))


@functools.cache
def _load(_stamp_key):
    rows = apply_page_overrides(read_jsonl(PAGES), read_overrides())
    return {r["id"]: r for r in rows}


def pages():
    """페이지 id → 페이지 레코드(사람 수정 얹은 판)."""
    return _load(_stamp())


def page_id(where, event=None, page=None):
    """(맵, 이벤트, 페이지) 셋이나 사이트 id를 페이지 id 한 꼴로 접는다."""
    if event is not None:
        return f"m{where}.e{event}.p{page}"
    m = SITE_ID.match(str(where))
    return m.group(1) if m else str(where)


def of(where, event=None, page=None):
    """그 페이지의 판정 레코드. 페이지 층에 없는 자리(맵 밖 절 등)는 빈 dict."""
    return pages().get(page_id(where, event, page), {})


def layer(where, event=None, page=None):
    """층 — PS(정본 인물) · PC(그 밖 인물) · N(지문). 모르는 자리는 빈 문자열."""
    return of(where, event, page).get("layer", "")


def scene(where, event=None, page=None):
    """장면 부류 — 컷신 · 잡담 · 대화 · 트레이너 · 공통. 모르는 자리는 빈 문자열."""
    return of(where, event, page).get("scene", "")


def row_layer(row):
    """한 자리의 층 — **행에 적힌 값이 먼저이고 페이지 판정이 그다음이다.**

    층은 페이지 판정이지만 예외가 행으로 산다 — 컷신 안의 화자 없는 확인창·회상 자막처럼
    사람이 행 하나만 N으로 고쳐 둔 자리가 9건 있다(overrides, 2026-08-13·08-18). 페이지
    판정으로 갈아 끼우면 그 판정이 표시에서 사라지므로 행 값을 먼저 본다. gen은 더 이상
    자리에 층을 안 싣는다(설계 3단계 완료) — 그래서 행 값이 서는 자리는 overrides 9줄과
    materials가 붙이는 화면 자리(`layer: "화면"`)뿐이다.
    """
    return row.get("layer") or layer(row.get("id", ""))


def voice_ref(row):
    """한 행의 말투가 어느 표로 가나 — (표, 그 표의 열쇠).

    이름표(`how`가 태그·상속)면 말투표(voices)를 이름으로 열고, 그림(`how="그림"`)이면
    페르소나표(groups)를 스프라이트로 연다. 그 밖(미상·선택지·지문)은 표가 없다.
    열쇠가 비어도 표는 알려 준다 — 「그림인데 스프라이트가 없다」와 「그림이 아니다」는
    거르는 자리가 다르다(batch_pages의 페르소나표 밖 셈이 그 차이를 센다).
    """
    how = row.get("how") or ""
    if how == "그림":
        return GROUPS, row.get("sprite") or ""
    if how in ("태그", "상속"):
        return VOICES, row.get("who") or ""
    return "", ""


def selftest():
    assert page_id(26, 4, 0) == page_id("m26.e4.p0.c7") == page_id("m26.e4.p0") == "m26.e4.p0"
    assert page_id("m26.e4.p0.c7.0") == "m26.e4.p0"       # 선택지 갈래도 제 페이지로
    assert page_id("s23.k0") == "s23.k0" and of("s23.k0") == {}
    assert layer("m0.e51.p0") == "N" and scene(0, 51, 0) == "공통"
    assert voice_ref({"how": "그림", "sprite": "campesinaw"}) == (GROUPS, "campesinaw")
    assert voice_ref({"how": "그림"}) == (GROUPS, "")
    assert voice_ref({"how": "상속", "who": "멜리아"}) == (VOICES, "멜리아")
    assert voice_ref({"how": "미상", "who": "멜리아"}) == ("", "")
    # 행에 적힌 층이 페이지 판정을 이긴다 — 사람이 행 하나만 고쳐 둔 자리를 안 잃는다
    assert row_layer({"id": "m0.e51.p0.c1", "layer": "PS"}) == "PS"
    assert row_layer({"id": "m0.e51.p0.c1"}) == "N"
    assert row_layer({"id": "s23.k0"}) == "" and row_layer({}) == ""
    # 사람 수정이 페이지 판정을 이긴다 — overrides 창구는 그대로 쓴다(설계 2절)
    p = apply_page_overrides([{"id": "m1.e1.p0", "layer": "N", "by": "machine/gen"}],
                             [{"id": "m1.e1.p0", "set": {"layer": "PS"}, "by": "사람/시험"}])
    assert p[0]["layer"] == "PS" and p[0]["by"] == "사람/시험", p
    n = len(pages())
    assert n > 4000, n
    print(f"structure 자체 검사 통과 — 페이지 {n}장 · id 접기 · 말투 표 연결 · overrides 우선")


if __name__ == "__main__":
    selftest()
