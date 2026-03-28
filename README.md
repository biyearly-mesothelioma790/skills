This repo contains reusable skills for Claude Code, Codex, Cursor, and similar agent environments.

Each skill is a self-contained workflow with a `SKILL.md`, supporting scripts when needed, and a focused problem statement so an agent can pick the right tool quickly.

## Skills

- [new-mac-setup](./new-mac-setup) — opinionated Apple Silicon Mac bootstrap for fullstack and AI work. Installs Homebrew, shell tooling, editors, local AI tools, terminal setup, and macOS defaults in a repeatable run order.
- [download-video](./download-video) — downloads embedded or private video players from web pages by resolving the real player URL and calling `yt-dlp` with the right referer/origin headers.
- [youtube-api](./youtube-api) — programmatic YouTube channel management via the YouTube Data API v3. Handles OAuth setup, custom thumbnail uploads, metadata updates, and listing channel videos without relying on YouTube Studio's browser UI.

Click into each folder for the detailed workflow, prerequisites, and command examples.
