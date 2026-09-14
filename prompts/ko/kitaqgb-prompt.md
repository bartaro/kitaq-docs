# KITAQGB·KOKURA·SARAKURA를 활용한 게임 개발

요구 사항을 작성한 뒤 이 문서 전체를 AI에 전달하세요. 명령은 `kitaqgb`, `kitaqfc`, `kokura`, `kurosaki`, `sarakura`, `kitaq-docs` 저장소와 `game-gb` 또는 `game-fc` 프로젝트가 같은 상위 폴더에 있는 구성을 가정합니다. 해당 상위 폴더에서 실행하고, 실제 환경에 맞게 경로를 조정하세요.

## 요구 사항

- 게임 이름: <작성>
- 장르와 핵심 플레이 방식: <작성>
- 조작 방법과 성공·실패 조건: <작성>
- 필수 화면·스테이지·적·아이템: <작성>
- 그래픽 스타일·배경 음악·효과음: <작성, 제공 자료의 경로도 명시>
- 저장·통신·주변기기 등 추가 요구 사항: <작성 또는 없음>
- 프로젝트 폴더: <작성>
- 재배포 조건: <예: 자체 제작 코드와 소재를 MIT로 공개할 수 있는 상태>

- 대상 기종: <초대 Game Boy / GB·CGB 양쪽 지원 / CGB 전용>
- 성능 목표: <예: 일반 플레이에서 초당 60회 게임 갱신. 부하가 큰 장면에서 허용할 동작도 명시>

## 수행할 작업

KITAQGB와 해당 라이브러리로 게임을 구현해 주세요. 실행과 디버깅에는 KOKURA를, 진단 정리와 수정 전후 비교에는 SARAKURA를 사용하세요.

합격 기준을 충족할 때까지 명세 구체화 → 작은 단위 구현 → 빌드 → 입력과 관찰 → 원인 조사 → 수정 → 동일 조건 재검증을 반복하세요. 계획 작성, 코드 제시 또는 컴파일 성공만으로 완료하지 마세요.

### 환경과 합격 기준 확인

1. 작업 폴더의 지침, 도구별 README, HTML 설명서, 사용할 라이브러리의 헤더와 구현을 읽으세요. 실행 파일 경로와 버전 또는 SHA-256을 기록하고, 명령은 실제 `--help` 출력으로, API는 소스로 확인하세요.
2. 입력·화면·소리·진행·갱신 빈도를 판정할 수 있는 합격 기준을 정하세요. 예를 들어 START를 눌렀다 놓으면 시작하고, 충돌하면 잔기가 하나 줄며, 일시 정지 시 지정한 소리가 멈추고 해제 후 다시 재생되는지 확인합니다.
3. 중요한 모호함만 질문하고, 일반적인 되돌릴 수 있는 구현 판단은 자율적으로 진행하세요. 요구 사항이나 합격 기준을 임의로 완화하지 마세요.
4. 먼저 작은 제공 예제를 컴파일러·에뮬레이터·SARAKURA로 실행해 도구 간 연결을 확인하세요. 이것을 요청받은 게임의 완성으로 간주하지 마세요.

### 작게 시작해 플레이 가능한 형태로 구현

- KITAQGB의 C 문법과 `void main()`을 사용하세요. 데스크톱 C나 GBDK API를 그대로 쓸 수 있다고 가정하지 마세요. 선언뿐 아니라 필요한 `.c` 구현도 빌드에 포함하고, 초기화 순서·단위·부호·범위·버퍼 수명·ROM 뱅크를 확인하세요.
- VRAM/OAM 갱신, VBlank, 인터럽트, 스택, ROM/WRAM 뱅크와 타일·스프라이트 제한을 설계에 반영하세요. 전송 큐의 총용량·여유 용량은 물리 VRAM의 용량·여유 공간과 다릅니다.
- DMG 대상 게임에 CGB 전용 기능을 사용하지 마세요. 양쪽을 지원한다면 각 하드웨어 모드에서 따로 검증하세요.
- 영문자·숫자·기호에는 제공된 자체 제작 `ascii.c` 글꼴을 사용하고, 문자와 타일의 대응을 확인하세요.

- 먼저 부팅·타이틀·조작 가능한 플레이어·성공 또는 실패·재시작을 연결한 뒤 내용을 늘리세요.
- 그래픽·음악·효과음의 편집 가능한 원본과 생성 절차를 보관하고, 빌드가 실제로 내보낸 데이터를 읽는지 확인하세요.
- 소스 주석은 영어, 진행 보고는 한국어로 작성하세요. SARAKURA의 표준 보고서는 영어로 유지하세요.

### 빌드와 실행 결과 연결

`out/iter-001`처럼 반복별 출력 폴더를 나누세요. 명령, 종료 코드, 소스·소재·도구·ROM·메타데이터의 해시를 기록하세요. 빌드 실패 후 남아 있는 이전 ROM을 실행하지 마세요. 맵·소스 맵·디버그 정보는 ROM과 동일한 빌드에서 나온 것을 사용하세요.

다음은 기본적인 DMG 확인 예입니다. `main.c`와 필요한 라이브러리 구현 파일을 준비하고 옵션과 입력 순서를 게임에 맞게 조정하세요.

```powershell
$iteration = '.\game-gb\out\iter-001'
New-Item -ItemType Directory -Force $iteration | Out-Null

# Include all additional implementation units required by the game.
& '.\kitaqgb\kitaqgb.exe' '.\game-gb\src\main.c' `
  -I '.\kitaqgb\lib' -o "$iteration\game.gb" `
  --profile=dev --rst-disable --stack-bank=fixed --no-disasm `
  "--emit-ai-metadata=$iteration\build.json"
if ($LASTEXITCODE -ne 0) { throw 'Build failed; inspect the build log.' }

# This sequence presses START once, with released intervals on both sides.
& '.\kokura\kokura-cli.exe' "$iteration\game.gb" `
  --hardware dmg --run-frames 300 `
  --input-seq 'NONE:60;START:1;NONE:239' `
  --png "$iteration\frame.png" --record-wav "$iteration\audio.wav" `
  --dump-report "$iteration\run.json" `
  --emit-diagnostics "$iteration\events.jsonl"
if ($LASTEXITCODE -ne 0) { throw 'Emulator run failed; inspect the run log.' }

& '.\sarakura\sarakura.exe' gb analyze `
  --metadata "$iteration\build.json" --events "$iteration\events.jsonl" `
  --frames 300 --out "$iteration\analysis" --fail-on error
if ($LASTEXITCODE -ne 0) { throw 'Inspect the analysis report and fix the cause.' }
```


`--hardware dmg`는 초대 GB용입니다. CGB 또는 양쪽 지원을 시험할 때는 ROM 헤더와 에뮬레이터 기종 설정을 맞추세요. 예제 입력은 버튼을 놓은 구간 사이에서 START를 한 번 누릅니다. 300프레임 실행이 게임 전체의 검증을 뜻하지는 않습니다.

### 화면·소리·상태·성능 확인

- 누르기·유지·놓기를 구분한 입력 시나리오를 저장하세요. 부팅, 시작, 이동, 행동, 충돌, 스크롤, 스테이지 전환, 게임 오버, 재시작, 일시 정지와 필요한 저장·통신 등 명세의 모든 경로를 실행하세요.
- 필요한 프레임의 PNG, 입력 데이터, 실행 보고서, 진단 JSONL, WAV와 필요한 상태·메모리 관측을 보관하세요. 도달 프레임과 정지 이유를 확인하세요. 이미지를 실제로 열어 보고, 한 장의 스크린샷만으로 움직임이나 입력 반응을 검증했다고 하지 마세요. 카운터·좌표·상태 전환을 기대값과 비교하고 화면 끝·타일 및 속성 경계·스프라이트 밀집 장면도 확인하세요.
- 음악·효과음·동시 재생·끊김·일시 정지·재개를 확인하세요. WAV 생성만으로 올바른 소리를 증명할 수 없습니다. 들을 수 없는 환경에서는 실시한 파형·수치 검사와 아직 확인하지 못한 청감 품질을 구분하세요.
- 부하가 큰 장면의 대상 CPU 작업량·게임 갱신·전송량을 측정하고 FC에서는 NMI 작업도 포함하세요. 호스트에서의 에뮬레이터 처리 속도를 게임 갱신 빈도나 실기 속도와 동일시하지 마세요. `--allow-unimplemented`로 계속 실행된다고 해서 미구현 기능이 지원되는 것은 아닙니다.

### 분석·수정·재검증

- 시험한 ROM의 빌드 메타데이터와 해당 실행의 진단 JSONL을 SARAKURA에 전달하세요. CPU 트레이스나 일반 실행 보고서로 대체하지 마세요. `--frames`는 분석 조건이며, SARAKURA는 ROM을 실행하거나 소스를 자동 수정하지 않습니다.
- `report.html`, `ai_diagnostics.json`, `repair_prompt.md`, `retest_plan.json`을 읽고 재현 절차·화면·소리·소스와 대조하세요. 추정한 소스 위치와 원인을 확인된 사실과 구분하고, 정상 대기 루프와 멈춤 버그를 구분하세요. 경고를 개별 판단하고 미지원 이벤트와 분석 한계를 기록하세요. 필터로 경고를 숨기거나 테스트를 줄여 합격시키지 마세요.
- 문제를 최소 재현 예제로 줄이고 원인을 수정한 뒤 다시 빌드하세요. 컴파일러나 에뮬레이터가 원인이면 게임 코드와 분리해 결함을 확인하고 도구 수정에 회귀 검증을 추가하세요.
- 입력·난수 시드·기종 및 영상 방식·매퍼·관측 프레임·진단 설정을 맞춰 재검증하세요. ROM마다 해당 메타데이터를 사용하고 코드나 RAM 배치가 바뀐 뒤 저장 상태를 무조건 재사용하지 마세요.

```powershell
& '.\sarakura\sarakura.exe' baseline-delta `
  --baseline '.\game-gb\out\iter-001\analysis' `
  --current '.\game-gb\out\iter-002\analysis' `
  --out '.\game-gb\out\delta.json' --markdown '.\game-gb\out\delta.md' `
  --fail-on-new error --fail-on-regression error --enforce
```


진단 차이는 조작·그래픽·소리의 합격 판정과 함께 사용하세요. 같은 실패가 반복되면 근거와 가설을 다시 검토하고 무작정 수정을 이어 가지 마세요.

### 완료 조건과 결과물

납품할 소스와 설정으로 만든 최종 ROM에서 모든 필수 시나리오를 다시 실행하세요. 무적 상태·자동 시험 입력·다른 매퍼만으로 최종 빌드의 일반 플레이를 검증했다고 하지 마세요. 요구 사항과 시험의 대응표, 남은 경고의 이유, 미확인·미지원 항목을 명시하세요. 실기 시험을 하지 않았다면 ‘실기 미확인’으로 표시하세요.

소스, 도구·라이브러리 식별 정보, 편집 가능한 소재, 재현 가능한 빌드·검증 스크립트, ROM, 최종 검증 증거, 설치·조작·알려진 제한을 설명한 README를 제공하세요. 필요한 리플레이와 검증 하네스도 포함하세요. 공개·외부 전송은 명시적으로 허용된 범위에서만 수행하세요. 검증 후 불필요한 중간 빌드와 임시 트레이스는 지우되 소스·소재·최종 결과물·필요한 회귀 증거는 보관하세요.

환경이나 권한 때문에 필수 검사를 할 수 없다면 정확한 재현 절차와 필요한 조치를 보고하고, 완료로 처리하지 마세요.
