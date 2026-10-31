# Author's actual Medium voice (reference)

Derived from the user's two strongest published posts on
https://medium.com/@pulkit7332 (RSS: https://medium.com/feed/@pulkit7332):
"We Ran Out of TCP Ports at 1:30 AM — the Crack Was tcp_tw_reuse=0" and
"We Gave Our Service More CPU — and It Took Down Production." Both are
published under his employer's engineering publication, **"Engineering @
Housing/Proptiger/Makaan"** — naming the employer/publication is fine and
already his practice; it's internal codenames, ticket IDs, team names and
teammates that get anonymized, not the company. (He also has a handful of
more generic explainer/listicle posts — "Optimizing Spring Boot for
Massive Scale," "Is Java Really Dead?" etc. — those are visibly lower
voice-distinctiveness than the two narrative posts above. Default to the
narrative voice below; it's the one actually building his reputation.)

## Structure — the Act 1-4 shape is the strongest default, not a mandate

The two reference posts both happen to be single-incident mysteries, which
is why they fall naturally into a four-act investigation. That shape is
the right default whenever the underlying story genuinely has a mystery
in it (a confusing symptom, a wrong turn, a reveal). It is not the voice
itself — don't force a story that isn't shaped like a mystery into four
acts just to match the template. A phased rollout, a "here's what I'd
tell someone about to do this" field guide, a before/after comparison, or
several short war-story beats strung together under one theme can all be
more engaging than a forced four-act structure, depending on what actually
happened. Pick the shape the real material supports; keep everything else
below (the hook, the steal-able lessons, the one-sentence TL;DR, the
sign-off, concrete numbers, no internal codenames) regardless of shape.

When the four-act shape does fit, here's what each beat is doing:

1. **Title**: "We [did X] — [ironic/surprising consequence]" or "We [did
   X]. [twist]." First-person plural. Concrete and specific, often with a
   telling detail (a time of day, an exact setting name, a number).
   **When the post is meant to teach a named technology or problem (not
   just recount one incident)**, lead the main title with that
   problem/technology and the headline win, so a reader scanning titles
   immediately knows what it's about — and demote the punchy incident hook
   to a subheading inside the piece, introducing the war-story section,
   rather than burying the topic under a clever title only insiders would
   click.
2. **One-line hook right under the title** (works as a subtitle): states
   the twist and the payoff in one sentence, so a reader decides to
   continue in 5 seconds.
3. **Act 1 — the mystery**: what broke, what it looked like from the
   outside, why the obvious explanations were all wrong. Short, punchy
   sentences. Build genuine suspense — don't reveal the cause yet.
4. **Act 2 — the wrong turn / the red herring**: what the team tried that
   didn't work, and *why* it looked like it should have worked. This is
   often where the best isolated lesson lives (e.g. "a partial rollback is
   not a rollback").
5. **Act 3 — the actual mechanism**: the real root cause, explained from
   first principles assuming a smart reader who doesn't know this specific
   system. Code snippets only where they clarify the mechanism. This is
   the most technically dense section and should still read like a story,
   not documentation.
6. **Act 4 — resolution**: the fix (usually two-layered: the fast
   mitigation and the real architectural fix), and the outcome in concrete
   numbers.

Whatever shape you pick, close with:

7. **"The lessons (the part you can steal)"** — H3 subheadings, each a
   complete bolded one-line claim (not "Lesson 1" — the actual lesson
   text as the heading), followed by 1-3 sentences that generalize it
   past this specific system. Usually 3-5 of these.
8. **"The one-sentence version"** — a single blockquote that compresses
   the whole story into one sentence. This is the line most likely to get
   quoted/screenshotted — write it to stand alone.
9. **Sign-off** — short, direct, a little warm: "Thanks for reading. If
   this saved you one 1:30 AM mystery, it did its job." Vary the specific
   line per post, keep the plainness and the implied "this is useful, not
   a victory lap" tone.

## Voice notes
- Bold is used for emphasis on the key clause of a sentence, not whole
  sentences — sparingly, so it still lands.
- Rhetorical/short-sentence beats for drama: "Nothing helped." / "It
  wasn't CPU exhaustion. It was thread starvation."
- Internal system names are described by business function ("a
  background-job service," "the lead-creation API," "a struggling
  service"), never by internal codename.
- Numbers are always concrete and real (port counts, request volumes,
  core counts, percentages) — never rounded into vague language like
  "significantly."
- Tags: lowercase-hyphenated, specific and plural where natural (e.g.
  `production-issue`, `jvm`, `kubernetes`, `optimization`, `java21`) —
  5-ish per post, mixing the technology and the theme.

Use this as the default voice for every drafted post and its LinkedIn
teaser, not just a one-off match for whatever prompted this file.
