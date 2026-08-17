"""Copy already-downloaded essays from the Telegram Desktop folder into tg-private/docs
under the tg_docs.py naming convention, and convert to .txt.

Read-only against Downloads; writes only into tg-private/docs (gitignored).
"""
import json, os, re, sys, io, shutil, subprocess, time, collections, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DL = r"C:\Users\Bogdan\Downloads\Telegram Desktop"
OUT = os.path.join('tg-private', 'docs')
TEXT_EXT = {'.pdf', '.docx'}          # converters we actually have
SKIP_EXT = {'.odt', '.doc', '.rtf'}   # need pandoc/LibreOffice - not installed

def norm(n):
    n = n.lower(); n = re.sub(r'^\d{8}[-_]', '', n)
    n = re.sub(r'\s*\(\d+\)(?=\.[a-z0-9]+$)', '', n)
    n = re.sub(r'[\s_\-]+', ' ', n); n = re.sub(r'[^a-z0-9. ]', '', n)
    return n.strip()

def safe(s):
    s = re.sub(r'[<>:"/\\|?*]', '_', str(s)).strip()
    # pdftotext is an ANSI Windows binary: it cannot open a path holding characters
    # outside the system codepage (one sender's display name carries an emoji).
    return ''.join(c if c.encode('cp1252', 'ignore') else '_' for c in s)

def convert(src, dst_txt):
    ext = os.path.splitext(src)[1].lower()
    if ext == '.pdf':
        r = subprocess.run(['pdftotext', '-layout', src, dst_txt],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return False, (r.stderr or '').strip()[:120]
        return True, ''
    if ext == '.docx':
        import docx
        d = docx.Document(src)
        parts = [p.text for p in d.paragraphs]
        for t in d.tables:
            for row in t.rows:
                parts.append('\t'.join(c.text for c in row.cells))
        open(dst_txt, 'w', encoding='utf-8').write('\n'.join(parts))
        return True, ''
    return False, 'no converter'

ap = argparse.ArgumentParser()
ap.add_argument('--limit', type=int, default=20)
ap.add_argument('--all', action='store_true')
args = ap.parse_args()

idx = json.load(open('tg-private/tac-docs-index.json', encoding='utf-8'))
files = [f for f in os.listdir(DL) if os.path.isfile(os.path.join(DL, f))]
dlmap = collections.defaultdict(list)
for f in files:
    dlmap[norm(f)].append(f)
want = collections.Counter(norm(e.get('file', '')) for e in idx)

# unambiguous: exactly one index entry wants this name, exactly one disk file provides it
un = [e for e in idx
      if norm(e['file']) in dlmap
      and want[norm(e['file'])] == 1
      and len(dlmap[norm(e['file'])]) == 1
      and os.path.splitext(e['file'])[1].lower() in TEXT_EXT]
un.sort(key=lambda e: e['date'])

if not args.all:
    # spread the trial across senders and years rather than taking one dense block
    bysender = collections.defaultdict(list)
    for e in un:
        bysender[str(e['sender'])].append(e)
    picked, i = [], 0
    order = sorted(bysender, key=lambda s: -len(bysender[s]))
    while len(picked) < args.limit:
        added = False
        for s in order:
            if i < len(bysender[s]) and len(picked) < args.limit:
                picked.append(bysender[s][i]); added = True
        if not added: break
        i += 1
    un = picked

os.makedirs(OUT, exist_ok=True)
t0 = time.time()
ok = fail = skipped = 0
bytes_copied = 0
for e in un:
    src_name = dlmap[norm(e['file'])][0]
    src = os.path.join(DL, src_name)
    who = safe(e['sender']).replace(' ', '_')
    base = f"{e['date'][:10]}_{e['id']}_{who}_{safe(e['file'])}"
    dst = os.path.join(OUT, base)
    dst_txt = os.path.splitext(dst)[0] + '.txt'
    if os.path.exists(dst_txt):
        skipped += 1; continue
    shutil.copy2(src, dst)
    bytes_copied += os.path.getsize(dst)
    good, err = convert(dst, dst_txt)
    if good:
        n = len(open(dst_txt, encoding='utf-8', errors='replace').read().split())
        ok += 1
        print(f"  OK  {n:6d} words  {base[:78]}")
        if n < 50:
            print(f"      ^^ LOW WORD COUNT - likely scanned/image PDF, needs OCR")
    else:
        fail += 1
        print(f"  FAIL {err}  {base[:70]}")
el = time.time() - t0
print(f"\nconverted {ok}, failed {fail}, already-present {skipped} in {el:.1f}s"
      f"  ({el/max(ok+fail,1):.2f}s/file, {bytes_copied/1e6:.1f} MB)")
if ok + fail:
    print(f"projected for 1523 unambiguous files: {el/(ok+fail)*1523/60:.1f} min")
