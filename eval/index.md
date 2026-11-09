# Eval

Tests whether organizing notes as an OS makes an agent more accurate, cheaper, or more useful than loose notes. Not part of a user's OS. Onboarding deletes it.

* [findings.md](findings.md) - What the eval has shown so far. No accuracy difference at 15 or 60 notes. At 200 long notes, loose notes passed 173 of 190 answers and the OS 188 of 190, at about twice the edit cost.
* [plan.md](plan.md) - How the eval works, what each trap tests, how results get read, and what it can't show.
* [s200-update.md](s200-update.md) - Three changes to the 200-note round before its full run: raw sources, a saved synthesis, and a question spanning many clients.
* [tasks.json](tasks.json) and [tasks-60.json](tasks-60.json) - The questions and the pass and fail rubric for each, for the 15-note and 60-note sets.
* [aos_eval.py](aos_eval.py) - Runs, grades, builds the blind pairs, and writes the report.
* [fixtures/](fixtures/) and [fixtures-60/](fixtures-60/) - The same made-up notes, written three ways, at 15 and 60 notes. The empty folder for the floor is in `fixtures/`.
* `results/` - Created by the runner. Raw runs aren't committed.
