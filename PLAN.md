# singaporerabbits.com — long-term SEO build plan

## Context

You want a 5th SEO property as a passion + portfolio diversifier. Constraint: managed end-to-end by Claude + Codex (no WordPress admin, no PHP), 5 hr/week sustainable, no filming/video/recordings, pure aggregator/curator angle (you don't own a rabbit). Inputs you already have: SG rabbit owner FB groups (read-only, manual capture), Reddit (r/Rabbits) for global volume, willingness to do text Q&A with SG vets/breeders/shops. Monetization is sequenced — affiliate first, display ads second, lead-gen third, owned products fourth. Honest ceiling: SG TAM is small (~5-10k rabbit-owning households), so this is a 2-3 yr compounder, not a 6-month cash play. Treat it as your "learn the modern static-SEO + GEO stack" sandbox that also happens to throw off some lead-gen and affiliate revenue.

## Strategic positioning

Brand: **"Singapore Rabbits — what local owners actually ask, answered."**

- Position as a community **digest + curator**, not a vet. Every health/medical post links out to a real SG vet, never gives diagnostic advice. This is also your legal moat.
- Three content pillars (each becomes a top-nav category):
  1. **Care guides** (evergreen): housing, hay, diet, grooming, SG-climate-specific (humidity, AC, heat stroke).
  2. **Owner FAQ** (long-tail): mined from FB groups + r/Rabbits, rewritten in your own words, attributed to "owners commonly ask" not specific people.
  3. **SG directory** (the moat): vets that see rabbits, exotic-pet groomers, boarding for travel, hay/pellet stockists, rescues. This is what nobody else has structured for SG and it's what powers lead-gen later.
- E-E-A-T workaround for no-rabbit-ownership: **named contributor model**. Approach 2-3 SG owners (via the FB groups you already lurk) and offer "guest column" credit + photo credit in exchange for a quote/photo per piece. You're the editor, not the expert. Google rewards this if attribution is real.

## Tech stack (Claude + Codex friendly, no WP)

| Layer | Choice | Why |
|---|---|---|
| Framework | **Astro 5+** with Tailwind | Markdown-first content collection, zero-JS by default → perfect Core Web Vitals, ideal for AI-Overviews-friendly passages |
| Hosting | **Vercel** (free tier or Hobby) | Same vendor pattern you already use; git push = deploy |
| Repo | GitHub `xavierfok/singaporerabbits` (private→public when launched) | Codex/Claude edit markdown directly via PR, no admin login |
| DNS | Cloudflare | DDoS, IndexNow proxy, free analytics |
| Content | `src/content/` collections: `guides/`, `faq/`, `directory/`, `news/` | Frontmatter (title, description, schema_type, last_updated, contributor) drives meta + JSON-LD automatically |
| Search | **Pagefind** (static index, runs at build) | No backend, no DB, free, fast |
| Comments / community | **Giscus** (GitHub Discussions backed) | Free, anti-spam by default, doesn't block CWV |
| Newsletter | **Buttondown** ($9/mo when >100 subs) | Markdown emails, no design needed, RSS-to-email automation |
| Forms (vet/contributor signup, lead-gen) | **Formspark** or Cloudflare Workers + Resend | Static-site friendly, no PHP |
| Schema | Hand-rolled JSON-LD components (`<Schema type="Article" />`, `<Schema type="LocalBusiness" />` for directory) | You already have the seo-schema skill |
| Sitemap | `@astrojs/sitemap` + `@astrojs/rss` | Auto-generated on build |
| IndexNow | Cron-triggered ping after each deploy via Cloudflare Worker | Sub-hour Bing/Yandex pickup |
| Image pipeline | Astro `<Image>` (auto WebP/AVIF, lazy-load) + Cloudflare Images for hosted contributor photos | Zero CLS, Lighthouse 100 |
| Analytics | GA4 + Plausible (privacy fallback) + Search Console | All four already in your seo-google skill |

**Why not WordPress:** you said no. Also: with aggregator content, you need fast publish/edit cycles via PR diffs, which markdown gives you and WP doesn't. CWV ceiling on Astro is also ~30 points higher than DRT's WP+Astra (your own site).

**Why not Next.js:** more JS than this site needs, and the dynamic features (directory search, vet filter) all work statically with Pagefind + a single Cloudflare Worker for the lead-form handler.

## Site architecture

```
singaporerabbits.com/
├── /                              # Hero + 3 pillar links + latest 6 posts + newsletter signup
├── /care/                         # Care guides hub
│   ├── /care/feeding-singapore-climate/
│   ├── /care/heat-stroke-prevention/
│   ├── /care/hay-where-to-buy-singapore/
│   └── ...
├── /faq/                          # Owner Q&A hub (mined from FB + r/Rabbits)
│   └── /faq/{question-slug}/
├── /vets/                         # ★ the moat — directory landing
│   ├── /vets/{clinic-slug}/       # one page per SG rabbit-friendly vet
│   └── /vets/by-region/{north|south|east|west|central}/
├── /breeders/  /groomers/  /boarding/  /shops/  /rescues/   # same directory pattern
├── /breeds/                       # Holland Lop, Netherland Dwarf, Lionhead, Mini Rex (top SG breeds)
│   └── /breeds/{breed}/
├── /community/                    # owner stories, named-contributor columns
├── /about/  /contact/  /contributors/  /editorial-policy/  /disclaimer/
├── /sitemap.xml  /rss.xml  /llms.txt  /robots.txt
```

Key decisions:
- **Flat URLs, ≤2 levels deep**, kebab-case, no dates in slugs (evergreen).
- **`/vets/` and friends are pSEO-style**: one page per business, fed from a single `directory.json` that Codex maintains. Each gets `LocalBusiness` schema, drives Maps citation signals.
- **`/llms.txt` from day one** (you have the seo-geo skill) — passage-formatted bullets so ChatGPT/Perplexity cite you for SG rabbit queries even before you rank #1 on Google.
- **Internal linking convention**: every FAQ post links to ≥1 care guide and ≥1 directory page. Care guides link to ≥3 FAQs. Directory pages link back to the relevant care guide. This is what `seo-superpowers-portfolio` will enforce.

## Content strategy

### Source mix per week (5 hr budget)
- **2 hr** — Claude pulls fresh r/Rabbits + r/Pets posts via reddit-fetch skill, you skim, pick 3-5 question angles, paste into a research note.
- **1 hr** — manual FB group capture (anonymized themes, never copy-paste). You write 1-line summaries of recurring SG-specific issues.
- **1 hr** — Claude drafts 2 posts (1 care guide, 1 FAQ) from the research notes, runs humanizer skill, you review.
- **30 min** — directory maintenance: one new vet/groomer/shop entry per week (just metadata + your own visit summary).
- **30 min** — ship: PR review, merge, IndexNow ping, GSC inspection.

Yields **~104 posts/yr** + **~52 directory entries/yr** = ~150 indexed URLs by year 1, ~400 by year 2, ~700 by year 3. At ~30 sessions/URL/mo organic ceiling for low-comp SG pet niche, that's ~12k–20k sessions/mo by month 24, which is the Ezoic threshold.

### Cornerstone burst (month 1, 20 hr)
Before the 5 hr/week BAU starts, spend month 1 producing the 25 evergreen cornerstones that become every internal-link target:
- 5 breed deep-dives (Holland Lop, Netherland Dwarf, Lionhead, Mini Rex, Mini Lop)
- 8 care guides (feeding, hay, water, housing, heat/AC, grooming, vet visits, travel)
- 5 SG-specific (HDB-friendly cages, condo rules, where to buy hay in SG, exotic vet list, monsoon-season care)
- 5 "vs" comparisons (rabbit vs guinea pig as SG pet, bonded pairs vs solo, etc. — high-CTR)
- 2 directory landings (vets/, shops/) with first 10 entries each

After month 1: shift to 5hr/week BAU.

## SEO + GEO foundations (built-in from day 1)

- **Schema.org JSON-LD per template**: `Article` for guides/FAQ, `FAQPage` for FAQ posts, `LocalBusiness` for directory pages, `BreadcrumbList` site-wide, `Organization` on home.
- **GEO-readiness** (your seo-geo skill): every post has a 40-80 word `summary` block at the top in plain prose (Perplexity/ChatGPT extract this), bullet "key facts" section under H2s, citations with explicit dates.
- **`llms.txt`** at root listing all cornerstone pages for AI crawler shortcuts.
- **AI crawler allowlist** in `robots.txt`: GPTBot, ClaudeBot, PerplexityBot, Google-Extended explicitly allowed.
- **CWV target**: LCP <1.5s, INP <100ms, CLS 0 (achievable on Astro + Cloudflare Images + zero-JS pages).
- **Internal-link budget** enforced by a build-time check (Codex script: each post must have ≥3 internal outbound links, ≥1 to a directory page).
- **Sitemap pinging**: IndexNow to Bing/Yandex on every deploy, sitemap submission to GSC weekly via your seo-google skill.

## Monetization roadmap (phased)

| Month | Lever | Realistic expected |
|---|---|---|
| 0-3 | Nothing. Build content + DR. | $0 |
| 4-6 | Affiliate links (Shopee SG, Lazada SG, iHerb) on care guides. Disclosure footer. | $20-100/mo |
| 6-12 | "Featured vet/groomer/shop" tier on directory pages — $30/mo per business for top placement + photo. Sell 5-10 = $150-300/mo. | $200-500/mo total |
| 12-18 | Display ads via **Ezoic** once at 10k sessions/mo. SG pet RPM ~$8-15. | $500-1.5k/mo |
| 18-24 | First owned product: **"Singapore Rabbit Owner Handbook" PDF** ($12) + **"SG Rabbit Vet Directory" emailed quarterly update** as paid addon. | +$200-600/mo |
| 24+ | Lead-gen marketplace: pet sitter / boarding match form, $10-30 per qualified lead. | +$500-2k/mo |

**Honest ceiling at year 3**: $2-4k/mo SGD. Not life-changing, but fully passive after build. The ROI is the **stack mastery + the SG vet/shop relationships**, both of which transfer to other Singapore-niche sites later (singaporecats, singaporehamsters, etc.) once you've proven the playbook.

## Operating workflow (what 5 hr/week actually looks like)

You already have the agents/skills for nearly all of this:
- **seo-superpowers-portfolio** agent — run weekly to surface ranking opportunities, internal-link gaps, schema drift.
- **seo-content** skill — pre-publish content QA (E-E-A-T, readability, AI-citation readiness).
- **seo-page** skill — single-URL deep audit when a post stalls.
- **humanizer** skill — every draft passes through this before merge.
- **reddit-fetch** skill — Monday content sourcing.
- **seo-schema** skill — verify JSON-LD on every new template.
- **seo-google** skill — weekly GSC + GA4 + CrUX pull, one-line trend report.

New automation to build (one-shot, then cron):
- **Weekly content brief generator** (Codex script, runs Sundays): pulls top r/Rabbits posts of last 7 days + your FB notes file, outputs a Markdown brief with 3-5 article angles + suggested H2s + suggested internal links to existing posts.
- **Directory entry validator** (build-time check): every `directory/*.md` must have name, address, phone, hours, lat/lng, source URL, last_verified date.
- **Stale-content alert** (monthly cron): flags any post >180 days old where rankings dropped >5 positions in GSC.

## Compliance / risk

- **FB ToS**: never scrape automated, never republish member posts verbatim, never name members. Capture themes and rewrite. Document the policy in `editorial-policy.md`.
- **Veterinary advice liability**: medical posts always end with "this is community-sourced information, not veterinary advice — see a licensed SG exotic vet." Include the disclaimer in `disclaimer.md` and link from every health-related post footer.
- **Affiliate disclosure**: prominent footer disclosure, FTC-style (still good practice in SG).
- **PDPA**: any contributor or newsletter signup needs a privacy notice + double opt-in.
- **Photo copyright**: only use (a) your own photos, (b) named contributor photos with permission documented in repo, (c) properly licensed stock (Unsplash/Pexels with attribution where required), (d) never FB-sourced photos.

## Critical files to create (initial scaffold)

```
singaporerabbits/
├── astro.config.mjs                     # Astro 5 + tailwind + sitemap + rss + image
├── package.json                         # astro, @astrojs/tailwind, @astrojs/sitemap, @astrojs/rss, pagefind, @astrojs/check
├── src/
│   ├── content/config.ts                # collection schemas (guides, faq, directory, breeds, news, contributors)
│   ├── content/guides/                  # MDX care guides
│   ├── content/faq/                     # MDX FAQ posts
│   ├── content/directory/{vets,groomers,boarding,shops,rescues}/  # one MDX per business
│   ├── content/breeds/                  # one MDX per breed
│   ├── content/contributors/            # contributor bios
│   ├── layouts/{Article,FAQ,Directory,Breed,Hub}.astro
│   ├── components/{Schema,Breadcrumb,RelatedPosts,DirectoryCard,InternalLinks,SummaryBlock,KeyFacts,AffiliateDisclosure}.astro
│   ├── pages/{index,care,faq,vets,breeders,groomers,boarding,shops,rescues,breeds,community,about,contact,disclaimer,editorial-policy}.astro
│   ├── pages/llms.txt.ts                # generated llms.txt
│   └── styles/global.css
├── public/{robots.txt,favicon.svg,og-default.png}
├── scripts/
│   ├── weekly-brief.ts                  # Codex-runnable content brief generator
│   ├── validate-directory.ts            # build-time check
│   └── indexnow-ping.ts                 # post-deploy hook
└── README.md                            # operating instructions for future-you
```

## Phase plan

**Phase 0 — pre-launch (week 1, ~10 hr)**
- Register `singaporerabbits.com` (Cloudflare Registrar, ~$10/yr).
- Init GitHub repo, scaffold Astro project from this plan's file tree.
- Pick 25 cornerstone topics (Codex generates from r/Rabbits + SG forum keyword research).
- Write `editorial-policy.md`, `disclaimer.md`, `about.md`, `contact.md`.
- Configure Vercel deploy, Cloudflare DNS, GA4, GSC, Plausible.

**Phase 1 — cornerstone burst (month 1, 20 hr)**
- Ship 25 cornerstone articles + first 10 vet directory entries + first 10 shop directory entries.
- Ping IndexNow on every publish.
- Reach out to 5 SG owners (FB DM) for the contributor program.

**Phase 2 — BAU compounding (months 2-12, 5 hr/week)**
- 2 articles + 1 directory entry per week.
- Monthly: weekly-brief script run, stale-content audit, contributor outreach.
- Quarterly: full seo-superpowers-portfolio audit, schema drift check, internal-link rebalance.

**Phase 3 — monetization on (month 4 onward)**
- Affiliate links live in care guides (month 4).
- Featured-listing tier launched (month 6, requires 3-5 directory entries with proven traffic).
- Ezoic application (month 12 if at 10k sessions).

**Phase 4 — owned product (month 18-24)**
- "SG Rabbit Owner Handbook" PDF compiled from top-30 cornerstone posts + edits.
- Sold via Gumroad embed, affiliate-style 30% rev-share offered to named contributors.

## Verification

How to know each phase is working:

| Phase | Metric | Target | Check via |
|---|---|---|---|
| 0 | Site loads, Lighthouse all 100 | green | seo-performance skill |
| 1 | All 25 cornerstones indexed | ≥20/25 in GSC within 14d of publish | seo-google skill (URL Inspection API) |
| 2 (mo 6) | Organic sessions | ≥500/mo | GA4 |
| 2 (mo 12) | Organic sessions | ≥3k/mo, 50+ keywords ranking top 20 | seo-google + DataForSEO |
| 3 (mo 12) | First $100/mo from any monetization lever | $100/mo | Stripe/Shopee/Lazada dashboards |
| 3 (mo 18) | $500/mo combined | $500/mo | aggregator spreadsheet |
| 4 (mo 24) | $1k+/mo + 10k+ sessions | both | full quarterly review |
| GEO | Site cited in ≥1 ChatGPT/Perplexity answer for "rabbit care Singapore" | yes by mo 9 | seo-geo skill manual check |

**Kill criteria**: if at month 12 you have <500 organic sessions/mo AND no monetization signal AND your interest has waned, mothball gracefully (keep domain, freeze content, redirect to a relevant SG site). 5 hr/week × 12 mo = 260 hr investment cap before pivot decision.

## Why this beats the alternatives you didn't pick

You didn't ask for alternatives in the end, but for the record: I considered "drop rabbits, build a bigger SG-niche pSEO site" (e.g., SG postal-code pages, SG school finder, SG hawker stall directory). Those have higher TAM but **(a)** you'd be competing with Reddit/Tripadvisor/MOE, **(b)** they need real data sources you don't have access to, and **(c)** they're not a 5-hr/week passion project — they're full-time products. Singaporerabbits.com hits the sweet spot of "small enough that 5 hr/week is competitive, niche enough that there's no incumbent, structured enough that the directory becomes a real moat."

If you want to evaluate other ideas later, the same stack + workflow above is fully transferable to singaporecats / singaporehamsters / singaporeparrots without rework.
