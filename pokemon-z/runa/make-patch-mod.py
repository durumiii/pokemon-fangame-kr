# /// script
# requires-python = ">=3.12"
# ///
"""한글패치 코어 모드를 보관소에 조립한다.

담는 것은 셋이다.

  번역표 `Data/korean.dat` — 정본(translate/ko/)에서 새로 굽는다. 이 갈래의 build.py는
                             문자열에 UTF-8 인코딩 딱지를 붙인다(루비 1.9+ 실행기용).
  번역된 코어·맵        — 지금 배포 중인 「한글패치 코어」의 것을 그대로 가져온다.
  번역 자산(그림·소리)  — 마찬가지. 상류 배포물이 디스크에 없어 이것이 유일본이다.

폰트는 담지 않는다 — DPPT Font 모드의 몫이고, 카드가 그것을 `requires`로 가리킨다.
mkxp.json도 담지 않는다(순정과 동작이 같아 덮을 이유가 없다).

    uv run runa/make-patch-mod.py [--dry-run]

카드(mod.json)는 저장소가 정본이다. 에셋 목록만 여기서 기계로 채우고 — 자리마다 순정의
CRC32를 떠 넣는다 — 나머지 필드는 손으로 적은 것을 그대로 둔다.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

NAME = "한글패치 코어"
HERE = Path(__file__).resolve().parent
REPO = HERE.parent                                     # pokemon-z/
CARD = REPO / "mods" / NAME / "mod.json"
STORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame") / NAME
# 재료는 제 폴더다. 옛 「한글패치 코어」에서 떠 오던 것인데, 둘이 mod.json 말고는
# 바이트까지 같아져(2026-08-07 전수 대조) 하나만 남겼다. 번역표는 어차피 정본에서
# 새로 굽고 나머지는 그대로 옮기므로, 제자리 재조립이라도 결과가 달라지지 않는다.
SOURCE = STORE
# 원본 지문은 **지문표**에서 뜬다. 설치본에서 뜨면 이미 얹혀 있는 모드의 자국을
# 원본으로 새긴다 — 실제로 한 번 그랬고(2026-08-07), 호환 검사가 그것을 잡아냈다.
MANIFEST = Path("/mnt/d/GameVault/manifests/pokemon-z/V2.18-정본.json")

# 가져오지 않는 것 — 폰트는 DPPT Font 몫, mkxp.json은 순정과 같다, 나머지는 부스러기.
SKIP_DIRS = {"Fonts"}
SKIP_NAMES = {"mkxp.json", "mod.json", "읽어주세요.txt"}
SKIP_SUFFIX = (".bak", ".draft", ".orig")


def wanted(path: Path) -> bool:
    rel = path.relative_to(SOURCE)
    if rel.parts[0] in SKIP_DIRS or rel.name in SKIP_NAMES:
        return False
    if rel.name.endswith(SKIP_SUFFIX) or ".bak-" in rel.name or ".pre-" in rel.name:
        return False
    return True


def main() -> None:
    dry = "--dry-run" in sys.argv
    picked = sorted(p for p in SOURCE.rglob("*") if p.is_file() and wanted(p))
    rels = [str(p.relative_to(SOURCE)).replace("\\", "/") for p in picked]
    dat = "Data/korean.dat"
    assert dat in rels, "번역표가 원본 모드에 없어요 — 경로를 확인해요"

    print(f"가져올 파일 {len(rels)}개 (번역표는 새로 굽는다)")
    if dry:
        for rel in rels[:5]:
            print("  ", rel)
        print("   …")
        return

    if STORE.exists():
        shutil.rmtree(STORE)
    for src, rel in zip(picked, rels):
        target = STORE / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)

    # 번역표만은 사본이 아니라 정본에서 새로 굽는다.
    built = subprocess.run(
        ["uv", "run", "translate/build.py", f"--out={STORE / dat}"],
        cwd=REPO, check=True, capture_output=True, text=True)
    print(built.stdout.strip())

    vanilla = json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]
    assets = []
    for rel in rels:
        one = {"file": rel, "install_to": rel}
        if rel in vanilla:                     # 순정에 없던 자리는 대조할 원본이 없다
            one["replaces_crc"] = vanilla[rel][1]
        assets.append(one)

    card = json.loads(CARD.read_text(encoding="utf-8"))
    card["assets"] = assets
    card["touches"] = {"methods": [], "files": [a["install_to"] for a in assets]}
    CARD.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(CARD, STORE / "mod.json")

    crc = sum("replaces_crc" in a for a in assets)
    print(f"{STORE} — 에셋 {len(assets)}개 · 그중 순정을 덮는 자리 {crc}개")


if __name__ == "__main__":
    main()
