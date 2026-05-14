# Rubric hand-test results

## Pattern 1 — Plaintext password column

**Your verdict:**

Matched rows:
- **P11-11.10d-001** (primary, best fit) — "Plaintext credential storage in user entity"
  - Clause: **11.10(d)** — "Limiting system access to authorized individuals."
  - Confidence: **high**
  - GAMP 5: **category 5**
  - Reasoning: The finding describes a JPA `@Entity` (`LabUser`) with a `@Column(name="password") private String password` field, no `@Convert` annotation, and no bcrypt/argon2 call upstream in the `save()` path. This matches both code patterns in d-001 exactly: the entity field pattern and the absent `PasswordEncoder` bean / encoding call. The `evidence_needed` in this row explicitly says to confirm "the password column stores raw text by inspecting the entity field, the save path, and a sample database row (hash pattern absent); confirm no PasswordEncoder is wired." Before closing the finding I would verify no `@Convert` converter is performing transparent encoding, and that the field truly represents the user authentication credential (not an OAuth token).

No other rows match. P11-11.300-001 (password uniqueness) is not implicated — that row concerns username uniqueness enforcement, not storage encoding. P11-11.10a-001 (field-level constraint enforcement) is not implicated — the false-positive trap for that row explicitly excludes generic credential-storage findings and limits the row to regulated-field JPA persistence without validation, not to encryption-at-rest of passwords.

**Expected verdict:** Maps to exactly 11.10(d) with confidence `high`, GAMP 5 category 5; `evidence_needed` references the persistence call AND the absence of hashing.

**Result:** PASS

**Explanation:** The rubric fires exactly one row (P11-11.10d-001) at the correct clause (11.10(d)), with the correct confidence (high) and GAMP 5 category (5). The `evidence_needed` field explicitly calls out both the persistence-layer inspection and the absence of the PasswordEncoder. The false-positive traps guard against the `@Convert` ambiguity. All three expected criteria are satisfied.

**Proposed fix (if not PASS):** N/A

---

## Pattern 2 — Missing audit trail on entity update

**Your verdict:**

Matched rows:
- **P11-11.10e-001** (primary, best fit) — "No audit trail on entity create/update/delete"
  - Clause: **11.10(e)** — "Use of secure, computer-generated, time-stamped audit trails to independently record the date and time of operator entries and actions that create, modify, or delete electronic records."
  - Confidence: **high**
  - GAMP 5: **category 5**
  - Reasoning: The finding describes `SpecimenServiceImpl.updateSpecimen()` mutating and persisting a `Specimen` entity with no `@EntityListeners(AuditingEntityListener.class)`, no `@PrePersist`/`@PreUpdate` callback, no manual write to an audit log, and no surrounding AOP aspect. This is a direct textual match to both code patterns in e-001. The `evidence_needed` field instructs tracing "the full call graph from the service update method to persistence; confirm no audit write exists at any layer (entity listener, AOP, event listener, DB trigger visible in migration scripts)." Before closing the finding I would inspect Flyway/Liquibase migration scripts for DB triggers and check for any CDC stream, per the false-positive traps.

Secondary consideration: P11-11.10e-003 (audit trail missing operator identity) is not triggered because the finding only states that no audit trail exists at all — the absence of an `identity` field in a non-existent audit record is downstream of the primary finding and would be double-counted. P11-11.10e-002 (audit trail overwritable) is similarly not fired, as there is no audit trail to overwrite.

**Expected verdict:** Maps to exactly 11.10(e) with confidence `high`, GAMP 5 category 5; `evidence_needed` references the persistence call AND absence of any audit-trail mechanism in the call graph.

**Result:** PASS

**Explanation:** The rubric fires exactly one row (P11-11.10e-001) at the correct clause (11.10(e)), with the correct confidence (high) and GAMP 5 category (5). The `evidence_needed` field in that row exactly matches the expected description: tracing the full call graph and confirming absence of any audit mechanism. No spurious secondary rows fire.

**Proposed fix (if not PASS):** N/A

---

## Pattern 3 — Unauthenticated /actuator endpoints

**Your verdict:**

Matched rows:
- **P11-11.10d-002** (primary, best fit) — "Unauthenticated access to sensitive actuator or admin endpoints"
  - Clause: **11.10(d)** — "Limiting system access to authorized individuals."
  - Confidence: **medium**
  - GAMP 5: **category 5**
  - Reasoning: The finding describes `SecurityConfig` calling `.requestMatchers("/actuator/**").permitAll()`, with the actuator endpoints exposing heap dumps, env vars, and DB connection info. This is a direct match to the first code pattern of d-002: "Spring Security config calls `.requestMatchers('/actuator/**').permitAll()`." The actuator endpoints mentioned (heap dumps, env vars, DB connection info) map to the sensitive endpoints called out in the `evidence_needed` field (`/actuator/env`, `/actuator/heapdump`). Confidence stays at medium because network-layer controls may compensate.

Secondary consideration: **P11-11.10g-002** (unauthorized record alteration — no role gate on update endpoint) could be argued at low confidence if actuator endpoints are construed as "the system" itself. However, the g-002 pattern targets `@PutMapping`/`@PatchMapping` for regulated record entities, not management endpoints. P11-11.10g-001 (authority checks before electronic signature) is not implicated. The fan-out to 11.10(g) is at most a low-confidence secondary signal; the primary and best fit is d-002 at medium.

**Expected verdict:** Maps to 11.10(d) with confidence `medium`; acceptable to also map to 11.10(g) at `medium` or `low`. Two-clause fan-out is acceptable; GAMP 5 category 5.

**Result:** PASS

**Explanation:** The rubric fires P11-11.10d-002 at 11.10(d) with medium confidence and GAMP 5 category 5, which matches the expected verdict exactly. The secondary fan-out to 11.10(g) is possible but weak; the rubric appropriately keeps d-002 as the best fit and does not over-map to many clauses. The false-positive trap about `/actuator/health` and `/actuator/info` correctly limits the finding to the sensitive endpoints present in this pattern.

**Proposed fix (if not PASS):** N/A

---

## Pattern 4 — E-signature record missing signer metadata

**Your verdict:**

The finding contains three distinct deficiencies in the `signRecord()` output:
1. No `signature_meaning` field — missing meaning/reason for signing.
2. No rendered display string for the signer's printed name (only `signer_id` stored).
3. No cryptographic linkage between the signature row and the signed record (no record hash, no FK with cascade-protection described as a hash-based link).

Each deficiency maps to a separate rubric row:

**Matched rows:**

- **P11-11.50-002** — "E-signature record missing meaning/reason for signing"
  - Clause: **11.50**
  - Confidence: **high**
  - GAMP 5: **category 5**
  - Reasoning: `signRecord()` persists `signer_id` and `signed_at` but no `signature_meaning` field; the finding explicitly states "no `signature_meaning` field." This is a textual match to the first code pattern of 11.50-002: "SignatureRecord entity has no `signature_meaning`, `signing_reason`, or equivalent column."

- **P11-11.50-001** — "E-signature record missing printed name of signer"
  - Clause: **11.50**
  - Confidence: **high**
  - GAMP 5: **category 5**
  - Reasoning: The finding states "no rendered display string for the signer's printed name." Only `signer_id` is stored, matching the code pattern: "Signature entity or DTO has fields for `signer_id` (foreign key) and `signed_at` (timestamp) but no `printed_name` or `display_name` column." I would check whether the `signer_id` joins to an immutable user table (false-positive trap) — but absent that, 11.50-001 fires.

- **P11-11.70-001** — "No cryptographic link between signature row and signed record"
  - Clause: **11.70**
  - Confidence: **high**
  - GAMP 5: **category 5**
  - Reasoning: The finding states "no cryptographic linkage between the signature row and the record it signs (no record hash, no FK with cascade-protection)." This matches the code pattern: "SignatureRecord entity has a `record_id` foreign key to the signed record but no `record_hash` column storing a digest of the signed record's content at the time of signing." The note about "no FK with cascade-protection" is a separate concern addressed partly by P11-11.70-002 (signature row deletable), but the primary gap described is the absence of a content hash, which maps to 11.70-001.

Secondary consideration: **P11-11.70-002** (signature row deletable or reassignable) could be a tertiary match if the absence of "cascade-protection" on the FK is interpreted as the signature being reassignable. However, the finding does not explicitly describe a delete/reassign path, only the absence of a hash link — so 11.70-002 is not raised as a primary match.

Best-fit summary: P11-11.50-001 + P11-11.50-002 (clause 11.50, high) and P11-11.70-001 (clause 11.70, high). Legitimate multi-row, two-clause fan-out.

**Expected verdict:** Maps to 11.50 (missing meaning/printed name) AND 11.70 (missing cryptographic binding), confidence `high` on both, GAMP 5 category 5.

**Result:** PASS

**Explanation:** The rubric correctly fires two 11.50 rows and one 11.70 row, all at high confidence and GAMP 5 category 5, matching the expected two-clause verdict exactly. The multi-row fan-out within 11.50 (two rows for two distinct 11.50 deficiencies) is appropriate and expected; the spec says the pattern "Maps to 11.50 AND 11.70" and does not constrain it to exactly one row per clause.

**Proposed fix (if not PASS):** N/A

---

## Pattern 5 — Reflected XSS in a search box (negative control)

**Your verdict:**

The finding is: `/specimens/search` reflects the `q` query parameter into rendered HTML without escaping, enabling reflected XSS.

**Assessment against each candidate row:**

- **P11-11.10a-001** — The most tempting match (11.10(a) "validation of systems"). However, this row's false-positive trap explicitly states: *"XSS, SQL injection, and other generic input sanitization findings are explicitly out-of-scope for this row — this row fires only when regulated field data reaches a JPA/ORM persistence call without field-level constraints; do not use the `finding_category` as a keyword match for generic web sanitization findings."* The XSS pattern does not involve regulated field data reaching a JPA persistence call; it is an output-encoding deficiency in a search endpoint. **This row does NOT fire.**

- **P11-11.10d-002** — Addresses unauthenticated access to actuator/admin endpoints. XSS in a search box does not implicate access control or unauthenticated endpoint exposure. **Does not fire.**

- **P11-11.10d-003** — Addresses missing authorization before record retrieval (IDOR). XSS is an output issue, not an authorization-bypass issue. **Does not fire.**

- **P11-11.30-001 / P11-11.30-002 / P11-11.30-003** — Address encryption and integrity of records in transit or digital signatures on exported records. XSS is a browser injection attack unrelated to record transmission. **Do not fire.**

- No other rubric row has a code pattern that describes output-encoding deficiencies or reflected XSS in search endpoints. The rubric has no row for generic web application vulnerabilities.

**Conclusion:** No rubric row matches this pattern at confidence ≥ medium. The finding is out of scope for 21 CFR Part 11 as represented by this rubric.

**Expected verdict:** The rubric should classify this as out of scope (no Part 11 mapping at confidence ≥ medium), OR map it at explicit confidence `none`/`low` to no specific clause with a note that XSS is a generic web vulnerability outside Part 11. A rubric that maps XSS to 11.10(a) "validation" fails this pattern.

**Result:** PASS

**Explanation:** The rubric correctly excludes reflected XSS from Part 11 scope. The explicit false-positive trap in P11-11.10a-001 is the key discriminating element: it names XSS as out-of-scope by category, preventing the over-mapping failure mode the spec warns about. No other row in the rubric covers generic web output-encoding deficiencies. The negative control is correctly handled.

**Proposed fix (if not PASS):** N/A

---

## Summary

- **Patterns passed: 5 / 5**
- **Patterns partial: 0 / 5**
- **Patterns failed: 0 / 5**

**Top three recommended rubric edits (or "none" if all passed):**

All five patterns passed. The rubric shows strong discrimination quality. The following observations are improvement opportunities rather than failure corrections:

1. **Pattern 4 — Clarify that P11-11.50-001 and P11-11.50-002 are expected to co-fire:** The rubric has no guidance indicating that multiple 11.50 rows can and should fire simultaneously for a single signature-record finding. Adding a `co_fires_with` or `related_rows` field on 11.50-001 and 11.50-002 pointing to each other (and to 11.70-001) would help inspectors understand that a single `signRecord()` deficiency legitimately produces a multi-row, multi-clause finding without it being an error.

2. **Pattern 3 — Make the 11.10(g) secondary mapping explicit:** The expected verdict for Pattern 3 acknowledges that an additional 11.10(g) mapping at medium/low is acceptable. Currently the rubric has no row that would cleanly fire on "actuator endpoints with no authority check" under 11.10(g). Adding a note to P11-11.10g-002 or P11-11.10d-002 acknowledging the clause overlap for management endpoints would reduce ambiguity for inspectors who expect to see the 11.10(g) signal.

3. **None required for correctness** — all patterns produced the correct verdict. The two edits above improve usability and inter-row navigation but do not fix any discrimination failure.
