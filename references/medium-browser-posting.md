# Putting a draft directly into Medium's own editor (explicit-request only)

**This is not part of the normal flow.** The default, every time, is a
local Markdown file the user pastes in themselves — that's what makes this
skill safe to run unattended. Only use anything in this file when the user
explicitly asks you to put the draft directly into their Medium account
("can you do that," "add the images for me," "do it in Medium"), never as
a step you decide to take on your own, and never from a scheduled/
unattended run. **Never click Publish, under any circumstance, regardless
of what the user asks for in this flow** — that action stays theirs,
always; this file is only about getting a draft built and saved (Medium
autosaves drafts continuously).

## Prerequisites

- Driving this needs `mcp__claude-in-chrome__*` tools (load them via the
  chrome-browser skill first) so you're acting in the user's real,
  already-logged-in Chrome — the built-in browser pane is a separate,
  logged-out browser and can't reach their Medium session.
- Confirm the user is actually signed in before doing anything else:
  navigate to `medium.com/new-story` and screenshot. If it shows a
  sign-in screen, tell the user and wait for them to sign in themselves —
  never enter credentials or pick a sign-in provider on their behalf.

## Typing content: Medium does not auto-convert Markdown from simulated keystrokes

Typing `## `, `**bold**`, `*italic*`, `` ``` ``, or `> ` via the `type`
action does **not** trigger Medium's live Markdown shortcuts the way a
human typing the same characters would — they land as literal characters.
Don't fight this. Instead:

1. Type the plain prose (no Markdown symbols at all — strip `#`, `*`,
   `` ` ``, `>` before typing) in large batched chunks, one logical
   section per `type` call, separated by `\n` (each `\n` becomes its own
   paragraph block). Skip the frontmatter, the `---` dividers, the
   "Suggested tags" line, and the LinkedIn teaser section — none of that
   goes in the Medium body.
2. Convert any Markdown table in the source file to plain labeled lines
   before typing (e.g. `| Metric | Before | After |` rows become
   `Metric: X before, Y after.` sentences) — Medium's editor has no table
   block at all, so a literal table would just paste as broken pipe
   characters.
3. Go back and apply real formatting with keyboard shortcuts, which *do*
   work correctly here:
   - Select a line (`triple_click`) → `cmd+alt+1` for a large section
     heading, `cmd+alt+2` for a smaller sub-heading. Clicking the same
     (now green/active) icon in the floating toolbar again toggles a
     heading back to plain paragraph text.
   - Select text → `cmd+b` bold, `cmd+i` italic.
   - A "lesson" line that's meant to be its own bolded header (see
     `voice.md`) needs to be split into its own paragraph first — click
     right after the sentence's final period, press `Return`, then select
     and bold just that new paragraph. Don't try to bold only part of a
     paragraph in place; block-level formatting applies to the whole
     block.

### Changing the title after the fact is its own trap

Triple-clicking the title and typing a replacement can merge the new
title text directly into the very next paragraph (the title block and
the first body paragraph momentarily become one block) — this reproduced
identically twice in testing, not a one-off fluke. Recovery:

1. Click right at the boundary where the title text ends and the
   paragraph text begins (zoom in to find it precisely), and press
   `Return` to re-split them.
2. This can occasionally leave the title **empty** instead of restored —
   check with a screenshot before assuming it worked. If it's empty,
   just click into it and type the title fresh; don't try to undo your
   way out of it.
3. Confirm the paragraph below the title is still italicized afterward —
   the split sometimes drops that formatting even though the text
   survives, so re-apply `cmd+i` if needed.

Treat any title edit as needing a follow-up screenshot check, not a
fire-and-forget action.

### Precision matters more than it looks like it should

Clicking "right after this word" by eyeballed pixel coordinates is
genuinely error-prone — a click landing one character off and then
pressing `Return` or `Backspace` will silently eat or misplace a
character, and it's easy not to notice until you look closely. Concretely:
- After clicking near a boundary, `zoom` into a tight region around the
  cursor before acting on it, to confirm it landed exactly where intended
  (hidden-behind-the-cursor-icon characters make a correct click look
  wrong in a normal screenshot — zoom in before concluding something is
  missing).
- To select exactly to the end of a paragraph without guessing a pixel
  position, `triple_click` the whole paragraph (safe, selects the full
  block regardless of how many visual lines it wraps to) then press
  `Right` once — this collapses the selection to its end, giving an exact
  cursor position for free.
- After any split-and-reformat edit, re-read the surrounding text (`zoom`
  or a fresh screenshot) before moving to the next edit, and do a final
  top-to-bottom read of the whole draft when done. A stray empty
  paragraph or a dropped/duplicated letter from a slightly-off click is
  easy to introduce and easy to miss without this check.

## Images: Medium rejects SVG, and its image button opens an unclosable dialog

Read `references/images.md` first for how to get PNGs at all. Once you
have them, **do not click Medium's own "Add an image" button or any
visible file-input element** — it opens the OS's native file picker,
which this automation cannot see or interact with, and the session will
appear to hang. Instead:

1. Create an empty paragraph at the insertion point (same split technique
   as above: click, collapse selection, `Return`).
2. Inject a plain, visible `<input type="file">` into the page yourself
   via a JS tool call (give it a unique `id` each time):
   ```js
   const inp = document.createElement('input');
   inp.type = 'file';
   inp.id = 'claude-tmp-upload';
   document.body.appendChild(inp);
   ```
3. Find that element (`find` with a query like "file input element" — it
   shows up as a `button (file)` in the accessibility tree) and call the
   `file_upload` tool with its `ref` and the image's path. **The path
   must be inside a folder this session is allowed to read** — a folder
   under the project working directory, or the session's scratchpad
   directory; copy the PNG there first if it lives elsewhere (e.g. in
   `$SKILL_DIR/drafts/images/`, which is outside the allowed set).
4. With the file now sitting in that input's `.files`, simulate a real
   drop onto the empty paragraph with a small JS call (no giant base64
   string needed — the File object already exists in the page):
   ```js
   (async () => {
     const inp = document.getElementById('claude-tmp-upload');
     const file = inp.files[0];
     const dt = new DataTransfer();
     dt.items.add(file);
     const x = /* the empty paragraph's x */, y = /* its y */;
     const el = document.elementFromPoint(x, y);
     const opts = {bubbles: true, cancelable: true, composed: true, dataTransfer: dt, clientX: x, clientY: y};
     el.dispatchEvent(new DragEvent('dragenter', opts));
     el.dispatchEvent(new DragEvent('dragover', opts));
     el.dispatchEvent(new DragEvent('drop', opts));
     inp.remove();
   })();
   ```
5. Screenshot to confirm the image actually landed (Medium shows it
   inline immediately, green-outlined while still selected). Click
   elsewhere to deselect before moving on.

This same hidden-input-plus-synthetic-drop technique is the general
pattern for getting a real local file into any web app's file-drop zone
without triggering a native OS dialog — it isn't Medium-specific.

## When you're done

Tell the user the draft is saved (Medium autosaves continuously — there's
no explicit "save" step) and give them the draft's URL from the browser's
address bar. Remind them Publish is theirs to click.
