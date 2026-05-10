export const SITE = {
  name: 'singapore rabbits',
  url: 'https://singaporerabbits.com',
  tagline: 'what local owners actually ask, answered',
  description:
    'community digest and curator for Singapore rabbit owners. Care guides, owner faq, and a directory of SG rabbit-friendly vets, groomers, and shops.',
  locale: 'en-SG',
  publisher: {
    name: 'singapore rabbits',
    type: 'Organization',
  },
  social: {
    instagram: '@singaporerabbits',
    twitter: '@singaporerabbits',
  },
  newsletter: {
    provider: 'buttondown',
    formAction: 'https://buttondown.com/api/emails/embed-subscribe/singaporerabbits',
  },
} as const;

export const NAV_PRIMARY = [
  { href: '/care/', label: 'care guides' },
  { href: '/faq/', label: 'owner faq' },
  { href: '/vets/', label: 'directory' },
  { href: '/breeds/', label: 'breeds' },
  { href: '/community/', label: 'community' },
] as const;

export const NAV_DIRECTORY = [
  { href: '/vets/', label: 'vets' },
  { href: '/groomers/', label: 'groomers' },
  { href: '/boarding/', label: 'boarding' },
  { href: '/shops/', label: 'shops' },
  { href: '/rescues/', label: 'rescues' },
  { href: '/breeders/', label: 'breeders' },
] as const;

export const SG_REGIONS = ['north', 'south', 'east', 'west', 'central'] as const;
