import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';
import pagefind from 'astro-pagefind';

export default defineConfig({
  site: 'https://singaporerabbit.com',
  trailingSlash: 'always',
  build: {
    format: 'directory',
  },
  integrations: [
    tailwind({ applyBaseStyles: true }),
    mdx(),
    sitemap({
      changefreq: 'weekly',
      priority: 0.7,
      filter: (page) =>
        !page.includes('/_briefs/') && !page.includes('/admin/'),
    }),
    pagefind(),
  ],
  image: {
    service: { entrypoint: 'astro/assets/services/sharp' },
  },
  prefetch: {
    prefetchAll: false,
    defaultStrategy: 'hover',
  },
});
