# anything-os

A folder of plain notes that your AI agent keeps up for you. You answer 8 questions, and it builds an OS shaped around your actual week.

## Why bother

Your agent starts every conversation knowing nothing. Whatever you told it last week is gone unless it's written down somewhere it can find.

A folder of notes fixes that, until the agent starts treating a guess as a fact. A note doesn't say whether "we're going with the blue one" was decided or just mentioned once. Repeat it three times and it reads as settled.

So this template is mostly rules, plus just enough structure to follow them:

- Don't invent facts or numbers. A gap says it's a gap and what would fill it.
- A guess stays marked as a guess until you decide it.
- Only you can mark something as confirmed.
- Every number says where it came from.

Keeping the notes tidy is the part people give up on. It's also the part an agent does well, as long as the rules say exactly what tidy means.

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
