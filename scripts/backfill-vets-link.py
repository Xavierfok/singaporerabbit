"""backfill a /vets/ bullet into the related-reading section of any guide
that doesn't have one. idempotent: skips files that already have a /vets/
link anywhere in the body, or no related-reading section to inject into.

usage:
  python3 scripts/backfill-vets-link.py            # dry-run, report only
  python3 scripts/backfill-vets-link.py --apply    # write changes
"""
import argparse
import glob
import re
import sys

VET_BULLET = "- our [vet directory](/vets/) for any rabbit-savvy exotic clinic in Singapore"
RR_HEADER = re.compile(r'^## related reading\s*$', re.M)
LINK_RE = re.compile(r'\]\(/[a-z][a-z0-9/-]+/?\)')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    changed = 0
    skipped_already = 0
    skipped_no_rr = []

    for f in sorted(glob.glob("src/content/guides/*.mdx")):
        body = open(f).read()
        links = LINK_RE.findall(body)
        if any(l.startswith("](/vets") for l in links):
            skipped_already += 1
            continue
        m = RR_HEADER.search(body)
        if not m:
            skipped_no_rr.append(f)
            continue
        rest = body[m.end():]
        next_h2 = re.search(r'^## ', rest, re.M)
        section_end = m.end() + (next_h2.start() if next_h2 else len(rest))
        section = body[m.end():section_end]
        bullets = list(re.finditer(r'^- .*$', section, re.M))
        if not bullets:
            skipped_no_rr.append(f)
            continue
        insertion_point = m.end() + bullets[-1].end()
        new_body = body[:insertion_point] + "\n" + VET_BULLET + body[insertion_point:]
        if args.apply:
            open(f, "w").write(new_body)
        changed += 1

    for f in skipped_no_rr:
        print(f"NO_RR_OR_BULLETS: {f}")
    print(f"\nchanged={changed} skipped_already_has_vet={skipped_already} skipped_no_rr={len(skipped_no_rr)}")
    print("dry-run" if not args.apply else "applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
