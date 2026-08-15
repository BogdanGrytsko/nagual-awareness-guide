"""Read-only helper for the document attachments (essay PDFs) in a Telegram chat.

    py scripts/tg_docs.py list --chat -1001351431623 --since 2025-08-15 --until 2025-09-15
    py scripts/tg_docs.py get  --chat -1001351431623 --ids 30356,30357 --out tg-private/docs

Only reads and downloads. Nothing here sends, edits, deletes, joins or leaves.
Downloads go to a gitignored directory by default — they are other people's private material.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tg import get_client, resolve, parse_date, sender_name  # noqa: E402


def doc_name(msg):
    for attr in getattr(getattr(msg, "document", None), "attributes", []) or []:
        name = getattr(attr, "file_name", None)
        if name:
            return name
    return f"{msg.id}.bin"


def iter_docs(client, entity, since=None, until=None, ids=None, limit=None):
    if ids:
        for msg in client.get_messages(entity, ids=ids):
            if msg is not None:
                yield msg
        return
    kwargs = {"limit": limit}
    if since:
        kwargs.update(reverse=True, offset_date=since)
    elif until:
        kwargs.update(offset_date=until)
    for msg in client.iter_messages(entity, **kwargs):
        if since and msg.date < since:
            continue
        if until and msg.date > until:
            if since:
                break
            continue
        if getattr(msg, "document", None):
            yield msg


def cmd_list(client, args):
    entity = resolve(client, args.chat)
    cache = {}
    for msg in iter_docs(
        client, entity, parse_date(args.since), parse_date(args.until), limit=args.limit
    ):
        caption = (msg.message or "").replace("\n", " ")[:70]
        print(
            f"{msg.id:>7}  {msg.date:%Y-%m-%d}  {sender_name(client, msg, cache):<16}"
            f"  {doc_name(msg):<60}  {caption}"
        )


def cmd_get(client, args):
    entity = resolve(client, args.chat)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cache = {}
    ids = [int(i) for i in args.ids.split(",")]
    for msg in iter_docs(client, entity, ids=ids):
        if not getattr(msg, "document", None):
            print(f"{msg.id}: no document", file=sys.stderr)
            continue
        who = sender_name(client, msg, cache).replace(" ", "_")
        target = out / f"{msg.date:%Y-%m-%d}_{msg.id}_{who}_{doc_name(msg)}"
        client.download_media(msg, file=str(target))
        print(f"{msg.id} -> {target}")


def main():
    parser = argparse.ArgumentParser(description="Read-only Telegram document reader.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list")
    p.add_argument("--chat", required=True)
    p.add_argument("--since")
    p.add_argument("--until")
    p.add_argument("--limit", type=int, default=None)
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("get")
    p.add_argument("--chat", required=True)
    p.add_argument("--ids", required=True, help="comma-separated message ids")
    p.add_argument("--out", default="tg-private/docs")
    p.set_defaults(func=cmd_get)

    args = parser.parse_args()
    client = get_client()
    try:
        args.func(client, args)
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
