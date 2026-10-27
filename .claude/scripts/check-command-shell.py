#!/usr/bin/env python3
"""커맨드 문서의 bash 블록이 Bash 호출 사이에 셸 상태가 유지된다고 가정하는지 검사한다.

Claude Code의 Bash 도구는 호출마다 셸 변수와 작업 디렉토리를 초기화한다.
커맨드 문서의 bash 블록은 한 줄(논리 줄)이 한 번의 호출로 실행될 수 있으므로,
최상위에서 대입한 변수를 다른 줄에서 참조하거나 `&&` 없이 단독으로 `cd`하면 실패로 판정한다.

사용법:
  python3 .claude/scripts/check-command-shell.py [파일...]   # 인자가 없으면 .claude/commands 전체
  python3 .claude/scripts/check-command-shell.py --hook      # PostToolUse hook(stdin JSON)
"""

import json
import re
import sys
from pathlib import Path

FENCE_OPEN = re.compile(r"^\s*```bash\s*$")
FENCE_CLOSE = re.compile(r"^\s*```\s*$")
ASSIGN = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=")
STANDALONE_CD = re.compile(r"^cd(\s|$)")
OPENERS = re.compile(r"^(for|while|until|if|case)\b|\{\s*$")
CLOSERS = re.compile(r"^(done|fi|esac|\})\b")
COMMANDS_DIR = Path(".claude/commands")


def strip_comment(line):
    if line.lstrip().startswith("#"):
        return ""
    return re.sub(r"\s+#.*$", "", line)


def logical_lines(path):
    """bash 블록의 논리 줄을 (블록 번호, 시작 행, 텍스트, 복합문 깊이)로 반환한다."""
    in_block = False
    block = 0
    depth = 0
    pending = None
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not in_block:
            if FENCE_OPEN.match(raw):
                in_block, block, depth = True, block + 1, 0
            continue
        if FENCE_CLOSE.match(raw):
            in_block = False
            continue
        text = strip_comment(raw).strip()
        if pending:
            start, head = pending
            text = head + " " + text
        else:
            start = number
        if text.endswith("\\"):
            pending = (start, text[:-1].strip())
            continue
        pending = None
        if not text:
            continue
        if CLOSERS.match(text):
            depth = max(depth - 1, 0)
        yield block, start, text, depth
        if OPENERS.search(text) and not re.search(r"\b(done|fi|esac)\b|\}\s*$", text):
            depth += 1


def check(path):
    errors = []
    assigned = {}
    for block, line, text, depth in logical_lines(path):
        for name, origin in assigned.items():
            if re.search(r"\$\{?" + name + r"\b", text):
                errors.append(
                    f"{path}:{line}: [shell-state] 변수 {name}을(를) {origin}행에서 대입하고 다른 줄에서 참조합니다. "
                    f"Bash 호출마다 셸 변수가 초기화되므로, 값을 출력해 기록하고 {{자리표시자}}로 넘기세요."
                )
        if depth > 0:
            continue
        match = ASSIGN.match(text)
        if match:
            assigned[match.group(1)] = line
        if STANDALONE_CD.match(text) and "&&" not in text:
            errors.append(
                f"{path}:{line}: [shell-state] 단독 cd는 다음 Bash 호출까지 유지되지 않습니다. "
                f"`cd {{경로}} && {{명령}}`처럼 실행할 명령과 같은 줄에 쓰세요."
            )
    return errors


def targets_from_hook():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return []
    file_path = payload.get("tool_input", {}).get("file_path", "")
    path = Path(file_path)
    if path.suffix == ".md" and "/.claude/commands/" in path.as_posix() and path.exists():
        return [path]
    return []


def main(argv):
    hook = "--hook" in argv
    if hook:
        paths = targets_from_hook()
    elif argv:
        paths = [Path(arg) for arg in argv]
    else:
        paths = sorted(COMMANDS_DIR.rglob("*.md"))
    errors = [error for path in paths for error in check(path)]
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 2 if hook else 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
