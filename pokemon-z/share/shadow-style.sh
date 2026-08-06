#!/usr/bin/env bash
# 글자 그림자 두께를 바꾸고 루나판에 다시 넣는다.
#   bash share/shadow-style.sh thin|soft|step|thick [바깥겹_알파] [한글_굵게_알파(0~255)]
set -euo pipefail
S="${1:-}"
case "$S" in thin|soft|step|thick) ;; *) echo "쓰기: $0 thin|soft|step|thick"; exit 1;; esac
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNA="/mnt/d/Game/Pokemon Z/V2.18 루나판"
sed -i "s/^PIXEL_SHADOW_STYLE = :.*/PIXEL_SHADOW_STYLE = :$S/" "$REPO/mods/Pixel Shadow/001_Shadow.rb"
if [ -n "${3:-}" ]; then
  sed -i "s/^PIXEL_BOLD_ALPHA = [0-9]*/PIXEL_BOLD_ALPHA = $3/" "$REPO/mods/Pixel Shadow/003_BoldHangul.rb"
fi
if [ -n "${2:-}" ]; then
  sed -i "s/^PIXEL_SHADOW_FAINT = [0-9]*/PIXEL_SHADOW_FAINT = $2/" "$REPO/mods/Pixel Shadow/001_Shadow.rb"
fi
(cd "$REPO" && uv run inject.py "UI Text KR" "Battle Speed" "Better Movements" \
    "Controller UX" "Pixel Shadow" --game "$RUNA" >/dev/null)
cp "$RUNA/Data/Scripts.rxdata" "/mnt/d/GameVault/mods/Pokemon Z Fangame/한글패치 통합 (루나)/Data/Scripts.rxdata"
A=$(grep -o "^PIXEL_SHADOW_FAINT = [0-9]*" "$REPO/mods/Pixel Shadow/001_Shadow.rb" | grep -o "[0-9]*$")
W=$(grep -o "^PIXEL_BOLD_ALPHA = [0-9]*" "$REPO/mods/Pixel Shadow/003_BoldHangul.rb" | grep -o "[0-9]*$")
echo "그림자 = :$S (바깥 겹 알파 $A · 한글 굵게 알파 $W) · 게임과 모드 보관본에 반영 (게임을 다시 켜면 보인다)"
