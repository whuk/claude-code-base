# Status Line Configuration Prompt

아래 프롬프트를 Claude Code 세션 시작 시 복사해서 사용하세요.
새 프로젝트나 다른 머신으로 이동했을 때 이 파일을 참고하여 상태표시줄을 설정합니다.

---

## 📋 프롬프트 (복사하여 사용)

```
현재 세션에서 아래 형식의 상태표시줄(status line)을 설정해줘.

**표시 형식:**
{현재 디렉토리} | {모델명} | {git branch} | 토큰 사용: {사용량} | 토큰 잔여: {잔여량} ({잔여%}%)

**구현 요구사항:**

### 공통
- 현재 작업 디렉토리(pwd/Get-Location)를 실시간으로 읽어올 것
- 현재 사용 중인 Claude 모델명을 표시할 것
- git 저장소인 경우 현재 브랜치명을, git 저장소가 아닌 경우 `(no git)`을 표시할 것
- 토큰 사용량 및 잔여량을 가능한 경우 표시할 것 (API 응답 또는 세션 정보 기반)

### OS 환경 감지 및 설치 안내
현재 OS를 먼저 확인하고, 그에 맞는 방법으로 상태표시줄을 구성할 것.
필요한 프로그램이 없다면 설치 방법을 안내하고 설치 후 진행할 것.

#### Windows (PowerShell / CMD)
- `$env:OS`가 `Windows_NT`이거나 `[System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform([System.Runtime.InteropServices.OSPlatform]::Windows)`가 True인 경우
- git 브랜치: `git rev-parse --abbrev-ref HEAD 2>$null`
- JSON 파싱이 필요한 경우 PowerShell 내장 `ConvertFrom-Json` 사용 (jq 불필요)
- jq가 필요한 상황이라면 winget 또는 choco로 설치 안내:
  - `winget install jqlang.jq` 또는 `choco install jq`
- 경로 표시: 백슬래시(`\`) 형식, 예) `C:\Users\user\project`

#### macOS / Linux (Bash / Zsh)
- `uname -s`로 OS 확인 (`Darwin` = macOS, `Linux` = Linux)
- git 브랜치: `git rev-parse --abbrev-ref HEAD 2>/dev/null`
- jq가 설치되어 있지 않다면 자동 설치 시도:
  - macOS: `brew install jq`
  - Ubuntu/Debian: `sudo apt-get install -y jq`
  - RHEL/CentOS: `sudo yum install -y jq`
- 경로 표시: 슬래시(`/`) 형식, 예) `/home/user/project`

### 각 요소 획득 방법

| 항목 | Windows (PowerShell) | macOS/Linux (Bash) |
|------|----------------------|---------------------|
| 현재 디렉토리 | `(Get-Location).Path` | `pwd` |
| git 브랜치 | `git rev-parse --abbrev-ref HEAD 2>$null` | `git rev-parse --abbrev-ref HEAD 2>/dev/null` |
| 모델명 | Claude 세션에서 직접 확인 | Claude 세션에서 직접 확인 |
| 토큰 사용량 | API 응답 헤더 또는 세션 메타데이터 | API 응답 헤더 또는 세션 메타데이터 |

### 출력 예시
```
C:\Users\ryan-woo\dev\my-project | claude-opus-4-5 | feature/add-login | 토큰 사용: 12,430 | 토큰 잔여: 187,570 (93.8%)
```

또는 macOS/Linux:
```
/home/ryan/dev/my-project | claude-opus-4-5 | main | 토큰 사용: 12,430 | 토큰 잔여: 187,570 (93.8%)
```

위 설정을 완료한 후, 매 응답마다 또는 요청 시 상태표시줄을 출력해줘.
```

---

## 📝 참고사항

- 이 파일은 새 프로젝트 시작 또는 머신 이동 시 위 프롬프트를 Claude Code에 붙여넣는 용도로 사용합니다.
- 토큰 정보는 Claude API 사용 환경에 따라 표시 가능 여부가 다를 수 있습니다.
- Windows 환경에서는 `jq` 대신 PowerShell의 내장 JSON 파싱 기능을 우선 사용하세요.
- git이 설치되어 있지 않은 경우 브랜치 항목은 생략하거나 `(git not installed)`로 표시됩니다.
