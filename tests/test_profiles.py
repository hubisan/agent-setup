import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'scripts/profile.py'


class ProfilesTest(unittest.TestCase):
    def run_cli(self, *args, ok=True, env=None):
        result = subprocess.run([sys.executable, str(CLI), *map(str, args)],
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode == 0, ok, result.stderr)
        return json.loads(result.stdout) if ok else result.stderr

    def test_default_balanced_and_caps(self):
        plan = self.run_cli('plan', '--provider', 'codex')
        self.assertEqual(plan['profile'], 'balanced')
        self.assertEqual(plan['roles']['implementer']['model'], 'gpt-6-luna')
        self.assertEqual(plan['roles']['implementer']['effort'], 'max')
        self.assertEqual(plan['roles']['implementer-complex']['model'], 'gpt-6.2-sol')
        self.assertEqual(plan['roles']['implementer-complex']['effort'], 'medium')
        self.assertEqual(plan['evidence'], 'configured')

    def test_claude_cost_aware_profile_roles(self):
        expected = {
            'economy': ('low', 'sonnet/high', 'sonnet/medium', 'opus/low'),
            'balanced': ('low', 'sonnet/high', 'sonnet/high', 'opus/low'),
            'quality': ('medium', 'opus/medium', 'opus/medium', 'opus/medium'),
        }
        for profile, (coordinator, complex_role, reviewer, escalation) in expected.items():
            with self.subTest(profile=profile):
                roles = self.run_cli('plan', '--provider', 'claude-code', '--profile', profile)['roles']
                self.assertEqual(roles['coordinator']['model'], 'claude-sonnet-5-5')
                self.assertEqual(roles['coordinator']['effort'], coordinator)
                for name, pair in [('implementer-complex', complex_role), ('reviewer', reviewer),
                                   ('implementer-escalated', escalation)]:
                    family, effort = pair.split('/')
                    self.assertEqual((roles[name]['model'], roles[name]['effort']),
                                     ('claude-' + family + '-5-5', effort))
                if profile != 'quality':
                    self.assertEqual([name for name, row in roles.items()
                                      if row['model'] == 'claude-opus-5-5'], ['implementer-escalated'])
                self.assertTrue(roles['implementer-escalated']['approval_required'])

    def test_all_profiles_render_native_agents(self):
        for provider in ('codex', 'claude-code'):
            for profile in ('economy', 'balanced', 'quality'):
                with self.subTest(provider=provider, profile=profile), tempfile.TemporaryDirectory() as tmp:
                    output = Path(tmp) / 'staging'
                    plan = self.run_cli('render', '--provider', provider, '--profile', profile, '--output', output)
                    self.assertEqual(len(plan['roles']), 10)
                    self.assertTrue(plan['roles']['implementer-escalated']['approval_required'])
                    self.assertEqual(len(list(output.rglob('acs-*'))), 9)
                    for role, row in plan['roles'].items():
                        if row['model'] == 'gpt-6.2-sol':
                            self.assertIn(row['effort'], ('low', 'medium'))
                        if row['model'] == 'gpt-6.1-terra':
                            self.assertIn(row['effort'], ('medium', 'high'))
                        if row['model'] == 'claude-opus-5-5':
                            self.assertIn(row['effort'], ('low', 'medium'))
                        if role == 'coordinator':
                            continue
                        if provider == 'codex':
                            native = tomllib.loads((output / f'.codex/agents/acs-{role}.toml').read_text())
                            self.assertEqual(native['name'], 'acs-' + role)
                            self.assertEqual((native['model'], native['model_reasoning_effort']), (row['model'], row['effort']))
                        else:
                            content = (output / f'.claude/agents/acs-{role}.md').read_text()
                            self.assertIn(f'model: "{row["model"]}"', content)
                            self.assertIn(f'effort: "{row["effort"]}"', content)
                    self.run_cli('render', '--provider', provider, '--output', output, ok=False)
                    self.assertEqual(json.loads((output / 'profile-plan.json').read_text()), plan)

    def capability(self, provider, plan):
        models = {}
        for row in plan['roles'].values():
            models.setdefault(row['model'], [])
            if row['effort'] not in models[row['model']]:
                models[row['model']].append(row['effort'])
        return {'provider': provider, 'version': 'fixture', 'models': models}

    def test_luna_fallback_only_when_capabilities_require_it(self):
        plan = self.run_cli('plan', '--provider', 'codex')
        capabilities = self.capability('codex', plan)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'capabilities.json'
            capabilities['models']['gpt-6-luna'] = ['high', 'xhigh']
            path.write_text(json.dumps(capabilities))
            row = self.run_cli('plan', '--provider', 'codex', '--capabilities', path)['roles']['implementer']
            self.assertEqual((row['requested_effort'], row['effort']), ('max', 'xhigh'))
            capabilities['models']['gpt-6-luna'] = ['high']
            path.write_text(json.dumps(capabilities))
            self.assertIn('Client does not advertise', self.run_cli('plan', '--provider', 'codex', '--capabilities', path, ok=False))

    def test_check_rejects_override_inheritance_and_fallback(self):
        for provider in ('codex', 'claude-code'):
            with self.subTest(provider=provider), tempfile.TemporaryDirectory() as tmp:
                plan = self.run_cli('plan', '--provider', provider)
                cap = Path(tmp) / 'cap.json'
                cap.write_text(json.dumps(self.capability(provider, plan)))
                obs = Path(tmp) / 'obs.json'
                data = {'provider': provider, 'version': 'fixture', 'sources_reviewed': ['fixture config'],
                        'roles': {role: {'model': row['model'], 'effort': row['effort'], 'source': 'fixture'}
                                  for role, row in plan['roles'].items()}, 'overrides': [], 'fallbacks': []}
                args = ('check', '--provider', provider, '--capabilities', cap, '--observed', obs)
                obs.write_text(json.dumps(data))
                self.assertFalse(self.run_cli(*args)['runtime_verified'])
                row = data['roles']['implementer-complex']
                for model, effort in [(row['model'], 'low' if provider == 'claude-code' else 'high'),
                                      ('inherit', 'medium'), ('unknown', 'medium')]:
                    data['overrides'] = [{'role': 'implementer-complex', 'model': model, 'effort': effort, 'source': 'per-spawn'}]
                    obs.write_text(json.dumps(data))
                    self.run_cli(*args, ok=False)
                escalation = data['roles']['implementer-escalated']
                for effort in ('high', 'xhigh', 'max'):
                    data['overrides'] = [{'role': 'implementer-escalated', 'model': escalation['model'],
                                          'effort': effort, 'source': 'per-spawn'}]
                    obs.write_text(json.dumps(data))
                    self.assertIn('Unsupported or prohibited', self.run_cli(*args, ok=False))
                data['overrides'] = []
                data['fallbacks'] = ['unexpected']
                obs.write_text(json.dumps(data))
                self.assertIn('fallback', self.run_cli(*args, ok=False))
                data['fallbacks'] = []
                data['roles']['reviewer']['model'] = 'inherit'
                obs.write_text(json.dumps(data))
                self.run_cli(*args, ok=False)
                data['roles']['reviewer']['model'] = plan['roles']['reviewer']['model']
                obs.write_text(json.dumps(data))
                env = dict(os.environ)
                env['CLAUDE_CODE_EFFORT_LEVEL' if provider == 'claude-code' else 'CODEX_MODEL'] = 'override'
                self.assertIn('environment selector', self.run_cli(*args, ok=False, env=env))

    def test_unknown_profile_and_missing_capabilities_fail(self):
        self.run_cli('plan', '--provider', 'codex', '--profile', 'turbo', ok=False)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'cap.json'
            path.write_text(json.dumps({'provider': 'claude-code', 'version': 'fixture', 'models': {}}))
            self.assertIn('Client does not advertise', self.run_cli('plan', '--provider', 'claude-code', '--capabilities', path, ok=False))


if __name__ == '__main__':
    unittest.main()
