# /// script
# requires-python = ">=3.12"
# ///
"""글꼴 모드 세 갈래를 보관소에 짓는다 — 한글 모양만 다른 형제들이다.

    uv run runa/make-font-mods.py [--store <보관소>]

정본은 저장소의 `mods/DPPT Font`다. 여기서는 그 카드와 스크립트를 그대로 쓰고
`Fonts/`만 고른 마스터에서 새로 찍는다. 셋은 같은 능력(`hangul-font`)을 주므로
서로를 `conflicts`로 밀어낸다 — 한 게임에 둘을 얹으면 나중 것이 앞의 것을 덮는다.

라이선스 원문도 갈래에 맞는 것만 담는다. 바탕은 늘 DPPt라 그 두 장은 항상 들어간다.
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SOURCE = REPO / "mods" / "DPPT Font"
STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame")

# 모드 이름 → (마스터 파일, 한 줄 소개, 라이선스 원문 더하기)
VARIANTS = {
    "DPPT Font": (
        "dppt-kr.ttf", "한글도 DPPt 원판 글꼴이에요.", []),
    "DPPT Font (갈무리 한글)": (
        "galmuri-kr.ttf", "한글만 갈무리11로 바꿨어요 — 셋 중 가장 또렷하고, 글자가 "
        "1픽셀 넓어 줄이 조금 길어져요.", ["Galmuri-OFL.txt"]),
    "DPPT Font (BW 한글)": (
        "bw-kr.ttf", "한글만 Pokemon BW로 바꿨어요 — DPPt와 크기가 같아 줄 길이가 "
        "변하지 않아요.", ["pokemon-bw-LICENSE.txt", "pokemon-bw-README.txt"]),
}
ALWAYS = ["pokemon-dppt-LICENSE.txt", "pokemon-dppt-README.txt"]


def main() -> None:
    ap = argparse.ArgumentParser(description="글꼴 모드 세 갈래를 짓는다")
    ap.add_argument("--store", type=Path, default=STORE)
    args = ap.parse_args()

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
        card["summary"] = f"{base['summary'][:-1]} {blurb}"
        rivals = [one for one in VARIANTS if one != name]
        card["conflicts"] = {one: "같은 자리에 다른 한글 글꼴을 넣는 형제 모드예요." for one in rivals}
        card["assets"] = [{"file": f"Fonts/{p.name}", "install_to": f"Fonts/{p.name}"}
                          for p in sorted((folder / "Fonts").iterdir())]
        card["touches"] = {"methods": [], "files": [a["install_to"] for a in card["assets"]]}
        (folder / "mod.json").write_text(
            json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        print(f"{folder} — 글꼴 {len(card['assets'])}개(라이선스 포함)")


if __name__ == "__main__":
    main()
