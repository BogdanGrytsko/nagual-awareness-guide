"""Read-only Telegram reader for this repo.

Requires a one-time login first:  py scripts/tg_auth.py

    py scripts/tg.py chats [--limit 40]
    py scripts/tg.py search "inner silence" [--chat tnz] [--limit 50] [--from Nagual]
    py scripts/tg.py history --chat tnz [--since 2026-08-01] [--until 2026-08-14]
    py scripts/tg.py export --chat tnz --out tnz-telegram/corpus_all_messages.txt
    py scripts/tg.py whois @someuser

Every command only reads. Nothing here sends, edits, deletes, joins or leaves.
Output matches the format already used in tnz-telegram/:  [ISO-8601] Name: text

Credentials and session live in ~/.tg, outside the repo.
"""

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

TG_DIR = Path.home() / ".tg"

# Windows consoles default to cp1252, which blows up on emoji and Cyrillic.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")
CONFIG = TG_DIR / "config.json"
SESSION = TG_DIR / "user"


def get_client():
    try:
        from telethon.sync import TelegramClient
    except ImportError:
        sys.exit("Telethon is not installed. Run:  py -m pip install --user telethon")

    if not CONFIG.exists():
        sys.exit("No credentials yet. Run:  py scripts/tg_auth.py")

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    client = TelegramClient(
        str(SESSION), cfg["api_id"], cfg["api_hash"], flood_sleep_threshold=120
    )
    client.connect()
    if not client.is_user_authorized():
        sys.exit("Session is not authorized. Run:  py scripts/tg_auth.py")
    return client


def parse_date(value):
    if not value:
        return None
    return dt.datetime.fromisoformat(value).replace(tzinfo=dt.timezone.utc)


def display_name(entity):
    if entity is None:
        return None
    title = getattr(entity, "title", None)
    if title:
        return title
    parts = [getattr(entity, "first_name", None), getattr(entity, "last_name", None)]
    name = " ".join(p for p in parts if p)
    return name or getattr(entity, "username", None)


def resolve(client, ref):
    """Accept a @username, a numeric id, or a fuzzy dialog-title match."""
    if ref is None:
        return None
    try:
        if ref.lstrip("-").isdigit():
            return client.get_entity(int(ref))
        return client.get_entity(ref)
    except Exception:
        pass
    needle = ref.lower()
    for dialog in client.iter_dialogs():
        if needle in (dialog.name or "").lower():
            return dialog.entity
    sys.exit(f"Could not resolve chat: {ref!r}  (try: py scripts/tg.py chats)")


def sender_name(client, msg, cache):
    sid = msg.sender_id
    if sid is None:
        return getattr(msg, "post_author", None) or "channel"
    if sid not in cache:
        try:
            cache[sid] = display_name(msg.sender or client.get_entity(sid)) or str(sid)
        except Exception:
            cache[sid] = str(sid)
    return cache[sid]


def body(msg):
    text = (msg.message or "").strip()
    if text:
        return text
    if msg.media:
        return f"[{type(msg.media).__name__}]"
    return "[no text]"


def emit(client, messages, cache, as_json, out=None):
    lines = []
    for msg in messages:
        if as_json:
            lines.append(
                json.dumps(
                    {
                        "id": msg.id,
                        "date": msg.date.isoformat(),
                        "sender": sender_name(client, msg, cache),
                        "text": body(msg),
                    },
                    ensure_ascii=False,
                )
            )
        else:
            stamp = msg.date.strftime("%Y-%m-%dT%H:%M:%S")
            lines.append(f"[{stamp}] {sender_name(client, msg, cache)}: {body(msg)}")
    text = "\n".join(lines)
    if out:
        Path(out).write_text(text + "\n", encoding="utf-8")
        print(f"{len(lines)} messages -> {out}")
    else:
        print(text)
    return len(lines)


def walk(client, entity, args, search=None, from_user=None):
    """Yield messages honouring --since / --until, oldest-first when --since is set."""
    since, until = parse_date(getattr(args, "since", None)), parse_date(
        getattr(args, "until", None)
    )
    kwargs = {"limit": args.limit, "search": search, "from_user": from_user}
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
        yield msg


def cmd_chats(client, args):
    for dialog in client.iter_dialogs(limit=args.limit):
        kind = "group" if dialog.is_group else "channel" if dialog.is_channel else "dm"
        print(f"{dialog.id:>16}  {kind:<8}  {dialog.name}")


def cmd_search(client, args):
    entity = resolve(client, args.chat) if args.chat else None
    from_user = resolve(client, getattr(args, "from_user", None)) if args.from_user else None
    cache = {}
    scope = display_name(entity) if entity else "all chats"
    print(f"# search {args.query!r} in {scope}\n", file=sys.stderr)
    n = emit(client, walk(client, entity, args, search=args.query, from_user=from_user), cache, args.json)
    print(f"\n# {n} hits", file=sys.stderr)


def cmd_history(client, args):
    entity = resolve(client, args.chat)
    from_user = resolve(client, args.from_user) if args.from_user else None
    emit(client, walk(client, entity, args, from_user=from_user), {}, args.json)


def cmd_export(client, args):
    entity = resolve(client, args.chat)
    from_user = resolve(client, args.from_user) if args.from_user else None
    args.limit = None if args.limit == 0 else args.limit
    emit(client, walk(client, entity, args, from_user=from_user), {}, args.json, out=args.out)


def cmd_members(client, args):
    """List chat members, optionally filtered by a name fragment."""
    entity = resolve(client, args.chat)
    for user in client.iter_participants(entity, search=args.grep or "", limit=args.limit):
        handle = f"@{user.username}" if user.username else "-"
        print(f"{user.id:>14}  {handle:<20}  {display_name(user)}")


def cmd_whois(client, args):
    entity = resolve(client, args.who)
    print(
        json.dumps(
            {
                "id": entity.id,
                "name": display_name(entity),
                "username": getattr(entity, "username", None),
                "type": type(entity).__name__,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


def main():
    parser = argparse.ArgumentParser(description="Read-only Telegram reader.")
    parser.add_argument("--json", action="store_true", help="JSONL output")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("chats", help="list dialogs so you can find a chat's name/id")
    p.add_argument("--limit", type=int, default=40)
    p.set_defaults(func=cmd_chats)

    p = sub.add_parser("search", help="server-side message search")
    p.add_argument("query")
    p.add_argument("--chat", help="chat name, @username or id; omit to search everywhere")
    p.add_argument("--from", dest="from_user", help="only messages from this sender")
    p.add_argument("--since")
    p.add_argument("--until")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("history", help="read a chat's messages")
    p.add_argument("--chat", required=True)
    p.add_argument("--from", dest="from_user", help="only messages from this sender")
    p.add_argument("--since")
    p.add_argument("--until")
    p.add_argument("--limit", type=int, default=200)
    p.set_defaults(func=cmd_history)

    p = sub.add_parser("export", help="dump a chat to a file in the tnz-telegram/ format")
    p.add_argument("--chat", required=True)
    p.add_argument("--from", dest="from_user", help="only messages from this sender")
    p.add_argument("--out", required=True)
    p.add_argument("--since")
    p.add_argument("--until")
    p.add_argument("--limit", type=int, default=0, help="0 = no limit")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("members", help="list chat members, filtered by name fragment")
    p.add_argument("--chat", required=True)
    p.add_argument("--grep", help="name fragment to filter on")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_members)

    p = sub.add_parser("whois", help="resolve a user or chat")
    p.add_argument("who")
    p.set_defaults(func=cmd_whois)

    args = parser.parse_args()
    client = get_client()
    try:
        args.func(client, args)
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
