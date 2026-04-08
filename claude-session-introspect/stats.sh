#!/usr/bin/env bash
# stats.sh — print headline stats for a Claude Code session JSONL.
#
# Usage:
#   bash stats.sh                     # auto-locate the newest session for $PWD
#   bash stats.sh /path/to/session.jsonl
#   bash stats.sh <session-uuid>      # search ~/.claude/projects for that uuid
#
# Output: token totals, turn counts, prompt counts, top tool calls, and any
# compaction events. Requires jq.

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq is required" >&2
  exit 1
fi

resolve_session() {
  local arg="${1:-}"
  if [[ -z "$arg" ]]; then
    local enc dir
    enc="-$(pwd | sed 's,/,-,g' | sed 's/^-//')"
    dir="$HOME/.claude/projects/$enc"
    if [[ ! -d "$dir" ]]; then
      echo "error: no project session dir at $dir" >&2
      echo "       (is this a Claude Code project? try passing the path explicitly)" >&2
      exit 1
    fi
    ls -t "$dir"/*.jsonl 2>/dev/null | head -1
    return
  fi
  if [[ -f "$arg" ]]; then
    echo "$arg"
    return
  fi
  # treat as uuid — search all project dirs
  local hit
  hit=$(find "$HOME/.claude/projects" -name "${arg}.jsonl" 2>/dev/null | head -1)
  if [[ -z "$hit" ]]; then
    echo "error: could not find session file or uuid: $arg" >&2
    exit 1
  fi
  echo "$hit"
}

SESSION=$(resolve_session "${1:-}")
echo "session: $SESSION"
echo

echo "── event counts ─────────────────────────────────────────"
jq -r '.type' "$SESSION" | sort | uniq -c | sort -rn

echo
echo "── token totals ─────────────────────────────────────────"
jq -s '
  [.[] | select(.message.usage)] |
  {
    assistant_turns:     length,
    input_tokens:        (map(.message.usage.input_tokens // 0)               | add),
    output_tokens:       (map(.message.usage.output_tokens // 0)              | add),
    cache_read_tokens:   (map(.message.usage.cache_read_input_tokens // 0)    | add),
    cache_create_tokens: (map(.message.usage.cache_creation_input_tokens // 0)| add)
  } |
  . + { effective_input_total: (.input_tokens + .cache_read_tokens + .cache_create_tokens) }
' "$SESSION"

echo
echo "── human prompts (excluding tool results & system reminders) ──"
jq -r '
  select(.type == "user" and .toolUseResult == null) |
  (.message.content
    | if type == "string" then .
      else (map(select(.type == "text") | .text) | join("\n"))
      end)
' "$SESSION" \
| awk '
    BEGIN { n = 0; cur = "" }
    /^$/  { if (cur != "" && cur !~ /^<system-reminder>/ && cur !~ /^<command-/) n++; cur=""; next }
    {     if (cur=="") cur=$0 }
    END   { if (cur != "" && cur !~ /^<system-reminder>/ && cur !~ /^<command-/) n++; print "human_prompts:", n }
  '

echo
echo "── tool calls (top 15) ──────────────────────────────────"
jq -r '
  select(.type == "assistant") |
  .message.content[]? |
  select(.type == "tool_use") |
  .name
' "$SESSION" | sort | uniq -c | sort -rn | head -15

echo
echo "── compaction events ────────────────────────────────────"
COMPACTS=$(jq -r 'select(.type=="system" and (.subtype // "") == "compact_boundary") | .timestamp' "$SESSION" | wc -l | tr -d ' ')
echo "count: $COMPACTS"
if [[ "$COMPACTS" -gt 0 ]]; then
  jq -r '
    select(.type == "system" and (.subtype // "") == "compact_boundary") |
    "  - \(.timestamp)  trigger=\(.compactMetadata.trigger // "unknown")  preTokens=\(.compactMetadata.preCompactTokens // "?")"
  ' "$SESSION"
fi
