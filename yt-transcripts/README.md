# The Nagual Zone — public YouTube transcripts

- `index.tsv` lists every public upload on the channel (videos, shorts, live streams), newest first. Columns:
  upload date, kind, video id, duration, views (as of 2026-11-19), title, transcript path, and legacy transcript.
- `tnz/<date>_<id>_<slug>.txt` holds YouTube captions, cleaned into timestamped lines with `[hh:mm:ss]`.
  They are **machine captions**: names come out mangled ("Narwhal zone" = Nagual Zone, "Anna"/"an arm" = Anaam), so check
  the surrounding minute before quoting.
- The numbered `NN_*.txt` and `collab_*` / `sovereignty_*` files at the top level are the earlier set
  (top 30 by views, from `youtube_transcript_api`, no timestamps). They are kept as they were, and `index.tsv` links them.
- `external/` has public videos from other channels that the analysis uses.

Snapshot taken 2026-11-19: 403 uploads, 388 with captions. The 15 without are clips under 2:20.

`raw-vtt/` contains the raw caption files: `<id>.<lang>.vtt` (771 files; `en-orig` is the original track and is preferred) plus
`flat.tsv` / `meta.tsv` / `urls.txt`. To rebuild `tnz/` and `index.tsv`, run `python -I scripts/build_yt_index.py yt-transcripts/raw-vtt`.

To refresh from the channel:

```
yt-dlp --flat-playlist --print "<kind>\t%(id)s\t%(title)s\t%(duration_string)s" <channel>/<kind>   > flat.tsv
yt-dlp --skip-download --write-auto-subs --write-subs --sub-langs "en,en-orig,en-GB,en-US,es,es-orig" \
  --sub-format vtt --sleep-subtitles 2 -o "%(id)s.%(ext)s" \
  --print-to-file "%(id)s\t%(upload_date)s\t%(duration_string)s\t%(view_count)s\t%(language)s\t%(title)s" meta.tsv -a urls.txt
python -I scripts/build_yt_index.py <raw_dir>
```

Channel: https://www.youtube.com/channel/UCynH8ti6coNFeZDnA-Lk3JA
