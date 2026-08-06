#!/usr/bin/env bash
# 글자 그림자·굵게 값을 바꾸고 게임에 다시 얹는다.
#   bash share/shadow-style.sh thin|soft|step|thick [바깥겹_알파] [한글_굵게_알파(0~255)]
#
# 정본은 repo의 mods/DPPT Font 다. 보관소 사본은 여기서 새로 뜨고, 게임에는 modkit이 얹는다.
set -euo pipefail
S="${1:-}"
case "$S" in thin|soft|step|thick) ;; *) echo "쓰기: $0 thin|soft|step|thick"; exit 1;; esac

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MOD="$REPO/mods/DPPT Font"
STORE="/mnt/d/GameVault/mods"
GAME="${Z_GAME:-/mnt/d/Game/Pokemon Z/V2.18}"
MODKIT="${MODKIT_HOME:-$REPO/../../sketches/essentials-modkit}"

sed -i "s/^PIXEL_SHADOW_STYLE = :.*/PIXEL_SHADOW_STYLE = :$S/" "$MOD/001_Shadow.rb"
[ -n "${2:-}" ] && sed -i "s/^PIXEL_SHADOW_FAINT = [0-9]*/PIXEL_SHADOW_FAINT = $2/" "$MOD/001_Shadow.rb"
[ -n "${3:-}" ] && sed -i "s/^PIXEL_BOLD_ALPHA = [0-9]*/PIXEL_BOLD_ALPHA = $3/" "$MOD/003_BoldHangul.rb"

cp "$MOD"/*.rb "$MOD/mod.json" "$STORE/Pokemon Z Fangame/DPPT Font/"
(cd "$MODKIT" && uv run python -m modkit.cli apply "DPPT Font" "$GAME" --store "$STORE" >/dev/null)

A=$(grep -o "^PIXEL_SHADOW_FAINT = [0-9]*" "$MOD/001_Shadow.rb" | grep -o "[0-9]*$")
W=$(grep -o "^PIXEL_BOLD_ALPHA = [0-9]*" "$MOD/003_BoldHangul.rb" | grep -o "[0-9]*$")
echo "그림자 = :$S (바깥 겹 알파 $A · 한글 굵게 알파 $W) · 게임에 반영 (게임을 다시 켜면 보인다)"
