---
type: Standard
title: Conventions
description: The rules every file in this OS follows. Written for the agent. The person never needs to read it.
status: draft
generated: { by: claude-code/opus-5, at: 2026-10-20T22:19:01-07:00 }
---

# Conventions

These are the rules for every file in this folder. They're written for you, the agent. The person you work with doesn't need to know any of this, so don't explain it unless they ask.

The format underneath is [OKF v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md), the Open Knowledge Format, an open format from Google Cloud for folders of notes that agents maintain. You don't need the spec. Everything you need is on this page.

---

## 1. The rules that matter most

These are why the system works. Follow them in every file, in every conversation.

**Don't invent facts or numbers.** Not as examples, not as round estimates, not as "typical" figures. If something isn't known, the note says it isn't known and says what would settle it. For example: "Renewal date: not known yet. It's on the policy document." A note that admits a gap is worth more than one that fills it with something plausible.

**A guess stays a guess.** If something hasn't been decided, the note is marked `draft`, however many times it gets repeated. Repetition isn't a decision. Only the person can turn a draft into a decision.

**Only the person confirms.** A note can carry a `verified` entry showing the person checked it. You never write one. It's their signature, and writing it yourself would be forging it.

**Every number cites where it came from.** A figure in a note needs a source behind it: a document, a website, or the person saying so. See §4 for how.

**Dates are written out in full.** "2026-10-20," never "last week" or "next spring." Relative dates go wrong the day after they're written.

**Use the person's words.** If they call it "the schedule board," the note says "the schedule board."

---

## 2. What every note looks like

Every note opens with a short header block between two `---` lines, then the note itself. The header is for you and other tools. It's how you can tell what a note is and how sure it is without reading all of it.

```yaml
---
type: Note
title: Kitchen faucet replacement
description: One sentence saying what this note is. Listings quote it.
status: draft
generated: { by: claude-code/opus-5, at: 2026-10-20T14:22:05-07:00 }
---
```

| Field | Required | What it holds |
|---|---|---|
| `type` | **Yes** | What kind of note this is. See §3. |
| `title` | No, but use it | A short name. |
| `description` | No, but use it | One sentence. The folder's listing quotes it, so write it once and write it well. |
| `status` | No | `draft`, `stable`, or `deprecated`. Leaving it out means `stable`. Anything undecided is `draft`. |
| `generated` | No, but use it | Who last wrote the note and when. Update it every time you edit. |
| `sources` | When there's a fact | Where the facts came from. See §4. |
| `verified` | Never by you | Only the person writes it. See §1. |
| `stale_after` | No | A date after which the note should be rechecked. Useful for prices, deadlines, and anything else that goes out of date. |

**Who wrote it.** `generated.by` names the writer:
- A person is `human:` plus their name in lowercase with no spaces, like `human:sam`.
- An agent is its tool and model with a slash between them, like `claude-code/opus-5` or `codex/gpt-5`. Use whatever your tool and model actually are. If you don't know your model, use your tool's name and `unknown`, like `cowork/unknown`.
- An automated process is `process:` plus a name, like `process:weekly-cleanup`.

**When it was written.** `generated.at` is the real current time with a time zone, like `2026-10-20T14:22:05-07:00`. It's how you can tell an old note from a fresh one. Never use midnight or any other made-up time as a stand-in for "sometime that day." If you can't read the clock, leave the `generated` line out of that edit rather than guessing. It's optional, and an invented time is worse than none.

---

## 3. Types

`type` says what kind of note it is, so you can sort and find notes without reading each one. Nobody sets a master list. Each OS makes its own vocabulary, and a tool that meets a type it doesn't know just carries on.

Start with these and add only when one doesn't fit:

| `type` | Used for |
|---|---|
| `Identity` | `CLAUDE.md` or `AGENTS.md`. Who you are in this OS and the person's rules. |
| `Standard` | Rules to follow. This file. A writing guide. |
| `Note` | The default. Most things are notes. |
| `Decision` | Something the person decided, with the reasoning. Usually `stable`. |
| `Research` | Looking into something. Ends in a recommendation, not a pile of findings. |
| `Reference` | Facts to look up later: contacts, account details that aren't secret, how-tos. |

When you add a type, add a row to this table so the next session knows it exists.

**Types in this OS:** the six above, until you add one.

---

## 4. Sources

A fact needs a source behind it. Sources go in the header, and the note points at them with a footnote.

```yaml
sources:
  - id: policy-2026
    resource: house/insurance-policy.pdf
    title: "Homeowner's policy, page 3"
  - id: sam-2026-10-20
    resource: human:sam
    title: "Sam said this on 2026-10-20"
```

Then in the note:

```markdown
The deductible is on page 3 of the policy.[^policy-2026]

[^policy-2026]: Homeowner's policy, page 3
```

- `id` is a short label, unique within the note. Every footnote label has to match an `id`.
- `resource` is a link, a file path, or a person. When the person tells you something directly, they're the source, and you record when they said it.
- If there's no source, there's no figure. Write that it's not known and what would settle it.

---

## 5. Special files

Two filenames have their own rules. They aren't notes, so they follow different structures.

**`index.md` lists what's in a folder.** Every folder has one. It has no header block, with one exception: the `index.md` at the very top of this OS starts with this, and nothing else uses it:

```yaml
---
okf_version: "0.2"
---
```

An `index.md` is a title, then one line per file or subfolder: a link, then a dash, then the note's `description`. Group the lines under short headings if the list gets long. An empty folder's listing says so and says how to add something.

**`log.md` is a dated history.** It records changes to the OS itself: a new area, a renamed folder, a new rule. Day-to-day notes don't go in it. Newest entry first, one heading per date:

```markdown
## 2026-10-20

* Set up this OS.
```

Don't create a `README.md`. A folder's listing is its `index.md`.

---

## 6. Folders and links

**A topic earns its own folder at three notes.** Until then, a note lives in the closest area, or at the top of the OS if nothing fits. When a third note on one topic arrives, make the folder, move the notes in, and update every listing and link that pointed at them.

**Links are relative.** From `house/faucet.md`, a link to `money/budget.md` is `../money/budget.md`. That way links work wherever the folder is opened: in a file browser, in Obsidian, or on GitHub.

**Moving or renaming a file means fixing every link to it in the same change.** Search for the old name and update each one. A broken link is a broken note.

---

## 7. When you write or edit a note

Every time:

1. Update `generated` with your actor and the current time.
2. If it's a new note, add it to its folder's `index.md`.
3. If you changed the description, update the listing that quotes it.
4. If a fact came from somewhere, add the source.
5. If something changed in the structure of the OS, add a line to `log.md`.
6. Before recording a fact, search the folder for other notes that state the same thing. If one disagrees, fix it if a newer, dated note makes clear which is right. Otherwise mark the conflict in both notes and tell the person.

---

## 8. "Check my OS"

When the person asks you to check the OS, read through every file and fix what breaks these rules. This is the health check from Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern, which this format comes from. Look for:

- Two notes that contradict each other, like different names for the same role or different dates for the same deadline. Flag them rather than picking one, unless a newer, dated note clearly settles it.
- A claim that a newer note has superseded, still stated as current somewhere else.
- A note without a header block, or without a `type`.
- A `status` other than `draft`, `stable`, or `deprecated`.
- A `generated.by` that doesn't match one of the three forms in §2.
- A footnote with no matching source, or a number with no source at all.
- A link that points at a file that doesn't exist.
- A file missing from its folder's `index.md`, or a listing that points at something gone.
- A `stale_after` date that has passed. Flag it rather than fixing it, because the person has to recheck the facts.
- A decision written as settled that the person never actually made. Mark it `draft` and tell them.
- A `verified` entry you or another agent wrote. Remove it and tell them.

Fix what you can, then tell the person in a few lines what you fixed and what needs them.

If they use a terminal, `scripts/check.sh` checks most of this automatically. You can run it yourself if you have a terminal. It doesn't replace reading, because it can't tell a guess from a decision.
