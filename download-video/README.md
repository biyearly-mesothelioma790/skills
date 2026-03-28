# Download Video

Downloads embedded videos from web pages using yt-dlp. Handles private/unlisted videos (especially Vimeo) by resolving the correct embed URL and adding referer headers.

## Problem

Many videos on event pages, forums, and course platforms are private/unlisted embeds. The direct video URL (e.g., `vimeo.com/123456`) returns 404. You need the embed player URL (`player.vimeo.com/video/123456`) plus the correct referer header to download them.

## How It Works

1. Fetches the target web page
2. Identifies the video hosting service and embed URL from iframes, schema.org metadata, or JS config
3. Resolves the correct player/embed URL
4. Downloads with yt-dlp, adding referer/origin headers as needed

## Prerequisites

```bash
brew install yt-dlp
pip3 install curl_cffi  # recommended, avoids OAuth errors
```

## Quick Usage

```bash
# Standard video
yt-dlp "https://player.vimeo.com/video/{id}"

# Private embed with referer
yt-dlp --referer "https://source-page.com/" "https://player.vimeo.com/video/{id}"

# List available qualities
yt-dlp -F "https://player.vimeo.com/video/{id}"
```

## Supported Hosts

Vimeo, YouTube, Wistia, Brightcove, Loom, and anything else yt-dlp supports. See SKILL.md for the full troubleshooting guide.
