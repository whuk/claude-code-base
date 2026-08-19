# Status Line 설정 가이드

Claude Code 상태표시줄을 [claude-hud](https://github.com/jarrodwatts/claude-hud) 플러그인으로 설정하는 방법입니다.
새 프로젝트나 다른 머신으로 이동했을 때 이 파일을 참고하여 동일한 상태표시줄을 재현합니다.

## 왜 claude-hud인가

Claude Code는 `settings.json`의 `statusLine` 필드에 등록된 셸 커맨드를 실행하고, **세션 데이터를 JSON으로 stdin에 넘긴 뒤 그 출력을 입력창 아래 전용 행에 렌더링**합니다. 이 방식은 로컬에서 실행되므로 API 토큰을 소모하지 않고, 컨텍스트 사용률·비용·rate limit 같은 정확한 수치를 그대로 받아 씁니다.

claude-hud는 여기에 더해 **현재 세션의 transcript(JSONL)를 파싱**하여, 다른 상태표시줄이 보여주지 못하는 "Claude가 지금 무엇을 하고 있는가"를 표시합니다 — 실행 중인 툴, 동작 중인 서브에이전트, todo 진행 상황. 미관보다 진행 상황 관측을 우선할 때 적합합니다.

로컬 전용으로 동작하며 네트워크 요청을 하지 않습니다. 읽는 대상은 stdin JSON, Claude Code가 넘겨준 transcript 경로, `~/.claude` 하위 설정 파일, git 메타데이터입니다.

## 요구사항

- Claude Code v1.0.80 이상
- macOS/Linux: Node.js 18+ 또는 Bun
- Windows: Node.js 18+ (필수)

Nerd Font는 필요하지 않습니다.

## 설치

세션 안에서 슬래시 커맨드로 진행합니다.

```text
/plugin marketplace add jarrodwatts/claude-hud
/plugin install claude-hud
/reload-plugins
/claude-hud:setup
```

마지막 `/claude-hud:setup`이 `settings.json`의 `statusLine` 항목까지 설정합니다.

세션 밖에서 CLI로 설치하려면:

```bash
claude plugin marketplace add jarrodwatts/claude-hud
claude plugin install claude-hud@claude-hud
```

## 표시 항목

기본 2줄 구성입니다.

| 줄 | 내용 |
|---|---|
| 1줄 | 모델 배지, 프로젝트 경로, git 브랜치 |
| 2줄 | 컨텍스트 사용량 바(초록 → 노랑 → 빨강), rate limit 소진율 |

선택적으로 켤 수 있는 줄: 툴 활동(파일 읽기/편집/검색), 에이전트 상태, todo 진행률.

## 설정

`~/.claude/plugins/claude-hud/config.json`에서 조정합니다.

| 키 | 값 | 설명 |
|---|---|---|
| `lineLayout` | `"expanded"` / `"compact"` | 줄 배치 밀도 |
| `pathLevels` | `1`~`3` / `"full"` | 경로를 몇 단계까지 표시할지 |
| `display.showTools` | boolean | 툴 활동 줄 표시 |
| `display.showAgents` | boolean | 에이전트 상태 줄 표시 |
| `display.showTodos` | boolean | todo 진행 줄 표시 |
| `display.showUsage` | boolean | rate limit 표시 |
| `colors.*` | 색상명 또는 hex | 색상 커스터마이징 |

## 일시 비활성화

설정을 지우지 않고 해당 세션에서만 끄려면 환경변수를 사용합니다.

```bash
CLAUDE_HUD_DISABLE=1
```

완전히 제거하려면 `settings.json`에서 `statusLine` 필드를 삭제하거나 `/statusline` 에게 삭제를 요청합니다.

## 참고사항

- 상태표시줄은 로컬에서 실행되며 **API 토큰을 소모하지 않습니다.** 세션 시작 시 1회, 이후 새 어시스턴트 메시지 도착·`/compact` 완료·권한 모드 변경·vim 모드 전환 시 자동으로 갱신됩니다(300ms 디바운스).
- 컨텍스트 사용률과 비용이 상태표시줄에 상시 표시되므로 `/cost`를 따로 실행할 필요가 줄어듭니다. 다만 `cost.total_cost_usd`는 클라이언트에서 추정한 값이라 실제 청구액과 다를 수 있으며, 정확한 공식 수치는 `/cost`로 확인합니다.
- 직접 스크립트를 작성하고 싶다면 `settings.json`에 `statusLine`을 등록하고 stdin JSON을 파싱하면 됩니다. 사용 가능한 필드 전체 목록은 [공식 문서](https://code.claude.com/docs/en/statusline)를 참고하세요.
