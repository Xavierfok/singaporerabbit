"""audit src/content/guides/*.mdx for playbook §2 internal-link requirements.

playbook §2 (PLAYBOOK_SUNDAY_BATCH.md):
- every article has ≥3 internal links
- every article links to /vets/ (directory landing or specific vet) at least once

usage:
  python3 scripts/audit-internal-links.py          # report gaps
  python3 scripts/audit-internal-links.py --json   # machine-readable

exit code 0 if no gaps, 1 if gaps exist (so CI / launchd can alert).
"""
import argparse
import glob
import json
import re
import sys

LINK_RE = re.compile(r'\]\(/[a-z][a-z0-9/-]+/?\)')


def audit() -> list[dict]:
    gaps = []
    for f in sorted(glob.glob("src/content/guides/*.mdx")):
        body = open(f).read()
        links = LINK_RE.findall(body)
        vets = [l for l in links if l.startswith("](/vets")]
        if len(links) < 3 or not vets:
            gaps.append({
                "file": f,
                "slug": f.split("/")[-1][:-4],
                "total_links": len(links),
                "vet_links": len(vets),
            })
    return gaps


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    gaps = audit()
    if args.json:
        print(json.dumps(gaps, indent=2))
    else:
        total_files = len(glob.glob("src/content/guides/*.mdx"))
        print(f"audited {total_files} guides, found {len(gaps)} gap(s)")
        for g in gaps[:50]:
            print(f"  links={g['total_links']:2d}  vets={g['vet_links']}  {g['slug']}")
        if len(gaps) > 50:
            print(f"  ... and {len(gaps) - 50} more")
    return 0 if not gaps else 1


if __name__ == "__main__":
    sys.exit(main())
