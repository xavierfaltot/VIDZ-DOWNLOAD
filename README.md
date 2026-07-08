# VIDZDOWNLOAD

VIDZDOWNLOAD is a local video ingest tool built for creators, editors, and visual researchers.

It downloads videos from online links, detects the source automatically, retrieves metadata and thumbnails, and stores everything in a clean local structure. Videos are saved in a `VIDEOS` folder, while JSON metadata, thumbnails, and image assets are stored separately in `ASSETS`.

The app supports single URLs, batches of URLs, bookmark exports, playlists, Instagram reels, and carousel posts when available through the downloader. It includes an `AUTO ANALYZE` mode that can analyze each downloaded video locally and append visual tags to the filename, such as dominant color, brightness, motion, format, duration, and face detection when available.

VIDZDOWNLOAD is designed like a dedicated machine: one purpose, minimal interface, no complex menus. Paste links, choose an output folder, press `START`, and let the system prepare the files for editing or archival workflows.

## Features

- Paste one URL or many URLs at once
- Load URLs from a bookmark export file or a folder of bookmark files
- Automatic source detection: YouTube, Instagram, Vimeo, generic web
- Batch downloads with progress LEDs
- Configurable output folder with `VIDEOS/` and `ASSETS/` subfolders
- Instagram carousel expansion: a post with several videos is queued item by item
- `AUTO ANALYZE` toggle that adds visual tags after every download
- Metadata JSON next to each video
- Thumbnail download when available
- Filename format with artist, collection, your keywords, title, and optional analysis tags
- Local browser interface
- No cloud backend

## Install

On macOS, double-click:

```text
VIDZDOWNLOAD.command
```

On first launch, VIDZDOWNLOAD creates a local `.venv` folder and downloads the required components automatically:

- `yt-dlp` for downloads
- `imageio-ffmpeg` / ffmpeg for video processing
- `opencv-python-headless` for face detection during analysis

You only need Python 3 and an internet connection for the first launch.

Manual install:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Run

```bash
.venv/bin/python VIDZDOWNLOAD.py
```

The app opens in your browser.

Downloaded videos are saved by default in:

```text
VIDZ IMPORTS/
```

You can change the final output folder directly in the app with the `OUTPUT FOLDER` field.
Use `SET` to save the typed path, or `PICK` on macOS to choose a folder.

VIDZDOWNLOAD now keeps the output folder clean:

```text
Your output folder/
  VIDEOS/   video files
  ASSETS/   metadata JSON files, thumbnails, images
```

## Bookmarks

VIDZDOWNLOAD can also read URLs from a bookmarks source.

Paste a path into `BOOKMARKS PATH`, for example:

```text
/Users/you/Desktop/bookmarks.html
/Users/you/Desktop/VIDEO_BOOKMARKS/
```

Supported bookmark sources include `.html`, `.htm`, `.json`, `.txt`, `.url`, and `.webloc` files. If you give a folder, VIDZDOWNLOAD scans supported files inside it and extracts every URL it finds.

## Local Analysis Tags

Turn on `AUTO ANALYZE` at the top of the machine.

After each download, VIDZDOWNLOAD samples the video locally with ffmpeg and appends tags to the filename, for example:

```text
APHEX_TWIN__WARP__YOUR_TAGS__WINDOWLICKER__COLOR_ORANGE__FACE__FAST_MOTION__WIDE.mp4
```

The analysis can add tags for dominant color, brightness, motion speed, format, duration, high FPS, and face detection when OpenCV is available. It also updates the `.json` metadata next to the video.

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
