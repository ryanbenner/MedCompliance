"""Render rubric.json to a human-readable markdown rubric.md.

Usage: python3 scripts/render_rubric.py --in rubric.json --out rubric.md
"""
import argparse
import json
import sys
from pathlib import Path

CLAUSE_ORDER = [
    "11.10(a)", "11.10(c)", "11.10(d)", "11.10(e)",
    "11.10(g)", "11.10(h)",
    "11.30", "11.50", "11.70",
    "11.100", "11.200", "11.300",
]


def primary_clause(row: dict) -> str:
    return row["part11_clauses"][0]


def render(rubric: dict) -> str:
    out = ["# 21 CFR Part 11 → Code-Pattern Rubric", ""]
    out.append(
        "Generated from rubric.json. Each section lists code-detectable "
        "patterns that implicate the named subsection. Rows are grouped by "
        "their first-listed clause; rows that map to multiple clauses appear "
        "once, under the primary clause."
    )
    out.append("")
    by_clause: dict[str, list[dict]] = {c: [] for c in CLAUSE_ORDER}
    for row in rubric.get("rows", []):
        by_clause.setdefault(primary_clause(row), []).append(row)
    for clause in CLAUSE_ORDER:
        rows = by_clause.get(clause, [])
        if not rows:
            out.append(f"## {clause}")
            out.append("")
            out.append("_No rubric rows. Coverage gap — investigate._")
            out.append("")
            continue
        out.append(f"## {clause}")
        out.append("")
        for row in rows:
            extra = (
                f" (also: {', '.join(c for c in row['part11_clauses'] if c != clause)})"
                if len(row["part11_clauses"]) > 1
                else ""
            )
            out.append(
                f"### `{row['id']}` — {row['finding_category']}{extra}"
            )
            out.append("")
            out.append(f"> {row['clause_quote']}")
            out.append("")
            out.append(
                f"- **Confidence:** {row['mapping_confidence']}  "
                f"**GAMP 5:** category {row['gamp5_category']}"
            )
            out.append("- **Code patterns:**")
            for p in row["code_patterns"]:
                out.append(f"  - {p}")
            out.append(f"- **Evidence needed:** {row['evidence_needed']}")
            if row["false_positive_traps"]:
                out.append("- **False-positive traps:**")
                for t in row["false_positive_traps"]:
                    out.append(f"  - {t}")
            out.append("")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", required=True)
    ap.add_argument("--out", dest="outfile", required=True)
    args = ap.parse_args()
    rubric = json.loads(Path(args.infile).read_text())
    md = render(rubric)
    out = Path(args.outfile)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md)
    print(f"rendered {len(rubric.get('rows', []))} rows to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
