#!/usr/bin/env python3
"""
Watches three Trackr boards (Germany Finance, Hong Kong Finance, UK Finance -
Summer Internships) for changes to each programme's Opening Date / Closing
Date, and sends a Telegram message whenever something changes.

State (the last-seen opening/closing date per programme) is kept in
state.json, which this script rewrites on every run. The GitHub Actions
workflow commits that file back to the repo so the next run can compare
against it.
"""

import json
import os
import sys
import urllib.request
import urllib.parse

BOARDS = [
    {"label": "Germany Finance", "region": "Germany", "industry": "Finance"},
    {"label": "Hong Kong Finance", "region": "Hong Kong", "industry": "Finance"},
    {"label": "UK Finance", "region": "UK", "industry": "Finance"},
]
SEASON = "2027"
TYPE = "summer-internships"
API_BASE = "https://api.the-trackr.com/programmes"

STATE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def fetch_board(board):
    params = {
        "region": board["region"],
        "industry": board["industry"],
        "season": SEASON,
        "type": TYPE,
    }
    url = API_BASE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)


def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID env vars", file=sys.stderr)
        sys.exit(1)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": text,
        "disable_web_page_preview": "true",
    }).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()


def main():
    state = load_state()
    changes = []

    for board in BOARDS:
        try:
            programmes = fetch_board(board)
        except Exception as e:
            print(f"Failed to fetch {board['label']}: {e}", file=sys.stderr)
            continue

        for p in programmes:
            pid = p.get("id")
            if not pid:
                continue
            key = f"{board['label']}::{pid}"
            company = (p.get("company") or {}).get("name", "")
            name = p.get("name", "")
            opening = p.get("openingDate")
            closing = p.get("closingDate")

            prev = state.get(key)
            new_val = {"opening": opening, "closing": closing}

            if prev is None:
                # First time seeing this programme: record it, but only alert
                # if it already has a date (avoids a flood of "new" alerts on
                # first-ever run — comment out the `if opening or closing`
                # guard below if you'd rather be alerted about brand-new
                # postings too).
                state[key] = new_val
                continue

            if prev.get("opening") != opening:
                changes.append(
                    f"{board['label']}: {company} - {name}\n"
                    f"Opening Date: {prev.get('opening') or '(none)'} -> {opening or '(none)'}"
                )
            if prev.get("closing") != closing:
                changes.append(
                    f"{board['label']}: {company} - {name}\n"
                    f"Closing Date: {prev.get('closing') or '(none)'} -> {closing or '(none)'}"
                )

            state[key] = new_val

    save_state(state)

    if changes:
        message = "Trackr update:\n\n" + "\n\n".join(changes)
        # Telegram messages are capped at 4096 chars; split if needed.
        for i in range(0, len(message), 4000):
            send_telegram(message[i:i + 4000])
        print(f"Sent {len(changes)} change(s).")
    else:
        print("No changes.")


if __name__ == "__main__":
    main()
