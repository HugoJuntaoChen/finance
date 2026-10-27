#!/usr/bin/env bash
# Fetch a LIVE X/Twitter profile timeline or single post, bypassing X's
# anonymous-access block (HTTP 402) and stale mirror snapshots.
#
# Usage:
#   ./fetch_live_x.sh <handle>              # live profile timeline
#   ./fetch_live_x.sh <handle> <status_id>  # full text of one post + replies
#
# STATUS (re-probed 2026-09-02): all three routes below are currently dead or
# walled for this network. r.jina.ai -> 401 "bad IP reputation"; syndication
# -> 2 stale pinned tweets at best; xcancel -> 321-byte stub page (HTTP 200 but
# no timeline). They worked 2026-08-19..21 and broke on 2026-08-25.
# LEAD WITH scripts/fetch_serenity_posts.py (GitHub archive, ~8h lag). Use this
# script only to probe for the last few hours or one specific status id, and
# report failure to the user instead of retrying across many mirrors.
#
# Source priority (when the routes are alive):
#   1. r.jina.ai reader proxy  -> LIVE content, includes post published-time,
#      full text after "Show more", and top replies. Primary.
#   2. syndication.twitter.com -> official widget API; frequently rate-limited
#      ("Rate limit exceeded"); worth one retry, JSON in __NEXT_DATA__.
#   3. xcancel.com             -> renders well via server-side fetch BUT serves
#      a cached snapshot that can lag HOURS. Last resort; always report the
#      staleness ("Nh ago" timestamps are relative to xcancel's capture time,
#      not now).
# Direct x.com fetch without login returns HTTP 402. Most nitter instances
# (nitter.net, nitter.space, poast, lightbrd, tiekoetter, privacydev, twiiit)
# are dead or captcha-walled.

set -u
HANDLE="${1:?usage: fetch_live_x.sh <handle> [status_id]}"
STATUS="${2:-}"

if [ -n "$STATUS" ]; then
  TARGET="https://x.com/${HANDLE}/status/${STATUS}"
else
  TARGET="https://x.com/${HANDLE}"
fi

echo "### source: r.jina.ai (live) -> ${TARGET}"
if curl -sf --max-time 30 "https://r.jina.ai/${TARGET}"; then
  exit 0
fi

echo "### r.jina.ai failed; trying syndication API"
curl -sf --max-time 20 \
  "https://syndication.twitter.com/srv/timeline-profile/screen-name/${HANDLE}" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" \
  | python3 -c '
import sys, re, json
raw = sys.stdin.read()
m = re.search(r"<script id=\"__NEXT_DATA__\" type=\"application/json\">(.*?)</script>", raw, re.S)
if not m:
    print("syndication unavailable:", raw[:120])
    sys.exit(1)
d = json.loads(m.group(1))
from datetime import datetime, timezone, timedelta
tweets = [e.get("content", {}).get("tweet", {}) for e in d["props"]["pageProps"]["timeline"]["entries"]]
tweets = [t for t in tweets if t]
fmt = "%a %b %d %H:%M:%S %z %Y"
newest = max((datetime.strptime(t["created_at"], fmt) for t in tweets if t.get("created_at")), default=None)
for t in tweets:
    print("===", t.get("created_at"), "id", t.get("id_str"))
    print(t.get("full_text", ""))
    print()
if newest is None or datetime.now(timezone.utc) - newest > timedelta(days=2):
    age = "unknown" if newest is None else f"{(datetime.now(timezone.utc) - newest).days}d"
    print(f"### syndication STALE: {len(tweets)} tweets, newest is {age} old (pinned only). Not a live timeline.")
    sys.exit(1)
' && exit 0

echo "### syndication failed; falling back to xcancel (WARNING: cached snapshot, may lag hours)"
BODY="$(curl -sf --max-time 20 "https://xcancel.com/${HANDLE}" || true)"
if [ "${#BODY}" -lt 2000 ]; then
  echo "### xcancel returned a ${#BODY}-byte stub (anti-bot / dead). All live routes failed."
  echo "### Fall back to: python3 scripts/fetch_serenity_posts.py --days 3 --refresh --all"
  exit 1
fi
printf "%s\n" "$BODY"
