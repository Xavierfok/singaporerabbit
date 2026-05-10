# singaporerabbits.com

community digest + curator for Singapore rabbit owners. Astro 5 static site, markdown-first, no
WordPress. strategy + roadmap live in [PLAN.md](./PLAN.md).

## quickstart

```bash
npm install
npm run dev          # local dev at http://localhost:4321
npm run build        # production build to dist/, runs pagefind
npm run preview      # serve dist/ locally
npm run check        # astro typecheck
npm run check:directory  # validate directory entries (last_verified < 180d, source_url alive)
npm run brief        # generate this week's content brief
```

## repo layout

```
src/
├── content/
│   ├── config.ts                          # zod schemas for all collections
│   ├── guides/                            # care guides (mdx)
│   ├── faq/                               # owner faq (mdx)
│   ├── breeds/                            # breed pages (mdx)
│   ├── directory/{vets,groomers,boarding,shops,rescues,breeders}/  # business listings (mdx)
│   ├── contributors/                      # contributor bios (mdx)
│   ├── policy/                            # about/contact/disclaimer/editorial-policy (mdx)
│   ├── news/                              # short SG-rabbit-news posts (mdx)
│   └── _briefs/                           # generated weekly briefs + the cornerstone burst
├── layouts/                               # BaseLayout + Article/FAQ/Directory/Breed/Hub
├── components/                            # Schema, Breadcrumb, SummaryBlock, KeyFacts, etc.
├── pages/                                 # static + dynamic routes
├── lib/site.ts                            # site config + nav constants
└── styles/global.css
scripts/
├── weekly-brief.ts                        # generate weekly brief
├── validate-directory.ts                  # pre-build directory validator
└── indexnow-ping.ts                       # post-deploy IndexNow ping
public/
├── favicon.svg
├── og-default.png
└── .well-known/security.txt
```

## adding a care guide

1. create `src/content/guides/{slug}.mdx`. frontmatter required:

```mdx
---
title: how to buy timothy hay in Singapore
description: a 160-char meta description.
summary: 40–80 words plain prose. ChatGPT/Perplexity will extract this. answer the headline directly.
last_updated: 2026-05-10
published: 2026-05-10
contributor: someone-slug   # optional, must match a file in src/content/contributors/
schema_type: Article
tags: [hay, food, sg-shops]
affiliate_disclosure: false
---

# headline (h1 from layout, omit here if you want — or repeat)

your content...
```

2. ensure ≥3 internal links — at least one to `/vets/` (or another directory page) and at least
   one to a related guide.
3. ship the cornerstone heat-stroke-prevention link in any health-adjacent post.
4. run `npm run check` + `npm run build` locally before committing.
5. run the [humanizer skill](https://example.invalid) (already in your `~/.claude/skills/`)
   on the prose before merge.

## adding a directory entry

1. pick the right type folder: `src/content/directory/{vets|groomers|boarding|shops|rescues|breeders}/`.
2. filename = url slug (kebab-case).
3. frontmatter required (see `src/content/config.ts` for the full schema):

```mdx
---
name: My Pets Vet Clinic
type: vets
address: 123 Orchard Rd, Singapore 238888
region: central
phone: +65 6123 4567
website: https://example.com
hours:
  mon: 9am-6pm
  tue: 9am-6pm
  wed: 9am-6pm
  thu: 9am-6pm
  fri: 9am-6pm
  sat: 9am-1pm
  sun: closed
lat: 1.3048
lng: 103.8318
sees_rabbits: true
source_url: https://example.com/about
last_verified: 2026-05-10
featured: false
summary: 80–480 char description. SG-specific. note rabbit experience explicitly.
schema_type: LocalBusiness
tags: [exotic-pet, central]
---

optional long-form notes about the business — staff names, your visit experience, etc.
```

4. `npm run check:directory` before committing. fail = stale `last_verified` (>180d) or dead
   source_url. for newly-added entries this should never trigger.

## the 5-hour weekly cycle

per PLAN.md:

| day | minutes | task |
|---|---|---|
| sun | 30 | `npm run brief` → fill in 2-3 angles you'll write this week |
| mon | 60 | manual FB-group capture into `src/content/_briefs/notes.md` (themes only, no names) |
| tue | 30 | reddit-fetch r/Rabbits + r/SingaporePets last 7d → `src/content/_briefs/reddit-fetch.json` |
| wed | 60 | claude drafts 1 care guide + 1 faq from the brief |
| thu | 60 | edit drafts, run humanizer, run `npm run check` |
| fri | 30 | one new directory entry + verify 2 existing entries |
| sat | 30 | merge, push, IndexNow ping fires automatically on deploy |

## deploy

vercel project will be connected manually (see [PLAN.md](./PLAN.md) §"What's NOT done in this
session"). once connected:

```bash
git push origin main      # vercel auto-deploys
INDEXNOW_KEY=<key> npm run indexnow   # post-deploy, pings bing/yandex
```

vercel build command: `npm run build`. output dir: `dist/`. install command: `npm install`.

## env vars

| var | used by | required for |
|---|---|---|
| `INDEXNOW_KEY` | scripts/indexnow-ping.ts | post-deploy ping |
| `INDEXNOW_KEY_LOC` | scripts/indexnow-ping.ts | only if key file isn't at site root |
| `SITE_URL` | scripts/indexnow-ping.ts | only if site differs from singaporerabbits.com |

(no env vars needed for build itself.)

## content checklist before merging a PR

- [ ] frontmatter validates (`npm run check`)
- [ ] summary is 40–80 words, plain prose (extract target for ChatGPT/Perplexity)
- [ ] last_updated set to today
- [ ] ≥3 internal links, ≥1 to a directory page
- [ ] medical posts: "community-sourced information, not veterinary advice" disclaimer in first
      100 words
- [ ] medical posts: link to /vets/ in body or footer
- [ ] photo credits documented (your photo / contributor name / stock attribution)
- [ ] humanizer skill run on prose
- [ ] no FB-sourced photos, no member names
- [ ] affiliate links: disclosure banner present if any used

## known follow-ups (handed off, not in this scaffold)

- register `singaporerabbits.com` at Cloudflare Registrar
- connect vercel project to GitHub
- cloudflare DNS (A/AAAA → vercel, CNAME for www)
- google analytics 4 + google search console + plausible
- buttondown account + replace `formAction` in `src/lib/site.ts`
- IndexNow API key (random uuid → host `<key>.txt` at site root)
- write 25 cornerstone posts per `src/content/_briefs/cornerstones.md`
- recruit 5 SG owner contributors via FB DM

## kill criteria

per PLAN.md §"Kill criteria": if at month 12 you have <500 organic sessions/mo AND no
monetization signal AND your interest has waned, mothball gracefully. 5 hr/week × 12 mo = 260
hr investment cap before pivot decision.

## license + ownership

private until launched. owner: Xavier Fok. content licensed under all-rights-reserved unless
otherwise specified per-post. directory listings: facts (name/address/phone/hours) are not
copyrightable; our editorial summaries are.
