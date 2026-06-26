#!/usr/bin/env python3
"""Convert a Claude Code session JSONL to an Obsidian markdown note."""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT_DIR = Path("/home/user/Build-a-Bear")
SESSIONS_DIR = VAULT_DIR / "Sessions"


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:80]


def extract_text(content) -> str:
    """Return plain text from a message content field (str or list of blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )
    return ""


def convert_session(jsonl_path: str, output_dir: Path | None = None) -> Path:
    if output_dir is None:
        output_dir = SESSIONS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    messages: list[tuple[str, str]] = []
    title: str | None = None
    session_id: str | None = None
    cwd: str | None = None
    started_at: str | None = None

    with open(jsonl_path, encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue

            etype = entry.get("type")

            if etype == "ai-title" and not title:
                title = entry.get("aiTitle", "")
                session_id = session_id or entry.get("sessionId")

            elif etype == "user":
                session_id = session_id or entry.get("sessionId")
                cwd = cwd or entry.get("cwd")
                started_at = started_at or entry.get("timestamp")

                text = extract_text(entry.get("message", {}).get("content", ""))
                if text.strip():
                    messages.append(("user", text.strip()))

            elif etype == "assistant":
                text = extract_text(entry.get("message", {}).get("content", []))
                if text.strip():
                    # Merge consecutive assistant entries
                    if messages and messages[-1][0] == "assistant":
                        prev = messages[-1][1]
                        messages[-1] = ("assistant", prev + "\n\n" + text.strip())
                    else:
                        messages.append(("assistant", text.strip()))

    # ── Metadata ──────────────────────────────────────────────────────────────
    if started_at:
        dt = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
        date_str = dt.strftime("%Y-%m-%d")
        datetime_str = dt.strftime("%Y-%m-%d %H:%M UTC")
    else:
        now = datetime.now(timezone.utc)
        date_str = now.strftime("%Y-%m-%d")
        datetime_str = now.strftime("%Y-%m-%d %H:%M UTC")

    title = title or "Untitled Session"
    session_id = session_id or Path(jsonl_path).stem
    project = Path(cwd).name if cwd else "unknown"

    # ── Output path ───────────────────────────────────────────────────────────
    slug = slugify(title)
    base_name = f"{date_str}_{slug}"
    output_path = output_dir / f"{base_name}.md"

    # Handle duplicate filenames for different sessions on the same day
    counter = 1
    while output_path.exists():
        existing = output_path.read_text(encoding="utf-8")
        if f"session_id: {session_id}" in existing:
            break  # Same session – overwrite
        output_path = output_dir / f"{base_name}-{counter}.md"
        counter += 1

    # ── Render markdown ───────────────────────────────────────────────────────
    lines = [
        "---",
        f'title: "{title}"',
        f"date: {date_str}",
        f'datetime: "{datetime_str}"',
        f"session_id: {session_id}",
        f"project: {project}",
        f"cwd: {cwd or 'unknown'}",
        "tags:",
        "  - claude-session",
        "---",
        "",
        f"# {title}",
        "",
        f"**Date:** {datetime_str}  ",
        f"**Project:** {project}  ",
        f"**Session ID:** `{session_id}`",
        "",
        "---",
        "",
        "## Conversation",
        "",
    ]

    for role, text in messages:
        if role == "user":
            lines.append("> [!question]+ User")
            for line in text.split("\n"):
                lines.append(f"> {line}" if line else ">")
            lines.append("")
        else:
            lines.append("**Claude:**")
            lines.append("")
            lines.append(text)
            lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <session.jsonl> [output_dir]", file=sys.stderr)
        sys.exit(1)

    out = convert_session(
        sys.argv[1],
        Path(sys.argv[2]) if len(sys.argv) > 2 else None,
    )
    print(out)
