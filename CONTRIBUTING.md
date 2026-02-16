# Contributing to claude-shorts

Thanks for your interest in contributing! Here's how to get involved.

## Reporting Bugs

Open a [GitHub Issue](https://github.com/AgriciDaniel/claude-shorts/issues) with:

- Your OS, Python version, Node.js version, and GPU info
- The full error output (copy from terminal)
- The command or step that failed
- Input video details (duration, resolution, codec) if relevant

## Suggesting Features

Use [GitHub Discussions](https://github.com/AgriciDaniel/claude-shorts/discussions) for feature ideas and questions.

## Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Test with a short video clip (under 5 minutes) before submitting
5. Submit a PR with a clear description of what changed and why

### Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/claude-shorts.git
cd claude-shorts
bash setup.sh
bash install.sh
```

### Guidelines

- All Python scripts should output JSON for Claude Code to parse
- Shell scripts should use `set -euo pipefail` for safety
- Test both GPU and CPU code paths when possible
- Keep dependencies minimal — don't add packages for single-use operations
