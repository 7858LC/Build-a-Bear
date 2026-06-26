#!/usr/bin/env python3
"""Import all existing Claude Code sessions into the Obsidian vault."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from session_to_obsidian import convert_session, SESSIONS_DIR, VAULT_DIR

CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"


def import_all() -> None:
    if not CLAUDE_PROJECTS_DIR.exists():
        print("No ~/.claude/projects directory found.", file=sys.stderr)
        sys.exit(1)

    # Collect all top-level session JSONL files (skip subagent subdirs)
    jsonl_files = [
        f
        for project_dir in CLAUDE_PROJECTS_DIR.iterdir()
        if project_dir.is_dir()
        for f in project_dir.glob("*.jsonl")
        if f.parent == project_dir  # must be a direct child, not nested
    ]

    if not jsonl_files:
        print("No session files found.")
        return

    print(f"Found {len(jsonl_files)} session(s) to import…")
    imported = 0
    for jsonl in sorted(jsonl_files):
        try:
            out = convert_session(str(jsonl))
            print(f"  ✓ {out.name}")
            imported += 1
        except Exception as exc:
            print(f"  ✗ {jsonl.name}: {exc}", file=sys.stderr)

    print(f"\nImported {imported}/{len(jsonl_files)} sessions → {SESSIONS_DIR}")
    _update_index()


def _update_index() -> None:
    """Regenerate Sessions/_Index.md with a table of all session notes."""
    notes = sorted(
        [n for n in SESSIONS_DIR.glob("*.md") if n.name != "_Index.md"],
        reverse=True,
    )

    rows = []
    for note in notes:
        stem = note.stem
        parts = stem.split("_", 1)
        date = parts[0] if len(parts) == 2 else ""
        friendly = parts[1].replace("-", " ").title() if len(parts) == 2 else stem
        rows.append(f"| {date} | [[Sessions/{stem}\\|{friendly}]] |")

    lines = [
        "---",
        'title: "Claude Sessions Index"',
        "tags:",
        "  - index",
        "  - claude-session",
        "---",
        "",
        "# Claude Sessions",
        "",
        f"*{len(notes)} session(s) total*",
        "",
        "| Date | Session |",
        "|------|---------|",
        *rows,
    ]

    index_path = SESSIONS_DIR / "_Index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Index updated: {index_path}")


if __name__ == "__main__":
    import_all()
