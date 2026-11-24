#!/usr/bin/env python3
"""Render and audit explicit ACS profile requests; never launch a host."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
MODELS = {
    'codex': {'luna': ('gpt-6-luna', ('high', 'xhigh', 'max')),
              'terra': ('gpt-6.1-terra', ('medium', 'high')),
              'sol': ('gpt-6.2-sol', ('low', 'medium'))},
    'claude-code': {'sonnet': ('claude-sonnet-5-5', ('low', 'medium', 'high')),
                    'opus': ('claude-opus-5-5', ('low', 'medium'))},
}
# Conservative: any of these selectors requires clearing it before a clean audit.
ENV_KEYS = {
    'codex': ('CODEX_MODEL', 'CODEX_MODEL_REASONING_EFFORT'),
    'claude-code': ('ANTHROPIC_MODEL', 'CLAUDE_CODE_EFFORT_LEVEL',
                    'CLAUDE_CODE_SUBAGENT_MODEL', 'CLAUDE_CODE_SUBAGENT_EFFORT',
                    'ANTHROPIC_DEFAULT_SONNET_MODEL', 'ANTHROPIC_DEFAULT_OPUS_MODEL'),
}
INSTRUCTIONS = {
    'planner': 'Read the scoped issue and relevant artifacts. Identify risks, owned files, acceptance checks and the smallest useful plan. Do not edit files.',
    'implementer': 'Implement only the assigned scope. Run focused checks, address documentation impact and report changes, tests and blockers.',
    'tester': 'Run the assigned checks. Report actual results, evidence and remaining gaps. Do not expand the scope.',
    'reviewer': 'Independently review the supplied diff against the acceptance criteria and affected risks. Report actionable findings with file references. Do not edit files.',
}


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def allowed(provider, model, effort):
    require(any(model == mid and effort in efforts
                for mid, efforts in MODELS[provider].values()),
            f'Unsupported or prohibited {provider} model/effort: {model}/{effort}')


def plan(provider, profile, capabilities=None):
    catalog = read_json(ROOT / 'profiles/catalog.json')
    names = catalog['roles']
    pairs = catalog[provider][profile]
    require(set(names) == set(pairs) and len(set(names)) == len(names), 'Invalid role catalog')
    if capabilities is not None:
        require(capabilities['provider'] == provider and isinstance(capabilities['version'], str)
                and capabilities['version'].strip(), 'Capability provider/version missing or mismatched')
    roles = {}
    for role in names:
        family, requested = pairs[role].split('/')
        model, _ = MODELS[provider][family]
        allowed(provider, model, requested)
        effort = requested
        if capabilities is not None:
            supported = capabilities['models'].get(model, [])
            require(isinstance(supported, list), 'Capability efforts must be a list')
            if model == 'gpt-6-luna' and effort == 'max' and 'max' not in supported and 'xhigh' in supported:
                effort = 'xhigh'
            require(effort in supported, f'Client does not advertise {model}/{effort} for {role}')
        roles[role] = {'model': model, 'effort': effort, 'requested_effort': requested,
                       'approval_required': role == 'implementer-escalated'}
    return {'provider': provider, 'profile': profile, 'evidence': 'configured',
            'capability_version': capabilities['version'] if capabilities else None,
            'coordinator_control': 'host-selected; recommendation only', 'roles': roles}


def native_files(result):
    provider = result['provider']
    for role, config in result['roles'].items():
        if role == 'coordinator':
            continue
        name = 'acs-' + role
        model, effort = config['model'], config['effort']
        instructions = INSTRUCTIONS[role.split('-')[0]]
        if config['approval_required']:
            instructions = 'Use only after explicit user approval of escalation. ' + instructions
        description = 'ACS ' + role + '; use only for its assigned scope.'
        if provider == 'codex':
            values = dict(name=name, description=description, model=model,
                          model_reasoning_effort=effort, developer_instructions=instructions)
            yield '.codex/agents/' + name + '.toml', ''.join(f'{k} = {json.dumps(v)}\n' for k, v in values.items())
        else:
            values = dict(name=name, description=description, model=model, effort=effort)
            yield '.claude/agents/' + name + '.md', '---\n' + ''.join(f'{k}: {json.dumps(v)}\n' for k, v in values.items()) + '---\n\n' + instructions + '\n'


def render(result, output):
    # A new staging tree only. Installer/update ownership belongs to issue #3.
    output.mkdir()
    try:
        for relative, content in native_files(result):
            path = output / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
        (output / 'profile-plan.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    except Exception:
        shutil.rmtree(output)
        raise


def check(result, observed):
    provider = result['provider']
    require(result['capability_version'], 'check requires --capabilities from the target client')
    require(observed['provider'] == provider and observed['version'] == result['capability_version'],
            'Observed provider/version differs from capability inventory')
    require(isinstance(observed['sources_reviewed'], list) and observed['sources_reviewed']
            and all(isinstance(s, str) and s.strip() for s in observed['sources_reviewed']),
            'Record reviewed configuration sources')
    require(isinstance(observed['overrides'], list), 'List all inspected overrides, or []')
    require(not any(os.environ.get(key) for key in ENV_KEYS[provider]),
            'Routing environment selector present: ' + ', '.join(k for k in ENV_KEYS[provider] if os.environ.get(k)))
    expected = result['roles']
    require(set(observed['roles']) == set(expected), 'Audit must include every role, including coordinator')
    for role, row in list(observed['roles'].items()) + [(row['role'], row) for row in observed['overrides']]:
        require(role in expected, f'Unknown role: {role}')
        require(isinstance(row['source'], str) and row['source'].strip(), f'Missing source for {role}')
        model, effort = row['model'], row['effort']
        allowed(provider, model, effort)
        require((model, effort) == (expected[role]['model'], expected[role]['effort']),
                f'Profile mismatch for {role} from {row["source"]}; explicit change required')
    require(observed['fallbacks'] == [], 'Automatic model fallback configured or not accounted for')
    return {**result, 'audit': 'supplied configuration matches',
            'sources_reviewed': observed['sources_reviewed'], 'runtime_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan', 'render', 'check'])
    parser.add_argument('--provider', required=True, choices=MODELS)
    parser.add_argument('--profile', default='balanced', choices=['economy', 'balanced', 'quality'])
    parser.add_argument('--capabilities', type=Path)
    parser.add_argument('--observed', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = plan(args.provider, args.profile, read_json(args.capabilities) if args.capabilities else None)
        require(args.command == 'render' or args.output is None, '--output is only valid for render')
        require(args.command == 'check' or args.observed is None, '--observed is only valid for check')
        if args.command == 'render':
            require(args.output is not None, 'render requires --output (new directory)')
            render(result, args.output)
        if args.command == 'check':
            require(args.observed is not None, 'check requires --observed')
            result = check(result, read_json(args.observed))
        print(json.dumps(result, indent=2))
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as error:
        print(f'Profile error: {error}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
