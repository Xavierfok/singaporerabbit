"""ship untracked .mdx orphans left behind by ad-hoc bulk sessions.

context: the daily factory writes one article + commits to an auto-drafts/*
branch. ad-hoc bulk sessions (e.g. the 2026-05-14 50-batch) sometimes write
files to src/content/guides/ but never commit. those orphans sit untracked
until a human notices.

this sweeper runs at the end of cron.sh:
1. find untracked .mdx files under src/content/guides/ and src/content/_briefs/
2. lint each guide file via factory.lint.lint_post
3. if ALL pass: stage everything, commit, push, deploy, indexnow ping
4. if any fail: TG alert with file:errors list, leave files in place for human

does NOT touch files that lint fails — keeps them untracked for review.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent.parent
sys.path.insert(0, str(ROOT))

from lint import lint_post  # noqa: E402


def sh(*args: str, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)


def notify(msg: str, title: str = "rabbits orphan sweep") -> None:
    notifier = REPO_ROOT / "scripts" / "tg-notify.sh"
    if notifier.exists():
        subprocess.run([str(notifier), msg, title], check=False)


def find_orphans() -> list[Path]:
    res = sh("git", "status", "--porcelain", "src/content/")
    orphans: list[Path] = []
    for line in res.stdout.splitlines():
        if not line.startswith("?? "):
            continue
        rel = line[3:].strip()
        if rel.endswith(".mdx") or rel.endswith(".md"):
            orphans.append(REPO_ROOT / rel)
    return orphans


def main() -> int:
    orphans = find_orphans()
    if not orphans:
        print("no orphans, skipping sweep")
        return 0

    guide_orphans = [p for p in orphans if "/guides/" in str(p)]
    print(f"found {len(orphans)} orphan file(s), {len(guide_orphans)} guides")

    # lint each guide
    failures: dict[str, list[str]] = {}
    for path in guide_orphans:
        content = path.read_text()
        ok, errs = lint_post(content)
        if not ok:
            failures[path.name] = errs

    if failures:
        lines = [f"{len(failures)} orphan(s) failed lint, NOT shipping:"]
        for name, errs in failures.items():
            lines.append(f"  - {name}")
            for e in errs[:3]:
                lines.append(f"      · {e}")
        msg = "\n".join(lines)
        print(msg)
        notify(msg)
        return 1

    # all clean: stage, commit, push, deploy
    for path in orphans:
        sh("git", "add", str(path.relative_to(REPO_ROOT)))

    titles = [p.stem for p in guide_orphans]
    n_briefs = len(orphans) - len(guide_orphans)
    summary = f"orphan-sweep: {len(guide_orphans)} guide(s)"
    if n_briefs:
        summary += f" + {n_briefs} brief(s)"
    body = "\n".join(f"  - {t}" for t in titles[:30])

    commit_msg = f"{summary}\n\nshipped via orphan-sweep:\n{body}\n\nCo-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
    commit_res = sh("git", "commit", "-m", commit_msg)
    if commit_res.returncode != 0:
        notify(f"orphan-sweep: git commit failed\n{commit_res.stderr[:300]}")
        return 2

    push_res = sh("git", "push", "origin", "main")
    if push_res.returncode != 0:
        notify(f"orphan-sweep: committed but push failed\n{push_res.stderr[:300]}")
        return 3

    # deploy
    deploy_res = subprocess.run(
        ["bash", "scripts/deploy.sh"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if deploy_res.returncode != 0:
        tail = deploy_res.stdout.splitlines()[-15:] + deploy_res.stderr.splitlines()[-5:]
        notify(f"orphan-sweep: shipped {len(guide_orphans)} but DEPLOY FAILED\n" + "\n".join(tail))
        return 4

    notify(f"orphan-sweep shipped {len(guide_orphans)} guide(s) + deployed:\n{body[:600]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
