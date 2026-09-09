"""Validate rubric slice JSON against schema + Part 11 grounding rules.

Usage:  python3 scripts/validate_slices.py path/to/slice.json [more.json ...]

Exit 0 = all valid; non-zero = at least one rule failed.
Errors are printed to stderr, one per line.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "rubric-row.schema.json"
PART11_PATH = ROOT / "sources" / "part11.txt"

ID_RE = re.compile(r"^P11-11\.(10[acdegh]|30|50|70|100|200|300)-[0-9]{3}$")
KNOWN_CLAUSES = {
    "11.10(a)", "11.10(c)", "11.10(d)", "11.10(e)",
    "11.10(g)", "11.10(h)",
    "11.30", "11.50", "11.70",
    "11.100", "11.200", "11.300",
}
CONFIDENCE = {"high", "medium", "low", "none"}
GAMP5 = {1, 3, 4, 5}
REQUIRED = [
    "id", "finding_category", "part11_clauses", "clause_quote",
    "code_patterns", "mapping_confidence", "gamp5_category",
    "evidence_needed", "false_positive_traps",
]

_ID_SUFFIX_RE = re.compile(r"^11\.10([acdegh])$|^11\.(30|50|70|100|200|300)$")


def _id_clause_key(row_id: str) -> str:
    suffix = row_id.split("-")[1]
    m = _ID_SUFFIX_RE.match(suffix)
    if not m:
        return suffix
    if m.group(1):
        return f"11.10({m.group(1)})"
    return f"11.{m.group(2)}"


def validate_row(row: dict, part11_lower: str, errors: list) -> None:
    rid = row.get("id", "<no-id>")
    for key in REQUIRED:
        if key not in row:
            errors.append(f"{rid}: missing required field {key}")
            return
    if not isinstance(row["id"], str) or not ID_RE.match(row["id"]):
        errors.append(f"{rid}: id does not match pattern")
    if not isinstance(row["finding_category"], str) or len(row["finding_category"]) < 3:
        errors.append(f"{rid}: finding_category too short")
    if not isinstance(row["part11_clauses"], list) or not row["part11_clauses"]:
        errors.append(f"{rid}: part11_clauses must be non-empty list")
    else:
        for c in row["part11_clauses"]:
            if c not in KNOWN_CLAUSES:
                errors.append(f"{rid}: unknown clause {c!r}")
    if not isinstance(row["clause_quote"], str) or len(row["clause_quote"]) < 5:
        errors.append(f"{rid}: clause_quote too short")
    else:
        if row["clause_quote"].lower() not in part11_lower:
            errors.append(
                f"{rid}: clause_quote not a literal substring of part11.txt"
            )
    if not isinstance(row["code_patterns"], list) or not row["code_patterns"]:
        errors.append(f"{rid}: code_patterns must be non-empty list")
    if row["mapping_confidence"] not in CONFIDENCE:
        errors.append(f"{rid}: bad mapping_confidence {row['mapping_confidence']!r}")
    if row["gamp5_category"] not in GAMP5:
        errors.append(f"{rid}: bad gamp5_category {row['gamp5_category']!r}")
    if not isinstance(row["evidence_needed"], str) or len(row["evidence_needed"]) < 5:
        errors.append(f"{rid}: evidence_needed too short")
    if not isinstance(row["false_positive_traps"], list):
        errors.append(f"{rid}: false_positive_traps must be list")
    if ID_RE.match(row.get("id", "")):
        expected_clause = _id_clause_key(row["id"])
        if expected_clause not in row.get("part11_clauses", []):
            errors.append(
                f"{rid}: id encodes {expected_clause} but part11_clauses lacks it"
            )


def main(argv):
    if len(argv) < 2:
        print("usage: validate_slices.py slice.json [more.json ...]", file=sys.stderr)
        return 2
    if not PART11_PATH.exists():
        print(f"missing {PART11_PATH}", file=sys.stderr)
        return 2
    part11_lower = PART11_PATH.read_text().lower()
    errors = []
    for path_str in argv[1:]:
        path = Path(path_str)
        try:
            data = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"{path}: cannot parse JSON ({e})")
            continue
        if not isinstance(data, dict) or "rows" not in data:
            errors.append(f"{path}: top-level object must have 'rows' key")
            continue
        if not isinstance(data["rows"], list):
            errors.append(f"{path}: 'rows' must be a list")
            continue
        for row in data["rows"]:
            if not isinstance(row, dict):
                errors.append(f"{path}: row is not an object")
                continue
            validate_row(row, part11_lower, errors)
    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
