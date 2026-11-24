"""End-to-end tests for the project-local installer; no live host required."""
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]
STATE = '.agents/setup/state.json'
PENDING = '.agents/setup/pending.json'


class InstallerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.target = self.base / 'target'
        self.target.mkdir()
        self.source = ROOT

    def cli(self, command, *options, ok=True, target=None, fail_at=None):
        script = self.source / 'scripts/install.py'
        args = [str(script), command, '--target', str(target or self.target), *map(str, options)]
        if fail_at:
            # Inject an I/O failure at the named destination, after any earlier writes.
            wrapper = """
import os, pathlib, runpy, sys
destination = sys.argv.pop(1)
script = sys.argv[1]
sys.argv = sys.argv[1:]
sys.path.insert(0, str(pathlib.Path(script).parent))
def interrupted(operation):
    def call(src, dst, *args, **kwargs):
        if str(dst) == destination:
            raise OSError('simulated interruption')
        return operation(src, dst, *args, **kwargs)
    return call
os.replace = interrupted(os.replace)
os.link = interrupted(os.link)
runpy.run_path(script, run_name='__main__')
"""
            launch = [sys.executable, '-c', wrapper, str(self.target / fail_at), *args]
        else:
            launch = [sys.executable, *args]
        result = subprocess.run(launch, capture_output=True, text=True, timeout=30)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertEqual(result.returncode, 2, result.stderr)
        return result.stderr

    def put(self, relative, data, mode=0o644, root=None):
        path = (root or self.target) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(mode)
        return path

    def read(self, relative):
        return (self.target / relative).read_bytes()

    def state(self):
        return json.loads(self.read(STATE))

    def tree(self):
        return {p.relative_to(self.target).as_posix(): (p.read_bytes(), stat.S_IMODE(p.stat().st_mode))
                for p in self.target.rglob('*') if p.is_file() and not p.is_symlink()}

    def install(self, *options):
        preview = self.cli('preview', *options)
        result = self.cli('apply', *options, '--approve', preview['approval'])
        self.assertTrue(result['applied'])
        return preview

    def fixture_source(self):
        # Only a private temporary test source; the real accepted registry remains empty.
        self.source = self.base / 'source'
        for rel in ('scripts/install.py', 'scripts/profile.py', 'scripts/hook_config.py',
                    'scripts/hook_runtime.py', 'core/manifest.json', 'core/APS.md',
                    'modules/acs/WORKFLOW.md', 'docs/models.md', 'profiles/catalog.json'):
            dst = self.source / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dst)
        manifest = json.loads((self.source / 'core/manifest.json').read_bytes())
        manifest['skills'] = {
            'aps-focus': {'status': 'accepted', 'module': 'aps', 'requires': ['aps-base']},
            'aps-base': {'status': 'accepted', 'module': 'aps', 'requires': []},
            'acs-example': {'status': 'accepted', 'module': 'acs', 'requires': []},
            'aps-candidate': {'status': 'candidate', 'module': 'aps', 'requires': []},
        }
        (self.source / 'core/manifest.json').write_text(json.dumps(manifest))
        for name in manifest['skills']:
            prefix = f'modules/{name.split("-")[0]}/skills/{name}'
            self.put(prefix + '/SKILL.md', f'---\nname: {name}\ndescription: Test only.\n---\n'.encode(),
                     root=self.source)
        self.put('modules/aps/skills/aps-focus/references/guide.md', b'Original reference\n', root=self.source)
        self.put('modules/aps/skills/aps-focus/scripts/check.sh', b'#!/bin/sh\nexit 0\n', 0o755, self.source)

    def test_fresh_aps_preview_apply_idempotent_remove(self):
        preview = self.cli('preview')
        self.assertFalse(list(self.target.iterdir()))
        self.assertEqual(preview['selection']['modules'], ['aps'])
        self.assertEqual(preview['selection']['skills'], [])
        self.assertEqual(preview['directories_to_create'], ['.agents', '.agents/setup'])
        self.assertEqual({r['path'] for r in preview['changes']}, {'AGENTS.md', 'CLAUDE.md', STATE})
        self.cli('apply', '--approve', preview['approval'])
        self.assertIn(b'Shared project workflow', self.read('AGENTS.md'))
        self.assertIn(b'@AGENTS.md', self.read('CLAUDE.md'))
        self.assertFalse((self.target / '.codex').exists())
        self.assertFalse((self.target / '.claude').exists())
        self.assertFalse((self.target / '.agents/skills').exists())
        self.assertFalse((self.target / '.agents/WORKFLOW.md').exists())
        self.assertFalse((self.target / '.agents/models.md').exists())
        self.assertFalse((self.target / '.agent-setup').exists())
        self.assertEqual(len(self.state()['source']['content_sha256']), 64)
        self.assertTrue(self.cli('status')['installed'])
        before = self.tree()
        self.assertEqual(self.cli('preview')['changes'], [])
        self.assertEqual(self.cli('preview', '--providers', 'codex,claude-code')['changes'], [])
        self.install()
        self.assertEqual(self.tree(), before)
        self.install('--remove')
        self.assertEqual(self.tree(), {})
        self.assertFalse(self.cli('status')['installed'])

    def test_existing_project_preserves_instructions_and_org_files(self):
        original = b'# Projekt\r\nEigene Regeln ohne Schlussumbruch'
        claude = b'# Existing Claude instructions\n@AGENTS.md\nKeep this.\n'
        self.put('AGENTS.md', original, 0o640)
        self.put('CLAUDE.md', claude)
        self.put('docs/notes.org', b'* Existing Org notes\n')
        self.put('src/AGENTS.md', b'Nested instructions\n')
        self.put('.claude/skills/user-skill/SKILL.md', b'Unrelated skill\n')
        before = self.tree()
        self.install()
        self.assertTrue(self.read('AGENTS.md').startswith(original))
        self.assertEqual(self.read('CLAUDE.md'), claude)
        self.assertEqual(stat.S_IMODE((self.target / 'AGENTS.md').stat().st_mode), 0o640)
        suffix = b'\n# New user rule\n'
        with (self.target / 'AGENTS.md').open('ab') as handle:
            handle.write(suffix)
        self.assertEqual(self.cli('preview')['changes'], [])
        self.install('--modules', 'acs', '--providers', 'codex')
        self.assertTrue(self.read('AGENTS.md').endswith(suffix))
        self.install('--remove')
        before['AGENTS.md'] = (original + suffix, 0o640)
        self.assertEqual(self.tree(), before)

    def test_acs_profiles_and_partial_provider_switch(self):
        self.put('.codex/agents/user.toml', b'name = "unrelated"\n')
        self.put('CLAUDE.md', b'Existing local guidance')
        before = self.tree()
        plan = self.install('--modules', 'acs')
        self.assertEqual(plan['selection']['modules'], ['acs', 'aps'])
        self.assertEqual(plan['selection']['added_modules'], ['aps'])
        self.assertEqual(plan['requested']['profile'], 'balanced')
        self.assertEqual(len(list((self.target / '.codex/agents').glob('acs-*.toml'))), 9)
        self.assertEqual(len(list((self.target / '.claude/agents').glob('acs-*.md'))), 9)
        self.assertIn(b'.agents/WORKFLOW.md', self.read('AGENTS.md'))
        self.assertNotIn(b'../../docs/models.md', self.read('.agents/WORKFLOW.md'))
        policy = self.read('.agents/models.md')
        self.assertIn(b'Sonnet is capped at high and Opus at medium', policy)
        self.assertIn(b'Opus low is reserved for user-approved escalation', policy)
        self.assertNotIn(b'## Profile commands', policy)
        for host in ('codex', 'claude-code'):
            expected = json.loads(self.read(f'.agents/setup/profile-{host}.json'))
            self.assertEqual(expected['profile'], 'balanced')
            self.assertEqual(expected['evidence'], 'configured')
        reviewer = tomllib.loads(self.read('.codex/agents/acs-reviewer.toml').decode())
        self.assertEqual(reviewer['model_reasoning_effort'], 'medium')
        self.assertIn(b'claude-sonnet-5-5', self.read('.claude/agents/acs-reviewer.md'))
        self.install('--profile', 'quality', '--providers', 'claude-code')
        self.assertEqual(list((self.target / '.codex/agents').glob('acs-*.toml')), [])
        self.assertEqual(self.read('.codex/agents/user.toml'), before['.codex/agents/user.toml'][0])
        self.assertFalse((self.target / '.agents/setup/profile-codex.json').exists())
        self.assertEqual(json.loads(self.read('.agents/setup/profile-claude-code.json'))['profile'], 'quality')
        self.install('--modules', 'aps')
        self.assertFalse((self.target / '.agents/WORKFLOW.md').exists())
        self.assertEqual(list((self.target / '.claude/agents').glob('acs-*.md')), [])
        self.install('--remove')
        self.assertEqual(self.tree(), before)

    def test_capabilities_are_retained_and_luna_fallback_resolved(self):
        inventory = self.base / 'capabilities.json'
        inventory.write_text(json.dumps({
            'provider': 'codex', 'version': 'fixture', 'models': {
                'gpt-6-luna': ['high', 'xhigh'],
                'gpt-6.1-terra': ['medium', 'high'],
                'gpt-6.2-sol': ['low', 'medium']}}))
        self.install('--modules', 'acs', '--providers', 'codex', '--codex-capabilities', inventory)
        plan = json.loads(self.read('.agents/setup/profile-codex.json'))
        fallback = [r for r in plan['roles'].values() if r['requested_effort'] == 'max']
        self.assertTrue(fallback)
        self.assertTrue(all(r['effort'] == 'xhigh' for r in fallback))
        inventory.unlink()
        self.assertEqual(self.cli('preview')['changes'], [])
        self.install('--codex-capabilities', 'none')
        self.assertIsNone(json.loads(self.read('.agents/setup/profile-codex.json'))['capability_version'])

    def test_selection_and_accepted_fixture_update_remove(self):
        self.fixture_source()
        self.put('.agents/skills/user-skill/SKILL.md', b'Unrelated')
        before = self.tree()
        plan = self.install('--skills', 'aps-focus')
        self.assertEqual(plan['selection']['skills'], ['aps-base', 'aps-focus'])
        self.assertEqual(plan['selection']['added_skills'], ['aps-base'])
        self.assertEqual(plan['selection']['modules'], ['aps'])
        for root in ('.agents/skills', '.claude/skills'):
            self.assertTrue((self.target / root / 'aps-base/SKILL.md').is_file())
            self.assertFalse((self.target / root / 'aps-candidate').exists())
            self.assertFalse((self.target / root / 'acs-example').exists())
            self.assertEqual(self.read(root + '/aps-focus/references/guide.md'), b'Original reference\n')
            self.assertEqual(stat.S_IMODE((self.target / root / 'aps-focus/scripts/check.sh').stat().st_mode), 0o755)
        old_source = self.state()['source']
        self.put('modules/aps/skills/aps-focus/references/guide.md', b'Updated\n', root=self.source)
        self.install()
        self.assertNotEqual(self.state()['source']['content_sha256'], old_source['content_sha256'])
        self.assertEqual(self.read('.agents/skills/aps-focus/references/guide.md'), b'Updated\n')
        self.assertEqual(self.read('.claude/skills/aps-focus/references/guide.md'), b'Updated\n')
        self.install('--skills', 'none')
        self.assertFalse((self.target / '.agents/skills/aps-focus/SKILL.md').exists())
        self.assertFalse((self.target / '.claude/skills/aps-base/SKILL.md').exists())
        self.install('--remove')
        self.assertEqual(self.tree(), before)

    def test_invalid_candidate_or_module_never_writes(self):
        self.fixture_source()
        for options in (('--skills', 'aps-candidate'), ('--skills', 'aps-unknown'),
                        ('--modules', 'gtd'), ('--providers', 'chatgpt'), ('--profile', 'quality')):
            with self.subTest(options=options):
                self.cli('preview', *options, ok=False)
                self.assertFalse(list(self.target.iterdir()))
        # A source directory is not acceptance, even when a SKILL.md exists.
        self.put('modules/aps/skills/aps-unregistered/SKILL.md', b'Test', root=self.source)
        self.assertIn('Unknown or unavailable accepted skill', self.cli(
            'preview', '--skills', 'aps-unregistered', ok=False))
        self.install('--skills', 'acs-example', '--providers', 'codex')
        self.assertEqual(self.state()['effective']['modules'], ['acs', 'aps'])

    def test_unowned_collision_and_override_no_writes(self):
        self.put('.codex/agents/acs-reviewer.toml', b'Existing')
        before = self.tree()
        self.assertIn('Unowned file collision', self.cli('preview', '--modules', 'acs', ok=False))
        self.assertEqual(self.tree(), before)
        self.put('AGENTS.override.md', b'Root override')
        before = self.tree()
        self.assertIn('would shadow', self.cli('preview', ok=False))
        self.assertEqual(self.tree(), before)

    def test_approval_and_local_managed_edits(self):
        self.put('AGENTS.md', b'User instructions\n')
        plan = self.cli('preview', '--modules', 'acs')
        self.put('AGENTS.md', b'New user instructions\n')
        before = self.tree()
        self.assertIn('preview stale', self.cli('apply', '--modules', 'acs', '--approve', plan['approval'], ok=False))
        self.assertEqual(self.tree(), before)
        self.install('--modules', 'acs')
        agent = '.codex/agents/acs-reviewer.toml'
        original = self.read(agent)
        self.put(agent, b'Local modification')
        before = self.tree()
        for options in ((), ('--profile', 'quality'), ('--remove',)):
            self.assertIn('Edited or missing managed file', self.cli('preview', *options, ok=False))
            self.assertEqual(self.tree(), before)
        self.put(agent, original)
        original = self.read('AGENTS.md')
        self.put('AGENTS.md', original.replace(b'Shared project workflow', b'Local edit inside block'))
        before = self.tree()
        self.assertIn('Edited or missing managed block', self.cli('preview', '--remove', ok=False))
        self.assertEqual(self.tree(), before)

    def test_skill_directory_collision_and_symlinks(self):
        self.fixture_source()
        self.put('.agents/skills/aps-focus/local.md', b'Unowned')
        before = self.tree()
        self.assertIn('Unowned content', self.cli('preview', '--skills', 'aps-focus', ok=False))
        self.assertEqual(self.tree(), before)
        (self.target / '.agents/skills/aps-focus/local.md').unlink()
        self.install('--skills', 'aps-focus')
        self.put('.claude/skills/aps-focus/local.md', b'Local extension')
        before = self.tree()
        self.assertIn('Unowned content', self.cli('preview', '--remove', ok=False))
        self.assertEqual(self.tree(), before)

    def test_reject_symlink_and_hardlink_collisions(self):
        outside = self.base / 'outside'
        outside.mkdir()
        secret = outside / 'AGENTS.md'
        secret.write_bytes(b'Outside data')
        (self.target / 'AGENTS.md').symlink_to(secret)
        self.assertIn('Symlink collision', self.cli('preview', ok=False))
        (self.target / 'AGENTS.md').unlink()
        os.link(secret, self.target / 'AGENTS.md')
        self.assertIn('Hard-link collision', self.cli('preview', ok=False))
        (self.target / 'AGENTS.md').unlink()
        (self.target / '.codex').symlink_to(outside, target_is_directory=True)
        self.assertIn('Symlink collision', self.cli('preview', '--modules', 'acs', ok=False))
        link = self.base / 'link'
        link.symlink_to(self.target, target_is_directory=True)
        self.assertIn('not symlinks', self.cli('preview', target=link, ok=False))
        self.assertEqual(secret.read_bytes(), b'Outside data')
        self.assertEqual(list(outside.iterdir()), [secret])

    def test_shared_agents_directory_preserves_unrelated_files(self):
        self.put('.agents/notes.md', b'Local notes')
        self.put('.agents/setup/local.json', b'{"owner":"project"}')
        self.put('.agents/skills/user-skill/SKILL.md', b'Existing skill')
        before = self.tree()
        self.install('--modules', 'acs', '--providers', 'codex')
        self.assertTrue((self.target / '.agents/WORKFLOW.md').is_file())
        self.assertTrue((self.target / '.agents/models.md').is_file())
        self.assertTrue((self.target / '.agents/setup/profile-codex.json').is_file())
        self.assertFalse((self.target / '.agents/agents').exists())
        self.assertFalse((self.target / '.agents/setup/profile-claude-code.json').exists())
        self.assertFalse((self.target / '.claude').exists())
        self.assertFalse((self.target / '.agent-setup').exists())
        self.assertEqual(self.cli('preview')['changes'], [])
        self.install('--remove')
        self.assertEqual(self.tree(), before)

    def test_shared_directory_collisions_fail_before_writes(self):
        self.put('.agents/WORKFLOW.md', b'Project-owned workflow')
        before = self.tree()
        self.assertIn('Unowned file collision', self.cli('preview', '--modules', 'acs', ok=False))
        self.assertEqual(self.tree(), before)
        (self.target / '.agents/WORKFLOW.md').unlink()
        outside = self.base / 'outside-setup'
        outside.mkdir()
        (self.target / '.agents/setup').symlink_to(outside, target_is_directory=True)
        self.assertIn('Symlink collision', self.cli('preview', ok=False))
        self.assertEqual(list(outside.iterdir()), [])
        (self.target / '.agents/setup').unlink()
        for name in ('state.json', 'pending.json'):
            with self.subTest(name=name):
                path = self.put('.agent-setup/' + name, b'Old draft')
                before = self.tree()
                self.assertIn('Legacy draft state detected', self.cli('preview', ok=False))
                self.assertEqual(self.tree(), before)
                path.unlink()

    def test_recover_interrupted_non_coding_install(self):
        self.put('AGENTS.md', b'User instructions\n', 0o640)
        before = self.tree()
        plan = self.cli('preview')
        self.assertIn('simulated interruption', self.cli(
            'apply', '--approve', plan['approval'], fail_at=STATE, ok=False))
        self.assertTrue((self.target / PENDING).is_file())
        self.assertEqual(stat.S_IMODE((self.target / PENDING).stat().st_mode), 0o600)
        self.assertIn('Pending transaction', self.cli('preview', ok=False))
        self.cli('recover')
        self.assertEqual(self.tree(), before)
        self.install()

    def test_recover_coding_update_and_refuse_new_edits(self):
        self.install('--modules', 'acs')
        before = self.tree()
        plan = self.cli('preview', '--profile', 'quality')
        self.assertIn('simulated interruption', self.cli(
            'apply', '--profile', 'quality', '--approve', plan['approval'], fail_at=STATE, ok=False))
        agent = '.agents/setup/profile-codex.json'
        interrupted = self.read(agent)
        self.assertNotEqual(interrupted, before[agent][0])
        self.put(agent, b'New local change')
        blocked = self.tree()
        self.assertIn('Recovery conflict', self.cli('recover', ok=False))
        self.assertEqual(self.tree(), blocked)
        self.put(agent, interrupted)
        self.cli('recover')
        self.assertEqual(self.tree(), before)
        self.install('--profile', 'quality')
        self.install('--remove')
        self.assertEqual(self.tree(), {})


    def init_git(self):
        subprocess.run(['git', 'init', '-q', str(self.target)], check=True)

    def test_optional_hooks_preserve_unrelated_settings_and_permissions(self):
        self.init_git()
        codex = {'description': 'local', 'hooks': {'SessionStart': [
            {'matcher': 'startup', 'hooks': [{'type': 'command', 'command': 'true'}]}]}}
        claude = {'permissions': {'deny': ['Bash(rm:*)']}, 'hooks': {'PreToolUse': [
            {'matcher': 'Bash', 'hooks': [{'type': 'command', 'command': 'true'}]}]}}
        self.put('.codex/hooks.json', json.dumps(codex).encode(), 0o640)
        self.put('.claude/settings.json', json.dumps(claude).encode(), 0o600)
        self.install('--modules', 'acs', '--guard-providers', 'codex',
                     '--telemetry-providers', 'claude-code')
        a = json.loads(self.read('.codex/hooks.json'))
        b = json.loads(self.read('.claude/settings.json'))
        self.assertEqual(a['hooks']['SessionStart'][0], codex['hooks']['SessionStart'][0])
        self.assertNotIn('SessionEnd', a['hooks'])
        self.assertIn('SessionEnd', b['hooks'])
        self.assertEqual(b['permissions'], claude['permissions'])
        self.assertEqual(stat.S_IMODE((self.target / '.claude/settings.json').stat().st_mode), 0o600)
        self.assertTrue((self.target / '.agents/hooks/runtime.py').is_file())
        self.assertEqual(self.cli('preview')['changes'], [])
        # User changes settings outside managed groups.
        b['env'] = {'LOCAL_SETTING': 'retained'}
        self.put('.claude/settings.json', json.dumps(b).encode(), 0o600)
        self.install('--guard-providers', 'claude-code', '--telemetry-providers', 'claude-code')
        self.assertEqual(json.loads(self.read('.codex/hooks.json')), codex)
        b = json.loads(self.read('.claude/settings.json'))
        self.assertEqual(len(b['hooks']['PreToolUse']), 2)
        self.assertTrue(b['hooks']['PreToolUse'][1]['hooks'][0]['command'].endswith(' both'))
        self.install('--guard-providers', 'none', '--telemetry-providers', 'none')
        claude['env'] = {'LOCAL_SETTING': 'retained'}
        self.assertEqual(json.loads(self.read('.claude/settings.json')), claude)
        self.assertEqual(json.loads(self.read('.codex/hooks.json')), codex)
        self.assertFalse((self.target / '.agents/hooks/runtime.py').exists())

    def test_hook_registration_conflicts_and_stale_preview(self):
        self.init_git()
        options = ('--modules', 'acs', '--guard-providers', 'codex,claude-code')
        config = self.put('.codex/config.toml', b'[[hooks.SessionStart]]\nmatcher = "startup"\n')
        self.assertIn('Existing inline Codex hooks', self.cli('preview', *options, ok=False))
        config.unlink()
        settings = self.put('.claude/settings.json', b'{"hooks":[]}')
        self.assertIn('Unsupported hooks', self.cli('preview', *options, ok=False))
        self.put('.claude/settings.json', b'{"hooks":{},"hooks":{}}')
        self.assertIn('Duplicate key', self.cli('preview', *options, ok=False))
        self.put('.claude/settings.json', b'{"permissions":{"deny":["Bash"]}}')
        plan = self.cli('preview', *options)
        self.put('.claude/settings.json', b'{"permissions":{"deny":["Write"]}}')
        self.assertIn('preview stale', self.cli('apply', *options, '--approve', plan['approval'], ok=False))
        self.install(*options)
        doc = json.loads(self.read('.claude/settings.json'))
        doc['hooks']['SessionStart'].append(doc['hooks']['SessionStart'][0])
        self.put('.claude/settings.json', json.dumps(doc).encode())
        before = self.tree()
        self.assertIn('duplicate managed hook', self.cli('preview', '--remove', ok=False))
        self.assertEqual(self.tree(), before)

    def test_hook_recovery_restores_existing_config_and_removes_new_files(self):
        self.init_git()
        self.put('.claude/settings.json', b'{"permissions":{"deny":["Bash"]}}\n', 0o600)
        before = self.tree()
        options = ('--modules', 'acs', '--guard-providers', 'codex,claude-code',
                   '--telemetry-providers', 'claude-code')
        plan = self.cli('preview', *options)
        self.assertIn('simulated interruption', self.cli('apply', *options,
                      '--approve', plan['approval'], fail_at=STATE, ok=False))
        self.assertTrue((self.target / '.claude/settings.json').exists())
        self.cli('recover')
        self.assertEqual(self.tree(), before)
        self.install(*options)
        self.install('--remove')
        self.assertFalse((self.target / '.codex/hooks.json').exists())
        self.assertEqual(json.loads(self.read('.claude/settings.json')), {'permissions': {'deny': ['Bash']}})

    def test_nested_git_and_claude_script_resolution(self):
        self.init_git()
        self.install('--modules', 'acs', '--guard-providers', 'codex,claude-code')
        nested = self.target / 'src/deep'
        nested.mkdir(parents=True)
        for path, provider in [('.codex/hooks.json', 'codex'), ('.claude/settings.json', 'claude-code')]:
            command = json.loads(self.read(path))['hooks']['SessionStart'][0]['hooks'][0]['command']
            result = subprocess.run(command, shell=True, cwd=nested, capture_output=True, text=True,
                                    input=json.dumps({'hook_event_name': 'SessionStart'}),
                                    env={**os.environ, 'CLAUDE_PROJECT_DIR': str(self.target)}, timeout=3)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, '')
            self.assertEqual(result.stderr, '')


    def test_hook_script_resolves_in_linked_worktree_with_spaces(self):
        self.init_git()
        subprocess.run(['git', '-C', str(self.target), '-c', 'user.name=Fixture',
                        '-c', 'user.email=fixture@example.invalid',
                        'commit', '--allow-empty', '-qm', 'Fixture'], check=True)
        worktree = self.base / 'linked worktree'
        subprocess.run(['git', '-C', str(self.target), 'worktree', 'add', '--detach',
                        str(worktree)], check=True, capture_output=True)
        self.target = worktree
        self.install('--modules', 'acs', '--guard-providers', 'codex,claude-code')
        nested = self.target / 'nested'
        nested.mkdir()
        for path in ('.codex/hooks.json', '.claude/settings.json'):
            command = json.loads(self.read(path))['hooks']['SessionStart'][0]['hooks'][0]['command']
            result = subprocess.run(command, shell=True, cwd=nested, capture_output=True, text=True,
                                    input='{"hook_event_name":"SessionStart"}',
                                    env={**os.environ, 'CLAUDE_PROJECT_DIR': str(self.target)}, timeout=3)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, '')
            self.assertEqual(result.stderr, '')


if __name__ == '__main__':
    unittest.main()
