#!/usr/bin/env bash
# webapp/ 정적 파일을 공개 repo로 배포 — 번역표·게임 데이터는 절대 포함하지 않는다
set -euo pipefail
cd "$(dirname "$0")"
REPO=${1:-$(gh api user -q .login)/z-kr-studio}
OWNER=${REPO%%/*}
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
gh repo view "$REPO" >/dev/null 2>&1 || gh repo create "$REPO" --public
git clone "https://github.com/$REPO" "$TMP" 2>/dev/null
rsync -a --delete \
  --exclude .git --exclude tests --exclude publish.sh \
  --exclude vendor/rubymarshal/tests --exclude __pycache__ \
  --exclude .pytest_cache \
  ./ "$TMP/"
cd "$TMP"
git add -A
git diff --cached --quiet || { git commit -m "deploy $(date +%F)"; git push origin HEAD; }
gh api "repos/$REPO/pages" -X POST -f 'source[branch]=main' -f 'source[path]=/' 2>/dev/null || true
echo "https://$OWNER.github.io/${REPO#*/}/"
