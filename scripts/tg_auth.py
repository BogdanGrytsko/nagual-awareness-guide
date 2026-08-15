"""One-time interactive Telegram login.

Run this yourself so the code and 2FA password never pass through anyone else:

    py scripts/tg_auth.py

Asks for api_id / api_hash (https://my.telegram.org -> API development tools)
the first time, then for your phone number, the login code Telegram sends you,
and your 2FA password if you have one set. Writes config.json and user.session
into ~/.tg, deliberately outside the repo so credentials never sit in a git
working tree.
"""

import json
import sys
from pathlib import Path

TG_DIR = Path.home() / ".tg"
CONFIG = TG_DIR / "config.json"
SESSION = TG_DIR / "user"


def main():
    try:
        from telethon.sync import TelegramClient
    except ImportError:
        sys.exit("Telethon is not installed. Run:  py -m pip install --user telethon")

    TG_DIR.mkdir(exist_ok=True)

    if CONFIG.exists():
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    else:
        print("Get these from https://my.telegram.org -> API development tools")
        print("(they identify the app, not your account)\n")
        cfg = {
            "api_id": int(input("api_id:   ").strip()),
            "api_hash": input("api_hash: ").strip(),
        }
        CONFIG.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
        print(f"\nSaved {CONFIG}")

    print("\nLogging in. Telegram will send a code to your app.\n")
    with TelegramClient(str(SESSION), cfg["api_id"], cfg["api_hash"]) as client:
        me = client.get_me()
        handle = f" (@{me.username})" if me.username else ""
        print(f"\nLogged in as {me.first_name or ''}{handle}, id={me.id}")
        print(f"Session written to {SESSION}.session")
        print("\nNext:  py scripts/tg.py chats --limit 40")


if __name__ == "__main__":
    main()
