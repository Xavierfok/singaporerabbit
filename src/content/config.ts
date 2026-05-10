import { defineCollection, reference, z } from 'astro:content';

const ISO_DATE = z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'use YYYY-MM-DD');

const directoryRegions = ['north', 'south', 'east', 'west', 'central'] as const;
const directoryTypes = ['vets', 'groomers', 'boarding', 'shops', 'rescues', 'breeders'] as const;

const guides = defineCollection({
  type: 'content',
  schema: ({ image }) =>
    z.object({
      title: z.string().min(8).max(120),
      description: z.string().min(40).max(180),
      summary: z.string().min(160).max(640).describe('40-80 word plain-prose summary, GEO extract target'),
      last_updated: ISO_DATE,
      published: ISO_DATE,
      contributor: reference('contributors').optional(),
      schema_type: z.literal('Article').default('Article'),
      hero: image().optional(),
      hero_alt: z.string().optional(),
      tags: z.array(z.string()).default([]),
      faqs: z
        .array(z.object({ q: z.string(), a: z.string() }))
        .optional(),
      affiliate_disclosure: z.boolean().default(false),
      related_directory: z.array(reference('directory')).optional(),
      draft: z.boolean().default(false),
    }),
});

const faq = defineCollection({
  type: 'content',
  schema: z.object({
    question: z.string().min(10).max(160),
    answer_summary: z.string().min(120).max(480).describe('AI-citation friendly summary'),
    last_updated: ISO_DATE,
    published: ISO_DATE,
    related_guides: z.array(reference('guides')).default([]),
    related_directory: z.array(reference('directory')).optional(),
    schema_type: z.literal('FAQPage').default('FAQPage'),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

const directory = defineCollection({
  type: 'content',
  schema: ({ image }) =>
    z.object({
      name: z.string().min(2).max(120),
      type: z.enum(directoryTypes),
      address: z.string().min(8),
      region: z.enum(directoryRegions),
      phone: z.string().optional(),
      website: z.string().url().optional(),
      hours: z
        .record(z.enum(['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']), z.string())
        .optional(),
      lat: z.number().min(1).max(1.5),
      lng: z.number().min(103).max(104.5),
      sees_rabbits: z.boolean().optional().describe('vets only — confirmed exotic-pet capable'),
      source_url: z.string().url(),
      last_verified: ISO_DATE,
      featured: z.boolean().default(false),
      featured_until: ISO_DATE.optional(),
      photo: image().optional(),
      photo_credit: z.string().optional(),
      summary: z.string().min(80).max(480),
      schema_type: z.literal('LocalBusiness').default('LocalBusiness'),
      tags: z.array(z.string()).default([]),
      draft: z.boolean().default(false),
    }),
});

const breeds = defineCollection({
  type: 'content',
  schema: ({ image }) =>
    z.object({
      name: z.string().min(2).max(60),
      alternate_names: z.array(z.string()).default([]),
      origin: z.string(),
      adult_weight_kg: z.tuple([z.number(), z.number()]),
      lifespan_years: z.tuple([z.number(), z.number()]),
      temperament: z.array(z.string()).min(1),
      sg_climate_notes: z.string().min(120),
      summary: z.string().min(160).max(640),
      hero: image().optional(),
      hero_alt: z.string().optional(),
      last_updated: ISO_DATE,
      published: ISO_DATE,
      tags: z.array(z.string()).default([]),
      draft: z.boolean().default(false),
    }),
});

const contributors = defineCollection({
  type: 'content',
  schema: ({ image }) =>
    z.object({
      name: z.string().min(2).max(80),
      bio: z.string().min(60).max(480),
      photo: image().optional(),
      social: z
        .object({
          instagram: z.string().optional(),
          twitter: z.string().optional(),
          website: z.string().url().optional(),
        })
        .optional(),
      joined: ISO_DATE,
      retired: z.boolean().default(false),
    }),
});

const news = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string().min(10).max(140),
    summary: z.string().min(80).max(360),
    source_url: z.string().url(),
    source_name: z.string(),
    published: ISO_DATE,
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

const policy = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    last_updated: ISO_DATE,
    nav_order: z.number().int().default(99),
  }),
});

export const collections = { guides, faq, directory, breeds, contributors, news, policy };
