#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://www.moltbook.com/api/v1"
CREDENTIALS_PATH = os.path.expanduser("~/.config/moltbook/credentials.json")


def load_api_key(explicit_key: str | None) -> str:
    if explicit_key:
        return explicit_key
    env_key = os.environ.get("MOLTBOOK_API_KEY")
    if env_key:
        return env_key
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


def request(method: str, path: str, api_key: str, payload: dict | None = None) -> None:
    url = f"{BASE_URL}{path}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "moltbook-post-script/1.0",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
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
    parser = argparse.ArgumentParser(description="Create a Moltbook post.")
    parser.add_argument("--api-key", help="API key (overrides env/file)")
    parser.add_argument("--submolt", default="general", help="Submolt name (default: general)")
    parser.add_argument("--title", required=True, help="Post title")
    parser.add_argument("--content", help="Text content")
    args = parser.parse_args()

    api_key = load_api_key(args.api_key)

    payload = {"submolt": args.submolt, "title": args.title}
    if args.content:
        payload["content"] = args.content

    request("POST", "/posts", api_key, payload)


if __name__ == "__main__":
    main()
