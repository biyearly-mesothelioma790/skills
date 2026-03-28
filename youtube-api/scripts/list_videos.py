#!/usr/bin/env python3
"""
list_videos.py — List videos from the authenticated user's YouTube channel.

Usage:
  python list_videos.py
  python list_videos.py --max-results 50
  python list_videos.py --json  # output as JSON for piping to other scripts
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from yt_auth import CONFIG_DIR, DEFAULT_CREDENTIALS, build_youtube_client


def list_channel_videos(youtube, max_results: int = 25) -> list:
    """List videos uploaded by the authenticated user."""
    # Get the user's upload playlist ID
    channels = youtube.channels().list(part="contentDetails", mine=True).execute()
    items = channels.get("items", [])
    if not items:
        raise ValueError("No channel found for this account")

    uploads_playlist = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Fetch videos from the uploads playlist
    videos = []
    page_token = None

    while len(videos) < max_results:
        remaining = max_results - len(videos)
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist,
            maxResults=min(remaining, 50),
            pageToken=page_token,
        )
        response = request.execute()

        for item in response.get("items", []):
            snippet = item["snippet"]
            videos.append({
                "video_id": snippet["resourceId"]["videoId"],
                "title": snippet["title"],
                "published_at": snippet["publishedAt"],
                "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
            })

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return videos


def main():
    parser = argparse.ArgumentParser(
        description="List videos from your YouTube channel"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=25,
        help="Maximum number of videos to return (default: 25)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON (for piping to other scripts)",
    )
    parser.add_argument(
        "--credentials",
        default=str(DEFAULT_CREDENTIALS),
        help=f"Path to OAuth client_secret.json (default: {DEFAULT_CREDENTIALS})",
    )

    args = parser.parse_args()

    print(f"Config directory: {CONFIG_DIR}", file=sys.stderr)
    youtube = build_youtube_client(Path(args.credentials))

    videos = list_channel_videos(youtube, args.max_results)

    if args.json:
        print(json.dumps(videos, indent=2))
    else:
        print(f"\nFound {len(videos)} video(s):\n")
        for v in videos:
            print(f"  {v['video_id']}  {v['published_at'][:10]}  {v['title']}")


if __name__ == "__main__":
    main()
