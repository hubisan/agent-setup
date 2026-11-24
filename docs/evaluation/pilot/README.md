# ACS pilot (#5)

Status: prepared, no authenticated host results. The current default remains balanced as a proposal, not a validated winner. No change to role mappings is justified by static fixtures alone.

Use the [evaluation protocol](../README.md), [fixed tasks](cases.md), and [result template](../result-template.md). Use a private disposable Linux project for every run. Do not install into a working project, add skills, connect additional services, or invoke models automatically from a benchmark script. Compare the same task and starting fixture; keep costs proportionate.

## 1. First verify the host

On the actual machine, run `codex --version` and/or `claude --version`, then follow [host verification](../../../providers/README.md) for the selected client. Inspect active model/effort, configuration sources, installed agents/skills, permission boundaries, overrides and capability inventory. Record the actual installed version. Use native trust and approval flows. Do not disable sandboxing or managed restrictions.

Choose the coordinator explicitly and keep it fixed across compared runs. The balanced plan's recommendation is an initial choice, not forced configuration. Use the existing catalogue and capability check, including the approved Luna fallback only when evidenced. If a required model or capability is unavailable, record the gap and stop that comparison; do not substitute another family or silently raise effort.

## 2. Prepare one disposable target at a time

Start in a clean checkout of this repository. Pin its commit and retain the same revision throughout a comparison. Example for Codex; set HOST to claude-code for Claude Code. Change the case and condition labels and create a **new** target for every run.

```bash
SOURCE="$(pwd -P)"
git -C "$SOURCE" rev-parse HEAD
HOST=codex
PROFILE=balanced
GUARD=none
TELEMETRY=none
CASE=simple
RUNS="$(mktemp -d "$HOME/acs-pilot.XXXXXX")"
TARGET="$RUNS/$HOST-$PROFILE-$CASE"
cp -R "$SOURCE/docs/evaluation/pilot/fixture" "$TARGET"
git -C "$TARGET" init --template= -q
python3 "$SOURCE/scripts/install.py" preview --target "$TARGET" \
  --modules acs --providers "$HOST" --profile "$PROFILE" \
  --guard-providers "$GUARD" --telemetry-providers "$TELEMETRY"
```

Inspect the preview, then use the identical options with `apply --approve APPROVAL_FROM_PREVIEW`. If using a verified capability inventory, include the corresponding flag in **both** commands, as in [adoption](../../adoption.md). Never auto-approve a real target from a script. Verify `status` and the generated profile plan, and commit the fixture plus reviewed installed configuration in this disposable Git repository using the normal local Git workflow. Save that run's start revision with `START_REV=$(git -C "$TARGET" rev-parse HEAD)`. Do not push it, copy credentials, or commit local logs or settings from another project.

Open the selected host from the target (`cd "$TARGET"` and launch `codex` or `claude` with the verified coordinator selection), follow its normal trust/permission prompts, and use a fresh session for the exact task from [cases](cases.md). Keep unrelated plugins, tools and instructions out of the comparison as far as the host allows; document any inherited configuration. Check actual instruction and delegate discovery independently of the model's self-report.

## 3. Run the smallest useful comparisons

| Stage | Condition | Tasks |
| --- | --- | --- |
| A: smoke | Balanced, guard/telemetry off | S on each available host |
| B: workflow | Same as A | N and C on each available host |
| C: hook impact | Same balanced setup, guard and telemetry on for that host | Repeat N with identical inputs and coordinator; verify normal output is silent |
| D: routing | Economy instead of balanced; hooks off in both | Repeat task C if the earlier runs justify further spending |

For C, set both GUARD and TELEMETRY to HOST when preparing its new target. For D use the existing economy profile, not ad hoc routing. Keep the baseline/variant within the same host; credits and token accounting are not interchangeable across providers. Do not run a full combinatorial matrix. Start with A, stop on a blocker, and review evidence before expanding. If cost measurements are too noisy or missing, report an inconclusive comparison rather than invent savings. A single paired run is exploratory.

Record class, actual steps, interruptions, context and unnecessary delegation; verify the independent-review and one-substantial-correction requirements. A separate controlled probe is described in [cases](cases.md). Review can use a suitably cheap independent delegate; the implementing agent's self-check cannot substitute for it. Do not spawn a delegate just to perform every workflow phase.

## 4. Check and record

From a trusted shell outside the coding session, review the candidate diff, then run:

```bash
git -C "$TARGET" diff "$START_REV"
git -C "$TARGET" status --short
python3 "$SOURCE/docs/evaluation/pilot/check.py" "$CASE" "$TARGET"
```

The check executes the candidate's local report.py for N and C; use it only in the reviewed disposable fixture. It covers functional behaviour, not code quality, test quality, documentation, routing, independent review or process acceptance. Review new/untracked files as well as tracked diffs; keep baseline and final commit identities if the agent commits. Run the candidate's own tests and inspect their coverage. Check for changes outside task scope and managed setup files.

Use one short [result record](../result-template.md) per comparison. Capture available native token/cache/credit metrics, total elapsed wall time including delegates/review/corrections, actual requested and effective model/effort, source of evidence, and unobserved values. Do not ask the model to reconstruct its token usage. Record coordinator and delegate costs, but do not add overlapping totals. Keep raw session data private.

## 5. Hook verification (remaining #16 runtime gates)

Use the [hook contract](../../hooks.md). Record native discovery/trust, actual events, available fields, denial versus observation, overrides and missing usage. Inspect local JSONL records outside the model context. Never paste the raw log into a model prompt. Check that ordinary events add neither model messages nor repeated visible warnings. Compare N with hooks disabled/enabled and record wall time and available context/usage counters. The stored hook_processing_ms excludes interpreter startup and final storage work; it is not end-to-end hook latency. If a native hook timing metric is not exposed, time the installed command in an isolated local synthetic probe and identify that as process overhead, not live task cost.

Do not deliberately send a prohibited high-cost model request to prove denial. If the installed host supports a safe explicit spawn override, a separately approved harmless within-cap but wrong-role effort (e.g. lower effort for a named role) can test the actual denial boundary without exceeding the model cap if the hook fails. Inspect the actual supported schema and precedence first. Use only the synthetic fixture and normal permissions; otherwise mark denial unrun. Do not test Astra or Sol above medium. Keep escalation approval separate from observed model fields.

If a client omits token counts, record unknown and use its supported native usage UI where available. Do not enable exporters, extra inference, or a monitoring stack as part of this pilot. Report attempt/agent correlation gaps; do not aggregate overlapping counters.

## 6. Publish the smallest useful result

Share sanitized results and evidence locations in [#5](https://github.com/hubisan/agent-setup/issues/5), and link findings to [#2](https://github.com/hubisan/agent-setup/issues/2), [#3](https://github.com/hubisan/agent-setup/issues/3), [#4](https://github.com/hubisan/agent-setup/issues/4) and [#16](https://github.com/hubisan/agent-setup/issues/16) where they satisfy a gate. Do not mark unknown or unrun criteria passed. Recommend profile mapping changes only after comparable acceptance and cost evidence, and obtain owner approval. Retain balanced and hooks off as existing defaults until then. No candidate skill adoption or packaged release is included.

Remove disposable projects and private telemetry only after reviewing and retaining required evidence; follow the [adoption guide](../../adoption.md) for managed removal. Do not delete any pre-existing target or shared telemetry directory.
