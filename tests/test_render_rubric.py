import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render_rubric.py"


def _row(rid, clause, name="some finding"):
    return {
        "id": rid,
        "finding_category": name,
        "part11_clauses": [clause],
        "clause_quote": "limiting system access to authorized individuals",
        "code_patterns": ["a pattern"],
        "mapping_confidence": "high",
        "gamp5_category": 5,
        "evidence_needed": "evidence here",
        "false_positive_traps": ["a trap"],
    }


def test_renders_grouped_by_clause(tmp_path):
    rubric = {
        "rows": [
            _row("P11-11.50-001", "11.50", "sig manifestation gap"),
            _row("P11-11.10d-001", "11.10(d)", "plaintext password"),
        ]
    }
    rpath = tmp_path / "rubric.json"
    rpath.write_text(json.dumps(rubric))
    out = tmp_path / "rubric.md"
    r = subprocess.run(
        ["python3", str(SCRIPT), "--in", str(rpath), "--out", str(out)],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    md = out.read_text()
    assert md.index("11.10(d)") < md.index("11.50")
    assert "plaintext password" in md
    assert "sig manifestation gap" in md
    assert "P11-11.10d-001" in md
    assert "a pattern" in md
