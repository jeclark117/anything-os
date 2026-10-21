---
type: Reference
title: Eval plan
description: How the anything-os eval works, what each trap tests, how results get read, and what it can't show.
status: draft
generated: { by: claude-code/opus-5, at: 2026-10-20T22:52:40-07:00 }
---

# Eval plan

Does organizing notes as an OS make an AI agent more accurate, cheaper, or more useful than a loose folder of the same notes? This eval answers that for one small, made-up business. Nothing in it has run at scale yet.

## The three versions

All three hold the same facts about Example Co., a made-up one-person design studio.

| Version | What it is | Folder |
|---|---|---|
| **A, loose** | 15 plain notes, the way most people keep them. No instruction file. | [fixtures/a-loose/](fixtures/a-loose/) |
| **B, loose plus rules** | The same 15 notes, plus a `CLAUDE.md` with only the rules: don't invent, label guesses, cite numbers, full dates. | [fixtures/b-rules/](fixtures/b-rules/) |
| **C, the OS** | The same facts as a 14-note OS: areas, listings, status labels, sources, a log. Passes the checker. | [fixtures/c-os/](fixtures/c-os/) |

B is the one that matters most. If B scores as well as C, the rules are doing the work and the folders aren't.

## The traps

Six questions, each aimed at one way an agent goes wrong with notes. The rubric for each is in [tasks.json](tasks.json), written before any run.

| Trap | Question | What's planted | Tests |
|---|---|---|---|
| t1 Guess repeated as fact | What price did we agree with Client A? | $4,000 was floated once and repeated in 3 notes. Client A never accepted. | Writing |
| t2 Superseded fact | When is Client A's launch deadline? | 2026-11-14 at kickoff, moved to 2026-12-05 in a later note. | Writing |
| t3 Sourced number | How much is the insurance renewal, and how do you know? | $1,240, from a renewal letter. | Reading |
| t4 Missing fact | What's Client B's budget? | Nowhere in the notes. | Reading |
| t5 Conflicting notes | Who's my main contact at Client B? | One note says Dana, another says Lee. Neither is dated. | Reading |
| t6 Filing task | Client B's budget is $6,000 and they want to start January 2027. Add that. | Nothing. Tests where the agent writes and what it updates. | Upkeep |

**Writing traps favor C on purpose.** In t1 and t2, the OS version was written the way the OS rules say notes get written: the floated price is labeled "not decided," and the moved deadline was updated in place with its history. That's the claim being tested. The OS changes how notes get written, and that should make later answers better. A reader who thinks this rigs t1 and t2 should look at t3 to t5, where every version has the same information in the same state.

**t5 is left unresolved in C too.** Both contact notes stay separate and unreconciled in every version, so it tests reading, not writing.

## Runs

| Round | Model | Versions | Runs per question | Runs |
|---|---|---|---|---|
| Traps | Sonnet 5.5 | A, B, C | 5 | 90 |
| Traps | Opus 5.5 | A, B, C | 2 | 36 |
| Usefulness | Sonnet 5.5 | A, C | 1 | 10 |
| Floor | Sonnet 5.5 and Opus 5.5 | empty folder | 3 and 2 | 5 |

Each run is a fresh, headless Claude Code session in a temporary copy of the folder, outside any vault. It gets read-only tools (Read, Glob, Grep), plus Write and Edit for t6. It loads no MCP servers and no user settings, and saves no session. So nothing from anyone's own setup leaks in, and every run starts cold.

**Opus is a comparison, not a verdict.** Two runs per question is enough to see whether a stronger model gets more out of the OS. It isn't enough to prove it.

## Measures

**Accuracy.** Each trap run is graded pass or fail by a separate Sonnet 5.5 session, against the rubric. The grader sees the answer with file names, links, and format words stripped out, so it can't tell which version it's grading. t6 is the exception, because grading a filing task means reading the diff, and the diff shows the format. Its grading isn't blinded, and the report says so. Joseph spot-checks about a fifth of the grades by hand. If he disagrees with the grader often, its grades don't count.

**Context.** From each run's own usage data:
- **Peak context above floor:** how full the window got at its largest point, minus what Claude Code uses before reading any note.
- **Total input tokens:** everything the run read, summed across its model calls. This drives cost.
- **Files read and model calls:** whether it went straight to the right note or searched.

**Tokens per passing answer** combines the two. A cheap wrong answer doesn't count as a saving.

**Usefulness, measured as accuracy.** Five open-ended tasks: a status update for a client, what to work on this week, a reply to a client, where admin stands, and whether to raise rates. Each is answered from A and C. For each task, the facts a correct answer depends on are written down before the run, and a blinded grader counts the wrong or stale facts in each answer. An answer that reads well and states one wrong fact is a failed answer.

This replaced blind preference picks on 2026-10-20. In the first pick round, Joseph preferred the loose answers 4 to 1, including three that stated a stale date as current. He had no way to check the facts, so the picks measured how persuasive an answer was, not whether it was right. See [findings.md](findings.md).

## How to read it

Counts are reported raw, like 4 of 5. With this few runs, a percentage would claim more precision than the data has.

These rules were written before any results:

- **C clearly beats B on the traps:** the structure earns its place. Lead with it.
- **B roughly matches C:** the rules do the work. Lead the README with the rules, and trim the structure.
- **All three roughly match:** at this size, the claim isn't supported. Say so, and don't claim anything before testing at a larger size.
- **C costs more context than A at this size:** expected, and not a failure on its own. C's instruction file is bigger and every note has a header. The theory is that listings save context as a folder grows, so the second round tests that.

**Second round, only if B or C wins:** the same traps with about 60 notes instead of 15. That's where C should pull ahead of B if the structure matters. If it doesn't, that's the finding.

## Round two: realistic length, and upkeep

The first two pilots used notes of about 12 words each. Real notes in the vault this template came from run a median of 1,420 and 3,398 words in its two main folders. At 12 words, opening extra files costs almost nothing, so the first pilots couldn't show whether listings save context. Round two fixes that and adds the upkeep test.

**Long notes (set `s60long`).** The same 60 notes, each padded with about 1,200 words of working-note text that adds no facts. [pad_notes.py](pad_notes.py) generates the padding and rejects any of it containing a digit, a currency sign, or a name the notes don't already use. In the OS version, each note carries the same padding as the loose notes it was built from, so both versions hold the same text.

**Edits.** [edits.json](edits.json) holds 10 updates, applied in order to one persistent copy of each version, each in its own fresh session with write access. Examples: Pat confirmed a price, the launch moved again, Dana left Client B, the insurance got paid, the rate is going up. Then 9 questions get asked, each in a fresh read-only session, whose answers depend on the latest state. Several target facts that the loose notes repeat in more than one place, like the launch date in the to-do list and the capacity note. Those are where a folder goes stale.

The report also counts how many mentions of superseded values are left in each folder afterward. That count includes legitimate history, like "moved from 2026-12-05," so it's a rough signal, not a grade.

The evolving folders live in the system temp directory during a run, outside any vault. Claude Code reads instruction files from parent directories, and a folder inside the vault would pick up the vault's own.

## What it can't show

- **Whether it holds up over months.** Ten edits in an afternoon is a stand-in for months of real use, not the same thing.
- **More than one business.** One made-up studio, written by one author. Different notes might behave differently.
- **Whether an answer reads well.** Accuracy is the measure. A reader judging answers blind can't tell a confident wrong answer from a right one, so preference isn't measured.

## Cost

From a smoke run on 2026-10-20: about $0.09 per Sonnet trap run, $0.05 per grade, and $0.05 for a floor run. Opus hasn't been measured on a trap run yet. A full round should land somewhere around $20 to $30, mostly Sonnet runs and grading. That's an estimate from 3 runs, so the runner prints spend as it goes.

## Running it

```bash
python3 eval/aos_eval.py plan
python3 eval/aos_eval.py run floor  --model sonnet --runs 3 --yes
python3 eval/aos_eval.py run traps  --model sonnet --runs 5 --yes
python3 eval/aos_eval.py run floor  --model opus   --runs 2 --yes
python3 eval/aos_eval.py run traps  --model opus   --runs 2 --yes
python3 eval/aos_eval.py run useful --model sonnet --arms a,c --runs 1 --yes
python3 eval/aos_eval.py grade
python3 eval/aos_eval.py pairs
python3 eval/aos_eval.py report
```

Raw runs land in `results/raw/` and aren't committed. Finished runs are skipped, so a stopped round picks up where it left off.
