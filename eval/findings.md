---
type: Research
title: Eval findings
description: What the eval has shown so far. On Sonnet 5.5 the OS made no accuracy difference, at 15 or 60 notes or after 10 edits. It did keep the files themselves current, at about twice the cost per edit.
status: draft
generated: { by: claude-code/opus-5, at: 2026-10-20T19:34:21-07:00 }
---

# Eval findings

**So far, the structure hasn't earned its place on accuracy.** On Sonnet 5.5, loose notes, loose notes plus rules, and the full OS all passed every trap, at both 15 and 60 notes. The OS used more tokens to get there. These are pilot results, one run per trap per version, so they show the shape and can't settle small differences.

## Runs so far

All on Sonnet 5.5, 2026-10-20, Claude Code 2.1.281.

| Set | Notes | Runs | Result |
|---|---|---|---|
| s15 | 15 loose, 14 in the OS | 18 trap runs | All versions pass t1, t2, t4, t6. t3 and t5 split, but both splits traced to test flaws, not to the notes. See below. |
| s60 | 60 loose, 40 in the OS | 21 trap runs | All three versions pass all 7 traps. |

## What looked like differences, and wasn't

- **s15 t3, insurance source.** Only the OS passed at first. The loose answers did name the renewal letter. The grader failed them because the blinding step had replaced the file name with "[a note]," and the rubric asked for the letter by name. Fixed in both the blinding and the rubric before the s60 round.
- **s15 t5, main contact.** Only the rules version passed. The trap was weak: "Lee is running the project on their side" doesn't contradict "main contact: Dana," and the failing answers read it sensibly. The s60 version has two notes that each say "main contact" with different names, and every version caught it.
- **s60 t7, November bills.** The loose and OS versions failed at first for including the monthly Figma and Webflow charges. Those do recur in November, so the rubric was wrong, not the answers. Fixed and regraded. All three pass.

Every one of these was a flaw in the test, and each one, uncorrected, would have made the OS look better than it is.

## Context

From the s60 pilot, medians per run across the 7 traps:

| Version | Peak context above floor | Total input tokens | Files opened | Model calls |
|---|---|---|---|---|
| Loose | 2,689 | 41,314 | 4 | 3 |
| Loose plus rules | 2,845 | 41,339 | 4 | 3 |
| OS | 3,298 | 57,230 | 3 | 4 |

**The OS opens fewer files on simple lookups and spends more getting there.** For the deadline and insurance questions it opened 1 file, against 3 to 4 for the loose version, because the listings pointed straight at the right note. But following listings costs extra model calls, and every call re-reads the context. So total input was higher, by about 16,000 tokens per run at the median. At 60 notes, searching the loose folder is cheap enough that the listings don't pay for themselves.

## After 10 edits

One history per version, on the 60-note set, Sonnet 5.5, 2026-10-20. Ten updates were applied in order, each in its own session, then 9 questions were asked in fresh sessions.

**Every version answered all 9 questions correctly.** That includes the questions aimed at facts the loose notes repeat in more than one place.

**The files themselves came out very differently.** Here's the to-do list after all 10 edits:

| Version | Client A quote | Insurance | Client A launch |
|---|---|---|---|
| Loose | $4,200, current | Still says renew it, though it's paid | 2027-01-23, current |
| Loose plus rules | **$4,000, stale** | **Still says renew it** | **12/5, two moves out of date** |
| OS | $4,200, current | Removed | 2027-01-23, current |

The capacity note shows the same pattern. The rules version still says the studio is booked until December 5. The other two are current.

**So Sonnet got the answers right by reconstructing them at read time.** It read the dated notes, worked out which was newest, and ignored the stale lines. The OS did that work at write time instead. Across the 10 edits, it made 49 changes to existing files, against 11 for the loose version and 8 for the loose plus rules version.

**That upkeep roughly doubled the cost of editing.** The 10 edits cost $1.43 in the OS against $0.61 for loose notes, at list price. Answering questions afterward cost about the same in all three.

**What this means:**
- **The OS doesn't make a strong model answer better.** It makes the files true. That matters to anyone who reads one file without reconstructing the history: a person opening the to-do list, a weaker model, or a quick lookup.
- **Reconstructing at read time gets more expensive as notes get longer.** At 12 words a note, it's nearly free. At the lengths in the vault this came from, it may not be. That's the next test, and the long-note set exists for it.
- **The rules on their own kept files the worst.** One run can't say why. One guess: "don't invent anything" pushes the agent toward adding new lines instead of correcting old ones. It's worth watching in more runs, because it cuts against shipping the rules without the structure.
- **One history per version.** Treat all of this as the shape of the result, not a measurement.

**Grading note:** Haiku graded these 27 answers. It failed one that should have passed: the loose version's to-do answer listed sending the $4,200 quote as open, which is correct, and Haiku read it as the $4,000 quote. Sonnet regraded it as a pass, and the overruled grade is kept in the result file. Every other Haiku grade was spot-checked against its answer and holds.

## What this means for the template

- **Don't claim the structure makes answers more accurate.** At these sizes, on this model, it doesn't.
- **The README's "why bother" section needs rewriting.** It says an agent treats a repeated guess as fact. In this test, it didn't, even in loose notes, as long as the note said the client would think about it.
- **What's left untested is where any real benefit would be:**
  - **Upkeep over time.** Tested in a first pass. See "After 10 edits" above.
  - **Weaker models.** Sonnet 5.5 may be strong enough not to need the help. A smaller model might.
  - **Usefulness.** The blind side-by-side picks haven't run.

## Spend

About $6 at list price across the trap pilots and their grading, plus about $9 for the edit simulation, the padding, and their grading, counted against Joseph's plan usage rather than billed.
