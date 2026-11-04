"""VTT -> private-calls/ transcript + by-minute copy, with other people's names aliased.

Usage: python -I scripts/process_call.py <in.vtt> <out-stem>
       (stem e.g. private-calls/call-73-2026-09-05-5of8)

The alias table is order-sensitive. Keep it in sync with private-calls/README.md, and after each
new call grep the output for capitalised words that are not in the table.
"""
import re
import subprocess
import sys
import pathlib

B = r'\b'
ALIASES = [
    # fenn (Steen) and his caption garbles; "Steam" only where it is used as his name
    (B + r"(?:St[e]+n|Sten|Stein|Stin|Stain|Sting|Stig|Yestine)" + B, '[fenn]'),
    (B + r"Ste(?='s|,)", '[fenn]'),
    (r"(?<=go to )Steam" + B + r"|(?<=switch to )[Ss]team" + B, '[fenn]'),
    (B + r"Tim\?", '[fenn]?'),
    (r"(?<=to )steam" + B + r"(?=[?.,])|(?<=still )steam" + B, '[fenn]'),
    (r"(?<=[Mm]y name is )Dane" + B, '[fenn]'),
    # fenn's employer is a quasi-identifier; the name is split across caption lines
    (r"Politically(\n\[[\d:]+\] )Incorrect(?: Tours| to Us)?", r"[employer]\1"),
    (B + r"Politically Incorrect(?: Tours)?", '[employer]'),
    # yar's wife and her caption garbles
    (B + r"(?:(?:O|Oo|Ho|A)lena|Oena|Oina|Helen(?: K)?)" + B, "[yar's wife]"),
    (B + r"Lena" + B + r"(?= on the streets)", "[yar's wife]"),
    # private third parties
    (B + r"(?:Lena|Mariana|Lottie)" + B, '[a friend]'),
    (B + r"Monica" + B, "[a friend's child]"),
    (B + r"(?:Oleg|Jared|Roger|Nigel|Yuri)" + B, '[friend]'),
    (B + r"Leela" + B, "[the teacher's wife]"),
    # apprentices, by the repo's alias table
    (B + r"Hugo" + B, '[dell]'),
    (B + r"(?:Ol[ao]n?du|Olupandu)" + B, '[tove]'),
    (B + r"(?:[CS]ila|Seila)" + B, '[wren]'),
    (B + r"(?:[Aa]s?saia?s|As?saya|Asa|Georg)" + B, '[holt]'),
    (B + r"(?:Leo|Ben)" + B, '[rook]'),
    (B + r"(?:Derwen|Darwin)" + B, '[vela]'),
    (B + r"Ilona" + B, '[sable]'),
    (B + r"(?:Jules|Jewels)" + B, '[kesh?]'),
    (B + r"Sophie" + B, "[tove's daughter]"),
    # named in passing, identity not established
    (B + r"(?:Ala|Ela|Ella|Maya|Dwan|Christine|Lona|Lana|Cau)" + B, '[name]'),
]


# Per-call redactions, agreed with yar 2026-11-04. Keyed by the call-file prefix.
#   ('block', start, end, label): lines with stamps in [start, end] collapse into one label line
#   ('amounts', start, end, label): numbers in lines with stamps in [start, end] become the label
REDACTIONS = {
    'call-73-': [('block', '00:11:07', '00:11:13', '[redacted: family medical]')],
    'call-74-': [('block', '00:33:42', '00:35:16', "[redacted: fenn's personal finances]"),
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
