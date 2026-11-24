# Skill and instruction design gate

Apply this gate whenever creating or revising a skill, repository instruction, or workflow. It is a development reference, not context that every target task must load.

## Required design reference

The owner selected OpenAI's [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) as a design input. Its relevant guidance is to narrow descriptions to real triggers, disclose supporting material only when relevant, replace rigid recipes with useful guidance, and make repository reading conditional. Clear completion boundaries also matter. The article discusses Astra; validate the resulting instructions on our intended models instead of assuming the same effects for Luna, Terra, Sol, or Claude.

## Before creating or retaining a skill

A reusable method is not automatically a skill. Require a recurring need in the intended target projects and evidence that specialised guidance improves the agent's native behaviour enough to justify its discovery, context and maintenance cost. Apply this test to every existing and proposed APS/ACS skill, including previously planned candidates. Frequency must be grounded in actual recurring work or a concrete, plausible usage pattern to test; an occasional task across many projects is not sufficient reason to expose its instructions in every target.

Process discipline is a legitimate benefit even when the model already knows how to perform the underlying task. A skill may keep a recurring task focused, preserve consequential steps, prevent unnecessary detail or detours, and establish a reliable stopping point. Compare this benefit with a short workflow rule or on-demand guide; do not impose steps that do not contribute to the outcome.

Choose the smallest adequate form:

| Need | Form |
| --- | --- |
| Deterministic operation | Script or CLI with focused tests |
| Infrequent setup, migration or one-off procedure | On-demand guide or template, outside skill discovery |
| Binding routine across tasks | Short workflow rule |
| Recurring specialised task with a demonstrated gap | Skill candidate, subject to evaluation |

Start with native capabilities. Before writing a candidate, record representative recurring cases, the observed gap, and why a lighter form does not suffice. A workflow phase, a useful upstream technique, or manual invocation alone is not justification. If recurrence or incremental value is unproven, defer the package or retain the method as an on-demand reference. Reassess existing skills using the same gate; remove unnecessary discovery entries rather than keep them because they already exist.

## Small contract

Describe the user problem, trigger and exclusions, necessary inputs, useful result, and completion boundary. Start with the smallest adequate form identified above.

Keep the description short enough to distinguish the trigger. Keep `SKILL.md` focused; link coding-specific or host-specific detail with explicit read conditions. Avoid duplicating core policy, instructions the agent already follows, or the same method across APS and ACS. Record the source, adopted ideas, changes, and required notices when deriving material.

## Acceptance evidence

| Question | Minimum useful evidence |
| --- | --- |
| Does it warrant a skill? | Recurring usage cases and a concrete gap versus native behaviour or a lighter form. |
| Is it discoverable? | Package/metadata validation in the intended host. |
| Is it selected appropriately? | Fresh-context natural prompts, explicit invocation, and prompts where it should not activate. Record host traces when available; otherwise mark selection uncertain. |
| Does it behave correctly? | A small set of realistic success, boundary, and failure scenarios with observable results. |
| Does it add value? | Compare equivalent tasks with the lean workflow alone and with the candidate. Record quality, required-step adherence, scope drift, premature or late completion, user interventions, and rework. |
| What does it cost? | Record available context/token/credit and elapsed-time observations, including delegates and retries; label unavailable data. |
| Is it accepted? | Independent review and explicit user acceptance for that candidate, with evidence links and remaining host limitations. |

Use the [small evaluation protocol and result template](evaluation/README.md), not an elaborate evaluation platform. Do not infer a general win from one successful example. A skill's own claim that it ran is weaker than a host activation trace; successful manual use does not establish natural activation.

States are candidate, prototype, pilot, and accepted. A merged source PR, a valid package, or a previous UI pilot is not acceptance of a changed package on another host. Retest the changed behaviour rather than every historical scenario by default.

## Context cost to account for

Where a host exposes skill names and descriptions for discovery, even an unused installed skill can add metadata context. Invoking it loads instructions; references and tool outputs add more when read. Independent agent sessions also consume their own brief and relevant context. Exact loading, caching, and billing depend on the host and must be measured or marked unknown.

Consequently, selective installation, specific triggers, conditional references, short outputs, and sufficient downstream artifacts are part of the design. Do not strip useful Luna reasoning or necessary review merely to make one prompt smaller. Keep an addition only when its observed contribution justifies its total task cost.
