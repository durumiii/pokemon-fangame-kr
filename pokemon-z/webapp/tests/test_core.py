import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))          # core, rubywrite
sys.path.insert(0, str(HERE.parent / "vendor"))  # rubymarshal

STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 통합/Data/korean.dat")
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
