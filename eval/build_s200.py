#!/usr/bin/env python3
"""Build the 200-note set (s200long) from the 60-note set plus s200_notes.py.

Three versions, all with the same notes and the same padding:
  a-loose            200 loose notes, no instruction file
  d-os-conventions   the OS plus conventions.md, as onboarding would leave it
  e-os-heavy         the same OS with about 8,500 tokens of instructions that
                     load every session, matched to the owner's own work OS

  python3 eval/build_s200.py pad        write padding for any new note missing it
  python3 eval/build_s200.py extras     write the heavy version's extra instructions
  python3 eval/build_s200.py build      assemble fixtures-200-long
  python3 eval/build_s200.py stats      words, files, and instruction sizes
  python3 eval/build_s200.py check-sources   the five raw-source edits follow s200-update.md
"""
import concurrent.futures as cf, hashlib, os, re, shutil, sys

import pad_notes as P
from s200_notes import NOTES, OS_TEXT, NEW_AREAS, NEW_FOLDERS

HERE = os.path.dirname(os.path.abspath(__file__))
SRC60 = os.path.join(HERE, "fixtures-60")
DST = os.path.join(HERE, "fixtures-200-long")
PAD200 = os.path.join(HERE, "padding-200")
EXTRAS = os.path.join(HERE, "s200-extras")
CONVENTIONS = os.path.join(os.path.dirname(HERE), "conventions.md")
STAMP = "generated: { by: process:eval-fixture, at: 2026-10-15T17:00:00-07:00 }"


def names():
    words = P.allowed_names()
    for _, _, _, body in NOTES:
        words |= set(re.findall(r"\b[A-Z][a-z]+\b", body))
    return words


# ---------------------------------------------------------------- padding

def pad_one(entry, allowed):
    fn, _, _, body = entry
    out = os.path.join(PAD200, fn.replace(".md", ".txt"))
    if os.path.exists(out):
        return fn, "skipped"
    import json, subprocess, tempfile
    last = []
    for attempt in range(3):
        work = tempfile.mkdtemp(prefix="aos-pad-")
        try:
            p = subprocess.run(["claude", "-p", P.PROMPT.format(n=P.TARGET_WORDS, note=body), "--model", P.MODEL,
                                "--output-format", "json", "--tools", "", "--strict-mcp-config",
                                "--setting-sources", "project", "--no-session-persistence"],
                               cwd=work, capture_output=True, text=True, timeout=600, stdin=subprocess.DEVNULL)
            text = json.loads(p.stdout).get("result", "").strip()
        except Exception as e:
            last = [f"error: {e}"]
            continue
        finally:
            shutil.rmtree(work, ignore_errors=True)
        last = P.problems(text, allowed)
        if not last:
            os.makedirs(PAD200, exist_ok=True)
            open(out, "w").write(text + "\n")
            return fn, f"ok, {len(text.split())} words, attempt {attempt + 1}"
    return fn, "FAILED: " + "; ".join(last[:4])


def cmd_pad():
    allowed = names()
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for fn, status in ex.map(lambda e: pad_one(e, allowed), NOTES):
            print(f"{fn}: {status}")


# ---------------------------------------------------------------- heavy instructions

EXTRA_PROMPT = """I'm building test data for an evaluation of note-taking systems. Write a {kind} for an AI assistant that works inside a one-person design studio's folder of notes. About {n} words, plain markdown with headings and bullets, written to the assistant as "you".

{about}

Constraints, because the test depends on them:
- No dates, days, months, times, or numbers of any kind, including numbers written as words.
- No prices, amounts, durations, quantities, or percentages.
- No names of people, companies, clients, products, tools, or places.
- Nothing about any specific client or project.

Reply with only the document."""

EXTRA_DOCS = {
    "writing.md": ("writing standard", "It covers how the studio writes to clients: tone, structure of an email, how to give bad news, how to ask for feedback, words to avoid, how to write a proposal summary, and a checklist to run before anything is sent. Detailed, like a real house style guide."),
    "working.md": ("working guide", "It covers how the assistant should handle requests: when to just do the task and when to ask first, how to prepare for a client call, how to draft a proposal from notes, how to handle money questions, how to keep the to-do list useful, what to do at the start and end of each week, and how to report back. Detailed, like a real operating manual."),
}
EXTRA_WORDS = 2400


def cmd_extras():
    import json, subprocess, tempfile
    os.makedirs(EXTRAS, exist_ok=True)
    allowed = names()
    for fn, (kind, about) in EXTRA_DOCS.items():
        out = os.path.join(EXTRAS, fn)
        if os.path.exists(out):
            print(f"{fn}: skipped")
            continue
        for attempt in range(3):
            work = tempfile.mkdtemp(prefix="aos-extra-")
            try:
                p = subprocess.run(["claude", "-p", EXTRA_PROMPT.format(kind=kind, n=EXTRA_WORDS, about=about),
                                    "--model", P.MODEL, "--output-format", "json", "--tools", "", "--strict-mcp-config",
                                    "--setting-sources", "project", "--no-session-persistence"],
                                   cwd=work, capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
                text = json.loads(p.stdout).get("result", "").strip()
            finally:
                shutil.rmtree(work, ignore_errors=True)
            # Title-case headings read as new names to the padding check, so
            # only digits and currency count here. The capitalized words get
            # printed for a person to look over instead.
            issues = [i for i in P.problems(text, allowed) if not i.startswith(("too short", "new name"))]
            caps = sorted(set(re.findall(r"(?<=[a-z,;:] )([A-Z][a-z]+)", text)) - allowed)
            print(f"{fn}: capitalized words mid-sentence: {', '.join(caps) or 'none'}")
            if len(text.split()) < EXTRA_WORDS * 0.8:
                issues.append(f"too short ({len(text.split())} words)")
            if not issues:
                open(out, "w").write(text + "\n")
                print(f"{fn}: ok, {len(text.split())} words")
                break
            print(f"{fn}: attempt {attempt + 1} rejected: {'; '.join(issues[:4])}")


# ---------------------------------------------------------------- build

def _hash(s):
    return int(hashlib.sha256(s.encode()).hexdigest(), 16)


_NEW_ORDER = sorted((n[0] for n in NOTES), key=_hash)
_NEW_POS = {fn: P.POSITIONS[i % 3] for i, fn in enumerate(_NEW_ORDER)}


def split_new(pad, fn):
    """Same as pad_notes.split_padding, with positions dealt over the new notes."""
    paras = [x for x in re.split(r"\n\s*\n", pad.strip()) if x.strip()]
    pos, jitter = _NEW_POS[fn], (_hash(fn) >> 8) % 1000 / 1000
    cut = 0 if pos == "top" else len(paras) if pos == "bottom" else \
        max(1, min(len(paras) - 1, round(len(paras) * (1 / 3 + jitter / 3))))
    return "\n\n".join(paras[:cut]), "\n\n".join(paras[cut:])


def os_body(lines):
    out = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        ln = ln[2:] if ln.startswith("- ") else ln
        out.append("- " + ln[0].upper() + ln[1:])
    return "\n".join(out)


def title_of(fn, os_path):
    base = os.path.basename(os_path)[:-3].replace("-", " ")
    parent = os.path.basename(os.path.dirname(os_path))
    if parent.startswith("client-") and base != parent.replace("-", " "):
        base = parent.replace("-", " ") + ": " + base
    elif parent in ("bookkeeping", "reviews", "meetings", "motion-course"):
        base = {"bookkeeping": "Books", "reviews": "Review", "meetings": "Meeting", "motion-course": "Motion course"}[parent] + ": " + base
    base = base[0].upper() + base[1:]
    return re.sub(r"\b[Cc]lient ([a-z])\b", lambda m: "Client " + m.group(1).upper(), base)


def write_os_note(root, fn, os_path, desc, body, up, down):
    lines = body.split("\n")
    text = OS_TEXT.get(fn) or os_body(lines[1:])
    title = title_of(fn, os_path)
    head = f'---\ntype: Note\ntitle: "{title}"\ndescription: "{desc}"\n{STAMP}\n---\n\n# {title}\n\n'
    path = os.path.join(root, os_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(head + "\n\n".join(x for x in (up, text, down) if x) + "\n")


def write_loose(path, body, up, down):
    lines = body.split("\n")
    title, facts = lines[0], "\n".join(lines[1:]).strip()
    open(path, "w").write("\n\n".join(x for x in (title, up, facts, down) if x) + "\n")


def add_listing(index_path, line, heading=None):
    text = open(index_path).read().rstrip("\n") if os.path.exists(index_path) else f"# {heading}\n"
    open(index_path, "w").write(text + "\n" + line + "\n")


def build_os(root):
    """Start from the 60-note OS (short), add conventions and the 140 new notes."""
    shutil.copytree(os.path.join(SRC60, "c-os"), root)
    shutil.copy(CONVENTIONS, os.path.join(root, "conventions.md"))
    claude = open(os.path.join(root, "CLAUDE.md")).read()
    area_lines = "".join(f"- [{a}/]({a}/) - {d}\n" for a, d in NEW_AREAS.items())
    claude = re.sub(r"(## The areas\n\n(?:- .*\n)+)", lambda m: m.group(1) + area_lines, claude)
    open(os.path.join(root, "CLAUDE.md"), "w").write(claude)
    idx = open(os.path.join(root, "index.md")).read()
    idx = re.sub(r"(# Areas\n\n(?:\* .*\n)+)", lambda m: m.group(1) + "".join(f"* [{a}/]({a}/) - {d}\n" for a, d in NEW_AREAS.items()), idx)
    idx = idx.replace("* [log.md](log.md)", "* [conventions.md](conventions.md) - The rules every file follows.\n* [log.md](log.md)")
    open(os.path.join(root, "index.md"), "w").write(idx)
    for a in NEW_AREAS:
        os.makedirs(os.path.join(root, a), exist_ok=True)
        open(os.path.join(root, a, "index.md"), "w").write(f"# {a.capitalize()}\n\n")
    for folder, desc in NEW_FOLDERS.items():
        os.makedirs(os.path.join(root, folder), exist_ok=True)
        name = os.path.basename(folder)
        open(os.path.join(root, folder, "index.md"), "w").write(f"# {name.replace('-', ' ').title()}\n\n")
        add_listing(os.path.join(root, os.path.dirname(folder), "index.md"), f"* [{name}/]({name}/) - {desc}")
    for fn, os_path, desc, _ in NOTES:
        d, base = os.path.split(os_path)
        add_listing(os.path.join(root, d, "index.md"), f"* [{base}]({base}) - {desc}")
    log = open(os.path.join(root, "log.md")).read()
    log = log.replace("# Log\n", "# Log\n\n## 2026-10-15\n\n* Added the process and learning areas, and folders for clients with three or more notes.\n", 1)
    open(os.path.join(root, "log.md"), "w").write(log)


def pad_os_originals(root, above, below):
    """Pad the 60 original notes' OS versions exactly as pad_notes.cmd_build does."""
    for osn in above:
        path = os.path.join(root, osn)
        text = open(path).read()
        head, body = text.split("\n# ", 1)
        h1, rest = body.split("\n", 1)
        up = "\n\n".join(x for x in above[osn] if x)
        down = "\n\n".join(x for x in below[osn] if x)
        parts = [x for x in (up, rest.strip(), down) if x]
        open(path, "w").write(head + "\n# " + h1 + "\n\n" + "\n\n".join(parts) + "\n")


# The generated docs run long. Each is cut at a section boundary to about this
# many words, which puts the heavy version's always-loaded instructions near
# the 8,500 tokens of the owner's work OS. Measured, not estimated: see stats.
EXTRA_KEEP_WORDS = 1550


def trim_at_heading(doc, words):
    parts = re.split(r"(?m)^(?=## )", doc)
    out, n = [], 0
    for part in parts:
        w = len(part.split())
        if out and n + w > words:
            break
        out.append(part)
        n += w
    return "".join(out).rstrip() + "\n"


def cmd_build():
    missing = [n[0] for n in NOTES if not os.path.exists(os.path.join(PAD200, n[0].replace(".md", ".txt")))]
    if missing:
        sys.exit(f"{len(missing)} new notes have no padding. Run `pad` first.")
    if os.path.exists(DST):
        shutil.rmtree(DST)
    os.makedirs(DST)
    # Loose
    loose = os.path.join(DST, "a-loose")
    shutil.copytree(os.path.join(SRC60, "a-loose"), loose)
    above, below = {}, {}
    for fn, osn in P.OS_NOTE.items():
        up, down = P.split_padding(open(os.path.join(P.PAD, fn.replace(".md", ".txt"))).read(), fn)
        write_loose(os.path.join(loose, fn), open(os.path.join(SRC60, "a-loose", fn)).read().rstrip("\n"), up, down)
        above.setdefault(osn, []).append(up)
        below.setdefault(osn, []).append(down)
    new_pads = {}
    for fn, os_path, desc, body in NOTES:
        assert not os.path.exists(os.path.join(loose, fn)), fn
        up, down = split_new(open(os.path.join(PAD200, fn.replace(".md", ".txt"))).read(), fn)
        new_pads[fn] = (up, down)
        write_loose(os.path.join(loose, fn), body, up, down)
    # OS
    d = os.path.join(DST, "d-os-conventions")
    build_os(d)
    pad_os_originals(d, above, below)
    for fn, os_path, desc, body in NOTES:
        assert not os.path.exists(os.path.join(d, os_path)), os_path
        write_os_note(d, fn, os_path, desc, body, *new_pads[fn])
    # Heavy OS: the same folder, plus instructions that load every session.
    e = os.path.join(DST, "e-os-heavy")
    shutil.copytree(d, e)
    for fn in EXTRA_DOCS:
        doc = trim_at_heading(open(os.path.join(EXTRAS, fn)).read(), EXTRA_KEEP_WORDS)
        title = EXTRA_DOCS[fn][0].capitalize()
        open(os.path.join(e, fn), "w").write(f'---\ntype: Standard\ntitle: "{title}"\ndescription: "The studio\'s {EXTRA_DOCS[fn][0]}."\n{STAMP}\n---\n\n' + doc)
    with open(os.path.join(e, "CLAUDE.md"), "a") as fh:
        fh.write("\n## Standards that always apply\n\n@conventions.md\n\n@writing.md\n\n@working.md\n")
    idx = open(os.path.join(e, "index.md")).read().replace(
        "* [log.md](log.md)", "* [writing.md](writing.md) - How the studio writes to clients.\n* [working.md](working.md) - How the agent handles requests.\n* [log.md](log.md)")
    open(os.path.join(e, "index.md"), "w").write(idx)
    print(f"Built {DST}")
    cmd_stats()


def cmd_stats():
    for arm in sorted(os.listdir(DST)):
        root = os.path.join(DST, arm)
        mds = [os.path.join(r, f) for r, _, fs in os.walk(root) for f in fs if f.endswith(".md")]
        notes = [m for m in mds if os.path.basename(m) not in ("index.md", "log.md", "CLAUDE.md", "conventions.md", "writing.md", "working.md")]
        words = sum(len(open(m).read().split()) for m in mds)
        auto = 0
        cl = os.path.join(root, "CLAUDE.md")
        if os.path.exists(cl):
            auto = len(open(cl).read())
            for imp in re.findall(r"^@(\S+)", open(cl).read(), re.M):
                auto += len(open(os.path.join(root, imp)).read())
        print(f"{arm}: {len(mds)} files, {len(notes)} notes, {words} words, auto-loaded instructions ~{auto // 4} tokens")


# ---------------------------------------------------------------- raw sources

def numbers(text):
    """Every figure in a text, with thousands commas dropped, so $4,200 and 4200 match."""
    return set(re.findall(r"\d+", re.sub(r"(?<=\d),(?=\d{3})", "", text)))


def banned_rx(word):
    # A banned word matches at the start of a word, so "bill" catches "billing"
    # but "rate" doesn't catch "separate". A phrase ending in one letter, like
    # "Client A", has to end there too.
    end = r"\b" if re.search(r"\b\w$", word) else ""
    return re.compile(r"\b" + re.escape(word) + end, re.I)


def cmd_check_sources():
    import json
    cfg = json.load(open(os.path.join(HERE, "s200.json")))
    known = set()
    for fn in os.listdir(os.path.join(SRC60, "a-loose")):
        known |= numbers(open(os.path.join(SRC60, "a-loose", fn)).read())
    for _, _, _, body in NOTES:
        known |= numbers(body)
    failed = 0
    for i, ed in enumerate(cfg["edits"], 1):
        if "source" not in ed:
            known |= numbers(ed["text"])
            continue
        text = open(os.path.join(HERE, ed["source"])).read()
        issues = []
        words = len(text.split())
        if not 300 <= words <= 600:
            issues.append(f"{words} words, outside 300 to 600")
        for w in ed["banned"]:
            hits = banned_rx(w).findall(text)
            if hits:
                issues.append(f"banned '{w}' appears {len(hits)} times")
        n = text.count(ed["fact_phrase"])
        if n != 1:
            issues.append(f"fact phrase appears {n} times")
        else:
            at = text.index(ed["fact_phrase"]) / len(text)
            if not 1 / 3 <= at <= 2 / 3:
                issues.append(f"fact sits at {at:.0%} of the text, outside the middle third")
        allowed = known | numbers(ed["text"]) | numbers(ed["date"])
        new = sorted(numbers(text) - allowed, key=int)
        if new:
            issues.append("numbers not in the notes or the fact: " + ", ".join(new))
        print(f"edit {i}, {ed['source']}: {words} words, " + ("OK" if not issues else "FAIL: " + "; ".join(issues)))
        failed += bool(issues)
        known |= numbers(ed["text"])
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    {"pad": cmd_pad, "extras": cmd_extras, "build": cmd_build, "stats": cmd_stats,
     "check-sources": cmd_check_sources}[sys.argv[1]]()
