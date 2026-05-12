# Phase 2 Cadence Playbook — singaporerabbit.com BAU

Two batches a week. Cadence doubled from Sunday-only (2 + 1) to Wed + Sun
(2 + 1 each = 4 articles + 2 directory entries per week, ~200/year). pet
niche is uncompetitive relative to the SMP/cloudfone factory you already run —
out-produce it.

## When

- **Wednesday batch**: 2 articles + 1 directory entry, evening session (~90 min)
- **Sunday batch**: 2 articles + 1 directory entry, ~2 hours (this is the
  original Sunday slot)

Either batch can be skipped one week per month without breaking the cadence,
but never two in a row.

## 0. Auto-generated inputs (already in repo)

A launchd job runs `npm run brief` every Sunday 8:57am SGT. Open the latest
brief for whichever batch you are on:

```
ls -1t src/content/_briefs/*.md | head -1
```

The Sunday brief drives both Wednesday and Sunday batches that week.

## 1. Pick angles (10 min)

Open the brief. Cross out angles you do not want. Replace each keeper's
title + target query + H2s with your pick.

Source for picks (in priority order):
- gaps in `src/content/_briefs/cornerstones.md` tracking table
- recurring r/Rabbits / r/SingaporePets themes from the brief
- GSC queries getting impressions but no clicks (Phase 2 doc)
- commercial-intent gaps (e.g., "best timothy hay singapore", "cheapest rabbit
  boarding") — these monetise via affiliate links once the inventory is built

## 2. Draft (90 min — Claude direct Edit/Write, NOT codex)

Per `feedback_claude_not_codex_for_writing` — do this in the main Claude session
with the Write tool. Codex delegation degrades voice quality.

Format checklist per article:
- frontmatter: title (no caps after periods), description, summary (160-640 char), tags
- `contributor: xavier-fok` on all health, safety, and YMYL-adjacent posts
- `schema_type: HowTo` for step-based content (litter training, bonding, nail trim, first week setup), else `Article`
- 1,200-1,800 word target
- ≥3 internal links per article, including ≥1 to `/vets/` and ≥1 to another guide
- "## what owners often get wrong" section near the end
- "## related reading" footer with 3-4 links
- closing disclaimer: "community-sourced information here is not veterinary advice..."

Format checklist per directory entry:
- frontmatter passes `npm run check:directory` (HEAD-checks source_url)
- summary 80-480 chars
- `## related care guides` footer with 3 type-appropriate links
- coords lat ∈ [1.0, 1.5], lng ∈ [103.0, 104.5]
- use Google Maps search URL as source_url if first-party fails HEAD check
- **never fabricate businesses**. if you cannot verify a real listing, skip
  the directory entry that batch and add another article instead.

## 3. Validate (5 min)

```
npm run check && npm run check:directory
```

Both must return 0 errors. Fix anything that flags.

## 4. Deploy + ping (5 min)

```
set -a && source .env && set +a && npm run deploy
```

Deploy script auto-pings IndexNow after smoke test. Confirm `indexnow: 200 for N urls`.

Verify after deploy:
- `curl -s https://singaporerabbit.com/robots.txt | head -5` returns content
- `curl -s https://singaporerabbit.com/llms.txt | head -5` returns content
- `curl -s https://singaporerabbit.com/rss.xml | head -5` returns xml

## 5. Commit + push (3 min)

```
git add src/content/guides/<new>.mdx src/content/<other-new-files>
git commit -m "content: week N <batch> — <topic1> + <topic2> + <directory-type>

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
git push origin main
```

## 6. Update tracking (5 min)

Update `src/content/_briefs/cornerstones.md` tracking table — but only if the
topic was a listed cornerstone gap. New post-cornerstone topics live in the
brief archive.

## Weekly self-check

End of each Sunday batch, answer:
- did we ship 4 articles + 2 directory entries this week? if not, why?
- did any link rule break (orphan guide, directory entry without related-guides footer)?
- did indexnow ping succeed both deploys?
- did any directory entry get flagged for re-verification (>180 days)?
- next week's brief: any backlog from this week to carry forward?

## Phase 2 milestones (revised for 2x cadence)

- 12 weeks of BAU = 48 articles + 24 directory entries on top of Phase 1
- target by week 12: 80+ guides, 50+ directory entries across at least 4 of 6 directory types
- by month 3, audit GSC for top-impression / no-click queries — that becomes brief priority
- by month 6, ship 5 commercial-intent comparison guides (hay brands, pellets, boarders)
  to unlock affiliate revenue
