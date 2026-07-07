# VIDZDOWNLOAD

VIDZDOWNLOAD is a small local video ingest machine.

It downloads videos from URLs, detects the source automatically, retrieves metadata and thumbnails, and writes everything into a local `VIDZ IMPORTS` folder.

## Features

- Paste one URL or many URLs at once
- Automatic source detection: YouTube, Instagram, Vimeo, generic web
- Batch downloads with progress LEDs
- Instagram carousel expansion: a post with several videos is queued item by item
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
.venv/bin/python VIDZDOWNLOAD.py
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
VIDZDOWNLOAD.app
```

## Instagram

Individual reel URLs usually work better than profile pages.
Instagram carousel/post URLs are expanded when `yt-dlp` exposes multiple entries, so all available videos in the carousel are downloaded instead of only the first one.

For private, logged-in, or restricted Instagram content, export cookies manually as:

```text
VIDZ_COOKIES.txt
```

Place that file next to `VIDZDOWNLOAD.py`.

## Notes

VIDZDOWNLOAD uses `yt-dlp` for downloads. Respect platform terms, copyright rules, and local law.
