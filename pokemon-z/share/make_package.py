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

usage: uv run make_package.py [--variant runa|debug|clean|mods] [--font dppt|galmuri|bw]
                             [--name "..."]

변형 (v5 배포 체계, 2026-08-03):
  debug — 통 패치: 번역 전체(수술·UI Text) + 디버그 3편집(patch_debug)
  clean — 순수 번역: 번역 에셋+dat+Scripts(원본, Josa 포함).
          보간 6곳·부적 수정·화면 한글화는 빠진다(모드 묶음이 보충).
  mods  — 스크립트 모드 묶음: 완성 Scripts.rxdata(수술+UI Text) 단품.
          clean 위에 덮어쓰면 통 패치(디버그 제외)와 같아진다.

  runa  — 합본(v5.2.1~): 한글패치 통합-Runa + UI Text KR + Z-GUI + DPPT Font를
          한 벌로 묶는다. 번역표에 UTF-8 인코딩 딱지가 붙어 있어 최신 루비
          실행기에서도 돈다. `--font`로 한글 글꼴을 골라 세 벌을 낸다 —
          담기는 글꼴은 라틴·부호가 모두 DPPt이고 한글 음절만 다르다.
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
VARIANT_SUMMARY = {
    "debug": "포켓몬 Z 한글패치 — 번역 전체에 디버그 편집을 얹은 통 패치",
    "full": "포켓몬 Z 한글패치 — 번역 전체(주연 대사 재번역 반영)",
    "clean": "포켓몬 Z 한글패치 — 순수 번역만(스크립트 수술 없음)",
    "mods": "포켓몬 Z 한글패치 — 스크립트 모드 묶음(완성 Scripts 단품)",
    "runa": "포켓몬 Z 한글패치 — 번역·화면 한글화·GUI·글꼴 합본",
    "runa-debug": "포켓몬 Z 한글패치 — 합본 위에 덮는 디버그 코어 단품",
}
DIST = HERE / "dist"

# ─ 합본(runa) 전용 ───────────────────────────────────────────────────────────
RUNA_MOD = STORE / "Pokemon Z Fangame" / "한글패치 통합-Runa"
RUNA_INJECT = ["UI Text KR", "DPPT Font"]
RUNA_ASSET_MODS = ["Z-GUI"]                       # 파일만 얹는 모드 — 번역 자산 뒤에 덮는다
# 원본 배포판의 실행 설정을 한 판만 함께 싣는다. v5.1·v5.2가 넣었던 `fontSub`(글꼴 이름
# 14종을 Galmuri11로 꺾는 표)를 걷어 내려는 것 — v5.2.1부터는 글꼴 파일이 그 이름을 직접
# 들기 때문에 표가 남아 있으면 새 글꼴이 옛 Galmuri11로 되돌아간다. 원본과 우리 옛 판의
# 차이는 그 표와 기본값과 같은 smoothScaling 한 줄뿐이라, 원본을 그대로 덮어도 잃는 설정이
# 없다(2026-08-07 실측). ⚠ 옛 판에서 올라오는 사람이 한 바퀴 지나면 **다음 판에서 뺀다**.
VANILLA_MKXP = HERE / "vanilla" / "mkxp.json"
# 글꼴 갈래 — 이름표, 마스터 파일, 안내문에 쓸 한 줄.
FONT_VARIANTS = {
    "dppt": ("DPPt", "dppt-kr.ttf", "DPPt 원판 한글"),
    "galmuri": ("갈무리", "galmuri-kr.ttf", "갈무리11 한글"),
    "bw": ("BW", "bw-kr.ttf", "Pokemon BW 한글"),
}
# 배포 화면에 세울 차례 — 권하는 것이 맨 위다(유지자 실기 판단, 2026-08-07).
FONT_ORDER = {"galmuri": 1, "dppt": 2, "bw": 3}
# 재배포 조건이 붙은 글꼴의 라이선스 원문 — 함께 담지 않으면 조건을 어긴다.
FONT_LICENSES = [
    BASE_MOD / "Fonts" / "pokemon-dppt-LICENSE.txt",
    BASE_MOD / "Fonts" / "pokemon-dppt-README.txt",
]

# modstore는 vendor에 없다 — devbox의 fangame-library가 필요하다 (FANGAME_LIBRARY로 지정 가능)
_FANLIB_HOME = Path(
    os.environ.get("FANGAME_LIBRARY")
    or Path.home() / "workspace" / "claude-native" / "fangame-library"
)
if not (_FANLIB_HOME / "fanlib" / "modstore.py").exists():
    sys.exit(f"fangame-library를 찾지 못했습니다: {_FANLIB_HOME} — FANGAME_LIBRARY 환경변수로 경로를 주세요")
sys.path.insert(0, str(_FANLIB_HOME))
from fanlib import modstore  # noqa: E402


def _embed_card(final: Path, name: str, variant: str):
    """모드 카드(mod.json)를 동봉한다 — 받는 사람이 modkit으로 설치할 수 있게.

    패키지는 게임 폴더에 그대로 덮는 배치라, 카드의 `file`과 `install_to`가 같다.
    카드에 적을 목록은 **실제로 담긴 파일을 훑어서** 만든다 — 변형마다 Scripts와
    에셋 구성이 달라 보관소 카드를 그대로 베끼면 어긋난다.
    """
    # modkit-owners.json은 주입기가 스테이징에 남긴 제 장부다 — 배포물에 실리면
    # 받는 쪽 게임의 장부를 덮고, 그 자리가 어긋나 제거가 「반쪽」으로 막힌다(실측).
    skip = {"mod.json", "manifest.json", "읽어주세요.txt", "modkit-owners.json"}
    assets = []
    for f in sorted(final.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(final).as_posix()
        if rel in skip or rel.startswith("번역표/"):
            continue
        assets.append({"file": rel, "install_to": rel})
    card = {
        "name": name,
        "game": "Pokemon Z Fangame",
        "version": name,
        "summary": VARIANT_SUMMARY[variant],
        "description": (HERE / "읽어주세요.txt").read_text(encoding="utf-8").split("\n\n")[0],
        "install": "assets",
        "scripts": [],                       # 에셋형 — Scripts.rxdata도 통째로 얹는다
        "assets": assets,
        "touches": {"methods": [], "files": [a["install_to"] for a in assets]},
    }
    if variant == "runa":
        # 합본이 이미 품고 있는 것 — 능력으로 밝히고, 같은 것을 또 얹지 못하게 막는다.
        card["provides"] = ["hangul-font", "ui-text-kr", "korean-patch"]
        swallowed = "합본이 같은 것을 이미 품고 있어서 따로 얹으면 서로 덮어써요."
        card["conflicts"] = {one: swallowed for one in
                             ("DPPT Font", "UI Text KR", "Z-GUI",
                              "한글패치 통합", "한글패치 통합-Runa")}
    (final / "mod.json").write_text(
        json.dumps(card, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"mod.json 동봉: 에셋 {len(assets)}개 (모드로도 설치된다)")


def _embed_manifest(final: Path, name: str):
    """패키지에 진단용 지문(manifest.json)을 동봉한다.

    정본은 make_manifest_full.py가 뜬 manifest-full.json — 원본 배포 zip에 v5.1을
    얹은 게임 폴더 전체(scope="full")라, 옛 한글패치 v3 잔재처럼 패치가 덮지 않는
    자리의 파일도 외래로 잡힌다. 그게 없으면 스테이징 폴더만 담은 partial로
    떨어진다 — 목록 밖 파일은 진단이 손대지 않는다(안전하지만 잔재를 못 본다).
    """
    full = HERE / "manifest-full.json"
    if full.exists():
        made = json.loads(full.read_text(encoding="utf-8"))
        made["version"] = name
        (final / "manifest.json").write_text(
            json.dumps(made, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"manifest.json 동봉: {len(made['files'])}개 파일 (scope=full)")
        return

    modkit_home = Path(
        os.environ.get("MODKIT_HOME")
        or Path.home() / "workspace" / "claude-native" / "sketches" / "essentials-modkit"
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


def _zip(final: Path, asset: str):
    """배포 자산 zip을 뜬다 — 안은 게임 폴더 기준의 평평한 구조다(감싸는 폴더 없음).

    받는 사람이 압축을 풀어 게임 폴더에 그대로 덮는 배치라, 한 겹 더 씌우면
    옮겨 담는 손이 한 번 더 든다.
    """
    import zipfile

    out = DIST / f"{asset}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(final.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(final).as_posix())
    print(f"zip: {out.name} — {out.stat().st_size / 1e6:.1f}MB")


def _scrub_stage(stage: Path):
    """주입기가 스테이징에 남긴 제 작업 파일을 걷어 낸다.

    modstore.apply는 설치본을 다루는 도구라 백업(`.orig`)과 소유 장부
    (`modkit-owners.json`)를 함께 남긴다. 스테이징은 설치본이 아니라 **배포물의
    재료**인데, 그것을 그대로 담으면 받는 쪽에 실려 간다. 실제로 그랬다:

      · `Data/Scripts.rxdata.orig` — v5.2 배포물 셋에 이미 실려 나갔다. 설치하면
        modkit이 방금 뜬 진짜 순정 백업을 `.orig.orig`로 밀어내고 이 파일이 그
        자리를 차지한다. 그다음 제거는 순정 대신 **번역판 코어를 「복원」한다**
        (2026-08-07 실측: 네 단계를 밟고 코어가 255가 아니라 256으로 남았다).
      · `modkit-owners.json` — 받는 쪽 장부를 덮어 제거가 「반쪽」으로 막힌다.
    """
    junk = [p for p in stage.rglob("*") if p.is_file() and (
        p.name == "modkit-owners.json" or p.name.endswith(".orig")
        or ".pre-" in p.name or ".bak-" in p.name)]
    for p in junk:
        p.unlink()
    if junk:
        print(f"주입기 작업 파일 {len(junk)}개 걷어 냄: "
              + ", ".join(sorted(p.name for p in junk)[:4]))


def _settle_injections(scripts_path: Path):
    """주입으로 들어온 섹션의 `MOD:` 표를 뗀다 — 합본의 제 살이 되게.

    modkit은 코어를 통째로 갈아 끼울 때 **교체본이 싣고 온 남의 주입 섹션을 뺀다**
    (남의 조립 흔적이 유저 모르게 설치되는 것을 막는 규칙이다). 표를 단 채로 두면
    합본을 modkit으로 설치할 때 화면 한글화와 글꼴 스크립트가 통째로 걷힌다 — 실측.

    합본에서 이 셋은 「설치된 남의 모드」가 아니라 합본 자신의 코드다. 그래서 표를
    떼어 평범한 섹션으로 만든다. 대신 카드가 그 능력을 `provides`로 밝히고, 같은 것을
    또 얹지 못하게 `conflicts`로 막는다.
    """
    sys.path.insert(0, str(HERE.parent / "vendor"))
    from rubymarshal.reader import load                       # noqa: E402
    from fanlib import rubywrite                              # noqa: E402

    with open(scripts_path, "rb") as fh:
        rows = load(fh)
    renamed = 0
    for row in rows:
        name = row[1]
        text = name.text if hasattr(name, "text") else \
            (name.decode("utf-8", "replace") if isinstance(name, (bytes, bytearray)) else str(name))
        if text.startswith("MOD:"):
            row[1] = text[len("MOD:"):].encode("utf-8")
            renamed += 1
    scripts_path.write_bytes(rubywrite.dumps(rows))
    print(f"주입 섹션 {renamed}개를 합본 자체 섹션으로 굳힘")


def _bundle_extras(stage: Path, font: str):
    """합본에만 붙는 것 — GUI 그림, 고른 글꼴 16벌, 글꼴 라이선스 원문.

    글꼴은 주입기가 DPPT Font의 기본판을 이미 깔아 뒀더라도 여기서 다시 찍어 덮는다.
    고른 마스터에서 매번 새로 찍으므로 갈래가 섞일 여지가 없다.
    """
    import subprocess

    for mod in RUNA_ASSET_MODS:          # 번역 자산 위에 덮는다 — 순서가 곧 층이다
        card = json.loads((STORE / "Pokemon Z Fangame" / mod / "mod.json").read_text("utf-8"))
        for a in card["assets"]:
            dst = stage / a["install_to"]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(STORE / "Pokemon Z Fangame" / mod / a["file"], dst)
        print(f"{mod} 그림 {len(card['assets'])}장 덮음")

    runa = HERE.parent / "runa"
    master = runa / "fonts" / FONT_VARIANTS[font][1]
    if not master.exists():
        sys.exit(f"글꼴 마스터가 없어요: {master} — runa/make-hangul-variant.py로 먼저 만들어요")
    r = subprocess.run(
        ["uv", "run", str(runa / "stamp-fonts.py"),
         "--master", str(master), "--out", str(stage / "Fonts")],
        capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"글꼴 찍기 실패: {r.stderr[-400:]}")
    print(f"글꼴 {FONT_VARIANTS[font][2]} — {r.stdout.strip().splitlines()[0]}")

    keep = ["pokemon-dppt-LICENSE.txt", "pokemon-dppt-README.txt"]   # 바탕은 늘 DPPt다
    if font == "bw":
        keep += ["pokemon-bw-LICENSE.txt", "pokemon-bw-README.txt"]
    if font == "galmuri":
        keep += ["Galmuri-OFL.txt"]
    for fname in keep:
        shutil.copy2(runa / "fonts" / "licenses" / fname, stage / "Fonts" / fname)
    print(f"글꼴 라이선스 {len(keep)}장 동봉")

    if not VANILLA_MKXP.exists():
        sys.exit(f"원본 실행 설정이 없어요: {VANILLA_MKXP}")
    shutil.copy2(VANILLA_MKXP, stage / "mkxp.json")
    print("원본 mkxp.json 동봉 — 옛 판의 fontSub를 걷는다(다음 판에서 뺄 것)")


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
    font = "dppt"
    if "--font" in sys.argv:
        font = sys.argv[sys.argv.index("--font") + 1]
        if font not in FONT_VARIANTS:
            sys.exit(f"--font은 {'·'.join(FONT_VARIANTS)} 중 하나예요")
    label = FONT_VARIANTS[font][0]
    # 릴리스 화면은 자산을 **파일 이름순**으로 늘어놓는다(라벨 순서가 아니다). 받는 쪽이
    # 위에서부터 읽으면 되도록 이름에 차례를 넣는다 — 권하는 것이 맨 위다.
    asset_names = {
        "runa": f"pokemon-z-kr-patch-v5.2.1_{FONT_ORDER[font]}-{font}",
        "runa-debug": "pokemon-z-kr-patch-v5.2.1_4-debug-add",
    }
    default_names = {
        "full": "포켓몬Z 한글패치 v5.2",   # 기본판 — 디버그 없는 통합
        "debug": "포켓몬Z 한글패치 v5.2 (통합+디버그)",
        "clean": "포켓몬Z 한글패치 v5.2 (순수 번역)",
        "mods": "포켓몬Z 한글패치 v5.2 (스크립트 모드 묶음)",
        "runa": f"포켓몬Z 한글패치 v5.2.1 ({label})",
        "runa-debug": "포켓몬Z 한글패치 v5.2.1 (디버그 추가)",
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

    if variant in ("mods", "runa-debug"):
        # 완성 Scripts 단품 — 합본 위에 이 파일만 덮으면 된다.
        # 디버그 추가판은 글꼴과 무관하다(글꼴은 Fonts의 ttf일 뿐 코어에 안 들어간다) —
        # 그래서 세 갈래 어디에 얹어도 같은 파일 하나로 통한다.
        core = RUNA_MOD if variant == "runa-debug" else BASE_MOD
        (stage / "Data").mkdir(parents=True)
        shutil.copy2(core / "Data" / "Scripts.rxdata", stage / "Data" / "Scripts.rxdata")
        for mod in (RUNA_INJECT + ["디버그 모드"] if variant == "runa-debug" else INJECT_MODS):
            r = modstore.apply(STORE / "Pokemon Z Fangame", mod, stage)
            print(f"주입: {mod} → {r['did']}")
        if variant == "runa-debug":
            _settle_injections(stage / "Data" / "Scripts.rxdata")
            # 주입기가 DPPT Font의 글꼴 16벌까지 들여놓는다 — 여기서는 코어만 낸다.
            for junk in sorted(stage.rglob("*"), reverse=True):
                if junk.name != "Scripts.rxdata" and junk != stage / "Data":
                    junk.unlink() if junk.is_file() else junk.rmdir()
            shutil.copy2(HERE / "읽어주세요-디버그추가.txt", stage / "읽어주세요.txt")
        else:
            shutil.copy2(HERE / "읽어주세요-모드묶음.txt", stage / "읽어주세요.txt")
        _scrub_stage(stage)
        stage.rename(final)
        _embed_manifest(final, name)
        _embed_card(final, name, variant)
        size = sum(p.stat().st_size for p in final.rglob("*") if p.is_file())
        print(f"완성: {final} — {size / 1e6:.1f}MB")
        if "--zip" in sys.argv:
            _zip(final, asset_names.get(variant, name))
        return

    base = RUNA_MOD if variant == "runa" else BASE_MOD

    # 1. 원 패치 에셋 전체 (mod.json의 install_to 그대로)
    card = json.loads((base / "mod.json").read_text(encoding="utf-8"))
    n = 0
    for a in card["assets"]:
        src = base / a["file"]
        dst = stage / a["install_to"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        n += 1
    print(f"원 패치 에셋 {n}개 복사")

    # 2. 최신 korean.dat (보관소 사본이 build.py 산출로 항상 최신)
    shutil.copy2(base / "Data" / "korean.dat", stage / "Data" / "korean.dat")

    # 3. Scripts 조립 — 변형별
    if variant == "clean":
        # 원본(수술 전, Josa 내장). 보간·부적·화면 한글화 제외.
        shutil.copy2(BASE_MOD / "Data" / "Scripts.rxdata.pre-intl.bak",
                     stage / "Data" / "Scripts.rxdata")
        inject = []
    elif variant == "runa":
        inject = list(RUNA_INJECT)
    else:  # full(기본판)·debug(통합+디버그) — 수술판 Scripts + 전체 주입
        inject = list(INJECT_MODS)
    for mod in inject:
        r = modstore.apply(STORE / "Pokemon Z Fangame", mod, stage)
        print(f"주입: {mod} → {r['did']}")
    if variant == "debug":
        _run_patch_debug(stage / "Data" / "Scripts.rxdata")
    if variant == "runa":
        _settle_injections(stage / "Data" / "Scripts.rxdata")
        _bundle_extras(stage, font)

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

    _scrub_stage(stage)
    stage.rename(final)
    _embed_manifest(final, name)
    _embed_card(final, name, variant)
    total = sum(1 for _ in final.rglob("*") if _.is_file())
    size = sum(p.stat().st_size for p in final.rglob("*") if p.is_file())
    print(f"완성: {final} — 파일 {total}개, {size / 1e6:.0f}MB")
    if "--zip" in sys.argv:
        _zip(final, asset_names.get(variant, name))
    else:
        print("배포 전 점검: 읽어주세요.txt 버전·날짜, --zip으로 묶기")


if __name__ == "__main__":
    main()
