#!/usr/bin/env bash
# Reproducible Android debug APK builder for local SDK, Docker, GitLab or Codemagic.
# Requires JDK17+, Android SDK 35, and network access for Gradle/AGP dependencies.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GRADLE_VERSION=8.12
GRADLE_SHA256=7a00d51fb93147819aab76024feece20b6b84e420694101f276be952e08bef03
mkdir -p "$ROOT/android/app/src/main/assets/web"
cp -a "$ROOT/app/." "$ROOT/android/app/src/main/assets/web/"
if [[ -z "${ANDROID_SDK_ROOT:-}" && -z "${ANDROID_HOME:-}" ]]; then
  echo 'ERROR: Android SDK not found. Set ANDROID_SDK_ROOT or ANDROID_HOME.' >&2; exit 2
fi
SDK="${ANDROID_SDK_ROOT:-$ANDROID_HOME}"
if [[ ! -f "$SDK/platforms/android-35/android.jar" ]]; then
  echo 'Android SDK platform 35 absent; installing with sdkmanager (requires accepted SDK license).' >&2
  sdkmanager --sdk_root="$SDK" 'platforms;android-35' 'build-tools;35.0.0'
fi
printf 'sdk.dir=%s\n' "$SDK" > "$ROOT/android/local.properties"
if command -v gradle >/dev/null 2>&1 && gradle --version 2>/dev/null | grep -q "Gradle $GRADLE_VERSION"; then
  G=(gradle)
else
  if ! command -v curl >/dev/null || ! command -v unzip >/dev/null; then
    echo 'ERROR: curl/unzip required to bootstrap verified Gradle.' >&2; exit 2
  fi
  cache="${GRADLE_DISTRIBUTIONS:-$HOME/.cache/lanonapp-gradle}"
  mkdir -p "$cache"
  zip="$cache/gradle-$GRADLE_VERSION-bin.zip"
  if [[ ! -f "$zip" ]]; then
    curl -fL --retry 3 --connect-timeout 20 -o "$zip.part" "https://services.gradle.org/distributions/gradle-$GRADLE_VERSION-bin.zip"
    mv "$zip.part" "$zip"
  fi
  echo "$GRADLE_SHA256  $zip" | sha256sum -c -
  if [[ ! -x "$cache/gradle-$GRADLE_VERSION/bin/gradle" ]]; then
    unzip -q -o "$zip" -d "$cache"
  fi
  G=("$cache/gradle-$GRADLE_VERSION/bin/gradle")
fi
cd "$ROOT/android"
"${G[@]}" --no-daemon --stacktrace :app:assembleDebug
apk="$ROOT/android/app/build/outputs/apk/debug/app-debug.apk"
test -s "$apk"
sha256sum "$apk"
printf 'APK compilada: %s\n' "$apk"
