"""validate factory-generated MDX against the site's content rules.

returns (ok, errors) where errors is a list of strings. fails fast on
structural issues; warnings are returned as errors too because factory output
is auto-published only after review anyway.
"""
import re
from typing import Tuple


def lint_post(content: str, expected_title: str | None = None) -> Tuple[bool, list[str]]:
    errors: list[str] = []

    if not content.startswith("---\n"):
        errors.append("missing opening frontmatter delimiter")
        return False, errors

    parts = content.split("---\n", 2)
    if len(parts) < 3:
        errors.append("malformed frontmatter (missing closing delimiter)")
        return False, errors

    frontmatter, body = parts[1], parts[2]

    required = ["title:", "description:", "summary:", "last_updated:", "published:", "schema_type:", "tags:"]
    for key in required:
        if key not in frontmatter:
            errors.append(f"frontmatter missing: {key}")

    if "contributor: xavier-fok" not in frontmatter and "contributor:" not in frontmatter:
        errors.append("frontmatter missing contributor (should be xavier-fok)")

    word_count = len(re.findall(r"\b\w+\b", body))
    if word_count < 900:
        errors.append(f"body too short: {word_count} words (target 1200-1700)")
    if word_count > 2400:
        errors.append(f"body too long: {word_count} words (target 1200-1700)")

    if "## what owners often get wrong" not in body.lower():
        errors.append("missing 'what owners often get wrong' section")

    if "## related reading" not in body.lower():
        errors.append("missing 'related reading' section")

    if "veterinary advice" not in body.lower():
        errors.append("missing disclaimer paragraph (must mention 'veterinary advice')")

    h2_count = len(re.findall(r"^## ", body, re.M))
    if h2_count < 4:
        errors.append(f"too few H2 sections: {h2_count} (need at least 4)")

    em_dash_count = body.count("—")
    if em_dash_count > 2:
        errors.append(f"too many em-dashes in body: {em_dash_count} (max 2 after humanizer)")

    if expected_title and expected_title not in frontmatter:
        errors.append(f"frontmatter title does not match expected: {expected_title}")

    if re.search(r"\b(in conclusion|in summary|overall,)\b", body.lower()):
        errors.append("contains banned phrase (in conclusion / in summary / overall)")

    # MDX safety: import lines break the build (no Callout component exists, tsconfig alias is ~/* not @/*)
    if re.search(r"(?m)^import\s+", body):
        errors.append("MDX: contains import statement (no JSX components exist; use markdown only)")

    # MDX safety: bare <digit looks like a JSX tag opener and breaks vite/rollup
    lt_digit = re.findall(r"<\d", body)
    if lt_digit:
        errors.append(f"MDX: bare '<digit' pattern ({len(lt_digit)}x); rewrite as 'under N' or '&lt;N'")

    # MDX safety: JSX-style tags (<Callout>, <Alert>, etc.) — uppercase first letter after <
    jsx_tags = re.findall(r"<[A-Z][a-zA-Z]*\b", body)
    if jsx_tags:
        errors.append(f"MDX: JSX-style tags found ({', '.join(set(jsx_tags))}); use markdown blockquotes")

    # playbook §2: every article must link to /vets/ at least once
    if not re.search(r"\]\(/vets/?\)", body):
        errors.append("playbook: no link to /vets/ (required at least once)")

    # playbook §2: ≥3 internal links total
    internal_links = re.findall(r"\]\(/[a-z][a-z/-]*/?\)", body)
    if len(internal_links) < 3:
        errors.append(f"playbook: only {len(internal_links)} internal link(s) (need at least 3)")

    return len(errors) == 0, errors
