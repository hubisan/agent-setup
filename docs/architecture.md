# Architecture and distribution boundaries

## One source, selective distribution

The monorepo owns reusable methods and their integration. A target project keeps ownership of its domain documents, instructions, source code, and task tracker. APS must work for research, documentation, planning, and other non-software projects without adding a software structure.

| Boundary | Responsibility | Explicit exclusion |
| --- | --- | --- |
| Shared core | Selection, dependency resolution, installation/update state, provider adaptation, evidence format | Personal storage or a universal task system |
| APS | General clarification, analysis, domain modelling, decisions, documentation, status review, and handoff | Mandatory coding tools or Memento paths |
| ACS | Adaptive coding workflow and any justified coding-specific additions | Copies of APS methods; compulsory skill chain |
| Future GTD | Storage-independent GTD practices if later requested | Current implementation or invented skill list |
| Memento, outside this repository | Personal project index, capture/inbox, activity journal, Org/`orgfdb` adapters | Ownership of general APS or reusable GTD behaviour |

ACS depends on the APS shared contract. This does not mean installing every APS skill or waiting for all APS candidates. The first ACS slice uses the shared principles directly; candidate skills are optional until individually accepted. Documentation belongs to APS conceptually and is available to ACS; do not create a second core or ACS documentation skill.

## Source layout

The shared installer is implemented in `scripts/install.py`; `core/manifest.json` declares module dependencies and accepted skills, and `core/APS.md` is the minimal shared contract. The existing foundation contains `modules/aps/README.md`, `modules/acs/WORKFLOW.md`, and task-specific documentation under `docs/`. Profile tooling now lives in `profiles/catalog.json` and `scripts/profile.py`, with the two small native output adapters together in that script. Host capability notes live in `providers/README.md`; evaluation documents live in `docs/evaluation/`. The following broader layout remains a guide; absent paths are not shipped functionality:

| Planned path | Contents |
| --- | --- |
| `core/` | Small shared installation/configuration mechanisms and templates |
| `modules/aps/skills/<aps-name>/` | Canonical accepted APS packages; candidate development stays scoped to its issue/branch |
| `modules/acs/skills/<acs-name>/` | Optional accepted coding packages, only after evidence of a gap |
| `profiles/` | Declarative profile policy and provider role mappings |
| `providers/` | Host capability notes; split adapter code by host only when it grows |
| `scripts/`, `tests/` | Only the implementation and meaningful checks needed by those features |

Do not expose all source candidates to automatic discovery. The manifest declares accepted skills and dependencies; the installer records requested and effective selection. The installer must explain required additions or reject an invalid selection; it must not silently install the whole catalogue.

## Target ownership and updates

The [adoption guide](adoption.md) defines the preview/approval, idempotence, version and ownership workflow. Implementation choices: copy regular files into project-local host paths; keep a state manifest and a private recoverable transaction journal. Preserve existing instructions, Org/Markdown organisation, unrelated skills, and local modifications. Detect conflicting edits and show a concrete resolution rather than overwrite. Define update, removal, and recovery together; test repeated installation and a locally edited target.

Canonical skill content has one source. Provider-specific output is derived rather than maintained as independent method copies. Documented discovery paths are used; copies avoid writable cross-project symlink targets. Actual discovery and configuration precedence remain host-pilot checks.

## Provider capability boundary

Codex and Claude Code receive the same workflow semantics with provider-specific configuration. Do not translate Luna/Terra/Sol names directly into Claude configuration. ChatGPT needs an explicit supported distribution/install/update path; a file in a GitHub repository alone does not establish an installed ChatGPT skill or model-routing capability.

The active session's model remains host-controlled unless the host exposes a supported selector. Separate requested configuration, successful spawn, and independently observed runtime evidence. Do not add speculative per-provider infrastructure before the first usable slice.

See the [profile contract](models.md), [candidate catalogue](../modules/aps/README.md), and [roadmap](roadmap.md).
