# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Z-74 그림 자산 71장을 Z-GUI 모드에 반입한다.

원장(translate/data/asset-texts.jsonl)의 71장을 생성 폴더에서 코어 모드의
Graphics/Pictures/로 복사한다. 원장 in_core가 참인 46장은 이미 mod.json에 항목이
있어 파일만 갈아 끼우고, 거짓인 25장은 assets 배열에 항목을 새로 넣는다.
새 항목의 replaces_crc는 바닐라 원본의 CRC32 — 설치본에 `.orig`가 있으면 그것,
없으면 아직 안 덮은 설치본 파일에서 잰다.

mod.json은 보관소와 repo(mods/Z-GUI/mod.json) 양쪽을 같은 내용으로 갱신한다.

    uv run translate/assets/install_assets.py            # 표만 찍는다(기본)
    uv run translate/assets/install_assets.py --write    # 실제로 복사·갱신
"""
import argparse, json, shutil, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "translate/data/asset-texts.jsonl"
INSTALL = Path("/mnt/d/Game/Pokemon Z/V2.18/Graphics/Pictures")
CORE = Path("/mnt/d/GameVault/mods/Pokemon Z Fangame/Z-GUI")
REPO_MOD = ROOT / "mods/Z-GUI/mod.json"
DEFAULT_CARDS = Path(__file__).resolve().parents[2] / "mods/Z-GUI/Graphics/Pictures"  # 정본

# 원장에 없는 그림 자산 — 글자가 아니라 자리를 고친 것이라 문안 행이 없다.
# 산출은 각자 제 생성기가 낸다(mapRegion0.png ← gen_regionmap.py).
EXTRA = ["mapRegion0.png"]


def vanilla_crc(name):
    """바닐라 원본의 CRC32 — `.orig`가 있으면 그것이 바닐라, 없으면 설치본 본 파일."""
    for p in (INSTALL / (name + ".orig"), INSTALL / name):
        if p.exists():
            return zlib.crc32(p.read_bytes()) & 0xFFFFFFFF, p
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cards", default=str(DEFAULT_CARDS), help="완성본 폴더")
    ap.add_argument("--write", action="store_true", help="실제로 복사·갱신한다")
    a = ap.parse_args()
    cards = Path(a.cards)

    mod = json.loads(REPO_MOD.read_text(encoding="utf-8"))
    have = {x["install_to"] for x in mod["assets"]}
    rows = [json.loads(l) for l in LEDGER.open(encoding="utf-8")]
    rows += [{"file": n} for n in EXTRA]

    copy, new, missing, crc_fail = [], [], [], []
    for r in rows:
        if r.get("owner"):  # 다른 모드 소유 자산 — Z-GUI 반입 대상 아님
            continue
        name = r["file"]
        src = cards / name
        if not src.exists():
            missing.append(name); continue
        dest = f"Graphics/Pictures/{name}"
        copy.append((src, dest))
        if dest in have:
            continue
        entry = {"file": dest, "install_to": dest}
        crc, from_p = vanilla_crc(name)
        if crc is None:
            crc_fail.append(name)
        else:
            entry["replaces_crc"] = crc
        new.append((entry, from_p))

    print(f"완성본 폴더 {cards}")
    print(f"복사 대상 {len(copy)}장 — 교체 {len(copy)-len(new)} · 신규 {len(new)}")
    if missing:
        print(f"완성본 없음 {len(missing)}장: {', '.join(missing)}")
    if crc_fail:
        print(f"CRC 산출 실패 {len(crc_fail)}장: {', '.join(crc_fail)}")
    print("\n신규 mod.json 항목:")
    for entry, from_p in new:
        print(f"  {entry['install_to']}  crc={entry.get('replaces_crc','—')}"
              f"  (원본 {from_p.name if from_p else '없음'})")

    if not a.write:
        print("\n--dry-run(기본): 아무것도 쓰지 않았다. 실제 반입은 --write.")
        return

    pics = CORE / "Graphics/Pictures"
    pics.mkdir(parents=True, exist_ok=True)
    for src, dest in copy:
        shutil.copy2(src, CORE / dest)
    if new:
        mod["assets"] = sorted(mod["assets"] + [e for e, _ in new],
                               key=lambda x: x["install_to"])
        text = json.dumps(mod, ensure_ascii=False, indent=2) + "\n"
        for p in (REPO_MOD, CORE / "mod.json"):
            p.write_text(text, encoding="utf-8")
    print(f"\n복사 {len(copy)}장 · mod.json 항목 +{len(new)} (repo·보관소 양쪽)")


if __name__ == "__main__":
    main()
