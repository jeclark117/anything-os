# anything-os

A folder of plain notes that your AI agent keeps up for you. You answer 8 questions, and it builds an OS shaped around your actual week.

## Why bother

Once you have a lot of notes, a loose folder starts giving you wrong answers, and nothing tells you.

On 200 notes of about 1,300 words each, an agent reading loose notes got 173 of 190 answers right. Reading this template, it got 188.

Almost every miss was an old fact repeated as current. The update was buried in a long note, or missing from a plan the agent had saved earlier.

Nothing in those answers looked wrong. In an earlier round, I compared answers blind and picked the wrong one every time it was wrong.

At 60 notes or fewer, you probably don't need this. Sonnet got every answer right from loose notes at that size, even after 10 rounds of changes.

The difference is when the old line gets fixed. This template has the agent correct it as soon as the new fact arrives. A loose folder keeps both, and the agent has to work out which is current every time it reads.

After 20 changes, the loose folders still stated 15 to 20 outdated facts as current. This one stated 2 to 6.

It gets there with a few rules:

- Don't invent facts or numbers. A gap says it's a gap and what would fill it.
- A guess stays marked as a guess until you decide it.
- Only you can mark something as confirmed.
- Every number says where it came from.

A cleanup pass afterward helps, and the template has one. Run on the loose folders after those 20 changes, it brought them to about the same level. It can't fix the answers you already got before it ran, and that's where loose notes went wrong.

It also lets a cheaper model do the job. Haiku 4.5, Claude's smallest model, got 84 of 95 answers right on this template. Sonnet on loose notes got 83, and cost about five times as much per question.

The upkeep costs a little. Recording a change costs about $0.17 more than in a loose folder, on Sonnet at list price. That pays off if you ask several things in one conversation, and not if you ask one thing and leave.

That's four rounds of testing on one made-up business, mostly one to three runs each. It shows the shape, not a precise measurement. It's all in [eval](eval/) if you want to check the work.

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
