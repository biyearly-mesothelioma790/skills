"""
Shared YouTube API authentication module.

Auto-detects the best credential directory (Cowork vs standard),
handles OAuth2 token caching and refresh, and builds the YouTube
API client.
"""

import glob
import pickle
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Config directory auto-detection
# ---------------------------------------------------------------------------

def find_config_dir() -> Path:
    """Find the best persistent config directory for credentials and tokens.

    In Cowork (Linux VM), ~/.config is ephemeral and resets between sessions,
    but the mounted Downloads folder lives on the user's actual machine and
    persists forever. We prefer that path so a one-time OAuth login stays valid
    across VM resets.

    Priority:
      1. Cowork mounted Downloads: /sessions/*/mnt/Downloads/.youtube-api/
      2. Standard fallback:        ~/.config/youtube-api/
    """
    for mnt in sorted(glob.glob("/sessions/*/mnt/Downloads")):
        if Path(mnt).is_dir():
            return Path(mnt) / ".youtube-api"
    return Path.home() / ".config" / "youtube-api"


CONFIG_DIR = find_config_dir()
DEFAULT_CREDENTIALS = CONFIG_DIR / "client_secret.json"
TOKEN_PATH = CONFIG_DIR / "token.pickle"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def get_credentials(client_secret_path: Path = None) -> object:
    """Authenticate via OAuth2. Opens browser on first run, caches token after."""
    if client_secret_path is None:
        client_secret_path = DEFAULT_CREDENTIALS

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
    except ImportError:
        print("ERROR: Missing dependencies. Install with:")
        print("  pip install google-api-python-client google-auth-oauthlib google-auth --break-system-packages")
        sys.exit(1)

    creds = None

    # Load cached token
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)
        print(f"  Using cached token from {TOKEN_PATH}")

    # Refresh or create new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not client_secret_path.exists():
                print(f"ERROR: Credentials file not found: {client_secret_path}")
                print()
                print("One-time setup required. See SKILL.md for instructions, or run:")
                print(f"  mkdir -p '{CONFIG_DIR}'")
                print(f"  mv ~/Downloads/client_secret_*.json '{DEFAULT_CREDENTIALS}'")
                sys.exit(1)

            print("Opening browser for Google OAuth consent...")
            print("(Authorize the app to manage your YouTube account)")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(client_secret_path), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Cache the token
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(creds, f)
        print(f"Token cached at {TOKEN_PATH}")

    return creds


def build_youtube_client(credentials_path: Path = None):
    """Authenticate and return a YouTube API client."""
    from googleapiclient.discovery import build

    creds = get_credentials(credentials_path)
    return build("youtube", "v3", credentials=creds)
