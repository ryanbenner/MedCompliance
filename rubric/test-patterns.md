# Rubric hand-test patterns

Five patterns the merged rubric will be tested against. Patterns are written
before any generator subagent runs. Each pattern has an expected verdict that
defines what "good" looks like.

## Pattern 1 — Plaintext password column (high signal, single clause)

**Finding (paraphrased from a real Spring Boot LIMS audit):**
> A JPA `@Entity` named `LabUser` declares
> `@Column(name = "password") private String password;` with no
> `@Convert(converter = ...)` annotation and no bcrypt/argon2 call upstream
> in the `save()` path.

**Expected rubric verdict:**
- Maps to exactly **11.10(d)** with confidence `high`.
- GAMP 5 category 5.
- `evidence_needed` references the persistence call AND the absence of hashing.

## Pattern 2 — Missing audit trail on entity update (high signal, single clause)

**Finding:**
> `SpecimenServiceImpl.updateSpecimen()` mutates and persists a `Specimen`
> entity. No `@EntityListener` is registered, no `AuditingEntityListener`,
> no manual write to an audit log table, no surrounding `@Auditable` aspect.
> The entity has been updated; there is no record of who/when.

**Expected rubric verdict:**
- Maps to exactly **11.10(e)** with confidence `high`.
- GAMP 5 category 5.
- `evidence_needed` references the persistence call AND absence of any
  audit-trail mechanism in the call graph.

## Pattern 3 — Unauthenticated /actuator endpoints (medium signal, single clause)

**Finding:**
> `SecurityConfig` configures `http.authorizeHttpRequests(auth -> auth
> .requestMatchers("/actuator/**").permitAll())`. Actuator endpoints expose
> heap dumps, env vars, and DB connection info.

**Expected rubric verdict:**
- Maps to **11.10(d)** with confidence `medium` (operational hardening
  rather than per-record access control, but still authorization).
- Acceptable for it to also map to **11.10(g)** (authority checks) at
  `medium` or `low`. Two-clause fan-out is OK here; six would not be.
- GAMP 5 category 5.

## Pattern 4 — E-signature record missing signer metadata (high signal, multi-clause)

**Finding:**
> The `signRecord()` method persists a signature row with `signer_id` and
> `signed_at`, but no `signature_meaning` field, no rendered display string
> for the signer's printed name, and no cryptographic linkage between the
> signature row and the record it signs (no record hash, no FK with
> cascade-protection).

**Expected rubric verdict:**
- Maps to **11.50** (signature manifestations — missing meaning/printed name)
  AND **11.70** (signature/record linking — missing cryptographic binding).
- Confidence `high` on both.
- GAMP 5 category 5.

## Pattern 5 — Reflected XSS in a search box (negative-control / out-of-scope)

**Finding:**
> The `/specimens/search` endpoint reflects the `q` query parameter into
> the rendered HTML without escaping, allowing reflected XSS.

**Expected rubric verdict:**
- The rubric should classify this as **out of scope** (no Part 11 mapping
  at confidence ≥ medium), OR map it with explicit confidence `none` /
  `low` to no specific clause with a note that XSS is a generic web
  vulnerability outside Part 11.
- A rubric that maps generic XSS to 11.10(a) "validation" is over-mapping
  and fails this pattern.
