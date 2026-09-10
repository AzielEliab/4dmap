#!/usr/bin/env bash
# Pack the counted Softwares download tarball from repo sources.
# Hosts workers/download-tracker/public/4dmap-<version>.tar.gz (DEFAULT_ASSET).
# Nested public/*.tar.gz are omitted so ASSETS stays one generation deep.
# Author: Aziel Eliab only. Mesh remain-OFF. Dual-surface Worker unchanged.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VERSION="$(python3 -c 'import pathlib,re; t=pathlib.Path("fourdmap/scope.py").read_text(); print(re.search(r"__version__ = \"([^\"]+)\"", t).group(1))')"
NAME="4dmap-${VERSION}"
OUT="${ROOT}/workers/download-tracker/public/${NAME}.tar.gz"

entries=()
for p in * .gitignore; do
  [ -e "$p" ] || continue
  case "$p" in
    .git|.venv|.cursor) continue ;;
  esac
  entries+=("$p")
done

tar \
  --exclude='node_modules' \
  --exclude='.wrangler' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='*.pyc' \
  --exclude='*.egg-info' \
  --exclude='dist' \
  --exclude='workers/download-tracker/public/*.tar.gz' \
  --transform="s,^,${NAME}/," \
  -czf "$OUT" \
  "${entries[@]}"

BYTES="$(wc -c < "$OUT" | tr -d ' ')"
echo "Wrote ${OUT} (${BYTES} bytes) prefix=${NAME}/"
