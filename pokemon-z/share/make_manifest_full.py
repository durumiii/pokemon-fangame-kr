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
PATCH_ZIP = HERE / "dist" / "pokemon-z-kr-patch-v6_1-galmuri.zip"
BASE_TOP = "Pokemon Z V2.18/"
PATCH_TOP = ""  # 우리 배포 zip은 게임 폴더 기준으로 평평하다
# 조립 폴더는 WSL 쪽에 둔다 — 파일 만 구천 개를 푸는 일이라 파일시스템 경계를 넘기면
# 세션이 파일 옮기기에 녹는다. 원본 zip 둘은 한 번씩 읽고 마는 것이라 괜찮다.
WORK = Path.home() / ".cache" / "z-manifest-work"
OUT = HERE / "manifest-full.json"

GAME = "Pokemon Z Fangame"
VERSION = "포켓몬Z 한글패치 v6"

# Essentials 엔진이 스스로 만들거나 다시 만드는 것 — Z 밖에서도 통할 후보라
# 언젠가 modkit 코어(DEFAULT_EXCLUDE 또는 ESSENTIALS_RUNTIME)로 올라갈 몫이다.
# 근거는 게임 스크립트 실측(Scripts.rxdata 압축 해제 후 검색):
#   Data/Constants.rxdata  — Compiler:797 save_data (PBS 컴파일 산물)
#   Data/MapChecker.dat    — Compiler:3153 save_data (pbCompileTrainerEvents 캐시)
#   *LastSave.dat          — PScreen_Load:1076이 루트에 쓰고, Scene_Intro:87·
#                            Main:9는 Data/ 쪽도 읽는다. 코어 DEFAULT_EXCLUDE의
#                            "LastSave.dat"은 루트만 걸러 Data/ 변형을 놓친다.
#   Game*.rxdata           — 세이브는 보통 Windows「저장된 게임」폴더로 가지만
#                            (SpriteWindow:604 FOLDERID_SavedGames), 그 폴더를 못
#                            쓰면 pwd="."로 떨어져 게임 폴더에 쌓인다. 예방책.
ESSENTIALS_RUNTIME = (
    "Data/Constants.rxdata", "Data/MapChecker.dat", "*LastSave.dat",
    "Game.rxdata", "Game_*.rxdata",
)

# 이 게임·이 배포판에만 있는 것.
#   번역표/*·읽어주세요.txt — 우리 패치가 동봉하는 자료
#   Data/progreso*.dat      — Titulo:378이 읽는 Z 고유 진행도(스페인어)
#   showdown.txt            — 커뮤니티 플러그인 Export to Showdown이 루트에 쓴다
#                             (Z 배포본 동봉). 다른 게임에도 흔하면 위로 옮길 것.
#   Partidas Guardadas*     — 배포본이 동봉하는 세이브 폴더 바로가기(.lnk)
#   amadeus.dat             — 출처 미확정. 스크립트 전문 검색에 한 줄도 없다.
#   mod.json·조작법.txt     — v6부터 우리가 게임 루트에 싣는 것. 읽어주세요와 같은 격이다.
#   Fonts/*                 — 글꼴 파일 열여섯은 **갈래마다 내용이 다르다**(갈무리·DPPt·
#                             BW 각 판의 한글이 같은 이름에 들어간다. 2026-08-21 실측:
#                             세 갈래에서 CRC가 같은 것은 라이선스 문서 둘뿐). 지문표는
#                             셋이 함께 쓰므로 여기서 뺀다 — 글꼴의 무결은 글꼴 모드
#                             카드의 replaces_crc가 따로 지킨다.
Z_ONLY = (
    "번역표/*", "읽어주세요.txt", "조작법.txt", "mod.json", "Fonts/*",
    "Data/progreso*.dat", "showdown.txt", "Partidas Guardadas*", "amadeus.dat",
)

Z_EXCLUDE = ESSENTIALS_RUNTIME + Z_ONLY


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
