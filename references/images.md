# Images for a drafted post

His real published posts always carry images: a hero/header figure right
after the hook paragraph, plus 1-3 inline diagrams at the moments that
actually need a picture (a mechanism, a before/after, a timeline). A wall
of text with no images reads as unfinished by comparison — treat images as
part of the draft, not an optional extra.

## The one hard constraint: Medium does not accept SVG

Confirmed directly against Medium's own uploader: it rejects `.svg` with
"The file you tried to upload is a type we don't understand. Supported
image formats are JPEG, PNG, WEBP, AVIF, and GIF." This is true whether
the upload happens through the UI or by simulating a drop — the server
itself checks and rejects the file type, so there is no client-side way
around it. **Always deliver PNG (or JPEG), never SVG**, for any image
meant to end up in the post — including ones you hand the user to drag in
themselves, since they'll hit the same rejection.

## How to actually produce a PNG without a local rasterizer

This machine has no `rsvg-convert`, `inkscape`, or `cairosvg` installed —
don't assume one exists. The reliable path, using only tools already in
this session:

1. Write the diagram as inline SVG (viewBox sized to the final pixel
   dimensions you want, e.g. `0 0 900 360` for a 900×360 image).
2. Open a scratch browser tab (built-in browser or Claude in Chrome) at
   a plain, permissive page (`https://example.com` works — it has no CSP
   that would block inline content), then inject the SVG directly as the
   page body via a JS tool call:
   ```js
   document.documentElement.innerHTML = '<head></head><body style="margin:0;padding:0"></body>';
   document.body.innerHTML = `<svg viewBox="0 0 900 360" ... width="900" height="360">...</svg>`;
   ```
3. Resize the browser window to comfortably exceed the SVG's dimensions
   (`resize_window`, e.g. 900×420 for a 900×360 graphic).
4. Capture it with the `zoom` action, region `[0, 0, <width>, <height>]`,
   `save_to_disk: true`. This returns a real PNG file on disk at the exact
   pixel size you asked for — crop to the SVG's own bounds, not the full
   viewport, so there's no extra whitespace or browser chrome.
5. Copy that PNG into `$SKILL_DIR/drafts/images/` with a clear name
   (`fig0-hero.png`, `fig1-timeline.png`, ...). Close the scratch tab.

This is cheap and reliable. Do **not** try to pass image bytes through
your own context as a base64 string "just to be safe" — a ~110KB PNG can
burn on the order of 100K+ tokens as base64 text in a model context, for
no benefit, since the browser can read the file from disk itself.

## Design guidelines (keep every figure looking like it belongs together)

- White background, dark text, 1-3 accent colors used consistently
  across all figures in the same post (e.g. a muted red/slate for
  "before," green for "after," navy for a neutral/mechanism box).
- `font-family="-apple-system,Helvetica,Arial,sans-serif"` — no serif,
  no decorative fonts.
- Simple labeled boxes, arrows, and short text — never dense diagrams a
  reader has to study. If a figure needs more than ~10 seconds to parse,
  simplify it.
- A hero image (first figure, right after the subtitle) should distill
  the post's one headline number or claim — think "330s → 2-3s," not a
  restatement of the title in picture form. It's what shows up in link
  previews and social shares, so it should work standalone.
- Inline diagrams go right where the text introduces the thing they
  illustrate (a mechanism diagram next to the paragraph explaining the
  mechanism, a before/after timeline next to the paragraph with the
  numbers) — not bunched at the end.

## In the local Markdown file

Reference each image with a normal Markdown image tag and a relative
path into `drafts/images/`:

```markdown
![One runner warms up, a checkpoint freezes it, every pod restores already warm](images/fig1-mechanism.png)
```

The caption text (the alt text) should describe what the image shows, not
just restate "diagram" — it's what screen readers and link unfurls use.
