import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "merge_slices.py"


def _row(rid, clause):
    return {
        "id": rid,
        "finding_category": "x",
        "part11_clauses": [clause],
        "clause_quote": "limiting system access to authorized individuals",
        "code_patterns": ["pattern"],
        "mapping_confidence": "high",
        "gamp5_category": 5,
        "evidence_needed": "evidence",
        "false_positive_traps": [],
    }


def test_merges_multiple_slices_into_rubric_json(tmp_path):
    slices = tmp_path / "slices"
    slices.mkdir()
    (slices / "a.json").write_text(json.dumps(
        {"rows": [_row("P11-11.10d-001", "11.10(d)")]}
    ))
    (slices / "b.json").write_text(json.dumps(
        {"rows": [_row("P11-11.50-001", "11.50")]}
    ))
    out = tmp_path / "rubric.json"
    r = subprocess.run(
        ["python3", str(SCRIPT), "--in", str(slices), "--out", str(out)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    merged = json.loads(out.read_text())
    ids = sorted(row["id"] for row in merged["rows"])
    assert ids == ["P11-11.10d-001", "P11-11.50-001"]


def test_fails_on_duplicate_ids_across_slices(tmp_path):
    slices = tmp_path / "slices"
    slices.mkdir()
    (slices / "a.json").write_text(json.dumps(
        {"rows": [_row("P11-11.10d-001", "11.10(d)")]}
    ))
    (slices / "b.json").write_text(json.dumps(
        {"rows": [_row("P11-11.10d-001", "11.10(d)")]}
    ))
    out = tmp_path / "rubric.json"
    r = subprocess.run(
        ["python3", str(SCRIPT), "--in", str(slices), "--out", str(out)],
        capture_output=True, text=True,
    )
    assert r.returncode != 0
    assert "duplicate" in r.stderr.lower()
