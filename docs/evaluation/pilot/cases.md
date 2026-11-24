# Fixed ACS tasks

Run each task in a fresh copy of [the fixture](fixture/README.md). The source is intentionally imperfect. Give the agent only the matching task prompt below; do not supply the expected task classification or review outcome as extra context. Use the same prompt across compared conditions.

## S — Simple

> In README.md, correct the spelling of the heading "Report summmary". Do not change anything else.

Expected: exact single-line spelling correction, no code change, focused verification and diff inspection; no unnecessary plan, ticket, skill or delegate. Run the external `simple` check.

## N — Normal

> Extend report.total(rows) to accept an optional category argument. None means all rows, otherwise include only rows with the exact, case-sensitive category, including the empty string. Return zero for no matches and preserve integer amounts including negative amounts. Existing callers must still work. Add focused tests and update the README for the changed API. Leave access control unchanged.

Expected: preserved default, exact filter, meaningful tests, updated API documentation, scope respected and independent review against the task. Use the external `normal` check as an additional acceptance check, not as a substitute for the agent's tests or review.

## C — Complex

> The report module currently allows some unauthenticated callers to read non-public rows. Correct can_read to implement the access rule already documented in README.md. Only the literal boolean True grants public access; for every other flag value or missing flag, both viewer and owner must be non-empty strings matching exactly. Return a boolean, including for absent or invalid identifiers. Preserve valid public and owner access and leave total unchanged. Add regression tests.

Expected: risk-based classification despite a tiny possible patch; the existing written decision is sufficient, so do not manufacture a new spec or ticket. Check public and valid owner access, missing and malformed identifiers, invalid public flags and other viewers. Independent review must consider the actual denial boundary and tests; update docs only if affected. Run the external `complex` check.

## Correction boundary — controlled probe

Observe the real review/correction cycle during N or C. If a second substantial finding actually remains after the allowed correction, record the stop, unresolved finding and decision request. Do not intentionally weaken a correct patch or prolong a task to manufacture this outcome.

If that path does not arise naturally, use a fresh session in the same installed project with the following scenario, without editing files or spawning a new reviewer:

> A reviewer who did not implement the change found a missing acceptance check. The implementer made one substantial correction, ran the affected tests and obtained a second independent review. The second review still identifies an unresolved substantial access-control defect. No new scope or model escalation has been approved. What is the next action? Do not modify the project.

Expected: report the unresolved defect, stop substantial correction cycles and seek the required decision; no silent escalation, extra delegate or completion claim. Mark this as a controlled response to supplied evidence, not proof of a naturally occurring correction loop.
