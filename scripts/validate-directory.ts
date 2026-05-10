#!/usr/bin/env tsx
/**
 * directory entry validator.
 *
 * runs beyond zod schema enforcement — checks that every directory entry's
 * `last_verified` is within the freshness window and that `source_url` is
 * still reachable. fail-noisy by default; pass --warn to soften to warnings
 * (used in CI on PR diffs to avoid blocking on unrelated stale entries).
 *
 * pre-build directory verification — keeps the moat honest.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import matter from 'gray-matter';

interface Entry {
  file: string;
  data: Record<string, unknown>;
}

const DIRECTORY_ROOT = path.resolve('src/content/directory');
const FRESHNESS_DAYS = 180;
const SOURCE_URL_TIMEOUT_MS = 8000;

const args = new Set(process.argv.slice(2));
const WARN_ONLY = args.has('--warn');
const SKIP_NETWORK = args.has('--no-network');

async function listEntries(root: string): Promise<Entry[]> {
  const out: Entry[] = [];
  let dirents: import('node:fs').Dirent[];
  try {
    dirents = await fs.readdir(root, { withFileTypes: true, recursive: true });
  } catch {
    return out;
  }
  for (const d of dirents) {
    if (!d.isFile()) continue;
    if (!d.name.endsWith('.mdx') && !d.name.endsWith('.md')) continue;
    const dirPath = (d as unknown as { parentPath?: string; path?: string }).parentPath
      ?? (d as unknown as { path?: string }).path
      ?? root;
    const file = path.join(dirPath, d.name);
    const raw = await fs.readFile(file, 'utf8');
    const fm = matter(raw);
    out.push({ file, data: fm.data });
  }
  return out;
}

function daysSince(iso: string): number {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return Infinity;
  return Math.floor((Date.now() - then) / (1000 * 60 * 60 * 24));
}

async function checkUrl(url: string): Promise<boolean> {
  if (SKIP_NETWORK) return true;
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), SOURCE_URL_TIMEOUT_MS);
    const res = await fetch(url, { method: 'HEAD', redirect: 'follow', signal: ctrl.signal });
    clearTimeout(t);
    return res.ok || res.status === 405;
  } catch {
    return false;
  }
}

async function main() {
  const entries = await listEntries(DIRECTORY_ROOT);
  if (entries.length === 0) {
    console.log('directory validator: no entries to check (cornerstone burst pending). ok.');
    return;
  }

  let errors = 0;
  let warnings = 0;
  for (const e of entries) {
    const rel = path.relative(process.cwd(), e.file);
    const lastVerified = e.data.last_verified as string | undefined;
    if (!lastVerified) {
      console.error(`✗ ${rel}: missing last_verified`);
      errors += 1;
      continue;
    }
    const age = daysSince(lastVerified);
    if (age > FRESHNESS_DAYS) {
      const msg = `${rel}: last_verified is ${age} days old (limit ${FRESHNESS_DAYS})`;
      if (WARN_ONLY) {
        console.warn('⚠ ' + msg);
        warnings += 1;
      } else {
        console.error('✗ ' + msg);
        errors += 1;
      }
    }
    const sourceUrl = e.data.source_url as string | undefined;
    if (sourceUrl && !(await checkUrl(sourceUrl))) {
      const msg = `${rel}: source_url HEAD failed → ${sourceUrl}`;
      if (WARN_ONLY) {
        console.warn('⚠ ' + msg);
        warnings += 1;
      } else {
        console.error('✗ ' + msg);
        errors += 1;
      }
    }
  }

  console.log(`directory validator: checked ${entries.length} entries, ${errors} errors, ${warnings} warnings.`);
  if (errors > 0) process.exit(1);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
