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
  --exclude .git --exclude tests --exclude AGENTS.md --exclude publish.sh \
  --exclude vendor/rubymarshal/tests --exclude __pycache__ \
  --exclude .pytest_cache \
  ./ "$TMP/"
cd "$TMP"
# Jekyll이 밑줄 파일(__init__.py)을 빼먹지 않게 비활성화
touch .nojekyll
git add -A
git diff --cached --quiet || { git commit -m "deploy $(date +%F)"; git push origin HEAD; }
# Pages 켜기가 먼저다 — 꺼져 있을 때 빌드 발주부터 하면 404로 튕기고 그 판은 그냥 지나간다
# (2026-08-05 실측: 사이트가 통째로 404였고 pages API도 Not Found였다 — 이 순서로 되살아났다)
gh api "repos/$REPO/pages" -X POST -f 'source[branch]=main' -f 'source[path]=/' >/dev/null 2>&1 || true
gh api -X POST "repos/$REPO/pages/builds" >/dev/null 2>&1 || true
echo "https://$OWNER.github.io/${REPO#*/}/"
