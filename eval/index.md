# Eval

Tests whether organizing notes as an OS makes an agent more accurate, cheaper, or more useful than loose notes. Not part of a user's OS. Onboarding deletes it.

* [findings.md](findings.md) - What the eval has shown so far. No accuracy difference at 15 or 60 notes. At 200 long notes, loose notes passed 173 of 190 answers and the OS 188 of 190, at about twice the edit cost.
* [plan.md](plan.md) - How the eval works, what each trap tests, how results get read, and what it can't show.
* [s200-update.md](s200-update.md) - Three changes to the 200-note round before its full run, and how the round went, window by window.
* [tasks.json](tasks.json) and [tasks-60.json](tasks-60.json) - The questions and the pass and fail rubric for each, for the 15-note and 60-note sets.
* [edits.json](edits.json) and [accuracy.json](accuracy.json) - The 10 edits and their questions, and the key for the 60-note accuracy round.
* [s200.json](s200.json) - The 200-note round: 20 edits, the questions and sessions, the facts at each checkpoint, and history 1's old key.
* [aos_eval.py](aos_eval.py) - Runs, grades, builds the blind pairs, and writes the report.
* [pad_notes.py](pad_notes.py) - Pads each note to about 1,300 words of fact-free working-note text, from `padding/`.
* [s200_notes.py](s200_notes.py) and [build_s200.py](build_s200.py) - The 140 extra notes, and the builder for the 200-note set. Its `check-sources` command checks the raw sources.
* [s200_run.py](s200_run.py) - Runs, grades and reports the 200-note round, and test 2 of round four.
* [s200_check.py](s200_check.py) - Round four, test 1: the health check that starts from what changed.
* [s200_haiku.py](s200_haiku.py) - Round four, test 3: Haiku answering against the saved checkpoint folders.
* [fixtures/](fixtures/) and [fixtures-60/](fixtures-60/) - The same made-up notes, written three ways, at 15 and 60 notes. The empty folder for the floor is in `fixtures/`.
* [fixtures-60-long/](fixtures-60-long/) and [fixtures-200-long/](fixtures-200-long/) - The long-note sets, at 60 and 200 notes. Don't rebuild them. See plan.md.
* [padding/](padding/) and [padding-200/](padding-200/) - The working-note text the padding draws on.
* [s200-sources/](s200-sources/) - The five raw sources pasted in as edits, with the request versions history 1 used in `v1/`.
* [s200-extras/](s200-extras/) - The working guide and writing guide that load every session in the heavy OS, about 8,500 tokens with `CLAUDE.md`.
* [s200-variants/](s200-variants/) - Version F's rules files, for round four's test 2.
* `results/` - Created by the runners. Raw runs aren't committed. Reports, review files and grade copies are.
