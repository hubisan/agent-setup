# Optional hooks: implementation and evidence

Issue [#16](https://github.com/hubisan/agent-setup/issues/16). This branch introduces the shared command runtime and host registration builder. Do not manually add these registrations to an existing project until installer ownership and recovery are integrated.

## Host contracts (documentation, not live evidence)

Checked 2026-11-24. Neither Linux coding client is installed in the implementation environment. The current reference versions and actual client verification steps remain in [provider verification](../providers/README.md).

| Host / event | Intended use | Limits |
| --- | --- | --- |
| Codex SessionStart | Inspect reported model | Effort and effective routing remain unknown |
| Codex PreToolUse, spawn_agent / Agent | Inspect explicit model, reasoning_effort and agent_type; deny confirmed prohibited requests | Local tool coverage varies; not all spawn paths or fields are observable |
| Codex PreModelRequest / PostModelRequest | Observe individual attempts, status and available token usage | No denial boundary; retries may share turn IDs; not proof of effective effort |
| Both SubagentStart / Stop, SessionEnd | Lifecycle correlation | Spawn/resume is not model verification; main and child totals must not be added twice |
| Claude SessionStart / PreToolUse (Agent) | Inspect explicit requests (model, effort, subagent_type) | Alias resolution, inherited settings and overrides may be hidden |
| Claude PreModelSwitch | Explicit session switch boundary, to_model is canonical | No effort field, timeout can itself prevent a switch; not used solely for telemetry |
| Claude PostModelSwitch / ConfigChange | Observe session changes and settings-change category | One-turn fallback chains may be invisible; ConfigChange does not reveal changed values |

Sources: [Codex hooks](https://developers.openai.com/codex/hooks), [Codex spawn tool definition](https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/multi_agents_spec.rs), [Claude hooks](https://code.claude.com/docs/en/hooks), [Claude settings](https://code.claude.com/docs/en/settings), [Claude subagents](https://code.claude.com/docs/en/sub-agents), [Claude monitoring](https://code.claude.com/docs/en/monitoring-usage).

Both hosts use command hooks with JSON stdin; deny uses hookSpecificOutput.permissionDecision = deny only for PreToolUse or PreModelSwitch. No allow decision, permission bypass, settings rewriting, additional model prompt, or Stop loop. Unknown input or storage failures are not compliance. Host timeout and fail-closed policies are separate from our decision. Review Codex project trust and exact hook hashes via /hooks; Claude project trust and managed/user/local settings can restrict or override hooks. Native configuration is not proof of discovery.

## Runtime contract

The installer must generate policy snapshots from the existing profile plan and model catalogue, not maintain another model table. The guard evaluates observable explicit requests only. Startup and model-attempt events are diagnostic. Escalation approval is not visible in these payloads; a named escalation role does not establish approval. Use the documented approval workflow. Unresolved aliases, missing effort, hidden settings and unobserved fallbacks remain unknown. No automatic switching.

Telemetry is opt-in and independent of the guard. Each event is a schema-1 JSON line at ~/.local/state/agent-setup-hooks/<project hash>/events-YYYY-MM-DD.jsonl. Private application directories (0700), files (0600), no symlinks, no transcript reads, no network. Session, agent, turn and tool-call IDs are hashed. Known role/model/effort and fixed event/status/source codes only. The configured capability version is configuration, not an observed version. Unknown values are null. Hook processing time is not request duration. Files are bounded to 5 MiB per UTC day; storage failure is reported and cannot turn an unknown request into a denial. Delete old daily files (recommended 30 days) or the project directory when no longer needed. Export only reviewed, sanitized records explicitly.

Usage fields are candidate Codex attempt counters; the exact target schema still needs a live check. Only PostModelRequest contributes attempt-scoped usage, never PreModelRequest or lifecycle events. Do not sum retries, repeated notifications, session totals and subagent totals indiscriminately; no complete cost aggregate is claimed until the pilot validates correlation and deduplication. Claude hook payloads do not establish per-request token totals. Compare native usage displays or explicitly enabled OpenTelemetry metrics/API events, with a local destination and prompt/body capture disabled. No OTEL setup or automatic upload is included. API costs are not subscription credits.

## Remaining integration and verification

- Safe merge, ownership, preview/approval, uninstall and recovery in existing settings.
- Fixture verification of native registration, nested cwd, worktree, stale previews and interrupted application.
- Actual versions, hook support, timeout/trust behaviour, payloads, usage correlation and measured overhead on both hosts; carry live evidence into #5.
- Independent review and owner approval before release.

The initial unit tests use synthetic payloads, not actual host sessions.
