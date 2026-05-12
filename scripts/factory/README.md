# Content Factory

Daily 10am SGT autonomous draft generator for singaporerabbit.com.

## How it works

1. cron triggers `cron.sh`
2. picks oldest `queued` topic from `queue.json`
3. generates MDX via `claude --print --model sonnet` (subscription, not paid API)
4. humanizer pass (second claude call, strips AI tells)
5. lints (word count, required sections, schema, em-dash limit, banned phrases)
6. if pass: writes to `src/content/guides/<key>.mdx`, commits to `auto-drafts/<key>` branch, pushes to GitHub, marks topic `drafted`
7. if fail: marks topic `failed`, TG-notifies. Does NOT write.

Drafts do NOT auto-publish. You review the PR (open `https://github.com/Xavierfok/singaporerabbit/branches`), merge if good, then run `npm run deploy` locally.

## First-run checklist

```
# 1. dry-run to verify claude CLI + lint pipeline
cd /Users/foktunghoe/Desktop/singaporerabbits
python3 scripts/factory/generate.py --key rabbit-pee-blood-emergency --dry-run
# inspect scripts/factory/.factory-out/rabbit-pee-blood-emergency.mdx

# 2. real run on one topic
python3 scripts/factory/generate.py --key first-aid-kit-rabbit-singapore
# check Github for branch auto-drafts/first-aid-kit-rabbit-singapore

# 3. once happy with output quality:
launchctl load ~/Library/LaunchAgents/com.xavier.singaporerabbit.factory.plist
```

## Daily volume

One draft per day. ~7 drafts per week, ~365/year. Compared to your manual Wed+Sun batches (4 articles/wk, 200/year), factory adds another ~165/yr at zero per-article time cost.

## Tuning prompts

`prompts.py` controls voice and structure. After 4-5 drafts, look at the output, see what's still off (too generic, wrong voice, weak SG-specificity), and tighten the prompt. Most of the leverage is here.

## Disabling autonomously

```
launchctl unload ~/Library/LaunchAgents/com.xavier.singaporerabbit.factory.plist
```

Topics already drafted stay drafted; the cron just stops firing.

## Cost

- Sonnet via Claude Code subscription: $0 marginal cost
- ~2 generations per topic (draft + humanizer) = ~2 messages/day = well within free tier

## Failure modes

- **claude CLI not in PATH**: cron.sh sets `/Users/foktunghoe/.local/bin/claude`. If you move it, update `claude_call.py:CLAUDE_BIN`.
- **lint fails 3 days in a row**: topic prompts probably need tightening. Look at `.failed.mdx` files in `.factory-out/`.
- **git push fails**: usually a stale main. cron.sh does `git fetch + checkout main + pull` first, so this is rare.

## After AUTO_MERGE flip

After 30 days of manual review confirming quality, set `AUTO_MERGE = True` in `generate.py:35` to skip the branch step and commit straight to main. Pair with `npm run deploy` in the cron if you want full autonomous publish.
