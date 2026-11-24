import json
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import hook_config
import profile as profiles


class HookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / 'project'
        self.folder = self.project / '.agents/hooks'
        self.folder.mkdir(parents=True)
        self.home = self.base / 'home'
        self.home.mkdir()
        self.runtime = self.folder / 'runtime.py'
        shutil.copyfile(ROOT / 'scripts/hook_runtime.py', self.runtime)
        for provider in ('codex', 'claude-code'):
            p = hook_config.policy_for(profiles.plan(provider, 'balanced'))
            (self.folder / f'policy-{provider}.json').write_text(json.dumps(p))

    def call(self, provider, mode, event, **fields):
        payload = {'hook_event_name': event, 'session_id': 'private-session', **fields}
        result = subprocess.run([sys.executable, str(self.runtime), provider, mode],
                                input=json.dumps(payload), capture_output=True, text=True,
                                env={**os.environ, 'HOME': str(self.home)}, timeout=3)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout) if result.stdout else {}

    def events(self):
        paths = list(self.home.glob('.local/state/agent-setup-hooks/*/*.jsonl'))
        return [json.loads(row) for path in paths for row in path.read_text().splitlines()]

    def test_denies_explicit_codex_sol_high_but_not_missing_model(self):
        out = self.call('codex', 'guard', 'PreToolUse', tool_name='spawn_agent',
                        tool_input={'model': 'gpt-6.2-sol', 'reasoning_effort': 'high'})
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        out = self.call('codex', 'guard', 'PreToolUse', tool_name='spawn_agent',
                        tool_input={'reasoning_effort': 'high'})
        self.assertNotIn('hookSpecificOutput', out)
        self.assertEqual(self.events(), [])

    def test_luna_max_and_role_mismatch(self):
        out = self.call('codex', 'guard', 'PreToolUse', tool_name='spawn_agent',
                        tool_input={'agent_type': 'acs-implementer', 'model': 'gpt-6-luna',
                                    'reasoning_effort': 'max'})
        self.assertEqual(out, {})
        out = self.call('codex', 'guard', 'PreToolUse', tool_name='spawn_agent',
                        tool_input={'agent_type': 'acs-implementer', 'model': 'gpt-6.1-terra'})
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')

    def test_claude_cap_and_unknown_alias(self):
        out = self.call('claude-code', 'guard', 'PreToolUse', tool_name='Agent',
                        tool_input={'model': 'claude-opus-5-5', 'effort': 'high'})
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        out = self.call('claude-code', 'guard', 'PreToolUse', tool_name='Agent',
                        tool_input={'model': 'opus', 'effort': 'high'})
        self.assertNotIn('hookSpecificOutput', out)

    def test_model_request_is_diagnostic_and_usage_is_allowlisted(self):
        out = self.call('codex', 'both', 'PreModelRequest', model='gpt-6-astra',
                        prompt='SECRET_PROMPT')
        self.assertNotIn('hookSpecificOutput', out)
        self.call('codex', 'telemetry', 'PostModelRequest', model='gpt-6.2-sol',
                  status='failed', error='SECRET_ERROR', token_usage={'input_tokens': 0,
                  'cached_input_tokens': 2, 'cache_write_input_tokens': 3, 'output_tokens': False, 'secret': 'SECRET_USAGE'})
        rows = self.events()
        self.assertEqual(len(rows), 2)
        self.assertIsNone(rows[0]['usage'])
        self.assertEqual(rows[1]['usage'], {'input_tokens': 0, 'cached_input_tokens': 2, 'cache_write_input_tokens': 3})
        self.assertEqual(rows[1]['status'], 'failed')
        self.assertFalse(rows[1]['runtime_verified'])
        self.assertNotIn('SECRET', json.dumps(rows))
        self.assertNotIn('private-session', json.dumps(rows))

    def test_telemetry_only_never_denies(self):
        out = self.call('claude-code', 'telemetry', 'PreToolUse', tool_name='Agent',
                        tool_input={'model': 'claude-opus-5-5', 'effort': 'max', 'prompt': 'SECRET'})
        self.assertEqual(out, {})
        self.assertEqual(self.events()[0]['policy_result'], 'violation')
        self.assertFalse(self.events()[0]['guard_enabled'])

    def test_registration_independent_and_combined(self):
        for provider in ('codex', 'claude-code'):
            self.assertEqual(hook_config.registrations(provider, False, False), {})
            guard = hook_config.registrations(provider, True, False)
            telemetry = hook_config.registrations(provider, False, True)
            both = hook_config.registrations(provider, True, True)
            self.assertNotIn('SessionEnd', guard)
            self.assertIn('SessionEnd', telemetry)
            self.assertEqual(len(both['PreToolUse']), 1)
            self.assertTrue(both['PreToolUse'][0]['hooks'][0]['command'].endswith(' both'))
        self.assertNotIn('PreModelSwitch', hook_config.registrations('claude-code', False, True))

    def test_unknown_payload_does_not_block_or_record_raw_data(self):
        self.assertEqual(self.call('codex', 'both', 'NewEvent', raw='SECRET'), {})
        self.assertEqual(self.events(), [])


    def test_canonical_claude_switch_denies_unlisted_model_but_not_unknown(self):
        out = self.call('claude-code', 'both', 'PreModelSwitch', to_model='claude-opus-4-6')
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        out = self.call('claude-code', 'guard', 'PreModelSwitch', to_model=None)
        self.assertNotIn('hookSpecificOutput', out)
        self.assertEqual(self.events()[0]['policy_result'], 'violation')

    def test_terra_sonnet_caps_and_escalation_evidence(self):
        for provider, model, effort, tool in [
                ('codex', 'gpt-6.1-terra', 'xhigh', 'spawn_agent'),
                ('claude-code', 'claude-sonnet-5-5', 'max', 'Agent')]:
            effort_field = 'reasoning_effort' if provider == 'codex' else 'effort'
            out = self.call(provider, 'guard', 'PreToolUse', tool_name=tool,
                            tool_input={'model': model, effort_field: effort})
            self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        out = self.call('claude-code', 'both', 'PreToolUse', tool_name='Agent',
                        tool_input={'subagent_type': 'acs-implementer-escalated',
                                    'model': 'claude-opus-5-5', 'effort': 'low'})
        self.assertNotIn('hookSpecificOutput', out)
        self.assertEqual(self.events()[0]['policy_reason'], 'escalation-approval-unobserved')

    def test_internal_deadline_is_non_denial(self):
        proc = subprocess.Popen([sys.executable, str(self.runtime), 'claude-code', 'guard'],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            self.assertEqual(proc.wait(timeout=3), 1)
            self.assertEqual(proc.stdout.read(), b'')
            self.assertIn(b'evidence unavailable', proc.stderr.read())
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
            proc.stdin.close()
            proc.stdout.close()
            proc.stderr.close()


    def test_private_storage_and_symlink_conflict_does_not_erase_denial(self):
        self.call('codex', 'telemetry', 'SessionStart', model='gpt-6-luna')
        base = self.home / '.local/state/agent-setup-hooks'
        log = next(base.glob('*/*.jsonl'))
        self.assertEqual(log.stat().st_mode & 0o777, 0o600)
        self.assertEqual(log.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(base.stat().st_mode & 0o777, 0o700)
        shutil.rmtree(base)
        outside = self.base / 'outside'
        outside.mkdir()
        base.symlink_to(outside, target_is_directory=True)
        out = self.call('codex', 'both', 'PreToolUse', tool_name='spawn_agent',
                        tool_input={'model': 'gpt-6.2-sol', 'reasoning_effort': 'max'})
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertEqual(list(outside.iterdir()), [])


    def test_normal_and_routine_unknown_events_have_zero_output(self):
        for provider, tool, model, effort_key, effort in (
                ('codex', 'spawn_agent', 'gpt-6-luna', 'reasoning_effort', 'max'),
                ('claude-code', 'Agent', 'claude-sonnet-5-5', 'effort', 'medium')):
            for mode in ('guard', 'telemetry', 'both'):
                for event, fields in (
                        ('SessionStart', {'model': model}),
                        ('PreToolUse', {'tool_name': tool,
                                        'tool_input': {'model': model, effort_key: effort}}),
                        ('PreToolUse', {'tool_name': tool, 'tool_input': {}})):
                    with self.subTest(provider=provider, mode=mode, event=event, fields=fields):
                        result = subprocess.run(
                            [sys.executable, str(self.runtime), provider, mode],
                            input=json.dumps({'hook_event_name': event, **fields}),
                            capture_output=True,
                            env={**os.environ, 'HOME': str(self.home)}, timeout=3)
                        self.assertEqual(result.returncode, 0)
                        self.assertEqual(result.stdout, b'')
                        self.assertEqual(result.stderr, b'')


if __name__ == '__main__':
    unittest.main()
