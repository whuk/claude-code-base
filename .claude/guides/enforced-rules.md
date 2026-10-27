# 구조로 강제하는 규칙 대응표

반복된 실수를 문서 조항이 아니라 검사·hook 같은 구조로 막은 규칙과, 그 규칙을 강제하는 수단의 대응표다. `/rw:correct`가 행을 추가하고 갱신한다(`STYLE_GUIDE.md` 9번).

## 1. 대응표

| 규칙 | 강제 수단 | 위치 | 과거 실수 증거 |
|---|---|---|---|
| 커맨드 문서의 bash 블록은 Bash 호출 사이에 셸 변수·작업 디렉토리가 유지된다고 가정하지 않는다 | 검사 스크립트, Edit·Write 후 실행하는 `PostToolUse` hook | `.claude/scripts/check-command-shell.py`, `.claude/settings.json` | `163a267`(`blast-radius.md:23`), `253ba3c`(지시 누락이라 검사 범위 밖) |

## 2. 검사 실행

hook은 고친 파일 하나만 검사한다. 전체를 검사하려면 저장소 루트에서 실행한다. `python3`가 없으면 hook은 검사 없이 통과한다.

```bash
python3 .claude/scripts/check-command-shell.py
```
