#!/usr/bin/env python3
"""Fetch single X posts by status id via the public syndication endpoint.

Works without login (verified 2026-09-07) when timeline mirrors are walled.
Limits: long-form posts come back truncated at ~280 chars (no note_tweet),
so use it to (a) confirm a post exists / its timestamp, (b) read short posts,
(c) fetch the quoted post. Combine with fetch_serenity_posts.py for the bulk.

Usage: fetch_x_status.py <status_id> [<status_id> ...]
"""
import json, math, re, sys, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36"}

def token(i: str) -> str:
    n = (int(i) / 1e15) * math.pi
    ip, frac = int(n), n - int(n)
    digs = "0123456789abcdefghijklmnopqrstuvwxyz"; out = ""
    while ip: out = digs[ip % 36] + out; ip //= 36
    out += "."
    for _ in range(12):
        frac *= 36; d = int(frac); out += digs[d]; frac -= d
    return re.sub(r"(0+|\.)", "", out)

def fetch(i: str) -> dict:
    u = f"https://cdn.syndication.twimg.com/tweet-result?id={i}&token={token(i)}"
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20))

def main():
    for i in sys.argv[1:]:
        try:
            d = fetch(i)
        except Exception as e:
            print(f"### {i} ERR {e}"); continue
        user = (d.get("user") or {}).get("screen_name", "?")
        print(f"### @{user} {d.get('created_at')} https://x.com/{user}/status/{i}")
        nt = d.get("note_tweet"); text = (nt.get("text") if isinstance(nt, dict) else None) or d.get("text", "")
        print(text)
        q = d.get("quoted_tweet")
        if isinstance(q, dict):
            print(f"  > quoting @{(q.get('user') or {}).get('screen_name','?')}: {q.get('text','')}")
        print("-" * 70)

if __name__ == "__main__":
    main()
