# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]
# ///
"""공유용 한글패치 패키지 조립.

산출: dist/<패키지명>/ — 받는 사람이 게임 폴더에 덮어쓰면 끝나는 형태.
원 패치(한글패치 통합 모드)의 에셋 전체 + 최신 korean.dat +
UI Text KR을 주입한 Scripts.rxdata + 번역표(ko JSONL)와 독립 빌더.
조사 자동 선택(옛 Josa Select)은 2026-08-03부터 한글패치 통합의 본문
섹션이라 따로 주입하지 않는다(수술판·pre-intl.bak 양쪽에 구움 — bake_josa.py).

주입은 fangame-library modstore가 정본이라 여기서 다시 만들지 않는다 —
스테이징 폴더를 게임 이름으로 만들어 modstore.apply로 얹는다(제목 판별이
Game.ini 없으면 폴더 이름 폴백인 것을 이용).

usage: uv run make_package.py [--variant debug|clean|mods] [--name "..."]

변형 (v5 배포 체계, 2026-08-03):
  debug — 통 패치: 번역 전체(수술·UI Text) + 디버그 3편집(patch_debug)
  clean — 순수 번역: 번역 에셋+dat+Scripts(원본, Josa 포함).
          보간 6곳·부적 수정·화면 한글화는 빠진다(모드 묶음이 보충).
  mods  — 스크립트 모드 묶음: 완성 Scripts.rxdata(수술+UI Text) 단품.
          clean 위에 덮어쓰면 통 패치(디버그 제외)와 같아진다.
"""
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).parent
TRANSLATE = HERE.parent / "translate"
STORE = Path("/mnt/d/GameVault/mods")
BASE_MOD = STORE / "Pokemon Z Fangame" / "한글패치 통합"
INJECT_MODS = ["UI Text KR"]
DIST = HERE / "dist"

# modstore는 vendor에 없다 — devbox의 fangame-library가 필요하다 (FANGAME_LIBRARY로 지정 가능)
_FANLIB_HOME = Path(
    os.environ.get("FANGAME_LIBRARY")
    or Path.home() / "workspace" / "claude-native" / "sketches" / "fangame-library"
)
if not (_FANLIB_HOME / "fanlib" / "modstore.py").exists():
    sys.exit(f"fangame-library를 찾지 못했습니다: {_FANLIB_HOME} — FANGAME_LIBRARY 환경변수로 경로를 주세요")
sys.path.insert(0, str(_FANLIB_HOME))
from fanlib import modstore  # noqa: E402


def _embed_manifest(final: Path, name: str):
    """패키지에 진단용 지문(manifest.json)을 동봉한다.

    스테이징 폴더만 담으므로 scope="partial" — 받는 사람의 게임 폴더에는 여기 없는
    원본 파일이 잔뜩 있고, 그것을 외래로 몰면 modkit 진단이 게임을 부순다.
    """
    modkit_home = Path(
        os.environ.get("MODKIT_HOME")
        or Path.home() / "workspace" / "claude-native" / "sketches" / "modkit"
    )
    if not (modkit_home / "modkit" / "manifest.py").exists():
        print(f"modkit을 찾지 못해 manifest.json을 건너뜁니다: {modkit_home}")
        return
    sys.path.insert(0, str(modkit_home))
    from modkit import manifest as modkit_manifest

    exclude_patterns = modkit_manifest.DEFAULT_EXCLUDE + ("번역표/*", "읽어주세요.txt")
    made = modkit_manifest.capture(
        final, game="Pokemon Z Fangame", version=name, scope="partial", exclude=exclude_patterns)
    modkit_manifest.save(made, final / "manifest.json")
    print(f"manifest.json 동봉: {len(made['files'])}개 파일 (scope=partial)")


def _run_patch_debug(scripts_path: Path):
    import subprocess
    r = subprocess.run(
        ["uv", "run", str(HERE / "patch_debug.py"), str(scripts_path)],
        capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode != 0:
        sys.exit(f"patch_debug 실패: {r.stderr[-400:]}")


def main():
    variant = "debug"
    if "--variant" in sys.argv:
        variant = sys.argv[sys.argv.index("--variant") + 1]
    default_names = {
        "full": "포켓몬Z 한글패치 v5",   # 기본판 — 디버그 없는 통합
        "debug": "포켓몬Z 한글패치 v5 (통합+디버그)",
        "clean": "포켓몬Z 한글패치 v5 (순수 번역)",
        "mods": "포켓몬Z 한글패치 v5 (스크립트 모드 묶음)",
    }
    name = default_names[variant]
    if "--name" in sys.argv:
        name = sys.argv[sys.argv.index("--name") + 1]
    stage = DIST / "Pokemon Z Fangame"  # 주입기 게임 판별용 임시 이름
    final = DIST / name
    for p in (stage, final):
        if p.exists():
            shutil.rmtree(p)
    DIST.mkdir(exist_ok=True)

    if variant == "mods":
        # 완성 Scripts 단품: 수술판(BASE_MOD 사본, Josa 내장) + UI Text KR
        (stage / "Data").mkdir(parents=True)
        shutil.copy2(BASE_MOD / "Data" / "Scripts.rxdata", stage / "Data" / "Scripts.rxdata")
        for mod in INJECT_MODS:
            r = modstore.apply(STORE / "Pokemon Z Fangame", mod, stage)
            print(f"주입: {mod} → {r['did']}")
        shutil.copy2(HERE / "읽어주세요-모드묶음.txt", stage / "읽어주세요.txt")
        stage.rename(final)
        _embed_manifest(final, name)
        size = sum(p.stat().st_size for p in final.rglob("*") if p.is_file())
        print(f"완성: {final} — {size / 1e6:.1f}MB")
        return

    # 1. 원 패치 에셋 전체 (mod.json의 install_to 그대로)
    card = json.loads((BASE_MOD / "mod.json").read_text(encoding="utf-8"))
    n = 0
    for a in card["assets"]:
        src = BASE_MOD / a["file"]
        dst = stage / a["install_to"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        n += 1
    print(f"원 패치 에셋 {n}개 복사")

    # 2. 최신 korean.dat (보관소 사본이 build.py 산출로 항상 최신)
    shutil.copy2(BASE_MOD / "Data" / "korean.dat", stage / "Data" / "korean.dat")

    # 3. Scripts 조립 — 변형별
    if variant == "clean":
        # 원본(수술 전, Josa 내장). 보간·부적·화면 한글화 제외.
        shutil.copy2(BASE_MOD / "Data" / "Scripts.rxdata.pre-intl.bak",
                     stage / "Data" / "Scripts.rxdata")
        inject = []
    else:  # full(기본판)·debug(통합+디버그) — 수술판 Scripts + 전체 주입
        inject = list(INJECT_MODS)
    for mod in inject:
        r = modstore.apply(STORE / "Pokemon Z Fangame", mod, stage)
        print(f"주입: {mod} → {r['did']}")
    if variant == "debug":
        _run_patch_debug(stage / "Data" / "Scripts.rxdata")

    # 4. 번역표 + 독립 빌더
    tbl = stage / "번역표"
    tbl.mkdir()
    for p in sorted((TRANSLATE / "ko").glob("*.jsonl")):
        shutil.copy2(p, tbl / p.name)
    # 재번역 도구 — 남이 특정 대사를 다시 번역할 때 일관성을 지켜 주는 재료
    kit = tbl / "번역 도구"
    kit.mkdir()
    for fname in ("prompt.md", "prompt-npc.md", "glossary.md", "voices.md",
                  "speaker-aliases.json", "persona-table.jsonl", "sprite-groups.json"):
        shutil.copy2(TRANSLATE / fname, kit / fname)
    for fname in ("canon.jsonl", "aliases.jsonl", "exceptions.jsonl", "messages.jsonl.gz"):
        src = TRANSLATE / "canon" / fname
        if src.exists():  # aliases는 아직 빈 개념일 수 있다
            shutil.copy2(src, kit / fname)
    shutil.copy2(HERE / "빌드.py", tbl / "빌드.py")
    shutil.copy2(HERE.resolve().parents[0] / "vendor" / "fanlib" / "rubywrite.py",
                 tbl / "rubywrite.py")
    shutil.copy2(HERE / "수정법.txt", tbl / "수정법.txt")
    shutil.copy2(HERE / "번역표-README.md", tbl / "README.md")

    # 5. 안내문 (판본 안내는 읽어주세요 본문에 통합 — 2026-08-03)
    shutil.copy2(HERE / "읽어주세요.txt", stage / "읽어주세요.txt")

    stage.rename(final)
    _embed_manifest(final, name)
    total = sum(1 for _ in final.rglob("*") if _.is_file())
    size = sum(p.stat().st_size for p in final.rglob("*") if p.is_file())
    print(f"완성: {final} — 파일 {total}개, {size / 1e6:.0f}MB")
    print("배포 전 점검: 읽어주세요.txt 버전·날짜, zip으로 묶기")


if __name__ == "__main__":
    main()
