#!/usr/bin/env python3
"""
setup_auth.py — One-time OAuth setup for YouTube API access.

Run this on your LOCAL machine (not in Cowork) to authorize the app
and cache the OAuth token. After this, all subsequent runs — including
in headless environments like Cowork — are fully automatic.

Usage:
  python setup_auth.py
  python setup_auth.py --credentials /path/to/client_secret.json
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path so we can import yt_auth
sys.path.insert(0, str(Path(__file__).parent))

from yt_auth import (
    CONFIG_DIR,
    DEFAULT_CREDENTIALS,
    TOKEN_PATH,
    get_credentials,
)


def main():
    parser = argparse.ArgumentParser(
        description="One-time OAuth setup for YouTube API"
    )
    parser.add_argument(
        "--credentials",
        default=str(DEFAULT_CREDENTIALS),
        help=f"Path to client_secret.json (default: {DEFAULT_CREDENTIALS})",
    )
    args = parser.parse_args()

    print("=== YouTube API — One-Time OAuth Setup ===")
    print(f"Config directory: {CONFIG_DIR}")
    print()

    creds_path = Path(args.credentials)

    # Try to find client_secret in Downloads if not in config dir
    if not creds_path.exists():
        import glob as g
        candidates = sorted(g.glob(str(Path.home() / "Downloads" / "client_secret_*.json")))
        if candidates:
            src = candidates[-1]  # most recent
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(src, DEFAULT_CREDENTIALS)
            print(f"Found credentials: {src}")
            print(f"Copied to: {DEFAULT_CREDENTIALS}")
            creds_path = DEFAULT_CREDENTIALS
        else:
            print(f"ERROR: No client_secret.json found at {creds_path}")
            print(f"       and no client_secret_*.json in ~/Downloads/")
            print()
            print("Download your OAuth credentials from Google Cloud Console:")
            print("  Google Auth Platform → Clients → your client → Download JSON")
            sys.exit(1)

    # Run the auth flow (opens browser)
    creds = get_credentials(creds_path)

    print()
    print("=== Setup Complete! ===")
    print(f"  client_secret.json: {DEFAULT_CREDENTIALS}")
    print(f"  token.pickle:       {TOKEN_PATH}")
    print()
    print("These credentials persist across Cowork sessions automatically.")
    print("You should not need to run this again unless you revoke access.")


if __name__ == "__main__":
    main()
