# /// script
# requires-python = ">=3.12"
# ///
"""full 매니페스트(manifest-full.json) 캡처 — 기준 배포 zip + 한글패치 적용 상태.

패키지에 동봉하던 partial 매니페스트는 패치 파일만 담아, 옛 한글패치 v3 잔재처럼
「목록 밖」에 있는 파일을 진단이 손대지 못했다. 여기서 뜨는 지문은 게임 폴더
전체(원본 19,070개 + 패치)라 잔재가 foreign으로 잡힌다.

usage: uv run make_manifest_full.py [--work <조립 폴더>] [--keep]

원본 zip 둘은 읽기만 한다. 조립 폴더는 기본으로 끝나고 지운다(--keep로 남김).
"""
import shutil
import sys
import time
import zipfile
from pathlib import Path

HERE = Path(__file__).parent
BASE_ZIP = Path("/mnt/c/Users/durumii/Downloads/POKEMON Z V2.18.zip")
PATCH_ZIP = Path("/mnt/c/Users/durumii/Downloads/pokemon-z-kr-patch-v5.1.zip")
BASE_TOP = "Pokemon Z V2.18/"
PATCH_TOP = "포켓몬Z 한글패치 v5.1/"
WORK = Path("/mnt/d/GameVault/_modkit-baseline/Pokemon Z V2.18")
OUT = HERE / "manifest-full.json"

GAME = "Pokemon Z Fangame"
VERSION = "포켓몬Z 한글패치 v5.1"

# DEFAULT_EXCLUDE에 더할 Z 전용 제외 — 게임이 스스로 만드는 세이브·흔적과
# 재생성 캐시. 한글패치 통합 모드가 통파일에서 걸러낸 목록과 같은 뿌리다.
Z_EXCLUDE = (
    "manifest.json", "번역표/*", "읽어주세요.txt",
    "Partidas Guardadas*", "showdown.txt", "progreso*.dat", "amadeus.dat",
    "Data/Constants.rxdata", "Data/MapChecker.dat", "LastSave.dat",
)


def unpack(zpath: Path, dest: Path, strip_top: str) -> int:
    """zip을 dest에 푼다(덮어쓰기). 원본 zip은 UTF-8 플래그가 없어 zipfile이
    cp437로 읽는데, 스페인어 이름 둘(Créditos·Trovão)이 그 해독으로 정확히 나온다."""
    n = 0
    with zipfile.ZipFile(zpath) as z:
        for info in z.infolist():
            assert info.filename.startswith(strip_top), info.filename
            rel = info.filename[len(strip_top):]
            if not rel:
                continue
            out = dest / rel
            if info.is_dir():
                out.mkdir(parents=True, exist_ok=True)
                continue
            out.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, open(out, "wb") as f:
                shutil.copyfileobj(src, f, 1 << 20)
            n += 1
    return n


def main():
    work = WORK
    if "--work" in sys.argv:
        work = Path(sys.argv[sys.argv.index("--work") + 1])
    sys.path.insert(0, str(Path.home() / "workspace/claude-native/sketches/essentials-modkit"))
    from modkit import manifest as mk

    t = time.time()
    work.mkdir(parents=True, exist_ok=True)
    print(f"원본 {unpack(BASE_ZIP, work, BASE_TOP)}개 ({time.time()-t:.0f}s)")
    t = time.time()
    print(f"패치 {unpack(PATCH_ZIP, work, PATCH_TOP)}개 덮어씀 ({time.time()-t:.0f}s)")

    t = time.time()
    made = mk.capture(work, game=GAME, version=VERSION, scope="full",
                      exclude=mk.DEFAULT_EXCLUDE + Z_EXCLUDE)
    mk.save(made, OUT)
    print(f"{OUT}: {len(made['files'])}개 파일 ({time.time()-t:.0f}s)")

    if "--keep" not in sys.argv:
        shutil.rmtree(work)
        print(f"조립 폴더 정리: {work}")


if __name__ == "__main__":
    main()
