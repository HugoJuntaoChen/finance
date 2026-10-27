#!/usr/bin/env python3
"""Read Serenity's (@aleabitoreddit) recent X posts from the public GitHub archive.

WHY THIS EXISTS: as of 2026-08-25 every live-scrape route is dead or walled —
r.jina.ai returns 401 (IP reputation), xcancel/nitter.* serve anti-bot pages,
lightbrd + trackserenity return nothing, and syndication.twitter.com only yields
two stale pinned tweets. The yan-labs archive is a Codex heartbeat job that
mirrors the full timeline (main posts AND replies, with metrics) and typically
runs only a few hours behind live. Note data/sync_state.json understates
freshness — trust the max createdAt in the JSON, not last_update_time.

PRIMARY SOURCE (added 2026-09-08): the JSON feed behind the Chinese tracker
aichainmap.com/serenity -> https://serenity-webhook.pages.dev/feed . It holds
the last ~200 posts with FULL long-form text, a Chinese translation, metrics,
quoted/replied-to context, and lags live by minutes, not hours. The GitHub
archive is the fallback (and the only source for history older than ~2 weeks).

Usage:
    fetch_serenity_posts.py [--days N] [--all] [--refresh] [--repo-dir DIR]
                            [--source auto|feed|archive] [--cn]

    --days N     look back N days (default 3)
    --all        include @-replies (default: main posts only)
    --refresh    git pull (or clone) before reading
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys

REPO = "https://github.com/yan-labs/serenity-aleabitoreddit.git"
FEED = "https://serenity-webhook.pages.dev/feed"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36"}
DEFAULT_DIR = os.path.join(
    os.environ.get("TMPDIR", "/tmp"), "serenity-archive"
)
TW_FMT = "%a %b %d %H:%M:%S %z %Y"
BJ = dt.timezone(dt.timedelta(hours=8))


def ensure_repo(path, refresh):
    if not os.path.isfile(os.path.join(path, ".git", "HEAD")):
        if os.path.isdir(path):
            # stale/partial dir left behind by tmp cleanup -> re-clone
            import shutil
            shutil.rmtree(path, ignore_errors=True)
        subprocess.run(["git", "clone", "--depth", "1", REPO, path], check=True)
    elif refresh:
        subprocess.run(["git", "-C", path, "pull", "--ff-only"], check=False)


def parse_ts(tweet):
    try:
        return dt.datetime.strptime(tweet.get("createdAt", ""), TW_FMT)
    except ValueError:
        return dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc)


def load_feed():
    import urllib.request
    d = json.load(urllib.request.urlopen(urllib.request.Request(FEED, headers=UA), timeout=25))
    out = []
    for t in d.get("tweets", []):
        ts = dt.datetime.fromisoformat(t["posted_at"].replace("Z", "+00:00"))
        m = t.get("metrics") or {}
        out.append({
            "id": t["id"], "ts": ts, "text": t.get("text", ""), "text_cn": t.get("text_cn", ""),
            "is_reply": bool(t.get("is_reply")), "is_retweet": bool(t.get("is_retweet")),
            "likes": m.get("likes", "?"), "views": m.get("views", "?"),
            "quote": (t.get("quoted") or t.get("quote") or {}).get("text", "") if isinstance(t.get("quoted") or t.get("quote"), dict) else "",
            "reply_to": (t.get("reply_to") or {}).get("text", "") if isinstance(t.get("reply_to"), dict) else "",
        })
    return out


def load_archive(repo_dir, refresh):
    ensure_repo(repo_dir, refresh)
    raw = json.load(open(os.path.join(repo_dir, "data", "aleabitoreddit_tweets.json")))
    tweets = raw if isinstance(raw, list) else raw.get("tweets", raw)
    out = []
    for t in tweets:
        m = t.get("metrics") or {}
        out.append({
            "id": t.get("id"), "ts": parse_ts(t), "text": t.get("text", ""), "text_cn": "",
            "is_reply": t.get("text", "").startswith("@"), "is_retweet": bool(t.get("isRetweet")),
            "likes": m.get("likes", "?"), "views": m.get("impressions") or m.get("views") or "?",
            "quote": "", "reply_to": "",
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=3)
    ap.add_argument("--all", action="store_true", help="include @-replies")
    ap.add_argument("--refresh", action="store_true", help="git pull the archive (archive source only)")
    ap.add_argument("--repo-dir", default=DEFAULT_DIR)
    ap.add_argument("--source", choices=["auto", "feed", "archive"], default="auto")
    ap.add_argument("--cn", action="store_true", help="also print the Chinese translation (feed only)")
    args = ap.parse_args()

    rows, src = [], ""
    if args.source in ("auto", "feed"):
        try:
            rows, src = load_feed(), "feed"
        except Exception as e:
            print(f"# feed unavailable ({e}); falling back to archive", file=sys.stderr)
    if not rows and args.source in ("auto", "archive"):
        rows, src = load_archive(args.repo_dir, args.refresh), "archive"

    now = dt.datetime.now(dt.timezone.utc)
    newest = max(r["ts"] for r in rows)
    lag = (now - newest).total_seconds() / 3600
    print(f"# source: {src} | {len(rows)} tweets | newest {newest.astimezone(BJ):%Y-%m-%d %H:%M} Beijing (lag {lag:.1f}h)\n")

    cutoff = now - dt.timedelta(days=args.days)
    sel = [r for r in rows if r["ts"] >= cutoff and not r["is_retweet"] and (args.all or not r["is_reply"])]
    sel.sort(key=lambda r: r["ts"])
    for r in sel:
        kind = "REPLY" if r["is_reply"] else "POST"
        print(f"### {kind} {r['ts'].astimezone(BJ):%m-%d %H:%M} Beijing | likes {r['likes']} views {r['views']}"
              f" | https://x.com/aleabitoreddit/status/{r['id']}")
        print(r["text"])
        if r["quote"]:
            print("  > quoting:", r["quote"][:500])
        if r["reply_to"]:
            print("  > replying to:", r["reply_to"][:300])
        if args.cn and r["text_cn"]:
            print("  [CN]", r["text_cn"])
        print("-" * 70)
    if not sel:
        print(f"(no posts in the last {args.days} days)", file=sys.stderr)
    if src == "archive":
        print("# NOTE: archive source; long posts are truncated at ~300 chars and lag is typically 8-70h.", file=sys.stderr)


if __name__ == "__main__":
    main()
