#!/usr/bin/env bash
# Builds dist/throwindice/ : everything the site needs, nothing else, ready to drop on your own site as a sub-page.
#   SITE_URL=https://example.com/throwindice/ scripts/package.sh [outdir]
# All paths in the page are relative, so the folder works at any URL depth. SITE_URL only rewrites the share-card
# metadata (og:url, og:image) that must be absolute. Without it the GitHub Pages address stays.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="${1:-dist/throwindice}"
rm -rf "$OUT" && mkdir -p "$OUT"
cp -r index.html manifest.webmanifest assets data "$OUT"/
rm -f "$OUT"/data/run-report.json
rm -rf "$OUT"/data/cache
if [ -n "${SITE_URL:-}" ]; then
  U="${SITE_URL%/}/"
  sed -i "s#https://gharbete-max.github.io/throwindice/#${U}#g" "$OUT/index.html"
fi
echo "Packaged $(du -sh "$OUT" | cut -f1) -> $OUT"
