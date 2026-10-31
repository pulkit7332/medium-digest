---
name: medium-digest
description: >-
  Scans the user's own local Claude Code session history (every project,
  not just the current one) for day-to-day engineering work that could make
  a genuinely interesting Medium post that builds the user's reputation as
  a distinguished engineer — a tricky migration, a gnarly bug fix, an
  incident writeup, a reusable technique, a clean architecture decision,
  told with the judgment and point of view that makes senior engineers
  worth following. Surfaces a short, reasoned shortlist and, once the user
  picks one, drafts a polished Markdown post plus a short LinkedIn teaser,
  saved locally for the user to review and post themselves. NEVER calls any
  Medium or LinkedIn API and NEVER publishes anything automatically — this
  is draft-generation only. Use this whenever the user says "medium
  digest", "check my work for blog ideas", "what should I write about",
  "turn my recent work into a blog post", "any good Medium post ideas from
  this week", or when a scheduled weekly digest task invokes it.
  Self-contained: works correctly even when run from a fresh session with
  no memory of prior conversations.
argument-hint: "[--all]"
---

# Medium Digest

Turns the user's recent engineering work (read from local Claude Code
session transcripts) into Medium post ideas, and — only on explicit
selection — a draft post plus a LinkedIn teaser. This skill never publishes
anything. It never calls the Medium or LinkedIn API. It only ever reads
local transcripts (and, when useful, internal docs the user already wrote
about the same work) and writes local draft files. Treat "publish" as
permanently out of scope; the user posts the final draft in themselves.

**The actual goal is not "document what I did."** It's building the user's
reputation as a distinguished engineer with a technical audience —
Medium is the long-form home, LinkedIn is where that reputation actually
compounds through shares and comments. That changes the bar for both
selection and writing, not just where the output goes:
- A post succeeds if a senior engineer who has never heard of the user's
  employer still finds it worth their time and worth sharing. Internal
  war-story detail is raw material, not the finished product.
- Prefer topics with a real, defensible point of view or a counterintuitive
  lesson over topics that are just "here's a thing we built." A rewrite of
  an internal doc is not enough — it needs the judgment layer on top: why
  this over the obvious alternative, what you'd do differently, what
  generalizes to any reader's stack.
- Judge candidates partly by reach potential: would a staff/principal
  engineer at another company actually learn something, or just nod along?

This file is the whole brief — assume no memory of any earlier
conversation, since this also runs unattended from a scheduled task.

Skill directory: `~/Documents/medium-digest` (referred to below as `$SKILL_DIR`).
State file: `$SKILL_DIR/state.json`. Drafts: `$SKILL_DIR/drafts/`.

## Step 1 — Scan session history

Run the bundled scanner:

```bash
python3 "$SKILL_DIR/scripts/scan_sessions.py" \
  --use-state-since \
  --state-file "$SKILL_DIR/state.json" \
  --mark-run \
  --out /tmp/medium-digest-scan.json
```

This walks every `*.jsonl` session transcript under `~/.claude/projects/`
(across ALL of the user's projects, not just the one you're running in) and
writes lightweight per-session summaries — title, project, timestamps, turn
counts, and a handful of truncated prompts — to the JSON file. It does not
dump full transcripts, so the output stays small even over months of
history.

**Time window:**
- If the user invoked this with `--all` as an argument, or if this is
  clearly the *first ever run* (no `$SKILL_DIR/state.json` exists yet),
  drop `--use-state-since` from the command above so it scans **the entire
  history from the beginning**, not just a recent window.
- Otherwise `--use-state-since` makes it only return sessions active since
  the last time this skill ran (tracked in `state.json`), which is exactly
  what you want for a recurring weekly digest — it naturally never
  re-surfaces material you've already reviewed.
- `--mark-run` always updates `state.json` to "now" as part of this scan,
  regardless of time window, so the *next* run starts from here. Keep it on
  every invocation, including the first full-history one.

Read `/tmp/medium-digest-scan.json`. The top-level `is_first_run` field and
`session_count` tell you what you're working with — if it's the first run
with 100+ sessions, that's expected; read through all of them.

## Step 2 — Judge what's actually interesting

Go through the sessions and pick candidates for a blog post. Be genuinely
selective — most day-to-day work is not blog-worthy, and a shortlist of
mediocre ideas is worse than a short, sharp one. A few sessions on the same
underlying piece of work (e.g. a migration debugged across three sessions
over a week) are **one candidate**, not three.

**Look for:**
- A problem that took real effort to run down (a gnarly bug, a confusing
  failure mode, a subtle bug class) and was actually resolved
- A migration, upgrade, or architectural change with non-obvious gotchas
- An incident or outage with a clear root cause and a lesson
- A reusable technique, tool, or workflow the user built that others would
  want to steal
- A decision with real tradeoffs that got reasoned through, not just
  executed

**Discard:**
- Personal/non-work musings with no connection to an actual codebase or
  task (startup ideas, "what if AI..." philosophizing, general Q&A) — these
  show up as sessions with no real `cwd`/project substance behind them
- Trivial one-off questions or lookups, however many turns they took
- Unfinished or abandoned explorations with no resolution worth reporting
- Anything that only makes sense wrapped in proprietary internal context
  that can't be meaningfully generalized for a public, external audience
- Topics that duplicate a draft already sitting in `$SKILL_DIR/drafts/`
  (check that folder's existing filenames/frontmatter `source_sessions`
  before finalizing your shortlist)

End up with **3 to 7 candidates**. For each, write one sharp sentence
explaining why it's interesting — not a restatement of the title.

## Step 3 — Let the user choose

Use `AskUserQuestion` with a single question whose options are your
candidates (label = short punchy working title, description = your
one-line "why this" reasoning). Make clear in the question wording that
picking none is fine — the user can decline via "Other" and say so, or you
can add an explicit "None of these this week" option if the tool allows
only predefined options and no real pick stands out.

If the user picks nothing, stop here. Report what you found and why none
of it seemed worth writing up, and that the scan state has still been
updated so next time starts fresh from today.

## Step 4 — Draft the post (only after a pick)

**Match the author's actual voice.** Read `$SKILL_DIR/references/voice.md`
before writing anything — it's derived from the user's own strongest
published posts (fetched from his Medium RSS feed) and defines the real
structure to follow: a narrative "Act 1 / Act 2 / Act 3 / Act 4"
investigation, a "lessons (the part you can steal)" closer, a "the
one-sentence version" blockquote TL;DR, and a short direct sign-off. Don't
substitute a generic blog-post shape for this — it's what's actually
working for him. It also settles the sanitization question below: he
already publishes under his employer's real engineering publication name,
so the employer name is fine to use; it's internal codenames, ticket IDs,
team names and teammates that still get anonymized into their business
function, exactly as his own published posts already do.

**Images are part of the draft, not optional.** Read
`$SKILL_DIR/references/images.md` for how to produce a hero image plus any
inline diagrams the post needs, and for the one hard platform constraint
(Medium rejects SVG outright — only PNG/JPEG/WEBP/AVIF/GIF work). Save
generated images into `$SKILL_DIR/drafts/images/` alongside the post.

If the session transcripts point at an internal doc the user already wrote
about this work (a Confluence page, a design doc, a Slack writeup they
mention), and a tool to fetch it is available, pull it — it's the most
accurate source of real numbers and decisions, better than reconstructing
from fragmented transcript snippets. Treat it as factual raw material to
reframe for an external audience, not something to summarize as-is: an
internal doc's job is to inform colleagues, a Medium post's job is to teach
strangers and make them want to follow the author.

**But don't stop at the polished doc if the real R&D sessions are still
available.** A summary doc smooths over exactly the texture that makes a
post feel like a real investigation — the actual crash log, the wrong turn
that got tried first, the specific diagnostic command that cracked it. If
the source session transcripts for this candidate are still on disk,
read them directly (a background agent/fork is the right tool for this if
the sessions are long, so it doesn't blow your own context) and ground the
draft in what was actually typed and seen, not just the after-the-fact
summary. This consistently produces a sharper, more specific post than
paraphrasing the doc alone.

Write a Markdown file to `$SKILL_DIR/drafts/<YYYY-MM-DD>-<slug>.md` with:

```markdown
---
source_sessions: [<session_id>, ...]
source_projects: [<project>, ...]
source_docs: [<url>, ...]   # omit if none
generated_at: <ISO timestamp>
status: draft
---

# <Title>

*<One-line subtitle/dek — the hook, not a summary>*

![<alt text describing the headline number/claim>](images/fig0-hero.png)

<Body: an actual narrative with a point of view, not an internal report.
State the problem in terms any senior engineer recognizes before naming
your specific stack. Show the reasoning behind the decision (why this over
the obvious alternatives — a reader should learn how to think about this
class of problem, not just what you picked), the real numbers, and the
gotchas that only show up in production. Use code snippets where they
clarify, not to pad length. Write like someone with opinions worth
following, not like release notes or a status update.>

## Lessons / takeaways

- <Each one should generalize past this specific company/stack — write it
  so it's useful to someone who will never touch this codebase.>

---
**Suggested tags:** tag1, tag2, tag3, tag4
**Estimated read time:** ~X min

---
## LinkedIn teaser

<A standalone 2-4 sentence post: the hook/counterintuitive claim up front,
written the way the user would talk about it, not an ad for the article.
Ends with something like "Full writeup: <link>" — leave the actual URL for
the user to fill in once they've posted to Medium.>
```

**Before writing a single word of the draft, sanitize.** This content comes
from real work at a real employer. The employer/publication name itself is
fine (see the voice note above — he already publishes under it); generalize
or remove:
- Internal hostnames, service names, repo names, Jira/ticket IDs
  (e.g. rewrite "AV-1915" as "a reliability ticket")
- Proprietary business metrics, customer data, or anything competitively
  sensitive
- Any credential, token, API key, internal URL, or IP address that might
  have leaked into a transcript via a command's output — never let one into
  the draft even as an example

When in doubt, generalize rather than guess at what's safe. Tell the user
explicitly, when you hand off the draft, that they should give it one more
read for sensitive specifics themselves before publishing — they know
their employer's disclosure norms better than this skill does.

Tell the user the draft's file path. Do not open Medium, do not call any
API, do not create any account or integration. This skill's job ends at a
reviewed-and-sanitized local file.

## If the user explicitly asks you to build the draft directly in Medium

The default is always the local file above. But if the user explicitly
asks you to go further — put it directly into their Medium account, add
the images for them there, etc. — that's a reasonable request to help
with, using their real signed-in browser (Claude in Chrome). Read
`$SKILL_DIR/references/medium-browser-posting.md` first; it covers the
real gotchas (Medium doesn't auto-convert typed Markdown, its image button
opens a native file picker this automation can't use, and precise
click-based text editing is easy to get subtly wrong). This is never
something to do unprompted, and never something to do from an unattended
scheduled run — only on a direct, explicit ask in a live conversation. The
one rule that never changes regardless: never click Publish. That stays
the user's action, always.

## Notes for scheduled/unattended runs

When this skill is invoked by a scheduled task rather than typed by the
user directly, follow the exact same steps — the only difference is you
won't get a live chat turn-by-turn; `AskUserQuestion` still works and will
surface to the user whenever they next look, and the shortlist + any draft
produced are what they'll see. Never skip the sanitization step just
because no one is watching in real time.
