#!/usr/bin/env node
// Extract the currently-visible book spine-item from a browser-based reader
// (default: OverDrive Read) as text with [p. N] print-page markers inserted
// at each <a id="page-N"> anchor.
//
// Requires: Chrome launched with --remote-debugging-port=9222
// and --remote-allow-origins=* , with the book tab open and the desired
// chapter visible.
//
// Usage:
//   node overdrive.mjs                             # dump current spine to stdout
//   node overdrive.mjs -o out.txt                  # dump to file
//   node overdrive.mjs --range 5-20                # only keep Arabic pages 5..20
//   node overdrive.mjs --pages i,ii,1,5            # only keep specific pages (Roman or Arabic)
//   node overdrive.mjs --tab-pattern 'read\.overdrive\.com'   # override tab matcher
//   node overdrive.mjs --iframe-pattern '\.html($|\?)'        # override iframe matcher
//
// By default the script auto-detects the content iframe by looking for
// elements matching [id^="page-"] (the OverDrive Read page-anchor convention).
// If a book uses a different anchor convention, set --iframe-pattern to
// narrow the search to a URL regex you know identifies the content frame.

import puppeteer from 'puppeteer-core';
import { writeFileSync } from 'node:fs';

const args = process.argv.slice(2);
let outPath = null;
let range = null;
let pagesFilter = null;
let tabPatternStr = 'read\\.overdrive\\.com';
let iframePatternStr = null;
let debugPort = 9222;

function printUsage() {
  console.error('Usage: node overdrive.mjs [flags]');
  console.error('  -o, --out <path>           write output to file instead of stdout');
  console.error('  --range <start-end>        keep only Arabic pages in range (e.g. 5-20)');
  console.error('  --pages <p1,p2,...>        keep only the listed pages (Roman or Arabic)');
  console.error('  --tab-pattern <regex>      override browser tab URL matcher');
  console.error('  --iframe-pattern <regex>   override content iframe URL matcher (default: auto-detect)');
  console.error('  --port <n>                 Chrome remote debugging port (default: 9222)');
}

function requireValue(flag, i) {
  if (i + 1 >= args.length || args[i + 1].startsWith('--')) {
    console.error(`Error: ${flag} requires a value.`);
    switch (flag) {
      case '--range':
        console.error('  example: --range 5-20');
        break;
      case '--pages':
        console.error('  example: --pages i,ii,1,5');
        break;
      case '--port':
        console.error('  example: --port 9222');
        break;
      case '--tab-pattern':
        console.error('  example: --tab-pattern \'read\\.overdrive\\.com\'');
        break;
      case '--iframe-pattern':
        console.error('  example: --iframe-pattern \'\\.html($|\\?)\'');
        break;
      case '-o':
      case '--out':
        console.error('  example: -o out.txt');
        break;
    }
    printUsage();
    process.exit(1);
  }
  return args[i + 1];
}

for (let i = 0; i < args.length; i++) {
  if (args[i] === '-o' || args[i] === '--out') {
    outPath = requireValue(args[i], i);
    i++;
  } else if (args[i] === '--range') {
    const val = requireValue('--range', i);
    i++;
    const m = val.match(/^(\d+)-(\d+)$/);
    if (!m) {
      console.error('Error: --range must be like 5-20');
      printUsage();
      process.exit(1);
    }
    range = [parseInt(m[1]), parseInt(m[2])];
  } else if (args[i] === '--pages') {
    const val = requireValue('--pages', i);
    i++;
    pagesFilter = new Set(val.split(',').map(s => s.trim()));
  } else if (args[i] === '--tab-pattern') {
    tabPatternStr = requireValue('--tab-pattern', i);
    i++;
  } else if (args[i] === '--iframe-pattern') {
    iframePatternStr = requireValue('--iframe-pattern', i);
    i++;
  } else if (args[i] === '--port') {
    const val = requireValue('--port', i);
    i++;
    const portNum = /^\d+$/.test(val) ? parseInt(val, 10) : NaN;
    if (!Number.isFinite(portNum) || portNum < 1 || portNum > 65535) {
      console.error(`Error: --port must be an integer between 1 and 65535 (got '${val}').`);
      printUsage();
      process.exit(1);
    }
    debugPort = portNum;
  }
}

const tabPattern = new RegExp(tabPatternStr);
const iframePattern = iframePatternStr ? new RegExp(iframePatternStr) : null;

const browser = await puppeteer.connect({
  browserURL: `http://127.0.0.1:${debugPort}`,
  defaultViewport: null,
});

try {
  const pages = await browser.pages();
  const book = pages.find(p => tabPattern.test(p.url()));
  if (!book) {
    console.error(`No browser tab matching /${tabPatternStr}/ found.`);
    console.error('Open pages:');
    for (const p of pages) console.error(' ', p.url().slice(0, 120));
    process.exit(1);
  }

  const frames = book.frames();
  let content = null;
  let bestPageCount = 0;

  for (const f of frames) {
    if (iframePattern && !iframePattern.test(f.url())) continue;
    try {
      const pageCount = await f.evaluate(() =>
        document.querySelectorAll('[id^="page-"]').length
      );
      if (pageCount > bestPageCount) {
        bestPageCount = pageCount;
        content = f;
      }
    } catch {
      // cross-origin or detached frame; skip
    }
  }

  if (!content) {
    console.error('No content frame with [id^="page-"] anchors found.');
    console.error('Frames present:');
    for (const f of frames) console.error(' ', f.url().slice(0, 120));
    console.error('If the reader uses a different anchor convention, open');
    console.error('the content iframe in devtools, find the page-anchor');
    console.error('selector, and adjust this script accordingly.');
    process.exit(2);
  }

  const { spineUrl, text } = await content.evaluate(() => {
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT,
    );
    const parts = [];
    let n;
    while ((n = walker.nextNode())) {
      if (n.nodeType === 1) {
        const m = n.id?.match(/^page-([ivxlcdm0-9]+)$/i);
        if (m) parts.push(`\n\n[p. ${m[1]}]\n`);
      } else if (n.nodeType === 3) {
        const t = n.textContent;
        if (t && t.trim()) parts.push(t);
      }
    }
    return {
      spineUrl: location.href,
      text: parts.join('').replace(/[ \t]+\n/g, '\n').replace(/\n{3,}/g, '\n\n').trim(),
    };
  });

  let output = text;

  if (range || pagesFilter) {
    const chunks = output.split(/(?=\n\n\[p\. [^\]]+\]\n)/);
    const keep = chunks.filter((chunk, i) => {
      if (i === 0 && !/^\n*\[p\. /.test(chunk)) return false;
      const m = chunk.match(/^\n*\[p\. ([^\]]+)\]/);
      if (!m) return false;
      const page = m[1];
      if (pagesFilter) return pagesFilter.has(page);
      if (range) {
        const n = parseInt(page);
        if (Number.isNaN(n)) return false;
        return n >= range[0] && n <= range[1];
      }
      return true;
    });
    output = keep.join('').trim();
  }

  const header = `# Browser-reader extract\n# Spine URL: ${spineUrl}\n# Extracted: ${new Date().toISOString()}\n\n`;
  const final = header + output + '\n';

  if (outPath) {
    writeFileSync(outPath, final);
    console.error(`Wrote ${final.length} chars to ${outPath}`);
  } else {
    process.stdout.write(final);
  }
} finally {
  await browser.disconnect();
}
