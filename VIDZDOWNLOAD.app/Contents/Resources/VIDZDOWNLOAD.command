#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR" || exit 1

SYSTEM_PYTHON="$(command -v python3 || command -v python || true)"

if [ -z "${SYSTEM_PYTHON:-}" ]; then
  echo "Python is not installed."
  echo "Install Python 3, then launch this file again."
  read -r -p "Press Enter to close..."
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Preparing VIDZDOWNLOAD environment..."
  if ! "$SYSTEM_PYTHON" -m venv .venv; then
    echo
    echo "Could not create the local Python environment."
    echo "Install Python 3 from python.org, then launch VIDZDOWNLOAD again."
    read -r -p "Press Enter to close..."
    exit 1
  fi
fi

PYTHON=".venv/bin/python"

if [ -f "requirements.txt" ]; then
  "$PYTHON" - <<'PY' >/dev/null 2>&1
import cv2
import imageio_ffmpeg
import yt_dlp
PY
  if [ $? -ne 0 ]; then
    echo "Installing VIDZDOWNLOAD components..."
    echo "This can take a few minutes on first launch."
    "$PYTHON" -m ensurepip --upgrade >/dev/null 2>&1 || true
    "$PYTHON" -m pip install --upgrade pip
    "$PYTHON" -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
      echo
      echo "Dependency install failed."
      echo "Check your internet connection, then launch VIDZDOWNLOAD again."
      read -r -p "Press Enter to close..."
      exit 1
    fi
  fi
fi

echo "Starting VIDZDOWNLOAD..."
echo "Folder: $DIR"
echo
"$PYTHON" "$DIR/VIDZDOWNLOAD.py"

echo
echo "VIDZDOWNLOAD stopped."
read -r -p "Press Enter to close..."
