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
