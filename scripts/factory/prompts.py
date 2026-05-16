"""prompts for the singaporerabbit content factory.

each topic gets:
1. generation prompt → produces draft MDX content
2. humanizer prompt → second pass that tightens voice + removes AI tells

style rules (from CLAUDE.md + site voice):
- lowercase after periods, no caps mid-sentence (except SG, HDB, AC, proper nouns)
- no em-dashes inside body text (use commas, semicolons, or new sentences)
- short sentences. SG-specific where it matters (climate, vet costs, flat sizes)
- no veterinary prescriptions. always defer to exotic vet for medical decisions
- no fabricated businesses. if mentioning a vet/shop, must be one already in
  the existing directory
"""

GENERATION_TEMPLATE = """you are writing a 1300 to 1700 word care guide for singaporerabbit.com,
a Singapore-specific pet rabbit information site for owners and prospective owners.

write the MDX file content (frontmatter + body, no preamble, no code fences).
output only the .mdx file content, nothing else.

## topic
{title}

## frontmatter requirements

```
---
title: {title}
description: 40-180 character single sentence
summary: 160 to 640 character plain-prose paragraph for AI-citation. 40-80 words.
last_updated: {today}
published: {today}
contributor: xavier-fok
schema_type: {schema_type}
tags: [4 to 6 tags, lowercase, hyphenated]
affiliate_disclosure: false
---
```

## body structure

- opening: 1 paragraph framing the SG-specific angle. why does this matter
  to a SG rabbit owner specifically (climate, HDB constraints, vet access, etc.)
- 4 to 7 H2 sections covering the topic
- one H2 must be "## what owners often get wrong" near the end (3 to 4 patterns)
- one H2 must be "## related reading" at the very end with 3 to 4 internal
  links to plausible /care/ slugs (you may invent slug names; we will validate)
- closing disclaimer paragraph: "community-sourced information here is not
  veterinary advice. for any health concern see a licensed SG exotic vet."

## voice rules

- lowercase prose, including the first word of sentences
- capitalize: SG, Singapore, HDB, AC, MRT, English proper nouns, breed names,
  vet clinic names, brand names, and the pronoun I
- no em-dashes in body. use commas, semicolons, or split into separate sentences
- short sentences, ~12 to 18 words. no walls of text
- direct address ("you") to the owner where appropriate
- SG-specific facts wherever applicable: vet pricing in SGD, climate impact
  (28-32°C, 70-90% humidity year-round), HDB flat constraints, exotic vet
  scarcity vs cat/dog clinics, after-hours access limitations

## medical safety

- never recommend specific drug doses
- never tell owners to "wait and see" with any acute signs
- always defer to "see a SG exotic vet" for any sign requiring diagnosis
- if discussing prices or procedures, frame them as "as of 2026, costs typically range"
- never name a vet clinic by name unless you are quoting publicly available info

## MDX safety (CRITICAL, build breaks otherwise)

this is .mdx, not plain markdown. the MDX parser treats `<` and `{` as
JSX syntax. follow these rules exactly:

- NEVER add an `import` line. no `import { Callout } from ...`. no JSX
  components. components do not exist in this repo. plain markdown only.
- NEVER write a bare `<` immediately followed by a digit. for "less than
  50 PSI" write "under 50 PSI" or "below 50 PSI" or escape as `&lt;50`.
  the parser breaks on `<5` etc.
- NEVER use JSX-style tags like `<Callout>`, `<Alert>`, `<Card>`. for
  emphasis or warnings use a markdown blockquote starting with `> **label:**`
  (e.g. `> **emergency:** call a vet immediately`).
- NEVER use single curly braces around plain text. `{some value}` is parsed
  as a JSX expression and will break. use plain text.

## /vets/ link requirement

every article MUST link to `/vets/` at least once. the natural place is
the related-reading section as a bullet like:
`- our [vet directory](/vets/) — <one-line topic-specific anchor>`

## what NOT to do

- do not fabricate businesses, vets, shops, products. if you cite a brand
  in a comparison, only mention well-known international brands (Oxbow,
  Burgess, Sherwood, Kaytee, Niteangel, Lixit)
- do not use vague filler ("various factors", "many things to consider")
- do not start sections with "in conclusion" or "in summary"

output the full mdx file now. {schema_type_note}"""


HUMANIZER_TEMPLATE = """rewrite the following draft to remove AI tells while keeping all
factual content intact. preserve the frontmatter as-is.

specific edits:
- remove em-dashes (replace with commas, semicolons, or new sentences)
- collapse any "in conclusion", "in summary", "overall" phrasings
- shorten sentences over 25 words
- vary sentence opens (avoid 3+ sentences in a row starting the same way)
- remove "various", "numerous", "a multitude of", "plethora"
- lowercase the start of every sentence in the body (not frontmatter values
  except where they are proper nouns)

output the revised full MDX file, no preamble, no code fences.

DRAFT TO REWRITE:

{draft}"""


def build_generation_prompt(topic: dict, today: str) -> str:
    schema_type = topic.get("schema_type", "Article")
    schema_note = ""
    if schema_type == "HowTo":
        schema_note = (
            "since schema_type is HowTo, structure the body with numbered or "
            "clearly-stepped sections that walk through a discrete procedure."
        )
    return GENERATION_TEMPLATE.format(
        title=topic["title"],
        today=today,
        schema_type=schema_type,
        schema_type_note=schema_note,
    )


def build_humanizer_prompt(draft: str) -> str:
    return HUMANIZER_TEMPLATE.format(draft=draft)
