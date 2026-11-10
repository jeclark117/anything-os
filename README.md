# anything-os

anything-os is a personal OS: a memory your AI agent keeps up for you. It's a folder of plain notes on your computer, organized around your work or your life.

You answer 8 questions about your week, and the agent builds a small starting version. After that, you just talk to it.

It writes down what matters as you go. When something changes, it fixes the old note instead of adding a second one that disagrees. Beyond your AI tool, there's nothing to install.

## What you end up with

- A folder for each area of your life or work, in your words.
- An instruction file telling your agent who you are, what's private, and how you like to work.
- One real note about something you're working on now.
- Three phrases to grow it: "make a note about...", "add an area for...", and "check my OS."

It starts small on purpose and grows as you ask for things. The [examples](examples/) folder shows three finished versions: a household, a one-person business, and a garden.

Your agent follows a few rules in every note:

- Don't invent facts or numbers. A gap says it's a gap and what would fill it.
- A guess stays marked as a guess until you decide it.
- Only you can mark a note as confirmed. Tell your agent you've checked it, and it records that you did.
- Every number says where it came from.

## Why it helps

Your agent starts every conversation knowing nothing. Whatever you told it last week is gone unless it's written down somewhere it can find.

Notes fix that, and for a while a messy folder works fine. The trouble comes as it grows. Things change, the old line stays where it was, and the agent repeats it as if it's still true.

It doesn't warn you, either. A wrong answer sounds just as sure of itself as a right one.

In a blind test, I read two answers to each question without knowing which folder each came from. Three of the pairs had one answer built on an outdated date. I picked the wrong one all three times, because it looked more thorough.

I tested this on 200 notes of about 1,300 words each. An agent reading a loose folder got 173 of 190 answers right. Reading this template, it got 188.

The difference is when the old line gets fixed. Here, the agent corrects it as soon as the new fact arrives, so there's nothing stale left to repeat.

If you keep fewer than about 60 notes, you probably don't need this. At that size, Claude Sonnet got every answer right from loose notes, even after 10 rounds of changes.

## Getting started

1. Click **Use this template**, or download the zip from the **Code** button.
2. Open the folder in your AI tool. Claude's desktop app (Cowork) and Claude Code both work.
3. Say: "Read START.md and set me up."

The questions are meant to take about 15 minutes. At the end, the agent shows you a plan and builds nothing until you approve it.

Already know what you want? Say "Read START.md and take the fast track." You answer everything in one message, or point it at the instruction file from an OS you already have.

You never need to touch the file formats. The agent handles that.

## How it was tested

Four rounds, on one made-up business, mostly one to three runs each. That shows the shape, not a precise measurement. It's all in [eval](eval/) if you want to check the work.

**Files stay true.** After 20 changes, the loose folders still stated 15 to 20 outdated facts as current. This one stated 2 to 6.

**A cleanup pass later isn't the same.** Run on the loose folders after 20 changes, the template's own cleanup brought them to about the same level. It can't fix the answers you already got before it ran.

**A smaller model can answer from it.** Haiku 4.5, Claude's smallest model, got 84 of 95 answers right reading this template, about the same as Sonnet on loose notes. Reading loose notes, Haiku got 54. Keep the upkeep on a bigger model, though: asked to check the notes, Haiku missed what was stale.

**The upkeep costs a little.** Recording a change costs about $0.17 more than in a loose folder, on Sonnet 5.5 at list price. That pays off if you ask several things in one conversation, and not if you ask one thing and leave.

## What it works with

Built for Claude. OpenAI's tools should work, because setup writes an `AGENTS.md` for them, but nobody has tested that yet. If you try it, I'd like to hear how it went.

[Obsidian](https://obsidian.md) is a nice way to read the folder. It's optional.

## Where it comes from

The idea is Andrej Karpathy's [LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). An agent keeps a folder of notes current, rather than digging through raw files every time. The file format is Google Cloud's [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format) (OKF), which [formalizes](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) that pattern.

The rest is mine. I run three of these, for work and for home, and this template is what held up. That's the onboarding, the rules your agent follows, and the testing behind them.

The testing ran four rounds, plus a live setup with someone who'd never used one. The template changed because of what they found. Two of the rules came from Anthropic's [research on agent memory](https://www.anthropic.com/research/components-of-agent-memory).

I'm Joseph Clark. I build AI systems.

If you set one up, open an issue and tell me what the onboarding got wrong.

– Joseph

MIT licensed. See [LICENSE](LICENSE).
