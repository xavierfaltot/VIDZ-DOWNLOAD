#!/bin/bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
APP="$DIR/VIDZDOWNLOAD.app"

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"

cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key>
  <string>VIDZDOWNLOAD</string>
  <key>CFBundleDisplayName</key>
  <string>VIDZDOWNLOAD</string>
  <key>CFBundleIdentifier</key>
  <string>operator.gost.vidzdownload</string>
  <key>CFBundleVersion</key>
  <string>1.0</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleExecutable</key>
  <string>VIDZDOWNLOAD</string>
  <key>LSMinimumSystemVersion</key>
  <string>10.13</string>
</dict>
</plist>
PLIST

cat > "$APP/Contents/MacOS/VIDZDOWNLOAD" <<'RUNNER'
#!/bin/bash
APP_EXE_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$APP_EXE_DIR/../../.." && pwd)"

osascript <<APPLESCRIPT
tell application "Terminal"
  activate
  do script quoted form of "$PROJECT_DIR/VIDZDOWNLOAD.command"
end tell
APPLESCRIPT
RUNNER

chmod +x "$APP/Contents/MacOS/VIDZDOWNLOAD"

cp "$DIR/VIDZDOWNLOAD_LOGO.png" "$APP/Contents/Resources/VIDZDOWNLOAD_LOGO.png"

if command -v SetFile >/dev/null 2>&1 && command -v sips >/dev/null 2>&1; then
  cp "$DIR/VIDZDOWNLOAD_LOGO.png" "$APP/Icon"$'\r'
  sips -i "$APP/Icon"$'\r' >/dev/null
  SetFile -a V "$APP/Icon"$'\r' || true
  SetFile -a C "$APP" || true
fi

echo "Built: $APP"
