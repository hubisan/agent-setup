# Agent instructions

Use the active issue and its acceptance criteria as the work contract. Reuse settled decisions and downstream artifacts: ticket, spec, then conversation. Read the README for orientation on first entry; do not load every linked document.

## Read when

- Implementing, testing, reviewing, or delegating coding work: [ACS workflow](modules/acs/WORKFLOW.md).
- Changing models, profiles, or delegation settings: [model policy](docs/models.md).
- Changing module boundaries, installation, or provider integration: [architecture](docs/architecture.md). To adopt or update a target: [adoption guide](docs/adoption.md).
- Creating or changing skills or agent instructions: [design gate](docs/skill-design.md); use the [APS catalogue](modules/aps/README.md) to avoid overlapping skills.
- Resolving scope or conflicting historical proposals: [decisions](docs/decisions.md). Inspect [sources](docs/sources.md) only for the relevant provenance.
- Selecting the next task: [roadmap](docs/roadmap.md); issue bodies own current scope and dependencies.

## Working agreements

- Keep instructions and repository documentation in English. Use the user's language in conversation and preserve existing target-project language and Org/Markdown conventions.
- Write issues and documentation by audience: use `simple-english` for people and `writing-for-agents` for agents when available. In mixed documents, put the human summary and next action first, then the agent contract. Keep shared facts in one source. Use the combined `aps-writing-docs` after acceptance (#8).
- Resolve routine reversible implementation choices within the authorised task. Record material agent-selected choices separately from user decisions. Complete the active scope; do not automatically start another roadmap issue.
- Keep context targeted. Answer directly and briefly; report results, blockers, essential evidence and the next action when needed. Link details instead of repeating them. Keep enough context and explanation for the intended reader to understand and act. Expand on request or when clarity or correctness requires it. Apply the same brevity to documents. Do not bulk-load skill directories or historical decisions.
- Preserve user-owned target files and instructions. Do not modify the two source repositories as part of work here.
- Use a scoped branch and PR for subsequent work. Commit messages use Conventional Commits; link the owning issue. Do not rewrite shared history. Repository creation is the authorised bootstrap exception.
- Check documentation impact with every change. State actual verification and unrun checks; configuration is not proof of runtime behaviour.

Run `python3 -m unittest discover -s tests -v` for the full executable check. For documentation-only changes, inspect the diff, relative links and decision consistency. When evaluating a profile or skill, use [the evaluation protocol](docs/evaluation/README.md).
