# Results, s60

Generated 2026-10-20T19:33:43-07:00. Counts are raw, like 4 of 5, because the runs are too few for percentages to mean much.

## Floor

Context Claude Code uses before reading any note, from runs in an empty folder. Context figures below are reported above this floor.

- sonnet: 12206 tokens
- opus: not run

## Traps, sonnet

| Task | a-loose | b-rules | c-os |
|---|---|---|---|
| t1-price | 1 of 1 | 1 of 1 | 1 of 1 |
| t2-deadline | 1 of 1 | 1 of 1 | 1 of 1 |
| t3-insurance | 1 of 1 | 1 of 1 | 1 of 1 |
| t4-budget | 1 of 1 | 1 of 1 | 1 of 1 |
| t5-contact | 1 of 1 | 1 of 1 | 1 of 1 |
| t6-filing | 1 of 1 | 1 of 1 | 1 of 1 |
| t7-bills | 1 of 1 | 1 of 1 | 1 of 1 |

### Context and cost, sonnet

Medians per run, across all trap tasks.

| Version | Peak context above floor | Total input tokens | Files read | Model calls | Cost per run |
|---|---|---|---|---|---|
| a-loose | 2689 | 41314 | 4 | 3 | $0.100 |
| b-rules | 2845 | 41339 | 4 | 3 | $0.099 |
| c-os | 3298 | 57230 | 3 | 4 | $0.106 |

### Tokens per passing answer, sonnet

Total input tokens across a version's trap runs, divided by its passing answers.

- a-loose: 47116
- b-rules: 43807
- c-os: 56228

## After 10 edits, sonnet

Each cell is passing histories out of histories run.

| Question | a-loose | b-rules | c-os |
|---|---|---|---|
| q1-price | 1 of 1 | 1 of 1 | 1 of 1 |
| q2-launch | 1 of 1 | 1 of 1 | 1 of 1 |
| q3-contact | 1 of 1 | 1 of 1 | 1 of 1 |
| q4-bills | 1 of 1 | 1 of 1 | 1 of 1 |
| q5-capacity | 1 of 1 | 1 of 1 | 1 of 1 |
| q6-rate | 1 of 1 | 1 of 1 | 1 of 1 |
| q7-retainer | 1 of 1 | 1 of 1 | 1 of 1 |
| q8-pages | 1 of 1 | 1 of 1 | 1 of 1 |
| q9-todo | 1 of 1 | 1 of 1 | 1 of 1 |

| Version | Cost of the 10 edits | Median total input per edit | Median total input per question |
|---|---|---|---|
| a-loose | $0.61 per history | 63092 | 41718 |
| b-rules | $0.66 per history | 57550 | 42519 |
| c-os | $1.43 per history | 82382 | 44234 |

Mentions of superseded values left in the folder after the edits. This counts legitimate history too, like "moved from 2026-12-05," so read it as a rough signal.

- a/h1: old launch dates 2, $4,000 3, Dana as main contact 0, renew insurance 1, $95 1, 5 pages 2
- c/h1: old launch dates 6, $4,000 2, Dana as main contact 0, renew insurance 0, $95 2, 5 pages 3
- b/h1: old launch dates 5, $4,000 4, Dana as main contact 0, renew insurance 1, $95 2, 5 pages 2

## Spend

$9.56 across 78 runs and their grading.
