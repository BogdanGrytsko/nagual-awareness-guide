"""Write the FROZEN 2021-22 commitment register.

Takes my hand-classification of the ranked candidates (the SELECTION table below,
keyed by the index in the date-sorted high+mid band) and emits both a JSONL for
later scoring and a markdown table for git.

No outcome field exists in the output on purpose. Per rule 1 in
analysis/commitments-vs-outcomes.md the list is committed BEFORE any outcome is
looked at, so that selection cannot do the work that the finding should do.

    py scripts/freeze_commitments.py --ranked tg-private/tmp/ranked-2021-22.jsonl \
        --jsonl tg-private/commitments-2021-22-frozen.jsonl \
        --md analysis/commitments-2021-22-frozen.md
"""
import argparse
import collections
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ALIAS = {
    "Asaya": "holt",
    "Steen": "fenn",
    "Derwen Lyava": "vela",
    "Kisha Bo": "orin",
    "SatiMa Ra": "sena",
    "David": "arlo",
    "Jewels": "kesh",
    "Avianna": "isla",
    "Brooke Sophia": "thea",
    "Jarrad Gould": "bram",
    "Will Turner Sanders": "gale",
    "Ian Minick": "hale",
    "Dean": "dov",
    "Brett": "rex",
    "Sila": "wren",
    "Ilona": "sable",
    "Yar": "yar",
    "674233980": "mira",
    "1731636219": "wynn",     # Gabrielle, joined 2021-07-30, removed 2022-10-06
    "1907051013": "pia",      # Carolin, joined 2021-07-22, removed 2022-02-23
    "1589462348": "juno",     # Talitha, added 2021-03-16, removed 2021-10-11
    "1548288276": "bode",     # unidentified man, added 2021-03-16, removed 2021-07-03
    "Nagual Anaam": "Nagual Anaam",   # not anonymised: already public in tnz-telegram/
}

# index -> (kind, tier, deadline, what would settle it)
# kind: A self-initiated | B assigned by the teacher | C assent, no action attached
# tier: A externally anchored | B repeated specific reports | C single self-report | D assent
SELECTION = {
    12:  ("B", "B", "ongoing from 2021-03-25", "count comments per essay in TAC before vs after this date"),
    15:  ("A", "C", None, "any later report of watchfulness at a named incident"),
    35:  ("A", "B", "daily from 2021-04-30", "forgiveness exercise named again in later essays/chat"),
    36:  ("A", "A", "2021-07-01", "kukuwa or tai chi practice reported on or before 1 Jul 2021"),
    39:  ("A", "C", None, "a named act of impeccability attributed to this decision"),
    40:  ("A", "A", None, "income statements after 2021-05-10"),
    46:  ("A", "B", "every morning", "morning rah-rah / walking affirmation reported again"),
    51:  ("A", "C", None, "a later instance of respect toward a named person"),
    53:  ("A", "C", None, "a status report following the essay"),
    55:  ("A", "B", "ongoing from 2021-06-24", "silent walking + EFT reported again before removal 2021-10-11"),
    61:  ("A", "C", "2021-07-05", "beach walk reported next day"),
    71:  ("A", "B", "daily from 2021-07-16", "10-min sit or 20-30 min walk reported again"),
    72:  ("A", "A", "from 2021-07-16", "sugar-free / keto reported sustained, or abandoned"),
    80:  ("A", "A", "unstated", "did every apprentice get a food-growing task? search all later tasking"),
    81:  ("A", "A", None, "any later mention of that drug"),
    91:  ("A", "C", None, "later reports of working at her own pace"),
    92:  ("A", "C", None, "later communication style, or feedback about it"),
    98:  ("A", "B", None, "knee training and return to kukuwa reported again"),
    99:  ("A", "C", None, "an MP4 actually posted"),
    103: ("A", "C", None, "knee-wobble omission mentioned again"),
    104: ("A", "A", "2021-09-30", "was a kukuwa video posted in TAC on/near 30 Sep 2021"),
    106: ("A", "C", None, "a report-back message on the findings"),
    108: ("A", "A", "2021-12-31", "groin/pubic pain status at and after 31 Dec 2021"),
    111: ("A", "B", None, "'I am here to train' appearing in her later affirmation reports"),
    112: ("A", "C", "2021-12-31 / 2022-03-10", "did he calendar it, and did he mention the dates when they arrived"),
    119: ("B", "C", "next call", "EFT on a call, reported by either party"),
    124: ("A", "A", "2021-11-30", "a move into a new home reported by 30 Nov 2021"),
    133: ("B", "A", "2021-10-16", "spell-check task, sent within 3 days of 13 Oct 2021"),
    135: ("A", "C", None, "the mirror exercise with her mother reported done"),
    138: ("A", "A", "from 2021-10-26", "working 75% confirmed in later messages"),
    140: ("A", "C", None, "did she tell them; any later mention of 24h payment"),
    144: ("A", "C", None, "typo awareness in later essays"),
    146: ("A", "A", "2022-09", "woodworking income at/after Sept 2022: 800 EUR/month or not"),
    148: ("A", "B", "daily from 2021-11-18", "the task reported run again"),
    151: ("A", "A", "stated as imminent", "did he move to Sweden, and when"),
    152: ("A", "C", "2021-12-10", "essay submitted the next day"),
    155: ("C", "D", None, "no action attached - the type specimen for the language bucket"),
    158: ("C", "D", None, "no action attached"),
    162: ("A", "B", "nightly from 2021-12-25", "sleep affirmation reported again"),
    166: ("A", "A", "from 2021-12-31", "fruit/vegetable/water intake reported sustained"),
    167: ("A", "A", "from 2021-12-31", "chai mentioned again after this date"),
    168: ("A", "A", "unstated", "listed on the KukuwaFitness website; first class; first full class"),
    169: ("A", "A", "2022-03-31", "the stated condition at 31 Mar 2022"),
    172: ("A", "C", None, "quantitative investing study reported again"),
    175: ("A", "A", "2022-03-31", "weight at end of March 2022 - 63kg from 70kg"),
    177: ("A", "A", "2022-03-01", "healing work on humans/animals resumed by 1 Mar 2022"),
    180: ("A", "A", "2022-01-19", "smoking after 19 Jan 2022"),
    181: ("A", "A", "never", "daily coffee consumption at any later date"),
    182: ("A", "B", "2022-02-06", "impeccability over the 2.5 weeks to the Anaam meeting"),
    183: ("A", "B", "from 2022-01-21", "eating per Anaam's recommendations reported again"),
    185: ("A", "A", "2022-01-23", "book bought; Royal Court in his routine afterwards"),
    186: ("A", "B", "from 2022-01-23", "AT training reported again"),
    187: ("A", "A", "unstated", "did she move to the coastal town"),
    188: ("A", "B", "2022-02-03", "all tasks daily, reported at the 3 Feb meeting"),
    192: ("A", "C", None, "task sequencing reported again"),
    195: ("A", "C", None, "communication awareness reported at a named incident"),
    200: ("A", "B", None, "stop-breathe-ask reported at a later anger episode"),
    206: ("A", "A", "from 2022-03-22", "drinking frequency reported later"),
    211: ("A", "A", "2022-03-20", "nicotine after 20 Mar 2022"),
    221: ("A", "A", "ongoing", "weight loss reported with numbers later"),
    226: ("A", "C", "2022-04-23", "family recapitulation reported done"),
    227: ("A", "B", "before each cigarette", "pre-smoking affirmation reported again"),
    233: ("A", "C", None, "his own later assessment of whether he let himself down"),
    234: ("A", "A", "unstated", "smoking after 2022-05-01"),
    236: ("A", "A", "2022-07-15", "smoking after he moved out, mid-July 2022"),
    239: ("C", "D", None, "no action attached"),
    245: ("A", "B", "from 2022-05-10", "rah-rah plus the 50 written points"),
    249: ("A", "B", "hourly from 2022-05-17", "hourly alarm presence task reported again"),
    257: ("A", "C", None, "reflections written without humour"),
    265: ("A", "C", "2022-06-06", "essay sent to Anaam unread"),
    275: ("A", "A", "unstated", "yoga mastery - any external marker (teaching, certification, competition)"),
    276: ("A", "A", "unstated", "a BJJ black belt, ever"),
    280: ("C", "D", None, "retracted in the same sentence - keep as a specimen of assent language"),
    283: ("A", "C", None, "testimonials obtained and used in marketing"),
    286: ("A", "D", None, "no action attached to the motivation"),
    290: ("A", "A", "2022-07-31", "three places visited before the end of the following week"),
    293: ("A", "B", "daily", "the practice reported again"),
    298: ("A", "B", "from 2022-08-04", "YCHYL workbook essays restarted and continued"),
    299: ("A", "A", "retrospective", "SPECIAL: her own account of three abandoned commitments - debt paid off by year end, business full time within a year. Score the originals, and score her naming them"),
    300: ("A", "A", "2022-08-04", "nicotine after 4 Aug 2022"),
    304: ("C", "D", None, "'I can and I will be successfully self-employed' - no action, no date"),
    308: ("A", "A", "unstated", "did every apprentice sign a release of liability form"),
    309: ("A", "A", "2022-09-16", "chapter 9 YCHYL submitted before that Friday"),
    310: ("A", "A", "2022-09-18", "2nd YCHYL read-through completed that week, 3rd started"),
    311: ("A", "A", "2022-11-01", "regular essay cadence from 1 Nov 2022"),
    313: ("A", "B", "daily", "training reported again"),
    324: ("A", "A", "2022-10-11", "coffee after 11 Oct 2022"),
    326: ("A", "A", "2022-10-11 to 2022-11-11", "coffee in that window"),
    332: ("A", "A", "2022-10-15", "coffee after 15 Oct 2022"),
    337: ("A", "A", "2023-12-31", "100k in the bank at 31 Dec 2023"),
    341: ("A", "C", "2022-11-01", "essay sent as PDF the next day"),
    342: ("A", "C", None, "work days organised differently, reported"),
    345: ("A", "A", "2022-11-30", "BJJ attended before end of Nov 2022"),
    348: ("A", "A", "2023-06-22", "L3 completed by 22 Jun 2023"),
    352: ("A", "A", "2023", "at least two BJJ competitions during 2023"),
    354: ("A", "A", "2022-11-26", "the English Open competition attended"),
    357: ("A", "C", None, "the capacity trained, reported"),
    358: ("A", "A", "Dec 2022 - Jan 2023", "time with the illustrator; the journal produced"),
    359: ("A", "B", "from 2022-12-03", "presence while eating reported again"),
    360: ("A", "C", None, "presence reported at a later shocking video"),
    363: ("A", "A", "unstated", "did she walk away from everything"),
    366: ("B", "A", "weekly from 2022-12-14", "weekly reflections submitted after 14 Dec 2022"),
    367: ("A", "C", None, "self-marketing actions reported"),
    368: ("A", "B", "from 2022-12-15", "inner-child conversation reported again"),
    369: ("A", "A", "from 2022-12-17", "does he say 'strongends' in later messages"),
    370: ("A", "A", "from 2022-12-18", "does the new name persist"),
    373: ("A", "A", "Christmas 2022", "daily silent sit with the guest; diet kept; no drinking"),
    375: ("A", "B", "Christmas 2022", "YCHYL workbook worked through alone"),
    376: ("A", "B", "Christmas 2022", "listening task with the nephews reported"),
    378: ("A", "B", "Christmas 2022", "daily tasks, woodworking, healthy eating over Christmas"),
    381: ("A", "A", "Christmas 2022", "sugar only at Christmas brunch"),
    382: ("A", "B", "Christmas 2022", "daily tasks, PON reading, no unhealthy food"),
    383: ("A", "B", "2022-12-24 to 2023-01-06", "two silence sits daily while travelling"),
    384: ("A", "C", None, "listening act of power practised with that friend"),
    385: ("A", "A", "2022-12-30", "shared by 30 Dec 2022"),
}

# Real names and Telegram handles appear INSIDE the quotes, so aliasing the sender is
# not enough. Everything here is replaced before anything is written to analysis/.
# Order matters: handles and two-word names first, then bare given names.
# Book figures and public names (Don Juan, Carlos, Genaro, Louise Hay, Eckhart Tolle,
# Nagual Anaam) are deliberately NOT redacted - Nagual Anaam is already public in
# tnz-telegram/, and the rest are authors and characters.
REDACT = [
    ("@Jelagat_Mercy", "`mira`"), ("@brookesophia", "`thea`"), ("@HugoSylvio", "`dell`"),
    ("@JewelsJegamune", "`kesh`"), ("@cityfool231984", "`fenn`"), ("@Benjaminyj", "`rook`"),
    ("@yarodukh", "`yar`"),
    ("Jelagat Mercy", "`mira`"), ("Angus Seth McLaren", "`gus`"),
    ("Brooke Sophia", "`thea`"), ("Will Turner Sanders", "`gale`"),
    ("Jarrad Gould", "`bram`"), ("Ian Minick", "`hale`"), ("Kisha Bo", "`orin`"),
    ("SatiMa Ra", "`sena`"), ("Derwen Lyava", "`vela`"),
    ("Jegamune", "`kesh`"), ("Jelagat", "`mira`"), ("Almasi", "`mira`"),
    ("AlmaSi", "`mira`"), ("Olupandu", "`tove`"),
    ("Avianna", "`isla`"), ("Brooke", "`thea`"), ("Sophia", "`thea`"),
    ("Derwen", "`vela`"), ("Jarrad", "`bram`"), ("Jewels", "`kesh`"),
    ("Gabrielle", "`wynn`"), ("Carolin", "`pia`"), ("Talitha", "`juno`"),
    ("SatiMa", "`sena`"), ("Sati", "`sena`"), ("Asaya", "`holt`"), ("Assaya", "`holt`"),
    ("Steen", "`fenn`"), ("Kisha", "`orin`"), ("Ilona", "`sable`"), ("Bogdan", "`yar`"),
    ("Natalie", "`isla`"), ("Leslie", "`sena`"), ("Mercy", "`mira`"),
    ("David", "`arlo`"), ("Dean", "`dov`"), ("Brett", "`rex`"), ("Sila", "`wren`"),
    # Georg is an EARLIER NAME of the apprentice who later posted as Asaya. Verified
    # 2026-08-17: no sender named Georg exists in 34,609 messages, and Asaya is the
    # essay-poster immediately before a "Georg" greeting 84 times (next highest 27).
    # Mapping it to its own alias would split one person in two.
    ("Hugo", "`dell`"), ("Georg", "`holt`"), ("June", "`juni`"), ("Helena", "`H.`"),
    ("Maryam", "`M.`"), ("Danijela", "`D.`"), ("Preya", "`noor`"),
    # third parties who are not apprentices - initial only
    ("Mikey", "`M.`"), ("Susan", "`S.`"), ("Phil", "`P.`"), ("Charity", "`C.`"),
]


def redact(s):
    for real, alias in REDACT:
        s = s.replace(real, alias)
    return s


ap = argparse.ArgumentParser()
ap.add_argument("--ranked", required=True)
ap.add_argument("--jsonl", required=True)
ap.add_argument("--md", required=True)
args = ap.parse_args()

rows = [json.loads(l) for l in Path(args.ranked).open(encoding="utf-8")]
band = [r for r in rows if r["band"] in ("high", "mid")]
band.sort(key=lambda r: (r["date"], r["msgid"]))

out = []
for i, (kind, tier, deadline, check) in sorted(SELECTION.items()):
    r = band[i]
    out.append(
        {
            "cid": f"C{len(out) + 1:03d}",
            "idx": i,
            "date": r["date"],
            "person": ALIAS.get(r["sender"], r["sender"]),
            "sender_raw": r["sender"],
            "source": r["source"],
            "msgid": r["msgid"],
            "title": r["title"],
            "quote": r["text"],
            "kind": kind,
            "tier": tier,
            "deadline": deadline,
            "check": check,
        }
    )

with Path(args.jsonl).open("w", encoding="utf-8") as fh:
    for o in out:
        fh.write(json.dumps(o, ensure_ascii=False) + "\n")

people = collections.Counter(o["person"] for o in out)
kinds = collections.Counter(o["kind"] for o in out)
tiers = collections.Counter(o["tier"] for o in out)
dated = sum(1 for o in out if o["deadline"])

md = []
md.append("# Frozen commitment register — 2021–22 pilot")
md.append("")
md.append(
    "**This file is the pre-registration.** It was written and committed to git on "
    "2026-08-17 **before any outcome was looked at**, which is rule 1 of "
    "`commitments-vs-outcomes.md`. There is deliberately no outcome column. Scoring "
    "happens in a later commit, against this list, with nothing added or removed."
)
md.append("")
md.append(
    f"**{len(out)} commitments**, {dated} of them carrying a date or cadence that makes "
    f"absence visible. Window 2021-01-01 to 2022-12-31 — decision D1, taken 2026-08-17."
)
md.append("")
md.append("## How this list was built")
md.append("")
md.append(
    "1. `scripts/extract_commitments.py` scanned the whole window — 563 essays "
    "(519,079 words, 18 of them image-only and therefore empty) and 12,183 chat "
    "messages (435,920 words) — for first-person commitment language, and produced "
    "2,051 candidate sentences."
)
md.append(
    "2. `scripts/rank_commitments.py` scored each candidate on volition, cadence, "
    "deadline, quantity and concreteness, minus quotation, hypothetical and "
    "non-first-person markers. 388 landed in the high and mid bands."
)
md.append(
    "3. Every one of those 388 was read by hand. The ones below are those with an "
    "action specific enough that its absence would be visible — the definition in the "
    "design file. The rest were dropped as reflective prose, book exegesis or "
    "conversational filler, not commitments."
)
md.append("")
md.append(
    "**Known gap, stated before scoring:** the 975 low-band and 688 rejected candidates "
    "have not been hand-read. The recall check the design file requires — hand-reading "
    "one full month end to end and counting what the prefilter missed — has NOT been "
    "done yet. Until it is, this list is a floor on the number of commitments in the "
    "window, not a census."
)
md.append("")
md.append(
    "**Second known gap:** `hale` wrote 18 essays in this window and 16 of them are "
    "image-only scans with no text layer (`tg-private/unreadable.txt`). So his "
    "commitments are represented by chat only, and he is under-counted here by "
    "construction. Do not read his low count as reticence."
)
md.append("")
md.append(
    "**How that gap gets closed without breaking the freeze.** `hale`'s scans are being "
    "transcribed by hand as of 2026-08-17. Anything they turn up will be added as a "
    "clearly-labelled *supplement* below this register, dated, with the register above "
    "left untouched. Nothing already frozen gets removed or edited. That keeps the "
    "pre-registration auditable: a later reader can see exactly what was known before "
    "any outcome was consulted, and exactly what arrived afterwards."
)
md.append("")
md.append("## Composition")
md.append("")
md.append("| | count |")
md.append("|---|---|")
md.append(f"| A — self-initiated | {kinds['A']} |")
md.append(f"| B — assigned by the teacher | {kinds['B']} |")
md.append(f"| C — assent, no action attached | {kinds['C']} |")
md.append("")
md.append("| evidence tier | count |")
md.append("|---|---|")
for t in ("A", "B", "C", "D"):
    md.append(f"| {t} | {tiers[t]} |")
md.append("")
md.append(
    "The A:B ratio is itself a pre-registered result — see the diagnostic in the design "
    "file. Note that `Nagual Anaam`'s own commitments are in the list and scored by the "
    "same rule, on the same logic as rule 3, which puts `yar`'s in."
)
md.append("")
md.append(
    "**Two things about that ratio, said now rather than after scoring.** First, `yar` "
    "does not appear in this register at all — he joined after the window, so rule 3 has "
    "nothing to bite on here. That is an absence of data, not an exemption, and when the "
    "study extends past 2023 his commitments enter on the same terms as everyone's. "
    "Second, B is low (4 of 115) and that number should not be read as 'the teacher "
    "rarely assigns anything'. Assignment happens overwhelmingly on the paid calls, and "
    "no call is in the archive. What this register can see is the assignments that "
    "happened to be written down in the group. So the A:B diagnostic in the design file "
    "is answerable for *written* commitments only, and the write-up has to say so."
)
md.append("")
md.append("| person | commitments |")
md.append("|---|---|")
for p, n in people.most_common():
    md.append(f"| `{p}` | {n} |")
md.append("")
md.append("## The register")
md.append("")
md.append("| id | date | person | kind | tier | deadline | commitment | what would settle it | src |")
md.append("|---|---|---|---|---|---|---|---|---|")
for o in out:
    q = redact(o["quote"]).replace("|", "/").replace("\n", " ")
    if len(q) > 200:
        q = q[:197] + "..."
    dl = o["deadline"] or "—"
    src = f"{o['source'][0]}{o['msgid']}"
    md.append(
        f"| {o['cid']} | {o['date']} | `{o['person']}` | {o['kind']} | {o['tier']} | "
        f"{dl} | {q} | {o['check']} | {src} |"
    )
md.append("")
md.append(
    "`src` is `e<id>` for an essay attachment and `c<id>` for a chat message; the id is "
    "the Telegram message id, so every quote above is retrievable from "
    "`tg-private/tac-full.jsonl` or `tg-private/docs/`."
)
Path(args.md).write_text("\n".join(md) + "\n", encoding="utf-8")

print(f"{len(out)} commitments frozen")
print(f"  kinds  {dict(kinds)}")
print(f"  tiers  {dict(tiers)}")
print(f"  dated  {dated}")
print(f"  people {len(people)}")
print(f"-> {args.jsonl}\n-> {args.md}")
