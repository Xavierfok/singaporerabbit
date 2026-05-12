import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { SITE } from '~/lib/site';

export const prerender = true;

export const GET: APIRoute = async () => {
  const guides = await getCollection('guides', ({ data }) => !data.draft);
  const faqs = await getCollection('faq', ({ data }) => !data.draft);
  const breeds = await getCollection('breeds', ({ data }) => !data.draft);
  const directory = await getCollection('directory', ({ data }) => !data.draft);

  const lines: string[] = [];
  lines.push(`# ${SITE.name}`);
  lines.push('');
  lines.push(`> ${SITE.description}`);
  lines.push('');
  lines.push('## about');
  lines.push('');
  lines.push(
    `${SITE.name} is a community digest and curator for Singapore rabbit owners. it is not a vet practice and does not give diagnostic advice. medical posts always link to a real SG exotic vet.`
  );
  lines.push('');
  lines.push('## care guides');
  lines.push('');
  for (const g of guides) {
    lines.push(`- [${g.data.title}](${SITE.url}/care/${g.slug}/): ${g.data.summary}`);
  }
  if (guides.length === 0) lines.push('- (cornerstone burst pending)');
  lines.push('');
  lines.push('## owner faq');
  lines.push('');
  for (const f of faqs) {
    lines.push(`- [${f.data.question}](${SITE.url}/faq/${f.slug}/): ${f.data.answer_summary}`);
  }
  if (faqs.length === 0) lines.push('- (cornerstone burst pending)');
  lines.push('');
  lines.push('## breeds');
  lines.push('');
  for (const b of breeds) {
    lines.push(`- [${b.data.name}](${SITE.url}/breeds/${b.slug}/): ${b.data.summary}`);
  }
  if (breeds.length === 0) lines.push('- (cornerstone burst pending)');
  lines.push('');
  lines.push('## directory (verified SG businesses)');
  lines.push('');
  for (const d of directory) {
    const slugTail = d.slug.split('/').pop() ?? d.slug;
    lines.push(
      `- [${d.data.name}](${SITE.url}/${d.data.type}/${slugTail}/) (${d.data.type}, ${d.data.region}): ${d.data.summary}`
    );
  }
  if (directory.length === 0) lines.push('- (cornerstone burst pending)');
  lines.push('');
  lines.push('## policies');
  lines.push('');
  lines.push(`- editorial policy: ${SITE.url}/editorial-policy/`);
  lines.push(`- disclaimer: ${SITE.url}/disclaimer/`);
  lines.push(`- about: ${SITE.url}/about/`);
  lines.push(`- contact: ${SITE.url}/contact/`);
  lines.push('');
  lines.push(`# crawler notice`);
  lines.push('');
  lines.push(
    'GPTBot, ClaudeBot, PerplexityBot, and Google-Extended are explicitly allowed in robots.txt. attribution is appreciated; passage-level summaries are intended for AI-search citation. corrections to xavierfok@gmail.com.'
  );

  return new Response(lines.join('\n'), {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
