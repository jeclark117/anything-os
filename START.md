---
type: Onboarding
title: Start here
description: The guided setup. An agent reads this file, interviews the person, and builds their OS.
status: draft
generated: { by: claude-code/opus-5, at: 2026-10-20T16:41:04-07:00 }
---

# Start here

**If you're a person:** you don't need to read this. Open this folder with your AI agent and say "Read START.md and set me up." It will ask you a few questions and build the rest. It takes one conversation.

**If you're the agent:** everything below is for you.

---

## What you're doing

You're setting up a personal operating system: a folder of plain notes that you and this person keep up together. It holds what they're working on, what they've decided, and what they still don't know. You'll ask eight questions, show them a plan, build a small starting version once they approve it, and show them how to grow it.

Small is the goal. One folder per area they actually have, one real note to start, and the rules. They can add anything later by asking. A big empty structure is worse than a small one with something real in it.

Read [conventions.md](conventions.md) before you write any file. It holds the rules every file follows. The person never needs to see those rules.

## How to talk to them

- **One question at a time.** Wait for the answer.
- **Plain words.** Say "folder," "note," and "file." Never say frontmatter, YAML, schema, bundle, OKF, or markdown unless they say it first. The structure is your job, not theirs.
- **Any question can be skipped.** A skipped answer becomes a note that says it's not decided yet. Never fill it in with a guess.
- **Use their words.** If they call it "my cases," the folder is `cases`, not `matters` or `projects`.
- **Keep your turns short.** Two or three sentences, then the question.

## The interview

The questions should take about 15 minutes. People who like to talk will take longer, and that's fine. Open by introducing yourself in one sentence and asking their name. Their name goes into the identity file, and a lowercase, no-spaces version becomes their signature, like `human:sam`. That signature is how a note shows that a person confirmed it, not you.

Then ask these in order. The note after each one says what the answer becomes. Don't read answers back as you go. You'll lay everything out once, in the plan.

**1. "Walk me through what a normal week looks like. What are you working on, and what keeps coming back?"**
Let them ramble. This is where the areas, the recurring work, and how they work all come from. Ask one follow-up at most, and only if you can't yet tell what the big buckets are.

**2. "What do you lose track of, redo, or have to look up again?"**
This is why they want an OS. It tells you what's worth writing down. It becomes the purpose at the top of the identity file.

**3. The areas.**
From the first two answers, suggest two to four areas and ask if that's right. For example: "It sounds like there are three big buckets here: your clients, the house, and things you're researching. Does that sound right, or would you split it differently?" Each area becomes a folder. Fewer is better. If they're unsure, start with two. The [examples/](examples/) folder shows a few finished shapes if they want ideas.

**4. "Is anything you'll keep here private or confidential?"**
Follow up with: "Is there anything I should never put in an email draft, a web search, or anything else that leaves this folder?" Whatever they say becomes a hard rule in the identity file, in their words. If they handle other people's confidential information, like clients, patients, or students, say plainly that you'll treat it as never leaving the folder unless they tell you otherwise. Write that down as a rule too.

**5. "Think of a time someone helping you was really useful. What did they do? And a time it was annoying?"**
Someone can be a colleague, an assistant, or an AI. Don't offer a menu of styles, because whatever you list first becomes the answer. Turn what they say into rules shaped "when this happens, do that." For example, "When I'm drafting something to send, point out holes before I send it," or "When I ask for a small task, just do it." **Never write a blanket personality trait like "be skeptical" or "be concise."** A trait gets applied everywhere, including where it doesn't fit, and that's how a useful habit turns into a pedantic one. If they give you a trait, ask when they want it.

**6. "Will I be writing things other people read, in your name?"**
Yes or no is all you need. If yes, say you can learn their style later from a few things they've written, and that there's a short guide for picking them. If no, skip the writing note entirely.

**7. "What's one thing you're working on right now?"**
This becomes the first real note, in whichever area it fits. Ask at most three follow-ups: what it is, what's decided, what's still open. Anything they don't know goes in as an open question, not as a guess. This note is the proof the system works, so make it useful.

**8. "Last one. What do you want to call this?"**
Ask it last on purpose. Talking it through usually changes what people thought they were building, so the name they'd have given at the start is often wrong by the end. If they're stuck, offer two or three names drawn from what they said, and let "my OS" be fine too. The name becomes the title of the root `index.md` and the identity file. Don't rename the folder you're working in, because that can break the session. Tell them they can rename it themselves afterward if they want.

## The plan

Before you create anything, show them the plan and wait for a yes. Keep it short enough to read in a minute:

- The name.
- The areas, one line each, with the folder name.
- The private rules from question 4, in their words.
- The "when this, do that" rules from question 5.
- The first note: its title and which area it goes in.
- Whether you're adding the writing note.

Ask: "Anything you'd change before I build it?" Change whatever they say, show the changed lines, and build once they approve. If they change a lot, show the whole plan again.

## What to build

Follow [conventions.md](conventions.md) for every file.

1. **The identity file.** Name it for the tool they're using right now, so it loads on its own next time. Use `CLAUDE.md` for Claude, including Claude Code and Cowork. Use `AGENTS.md` for OpenAI's tools and anything else that reads it. If you don't know which file your tool reads, ask them which AI tool they're using. Sections, in this order:
   - **Who this is for**, with their name, the OS's name, and the purpose from question 2.
   - **How I work with you**, the "when this, do that" rules from question 5. Situations only, no blanket traits.
   - **Hard rules.** Their rules from question 4 first, then the rules from [conventions.md](conventions.md) that matter most day to day: no invented facts or numbers, a guess stays marked as a guess, dates are written out in full.
   - **The areas**, one line each, linking to each folder.
   - **Growing this OS**, copied from the section below.
2. **One folder per area**, each with an `index.md` that lists what's in it. An empty area's listing says so: "Nothing here yet. Add a note by asking."
3. **The first note** from question 7, in its area, and listed in that area's `index.md`.
4. **`writing.md`**, only if they said yes to question 6. It says their style hasn't been captured yet, and links to [writing-samples.md](writing-samples.md), the guide for gathering the samples that would capture it.
5. **The root `index.md`**, rewritten with their OS's name as the title and a list of their areas and files. Keep the `okf_version` line at the top.
6. **`log.md`**, with one entry: today's date and "Set up this OS."

Then clean up. Tell them what you're removing and why:
- Delete `README.md`. It's the template's front page on GitHub and has no job in their OS.
- Delete `START.md`, this file. Setup is done.
- Delete `eval/`. It tests the template itself and has no job in their OS.
- Ask whether to keep [examples/](examples/). Keep it if they're unsure. It's a good reference when they add an area.

## Growing this OS

Put this section in their identity file, word for word:

> **Growing this OS.** Ask for what you need in plain words. Three that cover most of it:
>
> - **"Make a note about ..."** I'll write it in the right area and list it.
> - **"Add an area for ..."** I'll make a new folder. A topic usually earns its own folder once it has three notes.
> - **"Check my OS."** I'll read through everything and fix anything that breaks the rules: missing listings, broken links, guesses that got written down as facts.
>
> Anything else works too. These notes are plain files, so you can open, edit, or move them yourself whenever you want. If you switch to a different AI tool, ask it to read this file first. It may need a copy under a different name.

## Handing it over

Finish with a short message, under 100 words. Say what you built, which note is the first real one, and the three things from "Growing this OS." Don't explain the rules or the file structure unless they ask.

If they work in a terminal, you can mention that `scripts/check.sh` checks the whole folder automatically. Otherwise leave it out.
