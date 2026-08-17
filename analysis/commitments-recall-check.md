# Recall check — how much did the extraction actually catch?

Required by rule "the prefilter's recall gets checked by hand-reading one full month and
counting what it missed" in `commitments-vs-outcomes.md`. Run 2026-08-17, immediately after
the first scoring pass, because that pass produced a headline claim that the method might
not have been able to support.

## Why this month

**2022-04.** Chosen adversarially, not conveniently: it is the **largest essay month in the
whole window** (41 essays, 40,367 words, plus 713 chat messages) and the frozen register
found only **3** commitments in it. If the instrument is weak anywhere it is weakest here.
Picking the month where my own method looks worst is the only version of this test worth
running.

All 41 essays were read end to end.

## Result: recall is about 27%

| | n |
|---|---|
| commitments found by hand in 2022-04 | 11 |
| commitments in the frozen register for 2022-04 | 3 |
| **recall** | **~27%** |

So **the frozen register is a ~1-in-4 sample, not a census.** The true commitment
population in 2021–22 is plausibly 300–400, not 115. Every absolute count in
`commitments-2021-22-frozen.md` and `commitments-2021-22-scored.md` has to be read that way.

## Where the failures are, precisely

Of the 8 missed, the failure was **not** mostly the keyword prefilter:

| failure mode | n | what it looked like |
|---|---|---|
| in the candidate pool, but banded `low`/`reject` so never hand-read | 4 | `sena` "I will send it out with blessings" (score 3); `gale` "which I'll start getting tea there now" (score 1); `fenn` "every time I interrupt the silence with a yes, I will do my very best" (3); `wynn` "I will not leave the sessions in tears" (3) |
| in the pool, in the `mid` band, read by me, and not selected | 1 | `fenn` "I will roll a cigarette now, and I will smoke it… [Last one.]" — a dated cessation claim I read and passed over |
| **never entered the candidate pool at all** | 3 | `gale` "I was gifted the ghost task"; `dov` "I was given an ultimatum to get it done before I could continue in my apprenticeship"; `mira` "I have come to the decision to not pursue Kukuwa" |

The band cutoff, not the keyword list, is the main leak. My scoring function rewarded
volition + concreteness + deadline and penalised hypotheticals, and a real commitment
phrased plainly and briefly ("I will not leave the sessions in tears") scores 3 and falls
below the line.

## The two claims this invalidates

### 1. "`reframed` never fired" — RETRACTED

That was the strongest pro-apprenticeship statement in the scored file, and it was an
artifact of the instrument. **`reframed` fired in this very month, and the method could not
see it.**

`mira` had committed to becoming a Kukuwa instructor — told the teacher, said so in an
essay, and spent money on a CPR/First Aid certificate towards it. On 2022-03-26 she appends
one line to an essay share: *"contrary to my claims at the time of writing these
reflections, my KUKUWA ambitions have been placed on an indefinite pause 😂."* Then in her
essay of 2022-04-17 the abandonment is converted into a gain:

> "I have come to the decision to not pursue Kukuwa… The mind had several ammunitions to
> lob, such as; I had already told the Nagual that I would become a Kukuwa instructor, I
> couldn't back down – it would demonstrate my weak will/indecisiveness. I had even spent
> money to obtain a CPR/First Aid Certificate towards this end. I had made declarations in
> my essay already… Had I listened to the rationalities of the mind; I would have missed a
> golden opportunity to immerse myself into Breathwork. What a wonderful lesson… **Thank
> you Nagual Anaam, for your words during a recent call that offered the gateway to give
> myself permission to be who I don't want to be.**"

That is the textbook shape: the commitment is dropped, the reasons for keeping it are
relabelled as machine-mind "ammunitions", and the drop is reissued as a lesson and a
permission granted by the teacher. Two further details complete it:

- **The replacement was abandoned too.** Breathwork was the stated golden opportunity.
  After April 2022, **the word "breathwork" never appears from her again** in the archive.
- **Nobody ever asked.** "Kukuwa" appears many times afterwards, always about `sena`'s
  classes. Neither the dropped instructor plan nor the vanished Breathwork is ever raised
  by anyone, including the teacher, in the remaining 16 months before she was removed.

Why the method was blind: `reframed` is not detectable by searching for commitment
language, because a reframe **contains no commitment**. It is a decision *not* to, phrased
as an insight. Any instrument built to find "I will" is structurally incapable of finding
it. Detecting `reframed` requires starting from a known earlier commitment and reading
forward — which is exactly what scoring does, and which is why the one case surfaced during
scoring rather than extraction.

**Corrected position: `reframed` is not measurable at all by the current method, and the
one case found by hand is a clean instance.** The honest bucket for it in the scored file
is not `0` but `not measurable`.

### 2. "Only 4 of 115 are teacher-assigned, because assignment happens on the calls" — WRONG

I wrote that the low B count reflected assignments happening on unrecorded calls. Two of
this month's three prefilter-blind misses are **written assignments**:

- `gale`: *"Recently I was gifted the ghost task — to behave as if I am hunted at all times,
  to leave no trace in my physical space, as would a ghost."*
- `dov`: an Ayahuasca ceremony task with **escalating parameters** (within a 6-hour drive →
  anywhere in the US → a 7-day retreat in Mexico) and finally *"I was given an ultimatum to
  get it done before I could continue in my apprenticeship."* He paid the deposit.

Assignments are written down constantly; they are just phrased as *"I was given / I was
tasked / Nagual Anaam asked me to / my task is"* — none of which my patterns match. In the
2021–22 window **55 chat messages** use that phrasing. Many are innocuous ("Nagual asked me
to share this essay"), but real tasks are in there (a song `arlo` was tasked to make, a
CC-books search `orin` was set).

**Corrected position: the A:B ratio in the frozen register is an artifact of the pattern
list and says nothing about how much the teacher assigns.** The diagnostic in the design
file — do self-initiated commitments outperform assigned ones? — remains unanswered, and
answering it needs an assignment-phrasing pass that has not been run.

## What survives

The bucket *proportions* among Tier A commitments are probably still indicative, because
the misses are not obviously biased toward kept or abandoned outcomes — of the 8 missed,
by later evidence roughly half were kept (`gale`'s tea switch is never contradicted;
`dov` paid the deposit and went) and half were not (`fenn`'s "last one" cigarette; his
yes-is-yes promise). What does not survive is any absolute count, the A:B ratio, and the
`reframed` zero.

## Fix list, for the next pass

1. **Lower the band cutoff to score ≥ 2 and hand-read the `low` band.** That alone recovers
   4 of the 8 misses. Cost: ~975 more candidates in the window.
2. **Add an assignment-phrasing pass**: `I was given|gifted|tasked|assigned|told to`,
   `my task is|was`, `Nagual (Anaam) asked/told me`, `ultimatum`. This is the only way B
   gets counted honestly.
3. **Detect `reframed` from the other end.** For each frozen commitment, search the person's
   later material for the *topic* rather than for commitment language, and read for whether
   the action or the framing changed. The `mira` case shows the tell: a retraction posted as
   a light aside, then a later essay converting it into a lesson.
4. **Do not report a bucket as zero when the instrument cannot see it.** Report
   `not measurable`.
