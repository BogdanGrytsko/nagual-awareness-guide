"""Collapse rolling YouTube auto-caption VTT into timestamped lines.
Usage: python -I scripts/clean_vtt.py in.vtt out.txt"""
import re, sys
src, dst = sys.argv[1], sys.argv[2]
ts_re = re.compile(r'^(\d\d:\d\d:\d\d)\.\d+ -->')
out, cur, last = [], None, None
for line in open(src, encoding='utf-8'):
    line = line.rstrip('\n')
    m = ts_re.match(line)
    if m:
        cur = m.group(1); continue
    if not line.strip() or line.startswith(('WEBVTT', 'Kind:', 'Language:')) or cur is None:
        continue
    text = re.sub(r'<[^>]+>', '', line).strip()
    if not text or text == last:
        continue
    if out and out[-1][1] == text:
        continue
    out.append((cur, text)); last = text
# drop lines that are a prefix-repeat of the next
res = []
for i, (t, x) in enumerate(out):
    if i + 1 < len(out) and out[i + 1][1].startswith(x):
        continue
    res.append(f'[{t}] {x}')
open(dst, 'w', encoding='utf-8').write('\n'.join(res) + '\n')
print(len(res), 'lines')
