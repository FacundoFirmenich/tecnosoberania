#!/usr/bin/env bash
# Builds native launchers with Go >=1.23. No downloaded dependency or SaaS required.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
GODIR="$ROOT/desktop/native"
mkdir -p "$GODIR/assets"
rm -rf "$GODIR/assets/app" "$GODIR/assets/site"
cp -a "$ROOT/app" "$GODIR/assets/app"
cp -a "$ROOT/site" "$GODIR/assets/site"
mkdir -p "$ROOT/dist/native"
cd "$GODIR"
for target in windows/amd64 linux/amd64 linux/arm64 darwin/arm64 darwin/amd64; do
  os="${target%/*}"; arch="${target#*/}"; ext=""
  [ "$os" != windows ] || ext=".exe"
  echo "Building $target"
  CGO_ENABLED=0 GOOS="$os" GOARCH="$arch" go build -trimpath -ldflags='-s -w' -o "$ROOT/dist/native/LaNonApp_${os}_${arch}${ext}" .
done
sha256sum "$ROOT"/dist/native/* > "$ROOT/dist/native/SHA256SUMS.txt"
