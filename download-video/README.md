# Download Video

Downloads embedded videos from web pages using `yt-dlp`. This skill is for cases where the obvious video URL fails because the real downloadable source is hidden behind an embed player, referer restriction, or private/unlisted hosting setup.

Use it when a page contains a Vimeo, YouTube, Wistia, Brightcove, Loom, or similar embedded player and you want the actual media file locally.

## Problem

Many videos on event pages, forums, and course platforms are private/unlisted embeds. The direct video URL (e.g., `vimeo.com/123456`) returns 404. You need the embed player URL (`player.vimeo.com/video/123456`) plus the correct referer header to download them.

## What This Skill Does

- Inspects the source page for iframe, metadata, and player config hints
- Resolves the correct embed/player URL instead of the public landing page URL
- Adds `referer` and `origin` headers when the host requires them
- Falls back through progressively stronger `yt-dlp` invocation patterns

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
