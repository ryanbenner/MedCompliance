import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_slices.py"


def run(slice_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(SCRIPT), str(slice_path)],
        capture_output=True, text=True
    )


def write_slice(tmp_path: Path, rows: list) -> Path:
    p = tmp_path / "slice.json"
    p.write_text(json.dumps({"rows": rows}))
    return p


def _good_row():
    return {
        "id": "P11-11.10d-001",
        "finding_category": "plaintext password storage",
        "part11_clauses": ["11.10(d)"],
        "clause_quote": "limiting system access to authorized individuals",
        "code_patterns": ["password column without bcrypt/argon2"],
        "mapping_confidence": "high",
        "gamp5_category": 5,
        "evidence_needed": "persistence call AND no hashing upstream",
        "false_positive_traps": ["dev-only seed scripts"],
    }


def test_passes_well_formed_slice(tmp_path):
    p = write_slice(tmp_path, [_good_row()])
    r = run(p)
    assert r.returncode == 0, r.stderr


def test_rejects_missing_required_field(tmp_path):
    row = _good_row()
    del row["clause_quote"]
    p = write_slice(tmp_path, [row])
    r = run(p)
    assert r.returncode != 0
    assert "clause_quote" in r.stderr


def test_rejects_unknown_clause(tmp_path):
    row = _good_row()
    row["part11_clauses"] = ["11.99(z)"]
    p = write_slice(tmp_path, [row])
    r = run(p)
    assert r.returncode != 0


def test_rejects_clause_quote_not_in_part11(tmp_path):
    row = _good_row()
    row["clause_quote"] = "this exact phrase will not appear in the regulation"
    p = write_slice(tmp_path, [row])
    r = run(p)
    assert r.returncode != 0
    assert "clause_quote" in r.stderr


def test_rejects_id_clause_mismatch(tmp_path):
    row = _good_row()
    row["id"] = "P11-11.50-001"
    row["part11_clauses"] = ["11.10(d)"]
    p = write_slice(tmp_path, [row])
    r = run(p)
    assert r.returncode != 0
    assert "id" in r.stderr.lower()


def test_rejects_bad_confidence_value(tmp_path):
    row = _good_row()
    row["mapping_confidence"] = "very high"
    p = write_slice(tmp_path, [row])
    r = run(p)
    assert r.returncode != 0
