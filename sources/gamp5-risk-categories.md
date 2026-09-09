# GAMP 5 Software Risk Categories (Second Edition, July 2022)

GAMP 5 classifies computerized systems into risk categories. Generator subagents
must assign exactly one category per rubric row.

## Category 1 — Infrastructure Software
Operating systems, databases (as services), middleware, antivirus, monitoring
tools. Not directly business-logic-bearing. Rarely a Part 11 finding sits here.

## Category 3 — Non-Configured Products
Commercial off-the-shelf software used out-of-the-box, no business-process
configuration beyond default options. Example: a stock instrument driver.

## Category 4 — Configured Products
Commercial products where business logic is implemented through configuration
(not custom code). Example: a LIMS instance with workflows configured via the
vendor's admin UI. Most LIMS/ELN/QMS findings sit at 4.

## Category 5 — Custom Applications
Bespoke code written specifically for the user's process. Example: a custom
audit-trail middleware written in-house. Highest validation rigor.

## Assignment heuristic for the rubric

- Finding is about the application's own auth/audit/signature/persistence code
  shipped by the vendor → Category **5**.
- Finding is about how the vendor's configuration surface (admin UI, YAML
  config, role definitions) enforces controls → Category **4**.
- Finding is about underlying database/OS hardening that the vendor does not
  control → Category **1** or **3**; usually out of rubric scope.

Default to **5** when the rubric row is describing code-level patterns in the
vendor's own source tree, which is most rows. Use **4** only when the pattern
is about configuration files / declarative policy.
