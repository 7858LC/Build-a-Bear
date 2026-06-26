#!/bin/bash
# Install gstack into ~/.claude/skills/gstack if not already present.
# Uses curl because the proxy only allows access to the configured repo.

set -euo pipefail

echo '{"async": true, "asyncTimeout": 300000}'

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

GSTACK_DIR="$HOME/.claude/skills/gstack"

if [ -d "$GSTACK_DIR" ] && [ -f "$GSTACK_DIR/README.md" ]; then
  exit 0
fi

echo "Installing gstack..."
curl -fsSL https://github.com/garrytan/gstack/archive/refs/heads/main.tar.gz \
  -o /tmp/gstack.tar.gz
mkdir -p "$HOME/.claude/skills"
tar -xzf /tmp/gstack.tar.gz -C /tmp/
rm -rf "$GSTACK_DIR"
mv /tmp/gstack-main "$GSTACK_DIR"
rm -f /tmp/gstack.tar.gz
echo "gstack installed at $GSTACK_DIR"
