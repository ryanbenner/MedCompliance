"""Merge all slice JSON files in a directory into a single rubric.json.

Usage: python3 scripts/merge_slices.py --in DIR --out FILE
"""
import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="indir", required=True)
    ap.add_argument("--out", dest="outfile", required=True)
    args = ap.parse_args()
    indir = Path(args.indir)
    if not indir.is_dir():
        print(f"not a directory: {indir}", file=sys.stderr)
        return 2
    all_rows: list[dict] = []
    seen_ids: dict[str, str] = {}
    for slice_path in sorted(indir.glob("*.json")):
        data = json.loads(slice_path.read_text())
        for row in data.get("rows", []):
            rid = row["id"]
            if rid in seen_ids:
                print(
                    f"duplicate id {rid!r} in {slice_path.name} "
                    f"(already seen in {seen_ids[rid]})",
                    file=sys.stderr,
                )
                return 1
            seen_ids[rid] = slice_path.name
            all_rows.append(row)
    out = Path(args.outfile)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"rows": all_rows}, indent=2) + "\n")
    print(f"merged {len(all_rows)} rows from {len(seen_ids)} ids into {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
