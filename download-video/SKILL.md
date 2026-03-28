---
name: download-video
description: |
  Downloads embedded videos from web pages. Fetches the page, identifies the video hosting service (Vimeo, YouTube, etc.), resolves the correct embed/player URL, and downloads using yt-dlp. Handles private/unlisted videos that require referer headers or embed URLs. Use this skill when someone says "download this video", "save this video", "grab the video from this page", "rip this video", or provides a URL and asks to download media from it. Also trigger when someone pastes a URL to a page with an embedded video and wants the video file locally.
license: MIT
compatibility: |
  Requires macOS or Linux with yt-dlp installed (brew install yt-dlp). curl_cffi Python package recommended for impersonation support (pip3 install curl_cffi). Internet connection required.
metadata:
  author: swyxio
  version: "1.0"
  last-updated: "2026-03-28"
  primary-tools: yt-dlp, WebFetch
---

# Download Video

This skill downloads embedded videos from web pages by inspecting the page source, identifying the video hosting service and embed URL, then using yt-dlp to download the video file.

## Why This Skill Exists

Many event replays, webinars, and talks are embedded on pages using private/unlisted video hosting (especially Vimeo). The direct video URL often returns 404 because the video is only accessible through the embed player with the correct referer. This skill handles that automatically.

## Prerequisites

Ensure yt-dlp is installed:

```bash
which yt-dlp || brew install yt-dlp
```

For best results, install the impersonation library (avoids OAuth token errors):

```bash
pip3 install curl_cffi
```

## How to Use This Skill

### Step 1: Fetch the Page and Identify the Video

Use WebFetch to inspect the target URL. Look for:

1. **iframe src** attributes pointing to video players
2. **video/source tags** with direct media URLs
3. **Schema.org VideoObject** metadata (`contentUrl`, `embedUrl`)
4. **JavaScript variables** containing video URLs or config objects
5. **Data attributes** on player container elements

Extract the video hosting service and any identifying info:

| Host | URL Pattern | Embed Pattern |
|---|---|---|
| Vimeo | `vimeo.com/{id}` | `player.vimeo.com/video/{id}` |
| YouTube | `youtube.com/watch?v={id}` | `youtube.com/embed/{id}` |
| Wistia | `fast.wistia.com/medias/{id}` | `fast.wistia.com/embed/medias/{id}` |
| Brightcove | varies | `players.brightcove.net/{account}/{player}/index.html?videoId={id}` |
| Loom | `loom.com/share/{id}` | `loom.com/embed/{id}` |

### Step 2: Resolve the Download URL

The direct URL (e.g., `vimeo.com/123456`) often fails for private/unlisted videos. Use the **embed/player URL** instead:

- **Vimeo**: Use `https://player.vimeo.com/video/{id}` instead of `https://vimeo.com/{id}`
- **YouTube**: The direct URL usually works, but embed URL works too
- **Wistia**: Use the embed URL with the media hash

If the video has a privacy hash (Vimeo `h=` parameter), include it:
```
https://player.vimeo.com/video/{id}?h={hash}
```

### Step 3: Download with yt-dlp

Try these approaches in order. Stop at the first one that works.

**Attempt 1 — Direct URL:**
```bash
yt-dlp "{video_url}"
```

**Attempt 2 — Embed/player URL:**
```bash
yt-dlp "https://player.vimeo.com/video/{id}"
```

**Attempt 3 — With referer header** (for private embeds):
```bash
yt-dlp --referer "{source_page_url}" "https://player.vimeo.com/video/{id}"
```

**Attempt 4 — With referer + origin headers:**
```bash
yt-dlp --referer "{source_page_url}" --add-header "Origin: {source_origin}" "https://player.vimeo.com/video/{id}"
```

### Step 4: Quality Selection (Optional)

If the user wants a specific quality:

```bash
# List available formats
yt-dlp -F "{url}"

# Download best quality (default)
yt-dlp -f "bestvideo+bestaudio" "{url}"

# Download specific resolution
yt-dlp -f "bestvideo[height<=1080]+bestaudio" "{url}"

# Download audio only
yt-dlp -f "bestaudio" -x --audio-format mp3 "{url}"
```

### Step 5: Output Location

By default yt-dlp saves to the current directory. To specify an output path:

```bash
yt-dlp -o "~/Downloads/%(title)s.%(ext)s" "{url}"
```

## Troubleshooting

### OAuth Token Error
```
ERROR: Failed to fetch OAuth token: HTTP Error 400
```
**Fix**: Install `curl_cffi` for impersonation support:
```bash
pip3 install curl_cffi
```
If that doesn't help, use the embed/player URL instead of the direct URL.

### 404 Not Found
```
ERROR: Unable to download API JSON: HTTP Error 404
```
**Fix**: The video is private/unlisted. Switch to the embed URL:
- `vimeo.com/{id}` -> `player.vimeo.com/video/{id}`

### 403 Forbidden
```
ERROR: HTTP Error 403: Forbidden
```
**Fix**: Add the referer header from the source page:
```bash
yt-dlp --referer "{source_page_url}" "{embed_url}"
```

### Impersonation Warning
```
WARNING: The extractor is attempting impersonation, but no impersonate target is available
```
**Fix**: Install curl_cffi. This is a non-fatal warning but may cause downstream failures.

### Geo-restricted Content
```
ERROR: This video is not available in your country
```
**Fix**: Consider using a VPN. yt-dlp supports `--proxy` flag:
```bash
yt-dlp --proxy socks5://127.0.0.1:1080 "{url}"
```

## Common Video Page Patterns

### OpenAI Forum Events
- Videos are Vimeo embeds
- Direct Vimeo URLs return 404 (private)
- Use `player.vimeo.com/video/{id}` with the forum page as referer

### Conference Talk Pages
- Often use Vimeo or YouTube embeds
- Check for `iframe` elements in the page source
- Some use custom players that wrap YouTube/Vimeo — look for the underlying embed URL

### Course/LMS Platforms
- Often use Wistia or Vimeo with domain restrictions
- Referer header is usually required
- May require cookies — use `--cookies-from-browser chrome` if needed
