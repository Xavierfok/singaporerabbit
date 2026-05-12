"""thin wrapper around the claude code CLI for the rabbits factory.

uses subscription (not API). strips wrapper preamble/footer. excludes
ANTHROPIC_API_KEY from subprocess env so it doesn't burn paid credits.

reference: ~/.claude/CLAUDE.md (feedback_claude_cli_rules)
"""
import os
import re
import subprocess
import time
from typing import Optional

CLAUDE_BIN = "/Users/foktunghoe/.local/bin/claude"

_WRAPPER_PREFIXES = (
    "here's a draft",
    "here is a draft",
    "here's the",
    "here is the",
    "here you go",
    "sure,",
    "sure!",
)


def _clean_env() -> dict:
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("CLAUDE_API_KEY", None)
    return env


def _strip_wrapper(text: str) -> str:
    text = text.strip()
    lines = text.splitlines()
    if lines and any(lines[0].lower().startswith(p) for p in _WRAPPER_PREFIXES):
        lines = lines[1:]
    if lines and re.match(r"^[\(~]?\s*\d+\s*words", lines[-1].lower()):
        lines = lines[:-1]
    out = "\n".join(lines).strip()
    if out.startswith("```") and out.endswith("```"):
        inner = out.split("\n", 1)[1] if "\n" in out else out[3:-3]
        out = inner.rsplit("\n```", 1)[0] if inner.endswith("```") else inner
    return out.strip()


def ask_claude(
    prompt: str,
    model: str = "sonnet",
    timeout: int = 600,
    retries: int = 2,
) -> Optional[str]:
    """call `claude --print --model <model>` with prompt on stdin.

    returns stripped output or None on failure.
    """
    cmd = [CLAUDE_BIN, "--print", "--model", model]
    last_err = None
    for attempt in range(retries + 1):
        try:
            r = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=_clean_env(),
            )
            if r.returncode != 0:
                last_err = f"exit {r.returncode}: {r.stderr[:300]}"
                time.sleep(5 * (attempt + 1))
                continue
            out = _strip_wrapper(r.stdout)
            if not out:
                last_err = "empty output (check claude cli)"
                time.sleep(5 * (attempt + 1))
                continue
            return out
        except subprocess.TimeoutExpired:
            last_err = f"timeout after {timeout}s"
            time.sleep(5 * (attempt + 1))
    print(f"[claude_call] FAILED after {retries+1} tries: {last_err}")
    return None
