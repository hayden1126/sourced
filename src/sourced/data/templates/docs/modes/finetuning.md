# [finetuning mode]

## Overview

Finetuning produces a **bounded range of alternatives** for a targeted local substitution so {{USER}} chooses before anything is committed. The failure mode this mode exists to prevent is **silent substitution** — applying one option without showing alternatives when {{USER}}'s message asked for a range. Inside finetuning, a single-option substitution is never a "small call" regardless of scope; all substitutions are gated on explicit selection.

## When to Use

**Enter when:**
- **Explicit trigger.** {{USER}} names the mode: `[finetune: title]`, `[finetune paragraph 3 sentence 2]`, `[finetune this word]`, or phrases like "finetune this", "give me alternatives for X".
- **Implicit 3-part trigger (all three required).** {{USER}}'s message satisfies:
  - (a) names a specific phrase, word, sentence, or short span in the draft (up to one paragraph), AND
  - (b) expresses negative evaluation — including but not limited to: "feels wrong," "is off," "not quite," "doesn't work," "something's off about," "not sure about," "can you try," question-framed dissatisfaction ("could this be stronger?" "is this the right word?"), hedged negatives ("maybe X isn't quite right"), AND
  - (c) does NOT ask for a specific named change (imperative "change X to Y"). A *tentative* candidate ("this feels stiff — maybe `argue`?") is an input to the alternatives set, not a directive; announce entry and produce alternatives with the candidate as one of them.
- Announce entry if any of (a), (b), ¬(c) is arguable. "Arguable" is deliberately low bar. False positives are cheap (one stray `Switching to [finetuning mode]` line); silent substitution is the expensive failure mode.
- Multi-span messages ("the verb in P2 and the transition in P3 both feel off") are multiple finetuning dispatches. Announce entry once, then produce one alternatives batch per span, each with its own scope clause.

**Do not enter when:**
- {{USER}} asks for a specific named change ("change `posit` to `argue`"). That's a direct edit, not finetuning. Apply per §5 small-call rules in root CLAUDE.md.
- The scope exceeds one paragraph (e.g., alternatives for a whole-section restructure). Announce entry to `[refining mode]` instead and punt — do not try to handle the overflow here.
- The request requires generating new content rather than substituting existing content ("add a transition," "write a counterargument"). That belongs in `[writing mode]` or `[refining mode]`.

## Iron Law

```
┌───────────────────────────────────────────────────┐
│  NO APPLICATION WITHOUT EXPLICIT SELECTION FIRST  │
└───────────────────────────────────────────────────┘
```

Silent acknowledgement ("hm," "ok") from {{USER}} is not approval. Neither is {{USER}}'s next message on an unrelated topic. Neither is your own judgment that one option is obviously best. If you haven't heard an explicit pick, do not apply anything. The scope-threshold test in §5 of root CLAUDE.md (small-call auto-apply rules) is **suspended inside this mode** — every substitution is gated.

## Steps

0. **Within-turn pre-flight (required on every turn whose prior user message contains evaluative language targeting draft prose).** Before emitting any substitution, rewrite, or in-context "illustration," run the 3-part trigger test against the prior user message. If it matches, stop, discard the draft response, and restart with step 1. This is the load-bearing checkpoint: the next-turn self-correction below only catches drift after it has shipped; this checkpoint prevents it from shipping in the first place.

1. **Announce entry.** First output of the turn: `Switching to [finetuning mode].` Name the scope in one clause after the announcement: "finetuning the title" / "finetuning the verb in paragraph 3 sentence 2" / "finetuning the em-dash clause in the opening".

2. **Produce 3–5 alternatives.** Each alternative declares a distinct **tradeoff axis** from:
   - **scope** — what it covers (e.g., just the verb, or the verb + subject);
   - **register** — formal/casual, academic/plain;
   - **emphasis** — what the phrase foregrounds;
   - **structure** — sentence shape, syntactic frame;
   - **rhythm** — cadence, syllable pattern;
   - **diction** — which semantic neighborhood of meaning the word lands in (near-synonym substitution with different semantic shade, e.g., "legible" vs "visible" vs "discernible").

   Each axis appears at most once per batch; if two alternatives share an axis, collapse them. An alternative without a declared axis fails the gate — re-emit the full batch before waiting for selection; do not ask for a pick on a partial batch.

   If you genuinely cannot produce 3 alternatives with distinct axes (e.g., the span is a single proper noun with no register alternatives), say so explicitly: "I can produce only N alternatives here — any more would collapse onto the same axis. Here they are." Do not silently produce fewer than 3 without the explanation; do not pad with axis-less filler.

3. **Name each alternative's tradeoff in one clause.** Format: `[letter]. "<alternative text>" — axis: <axis>. <what it gains>; <what it gives up>.`

   Example:
   > A. "show" — axis: diction. Plainer, less technical; loses the connotation of "render legible" that "reveal" carried.
   > B. "unfold" — axis: emphasis. Foregrounds process over result; reads more narrative than analytic.
   > C. "render legible" — axis: register. Keeps academic register; adds a word and some weight.

4. **Do not implement.** Wait for explicit selection. If {{USER}}'s message on the next turn is anything other than an explicit pick or a variant request, re-surface the alternatives and ask: "Which of A–C, or a variant?" **Re-surfacing means asking without applying — do not apply a provisional pick concurrently with re-surfacing. The two are mutually exclusive actions.** An "explicit pick" is the letter or the alternative text, verbatim or near-verbatim; ordinals ("the first") count; vague gestures ("the top one, I guess") require re-confirmation.

   **In-situ illustration is application.** Do not show "what B would look like in context" by rewriting the surrounding sentence. Show alternatives only as standalone substrings (the replacement text with tradeoff line). Embedding an alternative into the rewritten span is equivalent to applying it — the model has moved the prose, and the user sees a fait accompli. Forbidden.

5. **On selection, apply the chosen alternative.** On variant request ("C but with X instead of Y"), **emit the variant text and wait for an explicit "apply"** — do not treat the act of generating the variant as the confirmation. On "apply A", just apply.

6. **Announce return.** `Switching back to [<prior mode>].` Read the prior mode from the earlier mode-switch line in the conversation. If no prior mode-switch line exists in the session (e.g., finetuning fired on the first real turn after session-start default collaborative), return to `[collaborative mode]`.

## Missed-trigger self-correction

If in hindsight the prior turn's shape matched (a) + (b) + NOT (c), but no `Switching to [finetuning mode]` announcement fired — e.g., you responded with a single substitution or stayed in the prior mode — **open the next turn** with:

> `wait — that was a finetuning trigger I missed. Here are 3–5 alternatives for that span.`

Then proceed per steps 1–6 above. Parallel to §3's self-correction trigger in root CLAUDE.md: false-positive cost (one stray wait-announcement) is cheap; missed-trigger cost (silent substitution) is the failure mode this mode exists to block.

## Red Flags

If you catch yourself thinking any of the following, stop and check the trigger carefully:

- *"The change is obvious, I'll just apply it."* — No. You're already inside a trigger-matched turn. Applying skips the whole point of the mode.
- *"{{USER}} seemed vague but I know what he means."* — If the message matched the 3-part implicit trigger, produce alternatives. Your interpretation is one of them; show it alongside others.
- *"Three alternatives is overkill for this."* — The bound is 3–5, not "as many as feel needed." Fewer than 3 doesn't meet the bar.
- *"I'll produce alternatives but skip the tradeoff axes."* — Axes are what make the alternatives useful. Without them, {{USER}} is picking between strings without knowing what's different.
- *"{{USER}} didn't pick yet but also didn't reject, so let me apply the leading option."* — Silent promotion. Re-surface and ask.

## Rationalizations

Pre-empt the excuses. Each row is an excuse you might generate and the correct response.

| Excuse | Reality |
|--------|---------|
| "The change is trivial — just a verb swap." | Trivial in scope doesn't mean trivial in effect. Verb choice shifts voice, register, emphasis. Show alternatives. |
| "I already know which option is best." | Then say so in the tradeoff line ("I'd pick A because...") — but still show B, C, D. Your judgment is a data point, not the decision. |
| "{{USER}} is busy and wants a fast answer." | A fast answer is an unwanted rewrite that {{USER}} has to undo. The alternatives batch is the fast answer. |
| "Announcing the mode switch feels performative." | Announcing is a control point. {{USER}} uses it to sanity-check what you're doing. Skipping it is not economy; it's opacity. |
| "The scope is a single word — surely just pick one." | Single-word scope is fully inside the finetuning range (one word to one paragraph). Pick-one is the failure mode. |
| "The implicit trigger matched but felt ambiguous. I'll play it safe and stay in the prior mode." | Safe is the wrong framing. Producing alternatives on a false-positive costs one stray announcement. Silently substituting on a true-positive costs {{USER}}'s voice choice. Announce. |
| "{{USER}}'s next message was about something unrelated — I'll assume the finetuning is dropped." | No. Re-surface the pending alternatives before you move on. {{USER}} may have just context-switched and not resolved the earlier span yet. |
| "The alternatives I generated all share a tradeoff axis — good enough." | Collapse them. Each axis appears at most once per batch; otherwise the range isn't showing distinct choices. |
| "{{USER}}'s phrase wasn't in my canonical negative-eval list, so the trigger didn't match." | The list in When-to-Use is illustrative, not exhaustive. Any negative evaluation of a named span fires the trigger — including question-framed dissatisfaction ("could this be stronger?"), hedged negatives ("maybe this isn't right"), and implicit complaints ("this isn't landing"). When in doubt, announce. |
| "The span is macro-scale ('the opening,' 'the first half') — too big for finetuning." | If the span is within one paragraph, finetune it. If it genuinely overflows the one-word-to-one-paragraph bound, **announce entry to finetuning and punt to `[refining mode]` per exit gates** — do not silently stay in the prior mode because you judged the scope too big. |
| "{{USER}} gave both an evaluation and a candidate ('this feels stiff — maybe `argue`?'). The candidate counts as a named change, so bypass finetuning." | A tentative candidate ("maybe X?") is an input to the alternatives set — show it as one of A–E with an axis, alongside others. Only an imperative named change ("change to X", "use X instead") bypasses finetuning and becomes a direct edit. |
| "{{USER}} said `[finetune: X]` but I can only see one sensible option." | Explicit trigger overrides one-option intuition. Produce 3–5 with distinct axes, or decline explicitly per step 2 ("I can produce only N here — any more would collapse onto the same axis"). Never silently substitute. |
| "The alternatives would all be near-synonyms; the tradeoff axes feel forced." | Then `diction` is the axis and the gains/gives-up lines describe semantic shade between near-synonyms. Forced-feeling axes is the shape of "I'm trying to exit the mode" — recognize it, don't act on it. |
| "I'll show B in situ as an illustration, not an application." | In-situ illustration IS application. The moment you rewrite the surrounding sentence to "show what B looks like," the prose has moved. Show alternatives as standalone substrings (replacement + axis + tradeoff), never embedded in rewritten surrounding prose. |
| "{{USER}} didn't pick yet but their next message moved to another topic, so the finetuning is implicitly accepted." | No. Moving-on-to-another-topic is not acceptance. Re-surface the pending alternatives before engaging with the new topic: "Before that — A, B, or C on the earlier span?" |
| "I ran step 0's within-turn pre-flight but the trigger was 'ambiguous,' so I stayed in the prior mode to be safe." | Ambiguous means "arguable" means announce. "Stay in prior mode to be safe" is the exact rationalization the pre-flight exists to block — inverted, the step-0 rule reads: if the 3-part test is arguable, you must announce. |

## Quick Reference

```
TRIGGER MATCH?
  Explicit:  user named the mode / said "finetune X" / used [finetune: ...]  →  YES
  Implicit:  (a) named span in draft  AND
             (b) negative evaluation  AND
             NOT (c) specific named change                                      →  YES

ANNOUNCE:    Switching to [finetuning mode]. finetuning <the thing>.

PRODUCE:     3–5 alternatives. Each with:
               - the alternative text
               - a tradeoff axis (scope / register / emphasis / structure / rhythm / diction)
               - one-clause gains/gives-up
             Each axis at most once per batch.

WAIT:        Do not apply anything until {{USER}} picks explicitly.

APPLY:       On "apply A" → apply A. On variant request → generate, confirm, apply.

RETURN:      Switching back to [<prior mode>].
```

## What this mode does NOT do

- **Audit citations, §10, or voice.** Those belong in `[editing mode]`.
- **Restructure the argument.** That belongs in `[refining mode]`.
- **Regenerate beyond the scope named.** Word-level finetuning does not rewrite the sentence.
- **Pick a single option and ship it.** That is the failure mode this mode exists to prevent.

## Exit Gates

**Allowed transitions (from finetuning):**
- → `[<prior mode>]` (whatever was active before the announcement). Use `Switching back to [<prior mode>].` This is the standard exit on successful completion.
- → `[collaborative mode]` when no prior mode-switch line exists in the session — the default starting mode. Use `Switching back to [collaborative mode].`
- → `[refining mode]` if the scope overflowed one-word-to-one-paragraph mid-dispatch (e.g., {{USER}} widens the ask from a sentence to a whole section). Announce the re-switch and punt the overflow — do not try to handle it in finetuning.
- → `[research mode]` via §3 self-correction auto-trigger (if during alternatives generation you realize an alternative would introduce a citation whose full-text access hasn't been verified). Resume finetuning after verification; use `Switching back to [finetuning mode].` when returning.

**Forbidden transitions:**
- → `[writing mode]` direct. Finetuning's output is substitutions, not new prose. If the ask grows into generation, go through `[refining mode]` first.
- → `[editing mode]` direct. Editing is a full-draft audit; finetuning is a local substitution. Use collaborative as the intermediary if an edit pass follows.
- → `[formatting mode]` direct. Unthinkable — finetuning doesn't produce a paste-ready artifact.
- → `[plan mode]` / `[outlining mode]` direct. Planning and outlining are upstream of drafting; finetuning is downstream. A transition from finetuning to planning implies the finetuning scope was wrong — punt through collaborative first.

## See also

- `CLAUDE.md §7.3` — implicit trigger definition (source of truth).
- `CLAUDE.md §7.4` — mode-to-mode gate table (this file's Exit Gates mirror that table for the finetuning transitions only).
- `CLAUDE.md §7.6` — precedence rules; §10 applies to generated prose regardless of voice, including alternatives produced in this mode.
- `CLAUDE.md §5` — decision-threshold rules and their explicit carve-out: finetuning substitutions do NOT fall under §5's small-call list; all are gated on selection.
