#!/usr/bin/env python3
"""
set_thumbnail.py — Upload custom thumbnails to YouTube videos via the Data API v3.

Usage:
  # Single video:
  python set_thumbnail.py --video-id VIDEO_ID --thumbnail /path/to/image.jpg

  # Batch mode:
  python set_thumbnail.py --batch VIDEO_ID_1:/path/to/thumb1.jpg VIDEO_ID_2:/path/to/thumb2.jpg

  # Custom credentials location:
  python set_thumbnail.py --video-id VIDEO_ID --thumbnail /path/to/image.jpg \
    --credentials /path/to/client_secret.json
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from yt_auth import CONFIG_DIR, DEFAULT_CREDENTIALS, build_youtube_client

MAX_THUMBNAIL_BYTES = 2 * 1024 * 1024  # 2 MB


def validate_thumbnail(path: str) -> Path:
    """Validate thumbnail file exists, is the right format, and is under 2 MB."""
    p = Path(path).expanduser().resolve()

    if not p.exists():
        raise FileNotFoundError(f"Thumbnail not found: {p}")

    size = p.stat().st_size
    if size > MAX_THUMBNAIL_BYTES:
        raise ValueError(
            f"Thumbnail too large: {size:,} bytes ({size / 1024 / 1024:.1f} MB). "
            f"Max is 2 MB. Compress with:\n"
            f"  convert '{p}' -resize 1280x720 -quality 85 output.jpg"
        )

    suffix = p.suffix.lower()
    if suffix not in (".jpg", ".jpeg", ".png"):
        raise ValueError(f"Unsupported format: {suffix}. Use .jpg or .png")

    return p


def set_thumbnail(youtube, video_id: str, thumbnail_path: Path) -> dict:
    """Upload a custom thumbnail for a YouTube video."""
    from googleapiclient.http import MediaFileUpload

    mime = "image/jpeg" if thumbnail_path.suffix.lower() in (".jpg", ".jpeg") else "image/png"

    media = MediaFileUpload(str(thumbnail_path), mimetype=mime, resumable=False)
    request = youtube.thumbnails().set(videoId=video_id, media_body=media)
    return request.execute()


def main():
    parser = argparse.ArgumentParser(
        description="Upload custom thumbnails to YouTube videos via the Data API v3"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video-id", help="YouTube video ID (use with --thumbnail)")
    group.add_argument(
        "--batch",
        nargs="+",
        metavar="VIDEO_ID:PATH",
        help="Batch mode: VIDEO_ID:/path/to/thumb.jpg pairs",
    )
    parser.add_argument("--thumbnail", help="Path to thumbnail image (use with --video-id)")
    parser.add_argument(
        "--credentials",
        default=str(DEFAULT_CREDENTIALS),
        help=f"Path to OAuth client_secret.json (default: {DEFAULT_CREDENTIALS})",
    )

    args = parser.parse_args()

    # Build the list of (video_id, thumbnail_path) pairs
    pairs = []
    if args.video_id:
        if not args.thumbnail:
            parser.error("--thumbnail is required when using --video-id")
        pairs.append((args.video_id, args.thumbnail))
    else:
        for item in args.batch:
            if ":" not in item:
                parser.error(f"Invalid batch format: '{item}'. Use VIDEO_ID:/path/to/thumb.jpg")
            vid, path = item.split(":", 1)
            pairs.append((vid, path))

    print(f"Config directory: {CONFIG_DIR}")

    # Validate all thumbnails before starting
    validated = []
    for video_id, thumb_path in pairs:
        try:
            p = validate_thumbnail(thumb_path)
            validated.append((video_id, p))
            print(f"  \u2713 {video_id} \u2192 {p.name} ({p.stat().st_size / 1024:.0f} KB)")
        except (FileNotFoundError, ValueError) as e:
            print(f"  \u2717 {video_id}: {e}")
            sys.exit(1)

    # Authenticate and upload
    youtube = build_youtube_client(Path(args.credentials))

    print(f"\nUploading {len(validated)} thumbnail(s)...\n")
    successes = 0
    failures = 0

    for video_id, thumb_path in validated:
        try:
            set_thumbnail(youtube, video_id, thumb_path)
            print(f"  \u2713 {video_id}: Thumbnail set successfully")
            successes += 1
        except Exception as e:
            print(f"  \u2717 {video_id}: {e}")
            failures += 1

    print(f"\nDone: {successes} succeeded, {failures} failed")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
