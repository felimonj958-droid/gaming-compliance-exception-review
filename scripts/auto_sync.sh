#!/bin/zsh
set -e

mkdir -p .cache
REQ_FILE="requirements.txt"
STAMP_FILE=".cache/requirements.sha"

[[ -f "$REQ_FILE" ]] || exit 0
[[ -d ".venv" ]] || exit 0

CURRENT_HASH=$(shasum "$REQ_FILE" | awk '{print $1}')
SAVED_HASH=""

if [[ -f "$STAMP_FILE" ]]; then
  SAVED_HASH=$(cat "$STAMP_FILE")
fi

if [[ "$CURRENT_HASH" != "$SAVED_HASH" ]]; then
  echo "requirements.txt changed — syncing packages..."
  python -m pip install --upgrade pip
  python -m pip install -r "$REQ_FILE"
  echo "$CURRENT_HASH" > "$STAMP_FILE"
fi
