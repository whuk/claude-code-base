---
description: "열린 PR을 code-reviewer 에이전트로 리뷰하고 결과를 PR 코멘트로 남긴다. 승인·변경요청·머지는 하지 않는다."
argument-hint: "리뷰할 PR 번호 (예: #123 또는 123, 선택). 생략하면 현재 브랜치의 열린 PR을 대상으로 합니다."
user-invocable: true
---

# /rw:git:pr-review — PR 코드 리뷰 및 결과 코멘트

열린 PR의 변경분을 `code-reviewer` 에이전트(+ 저장소에 남아 있는 스택 전담 리뷰어)로 리뷰하고, 결과를 PR 코멘트로 남긴 뒤 확인용 링크를 출력합니다. **리뷰 accept(승인)와 머지는 사람이 직접 합니다** — 이 커맨드는 승인·변경요청·머지를 수행하지 않습니다.

`/rw:git:commit-and-push`(또는 `/commit-commands:commit-push-pr`)로 PR을 올린 뒤, `/rw:git:squash-merge-pull`로 머지하기 전에 실행하는 중간 단계입니다.

## 1단계: 대상 PR 결정

다음 순서로 분기 판정하세요.

### 경로 A: `$ARGUMENTS`에 PR 번호가 입력된 경우

`#123`, `123` 형식에서 숫자만 추출해 대상 PR로 삼습니다.

### 경로 B: `$ARGUMENTS`가 비어 있는 경우

1. `gh pr view --json number,url,title,state,headRefName,baseRefName`으로 현재 브랜치에 연결된 PR을 조회합니다.
2. 현재 브랜치에 열린 PR이 없으면 다음 메시지를 출력하고 **중단**하세요:
   > 현재 브랜치에 열린 PR이 없습니다. `/rw:git:commit-and-push`로 push한 뒤 PR을 먼저 생성해 주세요.
3. 여러 PR이 후보로 잡히면 목록을 보여주고 사용자에게 대상을 확인받습니다. 임의로 고르지 마세요.

## 2단계: PR 상태 확인

1. `gh pr view <PR번호> --json number,url,title,body,state,isDraft,mergeable,headRefName,baseRefName,files`로 PR 정보를 조회합니다.
2. PR이 이미 머지되었거나 닫혀 있으면 그 사실을 알리고 **중단**하세요.
3. Draft PR이면 리뷰는 진행해도 되지만, 결과 보고에서 Draft 상태임을 명시하세요.
4. `mergeable`이 충돌 상태면 리뷰를 중단하지 않되, 충돌 해소 전에는 머지할 수 없다는 사실을 결과 보고에 포함하세요.

## 3단계: 리뷰 범위 수집

1. `gh pr diff <PR번호>`로 변경분 전체를 가져옵니다. 필요하면 `gh pr diff <PR번호> --name-only`로 파일 목록을 먼저 확인합니다.
2. 변경분이 비어 있으면 리뷰할 내용이 없다고 보고하고 **중단**하세요.
3. 변경 파일의 확장자와 `.claude/rules/` 하위에 남아 있는 규칙 디렉토리로 저장소 스택을 판정합니다. 이 프로젝트가 채택하지 않아 삭제된 규칙은 리뷰 기준에서 제외합니다.

## 4단계: 리뷰 수행 (에이전트 위임)

리뷰는 직접 하지 않고 에이전트에게 위임합니다.

1. **`code-reviewer` 에이전트를 호출**해 일반 리뷰 관점(정확성·보안·중복·코드 스멜·컨벤션·에러 처리·성능·테스트)을 검토합니다. 대상 PR 번호와 리뷰 범위를 프롬프트에 명시합니다.
2. 3단계에서 판정한 스택의 **전담 리뷰어가 저장소에 남아 있으면 함께 호출**해 아키텍처 규칙 축을 검토합니다. 두 에이전트는 서로 독립적이므로 한 번에 병렬로 호출하세요.
   - Spring: `spring-code-reviewer`(Layered) 또는 `spring-hexagonal-code-reviewer`(Hexagonal)
   - NestJS: `nestjs-code-reviewer` / FastAPI: `fastapi-code-reviewer`
   - 프론트엔드: `frontend-code-reviewer`(React 계열) 또는 `frontend-vue-code-reviewer`(Vue.js)
   - 풀스택이면 백엔드·프론트엔드 리뷰어를 모두 호출합니다.
3. 반환된 결과를 병합합니다. 같은 `파일:라인`에 대한 중복 지적은 하나로 합치고, 등급이 다르면 높은 등급을 채택합니다.
4. 병합 결과를 심각도 순(Blocker → Major → Minor → Nit)으로 정렬하고 등급별 개수를 집계합니다. 지적이 하나도 없으면 그 사실을 그대로 유지합니다(억지로 항목을 만들지 않습니다).

## 5단계: 사용자 확인 후 PR 코멘트 게시

1. 게시할 코멘트 본문 전문과 대상 PR(번호·제목·URL)을 사용자에게 보여주고 **게시 여부를 확인받습니다.** 확인 없이 게시하지 마세요. 사용자가 거절하면 결과를 세션에만 출력하고 6단계로 넘어갑니다.
2. 코멘트 본문은 다음 구조로 작성합니다.

   ```markdown
   ## 코드 리뷰 결과

   - 리뷰 범위: `<base>...<head>` (변경 파일 N개)
   - 실행한 리뷰어: code-reviewer, <스택 리뷰어>
   - 요약: Blocker N / Major N / Minor N / Nit N

   ### Blocker
   - `파일:라인` — 문제
     - 근거: <위반 규칙 또는 실패 시나리오>
     - 제안: <구체적 대안>

   ### Major
   ...

   ### 참고 (이번 변경 범위 밖)
   ...

   > 이 리뷰는 Claude Code가 자동 생성했습니다. 승인(accept)과 머지는 사람이 직접 판단합니다.
   ```

3. 확인되면 `gh pr comment <PR번호>`로 게시합니다. 본문은 HEREDOC으로 전달하세요:
   ```bash
   gh pr comment <PR번호> --body "$(cat <<'EOF'
   <코멘트 본문>
   EOF
   )"
   ```
4. **`gh pr review`는 사용하지 마세요.** `--approve`/`--request-changes`는 물론 `--comment`도 사용하지 않습니다 — PR의 리뷰 상태를 바꾸지 않고 일반 코멘트만 남기는 것이 이 커맨드의 계약입니다.
5. 게시 명령이 출력한 코멘트 URL을 기록합니다. 게시에 실패하면(권한·네트워크) 원인을 보고하고 리뷰 결과를 세션에 그대로 출력하세요. 재시도를 반복하지 마세요.

## 결과 보고

다음을 간결하게 보고하세요. 링크는 사용자가 바로 클릭할 수 있도록 전체 URL로 출력합니다.

- 대상 PR: 번호, 제목, **PR URL**
- 게시한 리뷰 코멘트 **URL** (게시하지 않았으면 그 사유)
- 심각도별 지적 개수 요약 (Blocker/Major/Minor/Nit)
- Draft 여부, 충돌(`mergeable`) 상태 등 머지 전 확인이 필요한 사항
- 다음 단계 안내:
  - Blocker/Major가 있으면: 해당 지적을 수정한 뒤 이 커맨드를 다시 실행하도록 안내합니다. 수정은 이 커맨드가 하지 않습니다.
  - 지적이 없거나 Minor/Nit만 남으면: **사용자가 PR에서 직접 리뷰를 확인·승인한 뒤** `/rw:git:squash-merge-pull`로 머지하도록 안내합니다.

## 하지 말아야 할 것

- `gh pr review --approve` / `--request-changes` / `--comment` 실행하기 (리뷰 accept는 사람의 몫이며, 리뷰 상태를 바꾸지 않는다)
- PR 머지하기 (`/rw:git:squash-merge-pull`의 범위)
- 리뷰 중 발견한 문제를 직접 수정하거나 커밋·push 하기 (read-only 리뷰 흐름이다)
- 사용자 확인 없이 PR에 코멘트 게시하기
- 리뷰를 커맨드 세션에서 직접 수행하기 (`code-reviewer` 및 스택 리뷰어 에이전트에게 위임한다)
- 이 프로젝트가 채택하지 않아 삭제된 규칙 파일을 근거로 지적하기
- 지적이 없는데 형식을 채우려고 억지 지적을 만들기
- 변경분과 무관한 기존 코드를 머지 조건으로 지적하기
- 게시 실패 시 무한 재시도하거나 다른 PR에 게시하기
