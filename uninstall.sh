#!/usr/bin/env bash
set -euo pipefail

main() {
    echo "Uninstalling claude-shorts..."

    rm -rf "${HOME}/.claude/skills/shorts"

    echo "claude-shorts uninstalled."
    echo "Restart Claude Code to complete removal."
}

main "$@"
