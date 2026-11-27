# ACS scope and candidate catalogue

ACS adds coding-specific methods to the shared APS foundation. The [adaptive workflow](WORKFLOW.md) defines required outcomes. Skills are optional methods, not mandatory workflow stages. Each candidate must pass the [design gate](../../docs/skill-design.md). [#12](https://github.com/hubisan/agent-setup/issues/12) tracks decisions and acceptance evidence.

## ACS target catalogue (owner direction)

| Candidate | Boundary |
| --- | --- |
| `acs-codebase-design` | Improve software architecture, module boundaries, interfaces, testability and maintainability. |
| `acs-diagnosing-bugs` | Reproduce defects, test hypotheses, isolate causes and verify fixes. |
| `acs-tdd` | Use behaviour-first Red → Green → Refactor for clear, testable behaviour. Use mutation checks only for justified risks. |

## Proposed candidates — owner decision pending

| Candidate | Boundary |
| --- | --- |
| `acs-spec` | Convert an agreed solution into a technical specification when the existing artifacts are insufficient. |
| `acs-tickets` | Convert an agreed specification into actionable, scoped implementation tickets. |
| `acs-prototype` | Explore a design question or reduce uncertainty with a focused prototype. |

## Open decisions

| Candidate | Boundary |
| --- | --- |
| `acs-review` | Compare independent review of requirements and standards with native review support. |
| `acs-triage` | Assess recurring value for intake of code issues, bugs and pull requests. |

## Boundaries

- `acs-tdd`: use test-first for clear, reliably testable behaviour. Prefer visual, exploratory or integration checks when test-first adds little value. Mutation checks are optional for critical logic, security or justified doubts about test strength. See [#12](https://github.com/hubisan/agent-setup/issues/12) for the full testing contract.
- `acs-review`: independent review remains required for normal and complex behaviour changes regardless of skill packaging.
- Generic implementation and merge-conflict help use native agent capabilities by default. Prefer deterministic scripts and hooks for repeatable checks.
- Reuse [APS](../aps/README.md) for framing, clarification, solution design, planning, documentation and handoff. APS solution design answers how to solve the problem. ACS codebase design answers how to structure the software.

The catalogue records candidates, not accepted packages. No skill or runtime configuration changes follow from this list alone.
