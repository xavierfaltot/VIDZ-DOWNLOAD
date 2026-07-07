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
  <key>CFBundleIconFile</key>
  <string>VIDZDOWNLOAD</string>
  <key>LSMinimumSystemVersion</key>
  <string>10.13</string>
</dict>
</plist>
PLIST

cat > "$APP/Contents/MacOS/VIDZDOWNLOAD" <<'RUNNER'
#!/bin/bash
APP_EXE_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$APP_EXE_DIR/../Resources" && pwd)"

osascript <<APPLESCRIPT
tell application "Terminal"
  activate
  do script quoted form of "$PROJECT_DIR/VIDZDOWNLOAD.command"
end tell
APPLESCRIPT
RUNNER

chmod +x "$APP/Contents/MacOS/VIDZDOWNLOAD"

cp "$DIR/VIDZDOWNLOAD_LOGO.png" "$APP/Contents/Resources/VIDZDOWNLOAD_LOGO.png"
cp "$DIR/VIDZDOWNLOAD.py" "$APP/Contents/Resources/VIDZDOWNLOAD.py"
cp "$DIR/VIDZDOWNLOAD.command" "$APP/Contents/Resources/VIDZDOWNLOAD.command"
cp "$DIR/requirements.txt" "$APP/Contents/Resources/requirements.txt"
chmod +x "$APP/Contents/Resources/VIDZDOWNLOAD.command"

if command -v sips >/dev/null 2>&1 && command -v iconutil >/dev/null 2>&1; then
  ICONSET="$APP/Contents/Resources/VIDZDOWNLOAD.iconset"
  mkdir -p "$ICONSET"
  sips -z 16 16 "$DIR/VIDZDOWNLOAD_LOGO.png" --out "$ICONSET/icon_16x16.png" >/dev/null
  sips -z 32 32 "$DIR/VIDZDOWNLOAD_LOGO.png" --out "$ICONSET/icon_16x16@2x.png" >/dev/null
  sips -z 32 32 "$DIR/VIDZDOWNLOAD_LOGO.png" --out "$ICONSET/icon_32x32.png" >/dev/null
  sips -z 64 64 "$DIR/VIDZDOWNLOAD_LOGO.png" --out "$ICONSET/icon_32x32@2x.png" >/dev/null
  sips -z 128 128 "$DIR/VIDZDOWNLOAD_LOGO.png" --out "$ICONSET/icon_128x128.png" >/dev/null
  sips -z 256 256 "$DIR/VIDZDOWNLOAD_LOGO.png" --out "$ICONSET/icon_128x128@2x.png" >/dev/null
  sips -z 256 256 "$DIR/VIDZDOWNLOAD_LOGO.png" --out "$ICONSET/icon_256x256.png" >/dev/null
  sips -z 512 512 "$DIR/VIDZDOWNLOAD_LOGO.png" --out "$ICONSET/icon_256x256@2x.png" >/dev/null
  sips -z 512 512 "$DIR/VIDZDOWNLOAD_LOGO.png" --out "$ICONSET/icon_512x512.png" >/dev/null
  sips -z 1024 1024 "$DIR/VIDZDOWNLOAD_LOGO.png" --out "$ICONSET/icon_512x512@2x.png" >/dev/null
  if ! iconutil -c icns "$ICONSET" -o "$APP/Contents/Resources/VIDZDOWNLOAD.icns"; then
    python3 - "$ICONSET" "$APP/Contents/Resources/VIDZDOWNLOAD.icns" <<'PY'
import struct
import sys
from pathlib import Path

iconset = Path(sys.argv[1])
output = Path(sys.argv[2])
mapping = [
    ("icp4", "icon_16x16.png"),
    ("icp5", "icon_32x32.png"),
    ("icp6", "icon_32x32@2x.png"),
    ("ic07", "icon_128x128.png"),
    ("ic08", "icon_256x256.png"),
    ("ic09", "icon_512x512.png"),
    ("ic10", "icon_512x512@2x.png"),
]
chunks = []
for kind, name in mapping:
    data = (iconset / name).read_bytes()
    chunks.append(kind.encode("ascii") + struct.pack(">I", len(data) + 8) + data)
payload = b"".join(chunks)
output.write_bytes(b"icns" + struct.pack(">I", len(payload) + 8) + payload)
PY
  fi
  rm -rf "$ICONSET"
fi

if command -v SetFile >/dev/null 2>&1 && command -v sips >/dev/null 2>&1; then
  cp "$DIR/VIDZDOWNLOAD_LOGO.png" "$APP/Icon"$'\r'
  sips -i "$APP/Icon"$'\r' >/dev/null
  SetFile -a V "$APP/Icon"$'\r' || true
  SetFile -a C "$APP" || true
fi

echo "Built: $APP"
