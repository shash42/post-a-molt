#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = "https://www.moltbook.com/api/v1"
CREDENTIALS_PATH = os.path.expanduser("~/.config/moltbook/credentials.json")


def load_api_key() -> str:
    if os.path.exists(CREDENTIALS_PATH):
        try:
            with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            key = data.get("api_key")
            if key:
                return key
        except (OSError, json.JSONDecodeError):
            pass
    print("Missing API key. Set MOLTBOOK_API_KEY or create ~/.config/moltbook/credentials.json", file=sys.stderr)
    sys.exit(2)


def request(path: str, api_key: str) -> None:
    url = f"{BASE_URL}{path}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "moltbook-status-script/1.0",
    }

    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                print(json.dumps(json.loads(body), indent=2, sort_keys=True))
            except json.JSONDecodeError:
                print(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}", file=sys.stderr)
        print(body, file=sys.stderr)
        sys.exit(1)


def main() -> None:
    api_key = load_api_key()
    request("/agents/status", api_key)


if __name__ == "__main__":
    main()
