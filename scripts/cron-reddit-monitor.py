#!/usr/bin/env python3
"""daily reddit monitor for r/Rabbits + r/SingaporePets.

writes src/content/_briefs/reddit-fetch.json in the format the weekly-brief
script consumes. ranks posts by an engagement score (upvotes + comments * 5)
to surface high-discussion threads, not just upvoted ones.

filters r/SingaporePets for rabbit-related keywords since most posts in that
sub are dog/cat.

cron: weekly Sun 6am SGT via Library/LaunchAgents/com.xavier.singaporerabbit.reddit-monitor.plist
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

OUT = Path(__file__).resolve().parent.parent / "src" / "content" / "_briefs" / "reddit-fetch.json"
LOG = Path(__file__).resolve().parent.parent / ".logs" / "reddit-monitor.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

UA = "singaporerabbit-monitor/1.0 (https://singaporerabbit.com)"
HEADERS = {"User-Agent": UA}

# r/SingaporePets needs filtering since most posts are dog/cat
RABBIT_TERMS = (
    "rabbit",
    "bunny",
    "bunnies",
    "lop",
    "lionhead",
    "netherland",
    "rex",
    "buns",
    "house rabbit",
)

SUBREDDITS = [
    ("Rabbits", None),  # all posts
    ("SingaporePets", RABBIT_TERMS),  # filter
    ("rabbitsneedlove", None),
    ("Bunnies", None),
]


def fetch_top(sub: str, time: str = "week", limit: int = 25) -> list[dict]:
    url = f"https://old.reddit.com/r/{sub}/top.json?t={time}&limit={limit}"
    try:
        r = httpx.get(url, headers=HEADERS, timeout=15, follow_redirects=True)
        r.raise_for_status()
        return [c.get("data", {}) for c in r.json().get("data", {}).get("children", [])]
    except Exception as e:
        log(f"fetch {sub}: ERROR {e}")
        return []


def matches_filter(post: dict, terms: tuple[str, ...] | None) -> bool:
    if terms is None:
        return True
    haystack = (post.get("title", "") + " " + post.get("selftext", "")).lower()
    return any(t in haystack for t in terms)


def normalize(post: dict, sub: str) -> dict:
    ups = int(post.get("ups", 0))
    comments = int(post.get("num_comments", 0))
    return {
        "subreddit": sub,
        "title": post.get("title", "").strip(),
        "url": f"https://www.reddit.com{post.get('permalink', '')}",
        "ups": ups,
        "comments": comments,
        "score": ups + comments * 5,  # comments weighted higher (discussion signal)
        "selftext_excerpt": (post.get("selftext", "") or "")[:300].strip(),
        "created_utc": post.get("created_utc"),
        "flair": post.get("link_flair_text"),
    }


def log(msg: str) -> None:
    with LOG.open("a") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')} {msg}\n")


def main() -> int:
    log("=== reddit monitor start ===")
    all_posts: list[dict] = []
    for sub, terms in SUBREDDITS:
        raw = fetch_top(sub, time="week", limit=25)
        kept = [normalize(p, sub) for p in raw if matches_filter(p, terms)]
        log(f"r/{sub}: {len(raw)} raw, {len(kept)} kept")
        all_posts.extend(kept)

    # rank globally by engagement score, top 20
    all_posts.sort(key=lambda p: p["score"], reverse=True)
    top = all_posts[:20]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "sources": [s[0] for s in SUBREDDITS],
        "posts": top,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2))
    log(f"wrote {len(top)} posts to {OUT}")
    return 0 if top else 1


if __name__ == "__main__":
    sys.exit(main())
