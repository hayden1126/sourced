--[[
Pandoc Lua filter: preserve ASCII apostrophes inside italic spans for
linguistic glottal-stop notation.

Context. `[formatting mode]` invokes pandoc with `-t markdown…-smart`
for the google-docs and plain-markdown paste targets. Pandoc's smart
reader turns ASCII `'` in prose into U+2019 (`Moore's` → curly) and the
smart writer emits Str nodes with U+2019 as curly output. That is the
desired behavior for English apostrophes.

Linguistic forms in italic — `*Ma'heo'o*`, `*-'e*`, `*ma'heono*` — use
`'` as the glottal-stop character, not as an apostrophe. The smart
reader cannot distinguish the two and curls them all. This filter
reverses that inside `Emph` spans: U+2019 and U+2018 in any Str descended
from an Emph get converted back to ASCII `'`, so the writer emits them
unchanged.

Tradeoff. Any legitimate English italic that contains an apostrophe
(`*Moore's Data*`, `*The Handmaid's Tale*`) will also revert to ASCII
inside the italic. For this user's corpus (linguistics / anthropology
with italicized Cheyenne forms), the linguistic preservation wins. Users
whose italics are primarily English titles should drop the `--lua-filter`
flag from their google-docs and plain-markdown pandoc-flags lines in
style.md.

Known limitation. When a single italic span mixes glottal-stop and
English forms (e.g., a source title `*A sacred error: Cheyenne Ma'heo'o
doesn't mean "All-Father"*`), the `'` in `doesn't` also reverts to ASCII.
Workaround: pre-bake U+2019 into the citation log's `source.title` field
for mixed-language titles. See citations/schema.md §Typography.

Shipped at templates/filters/smart-quotes.lua; installed to
~/.claude/filters/smart-quotes.lua by install.sh. Invoked as a pandoc
`--lua-filter=` flag from each style.md's google-docs and plain-markdown
pandoc-flags lines. `word` and `latex` targets do not use this filter —
their writers render Quoted nodes natively.
]]

local function revert_apos(text)
  -- U+2019 (RIGHT SINGLE QUOTATION MARK) → ASCII '
  text = text:gsub('\u{2019}', "'")
  -- U+2018 (LEFT SINGLE QUOTATION MARK) → ASCII ' (appears rarely in italics)
  text = text:gsub('\u{2018}', "'")
  return text
end

function Emph(elem)
  return pandoc.walk_inline(elem, {
    Str = function(s)
      return pandoc.Str(revert_apos(s.text))
    end,
  })
end
