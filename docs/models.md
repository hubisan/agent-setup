# Model and profile policy

The purpose is to reduce unnecessary Sol and Opus usage while retaining suitable reasoning and review. This is the policy contract. The profile CLI renders and audits requested configurations; live host compatibility and measured cost comparisons are still open.

## Profiles

| Profile | Intended strategy |
| --- | --- |
| `economy` | Prefer Luna; use Terra for demanding work that exceeds Luna's suitable scope. |
| `balanced` (default) | Use Luna and Terra; reserve Sol for high-risk work that warrants it. |
| `quality` | Prefer Terra and Sol where their contribution is justified; raise reasoning only within the same hard limits. |

Profile names express a trade-off, not evidence of a model's price, quality, or suitability. Initial mappings are implemented as reviewable proposals in [the catalogue](../profiles/catalog.json); they require target-client verification and a pilot. Changing a profile is an explicit configuration choice; do not silently switch profiles to escape a failure.

## Hard constraints

- Preserve Luna's high/max choices; reducing Luna is not the savings objective. Validate what the selected host actually accepts.
- Terra may use at most `high`.
- Sol may use at most `medium` in every profile, role, retry, and escalation. Neither `high` nor a stronger equivalent is permitted through an override or fallback.
- Do not configure Astra as part of this setup.
- Implement and validate Codex and Claude Code profiles in the same first slice. Claude-specific aliases and efforts need their own supported mapping; the model-family names above are not Claude aliases.
- No silent model-family substitution, paid escalation, or incompatible effort coercion. Report an unavailable capability with the concrete alternative and required configuration choice.

The old coding setup documents a narrowly preapproved Luna `max` to `xhigh` fallback for a client that rejects `max`. The adapter implements this exception only when the supplied client capability inventory lists `xhigh` but not `max` for Luna. The generated plan retains both requested and selected effort. If neither is available it fails; it never silently changes model families. It is not permission to weaken other Luna roles or to change families. Record the effective fallback. The old Sol `high` escalation is explicitly superseded.

## Delegation and evidence

Use a subagent when cheaper suitable execution, independence, or useful parallel work can repay its startup/context overhead. A phase name alone is insufficient reason to spawn. Keep the brief to the task, acceptance criteria, relevant files, and necessary decisions. Record the model actually requested rather than merely saying “cheap agent”.

| Evidence state | What is established |
| --- | --- |
| `configured` | A configuration names a model and effort. |
| `spawn-confirmed` | The selected role started; effective model/effort may still be unknown. |
| `runtime-verified` | Independent host metadata identifies the effective model and effort, with a retrievable evidence location. |

A model's self-report, token count, or configuration file alone is not runtime verification. If the host exposes only part of the information, report that part and leave the rest unknown. Profile validation must consider inheritance, per-spawn options, environment or client overrides, and reviewer routing; a compliant default with a violating override is not compliant.

Measure total task cost where available: coordinator and delegates, repeated context, reasoning/output, retries, and review. Compare equivalent completion quality and risk, not only the cheapest individual call. Record subscription/credit observations separately from API prices; do not present one as the other. No numeric savings are claimed by this implementation.

## Profile commands

Requires Python 3.11+; no external packages. Run from this repository:

```bash
python3 scripts/profile.py plan --provider codex
python3 scripts/profile.py plan --provider claude-code --profile economy
python3 scripts/profile.py render --provider codex --profile balanced --output /tmp/acs-codex-balanced
python3 scripts/profile.py render --provider claude-code --profile quality --output /tmp/acs-claude-quality
```

Omit `--profile` for balanced. A plan includes the coordinator recommendation and nine delegate roles. The coordinator remains host-selected. Render writes a **new** staging directory, including `profile-plan.json` and either `.codex/agents/acs-*.toml` or `.claude/agents/acs-*.md`. Existing output is rejected; no project files or client settings are changed. Integration and safe switching in existing targets belong to #3. No host is launched and no credentials are requested.

The catalogue is the single role-to-model/effort mapping. Codex uses GPT-6 Luna, GPT-6.1 Terra and GPT-6.2 Sol. Claude Code uses pinned Sonnet 5.5 and Opus 5.5 IDs. Economy and balanced use Sonnet for regular work, including Sonnet medium and high respectively for review, and Sonnet high for complex implementation. Opus low is reserved for user-approved escalation in these two profiles; quality uses Opus medium for selected demanding roles and escalation. Sonnet is capped at high and Opus at medium. Codex escalation uses Sol medium. All escalation requires user approval. Haiku and Fable are not selected. Actual account availability and comparative quality and cost remain to be validated. Role instructions are narrow, not an automatic chain.

## Check target capability and overrides

Follow [host verification](../providers/README.md) before using the generated files. Prepare a sanitized capability inventory with actual host version and supported model/effort pairs, for example (synthetic, not client evidence):

```json
{
  "provider": "codex",
  "version": "fixture",
  "models": {
    "gpt-6-luna": ["high", "xhigh"],
    "gpt-6.1-terra": ["high"],
    "gpt-6.2-sol": ["medium"]
  }
}
```

Pass `--capabilities path/to/capabilities.json` to plan or render to validate the requested combinations and resolve the one approved Luna fallback. Missing models or unsupported combinations fail. Without this inventory the plan is documentation-based only.

To audit, inspect the actual loaded host configuration and record the fully resolved model and effort for every role (including coordinator), with source. Also record each relevant override you found, even if another layer shadows it. Use the following shape, **expanding roles to all ten entries** and replacing the example values with observations, not copying the generated plan as evidence:

```json
{
  "provider": "codex",
  "version": "fixture",
  "sources_reviewed": ["project config and agent files", "user and managed settings", "launch and spawn parameters"],
  "roles": {
    "coordinator": {"model": "gpt-6-luna", "effort": "high", "source": "explicit session selection"}
  },
  "overrides": [],
  "fallbacks": []
}
```

Every override row uses `role`, `model`, `effort`, `source`. If the host uses an alias or inheritance, resolve it to a concrete model ID and effort before recording it; an unresolved value is not a pass. List configured fallback chains in `fallbacks`; this audit rejects nonempty chains. An empty list means you checked and found none, not that the CLI discovered them.

```bash
python3 scripts/profile.py check --provider codex --profile balanced \
  --capabilities capabilities.json --observed observed.json
```

The audit rejects mismatches (even within the general effort cap), unknown roles/models, forbidden effort, incomplete role sets, mismatching provider/version, and selected routing environment variables. It checks the environment of this process, not that of an already running host. Run it in the intended launch environment and inspect settings/overrides separately. A successful audit only means the supplied configuration matches the profile. It is **not** a runtime enforcement mechanism or a proof of exhaustive discovery. A different host-selected coordinator within policy is possible, but does not pass an exact-profile audit. Choose it explicitly and record the departure instead of silently changing the profile.

For actual delegate invocation, use the named ACS roles and no conflicting overrides. Verify effective model and effort from host metadata, including resumed agents and automatic provider routing. Stop on a mismatch or unavailable required evidence; do not silently escalate. Record evidence and total task cost using [the evaluation protocol](evaluation/README.md).
