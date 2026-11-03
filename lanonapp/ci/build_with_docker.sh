#!/usr/bin/env bash
# Local build without installing Android SDK on the host; Docker and internet required.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -v "$ROOT:/work" -w /work \
  ghcr.io/cirruslabs/android-sdk:35 bash ci/build_android_debug.sh
