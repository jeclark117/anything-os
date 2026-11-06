---
type: Reference
title: s200 update, three changes before the full round
description: Changes to the 200-note round so it tests Karpathy's actual claim. Raw sources the agent has to ingest, a saved synthesis that later answers lean on, and one question that spans many clients.
status: draft
generated: { by: claude-code/opus-5, at: 2026-11-06T09:51:13-08:00 }
---

# s200 update, three changes before the full round

**Make these three changes to the 200-note round before the full run.** The smoke run can go ahead as it is. The full round waits until these are in and Joseph has read the five sources.

## Why

The accuracy round on 2026-10-21 came back 12 of 12 for loose notes, and [findings.md](findings.md) gives the likely reason: "the edits were easy to find." Every edit was one short, dated line that named its fact outright. s200 keeps that style for all 20 edits.

Search doesn't get harder with more notes. A search for "Client A" and "launch" turns up about the same few lines at 200 notes as at 60. So scaling up the note count alone will probably reproduce the last result at 3 to 4 times the cost: every version passes, the OS is cheaper to read and costs more to edit.

Karpathy's LLM Wiki pattern, which this format comes from, claims something the eval hasn't tested yet. A new source gets read once and folded into every page it touches, and good answers get saved back so later work builds on them. The three changes below test that.

## Change 1: five edits arrive as raw sources

Convert edits 12, 14, 15, 16 and 17 into pasted source material. Leave edits 1 to 11 and 18 to 20 exactly as they are. Checkpoints 0, 5 and 10 then stay comparable with the 60-note rounds, and give the round its own control. The raw sources only take effect at checkpoints 15 and 20.

**Prompt.** Raw edits use a new prefix in `s200.json`: `"Today is {date}. Using my notes in this folder, file this: "`, followed by the source. Short edits keep `edit_prefix`.

**Each source:**
- Is 300 to 600 words, in the form given below.
- States exactly one changed fact, once, somewhere in its middle third.
- Names that fact in words the notes don't already use for it. Each source has a list of banned words below. A check fails the build if any of them appears, ignoring case.
- Adds no other new fact. Every other name, date and figure it mentions already appears in the notes. Everything around the fact is small talk, logistics, or restating what the notes already say.
- Carries its own date in a header, the way a real email or call note does. That's realistic, and it helps the loose version, which keeps the test fair.

| Edit | Date | Form | The changed fact, as the key states it | Banned words |
|---|---|---|---|---|
| 12 | 2026-11-13 | Email from the accountant about year-end paperwork | Year-end prep bill, $450, due 2026-12-15 | bill, invoice, accountant's bill, year-end prep |
| 14 | 2026-11-18 | Email thread with Pat about the photo shoot | Client A goes live on 2027-02-06. In the source this reads as "let's aim to go live on February 6 instead." | launch, Client A, deadline |
| 15 | 2026-11-19 | Call notes with Client D's owner | Client D starts 2027-02-22. In the source: "they'd like us to kick off the week of February 22." | start date, Client D starts |
| 16 | 2026-11-20 | The owner's own pricing-research notes, pasted in | Rate from 2027-01-01 is $120 an hour, replacing $110 | rate, hourly, per hour |
| 17 | 2026-11-23 | Email from Client B's office | Lee is on leave until 2027-03-01, and Sam covers until then. In the source: "Sam will be your person here while Lee's away." | main contact, contact |

Banned words apply to the source text only. The source can say "Client D" in edit 15 if the call notes would naturally name them. The table bans only the phrase that would make the fact show up in a search for it.

Keep the five sources in a new `s200-sources/` folder, one `.txt` file per edit, and point to them from `s200.json` with a `source` field on the edit. Add a `check-sources` command to `build_s200.py` that enforces the word count, the banned words, and a rule that every number in a source already appears in the notes or is its changed fact.

**The `facts` list doesn't change.** The values and the steps where they change stay the same. Only how they arrive is different.

## Change 2: one saved synthesis at checkpoint 10

After the checkpoint 10 questions and before edit 11, run one session per history with write access:

> Today is 2026-11-10. Using my notes in this folder, put together my plan for January to March 2027: what's booked, when each thing starts or ends, and what's still open. Save it in my notes so I can come back to it.

Same prompt in every version. Both the loose notes and the OS already have a `q1 2027 plan` note, so most runs will probably update that one. Record which file or files each run wrote, from the session's diff, in the history's results.

**What this tests.** A saved synthesis either compounds or rots. Edits 14, 15 and 18 change Q1 2027 after it's saved. If the OS's write-time rule works, it brings the plan up to date. If it doesn't, a later answer might repeat the stale plan, since it reads as the authority. Both outcomes are worth knowing.

**What it doesn't test.** Whether the OS saves good answers on its own. `conventions.md` has no rule about saving answers today. Adding one is a template decision for Joseph and isn't part of this round.

**Measure:**
- The cost of the synthesis session, per version.
- Whether the plan file is current at checkpoint 20. Add whatever file each run wrote to that history's `living_files` check.
- Whether the u6 and u7 answers at checkpoints 15 and 20 cite the saved plan, and whether they're right.

**Optional control, if the budget allows:** one extra history of `d-os-conventions` that skips the synthesis step. With one history it's a pilot, and the report says so.

## Change 3: one question that spans many clients

Add to `questions`:

```json
{"id": "u7-starts", "kind": "open", "prompt": "Which clients have work booked to start in 2027, and when does each start?", "must": "Lists every client with work booked to start in 2027 at this checkpoint, with its current start, and no client that isn't booked. Booked starts by checkpoint: 0, none. 5, Client D on 2027-03-01. 10, Client D on 2027-03-01 and Client H in February 2027, pro bono. 15, Client D on 2027-02-22 and Client H in February 2027. 20, Client D on 2027-02-22, Client H in February 2027, and Client E's retainer restarting in February 2027 at $650 a month. Not booked at any checkpoint: Client I, which starts in 2026, Client J, Client K, and Client T, which is only a conversation. Mentioning Client A's ongoing work is fine, as long as it isn't listed as a new start."}
```

Add a session `{"id": "s1-u7", "questions": ["u7-starts"]}`. Leave the existing sessions alone.

**Before you add it, check that the key holds.** Search all 200 notes, in both formats, for anything else that books a 2027 start. If you find something, fix the key, not the notes. The answer depends on four edits (5, 9, 15 and 18), one of them a raw source. It also has three clients to leave out. Loose notes have to search more widely for this question as the folder grows, and that's the effect the round is trying to show.

## Order of work

1. Write the five sources and run `check-sources`.
2. **Show Joseph the five sources before anything else runs.** They're the part of the test most likely to be unfair to one side, in either direction.
3. Update `s200.json`: the raw prefix, the `source` fields, u7, and s1-u7. Update the `about` line to say what changed and when.
4. Add the synthesis step to `s200_run.py` at checkpoint 10, plus the per-history `living_files` addition.
5. Run the smoke run, extended to cover edit 14 and the synthesis step at checkpoint 10, on one history.
6. Write the predictions below into [plan.md](plan.md) as a new section, before the full round.
7. Run the full round.

## Predictions, written before any run

- **Checkpoints 0 to 10:** every version passes, as in the 60-note rounds. If they don't, the 200 notes are doing something on their own, which matters more than anything below.
- **Checkpoints 15 and 20:** this is where the versions should split, if they ever do. If loose notes stay accurate on the raw-source facts, the case for the OS doesn't rest on accuracy for a strong model at this size. The README should say that plainly.
- **u7** costs the loose version more as the round goes on, and costs the OS about the same.
- **The saved plan:** the outcome nobody can predict. A stale plan that later answers repeat would be the strongest argument for the write-time rule so far. It would also be an argument against saving answers without one.

## Limits

- **Five sources, one author.** The banned-word rule makes them hard to search on purpose. Real email isn't always that oblique, so a split here shows the mechanism, not how often it happens.
- **The saved plan is prompted.** A real user might not ask for one.
- **Same model throughout.** Sonnet 5.5. A weaker model is still untested.

## Status, 2026-10-21

**Done:** all three changes, the five sources (Joseph read them and called them fine), the predictions in [plan.md](plan.md), and the smoke run. The smoke run covered one history per version through edit 14, with checkpoints 0 and 10 and the saved plan. It cost $39.40 plus $0.83 for grading. Results are in `results/report-s200long.md`.

**Smoke results, one history, so shape only:**
- Light OS read cheaper than loose at every session size. With 6 questions per session, a question cost $0.08 to $0.10 against $0.15 to $0.17.
- The heavy OS cost more than loose with 1 question per session, and less with 6.
- Edits cost $0.15 loose, $0.27 light OS and $0.36 heavy OS, for one-line edits.
- Accuracy came out 38 of 38 for both OS versions and 35 of 38 for loose. One loose failure is a real stale answer at checkpoint 10: Client A launching 2026-12-05. One traces to a planted repeat, Client J. One is a grader nitpick to review.
- The saved plan: loose wrote a new `q1 2027 schedule.md` next to the old plan note. Both OS versions updated their existing plan.

**Joseph's call, 2026-10-21: the trimmed round, on plan usage, one chunk per session window.** That's 3 histories each for loose and the light OS, and 1 for the heavy OS, with no control. The smoke histories are reused as history 1, so history 1 has no checkpoint 5. Histories 2 and 3 do. The smoke run used most of a 5-hour window, so each chunk is sized about the same. The runner resumes where it stops, so a chunk that runs out of window loses nothing.

| Window | Command | About |
|---|---|---|
| 1 | `python3 eval/s200_run.py run --arms a,d,e --histories 1 --yes` | **Done 2026-10-21.** Finished history 1, edits 15 to 20. |
| 2 | `python3 eval/s200_run.py run --arms a,d --histories 2 --yes` | **Done 2026-11-06.** $44.73, no errors. |
| 3 | `python3 eval/s200_run.py run --arms a,d --histories 3 --yes` | $47 |
| 4 | `grade`, then `currency`, then `report`, then the findings write-up | $10. History 2 was graded early, see below. Move its `grades.json` files aside first for a full regrade. |

Windows 1 and 4 can share a window if there's room.

## History 1 found a flaw in the key, 2026-10-21

**Edits 14, 15 and 18 stated requests, not decisions, and the key treated them as settled.** Pat wrote "let's aim to go live on February 6 instead... Does that work on your end?" The Client D notes said "I'd check it against everything else and confirm." Edit 18 said Client E "wants to" restart. Graded against the original key, both OS versions failed most launch and Q1 answers at checkpoints 15 and 20. Reading their answers showed why. The OS held all three as open, following its own rule that only the person confirms, and added to-dos to answer Pat and Client D.

**Joseph's call, 2026-10-21: make the three decisions explicit from history 2 on.**
- Edit 14: Pat adds "You said on our call this morning that it works for you, so let's lock it in."
- Edit 15: "told them yes, that works."
- Edit 18: "We agreed it today."

The request versions are archived in `s200-sources/v1/` and in `text_v1`. All five sources still pass `check-sources`.

**History 1 stays as a pilot of how each version handles a request,** graded against `key_v1` in `s200.json`. Results:

| Version | Checkpoint 15 | Checkpoint 20 | Stale claims after edit 20 |
|---|---|---|---|
| Loose | 9 of 19 | 9 of 19 | 15 |
| OS, light | 19 of 19 | 19 of 19 | 2 |
| OS, heavy | 19 of 19 | 19 of 19 | 3 |

**Treat the loose numbers as a ceiling on the gap, not a measurement.** `key_v1` was written after the results were seen. The grader also applied it strictly. One loose answer said "set to launch on February 6, 2027, but you haven't confirmed that date with Pat yet," and it still failed for leading with the proposed date. Other loose answers do state the proposed date as settled with no caveat. The real loose count is somewhere between 9 and 19 per checkpoint, and a blind read by Joseph would settle it.

**What it shows anyway:** loose notes took a pasted request as a decision, and the OS didn't. The draft rule is the likely reason. Whether that's the right behavior when someone pastes an email and says "file this" is a template question, not something this round decides.

**Cost data from history 1 is unaffected** and counts toward the round.

## History 2, early grade, 2026-11-06

**History 2 ran on the decision wording, and the gap from history 1 closed.** Joseph asked for an early grade before window 3. Sonnet graded the 10 checkpoints for $1.40. Nobody has reviewed the grades by hand yet.

| Version | cp0 | cp5 | cp10 | cp15 | cp20 |
|---|---|---|---|---|---|
| Loose | 17 of 19 | 18 of 19 | 18 of 19 | 18 of 19 | 19 of 19 |
| OS, light | 18 of 19 | 19 of 19 | 19 of 19 | 19 of 19 | 19 of 19 |

**Six failures, of three kinds:**
- **Client J, loose, u7 at cp0, cp5 and cp10.** Loose listed J as starting in 2027, after Client A launches. J is a lead with no agreed start. It's the same planted repeat that failed in the smoke run.
- **Main contact, both versions, cp0.** Each said Dana without mentioning the note that says Lee. That's the t5 conflict, before any lint pass has marked it.
- **The saved plan went stale in loose, cp15.** This is the one the predictions said nobody could call. At checkpoint 10, loose saved a new `plan jan-mar 2027.md` next to the old `q1 2027 plan.md`, as it did in the smoke run. Edit 14 then moved Client A's launch to 2027-02-06. Loose updated other notes but not the plan, which still says January 23 after edit 20. At cp15, the u6 answer opened with "Your 'plan jan-mar 2027' note covers this" and gave January 23. At cp20 the same question passed, so the stale plan doesn't always get repeated.

**The OS updated its plan.** Its log for edit 14 lists `business/q1-2027-plan.md` among six files updated for the new launch date. The write-time rule worked on the saved synthesis in this history.

**One history, so this shows the shape only.** The stale-plan result is one answer out of 19 at one checkpoint. Window 3 shows whether it repeats.
