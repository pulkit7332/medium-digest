#!/usr/bin/env python3
"""
Scan local Claude Code session transcripts (~/.claude/projects/**/*.jsonl)
and emit lightweight per-session summaries as JSON, for the medium-digest
skill to read and judge for blog-worthy material.

Deliberately does NOT dump full transcript content: only titles, a handful
of user prompts per session, and basic counts/timestamps. This keeps output
bounded even when scanning a full history of hundreds of sessions.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

PROJECTS_DIR = os.path.expanduser("~/.claude/projects")
MAX_PROMPTS_PER_SESSION = 5
PROMPT_TRUNCATE = 220


def parse_iso(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def project_label(dirname):
    # Dirnames are the cwd with "/" replaced by "-", e.g.
    # -Users-pulkitgarg-Documents-GitHub-jasprr -> last 1-2 meaningful segments
    parts = [p for p in dirname.split("-") if p]
    return "/".join(parts[-2:]) if len(parts) >= 2 else dirname


def extract_text(content):
    """User/assistant message content can be a string or a list of blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                texts.append(block.get("text", ""))
        return " ".join(texts)
    return ""


def scan_file(path):
    session = {
        "session_id": None,
        "title": None,
        "cwd": None,
        "git_branch": None,
        "start_ts": None,
        "end_ts": None,
        "num_user_turns": 0,
        "num_assistant_turns": 0,
        "user_prompts": [],  # first few + last few, truncated
    }
    all_prompts = []
    try:
        with open(path, "r", errors="ignore") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue

                t = d.get("type")
                sid = d.get("sessionId")
                if sid and not session["session_id"]:
                    session["session_id"] = sid

                if t in ("custom-title", "agent-name"):
                    title = d.get("customTitle") or d.get("agentName")
                    if title:
                        session["title"] = title
                    continue

                if t not in ("user", "assistant"):
                    continue

                ts = parse_iso(d.get("timestamp"))
                if ts:
                    if session["start_ts"] is None or ts < session["start_ts"]:
                        session["start_ts"] = ts
                    if session["end_ts"] is None or ts > session["end_ts"]:
                        session["end_ts"] = ts

                if not session["cwd"] and d.get("cwd"):
                    session["cwd"] = d.get("cwd")
                if not session["git_branch"] and d.get("gitBranch"):
                    session["git_branch"] = d.get("gitBranch")

                msg = d.get("message") or {}
                role = msg.get("role")
                if t == "user" and role == "user":
                    text = extract_text(msg.get("content"))
                    if text.strip():
                        session["num_user_turns"] += 1
                        all_prompts.append(text.strip()[:PROMPT_TRUNCATE])
                elif t == "assistant" and role == "assistant":
                    session["num_assistant_turns"] += 1
    except (OSError, IOError):
        return None

    if not session["session_id"] or session["num_user_turns"] == 0:
        return None

    if len(all_prompts) <= MAX_PROMPTS_PER_SESSION:
        session["user_prompts"] = all_prompts
    else:
        head = all_prompts[:3]
        tail = all_prompts[-2:]
        session["user_prompts"] = head + ["..."] + tail

    session["start_ts"] = session["start_ts"].isoformat() if session["start_ts"] else None
    session["end_ts"] = session["end_ts"].isoformat() if session["end_ts"] else None
    return session


def iter_session_files():
    if not os.path.isdir(PROJECTS_DIR):
        return
    for project_dir in sorted(os.listdir(PROJECTS_DIR)):
        full_dir = os.path.join(PROJECTS_DIR, project_dir)
        if not os.path.isdir(full_dir):
            continue
        for fname in os.listdir(full_dir):
            if fname.endswith(".jsonl"):
                yield project_dir, os.path.join(full_dir, fname)


def load_state(state_file):
    if state_file and os.path.exists(state_file):
        try:
            with open(state_file) as fh:
                return json.load(fh)
        except (OSError, ValueError):
            return {}
    return {}


def save_state(state_file, state):
    os.makedirs(os.path.dirname(state_file), exist_ok=True)
    with open(state_file, "w") as fh:
        json.dump(state, fh, indent=2)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--since", help="ISO timestamp; only sessions active after this are included")
    ap.add_argument("--state-file", default=os.path.expanduser("~/Documents/medium-digest/state.json"))
    ap.add_argument("--use-state-since", action="store_true",
                     help="Use last_run_at from the state file as --since (ignored if --since is also given)")
    ap.add_argument("--max-sessions", type=int, default=300)
    ap.add_argument("--mark-run", action="store_true",
                     help="After scanning, write now() as last_run_at in the state file")
    ap.add_argument("--out", help="Write JSON to this file instead of stdout")
    args = ap.parse_args()

    since_dt = parse_iso(args.since)
    state = load_state(args.state_file)
    if since_dt is None and args.use_state_since:
        since_dt = parse_iso(state.get("last_run_at"))

    sessions = []
    for project_dir, path in iter_session_files():
        s = scan_file(path)
        if not s:
            continue
        s["project"] = project_label(project_dir)
        if since_dt:
            end_ts = parse_iso(s["end_ts"])
            if not end_ts or end_ts <= since_dt:
                continue
        sessions.append(s)

    sessions.sort(key=lambda s: s["end_ts"] or "", reverse=True)
    sessions = sessions[: args.max_sessions]

    result = {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "since": since_dt.isoformat() if since_dt else None,
        "is_first_run": since_dt is None,
        "session_count": len(sessions),
        "sessions": sessions,
    }

    out = json.dumps(result, indent=2)
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(out)
        print(f"Wrote {len(sessions)} sessions to {args.out}", file=sys.stderr)
    else:
        print(out)

    if args.mark_run:
        state["last_run_at"] = result["scanned_at"]
        save_state(args.state_file, state)
        print(f"Updated state file: last_run_at={result['scanned_at']}", file=sys.stderr)


if __name__ == "__main__":
    main()
