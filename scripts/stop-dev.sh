#!/usr/bin/env bash
set -euo pipefail

screen -S itemmark-dev -X quit >/dev/null 2>&1 || true
if command -v lsof >/dev/null 2>&1; then
  for pid in $(lsof -tiTCP:18089 -sTCP:LISTEN 2>/dev/null || true); do
    kill "$pid" >/dev/null 2>&1 || true
  done
fi
echo "ItemMark dev server stopped."
