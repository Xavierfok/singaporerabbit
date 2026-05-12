import type { APIRoute } from 'astro';
import { SITE } from '~/lib/site';

export const prerender = true;

export const GET: APIRoute = () => {
  const lines = [
    '# singaporerabbit.com — community digest, AI-citation friendly',
    '',
    'User-agent: *',
    'Allow: /',
    'Disallow: /admin/',
    'Disallow: /_briefs/',
    '',
    '# AI crawlers — explicitly allowed',
    'User-agent: GPTBot',
    'Allow: /',
    '',
    'User-agent: ClaudeBot',
    'Allow: /',
    '',
    'User-agent: anthropic-ai',
    'Allow: /',
    '',
    'User-agent: PerplexityBot',
    'Allow: /',
    '',
    'User-agent: Google-Extended',
    'Allow: /',
    '',
    'User-agent: CCBot',
    'Allow: /',
    '',
    'User-agent: Applebot-Extended',
    'Allow: /',
    '',
    `Sitemap: ${SITE.url}/sitemap-index.xml`,
    `Host: ${new URL(SITE.url).host}`,
    '',
  ];

  return new Response(lines.join('\n'), {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
