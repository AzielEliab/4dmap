#!/usr/bin/env bash
# 4DMap one-click install. Counted download via this project's Worker.
# Usage: curl -fsSL https://4dmap-download-tracker.vibelock.workers.dev/install.sh | bash
set -euo pipefail

HOST="${FOURDMAP_HOST:-https://4dmap-download-tracker.vibelock.workers.dev}"
ASSET="${FOURDMAP_ASSET:-4dmap-0.2.0.tar.gz}"
WORKDIR="${FOURDMAP_HOME:-$HOME/4dmap}"

mkdir -p "$WORKDIR"
cd "$WORKDIR"

echo "Downloading counted tarball from ${HOST}/download (User-Agent Mozilla/5.0)…"
curl -fsSL -A 'Mozilla/5.0' "${HOST}/download?asset=${ASSET}" -o "${ASSET}"

tar -xzf "${ASSET}"
DIR="$(find . -maxdepth 1 -type d -name '4dmap-*' | head -n 1)"
if [ -n "${DIR}" ]; then
  cd "${DIR}"
fi

python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .

echo
echo "Installed 4DMap."
echo "Run: 4dmap ui"
echo "Then open http://127.0.0.1:8844 (loopback only)"
echo "Inspection frame. Not a truth engine. Author: Aziel Eliab."
