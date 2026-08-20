# /// script
# requires-python = ">=3.12"
# dependencies = ["rubymarshal"]     # modkit의 코어 판독기가 쓴다 — 기준선을 뜨는 데 필요
# ///
"""글꼴 모드 세 갈래를 보관소에 짓는다 — 한글 모양만 다른 형제들이다.

    uv run runa/make-font-mods.py [--store <보관소>]

정본은 저장소의 `mods/DPPT Font`다. 여기서는 그 카드와 스크립트를 그대로 쓰고
`Fonts/`만 고른 마스터에서 새로 찍는다. 셋은 같은 능력(`hangul-font`)을 주므로
서로를 `conflicts`로 밀어낸다 — 한 게임에 둘을 얹으면 나중 것이 앞의 것을 덮는다.

라이선스 원문도 갈래에 맞는 것만 담는다. 바탕은 늘 DPPt라 그 두 장은 항상 들어간다.

기준선(`baseline/`)도 함께 싣는다 — 이 모드가 덮어쓰는 순정 함수 넷의 원문이다.
그것이 있어야 한글패치판 위에서 `expects`가 어긋날 때 modkit이 훅 자리를 다시 대조해
넘어간다(없으면 `BaseChanged`로 멈춰 `--force`가 필요하다).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SOURCE = REPO / "mods" / "DPPT Font"
STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame")
# 순정 코어 — modkit이 처음 덮을 때 남긴 백업이다. 보관소의 한글패치 코어에서 뜨면
# 패치 지문이 박힌다(packaging 가이드 「mod.json의 expects」 절).
VANILLA = Path("/mnt/d/Game/Pokemon Z/V2.18/Data/Scripts.rxdata.orig")
MODKIT = Path(os.environ.get("MODKIT_HOME")
              or Path.home() / "workspace" / "claude-native" / "sketches" / "essentials-modkit")


def vanilla_sources(core: Path):
    """순정 코어의 (섹션 이름, 소스). modkit의 scripts.sources는 게임 폴더를 받아
    `Data/Scripts.rxdata`만 보므로 백업 파일을 직접 가리킬 수 없다."""
    sys.path.insert(0, str(MODKIT))
    from modkit import rubyread                                    # noqa: E402

    if not core.is_file():
        raise SystemExit(f"순정 코어가 없어요: {core} — 게임 설치본의 .orig 백업이 필요해요")
    for entry in rubyread.loads(core.read_bytes()):
        yield (bytes(entry[1]).decode("utf-8", "replace"),
               zlib.decompress(bytes(entry[2])).decode("utf-8", "replace"))

# 모드 이름 → (마스터 파일, 한 줄 소개, 라이선스 원문 더하기)
VARIANTS = {
    "DPPT Font": (
        "dppt-kr.ttf",
        "한글이 든 DPPt 픽셀 글꼴과, 그 획 굵기에 맞춘 글자 그림자·굵게.", []),
    # 갈무리는 **통짜**다 — DPPt에 한글만 옮겨 심은 판은 게임이 쓰는 크기에서 글자마다
    # 높이가 갈렸다(2026-08-07 유지자 실기 + 실측: 25·26·28·31픽셀에서 세 무리로 쪼개짐).
    # 원본 그대로 쓰면 어느 크기에서도 두 무리(받침 있음·없음)로만 떨어진다.
    "Galmuri Font": (
        "galmuri-kr.ttf",
        "글꼴 전체를 갈무리11로 — 옛 한글패치와 같은 글자체.",
        ["Galmuri-OFL.txt"]),
    "BW Font": (
        "bw-kr.ttf",
        "한글만 Pokemon BW로 바꾼 글꼴 — DPPt와 크기가 같다.",
        ["pokemon-bw-LICENSE.txt", "pokemon-bw-README.txt"]),
}
ALWAYS = ["pokemon-dppt-LICENSE.txt", "pokemon-dppt-README.txt"]


def main() -> None:
    ap = argparse.ArgumentParser(description="글꼴 모드 세 갈래를 짓는다")
    ap.add_argument("--store", type=Path, default=STORE)
    ap.add_argument("--vanilla", type=Path, default=VANILLA)
    args = ap.parse_args()

    sys.path.insert(0, str(MODKIT))
    from modkit import modfit                                      # noqa: E402

    scripts = [(rb.name, rb.read_text(encoding="utf-8")) for rb in sorted(SOURCE.glob("*.rb"))]
    baseline = modfit.find_methods(list(vanilla_sources(args.vanilla)),
                                   modfit.overrides(scripts))
    if not baseline:
        raise SystemExit(f"순정에서 덮어쓰는 함수를 하나도 못 찾았어요 — {args.vanilla}가 "
                         "순정이 맞는지, modkit의 자리 탐색이 최상위 def를 보는지 확인해요")

    base = json.loads((SOURCE / "mod.json").read_text(encoding="utf-8"))
    for name, (master, blurb, extra_licenses) in VARIANTS.items():
        folder = args.store / name
        if folder.exists():
            shutil.rmtree(folder)
        (folder / "Fonts").mkdir(parents=True)

        for rb in sorted(SOURCE.glob("*.rb")):
            shutil.copy2(rb, folder / rb.name)

        done = subprocess.run(
            ["uv", "run", str(HERE / "stamp-fonts.py"),
             "--master", str(HERE / "fonts" / master), "--out", str(folder / "Fonts")],
            capture_output=True, text=True)
        if done.returncode != 0:
            raise SystemExit(f"글꼴 찍기 실패({name}): {done.stderr[-400:]}")

        for fname in ALWAYS + extra_licenses:
            shutil.copy2(HERE / "fonts" / "licenses" / fname, folder / "Fonts" / fname)

        card = dict(base)
        card["name"] = name
        card["summary"] = blurb
        rivals = [one for one in VARIANTS if one != name]
        card["conflicts"] = {one: "같은 자리에 다른 한글 글꼴을 넣는 형제 모드예요." for one in rivals}
        card["assets"] = [{"file": f"Fonts/{p.name}", "install_to": f"Fonts/{p.name}"}
                          for p in sorted((folder / "Fonts").iterdir())]
        card["touches"] = {"methods": base.get("touches", {}).get("methods", []),
                           "files": [a["install_to"] for a in card["assets"]]}
        modfit.write_baseline(folder, baseline)
        card["baseline_taken"] = True
        (folder / "mod.json").write_text(
            json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        print(f"{folder} — 글꼴 {len(card['assets'])}개(라이선스 포함) · "
              f"기준선 {len(baseline)}자리")


if __name__ == "__main__":
    main()
