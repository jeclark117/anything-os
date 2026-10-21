---
type: Research
title: Eval findings
description: What the eval has shown so far. Short notes, no difference. Long notes, the OS read less and cost less, but missed a conflict a loose search caught. After 10 edits, every version answered correctly and the OS kept the most current files, at twice the edit cost.
status: draft
generated: { by: claude-code/opus-5, at: 2026-10-20T22:19:15-07:00 }
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

## Long notes

The 60-note set again, with every note padded to about 1,300 words of fact-free working-note text, so the three versions carry the same roughly 78,000 words. Each note's facts sit at the top, middle, or bottom of its padding, a third each. Sonnet 5.5, 2026-10-20. One run per trap, then 3 runs each for the two traps that split.

**This is the first set where the versions differ.**

| Trap | Loose | Loose plus rules | OS |
|---|---|---|---|
| t2, the deadline that moved twice | 2 of 3 | 3 of 3 | 3 of 3 |
| t5, two notes naming different main contacts | 3 of 3 | 3 of 3 | **1 of 3** |
| The other five traps | all pass | all pass | all pass |

**The loose version missed a buried update.** In its failing run, it said "your Oct 15 notes don't mention a further change." They do, in the middle of about 1,300 words. That's the failure the OS is supposed to prevent, and the OS didn't make it.

**The OS missed a conflict, twice, and that's a failure it caused.** Both failing runs opened one Client B note, found "Main contact: Dana," and stopped. One said outright that it hadn't opened the other Client B notes. Search in the loose versions surfaced both "main contact" lines at once. The OS's listings pointed the agent at the obvious note, and it trusted that note too much. A real OS would usually have settled the conflict when it was written, so this fixture is harsher on the OS than real use. But contradictions do end up in separate files, and when they do, this is how the OS fails.

**Context finally favors the OS.** Medians per run, across these trap runs:

| Version | Peak context above floor | Files opened | Cost per run |
|---|---|---|---|
| Loose | 9,923 | 3 | $0.157 |
| Loose plus rules | 14,862 | 5 | $0.202 |
| OS | 6,346 | 1 | $0.128 |

At about 1,300 words a note, the OS opened one file where the loose versions opened 3 to 5. Its peak context came in about a third below the loose version, and its cost about a fifth below. That's in line with the breakeven estimated from the short-note pilots, about 1,100 words a note, which is roughly the median note length in the vault this template came from.

**The rules version read the most and cost the most.** It opened a median of 5 files. A guess is that "don't invent" makes it check more before answering, at a cost.

**Grading:** Haiku graded these runs. It failed the loose version's filing run for replacing "wants to start soon" with the January 2027 start, which is the update that was asked for. Sonnet regraded it as a pass. Every other grade was checked against its answer and holds.

## Long notes, after 10 edits

The same 10 edits and 9 questions, on the long-note set. One history per version, Sonnet 5.5, 2026-10-20.

**Answers: all three versions passed every question,** except one rules-version answer that failed because of a flaw in the test, not the notes. On edit 8, the rules version refused to record "renewed the domain today" because the update was dated 2026-11-06 and the real date was 2026-10-20. It asked which date was meant instead of guessing. Every other edit, in both edit runs, changed files. So the domain stayed unpaid in that folder, and its bills answer correctly reported what the folder said. The edits are future-dated so the questions can be asked "as of" a later day. A rerun should state the date in a way that doesn't read as a contradiction.

**Files: the OS kept the most current, and none was perfect.** The to-do list after all 10 edits:

| Version | Client A quote | Insurance | Client A launch |
|---|---|---|---|
| Loose | **$4,000, stale** | **Still says renew it** | 2027-01-23, current |
| Loose plus rules | **$4,000, stale** | **Still says renew it** | **12/5, stale** |
| OS | $4,200, current | **Still says renew it** | 2027-01-23, current |

All three recorded the insurance payment in the insurance note. None removed it from the to-do list. The capacity note was current in the loose and OS versions, and still said December 5 in the rules version. The OS made 59 changes to existing files across the 10 edits, against 14 and 10.

**Cost: editing the OS costs about twice as much, and reading it afterward costs less.**

| Version | 10 edits | Median input per question afterward |
|---|---|---|
| Loose | $1.17 | 75,607 |
| Loose plus rules | $1.28 | 97,575 |
| OS | $2.56 | 56,189 |

That's the trade the OS makes, now with long notes behind it. It pays at write time to keep files true, and gets some of it back at read time, because the agent doesn't have to dig through stale versions to answer.

## Fixing the conflict weakness

The OS's one real weakness, from the long-note pilot, was trusting the first note its listing pointed to. The fix follows Karpathy's LLM-wiki pattern, which this format comes from: note contradictions when writing, and run a periodic health check that looks for "contradictions between pages" and "stale claims that newer sources have superseded." Tested on the long-note OS version, Sonnet 5.5, 2026-10-20.

**Both versions of "Check my OS" found the conflict.** One run each, reading all 40 notes, at about $2.40 a pass:
- **The template's check as it was** flagged Dana against Lee in its reply and left the notes as they were. It also caught a stale claim: the Q4 goal to finish Client A, after its launch moved into 2027.
- **With Karpathy's two items added,** it flagged the conflict and also marked it in all four notes that name a contact.

**The marked notes fixed the read-time failure.** On the folder after the second check, the main-contact trap passed 3 of 3, up from 1 of 3. Every run still opened just 1 note, at about $0.12. The marker in that note was enough.

**The template now has both items.** `conventions.md` §7 adds a step: before recording a fact, search for other notes that state it, and fix or flag any that disagree. §8's health check now lists contradictions between notes and superseded claims first. A lint pass on long notes isn't cheap, about $2.40 here, so it belongs on a schedule or on request, not on every edit.

## What this means for the template

- **Don't claim the structure makes answers more accurate.** At these sizes, on this model, it doesn't.
- **The README's "why bother" section needs rewriting.** It says an agent treats a repeated guess as fact. In this test, it didn't, even in loose notes, as long as the note said the client would think about it.
- **What's left untested is where any real benefit would be:**
  - **Upkeep over time.** Tested in a first pass. See "After 10 edits" above.
  - **Long notes.** Tested in a pilot. See "Long notes" above.
  - **Weaker models.** Sonnet 5.5 may be strong enough not to need the help. A smaller model might.
  - **Usefulness.** The blind side-by-side picks haven't run.

## Spend

About $6 at list price across the trap pilots and their grading, plus about $9 for the edit simulation, the padding, and their grading, counted against Joseph's plan usage rather than billed.
