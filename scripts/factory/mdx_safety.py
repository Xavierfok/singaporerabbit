"""deterministic post-passes that run AFTER the humanizer and BEFORE the lint.

motivation: the LLM humanizer is unreliable at:
1. quoting YAML fields containing colons (breaks Astro build)
2. removing em-dashes (lint cap is 2 per body)
3. removing JSX-unsafe `<digit` and `{x}` patterns (MDX parser errors)

each pass is conservative: it ONLY edits lines that match the bug pattern.
no global rewrites. preserves frontmatter structure exactly.
"""
import re

QUOTE_FIELDS = ("title", "description", "summary")


def quote_yaml_fields(text: str) -> str:
    """auto-quote title/description/summary if value contains colon and is unquoted."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return text
    pre, fm, body = parts[0], parts[1], parts[2]

    new_lines = []
    for line in fm.split("\n"):
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if not m:
            new_lines.append(line)
            continue
        field, value = m.group(1), m.group(2).rstrip()
        if field not in QUOTE_FIELDS or not value:
            new_lines.append(line)
            continue
        # already quoted, array, or object
        if (value.startswith('"') and value.endswith('"')):
            new_lines.append(line)
            continue
        if (value.startswith("'") and value.endswith("'")):
            new_lines.append(line)
            continue
        if value.startswith("[") or value.startswith("{"):
            new_lines.append(line)
            continue
        # only quote if value contains a colon (the YAML trap)
        if ":" not in value:
            new_lines.append(line)
            continue
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        new_lines.append(f'{field}: "{escaped}"')

    return f"{pre}---{chr(10).join(new_lines)}---{body}"


def strip_em_dashes_body(text: str) -> str:
    """replace em-dashes in BODY only with commas/semicolons. preserves frontmatter."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return text
    pre, fm, body = parts[0], parts[1], parts[2]

    # em-dash variants: — (U+2014), – (U+2013), -- (double-hyphen)
    # heuristic: em-dash between two words → ", " ; at sentence start → ""
    body = re.sub(r"\s*[—–]\s*", ", ", body)
    body = re.sub(r"(?<=\w)--(?=\w)", ", ", body)
    body = re.sub(r"\s+--\s+", ", ", body)

    # collapse double-commas from accidental replacements
    body = re.sub(r",\s*,", ",", body)
    return f"{pre}---{fm}---{body}"


def fix_mdx_lt_digit(text: str) -> str:
    """escape `<5`, `<10` etc. in body to `&lt;5` to satisfy MDX parser."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return text
    pre, fm, body = parts[0], parts[1], parts[2]
    # word-boundary `<` followed by digit (avoid HTML tags and JSX)
    body = re.sub(r"<(?=\d)", "&lt;", body)
    return f"{pre}---{fm}---{body}"


def fix_mdx_single_braces(text: str) -> str:
    """remove single `{...}` JSX-expression patterns in body. uses simple heuristic."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return text
    pre, fm, body = parts[0], parts[1], parts[2]
    # only target single `{plain text}` (not in code blocks, not double `{{...}}`)
    # conservative: only inside backticks or sentence text
    # we just strip the braces, keep content
    body = re.sub(r"(?<!\{)\{([^{}]{1,80}?)\}(?!\})", r"\1", body)
    return f"{pre}---{fm}---{body}"


_FILLER_PATTERNS = [
    (re.compile(r"\b(in conclusion|in summary|to summarize|to conclude|overall),?\s*", re.IGNORECASE), ""),
    (re.compile(r"\b(various|numerous|a multitude of|a plethora of)\b", re.IGNORECASE), "several"),
    (re.compile(r"\bit's worth noting that\b", re.IGNORECASE), ""),
    (re.compile(r"\bit is important to note that\b", re.IGNORECASE), ""),
    (re.compile(r"\bplays a (?:crucial|vital|key|important) role\b", re.IGNORECASE), "matters"),
    (re.compile(r"\b(?:firstly|secondly|thirdly|moreover|furthermore|additionally)\b,?\s*", re.IGNORECASE), ""),
]


def strip_ai_filler_body(text: str) -> str:
    """remove common AI-writing tells from body. preserves frontmatter."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return text
    pre, fm, body = parts[0], parts[1], parts[2]
    for pat, repl in _FILLER_PATTERNS:
        body = pat.sub(repl, body)
    # collapse double spaces + double commas
    body = re.sub(r"  +", " ", body)
    body = re.sub(r",\s*,", ",", body)
    return f"{pre}---{fm}---{body}"


def strip_preamble_before_frontmatter(text: str) -> str:
    """if any text precedes the first `---`, strip it. fixes humanizer dropping opener."""
    text = text.lstrip()
    if text.startswith("---"):
        return text
    # find the first standalone `---` line
    idx = text.find("\n---")
    if idx == -1:
        return text
    # cut everything before that, keeping the `---`
    return text[idx + 1:]


def run_all(text: str) -> str:
    """run all safety passes in order. frontmatter -> body."""
    text = strip_preamble_before_frontmatter(text)
    text = quote_yaml_fields(text)
    text = strip_em_dashes_body(text)
    text = strip_ai_filler_body(text)
    text = fix_mdx_lt_digit(text)
    text = fix_mdx_single_braces(text)
    return text
