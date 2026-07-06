# VIDZDOWNATOR

VIDZDOWNATOR is a small local video ingest machine.

It downloads videos from URLs, detects the source automatically, retrieves metadata and thumbnails, and writes everything into a local `VIDZ IMPORTS` folder.

## Features

- Paste one URL or many URLs at once
- Automatic source detection: YouTube, Instagram, Vimeo, generic web
- Batch downloads with progress LEDs
- Metadata JSON next to each video
- Thumbnail download when available
- Filename format with artist, collection, keywords and title
- Local browser interface
- No cloud backend

## Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Run

```bash
.venv/bin/python VIDZDOWNATOR.py
```

The app opens in your browser.

Downloaded videos are saved in:

```text
VIDZ IMPORTS/
```

## macOS App

To build a double-clickable macOS app:

```bash
./build_macos_app.command
```

It creates:

```text
VIDZDOWNATOR.app
```

## Instagram

Individual reel URLs usually work better than profile pages.

For private, logged-in, or restricted Instagram content, export cookies manually as:

```text
VIDZ_COOKIES.txt
```

Place that file next to `VIDZDOWNATOR.py`.

## Notes

VIDZDOWNATOR uses `yt-dlp` for downloads. Respect platform terms, copyright rules, and local law.
