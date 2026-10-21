# Eval

Tests whether organizing notes as an OS makes an agent more accurate, cheaper, or more useful than loose notes. Not part of a user's OS. Onboarding deletes it.

* [plan.md](plan.md) - How the eval works, what each trap tests, how results get read, and what it can't show.
* [tasks.json](tasks.json) - The questions and the pass and fail rubric for each.
* [aos_eval.py](aos_eval.py) - Runs, grades, builds the blind pairs, and writes the report.
* [fixtures/](fixtures/) - The same made-up notes, written three ways, plus an empty folder for the floor.
* `results/` - Created by the runner. Raw runs aren't committed.
