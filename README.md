# anything-os

A folder of plain notes that your AI agent keeps up for you. You answer 8 questions, and it builds an OS shaped around your actual week.

## Why bother

Your agent starts every conversation knowing nothing. Whatever you told it last week is gone unless it's written down somewhere it can find.

A folder of notes fixes that, and a good model reads a messy one surprisingly well. In testing, Sonnet answered every question right from loose notes, even after 10 rounds of changes.

What a loose folder doesn't do is stay true. After those 10 changes, both loose to-do lists still said to renew insurance that was already paid. The model worked around it every time. You won't, when you open the file yourself.

The fix is an agent that corrects the old line instead of adding a new one. This template gets there with a few rules and just enough structure:

- Don't invent facts or numbers. A gap says it's a gap and what would fill it.
- A guess stays marked as a guess until you decide it.
- Only you can mark something as confirmed.
- Every number says where it came from.

The upkeep isn't free. In the same test, each change cost about twice as much to record. What you get for it is files you can trust when you open them.

That's one test, on made-up notes. It's all in [eval](eval/) if you want to check the work.

## Getting started

1. Click **Use this template**, or download the zip from the **Code** button.
2. Open the folder in your AI tool. Claude's desktop app (Cowork) and Claude Code both work.
3. Say: "Read START.md and set me up."

The questions are meant to take about 15 minutes. At the end, the agent shows you a plan and builds nothing until you approve it.

You never need to touch the file formats. The agent handles that.

## What you end up with

- A folder for each area of your life or work, in your words.
- An instruction file telling your agent who you are, what's private, and how you like to work.
- One real note about something you're working on now.
- Three phrases to grow it: "make a note about...", "add an area for...", and "check my OS."

The [examples](examples/) folder shows three finished versions: a household, a one-person business, and a garden.

## What it works with

Built for Claude. OpenAI's tools should work, because setup writes an `AGENTS.md` for them, but nobody has tested that yet. If you try it, I'd like to hear how it went.

[Obsidian](https://obsidian.md) is a nice way to read the folder. It's optional.

## Where it comes from

The format is the [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format) (OKF) from Google Cloud, which [formalizes](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) Andrej Karpathy's [LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) pattern. The onboarding and the rules are mine, from running two of these for my own work and home.

I'm Joseph Clark. I build AI systems for businesses at [Enreverix](https://enreverix.com).

If you set one up, open an issue and tell me what the onboarding got wrong.

– Joseph

MIT licensed. See [LICENSE](LICENSE).
