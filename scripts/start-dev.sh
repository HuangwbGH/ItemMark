#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

screen -S itemmark-dev -X quit >/dev/null 2>&1 || true
if command -v lsof >/dev/null 2>&1; then
  for pid in $(lsof -tiTCP:18089 -sTCP:LISTEN 2>/dev/null || true); do
    kill "$pid" >/dev/null 2>&1 || true
  done
fi
screen -dmS itemmark-dev bash -lc 'python3 -m uvicorn web.main:app --host 0.0.0.0 --port 18089 > logs/dev-server.log 2>&1'

echo "ItemMark dev server started: http://127.0.0.1:18089/"
echo "Logs: logs/dev-server.log"
