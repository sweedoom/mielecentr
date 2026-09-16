#!/usr/bin/env bash
# Сборка + коммит + пуш на GitHub Pages.
# Использует git credential helper (gh auth) — НЕ требует активного `gh auth login`.
set -e

cd "$(dirname "$0")"

REPO=${REPO:-sweedoom/mielecentr}     # github.com/USER/REPO
HOST=${HOST:-https://github.com}
COMMIT="site update $(date +%Y-%m-%d-%H%M)"

python build.py

if [ ! -d .git ]; then
  git init -q -b main
fi
git config user.name  "Мамченко Линар Сергеевич"
git config user.email "esquirecypherx@mail.ru"
git add -A
if git diff --cached --quiet; then
  echo "нечего коммитить — всё уже на месте"
  exit 0
fi
git commit -q -m "$COMMIT"

if ! git remote get-url origin >/dev/null 2>&1; then
  git remote add origin "$HOST/$REPO.git"
fi

# пуш через credential helper (gh auth git-credential)
git push -u origin main

# включить Pages на /docs (если ещё не включено)
TOKEN=$(echo "protocol=https
host=github.com" | git credential fill | awk -F= '/^password=/{print $2}')
if [ -n "$TOKEN" ]; then
  curl -s -X POST "https://api.github.com/repos/${REPO%/*}/${REPO##*/}/pages" \
       -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github+json" \
       -f "source[branch]=main" -f "source[path]=/docs" >/dev/null || true
  echo "✓ Pages включён"
fi

USER_LOGIN="${REPO%/*}"
NAME="${REPO##*/}"
echo
echo "✓ запушено. Сайт появится через 1-2 минуты на:"
echo "  https://${USER_LOGIN}.github.io/${NAME}/"