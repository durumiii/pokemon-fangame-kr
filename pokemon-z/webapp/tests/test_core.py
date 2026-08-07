import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))          # core, rubywrite
sys.path.insert(0, str(HERE.parent / "vendor"))  # rubymarshal

STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 코어/Data/korean.dat")
MESSAGES = Path("/mnt/d/Game/Pokemon Z/V2.18/Data/messages.dat")

pytestmark = pytest.mark.skipif(not STORE.exists(), reason="실물 korean.dat 없음")


@pytest.fixture(scope="module")
def dat_bytes():
    return STORE.read_bytes()


@pytest.fixture(scope="module")
def loaded(dat_bytes):
    import core
    msg = MESSAGES.read_bytes() if MESSAGES.exists() else None
    return json.loads(core.load_dat(dat_bytes, msg))


def test_load_row_count(loaded):
    # 실전 키 2만 행 이상 (build.py 주석의 20,715개 기준 하한)
    assert len(loaded["rows"]) > 20000


def test_load_row_shape(loaded):
    r0 = next(r for r in loaded["rows"] if r["sec"] == 0)
    assert set(r0) >= {"sec", "map", "idx", "k", "v"}
    r5 = next(r for r in loaded["rows"] if r["sec"] == 5)  # 기술 이름(목록 절)
    assert "idx" in r5 and "v" in r5


def test_load_sha_and_meta(loaded):
    assert len(loaded["sha"]) == 12
    # v5 dat엔 표식이 없다 — None 허용, 있으면 문자열
    assert loaded["meta"] is None or isinstance(loaded["meta"], str)


def test_build_noop_roundtrip(dat_bytes):
    import core
    core.load_dat(dat_bytes)
    out = core.build_dat("[]")
    before = json.loads(core.load_dat(dat_bytes))["rows"]
    after = json.loads(core.load_dat(bytes(out)))["rows"]
    assert before == after  # 무수정 빌드 → 내용 동일


def test_build_single_edit(dat_bytes):
    import core
    rows = json.loads(core.load_dat(dat_bytes))["rows"]
    target = next(r for r in rows if r["sec"] == 5)  # 기술 이름 하나
    edit = dict(target, v="테스트기술XYZ")
    out = core.build_dat(json.dumps([edit]))
    rows2 = json.loads(core.load_dat(bytes(out)))["rows"]
    hit = [r for r in rows2 if r["sec"] == 5 and r["idx"] == target["idx"]]
    assert hit[0]["v"] == "테스트기술XYZ"
    assert sum(1 for a, b in zip(rows, rows2) if a != b) == 1  # 다른 행 무변화


def test_build_hash_section_edit(dat_bytes):
    import core
    rows = json.loads(core.load_dat(dat_bytes))["rows"]
    target = next(r for r in rows if r["sec"] == 23)
    out = core.build_dat(json.dumps([dict(target, v="교체된 값")]))
    rows2 = json.loads(core.load_dat(bytes(out)))["rows"]
    hit = next(r for r in rows2 if r["sec"] == 23 and r["idx"] == target["idx"])
    assert hit["v"] == "교체된 값" and hit["k"] == target["k"]


def test_build_key_mismatch_rejected(dat_bytes):
    import core
    rows = json.loads(core.load_dat(dat_bytes))["rows"]
    target = next(r for r in rows if r["sec"] == 23)
    bad = dict(target, k="엉뚱한 원문", v="아무거나")
    with pytest.raises(ValueError):
        core.build_dat(json.dumps([bad]))


# ── 딱지판(루비 1.9+ 실행기용 korean.dat) ────────────────────────────────
RUNA = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 코어/Data/korean.dat")


@pytest.fixture(scope="module")
def runa_bytes():
    if not RUNA.exists():
        pytest.skip("딱지판 korean.dat 없음")
    return RUNA.read_bytes()


def test_tagged_dat_loads(runa_bytes):
    """딱지가 붙으면 판독기가 문자열을 str로 준다 — bytes()로 감싸면 TypeError로 죽었다."""
    import core
    got = json.loads(core.load_dat(runa_bytes))
    assert got["rows"] and core._state["tagged"] is True
    assert all(isinstance(r["v"], str) for r in got["rows"][:50])


def test_tagged_dat_keeps_tags_after_edit(runa_bytes):
    """고친 줄만 딱지가 빠지면 그 줄에서만 인코딩이 어긋난다."""
    import core
    rows = json.loads(core.load_dat(runa_bytes))["rows"]
    target = next(r for r in rows if r["sec"] == 5)
    out = core.build_dat(json.dumps([dict(target, v="딱지시험")]))
    again = json.loads(core.load_dat(bytes(out)))
    assert core._state["tagged"] is True          # 다시 열어도 딱지판이다
    hit = next(r for r in again["rows"] if r["sec"] == 5 and r["idx"] == target["idx"])
    assert hit["v"] == "딱지시험"


@pytest.fixture(scope="module")
def untagged_bytes(dat_bytes):
    """딱지 없는 판 — 배포 dat가 딱지판 하나로 합쳐져 실물이 없으므로 여기서 만든다.

    core.tag_utf8의 반대 — 문자열을 바이트열로 되돌리면 rubymarshal이 딱지 없이 쓴다.
    """
    import core
    import rubywrite

    def untag(o):
        if isinstance(o, list):
            return [untag(x) for x in o]
        if hasattr(o, "_private_data"):
            o._private_data = rubywrite.dumps(untag(core._inner(o)))
            return o
        # str·bytes·RubyString(딱지 붙은 문자열) 모두 맨 바이트열로
        return core._raw(o) if isinstance(o, (str, bytes, bytearray)) or hasattr(o, "text") else o

    core.load_dat(dat_bytes)
    return rubywrite.dumps(untag(core._state["d"]))


def test_untagged_dat_stays_untagged(untagged_bytes):
    """딱지 없는 판을 열어 고치면 딱지를 새로 붙이지 않는다."""
    import core
    rows = json.loads(core.load_dat(untagged_bytes))["rows"]
    assert core._state["tagged"] is False
    target = next(r for r in rows if r["sec"] == 5)
    out = core.build_dat(json.dumps([dict(target, v="딱지없음시험")]))
    core.load_dat(bytes(out))
    assert core._state["tagged"] is False
