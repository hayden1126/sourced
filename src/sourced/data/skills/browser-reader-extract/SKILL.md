---
name: browser-reader-extract
description: Use when extracting text from a DRM'd browser-based reader (OverDrive Read, Kindle Cloud Reader, Scribd, etc.) where the user holds legitimate access (library loan, paid subscription) but the reader UI blocks normal fetches. Connects to a user-launched Chrome via remote debugging and extracts text with [p. N] page markers preserved.
---

# Browser-reader extract

Works by connecting `puppeteer-core` to a Chrome instance the user launched with `--remote-debugging-port`. The user opens the book in Chrome; this skill reads the active tab's content iframe and emits plain text with `[p. N]` markers inserted at each page anchor. That lets `academic-researcher` cite by verifiable page number.

## When to use

- User has a library loan or paid subscription that opens a book inside a browser-based reader, and `Read` / `WebFetch` can't reach the content (DRM, iframe sandboxing, session auth).
- Citation requires page-level granularity for `location` in the citation log entry (CLAUDE.md §8).
- User is willing to launch Chrome with a remote debugging port. This is user-initiated setup; the skill does not launch or automate the browser for them.

Do **not** use this to bypass paywalls the user does not legitimately hold access to. The skill assumes access is legitimate; that check is the user's, not yours. If unclear, ask before extracting.

## Currently shipped extractors

| Reader | Script | Status |
|--------|--------|--------|
| OverDrive Read | `overdrive.mjs` | Proven |
| Kindle Cloud Reader | — | Not yet written; see *Adding a new reader* |
| Scribd | — | Not yet written; see *Adding a new reader* |

The extractor script is conservative about which iframe it reads: it auto-detects the content frame by looking for `[id^="page-"]` elements (the OverDrive Read page-anchor convention). A reader that uses a different page-anchor scheme needs either a tweak to the anchor selector or a new extractor script.

## Prerequisites

- **Node 18 or newer** on the machine running the skill. The script uses ESM + top-level await.
- **Chrome / Chromium** the user can launch with debugging flags.
- **`puppeteer-core`** installed in this skill's directory. Not installed by `sourced global-install`; run `npm install` inside `~/.claude/skills/browser-reader-extract/` on first use. The model should check for `node_modules/` before running any extractor and run `npm install` there if missing.

## First-run setup

1. Launch Chrome with remote debugging. Pick a port the rest of the session will reference:

   - **Windows (native):** `chrome.exe --remote-debugging-port=9222 "--remote-allow-origins=*" --user-data-dir=C:\temp\chrome-debug`
   - **macOS:** `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222 --remote-allow-origins=* --user-data-dir=/tmp/chrome-debug`
   - **Linux:** `google-chrome --remote-debugging-port=9222 --remote-allow-origins=* --user-data-dir=/tmp/chrome-debug`

   Use a throwaway `--user-data-dir` so the debug session does not touch the user's main profile. The user logs into the library / reader account inside this throwaway profile.

2. **WSL ↔ Windows loopback.** If Chrome runs on Windows and this skill runs inside WSL, mirrored networking routes `127.0.0.1:9222` correctly. Non-mirrored setups need either `netsh interface portproxy` forwarding on the Windows side or `--remote-debugging-address=0.0.0.0` plus the Windows host IP in `--port` on the WSL side. Test with `curl http://127.0.0.1:9222/json/version` inside WSL before running an extractor.

3. In the Chrome instance, navigate to the reader, log in, open the book, and navigate to the first chapter you want to extract.

4. In this skill's directory, run `npm install` once. Subsequent runs reuse `node_modules/`.

## Running the OverDrive extractor

From the skill directory (or with `cd` into it):

```bash
node overdrive.mjs                              # dump current spine to stdout
node overdrive.mjs -o intro.txt                 # dump to file
node overdrive.mjs --range 5-20                 # keep Arabic pages 5..20
node overdrive.mjs --pages i,ii,1,5             # keep specific pages (Roman or Arabic)
node overdrive.mjs --tab-pattern 'read\.somesite\.com'  # non-OverDrive tab matcher
node overdrive.mjs --iframe-pattern '\.html$'   # narrow the content-frame search
node overdrive.mjs --port 9333                  # non-default debug port
```

Argument validation: `--port` must be an integer in 1..65535 (non-numeric or out-of-range values error immediately with a clear message). `--tab-pattern` and `--iframe-pattern` accept values starting with a single `-` so regex patterns like `-chapter` pass through; only `--`-prefixed tokens are rejected as missing values.

The script emits a header with the spine URL and UTC timestamp, then the text. Each page boundary is marked `[p. N]` on its own line. Roman-numbered front matter (i, ii, iii...) renders with the Roman numeral preserved.

**Extracting a multi-chapter sequence.** The script reads only the currently-visible spine item. For a book split across chapters, either:

- Navigate chapter-by-chapter in Chrome and run the script after each navigation (simple, slow).
- Or extend the script: click through chapter buttons programmatically. For OverDrive Read, `button[id^="seeko-chapter-"]` triggers navigation; wait for the content-iframe URL to change before extracting. That extension is left out of the default script to keep the first version predictable.

## Mapping page markers to citation locations

Each `[p. N]` token becomes a citation `location` candidate. When a source-finder or academic-researcher cites from the extract, the citation log entry (CLAUDE.md §8, `citations/schema.md`) should carry:

- `location`: the page number from the marker (`"p. 42"`, `"pp. 42-44"`, or Roman `"p. xii"`).
- `exact_quote`: verbatim text from the extract.
- `surrounding_context`: the sentences immediately before and after, taken from the extract itself. No separate fetch needed; the extract is the source of truth.
- `retrieval`: `"browser-reader-extract: <platform>, <date>"` so the provenance is visible on audit.

## Adding a new reader

New readers follow the same pattern: connect via remote debugging, find the tab, find the content iframe, walk the DOM, emit page markers.

1. Identify the tab URL pattern the user lands on when the book is open. For OverDrive it is `read.overdrive.com/?d=`. For Kindle Cloud Reader, `read.amazon.com`. For Scribd, `scribd.com/read/`.
2. Identify the content iframe. Open devtools on the book page, find the iframe whose `<body>` contains the visible text, and note its URL pattern. The default extractor auto-detects by `[id^="page-"]` anchors; if the reader does not emit such anchors, record the anchor pattern it does use.
3. Identify the page-marker selector. OverDrive Read uses `<a id="page-N">`. Kindle Cloud Reader uses `data-kcr-page` attributes on divs. Scribd uses `.page` divs with `data-pageid`.
4. Identify the chapter-navigation selector if the reader paginates by chapter (OverDrive: `button[id^="seeko-chapter-"]`). Not all readers do.
5. Copy `overdrive.mjs` to `<reader>.mjs` and adjust: tab-pattern default, content-frame auto-detection, page-marker walker, chapter-navigation code if present.
6. Add a row to the *Currently shipped extractors* table above and document any reader-specific quirks.

Platforms the model can reach normally (open web, non-DRM PDFs, plain HTML articles) do **not** need this skill. Use `Read`, `WebFetch`, or pandoc against the source file instead.

## Troubleshooting

- **`No browser tab matching /.../ found`**: the tab pattern did not match any open page. Check the URL in Chrome; pass `--tab-pattern` with a wider regex if the reader URL varies across sessions.
- **`No content frame with [id^="page-"] anchors found`**: either the reader does not use that anchor convention, or the current spine is between chapters. Navigate to a chapter with visible text and retry. If the reader uses a different anchor scheme, see *Adding a new reader*.
- **Connection refused to `127.0.0.1:9222`**: Chrome is not running with the debug flag, or (WSL) the loopback is not mirrored. See *First-run setup* step 2.
- **Extracts empty or truncated**: the reader virtualizes scrolling and only renders visible text. Scroll through the chapter before extracting so the DOM populates.

## Invariants

- This skill never modifies the source prose or the citation log directly. Extracts are raw material for `academic-researcher` to quote, paraphrase, and log per CLAUDE.md §4.
- The skill does not launch Chrome, log into accounts, or bypass access controls. Launch, login, and book-opening are user actions.
- The extractor emits text with explicit `[p. N]` markers so page-level citation stays verifiable; do not strip the markers when pasting the extract into a source file used for quoting.
