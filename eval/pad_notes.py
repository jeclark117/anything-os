#!/usr/bin/env python3
"""Build the long-note set (s60-long) from s60.

Each loose note gets about 1,200 words of padding: realistic working-note
prose that adds no facts. The padding is checked mechanically and rejected if
it contains a digit, a currency sign, or a capitalized name the notes don't
already use. The OS version gets the same padding, attached to whichever OS
note holds that loose note's facts, so both versions carry the same text.

  python3 eval/pad_notes.py generate     write padding for any note missing it
  python3 eval/pad_notes.py build        assemble fixtures-60-long from s60 + padding
  python3 eval/pad_notes.py placement    show where each note's facts land
"""
import concurrent.futures as cf, hashlib, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "fixtures-60")
DST = os.path.join(HERE, "fixtures-60-long")
PAD = os.path.join(HERE, "padding")
MODEL = "claude-sonnet-5-5"
TARGET_WORDS = 1200

# Which OS note holds each loose note's facts.
OS_NOTE = {
 "client a kickoff.md": "clients/client-a/client-a.md", "call notes sept 8.md": "clients/client-a/client-a.md",
 "client a sept 22.md": "clients/client-a/client-a.md", "meeting oct 1.md": "clients/client-a/client-a.md",
 "client a oct 15.md": "clients/client-a/client-a.md", "client a sitemap.md": "clients/client-a/sitemap.md",
 "client a homepage feedback.md": "clients/client-a/homepage-feedback.md", "client a invoice plan.md": "clients/client-a/invoice-plan.md",
 "client b.md": "clients/client-b/client-b.md", "client b kickoff.md": "clients/client-b/kickoff.md",
 "client b call.md": "clients/client-b/call.md", "client b moodboard.md": "clients/client-b/moodboard.md",
 "client b questions.md": "clients/client-b/questions.md",
 "client c.md": "clients/client-c.md", "client c invoice.md": "clients/client-c.md", "client c testimonial.md": "clients/client-c.md",
 "client d.md": "clients/client-d.md", "client d call.md": "clients/client-d.md",
 "client e.md": "clients/client-e.md", "client e oct.md": "clients/client-e.md", "client e invoice nov.md": "clients/client-e.md",
 "client f.md": "clients/client-f.md", "referral from pat.md": "clients/client-f.md", "client g.md": "clients/client-g.md",
 "client h.md": "clients/client-h.md", "leads.md": "clients/leads.md",
 "insurance.md": "admin/insurance.md", "insurance 2025.md": "admin/insurance.md",
 "taxes.md": "admin/taxes.md", "taxes 2025.md": "admin/taxes.md", "accountant.md": "admin/accountant.md",
 "business bank.md": "admin/bank.md", "domain.md": "admin/domain.md", "tools.md": "admin/tools.md",
 "software costs.md": "admin/tools.md", "contracts.md": "admin/contracts.md", "invoices.md": "admin/invoices.md",
 "rates.md": "business/rates.md", "pricing research.md": "business/rates.md", "capacity.md": "business/capacity.md",
 "todo.md": "todo.md", "ideas.md": "business/ideas.md", "newsletter idea.md": "business/ideas.md",
 "workshop idea.md": "business/ideas.md", "q4 goals.md": "business/goals.md", "contacts.md": "business/contacts.md",
 "weekly routine.md": "business/routine.md", "holidays.md": "business/routine.md",
 "client feedback themes.md": "business/notes.md", "meeting notes misc.md": "business/notes.md",
 "equipment.md": "business/workspace.md", "office.md": "business/workspace.md", "learning.md": "business/workspace.md",
 "reading list.md": "business/workspace.md",
 "marketing.md": "marketing/ads.md", "instagram.md": "marketing/instagram.md", "portfolio.md": "marketing/portfolio.md",
 "website.md": "marketing/website.md", "brand.md": "marketing/brand.md", "networking.md": "marketing/networking.md",
}

def allowed_names():
    words = set()
    for fn in os.listdir(os.path.join(SRC, "a-loose")):
        words |= set(re.findall(r"\b[A-Z][a-z]+\b", open(os.path.join(SRC, "a-loose", fn)).read()))
    return words | {"Client", "Example", "Co", "Figma", "Webflow", "Instagram", "I", "The", "A"}

def problems(text, names):
    issues = []
    if re.search(r"\d", text): issues.append("contains a digit")
    if re.search(r"[$£€¥]", text): issues.append("contains a currency sign")
    # A capitalized word mid-sentence that isn't already a name in the notes.
    for w in set(re.findall(r"(?<=[a-z,;:] )([A-Z][a-z]+)", text)):
        if w not in names: issues.append(f"new name '{w}'")
    if len(text.split()) < TARGET_WORDS * 0.8: issues.append(f"too short ({len(text.split())} words)")
    return issues

PROMPT = """I'm building test data for an evaluation of note-taking systems. Below is a short note from a fictional one-person design studio. Write about {n} words of general working notes that could sit below it: approach, process, things to keep in mind, and open-ended ideas, in the same casual voice. Plain prose and loose bullet points.

Constraints, because the test depends on them:
- No dates, days of the week, months, times, or numbers of any kind, including numbers written as words.
- No prices, amounts, durations, quantities, or percentages.
- No names of people, companies, clients, products, tools, or places, other than words already in the note.
- No decisions, commitments, agreements, deadlines, or status changes.
- Don't repeat or contradict anything the note says.

Reply with only the text.

The note:
<note>
{note}
</note>"""

def generate_one(fn, names):
    out = os.path.join(PAD, fn.replace(".md", ".txt"))
    if os.path.exists(out): return fn, "skipped"
    note = open(os.path.join(SRC, "a-loose", fn)).read()
    last = []
    for attempt in range(3):
        work = tempfile.mkdtemp(prefix="aos-pad-")
        try:
            p = subprocess.run(["claude", "-p", PROMPT.format(n=TARGET_WORDS, note=note), "--model", MODEL,
                                "--output-format", "json", "--tools", "", "--strict-mcp-config",
                                "--setting-sources", "project", "--no-session-persistence"],
                               cwd=work, capture_output=True, text=True, timeout=600, stdin=subprocess.DEVNULL)
            text = json.loads(p.stdout).get("result", "").strip()
            if text.startswith("API Error"):
                last = ["refused: " + text[:80]]
                continue
        finally:
            shutil.rmtree(work, ignore_errors=True)
        last = problems(text, names)
        if not last:
            os.makedirs(PAD, exist_ok=True)
            open(out, "w").write(text + "\n")
            return fn, f"ok, {len(text.split())} words, attempt {attempt + 1}"
    return fn, "FAILED: " + "; ".join(last[:4])

def cmd_generate():
    names = allowed_names()
    fns = sorted(os.listdir(os.path.join(SRC, "a-loose")))
    assert set(fns) == set(OS_NOTE), set(fns) ^ set(OS_NOTE)
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for fn, status in ex.map(lambda f: generate_one(f, names), fns):
            print(f"{fn}: {status}")

POSITIONS = ("top", "middle", "bottom")


def _hash(fn):
    return int(hashlib.sha256(fn.encode()).hexdigest(), 16)


# Notes sorted by hash, then dealt top, middle, bottom in turn: exactly a third
# in each position, fixed across rebuilds, and not tied to the file name order.
_ORDER = sorted(OS_NOTE, key=_hash)
_POS = {fn: POSITIONS[i % 3] for i, fn in enumerate(_ORDER)}


def placement(fn):
    """A fixed position for this note's facts within its padding. Varied so
    facts aren't always in the first lines, which would make them too easy to
    find. The second value places a middle split somewhere in the middle third."""
    return _POS[fn], (_hash(fn) >> 8) % 1000 / 1000


def split_padding(pad, fn):
    """Split padding into the part above the facts and the part below."""
    paras = [x for x in re.split(r"\n\s*\n", pad.strip()) if x.strip()]
    pos, jitter = placement(fn)
    if pos == "top":
        cut = 0
    elif pos == "bottom":
        cut = len(paras)
    else:  # somewhere in the middle third to two-thirds
        cut = max(1, min(len(paras) - 1, round(len(paras) * (1 / 3 + jitter / 3))))
    return "\n\n".join(paras[:cut]), "\n\n".join(paras[cut:])


def cmd_build():
    if os.path.exists(DST): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    above, below = {}, {}
    for fn, osn in OS_NOTE.items():
        pad = open(os.path.join(PAD, fn.replace(".md", ".txt"))).read()
        up, down = split_padding(pad, fn)
        for arm in ("a-loose", "b-rules"):
            path = os.path.join(DST, arm, fn)
            lines = open(path).read().rstrip("\n").split("\n")
            # Loose notes open with a title line. Keep it first, like a real note.
            title, facts = lines[0], "\n".join(lines[1:]).strip()
            parts = [title] + [x for x in (up, facts, down) if x]
            open(path, "w").write("\n\n".join(parts) + "\n")
        above.setdefault(osn, []).append(up)
        below.setdefault(osn, []).append(down)
    for osn in above:
        path = os.path.join(DST, "c-os", osn)
        text = open(path).read()
        # Header block and H1 stay on top. The body keeps its own structure,
        # with the same padding above and below it as its loose sources.
        head, body = text.split("\n# ", 1)
        h1, rest = body.split("\n", 1)
        up = "\n\n".join(x for x in above[osn] if x)
        down = "\n\n".join(x for x in below[osn] if x)
        parts = [x for x in (up, rest.strip(), down) if x]
        open(path, "w").write(head + "\n# " + h1 + "\n\n" + "\n\n".join(parts) + "\n")
    print(f"Built {DST}")


def cmd_placement():
    from collections import Counter
    c = Counter(placement(fn)[0] for fn in OS_NOTE)
    print("positions across the 60 notes:", dict(c))
    for trap_note in ("call notes sept 8.md", "client a oct 15.md", "insurance.md", "insurance 2025.md",
                      "client b.md", "client b kickoff.md", "domain.md", "client d.md", "marketing.md", "todo.md", "capacity.md"):
        print(f"  {trap_note}: {placement(trap_note)[0]}")


if __name__ == "__main__":
    {"generate": cmd_generate, "build": cmd_build, "placement": cmd_placement}[sys.argv[1]]()
