# Model and profile policy

The purpose is to reduce unnecessary Sol usage while retaining suitable reasoning and review. This is a policy contract; executable mappings and measured cost comparisons are not implemented yet.

## Profiles

| Profile | Intended strategy |
| --- | --- |
| `economy` | Prefer Luna; use Terra for demanding work that exceeds Luna's suitable scope. |
| `balanced` (default) | Use Luna and Terra; reserve Sol for high-risk work that warrants it. |
| `quality` | Prefer Terra and Sol where their contribution is justified; raise reasoning only within the same hard limits. |

Profile names express a trade-off, not evidence of a model's price, quality, or suitability. Exact coordinator, implementer, and reviewer mappings require provider verification and a pilot. Changing a profile is an explicit configuration choice; do not silently switch profiles to escape a failure.

## Hard constraints

- Preserve Luna's high/max choices; reducing Luna is not the savings objective. Validate what the selected host actually accepts.
- Terra may use at most `high`.
- Sol may use at most `medium` in every profile, role, retry, and escalation. Neither `high` nor a stronger equivalent is permitted through an override or fallback.
- Do not configure Astra as part of this setup.
- Implement and validate Codex and Claude Code profiles in the same first slice. Claude-specific aliases and efforts need their own supported mapping; the model-family names above are not Claude aliases.
- No silent model-family substitution, paid escalation, or incompatible effort coercion. Report an unavailable capability with the concrete alternative and required configuration choice.

The old coding setup documents a narrowly preapproved Luna `max` to `xhigh` fallback for a client that rejects `max`. Evaluate this existing compatibility exception for the new adapter; preserve its intent if supported and tested. It is not permission to weaken other Luna roles or to change families. Record the effective fallback. The old Sol `high` escalation is explicitly superseded.

## Delegation and evidence

Use a subagent when cheaper suitable execution, independence, or useful parallel work can repay its startup/context overhead. A phase name alone is insufficient reason to spawn. Keep the brief to the task, acceptance criteria, relevant files, and necessary decisions. Record the model actually requested rather than merely saying “cheap agent”.

| Evidence state | What is established |
| --- | --- |
| `configured` | A configuration names a model and effort. |
| `spawn-confirmed` | The selected role started; effective model/effort may still be unknown. |
| `runtime-verified` | Independent host metadata identifies the effective model and effort, with a retrievable evidence location. |

A model's self-report, token count, or configuration file alone is not runtime verification. If the host exposes only part of the information, report that part and leave the rest unknown. Profile validation must consider inheritance, per-spawn options, environment or client overrides, and reviewer routing; a compliant default with a violating override is not compliant.

Measure total task cost where available: coordinator and delegates, repeated context, reasoning/output, retries, and review. Compare equivalent completion quality and risk, not only the cheapest individual call. Record subscription/credit observations separately from API prices; do not present one as the other. No numeric savings are claimed by this foundation.
