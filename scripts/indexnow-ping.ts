#!/usr/bin/env tsx
/**
 * IndexNow post-deploy ping for Bing/Yandex/Seznam.
 *
 * reads the live sitemap from $SITE_URL/sitemap-index.xml + sitemap-0.xml and
 * pings api.indexnow.org with every URL. simplest mode (no diff vs previous
 * deploy) — IndexNow rate limits per-host, not per-URL, and re-pinging known
 * URLs is a no-op for the search engines.
 *
 * env:
 *   INDEXNOW_KEY      — required, the random key string we host at /<key>.txt
 *   INDEXNOW_KEY_LOC  — optional, override the key file URL (default: site root)
 *   SITE_URL          — defaults to https://singaporerabbits.com
 */
const SITE_URL = process.env.SITE_URL ?? 'https://singaporerabbits.com';
const KEY = process.env.INDEXNOW_KEY;
const KEY_LOC = process.env.INDEXNOW_KEY_LOC ?? `${SITE_URL}/${KEY}.txt`;

if (!KEY) {
  console.error('INDEXNOW_KEY env var is required');
  process.exit(1);
}

async function fetchSitemap(url: string): Promise<string[]> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`sitemap fetch failed: ${url} → ${res.status}`);
  const xml = await res.text();
  const sub = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1] ?? '').filter(Boolean);
  if (sub.some((u) => u.endsWith('.xml'))) {
    const all: string[] = [];
    for (const s of sub) all.push(...(await fetchSitemap(s)));
    return all;
  }
  return sub;
}

async function main() {
  const urls = await fetchSitemap(`${SITE_URL}/sitemap-index.xml`);
  if (!urls.length) {
    console.warn('no urls discovered in sitemap');
    return;
  }
  const host = new URL(SITE_URL).host;
  const body = {
    host,
    key: KEY,
    keyLocation: KEY_LOC,
    urlList: urls,
  };
  const res = await fetch('https://api.indexnow.org/indexnow', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  console.log(`indexnow: ${res.status} for ${urls.length} urls on ${host}`);
  if (!res.ok && res.status !== 202) {
    const text = await res.text();
    console.error(text);
    process.exit(1);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
