#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR" || exit 1

if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
else
  PYTHON="$(command -v python3 || command -v python || true)"
fi

if [ -z "${PYTHON:-}" ]; then
  echo "Python is not installed."
  echo "Install Python 3, then launch this file again."
  read -r -p "Press Enter to close..."
  exit 1
fi

echo "Starting VIDZDOWNLOAD..."
echo "Folder: $DIR"
echo
"$PYTHON" "$DIR/VIDZDOWNLOAD.py"

echo
echo "VIDZDOWNLOAD stopped."
read -r -p "Press Enter to close..."
