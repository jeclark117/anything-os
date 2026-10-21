---
type: Research
title: Eval findings
description: What the eval has shown so far. On Sonnet 5.5, the OS structure made no accuracy difference at 15 or 60 notes, and used more tokens.
status: draft
generated: { by: claude-code/opus-5, at: 2026-10-20T18:51:07-07:00 }
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

## What this means for the template

- **Don't claim the structure makes answers more accurate.** At these sizes, on this model, it doesn't.
- **The README's "why bother" section needs rewriting.** It says an agent treats a repeated guess as fact. In this test, it didn't, even in loose notes, as long as the note said the client would think about it.
- **What's left untested is where any real benefit would be:**
  - **Upkeep over time.** Every fixture here was written cleanly and all at once. The OS's claim is that it keeps notes current as they change. Loose notes in real life go stale, and nothing here measured that.
  - **Weaker models.** Sonnet 5.5 may be strong enough not to need the help. A smaller model might.
  - **Usefulness.** The blind side-by-side picks haven't run.

## Spend

About $6 at list price across both pilots and their grading, counted against Joseph's plan usage rather than billed.
