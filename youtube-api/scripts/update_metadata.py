#!/usr/bin/env python3
"""
update_metadata.py — Update YouTube video metadata (title, description, tags).

Usage:
  # Update a single video:
  python update_metadata.py --video-id VIDEO_ID --title "New Title"
  python update_metadata.py --video-id VIDEO_ID --title "New Title" --description "New desc" --tags "tag1,tag2"

  # Batch update from JSON file:
  python update_metadata.py --batch updates.json

  updates.json format:
  [
    {"video_id": "abc123", "title": "New Title", "description": "New description"},
    {"video_id": "def456", "tags": ["tag1", "tag2", "tag3"]}
  ]

Only fields you specify are updated — everything else is preserved.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from yt_auth import CONFIG_DIR, DEFAULT_CREDENTIALS, build_youtube_client


def get_video_snippet(youtube, video_id: str) -> dict:
    """Fetch the current snippet for a video."""
    response = youtube.videos().list(part="snippet", id=video_id).execute()
    items = response.get("items", [])
    if not items:
        raise ValueError(f"Video not found: {video_id}")
    return items[0]["snippet"]


def update_video(youtube, video_id: str, title: str = None,
                 description: str = None, tags: list = None) -> dict:
    """Update a video's metadata. Only specified fields are changed."""
    # Fetch current snippet to preserve unmodified fields
    snippet = get_video_snippet(youtube, video_id)

    if title is not None:
        snippet["title"] = title
    if description is not None:
        snippet["description"] = description
    if tags is not None:
        snippet["tags"] = tags

    # categoryId is required for update even if unchanged
    body = {
        "id": video_id,
        "snippet": {
            "title": snippet["title"],
            "description": snippet["description"],
            "tags": snippet.get("tags", []),
            "categoryId": snippet["categoryId"],
        },
    }

    return youtube.videos().update(part="snippet", body=body).execute()


def main():
    parser = argparse.ArgumentParser(
        description="Update YouTube video metadata (title, description, tags)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video-id", help="YouTube video ID")
    group.add_argument("--batch", help="Path to JSON file with batch updates")

    parser.add_argument("--title", help="New video title")
    parser.add_argument("--description", help="New video description")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument(
        "--credentials",
        default=str(DEFAULT_CREDENTIALS),
        help=f"Path to OAuth client_secret.json (default: {DEFAULT_CREDENTIALS})",
    )

    args = parser.parse_args()

    print(f"Config directory: {CONFIG_DIR}")
    youtube = build_youtube_client(Path(args.credentials))

    updates = []
    if args.video_id:
        update = {"video_id": args.video_id}
        if args.title:
            update["title"] = args.title
        if args.description:
            update["description"] = args.description
        if args.tags:
            update["tags"] = [t.strip() for t in args.tags.split(",")]
        if len(update) == 1:
            parser.error("Specify at least one of --title, --description, or --tags")
        updates.append(update)
    else:
        with open(args.batch) as f:
            updates = json.load(f)
        print(f"Loaded {len(updates)} update(s) from {args.batch}")

    print(f"\nUpdating {len(updates)} video(s)...\n")
    successes = 0
    failures = 0

    for update in updates:
        vid = update["video_id"]
        try:
            update_video(
                youtube,
                vid,
                title=update.get("title"),
                description=update.get("description"),
                tags=update.get("tags"),
            )
            fields = [k for k in ("title", "description", "tags") if k in update]
            print(f"  \u2713 {vid}: Updated {', '.join(fields)}")
            successes += 1
        except Exception as e:
            print(f"  \u2717 {vid}: {e}")
            failures += 1

    print(f"\nDone: {successes} succeeded, {failures} failed")
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
