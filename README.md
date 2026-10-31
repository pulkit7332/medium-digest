# medium-digest

A Claude Code skill that scans your own local Claude Code session history
and turns genuinely interesting day-to-day engineering work into Medium
post ideas — then, only after you pick one, drafts a post plus a LinkedIn
teaser. It never calls any Medium/LinkedIn API and never publishes
anything; it only reads local session transcripts and writes local draft
files for you to review and post yourself.

## What it does

1. Scans every local Claude Code session transcript under
   `~/.claude/projects/**/*.jsonl` (all your projects, not just one repo)
   since the last time it ran.
2. Judges what's actually interesting — not "what did I do" but "would a
   senior engineer elsewhere learn something from this and want to share
   it." Groups multi-session work into one candidate, discards personal/
   trivial/unresolved threads.
3. Shows you a shortlist (3-7 candidates) with a one-line reason each and
   lets you pick one (or none).
4. If you pick one: pulls in any internal doc you already wrote about the
   same work (via Confluence, if that connector's available) — or, better,
   the real session transcripts if they're still around, for the texture a
   polished doc smooths over — sanitizes internal names/tickets/teammates,
   and drafts a post in your own voice (see below), with a hero image and
   inline diagrams, plus a short LinkedIn teaser — saved locally.

## Install

```bash
git clone https://github.com/pulkit7332/medium-digest.git ~/Documents/medium-digest
ln -s ~/Documents/medium-digest ~/.claude/skills/medium-digest
```

Then just ask Claude Code: `/medium-digest` (or "check my work for blog
ideas", "what should I write about this week"). First run scans your
entire local history; later runs are incremental.

## Make it sound like you, not me

`references/voice.md` is a style guide extracted from *my* own published
Medium posts (structure, tone, sign-off pattern) — it's there as a worked
example, not a universal voice. To make drafts sound like you:

1. Replace the two example posts it's built from with links to 1-2 of
   your own strongest published posts (or skip this if you don't have any
   yet — the skill still works, just with a more generic voice).
2. Ask Claude Code to read those and regenerate `references/voice.md` in
   the same format — the section headers it uses are deliberately
   reusable, not tied to my specific posts.

Don't feel bound to the "Act 1-4 investigation" structure the example
leans on — it's the right shape for stories that are genuinely a mystery,
and the wrong shape to force onto a story that isn't. `voice.md` says this
explicitly; pick whatever structure best fits the actual material.

## What's personal vs. reusable

- `SKILL.md`, `scripts/scan_sessions.py` — fully reusable, no changes
  needed.
- `references/voice.md` — reusable as a template; regenerate for your own
  voice as above.
- `references/images.md` — how to generate a hero image + diagrams as PNG
  (Medium rejects SVG), fully reusable.
- `references/medium-browser-posting.md` — optional, explicit-request-only
  technique for having Claude build the draft directly inside your Medium
  account using Claude in Chrome, instead of you pasting the file in
  yourself. Never used automatically; never clicks Publish.
- `state.json`, `drafts/*.md` — personal to each install; gitignored.

## Weekly automation

In Claude Code, create a scheduled task pointing at this skill's
`SKILL.md` (e.g. via the `scheduled-tasks` tool or the app's Scheduled
section) on whatever cadence you want. It's entirely local and offline
apart from the optional Confluence lookup — nothing it does requires this
repo to be shared or public beyond that.
