# HLS Plugin for Claude Code

This plugin integrates the Haskell Language Server (HLS) with Claude Code, enabling full LSP support for Haskell development including diagnostics, go-to-definition, find references, hover information, completions, and code actions for `.hs` and `.lhs` files. It includes a `/hls:status` command for quick health checks and a troubleshooting skill that guides you through diagnosing HLS issues when things aren't working. The plugin requires HLS (`haskell-language-server-wrapper`) to be installed and available in your PATH, along with an existing Cabal or Stack project—it handles project detection automatically.

## Prerequisites

- [Haskell Language Server](https://github.com/haskell/haskell-language-server) installed and available in your PATH
- A Cabal or Stack project

## Installation

1. Add the marketplace:
   ```
   /plugin marketplace add m4dc4p/claude-hls
   ```

2. Install the plugin:
   ```
   /plugin install hls@claude-hls
   ```

## Usage

- **Check HLS status**: Run `/hls:status` to verify HLS is installed and working
- **Troubleshooting**: If you encounter issues, ask Claude "HLS is not working, can you help?" to trigger the troubleshooting skill
- **LSP features**: Once working, Claude will automatically use HLS for diagnostics, completions, go-to-definition, and more when working with `.hs` or `.lhs` files
