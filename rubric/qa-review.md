# 21 CFR Part 11 Rubric QA Review

Reviewed: rubric/rubric.json (39 rows, merged from 5 generator slices)
Against: sources/part11.txt, rubric/test-patterns.md

---

## Duplicates and near-duplicates

No finding-category strings were found to differ by only whitespace, capitalization, or trivial paraphrase. All 39 `finding_category` values are textually distinct.

However, one pair of rows contains **near-identical code patterns** mapped to different clauses, which creates a functional near-duplicate at the code-pattern level:

**P11-11.10d-004 vs P11-11.300-004** — code-pattern near-duplicate

| | P11-11.10d-004 | P11-11.300-004 |
|---|---|---|
| `finding_category` | Session token not invalidated on logout | No loss management — compromised tokens not electronically deauthorized |
| `part11_clauses` | `["11.10(d)"]` | `["11.300"]` |
| `mapping_confidence` | `high` | `medium` |

The second code pattern of P11-11.10d-004 reads:
> "JWT-based auth with no token revocation list (blacklist) and token expiry set longer than the session idle timeout — a stolen token remains valid past logout"

The first code pattern of P11-11.300-004 reads:
> "JWT-based authentication with no token revocation mechanism — no blacklist table, no Redis revocation set, and token expiry is the only mechanism to invalidate a compromised token"

Both describe the same observable code fact: a JWT implementation with no blacklist/revocation store. A scanner encountering this pattern could fire both rows simultaneously, producing two Part 11 findings under different clauses for the same code evidence. See also the Contradictory Mappings section for the proposed resolution.

**Proposal:** Keep both rows (they address genuinely different regulatory concerns — logout vs. loss management). Remove the JWT scenario from P11-11.10d-004 `code_patterns[1]` and restrict that row to stateful session architectures only (HttpSession.invalidate path). The JWT scenario belongs exclusively to P11-11.300-004.

---

## Contradictory mappings

### Contradiction 1 — P11-11.10d-004 / P11-11.300-004: JWT blacklist absence mapped to two clauses

As detailed in the Duplicates section, both rows can be triggered by observing a JWT implementation that lacks a revocation store. They produce conflicting clause attributions:

- P11-11.10d-004 maps it to **11.10(d)** at `high` confidence ("limiting system access")
- P11-11.300-004 maps it to **11.300** at `medium` confidence ("loss management — electronically deauthorize compromised tokens")

The regulatory basis of § 11.300(c) is unambiguous: it explicitly requires procedures to "electronically deauthorize lost, stolen, missing, or otherwise potentially compromised tokens." A JWT without a revocation mechanism is a direct hit on 11.300(c). The § 11.10(d) text ("Limiting system access to authorized individuals") does not specifically address token lifecycle management after compromise.

**Proposed resolution:** P11-11.300-004 holds the correct mapping. Remove the JWT scenario from P11-11.10d-004 `code_patterns[1]` (Type A inline edit on P11-11.10d-004). P11-11.300-004 requires no change.

---

## Coverage gaps

Coverage was evaluated for all 12 targeted subsections. For each, the count of rows with `mapping_confidence` of `high` or `medium` is shown, both as primary mapping (`part11_clauses[0]`) and appearing anywhere in `part11_clauses`.

| Subsection | Primary high/med rows | Appears anywhere (high/med) | Gap? |
|---|---|---|---|
| 11.10(a) | 4 (001–004, all medium) | 4 | No |
| 11.10(c) | 2 (001 high, 002 medium) | 2 | No |
| 11.10(d) | 4 (001,003,004 high; 002 medium) | 4 | No |
| 11.10(e) | 4 (001,002,003 high; 004 medium) | 4 | No |
| 11.10(g) | 3 (001,002 high; 003 medium) | 3 | No |
| 11.10(h) | 3 (all medium) | 3 | No |
| 11.30 | 3 (001 high; 002,003 medium) | 3 | No |
| 11.50 | 4 (001,002,003,004 all high) | 4 | No |
| 11.70 | 3 (001,002 high; 003 medium) | 3 | No |
| 11.100 | 1 (001 high) | 1 | **Borderline** |
| 11.200 | 2 (001 high; 002 medium) | 2 | No |
| 11.300 | 4 (001,003 high; 002,004 medium) | 4 | No |

**11.100 — borderline coverage:** There is one `high`-confidence row (P11-11.100-001, addressing uniqueness and reassignment of signature identifiers) and one `low`-confidence row (P11-11.100-002, identity verification). No `medium`-confidence rows exist for this subsection. The low-confidence row correctly notes that § 11.100(b) (identity verification before provisioning) is primarily procedural and largely undetectable from code alone. § 11.100(c) (certification to FDA) has no code-detectable pattern at all. No gap flag is raised, but the absence of a `medium` row for any code-detectable aspect of 11.100 means coverage rests on a single `high` row. If re-dispatch capacity exists, consider adding a `medium`-confidence row for the self-service provisioning path (e.g., immediate `signing_enabled=true` without a pending-verification state machine), currently covered only at `low`.

No subsection has **zero** high/medium rows. No coverage gap flag is required.

---

## Over-mapping risks

### P11-11.10a-001 — "Missing input validation on electronic record fields"

**Risk level:** Moderate. The phrase "input validation" in the `finding_category` is the same language used to describe XSS, SQL injection, and other generic web vulnerabilities in OWASP and NIST taxonomies. A tool or analyst matching test-patterns.md Pattern 5 (reflected XSS on a search endpoint) against this rubric by `finding_category` keyword alone could classify the XSS as a 11.10(a) finding at `medium` confidence, producing a false Part 11 hit. This is precisely the failure mode that test-patterns.md Pattern 5 is designed to catch.

The `code_patterns` are specific enough to reject XSS correctly (they require `@RequestBody` → `repository.save()` without `@Valid`, entity setters without `@NotNull/@Pattern`, and absence of persistence-path tests) — but only if a tool evaluates the full `code_patterns` array. If the `finding_category` string is used as a summary label for routing or triage, the XSS overlap risk materializes.

**Proposed tightening rewrite:**
- Current: `"Missing input validation on electronic record fields"`
- Proposed: `"Missing field-level constraint enforcement on regulated record persistence path"`

This rename removes the phrase "input validation" and replaces it with language that anchors the finding to the JPA/ORM persistence layer rather than generic data sanitization.

### P11-11.10h-001 — "No source-of-input validation on inbound data operations"

**Risk level:** Low-moderate. The phrase "source-of-input validation" is ambiguous: it means "validation of the source (device) from which input originates" (the 11.10(h) device-check concept), but it can be read as "validation of the input values from any source" (a generic sanitization concept). An XSS finding would not match the `code_patterns` (which require client-certificate, API-key, or device-identifier checks), but the `finding_category` string could mislead a category-level search.

**Proposed tightening rewrite:**
- Current: `"No source-of-input validation on inbound data operations"`
- Proposed: `"Missing device-identity authentication on data ingestion endpoint"`

---

## Suspicious clause_quotes

### P11-11.30-001, P11-11.30-002, P11-11.30-003 — lowercase fragment

All three rows share the `clause_quote`:

> `"document encryption and use of appropriate digital signature standards to ensure, as necessary under the circumstances, record authenticity, integrity, and confidentiality."`

This string starts with a lowercase `"d"`. It is extracted from the middle of the § 11.30 sentence:

> "Such procedures and controls shall include those identified in § 11.10, as appropriate, and additional measures **such as document encryption** and use of appropriate digital signature standards to ensure, as necessary under the circumstances, record authenticity, integrity, and confidentiality."

The extracted fragment omits the lead-in "such as" qualifier, making it appear to be a complete independent clause when it is a subordinate fragment. An audit reader or tool treating the `clause_quote` as a self-contained sentence will misread its grammatical scope. The phrase "as necessary under the circumstances" already signals conditionality, but without the "such as" lead-in, the fragment can be misread as a mandatory requirement rather than an illustrative measure.

**Proposed fix:** Prefix all three quotes with the leading context:
> `"Such procedures and controls shall include those identified in § 11.10, as appropriate, and additional measures such as document encryption and use of appropriate digital signature standards to ensure, as necessary under the circumstances, record authenticity, integrity, and confidentiality."`

Affected rows: **P11-11.30-001, P11-11.30-002, P11-11.30-003** (Type A inline edits).

### P11-11.10d-001, P11-11.10d-002, P11-11.10d-003, P11-11.10d-004 — whole-clause quote too terse for disambiguation

All four 11.10(d) rows share the `clause_quote`:

> `"Limiting system access to authorized individuals."`

This is technically the complete text of § 11.10(d), so it is a valid substring of part11.txt and not fabricated. However, at 46 characters, it is maximally generic — it does not specify which access-control mechanism is implicated, making it impossible for an audit reader to distinguish credential storage (d-001) from actuator exposure (d-002) from IDOR (d-003) from session management (d-004) based on the quote alone. Every 11.10(d) finding looks identical at the `clause_quote` level.

This is not a correctness defect (the clause IS "Limiting system access to authorized individuals") but it creates low anchor value for reviewers and tools that use `clause_quote` for disambiguation. Per the task brief, this qualifies as a quote that "does not actually anchor the mapping."

**Proposed fix:** Each row should use a slightly expanded quote that incorporates interpretive context. Since the clause text cannot be extended (it is in full), the `evidence_needed` field for each row should be updated to explicitly name the specific access-control failure mode (already partially done for d-003 and d-004 but inconsistently applied across all four).

Affected rows: **P11-11.10d-001, P11-11.10d-002, P11-11.10d-003, P11-11.10d-004** (Type A inline edits to `evidence_needed` to add disambiguation language; `clause_quote` cannot be expanded beyond the actual clause text).

---

## Out-of-scope drift

### P11-11.10d-003 — IDOR dressed as a Part 11 finding

**ID:** P11-11.10d-003
**Finding:** "Missing authorization check before record retrieval by ID"
**Clause:** 11.10(d) at `high`

The code patterns describe a classic Insecure Direct Object Reference (IDOR) vulnerability: a `@GetMapping("/{id}")` endpoint that returns any entity for any authenticated user without ownership or role checks. IDOR is a OWASP Top 10 pattern (now under A01:2021 Broken Access Control) and a standard DAST/SAST finding.

The mapping to 11.10(d) is not incorrect — "limiting system access to authorized individuals" plausibly covers unauthorized cross-user record retrieval. However, the row makes no mention that the retrieved record must be a **regulated electronic record** under Part 11. As written, the pattern would fire on any IDOR finding in any Spring Boot application, including endpoints that return user profile photos, settings, or other non-regulated data. The `evidence_needed` section does not require confirming that the record type is subject to Part 11.

**Flag for Pattern 5 (XSS) test:** This row would not map XSS at medium-or-above confidence, so it does not fail Pattern 5. However, it could produce false Part 11 findings on non-regulated IDOR instances.

**Proposed one-line fix:** Add to `evidence_needed`: "Confirm that the record returned by the endpoint is an electronic record subject to Part 11 (i.e., a regulated record type, not a non-regulated resource)."

### P11-11.30-003 — TLS cipher hardening dressed as a Part 11 open-system finding

**ID:** P11-11.30-003
**Finding:** "TLS configuration permits weak cipher suites or outdated protocol versions"
**Clause:** 11.30 at `medium`

The code patterns describe generic TLS misconfiguration (TLSv1.0/1.1 enabled, or a custom `TrustManager` that accepts any certificate). This is a standard cryptographic hygiene finding that appears in NIST SP 800-52, CIS Benchmarks, PCI DSS, and every major TLS audit checklist. The mapping to § 11.30 is technically defensible for open-system contexts, but the code patterns make no reference to whether the affected SSL context is used for **regulated record transmission** across an open system. A Spring Boot application that uses TLSv1.1 only for an internal monitoring endpoint — not for any regulated record path — would trigger this row as a Part 11 finding.

**Proposed one-line fix:** Add to `code_patterns` a qualifying phrase: "— and the affected SSL context is used in a code path that transmits regulated electronic records across an open (non-closed) system network boundary."

---

## Summary

**Total rows reviewed:** 39

**Rows requiring inline edits (Type A):**
- P11-11.10a-001 — tighten `finding_category` to remove "input validation" phrasing
- P11-11.10d-004 — remove JWT blacklist absence from `code_patterns[1]`; restrict to stateful sessions
- P11-11.30-001 — prefix `clause_quote` with full sentence context
- P11-11.30-002 — prefix `clause_quote` with full sentence context
- P11-11.30-003 — prefix `clause_quote` with full sentence context; add regulated-record qualifier to `code_patterns`
- P11-11.10d-001 — add disambiguation language to `evidence_needed`
- P11-11.10d-002 — add disambiguation language to `evidence_needed`
- P11-11.10d-003 — add regulated-record confirmation requirement to `evidence_needed`; add disambiguation language
- P11-11.10d-004 — add disambiguation language to `evidence_needed` (in addition to code_pattern fix above)
- P11-11.10h-001 — tighten `finding_category` to remove "input validation" phrasing

**Type A ids (10 total):** P11-11.10a-001, P11-11.10d-001, P11-11.10d-002, P11-11.10d-003, P11-11.10d-004, P11-11.10h-001, P11-11.30-001, P11-11.30-002, P11-11.30-003

**Rows requiring re-generation by a subagent (Type B):** None. All identified issues are inline edits to existing fields — no row needs to be structurally rebuilt or replaced with a fresh generation.

**Coverage gaps requiring re-dispatch:** None. All 12 targeted subsections have at least one `high` or `medium` confidence row. 11.100 has borderline coverage (one `high`, one `low`, no `medium`) but does not meet the zero-high/medium threshold for mandatory re-dispatch. Optional: dispatch a subagent to add one `medium`-confidence row for § 11.100(b) (self-service provisioning without identity verification state machine), currently only covered at `low` by P11-11.100-002.

---

*Issue counts by section:*
- Duplicates/near-duplicates: 1 (code-pattern level, across P11-11.10d-004 and P11-11.300-004)
- Contradictory mappings: 1 (P11-11.10d-004 vs P11-11.300-004, JWT blacklist scenario)
- Coverage gaps: 0 (no subsection at zero high/medium; 11.100 flagged as borderline)
- Over-mapping risks: 2 (P11-11.10a-001, P11-11.10h-001)
- Suspicious clause_quotes: 2 groups, 7 rows affected (P11-11.30-001/002/003 fragment; P11-11.10d-001/002/003/004 terse)
- Out-of-scope drift: 2 (P11-11.10d-003 IDOR, P11-11.30-003 TLS hardening)
