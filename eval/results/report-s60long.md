# Results, s60long

Generated 2026-10-21T09:00:44-07:00. Counts are raw, like 4 of 5, because the runs are too few for percentages to mean much.

## Floor

Context Claude Code uses before reading any note, from runs in an empty folder. Context figures below are reported above this floor.

- sonnet: 12206 tokens
- opus: not run

## Traps, sonnet

| Task | a-loose | b-rules | c-os |
|---|---|---|---|
| t1-price | 1 of 1 | 1 of 1 | 1 of 1 |
| t2-deadline | 2 of 3 | 3 of 3 | 3 of 3 |
| t3-insurance | 1 of 1 | 1 of 1 | 1 of 1 |
| t4-budget | 1 of 1 | 1 of 1 | 1 of 1 |
| t5-contact | 3 of 3 | 3 of 3 | 1 of 3 |
| t6-filing | 1 of 1 | 1 of 1 | 1 of 1 |
| t7-bills | 1 of 1 | 1 of 1 | 1 of 1 |

### Context and cost, sonnet

Medians per run, across all trap tasks.

| Version | Peak context above floor | Total input tokens | Files read | Model calls | Cost per run |
|---|---|---|---|---|---|
| a-loose | 9923 | 60831 | 3 | 4 | $0.157 |
| b-rules | 14862 | 80751 | 5 | 4 | $0.202 |
| c-os | 6346 | 62071 | 1 | 4 | $0.128 |

### Tokens per passing answer, sonnet

Total input tokens across a version's trap runs, divided by its passing answers.

- a-loose: 83029
- b-rules: 89055
- c-os: 82197

## Blind picks

| Task | Picked | Why |
|---|---|---|
| u1-status | a-loose | more structured and thorough. probably the okf one since it uses my name vs "your Name" |
| u2-week | a-loose | more clear and structured. |
| u3-reply | a-loose | looks like it had the actual correct date vs a guess. the dates are different so I don't know which to trust but 2 seems to have more supporting evidence and precision. |
| u4-admin | a-loose | better structure, focuses on the important parts. likely okf version |
| u5-rates | c-os | they are pretty close but it seemed more planned out. 2 feels more definitive and to the point. I think 1 is OKF |

c-os picked 1 times, a-loose 4 times.

## After 10 edits, sonnet

Each cell is passing histories out of histories run.

| Question | a-loose | b-rules | c-os | d-os-conventions |
|---|---|---|---|---|
| q1-price | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| q2-launch | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| q3-contact | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| q4-bills | 1 of 1 | 0 of 1 | 1 of 1 | 1 of 1 |
| q5-capacity | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| q6-rate | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| q7-retainer | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| q8-pages | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| q9-todo | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |

| Version | Cost of the 10 edits | Median total input per edit | Median total input per question |
|---|---|---|---|
| a-loose | $1.17 per history | 79828 | 75607 |
| b-rules | $1.28 per history | 76492 | 97575 |
| c-os | $2.56 per history | 122314 | 56189 |
| d-os-conventions | $3.03 per history | 150202 | 57205 |

Mentions of superseded values left in the folder after the edits. This counts legitimate history too, like "moved from 2026-12-05," so read it as a rough signal.

- a/h1: old launch dates 2, $4,000 3, Dana as main contact 0, renew insurance 1, $95 1, 5 pages 2
- c/h1: old launch dates 6, $4,000 2, Dana as main contact 0, renew insurance 1, $95 4, 5 pages 4
- d/h1: old launch dates 6, $4,000 1, Dana as main contact 0, renew insurance 0, $95 4, 5 pages 3
- b/h1: old launch dates 4, $4,000 3, Dana as main contact 0, renew insurance 1, $95 1, 5 pages 2

## Spend

$39.86 across 167 runs and their grading.
