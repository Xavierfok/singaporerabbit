import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import { SITE } from '~/lib/site';

export async function GET(context: { site?: URL }) {
  const guides = await getCollection('guides', ({ data }) => !data.draft);
  const faqs = await getCollection('faq', ({ data }) => !data.draft);

  const items = [
    ...guides.map((g) => ({
      title: g.data.title,
      pubDate: new Date(g.data.published),
      description: g.data.description,
      link: `/care/${g.slug}/`,
      categories: g.data.tags ?? [],
    })),
    ...faqs.map((f) => ({
      title: f.data.question,
      pubDate: new Date(f.data.published),
      description: f.data.answer_summary,
      link: `/faq/${f.slug}/`,
      categories: f.data.tags ?? [],
    })),
  ].sort((a, b) => b.pubDate.getTime() - a.pubDate.getTime());

  return rss({
    title: SITE.name,
    description: SITE.description,
    site: context.site ?? SITE.url,
    items,
    customData: `<language>${SITE.locale}</language>`,
  });
}
