#!/usr/bin/env python3
"""anything-os eval. Stdlib only.

Runs the same questions against three versions of the same notes and records
whether each answer passed, how much context it used, and what it cost.

  python3 eval/aos_eval.py plan                       what a full round would run
  python3 eval/aos_eval.py run traps --model sonnet --runs 5 --yes
  python3 eval/aos_eval.py run traps --model opus --runs 2 --yes
  python3 eval/aos_eval.py run useful --model sonnet --arms a,c --runs 1 --yes
  python3 eval/aos_eval.py run floor --model sonnet --runs 3 --yes
  python3 eval/aos_eval.py grade                      grade every ungraded trap run
  python3 eval/aos_eval.py pairs                      build the blind side-by-side file
  python3 eval/aos_eval.py report                     write results/report.md

Every run happens in a fresh temporary copy of a fixture, outside any vault,
with a fixed tool list, no MCP servers, no user settings, and no saved session.
Finished runs are skipped, so an interrupted round resumes where it stopped.
"""

import argparse
import concurrent.futures as cf
import json
import os
import random
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# Two sets: s15 is the first, small fixture, s60 the larger one. Each has its
# own fixtures, tasks, and raw results, so neither overwrites the other.
SETS = {
    "s15": ("fixtures", "tasks.json", "raw"),
    "s60": ("fixtures-60", "tasks-60.json", "raw-60"),
    "s60long": ("fixtures-60-long", "tasks-60.json", "raw-60long"),
}
EDITS = json.load(open(os.path.join(HERE, "edits.json")))
RESULTS = os.path.join(HERE, "results")


def use_set(name):
    global FIXTURES, RAW, TASKS, SET
    fx, tk, rw = SETS[name]
    SET = name
    FIXTURES = os.path.join(HERE, fx)
    RAW = os.path.join(RESULTS, rw)
    TASKS = json.load(open(os.path.join(HERE, tk)))


use_set("s15")
CHECKER = os.path.join(os.path.dirname(HERE), "scripts", "okf_check.py")

MODELS = {"sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}
ARMS = {"a": "a-loose", "b": "b-rules", "c": "c-os", "empty": "empty"}
# The floor is the same for every set: an empty folder.
EMPTY = os.path.join(HERE, "fixtures", "empty")
GRADER_MODEL = "claude-sonnet-5-5"
READ_TOOLS = ["Read", "Glob", "Grep"]
# Above this many runs, `run` refuses without --yes, so a typo can't spend money.
CONFIRM_ABOVE = 3


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def claude_version():
    try:
        return subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    except OSError:
        return "unknown"


def isolated_cmd(prompt, model_id, tools, fmt):
    cmd = [
        "claude", "-p", prompt,
        "--model", model_id,
        "--output-format", fmt,
        "--tools", ",".join(tools) if tools else "",
        "--strict-mcp-config",
        "--setting-sources", "project",
        "--no-session-persistence",
    ]
    if tools:
        cmd += ["--allowedTools", ",".join(tools)]
    if fmt == "stream-json":
        cmd.append("--verbose")
    return cmd


# ---------------------------------------------------------------- planning

def jobs_for(kind, arms, runs, only=None):
    if kind == "traps":
        tasks = [t for t in TASKS["traps"] if not only or t["id"] in only]
    elif kind == "useful":
        tasks = [t for t in TASKS["useful"] if not only or t["id"] in only]
    elif kind == "floor":
        tasks = [{"id": "floor", "prompt": TASKS["floor_prompt"], "raw_prompt": True}]
        arms = ["empty"]
    else:
        sys.exit(f"unknown kind {kind}")
    return [(arm, t, n) for t in tasks for arm in arms for n in range(1, runs + 1)]


def cmd_plan(_):
    rounds = [
        ("traps", "sonnet", ["a", "b", "c"], 5),
        ("useful", "sonnet", ["a", "c"], 1),
        ("floor", "sonnet", ["empty"], 3),
        ("traps", "opus", ["a", "b", "c"], 2),
        ("floor", "opus", ["empty"], 2),
    ]
    total = 0
    for kind, model, arms, runs in rounds:
        n = len(jobs_for(kind, arms, runs))
        total += n
        print(f"{kind:7} {model:7} arms={','.join(arms):7} runs={runs}  -> {n} runs")
    graded = len(jobs_for("traps", ["a", "b", "c"], 5)) + len(jobs_for("traps", ["a", "b", "c"], 2))
    print(f"\n{total} agent runs, plus {graded} grader runs on {GRADER_MODEL}.")


# ---------------------------------------------------------------- running

def out_path(model, arm, task_id, n):
    return os.path.join(RAW, model, arm, task_id, f"{n}.json")


def parse_stream(lines):
    msgs, tools, result = {}, {}, {}
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        try:
            ev = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            m = ev.get("message", {})
            mid = m.get("id") or f"anon-{len(msgs)}"
            if m.get("usage"):
                msgs[mid] = m["usage"]
            for block in m.get("content", []) or []:
                if block.get("type") == "tool_use":
                    tools[block.get("id")] = {"name": block.get("name"), "input": block.get("input", {})}
        elif ev.get("type") == "result":
            result = ev
    ctx = [u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
           + u.get("cache_creation_input_tokens", 0) for u in msgs.values()]
    reads = [t["input"].get("file_path") for t in tools.values() if t["name"] == "Read"]
    return {
        "answer": result.get("result", ""),
        "is_error": result.get("is_error", True),
        "first_context": ctx[0] if ctx else None,
        "peak_context": max(ctx) if ctx else None,
        "total_input": sum(ctx),
        "output_tokens": sum(u.get("output_tokens", 0) for u in msgs.values()),
        "model_calls": len(ctx),
        "num_turns": result.get("num_turns"),
        "files_read": len({r for r in reads if r}),
        "tool_calls": {name: sum(1 for t in tools.values() if t["name"] == name)
                       for name in sorted({t["name"] for t in tools.values()})},
        "cost_usd": result.get("total_cost_usd"),
        "duration_ms": result.get("duration_ms"),
        # What actually served the run, not what was asked for. Claude Code also
        # makes a small Haiku call of its own, which shows up here and in cost.
        "models_used": sorted((result.get("modelUsage") or {}).keys()),
    }


def dir_diff(before, after):
    p = subprocess.run(["diff", "-ruN", "-x", ".claude", before, after],
                       capture_output=True, text=True)
    return p.stdout.replace(before, "BEFORE").replace(after, "AFTER")


def run_one(kind, model, arm, task, n, version):
    path = out_path(model, arm, task["id"], n)
    if os.path.exists(path):
        return path, "skipped"
    fixture = EMPTY if arm == "empty" else os.path.join(FIXTURES, ARMS[arm])
    work = tempfile.mkdtemp(prefix="aos-eval-")
    notes = os.path.join(work, "notes")
    shutil.copytree(fixture, notes)
    prompt = task["prompt"] if task.get("raw_prompt") else TASKS["prefix"] + task["prompt"]
    tools = READ_TOOLS + task.get("tools_extra", [])
    cmd = isolated_cmd(prompt, MODELS[model], tools, "stream-json")
    try:
        p = subprocess.run(cmd, cwd=notes, capture_output=True, text=True, timeout=600, stdin=subprocess.DEVNULL)
        lines = p.stdout.splitlines()
        rec = parse_stream(lines)
        rec["diff"] = dir_diff(fixture, notes)
        if arm == "c" and task.get("tools_extra"):
            chk = subprocess.run([sys.executable, CHECKER, notes], capture_output=True, text=True)
            rec["checker_ok"] = chk.returncode == 0
            rec["checker_tail"] = "\n".join(chk.stdout.strip().splitlines()[-6:])
        rec.update({
            "kind": kind, "model": model, "model_id": MODELS[model], "arm": arm,
            "task": task["id"], "run": n, "prompt": prompt, "tools": tools,
            "exit_code": p.returncode, "stderr_tail": p.stderr[-2000:],
            "claude_version": version, "at": now(),
        })
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(rec, fh, indent=1)
        with open(path[:-5] + ".jsonl", "w") as fh:
            fh.write(p.stdout)
        return path, "ok" if not rec["is_error"] else "error"
    finally:
        shutil.rmtree(work, ignore_errors=True)


def cmd_run(a):
    arms = a.arms.split(",") if a.arms else (["a", "b", "c"] if a.kind == "traps" else ["a", "c"])
    only = set(a.only.split(",")) if a.only else None
    jobs = jobs_for(a.kind, arms, a.runs, only)
    todo = [j for j in jobs if not os.path.exists(out_path(a.model, j[0], j[1]["id"], j[2]))]
    print(f"{len(jobs)} runs planned, {len(todo)} not done yet.")
    if len(todo) > CONFIRM_ABOVE and not a.yes:
        sys.exit(f"More than {CONFIRM_ABOVE} runs. Add --yes to spend the money.")
    version = claude_version()
    cost = 0.0
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        futs = {ex.submit(run_one, a.kind, a.model, arm, t, n, version): (arm, t["id"], n)
                for arm, t, n in todo}
        for i, f in enumerate(cf.as_completed(futs), 1):
            arm, tid, n = futs[f]
            path, status = f.result()
            c = json.load(open(path)).get("cost_usd") or 0
            cost += c
            print(f"[{i}/{len(todo)}] {a.model} {arm} {tid} #{n}: {status}  ${c:.3f}  (round ${cost:.2f})")


# ---------------------------------------------------------------- edits

def edit_dir(model, arm, h):
    return os.path.join(RAW, "edits", model, arm, f"h{h}")


def run_session(prompt, model, tools, cwd):
    cmd = isolated_cmd(prompt, MODELS[model], tools, "stream-json")
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
    rec = parse_stream(p.stdout.splitlines())
    rec.update({"exit_code": p.returncode, "stderr_tail": p.stderr[-2000:]})
    return rec, p.stdout


def stale_counts(folder):
    text = ""
    for root, _, files in os.walk(folder):
        for fn in files:
            if fn.endswith(".md"):
                text += open(os.path.join(root, fn), errors="ignore").read().lower() + "\n"
    return {k: sum(text.count(m.lower()) for m in ms) for k, ms in EDITS["stale_markers"].items()}


def run_history(model, arm, h, version):
    """Apply every edit in order to one persistent copy of the folder, then ask
    every question against the result. The folder lives in the temp directory,
    outside any vault, and is snapshotted into results after each step."""
    out = edit_dir(model, arm, h)
    state_path = os.path.join(out, "state.json")
    os.makedirs(out, exist_ok=True)
    state = json.load(open(state_path)) if os.path.exists(state_path) else {"done_edits": 0}
    work = os.path.join(tempfile.gettempdir(), "aos-eval-edits", SET, model, arm, f"h{h}")
    snap = os.path.join(out, "folder")
    if state["done_edits"] == 0:
        shutil.rmtree(work, ignore_errors=True)
        shutil.copytree(os.path.join(FIXTURES, ARMS[arm]), work)
    elif not os.path.exists(work):
        shutil.copytree(snap, work)
    tools = READ_TOOLS + ["Write", "Edit"]
    for i in range(state["done_edits"], len(EDITS["edits"])):
        rec, raw = run_session(EDITS["edit_prefix"] + EDITS["edits"][i], model, tools, work)
        rec.update({"kind": "edit", "set": SET, "model": model, "arm": arm, "history": h, "step": i + 1,
                    "prompt": EDITS["edits"][i], "claude_version": version, "at": now()})
        json.dump(rec, open(os.path.join(out, f"edit-{i + 1:02}.json"), "w"), indent=1)
        open(os.path.join(out, f"edit-{i + 1:02}.jsonl"), "w").write(raw)
        shutil.rmtree(snap, ignore_errors=True)
        shutil.copytree(work, snap)
        state["done_edits"] = i + 1
        json.dump(state, open(state_path, "w"))
        print(f"  {model} {arm} h{h} edit {i + 1}: ${rec.get('cost_usd') or 0:.3f}")
    state["stale"] = stale_counts(work)
    json.dump(state, open(state_path, "w"), indent=1)
    for q in EDITS["questions"]:
        qpath = os.path.join(out, f"{q['id']}.json")
        if os.path.exists(qpath):
            continue
        ask = tempfile.mkdtemp(prefix="aos-eval-q-")
        try:
            folder = os.path.join(ask, "notes")
            shutil.copytree(work, folder)
            rec, raw = run_session(EDITS["question_prefix"] + q["prompt"], model, READ_TOOLS, folder)
        finally:
            shutil.rmtree(ask, ignore_errors=True)
        rec.update({"kind": "edit-q", "set": SET, "model": model, "arm": arm, "history": h, "task": q["id"],
                    "prompt": q["prompt"], "claude_version": version, "at": now()})
        json.dump(rec, open(qpath, "w"), indent=1)
        print(f"  {model} {arm} h{h} {q['id']}: ${rec.get('cost_usd') or 0:.3f}")
    return arm, h


def cmd_edits(a):
    arms = a.arms.split(",") if a.arms else ["a", "b", "c"]
    jobs = [(arm, h) for arm in arms for h in range(1, a.histories + 1)]
    n = len(jobs) * (len(EDITS["edits"]) + len(EDITS["questions"]))
    print(f"{len(jobs)} histories, up to {n} sessions. Finished steps are skipped.")
    if not a.yes:
        sys.exit("Add --yes to run.")
    version = claude_version()
    # Histories run in parallel. Steps inside one history can't, because each edit builds on the last.
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for arm, h in ex.map(lambda j: run_history(a.model, j[0], j[1], version), jobs):
            print(f"done: {arm} h{h}")


# ---------------------------------------------------------------- grading

def neutral_name(m):
    """Turn any note path into the same neutral form, so `admin/insurance.md`
    and `insurance.md` both read as "the insurance note"."""
    base = os.path.basename(m.group(1)).rsplit(".", 1)[0]
    return "the " + re.sub(r"[-_ ]+", " ", base).strip().lower() + " note"


BLIND = [
    (re.compile(r"\[([^\]]+)\]\([^)]*\)"), r"\1"),
    # Backticked names may contain spaces. Bare names can't, or the match
    # would swallow the words in front of them.
    (re.compile(r"`([^`\n]+\.md)`"), neutral_name),
    (re.compile(r"\b([\w./-]+\.md)\b"), neutral_name),
    (re.compile(r"\bfront ?matter\b", re.I), "header"),
    (re.compile(r"\bstatus:\s*\w+", re.I), ""),
    (re.compile(r"\b(this|your|the) OS\b"), "the notes"),
]


def blind(text):
    for rx, rep in BLIND:
        text = rx.sub(rep, text)
    return text


def grade_prompt(task, rec):
    if task.get("tools_extra"):
        body = (f"The assistant was asked to update a folder of notes. Its final message:\n\n"
                f"<message>\n{rec['answer']}\n</message>\n\nThe change it made, as a diff:\n\n"
                f"<diff>\n{rec['diff'] or '(no files changed)'}\n</diff>")
        if "checker_ok" in rec:
            body += f"\n\nThe folder's format checker {'passed' if rec['checker_ok'] else 'failed'} afterward."
    else:
        body = f"The assistant's answer:\n\n<answer>\n{blind(rec['answer'])}\n</answer>"
    return (
        "You are grading one answer from an AI assistant against a fixed rubric. "
        "Judge only against the rubric. Ignore style, length, and formatting.\n\n"
        f"The user asked: \"{task['prompt']}\"\n\n{body}\n\n"
        f"PASS if: {task['pass']}\nFAIL if: {task['fail']}\n\n"
        'Reply with only a JSON object and nothing else: {"pass": true or false, "reason": "one sentence"}'
    )


def grade_one(path, task):
    rec = json.load(open(path))
    work = tempfile.mkdtemp(prefix="aos-grade-")
    try:
        cmd = isolated_cmd(grade_prompt(task, rec), GRADER_MODEL, [], "json")
        p = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
        out = json.loads(p.stdout)
        m = re.search(r"\{.*\}", out.get("result", ""), re.S)
        g = json.loads(m.group(0)) if m else {"pass": None, "reason": "unparseable grader reply"}
        g.update({"grader": GRADER_MODEL, "blinded": not task.get("tools_extra"),
                  "cost_usd": out.get("total_cost_usd"), "at": now()})
    except Exception as e:  # keep going, record the failure
        g = {"pass": None, "reason": f"grader error: {e}", "grader": GRADER_MODEL, "at": now()}
    finally:
        shutil.rmtree(work, ignore_errors=True)
    rec["grade"] = g
    with open(path, "w") as fh:
        json.dump(rec, fh, indent=1)
    return path, g


def records_in(raw_name):
    for root, _, files in os.walk(os.path.join(RESULTS, raw_name)):
        for fn in files:
            if fn.endswith(".json"):
                p = os.path.join(root, fn)
                yield p, json.load(open(p))


def all_records():
    for root, dirs, files in os.walk(RAW):
        dirs[:] = [d for d in dirs if d != "folder"]
        for fn in files:
            if fn.endswith(".json") and fn != "state.json":
                p = os.path.join(root, fn)
                yield p, json.load(open(p))


def cmd_grade(a):
    tasks = {t["id"]: t for t in TASKS["traps"]}
    tasks.update({q["id"]: q for q in EDITS["questions"]})
    todo = [(p, tasks[r["task"]]) for p, r in all_records()
            if r.get("kind") in ("traps", "edit-q") and (a.regrade or not r.get("grade") or r["grade"].get("pass") is None)]
    print(f"{len(todo)} runs to grade.")
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for i, (p, g) in enumerate(ex.map(lambda x: grade_one(*x), todo), 1):
            print(f"[{i}/{len(todo)}] {os.path.relpath(p, RAW)}: {'PASS' if g.get('pass') else 'FAIL' if g.get('pass') is False else '??'}  {g.get('reason','')}")


# ---------------------------------------------------------------- blind pairs

def cmd_pairs(a):
    recs = {(r["arm"], r["task"]): r for _, r in all_records()
            if r.get("kind") == "useful" and r.get("model") == a.model and r.get("run") == 1}
    rng = random.SystemRandom()
    key, out = {}, ["# Blind picks", "",
                    "Each task was answered twice, from two different versions of the same notes. "
                    "For each one, write which answer you'd rather have received, 1 or 2, and one line on why. "
                    "Don't open pairs-key.json until you're done.", ""]
    for t in TASKS["useful"]:
        pair = [recs.get(("a", t["id"])), recs.get(("c", t["id"]))]
        if not all(pair):
            print(f"skipping {t['id']}: missing a run")
            continue
        order = [0, 1]
        rng.shuffle(order)
        key[t["id"]] = {"1": ["a", "c"][order[0]], "2": ["a", "c"][order[1]]}
        out += [f"## {t['id']}", "", f"> {t['prompt']}", ""]
        for label, idx in (("1", order[0]), ("2", order[1])):
            out += [f"### Answer {label}", "", blind(pair[idx]["answer"]).strip(), ""]
        out += ["**Pick (1 or 2):** ", "", "**Why:** ", "", "---", ""]
    os.makedirs(RESULTS, exist_ok=True)
    with open(os.path.join(RESULTS, f"pairs-{SET}.md"), "w") as fh:
        fh.write("\n".join(out))
    with open(os.path.join(RESULTS, f"pairs-{SET}-key.json"), "w") as fh:
        json.dump(key, fh, indent=1)
    print(f"Wrote results/pairs-{SET}.md with {len(key)} pairs. The key is in results/pairs-{SET}-key.json.")


# ---------------------------------------------------------------- report

def med(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs)) if xs else None


def cmd_report(_):
    recs = [r for _, r in all_records()]
    floor_recs = [r for _, r in records_in(SETS["s15"][2])] if SET != "s15" else recs
    floors = {}
    for model in MODELS:
        fs = [r["first_context"] for r in floor_recs if r.get("kind") == "floor" and r["model"] == model]
        floors[model] = med(fs)
    lines = [f"# Results, {SET}", "", f"Generated {now()}. Counts are raw, like 4 of 5, because the runs are too few for percentages to mean much.", ""]
    lines += ["## Floor", "", "Context Claude Code uses before reading any note, from runs in an empty folder. "
              "Context figures below are reported above this floor.", ""]
    for m, f in floors.items():
        lines.append(f"- {m}: " + (f"{f} tokens" if f is not None else "not run"))
    lines.append("")
    for model in MODELS:
        tr = [r for r in recs if r.get("kind") == "traps" and r["model"] == model]
        if not tr:
            continue
        floor = floors.get(model) or 0
        lines += [f"## Traps, {model}", "", "| Task | " + " | ".join(ARMS[x] for x in "abc") + " |",
                  "|---|" + "---|" * 3]
        for t in TASKS["traps"]:
            row = [t["id"]]
            for arm in "abc":
                rs = [r for r in tr if r["arm"] == arm and r["task"] == t["id"]]
                passed = sum(1 for r in rs if (r.get("grade") or {}).get("pass") is True)
                ungraded = sum(1 for r in rs if (r.get("grade") or {}).get("pass") is None)
                cell = f"{passed} of {len(rs)}" if rs else "-"
                if ungraded:
                    cell += f" ({ungraded} ungraded)"
                row.append(cell)
            lines.append("| " + " | ".join(row) + " |")
        lines += ["", f"### Context and cost, {model}", "",
                  "Medians per run, across all trap tasks.", "",
                  "| Version | Peak context above floor | Total input tokens | Files read | Model calls | Cost per run |",
                  "|---|---|---|---|---|---|"]
        for arm in "abc":
            rs = [r for r in tr if r["arm"] == arm]
            if not rs:
                continue
            peak = med([r["peak_context"] - floor for r in rs if r.get("peak_context") is not None])
            cost = statistics.median([r["cost_usd"] or 0 for r in rs])
            lines.append(f"| {ARMS[arm]} | {peak} | {med([r['total_input'] for r in rs])} | "
                         f"{med([r['files_read'] for r in rs])} | {med([r['model_calls'] for r in rs])} | ${cost:.3f} |")
        lines.append("")
        lines += [f"### Tokens per passing answer, {model}", "",
                  "Total input tokens across a version's trap runs, divided by its passing answers.", ""]
        for arm in "abc":
            rs = [r for r in tr if r["arm"] == arm]
            passed = sum(1 for r in rs if (r.get("grade") or {}).get("pass") is True)
            tot = sum(r["total_input"] for r in rs)
            lines.append(f"- {ARMS[arm]}: " + (f"{round(tot / passed)}" if passed else "no passing answers"))
        lines.append("")
    picks_path, key_path = os.path.join(RESULTS, f"pairs-{SET}.md"), os.path.join(RESULTS, f"pairs-{SET}-key.json")
    if os.path.exists(picks_path) and os.path.exists(key_path):
        key = json.load(open(key_path))
        text = open(picks_path).read()
        wins = {"a": 0, "c": 0}
        lines += ["## Blind picks", "", "| Task | Picked | Why |", "|---|---|---|"]
        for sec in text.split("\n## ")[1:]:
            tid = sec.split("\n", 1)[0].strip()
            m = re.search(r"\*\*Pick \(1 or 2\):\*\*\s*([12])", sec)
            why = re.search(r"\*\*Why:\*\*\s*(.*)", sec)
            if tid in key and m:
                arm = key[tid][m.group(1)]
                wins[arm] += 1
                lines.append(f"| {tid} | {ARMS[arm]} | {why.group(1).strip() if why else ''} |")
        lines += ["", f"{ARMS['c']} picked {wins['c']} times, {ARMS['a']} {wins['a']} times.", ""]
    eq = [r for r in recs if r.get("kind") == "edit-q"]
    for model in MODELS:
        mq = [r for r in eq if r["model"] == model]
        if not mq:
            continue
        lines += [f"## After 10 edits, {model}", "", "Each cell is passing histories out of histories run.", "",
                  "| Question | " + " | ".join(ARMS[x] for x in "abc") + " |", "|---|" + "---|" * 3]
        for q in EDITS["questions"]:
            row = [q["id"]]
            for arm in "abc":
                rs = [r for r in mq if r["arm"] == arm and r["task"] == q["id"]]
                passed = sum(1 for r in rs if (r.get("grade") or {}).get("pass") is True)
                row.append(f"{passed} of {len(rs)}" if rs else "-")
            lines.append("| " + " | ".join(row) + " |")
        lines += ["", "| Version | Cost of the 10 edits | Median total input per edit | Median total input per question |", "|---|---|---|---|"]
        for arm in "abc":
            ed = [r for r in recs if r.get("kind") == "edit" and r["model"] == model and r["arm"] == arm]
            qs = [r for r in mq if r["arm"] == arm]
            if ed:
                hs = max(1, len({r["history"] for r in ed}))
                lines.append(f"| {ARMS[arm]} | ${sum(r.get('cost_usd') or 0 for r in ed) / hs:.2f} per history | "
                             f"{med([r['total_input'] for r in ed])} | {med([r['total_input'] for r in qs])} |")
        lines += ["", "Mentions of superseded values left in the folder after the edits. "
                  "This counts legitimate history too, like \"moved from 2026-12-05,\" so read it as a rough signal.", ""]
        for root, _, files in os.walk(os.path.join(RAW, "edits", model)):
            if "state.json" in files:
                st_ = json.load(open(os.path.join(root, "state.json")))
                if "stale" in st_:
                    lines.append(f"- {os.path.relpath(root, os.path.join(RAW, 'edits', model))}: " +
                                 ", ".join(f"{k} {v}" for k, v in st_["stale"].items()))
        lines.append("")
    total = sum(r.get("cost_usd") or 0 for r in recs) + sum((r.get("grade") or {}).get("cost_usd") or 0 for r in recs)
    lines += ["## Spend", "", f"${total:.2f} across {len(recs)} runs and their grading.", ""]
    with open(os.path.join(RESULTS, f"report-{SET}.md"), "w") as fh:
        fh.write("\n".join(lines))
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    r = sub.add_parser("run")
    r.add_argument("kind", choices=["traps", "useful", "floor"])
    r.add_argument("--model", choices=list(MODELS), default="sonnet")
    r.add_argument("--arms", help="comma list of a,b,c")
    r.add_argument("--runs", type=int, default=1)
    r.add_argument("--only", help="comma list of task ids")
    r.add_argument("--jobs", type=int, default=4)
    r.add_argument("--yes", action="store_true")
    e = sub.add_parser("edits")
    e.add_argument("--model", choices=list(MODELS), default="sonnet")
    e.add_argument("--arms", help="comma list of a,b,c")
    e.add_argument("--histories", type=int, default=1)
    e.add_argument("--jobs", type=int, default=3)
    e.add_argument("--yes", action="store_true")
    g = sub.add_parser("grade")
    g.add_argument("--jobs", type=int, default=4)
    g.add_argument("--regrade", action="store_true")
    pr = sub.add_parser("pairs")
    pr.add_argument("--model", choices=list(MODELS), default="sonnet")
    sub.add_parser("report")
    ap.add_argument("--set", choices=list(SETS), default="s15", help="which fixture set (default s15)")
    a = ap.parse_args()
    use_set(a.set)
    {"plan": cmd_plan, "run": cmd_run, "edits": cmd_edits, "grade": cmd_grade, "pairs": cmd_pairs, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
