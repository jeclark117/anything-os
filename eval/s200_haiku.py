#!/usr/bin/env python3
"""Round four, test 3: Haiku answering. Stdlib only.

No new edits. Haiku 4.5 answers every checkpoint's questions, in the same
sessions as round three, against the s200 history 3 folders of a-loose and
d-os-conventions as each checkpoint saw them. Checkpoint 0 is the built fixture.
The rest are the folder-cpNN copies history 3 kept.

Answers land in results/raw-200long/haiku/, so `s200_run.py grade` grades them
with the same grader and key as the Sonnet answers.

  python3 eval/s200_haiku.py            run every session not yet run
  python3 eval/s200_run.py grade        then grade

See plan.md, "Round four", test 3.
"""
import concurrent.futures as cf, os

import aos_eval as E
import s200_run as R

E.MODELS["haiku"] = "claude-haiku-4-5-20251001"
HIST = 3


def folder_for(arm, cp):
    if cp == 0:
        return os.path.join(R.FIXTURES, R.ARMS[arm])
    return os.path.join(R.hdir("sonnet", arm, HIST), f"folder-cp{cp:02}")


def run_arm(arm, version):
    for cp in R.CHECKPOINTS:
        R.run_checkpoint("haiku", arm, HIST, cp, folder_for(arm, cp), version)
    return arm


if __name__ == "__main__":
    version = E.claude_version()
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        for arm in ex.map(lambda a: run_arm(a, version), ["a", "d"]):
            print(f"done: {arm} h{HIST}", flush=True)
