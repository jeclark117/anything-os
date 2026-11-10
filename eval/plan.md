---
type: Reference
title: Eval plan
description: How the anything-os eval works, what each trap tests, how results get read, and what it can't show.
status: draft
generated: { by: claude-code/opus-5, at: 2026-11-09T18:04:28-08:00 }
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

## Round three: 200 notes, cost over time

Written 2026-10-21, before any run. Settings in [s200.json](s200.json), changes and their reasons in [s200-update.md](s200-update.md).

**The question.** Writing to the OS costs more. Reading it may cost less. Which one is cheaper over time, given that a person reads far more often than they write? And do the files stay true?

**The set (`s200long`).** The 60 long notes plus 140 more, written in [s200_notes.py](s200_notes.py) and padded the same way, about 1,300 words a note. Built by [build_s200.py](build_s200.py). Three versions:

| Version | What it is |
|---|---|
| **a-loose** | 200 loose notes, no instruction file. |
| **d-os-conventions** | The OS plus `conventions.md`, the way onboarding leaves it. |
| **e-os-heavy** | The same OS with about 8,500 tokens of instructions that load every session, matched to the owner's own 200-file work OS. |

The rules-only version is dropped. It answered a question this round doesn't ask.

**Six of the new notes repeat a tracked fact in the loose version and link to the source in the OS version.** People repeat facts in loose notes, and the OS rules say to link instead. That favors the OS by design, like t1 and t2. The six are listed in `PLANTED` in `s200_notes.py`.

**The run.** Each history applies 20 edits in order. Edits 1 to 10 are the 60-note round's. Five of the last ten, edits 12, 14, 15, 16 and 17, arrive as a pasted email or set of notes, 300 to 600 words, stating one changed fact once, in words the notes don't use for it. `build_s200.py check-sources` enforces that. At checkpoints 0, 5, 10, 15 and 20, the same questions get asked in fresh read-only sessions: 3 lookups and 3 open-ended tasks, in sessions of 1, 3 and 6 questions, plus u7, which spans every client, on its own. After the checkpoint 10 questions, each history saves a Q1 2027 plan in a write session, and later edits change what's in it. Three histories per version, plus one OS history that skips the saved plan, as a pilot control.

**Measures.**
- **Cost per edit,** split into one-line edits and raw sources.
- **Cost per question, by session size.** Session size matters because the startup load is paid once per session.
- **Total cost over time,** worked out afterward for 1, 5, 10, 20 and 50 questions per edit, so the owner can read off their own rate rather than us picking one.
- **Accuracy,** graded against the facts as they stand at each checkpoint.
- **Stale files.** After the last edit, 22 undated notes a person would open, plus whatever the saved plan wrote, are checked for superseded values stated as current. In the OS, five listings get checked too, because a listing can go stale.

**Predictions:**
- **Checkpoints 0 to 10:** every version passes, as in the 60-note rounds. If they don't, the 200 notes are doing something on their own, which matters more than anything below.
- **Checkpoints 15 and 20:** this is where the versions should split, if they ever do. If loose notes stay accurate on the raw-source facts, the case for the OS doesn't rest on accuracy for a strong model at this size. The README should say that plainly.
- **u7** costs the loose version more as the round goes on, and costs the OS about the same.
- **The saved plan:** the outcome nobody can predict. A stale plan that later answers repeat would be the strongest argument for the write-time rule so far. It would also be an argument against saving answers without one.
- **Cost:** the OS costs more per edit, as before. Whether reading makes that back depends on questions per session. More questions per session should favor the OS, and the heavy OS needs more of them than the light one.

**Limits:**
- **Five sources, one author.** The banned-word rule makes them hard to search on purpose. Real email isn't always that oblique, so a split here shows the mechanism, not how often it happens.
- **The saved plan is prompted.** A real user might not ask for one.
- **Same model throughout.** Sonnet 5.5. A weaker model is still untested.
- **One grader.** Sonnet grades every checkpoint in one call. Joseph spot-checks a sample.

## Round four: three tests from Anthropic's memory work

Written 2026-11-06, before any run. Each test comes from Anthropic's agent memory study, its dreaming cookbook, or its knowledge wiki quickstart. See the "Outside evidence" section of [findings.md](findings.md). All three start after round three's window 3, and all three reuse the s200 folders and runner.

**Ran 2026-11-09, all three, in the order below. Results are in [findings.md](findings.md).** Test 2's two versions, `d2-os-conventions` and `f-os-judgment`, are copies of D with only their rules files changed, not rebuilds.

**Don't rerun `build_s200.py build`.** It copies the current `conventions.md` into `d-os-conventions`, which would no longer match the folder rounds three and four ran on. The built fixtures hold the copy they used.

### Test 1: a health check that starts from what changed

**The question.** Can a cheap check that starts from recent changes find what the full health check finds? And does the same check keep loose notes as true as the OS?

**Why.** "Check my OS" in `conventions.md` §8 reads every file, and cost about $2.40 at 40 notes on Sonnet. Anthropic's dreaming pass targets instead. Each input gets an agent that greps for the related memory files and reads only those in full, and its analyzers run on Haiku. Its recorded run cost $0.36 for 11 transcripts.

**Setup.** No new edits. Copy each folder as it stands after edit 20 in history 3. Every arm finds what changed by file modification time, against the time `edit-10.json` was written. In history 3, that's 36 OS files and 25 loose files. The plan first had the OS use `generated.at`, but in s200 history 2 the OS never updated it: 159 notes still carried the fixture date after 20 edits. Changed 2026-11-09, Joseph's call. The window includes the saved-plan session, so the saved plan counts as changed. Copy with modification times preserved, or the copy resets them.

| Arm | Folder | What the check reads | Model |
|---|---|---|---|
| Full | OS | Every file, the current §8 | Sonnet |
| Changed, Sonnet | OS | Notes changed since checkpoint 10, then every file that states one of their facts, found by search and read in full | Sonnet |
| Changed, Haiku | OS | The same | Haiku |
| Changed, loose | Loose | The same | Sonnet |

**Measures.** Stale claims fixed or flagged, out of those the `currency` step counts before the check. Wrong changes, meaning a current fact changed or a request turned into a decision. Cost, and files opened. Then the `currency` step again afterward.

**Predictions:**
- **Changed, Sonnet** finds nearly everything Full finds, for a fraction of the cost. Most stale claims sit one search away from a note that changed.
- **Changed, Haiku** finds less, and makes more wrong changes, but costs the least. Whether it's good enough is the result that matters most for the template's default.
- **Changed, loose** is the one nobody can call. If it comes close to the OS, the checking keeps files true and the structure doesn't, and the template could be much lighter.

**Rerun of the loose arm, 2026-11-09.** One run on one history took loose notes from 19 stale claims to 0, the result most able to change the README. Three more runs of `changed-loose`, same prompt: once more on history 3, to see run-to-run variance, and twice on history 2, which starts from 20 stale claims and 22 changed notes. Joseph's call, about $2.50 a run. Written while the runs were going, before any result came back. Prediction: every run clears most of what the currency check counts, and at least one leaves more than 2, the most the OS checks left. If all three reach 2 or fewer with no wrong changes, the check is doing the work the structure was credited with, and the README and §8 should say so.

**Ran 2026-11-09.** History 3 reached 0 again. History 2 reached 4 both times, about 2 or 3 of them real. The prediction held, narrowly. See [findings.md](findings.md).

### Test 2: the OS with judgment instead of layout rules

**The question.** Do the template's layout rules help a strong model, or get in its way?

**Why.** The study found that "for stronger models, giving them freedom to judge salience was more effective than setting fixed rules in advance." Version B tested the rules without the structure, and kept the worst files. The structure without its layout rules has never been tested.

**Setup.** A new version, **f-os-judgment**: the same starting folder as `d-os-conventions`, with a different `conventions.md`.

| Kept from `conventions.md` | Dropped |
|---|---|
| §1 in full | §2 and §3, except `status` |
| §4, sources | §5 and §6: the special files, the three-file rule, the listings |
| §7 steps 4, 6 and 7 | §7 steps 1, 2, 3 and 5 |
| §8's checks for contradictions, superseded claims, and decisions nobody made | §8's checks for format and listings |

The dropped sections are replaced by one paragraph on what to keep, adapted from the fallback in the wiki quickstart's analyzer prompt: durable facts a later conversation would want to already know, decisions and the reasons behind them, what's still open, and who owns what. Nothing about where it goes or how it's laid out.

One history each of `d-os-conventions` and `f-os-judgment`, through the full 20 edits and every checkpoint.

**Measures.** Accuracy, stale files after edit 20, cost per edit, files changed per edit, and new files created. New files show whether F sprawls without the folder rules.

**Predictions:**
- **F matches D on accuracy and stale files, at a lower cost per edit.** The layout rules are bookkeeping a strong model doesn't need. That's the more likely result.
- **If F's files drift,** through stale copies, scattered new notes, or a plan that never gets updated, the structure earns its place.
- **If F beats D on accuracy,** that's the study's result reproduced here, and the strongest reason to cut.

**Cost.** D's history 1 had a median of $0.27 per one-line edit and $0.57 per raw source, so about $7 for F's 20 edits, plus its questions. That's an estimate from medians.

### Test 3: a weaker model answering

**The question.** Does the OS let a cheaper model answer as well as a stronger one?

**Why.** It's the knowledge wiki quickstart's whole case: "a small model answers within a point of a larger model that searches the raw documents with no wiki, at about 1/15 of the price per answer." The study adds that memory did almost nothing for Sonnet 4.6, 0.330 to 0.364, until its instructions were refined, when it reached 0.641. Every round here has run on Sonnet 5.5.

**Setup.** No new edits. Ask every checkpoint's questions again, with Haiku 4.5 answering, against the history 3 folders of `a-loose` and `d-os-conventions`. Same grader and key.

**Predictions:**
- **Haiku on the OS comes closer to Sonnet than Haiku on loose notes does.** Following a listing is easier than reconciling scattered dated lines. If it holds, that's a cleaner pitch than anything the Sonnet rounds produced.
- **Haiku on loose notes fails most at checkpoints 15 and 20,** on the facts that arrived as raw sources.
- **If the two Haiku versions match,** the OS doesn't carry a weaker model either, and that goes in the README.

### Order

Test 1 first. It needs no edits and is the cheapest, and its loose arm could change how test 2 reads. Test 3 next, since it needs no edits either. Test 2 last, since it's the only one that runs a new history.

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
