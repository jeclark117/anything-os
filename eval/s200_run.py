#!/usr/bin/env python3
"""Cost over time at 200 notes. Stdlib only.

Each history applies the 20 edits in s200.json in order, one fresh session per
edit, to one persistent copy of a version. At each checkpoint (before any edit,
then after edits 5, 10, 15 and 20) it asks the same 6 questions in sessions of
1, 3 and 6 questions, read-only, against a copy of the folder as it stands.

  python3 eval/s200_run.py run --arms a,d,e --histories 1 --upto 14 --checkpoints 0,10 --yes   the smoke run
  python3 eval/s200_run.py run --arms a,d,e --histories 3 --control --yes                     the full round

After the checkpoint 10 questions, each history saves a Q1 2027 plan in a write
session (s200.json, "synthesis"). --control adds one OS history that skips it.
Edits with a "source" field paste in a raw email or note instead of one line.
  python3 eval/s200_run.py grade         grade every ungraded checkpoint, one grader call each
  python3 eval/s200_run.py currency      check the living files after the last edit
  python3 eval/s200_run.py report        write results/report-s200long.md

Finished steps are skipped, so a stopped round resumes where it left off.
"""
import argparse, concurrent.futures as cf, json, os, re, shutil, statistics, subprocess, sys, tempfile

import aos_eval as E

HERE = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(HERE, "s200.json")))
FIXTURES = os.path.join(HERE, "fixtures-200-long")
RAW = os.path.join(E.RESULTS, "raw-200long")
ARMS = {"a": "a-loose", "d": "d-os-conventions", "e": "e-os-heavy",
        # Round four, test 2. d2 is d with the template's current conventions.md, which added section 7 step 7.
        # f is d2 with the layout rules swapped for judgment. Both are copies of d, not rebuilds. See plan.md.
        "d2": "d2-os-conventions", "f": "f-os-judgment"}
QUESTIONS = {q["id"]: q for q in CFG["questions"]}
CHECKPOINTS = sorted(int(k) for k in CFG["checkpoints"])
SUFFIX = " Keep your answer to 100 words or fewer."
GRADER = "sonnet"
WRITE_TOOLS = E.READ_TOOLS + ["Write", "Edit"]


def hdir(model, arm, h):
    return os.path.join(RAW, model, arm, f"h{h}")


# ---------------------------------------------------------------- sessions

def read_paths(lines, cwd):
    """The notes a turn opened, relative to the folder, so a report can tell
    whether an answer leaned on the saved plan."""
    out = []
    for ln in lines:
        try:
            ev = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if ev.get("type") != "assistant":
            continue
        for b in ev.get("message", {}).get("content", []) or []:
            if b.get("type") == "tool_use" and b.get("name") == "Read":
                fp = (b.get("input") or {}).get("file_path") or ""
                rel = os.path.relpath(os.path.realpath(fp), os.path.realpath(cwd)) if fp else ""
                if rel and rel not in out:
                    out.append(rel)
    return out


def failed(rec):
    a = (rec.get("answer") or "").strip()
    return rec.get("is_error") or not a or a.startswith("API Error") or bool(re.search(r"hit your (usage )?limit|rate limit", a[:200], re.I))


def edit_prompt(ed):
    """A short edit is one line. A raw source is pasted in whole, the way a
    person would paste an email or their own notes."""
    if "source" in ed:
        return CFG["raw_prefix"].format(date=ed["date"]) + "\n\n" + open(os.path.join(HERE, ed["source"])).read().strip()
    return CFG["edit_prefix"].format(date=ed["date"]) + ed["text"]


def snapshot(folder):
    hashes = {}
    for root, _, files in os.walk(folder):
        for fn in files:
            p = os.path.join(root, fn)
            hashes[os.path.relpath(p, folder)] = hash(open(p, "rb").read())
    return hashes


def run_synthesis(model, arm, h, work, version):
    """The saved Q1 2027 plan, after the checkpoint 10 questions and before edit 11."""
    syn = CFG["synthesis"]
    before = snapshot(work)
    rec, raw = E.run_session(syn["prompt"], model, WRITE_TOOLS, work)
    if failed(rec):
        raise RuntimeError(f"{arm} h{h} synthesis failed: {rec['answer'][:80]}")
    after = snapshot(work)
    rec["files_written"] = sorted(f for f in after if before.get(f) != after[f] and not f.startswith(".claude"))
    rec.update({"kind": "s200-synthesis", "model": model, "arm": arm, "history": h, "prompt": syn["prompt"],
                "claude_version": version, "at": E.now()})
    out = hdir(model, arm, h)
    json.dump(rec, open(os.path.join(out, "synthesis.json"), "w"), indent=1)
    open(os.path.join(out, "synthesis.jsonl"), "w").write(raw)
    print(f"  {arm} h{h} synthesis: ${rec.get('cost_usd') or 0:.3f}, wrote {', '.join(rec['files_written']) or 'nothing'}")
    return rec


def run_multi(prompts, model, tools, cwd):
    """One session, several user turns, each sent only after the last answer.
    Returns one record per turn plus the raw stream."""
    cmd = ["claude", "-p", "--input-format", "stream-json", "--output-format", "stream-json", "--verbose",
           "--model", E.MODELS[model], "--tools", ",".join(tools), "--allowedTools", ",".join(tools),
           "--strict-mcp-config", "--setting-sources", "project", "--no-session-persistence"]
    p = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, bufsize=1)
    turns, raw, prev_cost = [], [], 0.0
    try:
        for prompt in prompts:
            p.stdin.write(json.dumps({"type": "user", "message": {"role": "user", "content": prompt}}) + "\n")
            p.stdin.flush()
            lines = []
            for line in p.stdout:
                lines.append(line)
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("type") == "result":
                    break
            raw += lines
            rec = E.parse_stream(lines)
            cum = rec.get("cost_usd") or 0.0
            # The result event's cost is the session's running total.
            rec["session_cost_so_far"] = cum
            rec["cost_usd"] = cum - prev_cost
            prev_cost = cum
            rec["prompt"] = prompt
            rec["read_paths"] = read_paths(lines, cwd)
            turns.append(rec)
    finally:
        try:
            p.stdin.close()
        except OSError:
            pass
        try:
            p.wait(timeout=120)
        except subprocess.TimeoutExpired:
            p.kill()
    return turns, "".join(raw)


def run_checkpoint(model, arm, h, cp, folder, version):
    out = os.path.join(hdir(model, arm, h), f"cp{cp:02}")
    os.makedirs(out, exist_ok=True)
    date = CFG["checkpoints"][str(cp)]

    def one(sess):
        path = os.path.join(out, f"{sess['id']}.json")
        if os.path.exists(path):
            return sess["id"], "skipped", 0.0
        ask = tempfile.mkdtemp(prefix="aos-s200-q-")
        try:
            notes = os.path.join(ask, "notes")
            shutil.copytree(folder, notes)
            prompts = [(CFG["question_prefix"].format(date=date) if i == 0 else CFG["followup_prefix"])
                       + QUESTIONS[q]["prompt"] + SUFFIX for i, q in enumerate(sess["questions"])]
            turns, raw = run_multi(prompts, model, E.READ_TOOLS, notes)
        finally:
            shutil.rmtree(ask, ignore_errors=True)
        if len(turns) != len(sess["questions"]) or any(failed(t) for t in turns):
            # Not saved, so the next run retries it. A rate-limit reply must never get graded as an answer.
            return sess["id"], "ERROR, not saved: " + next((t["answer"][:80] for t in turns if failed(t)), "missing turns"), 0.0
        for t, q in zip(turns, sess["questions"]):
            t["question"] = q
        rec = {"kind": "s200-session", "model": model, "arm": arm, "history": h, "checkpoint": cp, "date": date,
               "session": sess["id"], "size": len(sess["questions"]), "turns": turns,
               "cost_usd": sum(t["cost_usd"] for t in turns), "claude_version": version, "at": E.now()}
        json.dump(rec, open(path, "w"), indent=1)
        open(path[:-5] + ".jsonl", "w").write(raw)
        return sess["id"], "ok", rec["cost_usd"]

    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        for sid, status, cost in ex.map(one, CFG["sessions"]):
            print(f"  {arm} h{h} cp{cp} {sid}: {status} ${cost:.3f}")


def run_history(model, arm, h, upto, cps, version, synthesis=True):
    out = hdir(model, arm, h)
    os.makedirs(out, exist_ok=True)
    state_path = os.path.join(out, "state.json")
    state = json.load(open(state_path)) if os.path.exists(state_path) else {"done_edits": 0}
    work = os.path.join(tempfile.gettempdir(), "aos-s200", model, arm, f"h{h}")
    snap = os.path.join(out, "folder")
    if state["done_edits"] == 0:
        shutil.rmtree(work, ignore_errors=True)
        shutil.copytree(os.path.join(FIXTURES, ARMS[arm]), work)
    elif not os.path.exists(work):
        shutil.copytree(snap, work)
    after = CFG["synthesis"]["after_checkpoint"]

    def maybe_synthesis():
        if synthesis and state["done_edits"] == after and not state.get("synthesis_done"):
            if after in cps:
                run_checkpoint(model, arm, h, after, work, version)
            run_synthesis(model, arm, h, work, version)
            shutil.rmtree(snap, ignore_errors=True)
            shutil.copytree(work, snap)
            state["synthesis_done"] = True
            json.dump(state, open(state_path, "w"))

    if 0 in cps:
        run_checkpoint(model, arm, h, 0, work, version)
    for i in range(state["done_edits"], upto):
        if i == after:
            maybe_synthesis()
        ed = CFG["edits"][i]
        prompt = edit_prompt(ed)
        rec, raw = E.run_session(prompt, model, WRITE_TOOLS, work)
        if failed(rec):
            # Stop this history here. The folder may be half-edited, so the rerun restores the last snapshot.
            shutil.rmtree(work, ignore_errors=True)
            print(f"  {arm} h{h} edit {i + 1}: ERROR, history stopped: {rec['answer'][:80]}")
            return arm, h
        rec.update({"kind": "s200-edit", "model": model, "arm": arm, "history": h, "step": i + 1,
                    "raw_source": "source" in ed, "prompt": prompt, "claude_version": version, "at": E.now()})
        json.dump(rec, open(os.path.join(out, f"edit-{i + 1:02}.json"), "w"), indent=1)
        open(os.path.join(out, f"edit-{i + 1:02}.jsonl"), "w").write(raw)
        shutil.rmtree(snap, ignore_errors=True)
        shutil.copytree(work, snap)
        state["done_edits"] = i + 1
        json.dump(state, open(state_path, "w"))
        print(f"  {arm} h{h} edit {i + 1}: ${rec.get('cost_usd') or 0:.3f}")
        if (i + 1) in cps:
            # Keep the folder as each checkpoint saw it, so other models can be asked the same questions later.
            cp_snap = os.path.join(out, f"folder-cp{i + 1:02}")
            shutil.rmtree(cp_snap, ignore_errors=True)
            shutil.copytree(work, cp_snap)
            run_checkpoint(model, arm, h, i + 1, work, version)
    # After a stop, the latest checkpoint can still be finished from the snapshot.
    if state["done_edits"] in cps and state["done_edits"] > 0:
        run_checkpoint(model, arm, h, state["done_edits"], work, version)
    maybe_synthesis()
    return arm, h


def cmd_run(a):
    arms = a.arms.split(",")
    cps = [int(c) for c in a.checkpoints.split(",")] if a.checkpoints else CHECKPOINTS
    jobs = [(arm, h, True) for arm in arms for h in range(1, a.histories + 1)]
    if a.control:
        # One extra OS history that skips the saved plan. A pilot, with one history.
        jobs.append(("d", "c1", False))
    sessions = sum(1 for c in cps if c <= a.upto) * len(CFG["sessions"])
    print(f"{len(jobs)} histories, {a.upto} edits and {sessions} question sessions each. Finished steps are skipped.")
    if not a.yes:
        sys.exit("Add --yes to run.")
    version = E.claude_version()
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for arm, h in ex.map(lambda j: run_history(a.model, j[0], j[1], a.upto, cps, version, j[2]), jobs):
            print(f"done: {arm} h{h}")


# ---------------------------------------------------------------- grading

# History 1 ran on the request wording only in the round three versions. Later versions run the decision wording.
V1_ARMS = ("a", "d", "e")


def key_h(arm, h):
    return h if arm in V1_ARMS else None


def v1(h):
    """History 1 ran on the request versions of edits 14, 15 and 18, so it has its own key."""
    return str(h) in CFG["key_v1"]["histories"]


def must(q, h):
    return CFG["key_v1"]["musts"].get(q, QUESTIONS[q]["must"]) if v1(h) else QUESTIONS[q]["must"]


def facts_at(cp, h=None):
    lines = []
    if h is not None and v1(h):
        lines.append(CFG["key_v1"]["about"] + "\n")
    for f in CFG["facts"]:
        values = CFG["key_v1"]["facts"].get(f["topic"], f["values"]) if h is not None and v1(h) else f["values"]
        cur = [v for n, v in values if n <= cp][-1]
        # A value the current entry still names, like the last agreed date beside a pending request, isn't superseded.
        old = [v for v in [v for n, v in values if n <= cp and v != cur] + f.get("older", []) if v not in cur]
        lines.append(f"- {f['topic']}: {cur}." + (f" Superseded: {'; '.join(old)}." if old else ""))
    return "\n".join(lines)


def grade_prompt(cp, items, h=None):
    body = "\n\n".join(f"<item id=\"{i}\">\nQuestion: {QUESTIONS[q]['prompt']}\nA correct answer: {must(q, h)}\n"
                       f"<answer>\n{E.blind(ans)}\n</answer>\n</item>" for i, (q, ans) in enumerate(items))
    return (
        "You are grading answers from an AI assistant for factual accuracy against a fixed key. "
        "Ignore style, tone, length, and formatting. An answer that reads well but states one wrong fact fails.\n\n"
        f"It is {CFG['checkpoints'][str(cp)]}. These are the facts as they stand today. A superseded value "
        "presented as current is wrong. Mentioning it as history is fine.\n\n"
        f"{facts_at(cp, h)}\n\nFacts the key doesn't cover don't count against an answer, unless they contradict the facts above.\n\n"
        f"{body}\n\n"
        'Reply with only a JSON array, one object per item, in order, and nothing else: '
        '[{"id": 0, "pass": true or false, "reason": "one sentence naming any wrong fact"}]'
    )


def call_grader(prompt):
    work = tempfile.mkdtemp(prefix="aos-grade-")
    try:
        p = subprocess.run(E.isolated_cmd(prompt, E.MODELS[GRADER], [], "json"), cwd=work, capture_output=True,
                           text=True, timeout=900, stdin=subprocess.DEVNULL)
        out = json.loads(p.stdout)
        m = re.search(r"\[.*\]", out.get("result", ""), re.S)
        return (json.loads(m.group(0)) if m else None), out.get("total_cost_usd")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def cp_dirs():
    for root, dirs, files in os.walk(RAW):
        dirs[:] = [d for d in dirs if not d.startswith("folder")]
        if os.path.basename(root).startswith("cp") and files:
            yield root


def grade_cp(d):
    paths = sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".json") and f != "grades.json")
    if os.path.exists(os.path.join(d, "grades.json")):
        return d, "skipped"
    recs = [json.load(open(p)) for p in paths]
    items, keys = [], []
    for p, r in zip(paths, recs):
        for n, t in enumerate(r["turns"]):
            items.append((t["question"], t["answer"]))
            keys.append((os.path.basename(p), n))
    cp = recs[0]["checkpoint"]
    grades, cost = call_grader(grade_prompt(cp, items, key_h(recs[0]["arm"], recs[0]["history"])))
    if not grades or len(grades) != len(items):
        return d, "grader reply didn't parse"
    out = {"grader": E.MODELS[GRADER], "cost_usd": cost, "at": E.now(),
           "items": [{"file": k[0], "turn": k[1], "question": it[0], **{x: g.get(x) for x in ("pass", "reason")}}
                     for k, it, g in zip(keys, items, grades)]}
    json.dump(out, open(os.path.join(d, "grades.json"), "w"), indent=1)
    return d, f"{sum(1 for g in grades if g.get('pass'))} of {len(grades)} pass, ${cost or 0:.3f}"


def cmd_grade(a):
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for d, status in ex.map(grade_cp, list(cp_dirs())):
            print(f"{os.path.relpath(d, RAW)}: {status}")


# ---------------------------------------------------------------- currency

def currency_prompt(cp, files, h=None):
    body = "\n\n".join(f"<file name=\"{n}\">\n{t}\n</file>" for n, t in files)
    return (
        "You are checking whether a folder of notes is up to date. Below are the notes a person would open to see "
        "where things stand, and the facts as they actually stand today.\n\n"
        f"It is {CFG['checkpoints'][str(cp)]}. The facts:\n\n{facts_at(cp, h)}\n\n"
        "For each file, list every place it states a superseded value as current. A value given as history, "
        "like \"moved from 2026-12-05,\" is fine. A to-do item for something already done counts as stale. "
        "Ignore facts not in the list above. Ignore long passages of general working notes; only the specific "
        "claims matter.\n\n"
        f"{body}\n\n"
        'Reply with only a JSON array, one object per file, in order, and nothing else: '
        '[{"file": "name", "stale": ["short quote of each stale claim"]}]'
    )


def currency_one(d):
    rec_path = os.path.join(d, "currency.json")
    if os.path.exists(rec_path):
        return d, "skipped"
    st = json.load(open(os.path.join(d, "state.json")))
    cp = st["done_edits"]
    arm = os.path.basename(os.path.dirname(d))
    folder = os.path.join(d, "folder")
    idx = 0 if arm == "a" else 1
    names = [p[idx] for p in CFG["living_files"]["pairs"]] + ([] if idx == 0 else CFG["living_files"]["os_only"])
    syn_path = os.path.join(d, "synthesis.json")
    if os.path.exists(syn_path):
        # Whatever the saved plan wrote is a living file for this history.
        names += [f for f in json.load(open(syn_path))["files_written"] if f.endswith(".md") and f not in names]
    files = [(n, open(os.path.join(folder, n)).read()) for n in names if os.path.exists(os.path.join(folder, n))]
    missing = [n for n in names if not os.path.exists(os.path.join(folder, n))]
    res, cost = call_grader(currency_prompt(cp, files, key_h(arm, os.path.basename(d)[1:])))
    if res is None:
        return d, "grader reply didn't parse"
    json.dump({"checkpoint": cp, "files": res, "missing": missing, "cost_usd": cost, "at": E.now()},
              open(rec_path, "w"), indent=1)
    return d, f"cp{cp}: {sum(len(f.get('stale', [])) for f in res)} stale claims, ${cost or 0:.3f}"


def cmd_currency(a):
    ds = [os.path.dirname(os.path.join(r, "state.json")) for r, _, fs in os.walk(RAW) if "state.json" in fs]
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for d, status in ex.map(currency_one, ds):
            print(f"{os.path.relpath(d, RAW)}: {status}")


# ---------------------------------------------------------------- report

def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def cmd_report(a):
    sessions, edits, grades = [], [], {}
    for root, dirs, files in os.walk(RAW):
        dirs[:] = [d for d in dirs if not d.startswith("folder")]
        for fn in files:
            p = os.path.join(root, fn)
            if fn == "grades.json":
                for it in json.load(open(p))["items"]:
                    grades[(root, it["file"], it["turn"])] = it["pass"]
            elif fn.endswith(".json") and fn.startswith("edit-"):
                edits.append(json.load(open(p)))
            elif fn.endswith(".json") and fn.startswith("s") and fn not in ("state.json", "synthesis.json"):
                r = json.load(open(p))
                r["_dir"], r["_file"] = root, fn
                sessions.append(r)
    arms = [x for x in ARMS if any(s["arm"] == x for s in sessions + edits)]
    L = ["# Results, s200long", "", f"Generated {E.now()}. Counts are raw.", ""]

    L += ["## Cost per edit", "", "| Version | Kind | Edits run | Median cost per edit | Median input per edit |", "|---|---|---|---|---|"]
    for x in arms:
        for kind, raw in (("one line", False), ("raw source", True)):
            es = [e for e in edits if e["arm"] == x and bool(e.get("raw_source")) == raw]
            if es:
                L.append(f"| {ARMS[x]} | {kind} | {len(es)} | ${med([e['cost_usd'] for e in es]):.3f} | {round(med([e['total_input'] for e in es]))} |")

    syns = []
    for root, _, files in os.walk(RAW):
        if "synthesis.json" in files:
            syns.append(json.load(open(os.path.join(root, "synthesis.json"))))
    if syns:
        L += ["", "## The saved plan", "", "| Version | History | Cost | Files written |", "|---|---|---|---|"]
        for r in syns:
            L.append(f"| {ARMS[r['arm']]} | {r['history']} | ${r.get('cost_usd') or 0:.3f} | {', '.join(r['files_written']) or 'nothing'} |")
        plan_files = {(r["arm"], str(r["history"])): set(r["files_written"]) for r in syns}
        L += ["", "Did later u6 and u7 answers open the saved plan, and were they right?", "",
              "| Version | History | Checkpoint | Question | Opened the plan | Graded |", "|---|---|---|---|---|---|"]
        for sr in sessions:
            pf = plan_files.get((sr["arm"], str(sr["history"])))
            if not pf or sr["checkpoint"] <= CFG["synthesis"]["after_checkpoint"]:
                continue
            for n, t in enumerate(sr["turns"]):
                if t["question"] in ("u6-q1", "u7-starts"):
                    g = grades.get((sr["_dir"], sr["_file"], n))
                    L.append(f"| {ARMS[sr['arm']]} | {sr['history']} | {sr['checkpoint']} | {t['question']} ({sr['session']}) | "
                             f"{'yes' if pf & set(t.get('read_paths', [])) else 'no'} | {'pass' if g else 'fail' if g is False else '-'} |")

    L += ["", "## Cost per question, by session size", "",
          "Median cost of one question, by how many questions the session held. The first turn carries the session's startup cost.", "",
          "| Version | Checkpoint | 1 per session | 3 per session | 6 per session | First-turn context |", "|---|---|---|---|---|---|"]
    per_q = {}
    for x in arms:
        for cp in CHECKPOINTS:
            ss = [s for s in sessions if s["arm"] == x and s["checkpoint"] == cp]
            if not ss:
                continue
            row = []
            for size in (1, 3, 6):
                # u7 has a session of its own and is reported separately below.
                vals = [s["cost_usd"] / s["size"] for s in ss if s["size"] == size and s["session"] != "s1-u7"]
                per_q[(x, cp, size)] = med(vals)
                row.append(f"${med(vals):.3f}" if vals else "-")
            first = med([s["turns"][0]["first_context"] for s in ss])
            L.append(f"| {ARMS[x]} | {cp} | " + " | ".join(row) + f" | {round(first) if first else '-'} |")

    L += ["", "## u7, the question that spans many clients", "", "Cost of its single-question session, by checkpoint.", "",
          "| Version | " + " | ".join(f"cp{c}" for c in CHECKPOINTS) + " |", "|---|" + "---|" * len(CHECKPOINTS)]
    for x in arms:
        row = []
        for cp in CHECKPOINTS:
            v = med([s["cost_usd"] for s in sessions if s["arm"] == x and s["checkpoint"] == cp and s["session"] == "s1-u7"])
            row.append(f"${v:.3f}" if v is not None else "-")
        L.append(f"| {ARMS[x]} | " + " | ".join(row) + " |")

    L += ["", "## Accuracy", "", "| Version | Checkpoint | Pass | Of |", "|---|---|---|---|"]
    for x in arms:
        for cp in CHECKPOINTS:
            ss = [s for s in sessions if s["arm"] == x and s["checkpoint"] == cp]
            gs = [grades.get((s["_dir"], s["_file"], n)) for s in ss for n in range(len(s["turns"]))]
            if gs:
                L.append(f"| {ARMS[x]} | {cp} | {sum(1 for g in gs if g)} | {len(gs)}" + (f" ({sum(1 for g in gs if g is None)} ungraded)" if None in gs else "") + " |")
    fails = [(s, n) for s in sessions for n in range(len(s["turns"])) if grades.get((s["_dir"], s["_file"], n)) is False]
    if fails:
        L += ["", "Failed answers:", ""]
        for s, n in fails:
            L.append(f"- {ARMS[s['arm']]} h{s['history']} cp{s['checkpoint']} {s['session']} {s['turns'][n]['question']}")

    L += ["", "## Files after the last edit", ""]
    for root, _, files in os.walk(RAW):
        if "currency.json" in files:
            c = json.load(open(os.path.join(root, "currency.json")))
            n = sum(len(f.get("stale", [])) for f in c["files"])
            L.append(f"- {os.path.relpath(root, RAW)}, after edit {c['checkpoint']}: {n} stale claims")
            for f in c["files"]:
                for q in f.get("stale", []):
                    L.append(f"  - {f['file']}: {q}")

    # Cumulative cost: edits so far, plus r questions per edit at the cost measured at the nearest earlier checkpoint.
    L += ["", "## Total cost over time", "",
          "Edits so far plus questions asked at a given rate, using each checkpoint's measured cost per question. "
          "Pick the row nearest to how you actually work.", ""]
    max_edit = max([e["step"] for e in edits], default=0)
    for size in (1, 3, 6):
        L += [f"### {size} question{'s' if size > 1 else ''} per session", "",
              "| Questions per edit | " + " | ".join(ARMS[x] for x in arms) + " |", "|---|" + "---|" * len(arms)]
        for r in (1, 5, 10, 20, 50):
            row = []
            for x in arms:
                total = 0.0
                ok = True
                for k in range(1, max_edit + 1):
                    es = [e["cost_usd"] for e in edits if e["arm"] == x and e["step"] == k]
                    # The latest checkpoint before this edit that has measurements.
                    have = [c for c in CHECKPOINTS if (c < k or c == 0) and per_q.get((x, c, size)) is not None]
                    q = per_q.get((x, max(have), size)) if have else None
                    if not es or q is None:
                        ok = False
                        break
                    total += med(es) + r * q
                row.append(f"${total:.2f}" if ok else "-")
            L.append(f"| {r} | " + " | ".join(row) + " |")
        L.append("")

    syn_cost = sum(json.load(open(os.path.join(r, "synthesis.json"))).get("cost_usd") or 0
                   for r, _, fs in os.walk(RAW) if "synthesis.json" in fs)
    spend = sum(s["cost_usd"] for s in sessions) + sum(e.get("cost_usd") or 0 for e in edits) + syn_cost
    L += ["## Spend", "", f"${spend:.2f} for {len(edits)} edits, {len(sessions)} question sessions and the saved plans, before grading.", ""]
    open(os.path.join(E.RESULTS, "report-s200long.md"), "w").write("\n".join(L))
    print("\n".join(L))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--model", choices=list(E.MODELS), default="sonnet")
    r.add_argument("--arms", default="a,d,e")
    r.add_argument("--histories", type=int, default=1)
    r.add_argument("--upto", type=int, default=len(CFG["edits"]))
    r.add_argument("--checkpoints", help="comma list, default all")
    r.add_argument("--jobs", type=int, default=3)
    r.add_argument("--control", action="store_true", help="add one OS history that skips the saved plan")
    r.add_argument("--yes", action="store_true")
    for name in ("grade", "currency"):
        g = sub.add_parser(name)
        g.add_argument("--jobs", type=int, default=4)
    sub.add_parser("report")
    a = ap.parse_args()
    {"run": cmd_run, "grade": cmd_grade, "currency": cmd_currency, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
