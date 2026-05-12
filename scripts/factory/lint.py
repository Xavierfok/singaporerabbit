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

    return len(errors) == 0, errors
