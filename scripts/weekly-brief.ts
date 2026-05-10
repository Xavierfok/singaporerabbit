#!/usr/bin/env tsx
/**
 * weekly content brief generator.
 *
 * inputs:
 * - src/content/_briefs/notes.md (your manual FB-group capture, themes only)
 * - src/content/_briefs/reddit-fetch.json (optional, output of `reddit-fetch`
 *   skill for r/Rabbits + r/SingaporePets last 7 days; placeholder if absent)
 * - existing src/content/guides/*.{md,mdx} slugs (for internal-link suggestions)
 *
 * output: src/content/_briefs/{YYYY-MM-DD}-brief.md
 *
 * the brief follows the PLAN.md §"Source mix per week" budget — 3-5 angles,
 * suggested H2s, 3+ internal-link targets per angle, and a "review note"
 * hand-off block for the human editor (you).
 */
import fs from 'node:fs/promises';
import path from 'node:path';

const TODAY = new Date().toISOString().slice(0, 10);
const OUT = path.resolve(`src/content/_briefs/${TODAY}-brief.md`);
const NOTES = path.resolve('src/content/_briefs/notes.md');
const REDDIT_JSON = path.resolve('src/content/_briefs/reddit-fetch.json');
const GUIDES_DIR = path.resolve('src/content/guides');

async function readOptional(file: string): Promise<string> {
  try {
    return await fs.readFile(file, 'utf8');
  } catch {
    return '';
  }
}

async function listGuideSlugs(): Promise<string[]> {
  try {
    const ents = await fs.readdir(GUIDES_DIR, { withFileTypes: true, recursive: true });
    return ents
      .filter((d) => d.isFile() && (d.name.endsWith('.md') || d.name.endsWith('.mdx')))
      .map((d) => d.name.replace(/\.(md|mdx)$/, ''));
  } catch {
    return [];
  }
}

async function main() {
  const notes = await readOptional(NOTES);
  const redditRaw = await readOptional(REDDIT_JSON);
  const slugs = await listGuideSlugs();

  let redditSummary = '_no reddit-fetch data found. run the reddit-fetch skill first or capture themes by hand._';
  if (redditRaw) {
    try {
      const parsed = JSON.parse(redditRaw);
      const titles: string[] = Array.isArray(parsed?.posts)
        ? parsed.posts.slice(0, 8).map((p: { title?: string }) => `- ${p.title ?? '(untitled)'}`)
        : [];
      if (titles.length) redditSummary = titles.join('\n');
    } catch {
      redditSummary = '_reddit-fetch.json present but unparseable._';
    }
  }

  const internalLinks = slugs.length
    ? slugs.map((s) => `- /care/${s}/`).join('\n')
    : '_no published guides yet — internal-link slot will fill in over time._';

  const md = `---
title: weekly brief — ${TODAY}
type: brief
generated: ${new Date().toISOString()}
---

# weekly content brief — ${TODAY}

## raw inputs

### last 7 days, r/Rabbits + r/SingaporePets

${redditSummary}

### your FB-group + owner notes

${notes ? notes : '_src/content/_briefs/notes.md is empty. add SG-specific themes captured this week._'}

### existing internal-link targets

${internalLinks}

## proposed angles (pick 2–3)

> editor: cross out the two you'll skip, keep the H2 outline for the keepers, add the contributor
> who'll quote/photograph each piece, and you're ready to draft.

### 1. _angle title here_
- target query: \`...\`
- why now: ${redditRaw ? 'matches a recurring r/Rabbits theme this week' : 'evergreen SG gap'}
- proposed H2s:
  - ...
  - ...
  - ...
- internal links (≥3): pick from list above + at least one /vets/ entry
- contributor candidate: ...

### 2. _angle title here_
- target query: \`...\`
- proposed H2s:
  - ...
  - ...
  - ...
- internal links (≥3): ...

### 3. _angle title here_
- target query: \`...\`
- proposed H2s: ...
- internal links (≥3): ...

## hand-off

after editing this file, draft each kept angle into a guide or faq. run \`npm run check\`
locally before committing. final draft passes through the humanizer skill before merge.
`;

  await fs.mkdir(path.dirname(OUT), { recursive: true });
  await fs.writeFile(OUT, md, 'utf8');
  console.log(`brief written to ${path.relative(process.cwd(), OUT)}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
