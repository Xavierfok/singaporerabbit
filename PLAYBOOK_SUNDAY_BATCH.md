# Sunday Batch Playbook — singaporerabbit.com BAU

Run every Sunday, ~2 hours total. Goal: 2 articles + 1 directory entry shipped.

## 0. Auto-generated inputs (already in repo)

A launchd job runs `npm run brief` every Sunday 8:57am SGT. Open the latest:

```
ls -1t src/content/_briefs/*.md | head -1
```

## 1. Pick 3 angles (10 min)

Open the brief. Cross out 2 of the 3 placeholder angles you do not want. Replace the
keeper's title + target query + H2s with your pick.

Source for picks (in priority order):
- gaps in `src/content/_briefs/cornerstones.md` tracking table
- recurring r/Rabbits / r/SingaporePets themes from the brief
- GSC queries getting impressions but no clicks (see Phase 2 doc)
- empty directory subfolders: `/groomers/`, `/breeders/` (4 of 6 dir types still empty)

## 2. Draft (90 min — Claude direct Edit/Write, NOT codex)

Per `feedback_claude_not_codex_for_writing` — do this in the main Claude session
with the Write tool. Codex delegation degrades voice quality.

Format checklist per article:
- frontmatter: title (no caps after periods), description, summary (160-640 char), tags
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

## 5. Commit + push (3 min)

```
git add src/content/guides/<new>.mdx src/content/<other-new-files>
git commit -m "content: week N BAU — <topic1> + <topic2> + <directory-type>

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
git push origin main
```

## 6. Update tracking (5 min)

Update `src/content/_briefs/cornerstones.md` tracking table — but only if the topic was a
listed cornerstone gap. New post-cornerstone topics live in the brief archive.

## Weekly self-check

End of each batch, answer:
- did we ship 2 articles + 1 directory entry? if not, why?
- did any link rule break (orphan guide, directory entry without related-guides footer)?
- did indexnow ping succeed?
- next week's brief: any backlog from this week to carry forward?

## Phase 2 milestones

- 12 weeks of BAU = 24 articles + 12 directory entries on top of Phase 1
- target by week 12: 50+ guides, 40+ directory entries across all 6 directory types
- by month 3, audit GSC for top-impression / no-click queries — that becomes brief priority
