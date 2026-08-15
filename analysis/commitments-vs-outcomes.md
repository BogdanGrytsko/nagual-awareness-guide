# Commitments vs outcomes — does the frame produce change, or language about change?

The second standing question of this investigation, and in Yar's assessment the more important one. Companion to `frame-vs-evidence-log.md`, which asks whether the teaching can be corrected. This file asks whether the teaching *works*.

Status: **designed, not yet run.** Rules below are frozen deliberately, before any data is scored. Pilot scheduled for 2026-08-17.

## The question

> When an apprentice states that something will change, does the change appear in the record — or does the statement itself become the deliverable?

This is separate from the falsifier in the other file, and it can come out in the apprenticeship's favour while the falsifier stays unanswered. Those are compatible results: a system can be bad at correcting itself and still be good at making people act. If that is what the data says, that is what gets written down.

## Why it is now measurable

It was hard to quantify by recollection because memory keeps the vivid cases in both directions. It is tractable now because the archive is local and complete, and because commitments and outcomes are both **dated and written**:

| Year | Essay PDFs in the apprentice group | Chat messages | Distinct senders |
|------|-----|--------|-----|
| 2020 | 4 | 1,573 | 9 |
| 2021 | 123 | 5,960 | 27 |
| 2022 | 249 | 6,223 | 19 |
| 2023 | 266 | 5,754 | 19 |
| 2024 | 430 | 6,246 | 16 |
| 2025 | 454 | 5,923 | 15 |
| 2026 | 193 | 2,930 | 12 |
| **Total** | **1,719** (31 senders) | **34,609** (1.31M words) | |

Essays are attachments, so they do not appear as text in a chat export — `scripts/tg_docs.py` lists and downloads them. At roughly a thousand words each the essay corpus is ~1.7M words, so the full record is ~3M words. Availability is not the constraint; extraction is.

## Unit of analysis: the commitment

A first-person statement, dated, with an action specific enough that its absence would be visible. Three kinds, and **the ratio between them is itself a result**:

- **A — self-initiated.** The apprentice decides. *"I will watch two masterclasses per week until I've caught up."*
- **B — assigned.** A task, deadline, amount or penalty set by the teacher.
- **C — assent.** Agreement with a standard, or an insight named, **with no action attached.** The type specimen is holt's essay of 2025-09-03 concluding that a gift of 5–10% of total wealth "absolutely feel[s] like an adequate gift", after relabelling his own "way too much" reaction as fear of giving. This is the language bucket, and it is the thing the question is really about.

## Evidence tiers

Necessary because the archive rewards *reporting*: missed essays carry a £200 penalty (2025-09-01), so "reported doing it" partly measures compliance rather than change.

- **Tier A — externally anchored, hard to fake.** Job left, country moved, army training completed, business revenue, relationship ended, belt earned, apartment rented out.
- **Tier B — repeated specific reports over months.** wren's gifting cadence sustained for over a year, including a self-imposed £100 penalty when late.
- **Tier C — single self-report.**
- **Tier D — assent or insight with no action.**

A finding of "mostly Tier A/B, kept" is strong evidence for the apprenticeship. A finding of "mostly Tier D" is the answer this question was asked to detect.

## Scoring buckets

`kept` · `partly` · `abandoned` · `reframed` · `unknown`

`reframed` is its own bucket for the pattern already documented in the other file: the commitment reappears later as a fresh insight or a newly-named defect, with the original action never performed and never mentioned.

## Rules, frozen before scoring

1. **Pre-register.** Extract *every* commitment in the window and commit the frozen list to git **before** looking at a single outcome. Without this, selection does the work and the number means nothing.
2. **`unknown` is a real bucket and gets reported.** Silence is not failure — habits stop being reported — and not success. If `unknown` dominates, the honest finding is "not measurable from text", published as such, with no number attached.
3. **Yar's own commitments are in the list, scored by the same rule.** Including *"from now on - ask for people's names after a small talk, remember them (90%)"* (2025-08-31).
4. **Score the leavers.** 27 people posted in 2021; 6 of them still posted in 2026. Judging the apprenticeship on current members measures the ~22% who stayed. The leavers' commitments are in the archive and are the half of the evidence nobody inside the group can see.
5. **Two independent passes**, differently framed. Disagreements are read by hand, not averaged.
6. **Score outcomes by searching for the action, not by reading the person's later self-assessment first.** Their verdict on themselves is data about the frame, not evidence about the action.

## Confounders, named in advance

- **Reporting incentive.** Penalties for missing essays, and public praise for reporting tasks. Inflates `kept` at Tiers C–D.
- **Survivorship.** See rule 4.
- **Calls and masterclasses are invisible.** Most teaching happens there; several essays are an apprentice's filtered summary of a call. Commitments made verbally are absent, so the sample skews toward what people chose to write.
- **The analyst was invited by a member.** Yar set the standard for this work himself — honesty over agreement — and the pre-registration rule exists to keep that from depending on anyone's good intentions, including mine.

## Seed cases (already found, to be re-scored under the frozen rules)

| Who | Date | Commitment | Kind | Tier | Provisional |
|---|---|---|---|---|---|
| holt | 2025-09-03 | 5–10% of total wealth is an adequate gift | C | D | `abandoned` — subsequent gifts were tools for workmates and a €150 dinner; gap never noticed by anyone |
| wren | 2024–2025 | gifting task every 30–60 days | B | B | `kept` — sustained over a year, self-penalised when late, made junior instructor |
| yar | 2025-08-31 | ask people's names after small talk, 90% | A | C | `partly` — one dated instance a week later (remembered a name at BJJ) |
| vela | 2025-08-29 | two masterclasses per week until caught up | A | C | `unknown` — no follow-up found yet |
| rook | 2025-08-31 | "I CHANGE NOW" — read others' essays, give more than he takes | A | D | open |
| tove | 2025-09-02 | leave the apprenticeship if the essay pattern repeated | A | A | `abandoned` — stayed, paid £400 in penalties, restated the commitment |
| fenn | 2025-08-19 | 97% successfully self-employed | — | A | outcome, not commitment — anchor case for what Tier A evidence looks like |

## Pilot before the full pass

| | Scope | Estimate |
|---|---|---|
| **Pilot** | 2024–2025, four people: yar, holt, wren, plus one leaver from the 2021–22 cohort to test whether leaver material is scoreable at all. ~880 essays available in window, sample ~150. | download and convert ~1h; extraction and two scoring passes a few hours |
| **Full** | 2020–2026, 31 senders, 1,719 essays | 1–2 days of batched passes — worth doing only if the pilot shows a signal *and* a tolerable `unknown` rate |

Extraction is two-stage: a cheap keyword prefilter for commitment language (*"I will"*, *"from now on"*, *"by <date>"*, *"no more"*, *"every day/week"*, *"I commit"*, *"I change now"*), then classification of the candidates into the fields above. The prefilter's recall gets checked by hand-reading one full month and counting what it missed.

## Pre-committed interpretation

Written now so the goalposts cannot move once the numbers exist.

- **High keep-rate at Tiers A/B** → the apprenticeship produces real change. The sealing critique then narrows to a much smaller claim: it protects the teaching from correction while still working on people.
- **Low keep-rate with heavy Tier D volume** → language substitutes for change, and the essay is the deliverable.
- **The diagnostic that separates "the method works" from "the group works":** do self-initiated (A) commitments outperform assigned (B) ones? If A ≫ B, people change themselves and the frame takes the credit. If B ≫ A, the teacher's pressure is doing real work — an uncomfortable result for the critique, and it should be reported just as plainly.

## Open decisions

- **D1 — pilot window.** Default above is 2024–2025 plus one 2021–22 leaver. The alternative is to centre the pilot on 2021–22, where the leavers are and where the roster turnover happened, at the cost of thinner essay coverage (123 and 249 essays vs 430 and 454).
- **D2 — pseudonyms.** `fenn` and `tove` are minted here; the remaining senders need aliases before any table names them.
