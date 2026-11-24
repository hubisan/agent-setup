# Adopt Agent Setup in a project

Use this guide on demand. Adoption is an infrequent task, not an automatically discovered skill. No `aps-adopt` package is needed.

## 1. Inspect the target

Choose an existing project directory outside the Agent Setup source checkout. Check its Git status (if applicable), current instructions, task tracker, language and Org/Markdown organisation. Read `AGENTS.md`, `CLAUDE.md`, root overrides and the relevant host configuration. Keep project authority and local decisions; reconcile contradictory guidance before adoption. Back up or commit existing work.

Use Linux with Python 3.11+ and a local checkout of this repository. No external Python packages are required. Use a real directory, not a symlink, home directory, or system root. Run commands from the source checkout. Do not run concurrent editors or another installer against the same target while applying or recovering.

## 2. Select only what is needed

| Selection | Installs |
| --- | --- |
| APS (default) | A small shared project-workflow block; Claude import if Claude is selected. No coding workflow or delegates. |
| ACS | APS dependency, adaptive coding workflow, model policy, and native files for the selected coding hosts. |
| Skills | Explicitly named accepted packages and their required accepted dependencies. None by default. |
| Providers | Codex and/or Claude Code. Both by default. ChatGPT distribution is separate (#6). |

The [manifest](../core/manifest.json) is the accepted distribution registry. The candidate catalogue is not the registry. No skill is accepted for distribution yet. GTD is reserved, not installable. Choose a [profile](models.md) for ACS; balanced is the default. A profile is a requested configuration, not proof of runtime routing.

## 3. Preview, approve, apply

Example, with a separate target checkout:

```bash
TARGET="$HOME/projects/example"
python3 scripts/install.py preview --target "$TARGET" --modules acs --providers codex,claude-code --profile economy
```

For a non-coding project, replace the selection with `--modules aps`. Omit the profile. Add `--skills name1,name2` only for accepted names; use `--skills none` to remove previously selected packages.

The JSON preview lists requested and effective selection, dependency additions, source revision/content hash, paths, creates/updates/removals, modes, hashes, text diffs, and new directories. For binary content compare the hashes. Read the actual diffs; review any changes to existing instructions against the project's own decisions. Do not paste unsanitized output into a public issue.

After approving that exact preview, run the same selection with `apply` and the preview's `approval` digest:

```bash
python3 scripts/install.py apply --target "$TARGET" --modules acs --providers codex,claude-code --profile economy --approve APPROVAL_FROM_PREVIEW
python3 scripts/install.py status --target "$TARGET"
```

An absent, incorrect or stale approval fails before writing. The installer never runs a host, a skill script, Git commit, or remote operation against the target. A repeated identical installation has no changes.

## Optional coding hooks (#16)

Both hooks are disabled on first installation. Select guard and telemetry independently for ACS and the selected providers, for example:

```bash
python3 scripts/install.py preview --target "$TARGET" --modules acs \
  --guard-providers codex,claude-code --telemetry-providers codex
```

Use the same flags for apply with the approved digest. Use `none` for either feature to remove its registrations. Existing selections are retained on update for hosts that remain selected. Stop the coding clients before changing registrations. Codex requires a Git worktree root and refuses existing inline hooks in `.codex/config.toml`; Claude uses `.claude/settings.json`. Only exact managed groups are owned. Unrelated settings and file permissions are retained, though changed JSON is reformatted. Duplicate keys, unowned runtime references and changed managed groups block installation. Review the normal host trust prompts, never bypass them. See [hook contracts, storage and open verification gates](hooks.md). No live compatibility or complete enforcement is claimed.

## 4. Inspect and verify

Review the resulting Git diff and new files. Only the marked block in an existing instruction file is managed; other bytes and the original mode are retained. A standalone `@AGENTS.md` or `@./AGENTS.md` import outside a fenced example is recognised in an existing `CLAUDE.md`, so it need not be duplicated. A missing Claude import is added as a managed block. Unrelated instructions and files remain yours. A root `AGENTS.override.md` blocks Codex installation instead of silently bypassing it.

The provider-neutral files live under `.agents/`: ACS uses `.agents/WORKFLOW.md` and `.agents/models.md`, while installer state and per-provider profile plans live under `.agents/setup/`. These paths are our organisation convention, not an automatic host discovery standard; the workflow is linked from `AGENTS.md`. Native subagent definitions remain in their provider directories. No extra `.agents/agents/` copy is created.

The target state in `.agents/setup/state.json` records selection, source commit (if available), generated-content SHA-256, and owned blocks/files. Keep it with the installed files in version control; do not delete it to bypass a conflict. State is local configuration, not a runtime record.

| Host | Project locations |
| --- | --- |
| Codex | `AGENTS.md`, `.codex/agents/acs-*.toml`, `.agents/skills/<name>/` |
| Claude Code | `CLAUDE.md` (imports `AGENTS.md`), `.claude/agents/acs-*.md`, `.claude/skills/<name>/` |

Sources: [Codex instructions](https://developers.openai.com/codex/guides/agents-md), [Codex skills](https://developers.openai.com/api/reference/cli), [Codex subagents](https://developers.openai.com/codex/subagents), [Claude Code skills](https://code.claude.com/docs/en/skills), [Claude Code subagents](https://code.claude.com/docs/en/sub-agents), [Claude Code memory/imports](https://code.claude.com/docs/en/memory). These paths are documentation-based. The installer copies regular files; it does not install or traverse symlinks, hard links, special files or Git metadata. No symlink-based update or shared writable skill directories. Local platform tests are not client-discovery proof.

Before starting an actual coding session, complete the outstanding profile checks in #2 and follow the [host verification guide](../providers/README.md). Confirm effective settings, model/effort, discovered instructions, skills and delegates, including nested/global instructions, settings and provider overrides. Start a new session after changes. The generated profile plan is in `.agents/setup/profile-<provider>.json`. To supply a sanitized inventory, pass `--codex-capabilities PATH` or `--claude-capabilities PATH`; only provider, version and models are accepted. These inventories are saved in state for repeatability. Use `none` instead of a path to clear an inventory, and refresh it when the client changes. Do not include credentials. Without an inventory the plan is documentation-based. `status` verifies managed files and blocks, not actual discovery, effective routing, or all unrelated files.

## 5. Update, change selection or remove

Update the source checkout to the intended revision first. Run a new preview (with no selection flags to retain the previous selection), review, then apply the new digest. To switch profile, supply `--profile quality` (or another approved name) in both commands. To reduce the installed set, explicitly choose the new modules/providers/skills. Unchanged owned files are retained, no longer required owned files are removed, and local edits outside managed instruction blocks remain intact.

For removal:

```bash
python3 scripts/install.py preview --target "$TARGET" --remove
python3 scripts/install.py apply --target "$TARGET" --remove --approve APPROVAL_FROM_PREVIEW
```

The installer removes its unchanged files and exact instruction blocks. Existing unrelated `.agents/` contents are preserved. If an earlier unmerged installer draft left `.agent-setup/state.json` or `.agent-setup/pending.json`, use that draft to recover/remove its managed installation before adopting this layout; do not delete its state to bypass the check. It never recursively removes directories; empty directories may remain. If a managed file or block was edited or removed, or an unowned destination or skill-directory file exists, the entire plan fails with the path. Preserve the local work: copy it to a separate file, inspect the previous committed/generated version and reconcile differences. Restore the recorded managed content or move the colliding unowned file to a safe location after reviewing it, then preview again. Do not force an overwrite or delete the state to claim an existing file.

## 6. Recover an interrupted change

During apply, `.agents/setup/pending.json` is a private, mode-0600 recovery journal containing before/after file bytes, including any affected existing instructions. Never commit or share this file. If an application fails after journal creation, stop; do not apply another plan. Run:

```bash
python3 scripts/install.py recover --target "$TARGET"
```

Recovery rolls back changed files and state to their before versions only when all journal paths still match either the recorded before or after version, including permissions. On a third version it reports a conflict before making any recovery writes. Back up the project and journal and reconcile manually; preserve post-interruption edits. If an abrupt process death left a `.agent-setup-write-*` temporary file, inspect and remove only that verified installer temporary file before retrying, especially if linked to its destination. Recovery may leave empty directories. It covers interrupted file operations on a cooperative local filesystem, not hostile concurrent filesystem changes, power-loss durability, or an externally deleted/corrupted journal. Keep a Git commit or backup as the independent recovery path.

## Release boundary

This implementation can be evaluated in disposable fixtures. Do not publish a packaged release before the owner settles the distribution licence and notices. Do not import legacy skills or infer acceptance from passing installer tests. Actual host discovery, model routing and user acceptance remain pilot gates.
