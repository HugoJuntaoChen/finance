# Changelog

## 1.2.0 — 2026-09-08

- `fetch_serenity_posts.py` now reads `https://serenity-webhook.pages.dev/feed` (the JSON behind aichainmap.com/serenity) first: ~200 latest posts, full long-form text, Chinese translation (`--cn`), quoted/reply context, minutes of lag. GitHub archive kept as fallback / history (`--source archive`).
- SKILL.md updated accordingly.

## 1.1.1 — 2026-09-07

- Added `scripts/fetch_x_status.py`: single-post fetch via the public syndication endpoint (works while timeline mirrors are walled).
- `fetch_serenity_posts.py` now re-clones when the temp archive dir was gutted by macOS tmp cleanup (checks `.git/HEAD`).

## 1.1.0 — 2026-09-02

- Added `scripts/fetch_serenity_posts.py`: reads @aleabitoreddit's recent posts (and optionally replies) from the public `yan-labs/serenity-aleabitoreddit` GitHub archive, printed in Beijing time with likes/views/permalinks.
- Added `scripts/fetch_live_x.sh`: live X timeline/post probe (r.jina.ai -> syndication -> xcancel) with stub-page detection; documented that all routes have been blocked since 2026-08-25.
- Added a "Reading Serenity's own posts" section to SKILL.md: 白毛女 nickname decode, archive-first rule, lag reporting, and treat-posts-as-leads-not-proof guidance.
- Added trigger phrases for "看一下白毛女 / Serenity 最近说了什么" to the description.
- Updated `references/research-sources.md` with the archive link and live-route status.

## 1.0.0 — 2026-05-04

- Reworked the Skill around a default deep-research workflow.
- Added source-backed theme scanning, current-data rules, and plain-language output guidance.
- Added research-partner conversation behavior for idea discussion and method training.
- Added market-specific source paths and evidence grading references.
- Updated README.md as the English GitHub entry point and added README.zh-CN.md.
- Added an AI infrastructure value-chain demo.
- Removed launch-copy and social-post drafts from the Skill package.
