#!/usr/bin/env bash
# Fallback wrapper in case ${CLAUDE_PLUGIN_ROOT} doesn't expand in .lsp.json.
# Install: symlink or copy to somewhere in $PATH, or set .lsp.json command to
# the absolute path of this script.
exec python3 "$(dirname "$0")/hls-proxy.py" "$@"
