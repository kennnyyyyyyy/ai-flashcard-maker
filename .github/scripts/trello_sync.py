"""Keep the Trello board in step with pull requests.

Run by .github/workflows/trello-sync.yml. It finds Trello card links in the
pull request description, then:

- PR opened or reopened  -> moves the card to "Review / PR" and comments the PR link
- PR merged              -> moves the card to "Done", marks its due date complete, comments

Needs the repository secrets TRELLO_KEY and TRELLO_TOKEN. Without them it
prints a note and exits cleanly, so forks and local runs never fail.
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request

API = "https://api.trello.com/1"
CARD_LINK = re.compile(r"trello\.com/c/([A-Za-z0-9]{8})")
REVIEW_LIST = "Review / PR"
DONE_LIST = "Done"


def card_ids(text):
    """Unique Trello card short links found in a block of text, in order."""
    seen = []
    for match in CARD_LINK.findall(text or ""):
        if match not in seen:
            seen.append(match)
    return seen


def call(method, path, key, token, **params):
    params.update(key=key, token=token)
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read() or "null")


def find_list(card, name, key, token):
    lists = call("GET", f"boards/{card['idBoard']}/lists", key, token)
    for lst in lists:
        if lst["name"].strip().lower() == name.lower():
            return lst["id"]
    return None


def sync(event, key, token):
    pr = event["pull_request"]
    action = event["action"]
    merged = action == "closed" and pr.get("merged")
    if action not in ("opened", "reopened") and not merged:
        print(f"Nothing to do for '{action}'.")
        return
    target = DONE_LIST if merged else REVIEW_LIST
    for short in card_ids(pr.get("body")):
        card = call("GET", f"cards/{short}", key, token, fields="idBoard,name")
        list_id = find_list(card, target, key, token)
        if list_id:
            updates = {"idList": list_id, "pos": "top"}
            if merged:
                updates["dueComplete"] = "true"
            call("PUT", f"cards/{short}", key, token, **updates)
        if merged:
            note = f"Merged PR #{pr['number']} into {pr['base']['ref']}: {pr['html_url']}"
        else:
            note = f"Opened PR #{pr['number']} \"{pr['title']}\": {pr['html_url']}"
        call("POST", f"cards/{short}/actions/comments", key, token, text=note)
        print(f"{card['name']}: moved to {target}")


def main():
    key, token = os.environ.get("TRELLO_KEY"), os.environ.get("TRELLO_TOKEN")
    if not key or not token:
        print("TRELLO_KEY / TRELLO_TOKEN not set; skipping Trello sync.")
        return 0
    with open(os.environ["GITHUB_EVENT_PATH"], encoding="utf-8") as f:
        sync(json.load(f), key, token)
    return 0


if __name__ == "__main__":
    sys.exit(main())
