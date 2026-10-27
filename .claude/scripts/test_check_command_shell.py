#!/usr/bin/env python3
"""check-command-shell.py 회귀 테스트. 커맨드 문서 픽스처를 만들어 검사의 종료 코드로 판정한다.

실행: python3 .claude/scripts/test_check_command_shell.py
"""

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "check-command-shell.py"
FENCE = "```"


def bash_block(body):
    return f"{FENCE}bash\n{textwrap.dedent(body).strip()}\n{FENCE}\n"


class CheckCommandShellTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.commands = Path(self.tmp.name) / ".claude" / "commands"
        self.commands.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, content):
        path = self.commands / "fixture.md"
        path.write_text(content, encoding="utf-8")
        return path

    def check(self, content):
        path = self.write(content)
        return subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)

    def assertViolation(self, content):
        result = self.check(content)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("[shell-state]", result.stderr)

    def assertPasses(self, content):
        result = self.check(content)
        self.assertEqual(result.returncode, 0, result.stderr)

    # 변수
    def test_flags_variable_assigned_on_one_line_and_used_on_another(self):
        self.assertViolation(bash_block("X=$(mktemp -d)\necho $X"))

    def test_flags_variable_assigned_in_one_block_and_used_in_another(self):
        self.assertViolation(bash_block("WT=$(mktemp -d)") + "\n텍스트\n\n" + bash_block('git worktree remove "$WT"'))

    def test_passes_variable_assigned_and_used_on_the_same_line(self):
        self.assertPasses(bash_block("X=1; echo $X"))

    def test_passes_variable_assigned_and_used_inside_a_multiline_loop(self):
        self.assertPasses(bash_block("""
            for f in *.md; do
              b=$(basename "$f" .md)
              echo "$b"
            done | sort
        """))

    def test_flags_variable_assigned_inside_multiline_compound_and_used_after_it(self):
        self.assertViolation(bash_block("if true; then\n  Z=3\nfi\necho $Z"))

    def test_flags_variable_assigned_in_one_line_compound_and_used_on_next_line(self):
        self.assertViolation(bash_block("if true; then Z=3; fi\necho $Z"))

    def test_passes_variable_reassigned_before_use_on_the_same_line(self):
        self.assertPasses(bash_block("X=1\nX=2; echo $X"))

    def test_flags_previous_value_used_before_reassignment_on_the_same_line(self):
        self.assertViolation(bash_block("X=1\necho $X; X=2"))

    # cd
    def test_flags_standalone_cd(self):
        self.assertViolation(bash_block("cd /tmp\nls"))

    def test_passes_cd_chained_with_command(self):
        self.assertPasses(bash_block("cd /tmp && ls"))

    def test_passes_cd_followed_by_command_on_the_same_line(self):
        self.assertPasses(bash_block("cd /tmp; ls"))

    def test_flags_cd_as_last_command_on_a_line(self):
        self.assertViolation(bash_block("echo a; cd /tmp\nls"))

    def test_flags_cd_after_block_ending_with_line_continuation(self):
        self.assertViolation(bash_block("foo \\") + "\n" + bash_block("cd /tmp"))

    def test_flags_cd_as_last_command_inside_multiline_compound(self):
        self.assertViolation(bash_block("if true; then\n  cd /tmp\nfi\nls"))

    def test_passes_cd_followed_by_command_inside_multiline_compound(self):
        self.assertPasses(bash_block("for d in a b; do\n  cd $d\n  make\ndone"))

    # heredoc
    def test_ignores_heredoc_body(self):
        self.assertPasses(bash_block("""
            git commit -F - <<'EOF'
            X=1
            cd /tmp
            EOF
            echo done
        """))

    # hook
    def run_hook(self, path):
        payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(path)}})
        return subprocess.run([sys.executable, str(SCRIPT), "--hook"], input=payload, capture_output=True, text=True)

    def test_hook_blocks_violation_in_commands_document(self):
        result = self.run_hook(self.write(bash_block("cd /tmp\nls")))
        self.assertEqual(result.returncode, 2, result.stderr)

    def test_hook_ignores_file_outside_commands(self):
        path = Path(self.tmp.name) / "README.md"
        path.write_text(bash_block("cd /tmp\nls"), encoding="utf-8")
        self.assertEqual(self.run_hook(path).returncode, 0)


if __name__ == "__main__":
    unittest.main()
