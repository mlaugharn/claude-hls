#!/usr/bin/env bash
# PostToolUse hook: warn Claude that HLS diagnostics are stale after .hs edits.
# Reads tool_input JSON on stdin, checks file extension, emits additionalContext.

set -euo pipefail

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // ""')

case "$FILE_PATH" in
  *.hs|*.lhs)
    jq -n '{
      hookSpecificOutput: {
        hookEventName: "PostToolUse",
        additionalContext: "HLS is reprocessing this file after your edit. Any diagnostics shown right now may be stale — wait for HLS to finish before acting on them."
      }
    }'
    ;;
esac

exit 0
