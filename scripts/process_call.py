"""VTT -> private-calls/ transcript + by-minute copy, with names aliased and agreed redactions applied.

Usage: python -I scripts/process_call.py <in.vtt> <out-stem>
       (stem e.g. private-calls/call-73-2026-09-05-5of8)

The alias table is order-sensitive. Keep it in sync with private-calls/README.md. After each new
call, grep the output for capitalised words that are not in the table, and screen it for family
medical details, third parties' finances, and anything legally sensitive before committing.
"""
import re
import subprocess
import sys
import pathlib

B = r'\b'
NL = r'(\n\[[\d:]+\] )'  # a caption line break, so phrases split across lines can be matched

ALIASES = [
    # fenn (Steen) and his caption garbles; "Steam" only where it is used as his name
    (B + r"(?:St[e]+n|Sten|Stein|Stin|Stina|Stain|Sting|Stig|Yestine|stin)" + B, '[fenn]'),
    (B + r"Ste(?='s|,|\. Can)", '[fenn]'),
    (B + r"St\.?(?= has| What| How| Rock)", '[fenn]'),
    (r"(?<=go to )Steam" + B + r"|(?<=switch to )[Ss]team" + B, '[fenn]'),
    (B + r"Tim\?", '[fenn]?'),
    (r"(?<=to )steam" + B + r"(?=[?.,])|(?<=still )steam" + B, '[fenn]'),
    (r"(?<=[Mm]y name is )Dane" + B, '[fenn]'),
    # "latte" is a caption garble of Lottie, fenn's partner (call 75 also has the name spelled out)
    (r"(?<=my )latte" + B + r"|(?<=with )latte" + B + r"|(?<=and uh )latte" + B + r"|" + B + r"L's father",
     "[fenn's partner]"),
    (NL + r"latte(?=\. Those)", r"\1[fenn's partner]"),
    # fenn's employer is a quasi-identifier; the name can be split across caption lines
    (r"(?i)politically" + NL + r"incorrect(?: tours| to us)?(?!,)", r"[employer]\1"),
    (r"(?i)" + B + r"politically incorrect(?: tours| to us)?", '[employer]'),
    # yar's wife and her caption garbles
    (B + r"(?:(?:O|Oo|Ho|A|E)lena|[AE]lona|Oena|Oina|Helen(?: K)?)" + B, "[yar's wife]"),
    (B + r"Lena" + B + r"(?= on the streets)", "[yar's wife]"),
    (r"(?<=with )Elon" + B + r"|" + B + r"Elon(?= and I)", "[yar's wife]"),
    (B + r"a loaner" + B + r"|" + B + r"the lona" + B, "[yar's wife]"),
    # yar's wife's profession is identifying
    (r"wealth" + NL + r"management", r"[adviser]\1"),
    (B + r"wealth manag(?:ement coach(?:es)?|ers?|ement)" + B, '[adviser]'),
    # private third parties
    (B + r"(?:Lena|Mariana|Lola)" + B, '[a friend]'),
    (B + r"Lottie" + B, "[fenn's partner]"),
    (B + r"Monica" + B, "[a friend's child]"),
    (B + r"(?:Oleg|Jared|Roger|Nigel|Yuri)" + B, '[friend]'),
    (B + r"Leela" + B, "[the teacher's wife]"),
    # apprentices, by the repo's alias table
    (B + r"Hugo" + B, '[dell]'),
    (B + r"(?:Ol[ao]n?du|Olupandu)" + B, '[tove]'),
    (B + r"(?:[CS]ila|Seila)" + B, '[wren]'),
    (B + r"(?:[Aa]s?saia?s|As?saya|Assayiah|Assa|Asa|Georg)" + B + r"|(?<=what )Isaiah" + B, '[holt]'),
    (B + r"(?:Leo|Ben)" + B, '[rook]'),
    (B + r"(?:Derwen|Darwin)" + B + r"|(?<=like )Dar" + B, '[vela]'),
    (B + r"Ilona" + B, '[sable]'),
    (B + r"(?:Jules|Jewels)" + B, '[kesh?]'),
    (B + r"Sophie" + B, "[tove's daughter]"),
    (B + r"(?:Avianna|Aviana|Ariana)" + B, '[isla]'),
    (B + r"Magnus" + B, '[a colleague]'),
    # named in passing, identity not established
    (B + r"(?:Ala|Ela|Ella|Maya|Dwan|Christine|Lona|Lana|Cau|Yara|David|Andy|Justin)" + B, '[name]'),
]

# Per-call redactions agreed with yar on 2026-11-04 (family medical; fenn's money and financial
# details; third parties' finances; legally sensitive money handling). Keyed by call-file prefix.
#   ('block', start, end, label): lines stamped in [start, end] collapse into one label line
#   ('amounts', start, end, label): numbers in lines stamped in [start, end] become the label
REDACTIONS = {
    'call-70-': [('block', '00:54:56', '00:57:38', "[redacted: financial arrangements between the teacher and yar's family]"),
                 ('block', '01:26:29', '01:55:33', "[redacted: yar's wife - body, weight and exercise; another apprentice's weight]"),
                 ('amounts', '00:20:00', '00:24:00', '[amount]')],
    'call-71-': [('block', '01:49:30', '01:56:10', '[redacted: tax and money-handling details]'),
                 ('block', '01:15:40', '01:16:45', "[redacted: financial arrangements between the teacher and yar's family]"),
                 ('block', '01:56:50', '01:57:33', "[redacted: third parties' finances]"),
                 ('amounts', '01:13:00', '02:08:00', '[amount]')],
    'call-73-': [('block', '00:11:07', '00:11:13', '[redacted: family medical]')],
    'call-74-': [('block', '00:33:42', '00:35:16', "[redacted: fenn's personal finances]"),
                 ('block', '00:36:26', '00:36:50', "[redacted: financial arrangements between the teacher and yar's family]"),
                 ('amounts', '00:30:00', '00:44:00', '[amount]')],
}
AMOUNT = re.compile(r'[£€$]?\d[\d,.]*(?:\s?(?:k|K|kroner|krone|corner))?')


def redact(text, rules):
    lines = text.split('\n')
    for kind, start, end, label in rules:
        out, placed = [], False
        for line in lines:
            m = re.match(r'\[(\d\d:\d\d:\d\d)\] ', line)
            inside = bool(m) and start <= m[1] <= end
            if inside and kind == 'block':
                if not placed:
                    out.append(f'[{start}] {label}')
                    placed = True
                continue
            if inside and kind == 'amounts':
                line = line[:len(m[0])] + AMOUNT.sub(label, line[len(m[0]):])
            out.append(line)
        lines = out
    return '\n'.join(lines)


def main():
    vtt, stem = sys.argv[1], sys.argv[2]
    here = pathlib.Path(__file__).parent
    full = stem + '.txt'
    subprocess.run([sys.executable, '-I', str(here / 'clean_vtt.py'), vtt, full], check=True)
    t = open(full, encoding='utf-8').read()
    t = t.replace('&gt;', '>').replace('&amp;', '&').replace('&nbsp;', ' ')
    for pat, rep in ALIASES:
        t = re.sub(pat, rep, t)
    for prefix, rules in REDACTIONS.items():
        if pathlib.Path(stem).name.startswith(prefix):
            t = redact(t, rules)
    open(full, 'w', encoding='utf-8').write(t)
    out, lastm = [], None
    for line in t.splitlines():
        m = re.match(r'\[(\d\d):(\d\d):\d\d\] (.*)', line)
        if not m:
            continue
        if (m[1], m[2]) != lastm:
            out.append('\n[' + m[1] + ':' + m[2] + '] ')
            lastm = (m[1], m[2])
        out.append(m[3] + ' ')
    open(stem + '-by-minute.txt', 'w', encoding='utf-8').write(''.join(out).lstrip('\n') + '\n')


if __name__ == '__main__':
    main()
