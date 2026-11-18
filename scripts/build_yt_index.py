"""Build yt-transcripts/tnz/ (cleaned caption transcripts) and yt-transcripts/index.tsv
for every public upload on The Nagual Zone YouTube channel (videos, shorts, streams).

Inputs (outside the repo, raw download dir):
  flat.tsv  -- tab: kind, id, title, duration   (yt-dlp --flat-playlist per tab)
  meta.tsv  -- tab: id, upload_date, duration, views, language, title  (--print-to-file)
  <id>.<lang>.vtt -- caption files
Usage: python -I scripts/build_yt_index.py <raw_dir>
"""
import html, re, sys, unicodedata
from pathlib import Path

RAW = Path(sys.argv[1])
REPO = Path(__file__).resolve().parent.parent
OUT = REPO / 'yt-transcripts'
TNZ = OUT / 'tnz'
TNZ.mkdir(parents=True, exist_ok=True)
LANG_PREF = ['en-orig', 'en', 'en-GB', 'en-US', 'es-orig', 'es']
TS = re.compile(r'^(\d\d:\d\d:\d\d)\.\d+ -->')


def clean_vtt(path):
    out, cur, last = [], None, None
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        m = TS.match(line)
        if m:
            cur = m.group(1); continue
        if not line.strip() or line.startswith(('WEBVTT', 'Kind:', 'Language:')) or cur is None:
            continue
        text = html.unescape(re.sub(r'<[^>]+>', '', line)).strip()
        if not text or text == last or (out and out[-1][1] == text):
            continue
        out.append((cur, text)); last = text
    return [f'[{t}] {x}' for i, (t, x) in enumerate(out)
            if not (i + 1 < len(out) and out[i + 1][1].startswith(x))]


def slug(s, n=60):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = re.split(r'\s[-|~]\s|\|', s)[0]
    return re.sub(r'[^A-Za-z0-9]+', '-', s).strip('-')[:n] or 'untitled'


def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', s)


def read_tsv(p):
    return [l.rstrip('\r\n').split('\t') for l in p.read_text(encoding='utf-8', errors='replace').splitlines() if l.strip()]


kind = {r[1]: r[0] for r in read_tsv(RAW / 'flat.tsv')}
flat_title = {r[1]: r[2] for r in read_tsv(RAW / 'flat.tsv')}
meta = {}
for r in read_tsv(RAW / 'meta.tsv'):
    r += [''] * 6
    meta[r[0]] = dict(date=r[1], dur=r[2], views=r[3], lang=r[4], title=r[5])

# legacy files (youtube_transcript_api, no timestamps): match by URL in header, else title
legacy = {}
for f in OUT.glob('*.txt'):
    head = f.read_text(encoding='utf-8', errors='replace')[:600]
    m = re.search(r'watch\?v=([\w-]{11})|youtu\.be/([\w-]{11})', head)
    if m:
        legacy[m.group(1) or m.group(2)] = f.name

rows, missing = [], []
for vid, k in kind.items():
    md = meta.get(vid, dict(date='', dur='', views='', lang='', title=flat_title[vid]))
    title = md['title'] or flat_title[vid]
    d = md['date']
    date = f'{d[:4]}-{d[4:6]}-{d[6:]}' if len(d) == 8 else ''
    vtt = next((RAW / f'{vid}.{l}.vtt' for l in LANG_PREF if (RAW / f'{vid}.{l}.vtt').exists()), None)
    fname, lines = '', 0
    if vtt:
        body = clean_vtt(vtt)
        lines = len(body)
        fname = f"tnz/{date or 'nodate'}_{vid}_{slug(title)}.txt"
        url = f'https://www.youtube.com/watch?v={vid}' if k != 'shorts' else f'https://www.youtube.com/shorts/{vid}'
        hdr = [f'TITLE: {title}', f'URL:   {url}', f'DATE:  {date}', f'KIND:  {k}',
               f'DURATION: {md["dur"]}', f'CAPTIONS: {vtt.name.split(".")[-2]} (YouTube, machine captions unless manual)',
               '-' * 80, '']
        (OUT / fname).write_text('\n'.join(hdr + body) + '\n', encoding='utf-8')
    else:
        missing.append(vid)
    rows.append([date, k, vid, md['dur'], md['views'], title.replace('\t', ' '), fname, legacy.get(vid, '')])

rows.sort(key=lambda r: (r[0] or '0000', r[2]), reverse=True)
with open(OUT / 'index.tsv', 'w', encoding='utf-8', newline='\n') as fh:
    fh.write('upload_date\tkind\tid\tduration\tviews\ttitle\ttranscript\tlegacy_transcript\n')
    for r in rows:
        fh.write('\t'.join(r) + '\n')
print(f'{len(rows)} uploads, {len(rows) - len(missing)} with captions, {len(missing)} without')
print('no captions:', ' '.join(missing))
