#!/usr/bin/env python3
"""Round four, test 1: a health check that starts from what changed. Stdlib only.

No new edits. Each arm copies one s200 history 3 folder as it stood after
edit 20, with modification times kept, and runs one check session on it.

  full            OS, Sonnet, "Check my OS", which reads every file (conventions.md section 8)
  changed-sonnet  OS, Sonnet, starts from the notes changed since checkpoint 10
  changed-haiku   OS, Haiku, the same
  changed-loose   loose, Sonnet, the same

A note counts as changed if it was modified after edit-10.json was written, so
the saved plan counts too. Afterward, the currency check runs on the checked
folder, and a grader reads the diff for wrong changes: a current fact changed
or removed, or something undecided written as decided.

  python3 eval/s200_check.py run          run every arm not yet run
  python3 eval/s200_check.py run --arms full,changed-haiku
  python3 eval/s200_check.py report       write results/report-s200-check.md

See plan.md, "Round four", test 1.
"""
import argparse, concurrent.futures as cf, difflib, json, os, shutil, subprocess, sys, tempfile

import aos_eval as E
import s200_run as R

E.MODELS["haiku"] = "claude-haiku-4-5-20251001"

HIST = 3
SRC = os.path.join(R.RAW, "sonnet")
OUT = os.path.join(E.RESULTS, "raw-200long-check")
CP = 20
TODAY = R.CFG["checkpoints"][str(CP)]
SINCE = R.CFG["checkpoints"]["10"]

ARMS = {
    "full": ("d", "sonnet", "full"),
    "changed-sonnet": ("d", "sonnet", "changed"),
    "changed-haiku": ("d", "haiku", "changed"),
    "changed-loose": ("a", "sonnet", "changed"),
}


def changed_notes(src_arm):
    d = os.path.join(SRC, src_arm, f"h{HIST}")
    cutoff = os.path.getmtime(os.path.join(d, "edit-10.json"))
    folder = os.path.join(d, "folder")
    out = []
    for root, _, files in os.walk(folder):
        for fn in files:
            p = os.path.join(root, fn)
            if fn.endswith(".md") and os.path.getmtime(p) > cutoff:
                out.append(os.path.relpath(p, folder))
    return sorted(out)


def prompt_for(kind, notes):
    if kind == "full":
        return f"Today is {TODAY}. Check my OS."
    listing = "\n".join(f"- {n}" for n in notes)
    return (
        f"Today is {TODAY}. Check my notes for anything out of date, starting from what changed. "
        f"These notes changed since {SINCE}:\n\n{listing}\n\n"
        "For each one, work out which facts it records. Search the folder for other notes that state the same facts, "
        "and read those in full. Where another note still states an older value as current, fix it if a newer, dated "
        "note clearly settles it, and flag it in the note if not. Don't read notes that share no fact with a changed one. "
        "Then tell me in a few lines what you fixed and what needs me."
    )


def run_session(prompt, model, cwd):
    # The runner's sessions time out at 15 minutes. A full check of 200 long notes may not fit.
    cmd = E.isolated_cmd(prompt, E.MODELS[model], R.WRITE_TOOLS, "stream-json")
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=3600, stdin=subprocess.DEVNULL)
    rec = E.parse_stream(p.stdout.splitlines())
    rec.update({"exit_code": p.returncode, "stderr_tail": p.stderr[-2000:]})
    return rec, p.stdout


def read_tree(folder):
    out = {}
    for root, _, files in os.walk(folder):
        for fn in files:
            if fn.endswith(".md"):
                p = os.path.join(root, fn)
                out[os.path.relpath(p, folder)] = open(p, errors="ignore").read()
    return out


def currency(src_arm, folder):
    idx = 0 if src_arm == "a" else 1
    names = [p[idx] for p in R.CFG["living_files"]["pairs"]] + ([] if idx == 0 else R.CFG["living_files"]["os_only"])
    syn = json.load(open(os.path.join(SRC, src_arm, f"h{HIST}", "synthesis.json")))
    names += [f for f in syn["files_written"] if f.endswith(".md") and f not in names]
    files = [(n, open(os.path.join(folder, n)).read()) for n in names if os.path.exists(os.path.join(folder, n))]
    res, cost = R.call_grader(R.currency_prompt(CP, files, HIST))
    return res, cost


def wrong_changes_prompt(diff):
    return (
        "You are checking a set of edits an assistant made while tidying a folder of notes. Below are the facts as "
        f"they actually stand on {TODAY}, then a diff of every file it changed.\n\n{R.facts_at(CP, HIST)}\n\n"
        "List every change that makes a note wrong: a current fact replaced with an older or invented value, a "
        "current fact removed, or something undecided written as decided. Fixing a superseded value, flagging a "
        "conflict, and tidying wording are all fine. Ignore facts not in the list above.\n\n"
        f"<diff>\n{diff}\n</diff>\n\n"
        'Reply with only a JSON array, and nothing else: [{"file": "name", "change": "short quote", "why": "one sentence"}]. '
        "An empty array means no wrong changes."
    )


def run_arm(name):
    src_arm, model, kind = ARMS[name]
    out = os.path.join(OUT, name)
    if os.path.exists(os.path.join(out, "result.json")):
        return name, "skipped"
    os.makedirs(out, exist_ok=True)
    notes = changed_notes(src_arm)
    work = os.path.join(tempfile.gettempdir(), "aos-s200-check", name)
    shutil.rmtree(work, ignore_errors=True)
    shutil.copytree(os.path.join(SRC, src_arm, f"h{HIST}", "folder"), work)  # copy2 keeps modification times
    before = read_tree(work)
    prompt = prompt_for(kind, notes)
    rec, raw = run_session(prompt, model, work)
    open(os.path.join(out, "session.jsonl"), "w").write(raw)
    after = read_tree(work)
    shutil.rmtree(os.path.join(out, "folder"), ignore_errors=True)
    shutil.copytree(work, os.path.join(out, "folder"))
    touched = sorted(n for n in set(before) | set(after) if before.get(n) != after.get(n))
    diff = "".join("".join(difflib.unified_diff(before.get(n, "").splitlines(True), after.get(n, "").splitlines(True),
                                                 f"a/{n}", f"b/{n}", n=1)) for n in touched)
    wrong, wrong_cost = R.call_grader(wrong_changes_prompt(diff)) if touched else ([], 0)
    cur, cur_cost = currency(src_arm, work)
    before_cur = json.load(open(os.path.join(SRC, src_arm, f"h{HIST}", "currency.json")))["files"]
    res = {
        "arm": name, "source": f"{src_arm}/h{HIST}", "model": E.MODELS[model], "kind": kind, "prompt": prompt,
        "changed_notes": notes, "files_touched": touched, "files_created": [n for n in touched if n not in before],
        "files_read": rec.get("files_read"), "cost_usd": rec.get("cost_usd"), "total_input": rec.get("total_input"),
        "peak_context": rec.get("peak_context"), "duration_ms": rec.get("duration_ms"), "is_error": rec.get("is_error"),
        "answer": rec.get("answer"),
        "stale_before": sum(len(f.get("stale", [])) for f in before_cur),
        "stale_after": None if cur is None else sum(len(f.get("stale", [])) for f in cur),
        "currency_after": cur, "wrong_changes": wrong, "grading_cost_usd": (wrong_cost or 0) + (cur_cost or 0),
        "at": E.now(),
    }
    json.dump(res, open(os.path.join(out, "result.json"), "w"), indent=1)
    shutil.rmtree(work, ignore_errors=True)
    n_wrong = "?" if wrong is None else len(wrong)
    return name, (f"${rec.get('cost_usd') or 0:.2f}, {len(touched)} files changed, stale {res['stale_before']} -> "
                  f"{res['stale_after']}, {n_wrong} wrong changes")


def cmd_run(a):
    names = a.arms.split(",") if a.arms else list(ARMS)
    with cf.ThreadPoolExecutor(max_workers=len(names)) as ex:
        for name, status in ex.map(run_arm, names):
            print(f"{name}: {status}", flush=True)


def cmd_report(a):
    rows = []
    for name in ARMS:
        p = os.path.join(OUT, name, "result.json")
        if os.path.exists(p):
            rows.append(json.load(open(p)))
    lines = ["# Results, round four test 1", "", f"Generated {E.now()}. History {HIST}, after edit {CP}. Counts are raw.", "",
             "| Arm | Model | Notes it started from | Files read | Files changed | Stale before | Stale after | Wrong changes | Cost |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        nw = "?" if r["wrong_changes"] is None else len(r["wrong_changes"])
        start = "every file" if r["kind"] == "full" else len(r["changed_notes"])
        lines.append(f"| {r['arm']} | {r['model']} | {start} | {r['files_read']} | {len(r['files_touched'])} | "
                     f"{r['stale_before']} | {r['stale_after']} | {nw} | ${r['cost_usd'] or 0:.2f} |")
    for r in rows:
        lines += ["", f"## {r['arm']}", "", "**Stale claims left:**", ""]
        for f in r["currency_after"] or []:
            for s in f.get("stale", []):
                lines.append(f"- {f['file']}: {s}")
        lines += ["", "**Wrong changes:**", ""]
        for w in r["wrong_changes"] or []:
            lines.append(f"- {w.get('file')}: {w.get('change')} ({w.get('why')})")
        lines += ["", "**What it told the owner:**", "", (r["answer"] or "").strip()]
    open(os.path.join(E.RESULTS, "report-s200-check.md"), "w").write("\n".join(lines) + "\n")
    print("wrote results/report-s200-check.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--arms")
    r.set_defaults(fn=cmd_run)
    sub.add_parser("report").set_defaults(fn=cmd_report)
    a = ap.parse_args()
    a.fn(a)
