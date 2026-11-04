# Private calls

`yar`'s own one-to-one calls with the Nagual, taken from unlisted recordings on the channel
"The Toltec Apprentice". A second apprentice is often on the same call.

## Files

- `call-<NN>-<YYYY-MM-DD>-<part>of<total>.txt`: the cleaned transcript, one caption line per
  row, each prefixed with `[hh:mm:ss]`.
- `...-by-minute.txt`: the same text grouped into one paragraph per minute, for reading.

## Evidence tier

These are **auto-generated YouTube captions**, cleaned with `scripts/clean_vtt.py` but not
hand-checked. Names come out garbled, and speaker turns are marked only by `>>`. Quote with a
`[call NN, hh:mm:ss]` tag. Treat this as below hand-transcribed essays in reliability.

## Aliases

Names are replaced at processing time by `scripts/process_call.py`, which holds the table:

- Apprentices get the repo's aliases: `[fenn]`, `[dell]`, `[tove]`, `[wren]`, `[holt]`, `[rook]`,
  `[vela]`, `[sable]`. `[kesh?]` marks an identification that is likely but unconfirmed.
- Family and private people: `[yar's wife]`, `[the teacher's wife]`, `[friend]`, `[a friend]`,
  `[a friend's child]`.
- `[name]`: someone named in passing whose identity is not established.
- Public figures (authors, comedians, course sellers) are left as captioned.

Captions garble names, so after processing a new call, grep it for capitalised words that are not
in the table before committing. Everything else is verbatim caption text.

## Redactions

Agreed with `yar` on 2026-11-04 and applied by `scripts/process_call.py`. A redacted span shows
as one line, `[hh:mm:ss] [redacted: …]`. Money figures appear as `[amount]`. Current
redactions: family medical (call 73), `[fenn]`'s finances (calls 71 and 74), tax and
money-handling details (call 71), third parties' finances (call 71).

## Index

| # | date | part | length | topics |
|---|---|---|---|---|
| 71 | 2026-08-08 | 3/8 | 2:38:48 | yar's game demo and market research; "carry on" on the course plan; fenn's savings and tax (redacted in part) |
| 72 | 2026-08-24 | 4/8 | 2:01:55 | fenn's tour script and tips; gender-roles video with yar's wife; "men protect women" corrected |
| 73 | 2026-09-05* | 5/8 | 2:09:01 | yar's son and presence; fenn's diet and coffee; [wren]'s Glastonbury visit; invitations and energy |
| 74 | 2026-09-17 | 6/8 | 2:37:06 | fenn's money and adviser; credit for fenn's boundary; yar's invitations; the game-marketing dispute |
| 75 | 2026-10-02 | 7/8 | 2:04:16 | fenn's dependency on calls ("fly your own kite"); fenn's comedy group; yar's boxing coach; wife, dogs, Happy Wife School |
| 76 | 2026-10-25 | 8/8 | 2:08:01 | blue belt; feeling; the slapping; parenting; "apprenticeship 2.0" and weekly calls; spiritual-framework homework |
| 77 | 2026-11-04 | 1/8 | 2:37:30 | call 76 homework not started; the essay dispute; Old Testament sampling; "you need weekly" |

Dates are YouTube upload dates. \*Call 73 was probably recorded on Thursday 2026-09-03: `[fenn]`
says "today is… Thursday".

Video IDs, for re-fetching: 71 `vWL0bZZn-mo`, 72 `SG3W1HPDd9k`, 73 `EKOeCVzK6J8`, 74 `ZzsYu1ISEeU`, 75 `He9GWW6VIWk`,
76 `XQGXFBB3-4w`, 77 `3cgI76jN5LE`.

To process a call: fetch the `en-orig` VTT with yt-dlp into `tg-private/personal-calls/`, run
`python -I scripts/process_call.py <vtt> private-calls/call-NN-YYYY-MM-DD-XofY`, then grep for
names that were missed.
