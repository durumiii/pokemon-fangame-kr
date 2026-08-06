#!/usr/bin/env bash
# 루나판 되살리기 — 모드 설치·제거 사고로 망가졌을 때 한 번에 원상 복구한다.
#
# 왜 필요한가: 루나판은 이미 패치가 얹힌 V2.18을 하드링크로 복제해 만든 두 번째 버전이라
# 「내가 설치한 적이 없다」는 이력이 없다. modkit은 `.orig` 백업이 있으면 자기가 설치한
# 것으로 보고 되돌려 버린다(modassets.remove). 그때 우리 커스텀 셋 — 인코딩 딱지 dat ·
# 개명 폰트 16벌 · fontSub 없는 mkxp.json — 이 통째로 사라진다.
#
# 이 스크립트는 세 곳에서 되받아 온다:
#   ① 데스크톱 설치본 V2.18 — 자산·스크립트·층 보관본의 정본
#   ② 모드 보관소 「한글패치 통합 (루나)」 — 우리 커스텀 셋의 정본
#   ③ 정본 저장소 — dat를 다시 굽는다(브랜치 runa-utf8)
#
# 쓰기: bash share/restore-runa.sh [--full]
#   기본은 커스텀 셋만 되돌린다(빠름). --full은 자산·스크립트·층 보관본까지 전부 맞춘다.
set -euo pipefail

DESK="/mnt/d/Game/Pokemon Z/V2.18"
RUNA="/mnt/d/Game/Pokemon Z/V2.18 루나판"
MOD="/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 통합 (루나)"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

[ -d "$RUNA" ] || { echo "루나판이 없다: $RUNA"; exit 1; }
pgrep -f "Game.exe" >/dev/null 2>&1 && echo "⚠ 게임이 실행 중이면 폰트 파일이 잠긴다 — 끄고 다시 돌려라"

echo "① 커스텀 셋 되돌리기 (dat · 폰트 16벌 · mkxp.json)"
for f in "$MOD"/Fonts/pkmn*.ttf "$MOD"/Fonts/kr-*.ttf; do
  [ -e "$f" ] || continue
  rm -f "$RUNA/Fonts/$(basename "$f")"
  cp -p "$f" "$RUNA/Fonts/"
done
cp -p "$MOD/mkxp.json" "$RUNA/mkxp.json"
cp --remove-destination "$MOD/Data/korean.dat" "$RUNA/Data/korean.dat"
echo "   폰트 $(ls "$MOD"/Fonts/pkmn*.ttf "$MOD"/Fonts/kr-*.ttf 2>/dev/null | wc -l)벌 · mkxp.json · korean.dat"

if [ "${1:-}" = "--full" ]; then
  echo "② 자산·층 보관본을 데스크톱 판으로 맞추기"
  python3 - "$DESK" "$RUNA" <<'PY'
import hashlib, os, shutil, sys
desk, runa = sys.argv[1], sys.argv[2]
skip = {"korean.dat", "mkxp.json", "LastSave.dat", "modkit-log.jsonl", "configuration.json"}
def h(p):
    m = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""): m.update(c)
    return m.hexdigest()
n = 0
for root, _, files in os.walk(desk):
    if os.path.basename(root) == "Fonts": continue
    for name in files:
        a = os.path.join(root, name); b = runa + a[len(desk):]
        if name in skip: continue
        if not os.path.exists(b) or (os.path.getsize(a) != os.path.getsize(b) and h(a) != h(b)):
            os.makedirs(os.path.dirname(b), exist_ok=True)
            if os.path.exists(b): os.remove(b)     # 하드링크를 만들지 않는다
            shutil.copy2(a, b); n += 1
print(f"   {n}개 맞춤")
PY
  echo "③ 주입 모드 다시 세우기"
  (cd "$REPO" && uv run inject.py "UI Text KR" "Battle Speed" "Better Movements" \
      "Controller UX" "Pixel Shadow" --game "$RUNA" | tail -2)
fi

echo "확인:"
python3 - "$RUNA" <<'PY'
import sys, pathlib, re, json
runa = pathlib.Path(sys.argv[1])
d = (runa / "Data/korean.dat").read_bytes()
t = re.sub(r"^\s*//.*$", "", (runa / "mkxp.json").read_text(encoding="utf-8"), flags=re.M)
cfg = json.loads(re.sub(r",(\s*[}\]])", r"\1", t))
fonts = len(list((runa / "Fonts").glob("pkmn*.ttf"))) + len(list((runa / "Fonts").glob("kr-*.ttf")))
print(f"   dat 인코딩 딱지 {d.count(b'I\"'):,}개 · 폰트 {fonts}벌 · fontSub 없음 {'fontSub' not in cfg}"
      f" · solidFonts {cfg.get('solidFonts')}")
PY
