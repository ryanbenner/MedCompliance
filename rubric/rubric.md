# 21 CFR Part 11 → Code-Pattern Rubric

Generated from rubric.json. Each section lists code-detectable patterns that implicate the named subsection. Rows are grouped by their first-listed clause; rows that map to multiple clauses appear once, under the primary clause.

## 11.10(a)

### `P11-11.10a-001` — Missing field-level constraint enforcement on regulated record persistence path

> Validation of systems to ensure accuracy, reliability, consistent intended performance, and the ability to discern invalid or altered records.

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - Service or controller method accepts a record payload (e.g., @RequestBody) and directly persists it via repository.save() with no @Valid annotation and no explicit field-level validation before the call
  - Entity setter or constructor accepts a String parameter for a regulated field (e.g., lotNumber, specimenId) without length, format, or null checks — no @NotNull/@Pattern annotation and no guard clause
  - No unit or integration test class in the project exercises a save path with an out-of-range or malformed value for regulated record fields
- **Evidence needed:** Trace the save() call graph from the API endpoint to persistence layer; confirm absence of @Valid, Validator.validate(), or equivalent guard; confirm no schema-level constraint in the ORM mapping for the field in question.
- **False-positive traps:**
  - Validation may be enforced at the database DDL level (NOT NULL, CHECK constraints) even when absent in application code — check migration scripts before calling this a finding
  - A @Valid on the outer DTO may cascade to nested objects; inspect the full object graph before concluding validation is absent
  - Third-party framework interceptors (e.g., Spring's HandlerMethodArgumentResolverComposite) may silently apply validation even without explicit annotations in the observed class
  - XSS, SQL injection, and other generic input sanitization findings are explicitly out-of-scope for this row — this row fires only when regulated field data reaches a JPA/ORM persistence call without field-level constraints; do not use the finding_category as a keyword match for generic web sanitization findings

### `P11-11.10a-002` — No checksum or hash verification on retrieved electronic records

> Validation of systems to ensure accuracy, reliability, consistent intended performance, and the ability to discern invalid or altered records.

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - Record retrieval service (findById, fetchRecord) returns a deserialized entity with no integrity check — no comparison of a stored hash/checksum field against a freshly computed digest of the record's content fields
  - Entity class declares no @Column for a hash or checksum field, and there is no @PostLoad callback computing one
- **Evidence needed:** Review the entity class for a checksum/hash column; review the repository or service layer for any digest computation on load; absence of both is the finding.
- **False-positive traps:**
  - Some systems rely on database transaction isolation rather than application-level checksums — this is an architectural choice, not necessarily non-compliant; inspector must assess whether the system can discern altered records by other means
  - A separate audit trail (see 11.10(e)) that records every mutation can substitute for per-record checksums for discerning alteration

### `P11-11.10a-003` — No IQ/OQ/PQ test coverage for regulated record operations

> Validation of systems to ensure accuracy, reliability, consistent intended performance, and the ability to discern invalid or altered records.

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - No test class in the codebase exercises the create, update, or delete path for regulated entity types with assertions on returned values — measured by finding zero @Test methods whose names or body reference the regulated entity name and a persistence call
  - Test directory is absent or contains only smoke tests with no assertion on record field values after persistence
- **Evidence needed:** Enumerate all @Test/@ParameterizedTest methods; filter for those exercising regulated entity persistence; confirm no assertion on post-save field values. IQ/OQ/PQ documentation gap must be confirmed separately.
- **False-positive traps:**
  - External validation protocol documents (IQ/OQ/PQ scripts in PDF) are the primary evidence for 11.10(a) validation — absence of automated tests alone is insufficient if manual protocol records exist
  - A project may use BDD/Cucumber feature files not discovered by a grep for @Test — check all test directories

### `P11-11.10a-004` — Mutable entity allows post-save field overwrite without version guard

> Validation of systems to ensure accuracy, reliability, consistent intended performance, and the ability to discern invalid or altered records.

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - JPA entity class has public setters on all regulated fields and no @Version field, enabling a lost-update scenario where two concurrent writers silently overwrite each other's changes
  - Repository exposes a bulk update method (e.g., @Modifying @Query('UPDATE ...')) with no WHERE clause version check
- **Evidence needed:** Confirm entity has no @Version field; confirm service layer has no optimistic-lock retry or pessimistic-lock annotation; reproduce with a concurrent test or review transaction isolation level.
- **False-positive traps:**
  - Database-level serializable isolation may prevent lost updates even without @Version — confirm transaction isolation level before raising
  - Read-only entities with no update path are not implicated by this pattern

## 11.10(c)

### `P11-11.10c-001` — Missing retention enforcement — records deletable before retention period expires

> Protection of records to enable their accurate and ready retrieval throughout the records retention period.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - Repository exposes a deleteById() or delete() method callable from a service or REST endpoint with no guard checking a retentionExpiry or deletionAllowed flag on the record
  - Soft-delete pattern absent: entity has no @Column for deleted_at or is_archived, and hard-delete is the only deletion path in the codebase
- **Evidence needed:** Confirm deleteById/delete is reachable from a non-admin endpoint with no retention-period check; confirm entity lacks soft-delete columns; confirm no scheduled job enforces a retention hold.
- **False-positive traps:**
  - Admin-only delete endpoints protected by role checks (ROLE_ADMIN) may be compliant depending on SOPs — inspect whether the admin role is tightly controlled
  - Cascade deletes on parent entities may appear to delete records indirectly — trace cascade relationships before concluding records are unprotected

### `P11-11.10c-002` — Archive or export path produces incomplete record copies

> Protection of records to enable their accurate and ready retrieval throughout the records retention period.

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - Export/archive method serializes only a subset of entity fields (e.g., a hand-written toExportDto() that omits audit timestamps, signer ID, or version fields) resulting in a retrievable copy lacking fields required for accurate reproduction
  - A scheduled archival job moves records to cold storage but truncates or omits columns flagged as 'internal' in the mapping
- **Evidence needed:** Compare the entity field list against the serialized output of the export method; identify omitted fields; confirm those fields are required for record accuracy under the relevant records requirement.
- **False-positive traps:**
  - Some fields are legitimately excluded from exports (e.g., internal cache columns) — only regulated data fields are in scope for this finding
  - A separate archival system may store the complete record even if the application-level export is partial

### `P11-11.10c-003` — No retrieval test confirming records survive retention period boundary

> Protection of records to enable their accurate and ready retrieval throughout the records retention period.

- **Confidence:** low  **GAMP 5:** category 5
- **Code patterns:**
  - No integration test or validation script exercises a read path for a record whose creation date is older than the configured retention period — i.e., no test seeds an old-dated record and asserts it is still retrievable
  - Application has a configurable DATA_RETENTION_YEARS property but no automated check that reads records aged past that boundary to confirm they exist
- **Evidence needed:** Review test suite for any test that seeds records with past dates and asserts retrieval after a simulated retention period boundary; absence is a low-confidence code-level signal only — primary evidence is validation protocol documents.
- **False-positive traps:**
  - Database backups and archival infrastructure outside the application codebase can satisfy retrieval requirements — code-level absence is not sufficient alone
  - Cloud-managed storage with retention locks (e.g., S3 Object Lock) may satisfy this independent of application code

## 11.10(d)

### `P11-11.10d-001` — Plaintext credential storage in user entity

> Limiting system access to authorized individuals.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - JPA @Entity class declares @Column(name='password') private String password with no @Convert annotation and no password encoding call (e.g., BCryptPasswordEncoder.encode()) in the upstream save() or registration service method
  - PasswordEncoder bean is absent from the Spring Security configuration class — no @Bean method returning a PasswordEncoder or BCryptPasswordEncoder
- **Evidence needed:** Confirm the password column stores raw text by inspecting the entity field, the save path, and a sample database row (hash pattern absent); confirm no PasswordEncoder is wired. [Disambiguation: this row addresses credential storage failure — the specific access-control failure mode is that plaintext credentials can be exfiltrated and replayed to gain unauthorized system access, implicating the 'limiting system access' requirement directly at the credential layer.]
- **False-positive traps:**
  - An @Convert annotation using a custom AttributeConverter may perform encoding transparently — inspect the converter implementation before concluding storage is plaintext
  - Some entities store an OAuth token or API key in a field named 'password' that is not the user credential — confirm the field semantics

### `P11-11.10d-002` — Unauthenticated access to sensitive actuator or admin endpoints

> Limiting system access to authorized individuals.

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - Spring Security config calls .requestMatchers('/actuator/**').permitAll() or .requestMatchers('/admin/**').permitAll() without a compensating role restriction on a narrower matcher
  - WebSecurityCustomizer bean calls web.ignoring().requestMatchers('/actuator/**') bypassing the filter chain entirely for those paths
- **Evidence needed:** Confirm the endpoint is reachable without a session or token by tracing the security filter chain; confirm the endpoint exposes regulated record data or system credentials (e.g., /actuator/env, /actuator/heapdump). [Disambiguation: this row addresses unauthenticated endpoint exposure — the specific access-control failure mode is missing authentication at the HTTP security filter layer for management/admin paths, not credential storage (d-001), not per-record ownership authorization (d-003), and not session lifecycle management (d-004).]
- **False-positive traps:**
  - Actuator endpoints may be restricted at the network/reverse-proxy layer even when the application allows them — verify network-layer controls before raising as a finding
  - /actuator/health and /actuator/info are commonly left open by design and carry no regulated data; restrict this finding to endpoints exposing credentials or record data

### `P11-11.10d-003` — Missing authorization check before record retrieval by ID

> Limiting system access to authorized individuals.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - REST controller method annotated @GetMapping('/{id}') calls repository.findById(id) and returns the entity with no @PreAuthorize, no ownership check (e.g., entity.getOwnerId().equals(currentUserId())), and no role gate — allowing any authenticated user to retrieve any record by guessing the ID (IDOR)
  - Service method fetchRecord(Long id) has no SecurityContext lookup and no assertion that the requester owns or has been granted access to the specific record
- **Evidence needed:** Confirm the endpoint is reachable by a low-privileged authenticated user; confirm the ID space is guessable (sequential integer or short UUID); confirm a record belonging to a different user is returned. Confirm that the record returned by the endpoint is an electronic record subject to Part 11 (i.e., a regulated record type, not a non-regulated resource such as user profile photos, settings, or other non-regulated data). [Disambiguation: this row addresses per-record ownership authorization failure (IDOR) — the specific access-control failure mode is missing cross-user access gate at the record retrieval level for Part 11-regulated records, distinct from missing authentication (d-002), credential storage (d-001), and session lifecycle (d-004).]
- **False-positive traps:**
  - UUIDs with sufficient entropy may mitigate IDOR even without authorization checks — assess effective exploitability but still note the missing access control as a design gap
  - Multi-tenant filtering at the JPA layer (e.g., Hibernate @Filter on tenantId) may transparently enforce ownership — inspect the filter configuration
  - IDOR on non-regulated resources (user profile photos, application settings, non-Part-11 data) is out of scope for this row — confirm the retrieved record type is subject to Part 11 before raising

### `P11-11.10d-004` — Session token not invalidated on logout

> Limiting system access to authorized individuals.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - Logout endpoint calls SecurityContextHolder.clearContext() but does not call HttpSession.invalidate() or TokenStore.removeAccessToken(), leaving the stateful server-side session or opaque bearer token valid for reuse — applies to HttpSession-based and stateful token-store architectures only
  - Spring Security logout handler is configured with .logoutSuccessUrl('/login') but no .invalidateHttpSession(true) or .deleteCookies('JSESSIONID'), leaving the session active in the server-side session store after the user has logged out
- **Evidence needed:** Confirm the logout endpoint does not invalidate the server-side session (HttpSession.invalidate() absent) and that a captured session cookie continues to return 200 on authenticated endpoints post-logout. This row applies to stateful session architectures; JWT stateless token revocation absence is addressed by P11-11.300-004, not this row. [Disambiguation: this row addresses live session invalidation failure at logout — the specific access-control failure mode is that a logged-out user's stateful session remains usable, distinct from credential storage (d-001), unauthenticated endpoint exposure (d-002), and per-record ownership authorization (d-003).]
- **False-positive traps:**
  - JWT-based stateless authentication architectures are out of scope for this row — JWT token revocation absence (no blacklist/revocation store) is covered by P11-11.300-004, not here; applying both rows to the same JWT implementation creates a duplicate finding
  - Token revocation may be handled by an API gateway or OAuth server outside the application codebase — check the full auth architecture before raising

## 11.10(e)

### `P11-11.10e-001` — No audit trail on entity create/update/delete

> Use of secure, computer-generated, time-stamped audit trails to independently record the date and time of operator entries and actions that create, modify, or delete electronic records.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - JPA @Entity class has no @EntityListeners(AuditingEntityListener.class) annotation, no @CreatedDate/@LastModifiedDate fields, no @PrePersist/@PreUpdate lifecycle callbacks writing to an audit log table, and no surrounding AOP @Aspect with a @AfterReturning advice on repository.save()
  - Service method updateRecord() calls repository.save(entity) with no subsequent call to auditLogRepository.save() or auditEventPublisher.publish()
- **Evidence needed:** Trace the full call graph from the service update method to persistence; confirm no audit write exists at any layer (entity listener, AOP, event listener, DB trigger visible in migration scripts).
- **False-positive traps:**
  - Database triggers in migration scripts (e.g., Flyway/Liquibase) may write to an audit table without any application-level code — inspect migration files before concluding audit trail is absent
  - An infrastructure-level CDC (Change Data Capture) stream (e.g., Debezium) may capture all changes externally — this satisfies the requirement even if no application-level audit code exists
  - Spring Data JPA @CreatedDate/@LastModifiedDate with @EnableJpaAuditing satisfies timestamping of the record itself but does NOT write a separate audit trail entry — distinguish between in-row timestamps and an independent audit log

### `P11-11.10e-002` — Audit trail records overwritable by application

> Use of secure, computer-generated, time-stamped audit trails to independently record the date and time of operator entries and actions that create, modify, or delete electronic records. Record changes shall not obscure previously recorded information.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - AuditLog entity exposes a public setter on its content, timestamp, or userId field and the corresponding repository has no @PreUpdate guard preventing modification of existing audit rows
  - AuditLogRepository extends JpaRepository<AuditLog, Long> exposing deleteById() callable from a service layer method without restriction to a superuser-only path
- **Evidence needed:** Confirm an existing audit log row can be updated or deleted via the application API without superuser escalation; inspect the database grant — the application DB user should have INSERT-only on audit tables, not UPDATE/DELETE.
- **False-positive traps:**
  - Soft-delete on audit records (setting is_deleted=true) rather than physical DELETE may be acceptable depending on whether the original entry remains retrievable — assess retrieval path
  - Superuser-only deletion for compliance holds purges is a legitimate operational need; the finding applies only when non-privileged application roles can delete audit rows

### `P11-11.10e-003` — Audit trail missing operator identity

> Use of secure, computer-generated, time-stamped audit trails to independently record the date and time of operator entries and actions that create, modify, or delete electronic records.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - AuditLog entity has timestamp and action fields but no userId or username column — the recorded entry cannot be attributed to the individual who performed the action
  - Audit write code retrieves the current user as a system service account (e.g., always writes userId='system') rather than reading from SecurityContextHolder.getContext().getAuthentication().getName()
- **Evidence needed:** Inspect the AuditLog entity schema for a user identifier column; inspect the audit write path to confirm it sources the identity from the authenticated principal, not a hardcoded constant.
- **False-positive traps:**
  - Audit records in a shared-service architecture may record the calling service identity rather than end-user identity — assess whether the calling service passes the delegated user context in a header that is captured
  - Batch jobs running as a service account legitimately record the service account identity — apply this pattern only to interactive user-driven operations

### `P11-11.10e-004` — Audit trail retention shorter than record retention

> Such audit trail documentation shall be retained for a period at least as long as that required for the subject electronic records and shall be available for agency review and copying.

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - Scheduled @Scheduled(cron=...) purge job deletes AuditLog rows older than a configured audit.retention.days property, but the subject record retention period (record.retention.years) is longer — audit rows are purged before the records they describe
  - Application configuration file sets audit.retention.days=365 while the regulatory requirement for the subject records is 2+ years
- **Evidence needed:** Compare audit.retention.days/years config value against the regulatory retention requirement for the subject records; confirm the purge job uses the shorter value.
- **False-positive traps:**
  - Audit logs may be archived to cold storage rather than deleted — confirm that purged-from-database rows are truly unrecoverable and not archived elsewhere
  - The regulatory retention period may vary by record type — confirm the comparison is made for the same record category

## 11.10(g)

### `P11-11.10g-001` — Missing authority checks before electronic signature operations

> Use of authority checks to ensure that only authorized individuals can use the system, electronically sign a record, access the operation or computer system input or output device, alter a record, or perform the operation at hand.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - signRecord() service method persists a signature row without calling hasAuthority('ROLE_SIGNER') or equivalent — any authenticated user can invoke the signing path
  - No @PreAuthorize or @Secured annotation on the controller method mapped to POST /records/{id}/sign
- **Evidence needed:** Confirm the signing endpoint accepts requests from a user without ROLE_SIGNER; confirm the resulting signature row is persisted; confirm no server-side role check exists in the call graph.
- **False-positive traps:**
  - Role enforcement may be delegated to an upstream API gateway — verify whether the application itself enforces the check or relies on a gateway contract
  - Workflow state-machine checks (e.g., record must be in DRAFT state to sign) may partially restrict signing but do not substitute for role-based authority checks

### `P11-11.10g-002` — Unauthorized record alteration — no role gate on update endpoint

> Use of authority checks to ensure that only authorized individuals can use the system, electronically sign a record, access the operation or computer system input or output device, alter a record, or perform the operation at hand.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - REST controller @PutMapping or @PatchMapping for a regulated record entity has no @PreAuthorize annotation and no in-method role check — any authenticated user can alter the record
  - Bulk update service method updateAllRecords() has no caller role assertion and is reachable from a non-privileged API endpoint
- **Evidence needed:** Confirm PUT/PATCH endpoint returns 200 for a user without an editor or admin role; confirm the entity is mutated in the database.
- **False-positive traps:**
  - Ownership-based update (user can only update their own draft records) may be compliant for certain record types — assess whether the SOP requires a separate approver role
  - Read-only replicas or archived records may intentionally block updates at the database layer even when the application endpoint is unguarded

### `P11-11.10g-003` — Authority check configuration in YAML/properties — missing or overly permissive role definitions

> Use of authority checks to ensure that only authorized individuals can use the system, electronically sign a record, access the operation or computer system input or output device, alter a record, or perform the operation at hand.

- **Confidence:** medium  **GAMP 5:** category 4
- **Code patterns:**
  - application.yml or security-roles.yaml defines a role hierarchy where ROLE_USER inherits ROLE_SIGNER or ROLE_APPROVER, granting all users signing authority by default
  - Role definition configuration file assigns all permissions to a default role with no explicit exclusion of signing or record-alteration permissions
- **Evidence needed:** Read the role hierarchy configuration; trace effective permissions of ROLE_USER to confirm it includes ROLE_SIGNER or equivalent signing permission.
- **False-positive traps:**
  - Role inheritance in configuration may be intentional for a specific deployment context — compare against the system's access control SOP before raising
  - A separate identity provider (IdP) may override application-level role definitions — confirm which role source is authoritative

## 11.10(h)

### `P11-11.10h-001` — Missing device-identity authentication on data ingestion endpoint

> Use of device (e.g., terminal) checks to determine, as appropriate, the validity of the source of data input or operational instruction.

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - Data ingestion endpoint accepts POST requests with no validation of a client certificate, API key, or registered device identifier — any network client can submit data as if it were a trusted instrument or terminal
  - Instrument data import service reads from a file drop directory with no hash verification of the file source or digital signature on the payload — a file placed by any process is treated as originating from a trusted device
- **Evidence needed:** Confirm the ingestion endpoint or file import path accepts input without any device or client authentication; confirm data is persisted as a regulated record without source validation.
- **False-positive traps:**
  - Network-layer mTLS termination at a load balancer or API gateway may enforce device certificates even when the application code does not check them — verify end-to-end trust chain
  - For internal lab instruments on an isolated network segment, device-level authentication may be satisfied by network controls rather than application code

### `P11-11.10h-002` — Operational instruction accepted from unauthenticated source

> Use of device (e.g., terminal) checks to determine, as appropriate, the validity of the source of data input or operational instruction.

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - Internal REST or message-queue consumer processes instrument control commands (e.g., start run, abort run) with no verification that the message originates from a registered, authenticated device — message broker topic is unauthenticated
  - Admin command endpoint accepts operational instructions via a shared secret in a query parameter rather than a per-device signed token or certificate
- **Evidence needed:** Confirm the command consumer has no device-identity verification logic; confirm the message broker queue is not restricted to registered publisher certificates or credentials.
- **False-positive traps:**
  - This clause applies 'as appropriate' — systems with no instrument integration or no remote operational instructions are not implicated; confirm the system actually receives device-originated commands
  - VPN or firewall rules restricting which IP addresses can reach the command endpoint partially mitigate this — assess residual risk rather than treating as equivalent to cryptographic device authentication

### `P11-11.10h-003` — No validation of data input source identity in multi-tenant context

> Use of device (e.g., terminal) checks to determine, as appropriate, the validity of the source of data input or operational instruction.

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - Multi-tenant SaaS application accepts data submissions with a tenantId claim in a JWT but does not verify that the submitting device is registered under that tenant — any device authenticating as tenant A could submit data attributed to tenant B if the tenantId claim is user-controlled
  - Data import API reads tenantId from the request body (user-controlled) rather than from the validated JWT claims — device identity is not verified against the tenant's registered device list
- **Evidence needed:** Confirm tenantId in the data submission path is sourced from user-controlled input rather than validated JWT or session claims; confirm no cross-check against a registered device table.
- **False-positive traps:**
  - If the tenantId is embedded in the authenticated JWT and not overridable by the request body, this pattern does not apply — inspect the claim extraction code carefully
  - Single-tenant deployments are not implicated by cross-tenant confusion patterns

## 11.30

### `P11-11.30-001` — No encryption of records transmitted over open networks

> Such procedures and controls shall include those identified in § 11.10, as appropriate, and additional measures such as document encryption and use of appropriate digital signature standards to ensure, as necessary under the circumstances, record authenticity, integrity, and confidentiality.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - HTTP client configuration (RestTemplate, OkHttpClient, WebClient) uses a plain http:// base URL for calls to external services that transmit regulated records — TLS is not enforced
  - Spring Boot application.properties sets server.ssl.enabled=false or omits SSL configuration entirely while the application is deployed in a context accessible beyond a trusted private network
- **Evidence needed:** Confirm the application endpoint or outbound client uses unencrypted HTTP for regulated record transmission; confirm the network path crosses an untrusted segment (open system context).
- **False-positive traps:**
  - TLS may be terminated at a load balancer or reverse proxy (e.g., nginx, AWS ALB) — the application-to-proxy leg may be HTTP while the external-facing endpoint is HTTPS; verify the full path
  - If the system is a closed system (§11.10) rather than an open system (§11.30), this specific clause does not apply — confirm the system classification

### `P11-11.30-002` — No digital signature on records transmitted to external parties

> Such procedures and controls shall include those identified in § 11.10, as appropriate, and additional measures such as document encryption and use of appropriate digital signature standards to ensure, as necessary under the circumstances, record authenticity, integrity, and confidentiality.

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - Record export or submission method serializes the record to JSON/XML and POSTs it to an external endpoint with no HMAC, RSA, or ECDSA signature appended to the payload — recipient cannot verify authenticity or detect in-transit modification
  - No code in the codebase references java.security.Signature, javax.crypto.Mac, or a third-party signing library (e.g., Bouncy Castle) in the context of record transmission
- **Evidence needed:** Confirm the transmission path for regulated records to external parties includes no payload signature; confirm TLS alone is deemed insufficient for the authenticity requirement given the system's threat model.
- **False-positive traps:**
  - For most open-system transmissions TLS provides sufficient confidentiality and integrity — a digital signature on the payload is required only when non-repudiation or post-transmission tamper detection is needed; assess the regulatory context before raising
  - S/MIME or PGP email signing performed outside the application (e.g., by an email gateway) may satisfy this for email-based submissions

### `P11-11.30-003` — TLS configuration permits weak cipher suites or outdated protocol versions

> Such procedures and controls shall include those identified in § 11.10, as appropriate, and additional measures such as document encryption and use of appropriate digital signature standards to ensure, as necessary under the circumstances, record authenticity, integrity, and confidentiality.

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - SSLContext or TrustManager configuration explicitly enables TLSv1.0 or TLSv1.1 protocol versions via setEnabledProtocols() or server.ssl.enabled-protocols=TLSv1,TLSv1.1 — and the affected SSL context is used in a code path that transmits regulated electronic records across an open (non-closed) system network boundary
  - HttpsURLConnection or SSLSocketFactory is configured with a custom TrustManager that overrides checkServerTrusted() with an empty body — accepting any certificate including self-signed or revoked ones — and the affected SSL context is used in a code path that transmits regulated electronic records across an open (non-closed) system network boundary
- **Evidence needed:** Confirm the SSL/TLS configuration enables deprecated protocols or disables certificate validation; confirm the affected SSL context is used in a transmission path that carries regulated electronic records across an open system network boundary (§11.30 scope); TLS misconfiguration on non-regulated or internal monitoring paths is out of scope for this row.
- **False-positive traps:**
  - Disabled certificate validation in a test/dev profile only (detected by @Profile('dev') or if active profile is not production) is not a production finding — confirm the active deployment profile
  - Legacy instrument integration may require older TLS versions as the instrument does not support TLS 1.2+ — document as a compensating control finding rather than a direct violation

## 11.50

### `P11-11.50-001` — E-signature record missing printed name of signer

> Signed electronic records shall contain information associated with the signing that clearly indicates all of the following: (1) The printed name of the signer;

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - Signature entity or DTO has fields for signer_id (foreign key) and signed_at (timestamp) but no printed_name or display_name column — the stored record does not contain the human-readable name of the signer at the time of signing
  - signRecord() service method persists the signature row using only the user's numeric ID; no join to retrieve and store the display name at signing time, meaning subsequent name changes would make the name unrecoverable for the historical record
- **Evidence needed:** Inspect the SignatureRecord entity or table schema for a printed name column; confirm the signing service does not capture the name at signing time; confirm a name change to the user account would make attribution incomplete.
- **False-positive traps:**
  - If the system stores the user ID and the user table is immutable (names cannot be changed), the name can be reconstructed at retrieval time — assess whether this constitutes 'contained in the record' per FDA interpretation
  - An audit report layer that dynamically joins user name at display time may render the printed name in human-readable output even if not stored in the signature row itself — assess the human-readable form output path

### `P11-11.50-002` — E-signature record missing meaning/reason for signing

> Signed electronic records shall contain information associated with the signing that clearly indicates all of the following: (1) The printed name of the signer; (2) The date and time when the signature was executed; and (3) The meaning (such as review, approval, responsibility, or authorship) associated with the signature.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - SignatureRecord entity has no signature_meaning, signing_reason, or equivalent column — the stored row cannot indicate whether the signature represents review, approval, authorship, or another meaning
  - signRecord() method is called with only (recordId, userId) parameters — no signing reason is accepted or persisted
- **Evidence needed:** Confirm the signature table schema has no meaning/reason column; confirm the signing API accepts no meaning parameter; inspect any human-readable display of the signed record to confirm meaning is absent.
- **False-positive traps:**
  - Signing reason may be inferred from workflow state (e.g., signatures on records in APPROVED state always mean approval) — assess whether the system context makes the meaning unambiguous without explicit storage
  - A fixed-purpose signing workflow (only one action type ever signed) may have the meaning implicit; FDA guidance allows implicit meaning when context is unambiguous

### `P11-11.50-003` — Signature metadata not included in human-readable record output

> The items identified in paragraphs (a)(1), (a)(2), and (a)(3) of this section shall be subject to the same controls as for electronic records and shall be included as part of any human readable form of the electronic record (such as electronic display or printout).

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - PDF or HTML report generation method for a signed record renders the record content fields but omits the signature block (signer name, date/time, meaning) from the rendered output
  - Record printout template (e.g., Thymeleaf, Jasper Report) has no template variable or data binding for signature metadata — the rendered human-readable form shows only the record body
- **Evidence needed:** Generate a human-readable output (PDF/HTML printout) of a signed record and confirm the signer name, signing timestamp, and meaning are absent from the rendered document.
- **False-positive traps:**
  - Signature block may be rendered by a parent template or layout that is not visible in the child template file — inspect the full template inheritance chain
  - An electronic display path and a printout path may differ — confirm the finding applies to both paths or note which is deficient

### `P11-11.50-004` — Signing timestamp uses client-supplied time rather than server-generated time

> Signed electronic records shall contain information associated with the signing that clearly indicates all of the following: (1) The printed name of the signer; (2) The date and time when the signature was executed; and (3) The meaning (such as review, approval, responsibility, or authorship) associated with the signature.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - signRecord() service method reads the signing timestamp from the request body (e.g., request.getSignedAt()) and persists it directly — the client can supply an arbitrary past or future timestamp
  - SignatureRecord.signedAt is populated from a DTO field mapped from the JSON payload rather than from Instant.now() or a server-side clock call at the point of persistence
- **Evidence needed:** Confirm the signedAt value is sourced from the request payload; confirm it can be set to an arbitrary value by sending a custom timestamp in the POST body; confirm the server does not overwrite it with a server-generated timestamp.
- **False-positive traps:**
  - Client-supplied timestamps may be validated against a maximum skew window (e.g., reject if more than 5 minutes from server time) — a tight skew check partially mitigates the risk even if not fully compliant
  - Some architectures record both a client_timestamp and a server_received_at — if the server timestamp is what is displayed and stored as the official signing time, this pattern does not apply

## 11.70

### `P11-11.70-001` — No cryptographic link between signature row and signed record

> Electronic signatures and handwritten signatures executed to electronic records shall be linked to their respective electronic records to ensure that the signatures cannot be excised, copied, or otherwise transferred to falsify an electronic record by ordinary means.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - SignatureRecord entity has a record_id foreign key to the signed record but no record_hash column storing a digest (e.g., SHA-256) of the signed record's content at the time of signing — a post-signing edit to the record content is undetectable by inspecting the signature row
  - signRecord() service method persists the signature with only a foreign key reference; no hash of the record's serialized content is computed and stored alongside the signature
- **Evidence needed:** Confirm SignatureRecord schema has no content hash column; confirm that modifying the signed record's fields after signing does not invalidate the signature; confirm no trigger or application check validates hash integrity on record retrieval.
- **False-positive traps:**
  - Immutable records (append-only storage, database row-level locking preventing updates after signing) can satisfy the linking requirement without a hash — assess whether the record is truly immutable post-signing
  - A digital signature (asymmetric key signature over record content) subsumes the hash requirement — check for any RSA/ECDSA signing of the record body before concluding linking is absent

### `P11-11.70-002` — Signature row deletable or reassignable without cascading invalidation

> Electronic signatures and handwritten signatures executed to electronic records shall be linked to their respective electronic records to ensure that the signatures cannot be excised, copied, or otherwise transferred to falsify an electronic record by ordinary means.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - SignatureRepository exposes deleteById() or delete() callable from a service method without an immutability guard — an application user with sufficient privilege can excise a signature from a record
  - SignatureRecord.recordId can be updated via a setter or @Modifying @Query — the signature can be reassigned to a different record, constituting a transfer to falsify another record
- **Evidence needed:** Confirm a signature row can be deleted or its record_id updated via the application API; confirm the signed record does not detect or flag the missing or reassigned signature.
- **False-positive traps:**
  - Superuser-only deletion for regulatory purge holds is a legitimate need — the finding applies when non-privileged roles can excise signatures
  - A soft-delete (is_deleted flag) on signatures may be acceptable if the original record and a flag indicating deletion are preserved and retrievable

### `P11-11.70-003` — Signature hash computed over partial record content

> Electronic signatures and handwritten signatures executed to electronic records shall be linked to their respective electronic records to ensure that the signatures cannot be excised, copied, or otherwise transferred to falsify an electronic record by ordinary means.

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - computeRecordHash() method serializes only a subset of the entity's fields (e.g., result fields but not status, reviewer notes, or version) — mutations to excluded fields are not detected by the stored hash
  - Hash is computed over the record's toString() output which excludes transient or lazily-loaded fields that are part of the regulated record content
- **Evidence needed:** Compare the set of fields included in the hash computation against the complete set of regulated fields in the entity; confirm that modifying an excluded field does not change the stored hash.
- **False-positive traps:**
  - Internal system fields (e.g., JPA version counter, cache busting timestamps) are legitimately excluded from content hashes — only regulated data fields matter for this finding
  - A canonical serialization that is documented and stable is sufficient even if it excludes some entity fields, provided the excluded fields are not part of the regulated record content

## 11.100

### `P11-11.100-001` — Electronic signature ID reuse or reassignment allowed by code

> Each electronic signature shall be unique to one individual and shall not be reused by, or reassigned to, anyone else.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - User entity allows the username or email (used as the electronic signature identifier) to be updated via a PUT /users/{id} endpoint with no guard preventing reuse of a previously assigned identifier — a deactivated user's username can be reassigned to a new user
  - No UNIQUE constraint on the username or signature_id column in the database migration scripts, allowing the same identifier to be assigned to multiple users over time
- **Evidence needed:** Confirm the user identifier field has no UNIQUE database constraint or that the application permits username reassignment; confirm a deactivated user's identifier can be given to a new user.
- **False-positive traps:**
  - UUID-based user IDs are globally unique by construction — if the signature identifier is the UUID (not the username), reassignment is not possible; confirm which field serves as the electronic signature identifier
  - SSO/IdP-managed identities may enforce uniqueness externally — confirm whether the application enforces it independently

### `P11-11.100-002` — No identity verification before electronic signature provisioning

> Before an organization establishes, assigns, certifies, or otherwise sanctions an individual's electronic signature, or any element of such electronic signature, the organization shall verify the identity of the individual.

- **Confidence:** low  **GAMP 5:** category 5
- **Code patterns:**
  - User registration endpoint allows self-service account creation with only an email and password — no identity verification step (email confirmation, manager approval, identity document check) is enforced before the account can be used to sign records
  - UserService.createUser() method immediately sets account status to ACTIVE and signing_enabled=true with no pending verification state and no admin approval workflow
- **Evidence needed:** This clause is primarily procedural; code-level signal is the absence of any approval workflow or identity verification state in the user provisioning path. Low confidence because compliant identity verification may occur outside the application (e.g., HR onboarding). Confirm SOPs and onboarding records separately.
- **False-positive traps:**
  - Identity verification may be enforced by an upstream IdP or HR system external to the application — absence of verification code in the application is not a finding if an external process is documented
  - Email confirmation alone may satisfy some interpretations of identity verification for low-risk contexts — assess the regulatory context and system risk classification

## 11.200

### `P11-11.200-001` — Single-factor authentication used for electronic signature

> Employ at least two distinct identification components such as an identification code and password.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - signRecord() service method requires only a re-entry of the user's password (one factor) to authorize a signature — no second factor (TOTP, hardware token, PIN) is required or checked
  - Electronic signature endpoint authenticates the signing action by verifying only the Bearer JWT token already in the session — no additional credential challenge is presented at signing time
- **Evidence needed:** Confirm the signing endpoint requires only one credential; trace the authentication call graph to confirm only one factor is verified before the signature is persisted.
- **False-positive traps:**
  - If the user executed a full two-factor login during the same continuous controlled-access session (§11.200(a)(1)(i)), subsequent signings may use only one component — assess whether the session context is continuous and controlled
  - Biometric signatures (§11.200(b)) are exempt from the two-component requirement — confirm the signing mechanism is not biometric-based

### `P11-11.200-002` — Electronic signature components not unique to owner — shared credentials allowed

> Be used only by their genuine owners; and (3) Be administered and executed to ensure that attempted use of an individual's electronic signature by anyone other than its genuine owner requires collaboration of two or more individuals.

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - Shared service account (e.g., lab-admin, system-user) is used to sign records — the account's credentials are known to multiple individuals, defeating uniqueness
  - No enforcement in code preventing a user from sharing their password: no concurrent session detection, no device binding, and no anomaly detection for simultaneous logins from different IPs signing records
- **Evidence needed:** Confirm records are signed under a shared account by inspecting the signer_id of signature rows; confirm the account credentials are accessible to more than one individual via shared secrets.
- **False-positive traps:**
  - Service accounts for automated system-to-system integrations that do not constitute 'electronic signatures' under Part 11 are not implicated — confirm the signature use case
  - MFA with a hardware token bound to one person mitigates shared-password risk even if the password itself is shared — assess the full authentication chain

## 11.300

### `P11-11.300-001` — No password uniqueness enforcement — duplicate credential pairs allowed

> Maintaining the uniqueness of each combined identification code and password, such that no two individuals have the same combination of identification code and password.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - User registration or password-change service does not check whether the new (username, password) combination already exists for another user — no query against existing credentials to detect duplication (noting that hashed passwords require a different uniqueness strategy, e.g., unique username alone with individual password hashes)
  - No UNIQUE constraint on the username column in database migration scripts, allowing two users to share the same identification code
- **Evidence needed:** Confirm username uniqueness is not enforced at the database level (no UNIQUE constraint) and not enforced in the application service layer; confirm two users can register with the same username.
- **False-positive traps:**
  - When passwords are properly hashed, enforcing identical (username+password) combinations at the application layer is impractical — the uniqueness requirement is effectively satisfied by enforcing unique usernames alone; confirm username uniqueness rather than searching for duplicate hashed passwords
  - Email-as-username with a UNIQUE constraint on the email column satisfies this requirement even if not labeled 'username'

### `P11-11.300-002` — No password aging or periodic credential review

> Ensuring that identification code and password issuances are periodically checked, recalled, or revised (e.g., to cover such events as password aging).

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - No @Scheduled job or password expiry logic in the codebase — User entity has no password_last_changed or password_expires_at column, and no forced re-authentication or password reset is triggered after any configurable period
  - application.properties has no security.password.max-age or equivalent property, and no password rotation policy is enforced in the UserService
- **Evidence needed:** Confirm User entity lacks password_expires_at or equivalent; confirm no scheduled job or login-time check enforces password rotation; note that NIST 800-63B recommends against mandatory periodic rotation absent breach — assess regulatory context and SOP requirements.
- **False-positive traps:**
  - Modern NIST guidance (SP 800-63B) discourages mandatory periodic password changes unless compromise is suspected — FDA Part 11 does not prescribe a specific rotation interval; absence of rotation may be a deliberate, defensible policy choice
  - Password rotation may be enforced by the IdP (e.g., Active Directory group policy) external to the application — absence in the application code is not a finding if IdP policy is documented

### `P11-11.300-003` — No detection or reporting of unauthorized credential use attempts

> Use of transaction safeguards to prevent unauthorized use of passwords and/or identification codes, and to detect and report in an immediate and urgent manner any attempts at their unauthorized use to the system security unit, and, as appropriate, to organizational management.

- **Confidence:** high  **GAMP 5:** category 5
- **Code patterns:**
  - Authentication failure handler logs the failed attempt to a general application log but does not trigger an alert, increment a lockout counter, or publish a security event to a monitoring system — no call to securityEventPublisher.publishLoginFailure() or equivalent
  - No account lockout logic: failed login attempts are not counted in the User entity or a distributed cache; brute-force attacks will not trigger a lockout or alert
- **Evidence needed:** Confirm authentication failure handler has no lockout counter increment and no alert publication; confirm User entity has no failed_attempts or locked_until field; confirm monitoring system receives no security event on repeated failures.
- **False-positive traps:**
  - Rate limiting at an API gateway or WAF may prevent brute force even without application-level lockout — assess the full defense-in-depth stack before raising as a standalone finding
  - Log aggregation tools (Splunk, ELK) may alert on repeated authentication failures via log pattern matching external to the application — confirm whether this constitutes 'immediate and urgent' reporting as required

### `P11-11.300-004` — No loss management — compromised tokens not electronically deauthorized

> Following loss management procedures to electronically deauthorize lost, stolen, missing, or otherwise potentially compromised tokens, cards, and other devices that bear or generate identification code or password information, and to issue temporary or permanent replacements using suitable, rigorous controls.

- **Confidence:** medium  **GAMP 5:** category 5
- **Code patterns:**
  - JWT-based authentication with no token revocation mechanism — no blacklist table, no Redis revocation set, and token expiry is the only mechanism to invalidate a compromised token; there is no admin endpoint to revoke a specific user's tokens immediately
  - No UserService.revokeAllTokens(userId) method exists and no token_revoked_at or force_logout_at field on the User entity that would invalidate outstanding JWTs
- **Evidence needed:** Confirm there is no token revocation endpoint; confirm a captured JWT continues to authenticate successfully after the account is reported compromised (until natural expiry); confirm token TTL is long enough to present a material risk window.
- **False-positive traps:**
  - Short-lived JWTs (e.g., 5-minute access tokens) with opaque refresh tokens that are revocable substantially mitigate this — assess whether the access token TTL is short enough to limit the exposure window
  - Stateful sessions (server-side session store) can be invalidated immediately regardless of token format — this pattern applies only to stateless JWT architectures
