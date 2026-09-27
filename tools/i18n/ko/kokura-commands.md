## 13. 명령 실행 예제와 정확한 인수 문법

다음 PowerShell 명령은 각 저장소 폴더가 나란히 있는 상위 디렉터리에서 실행합니다. 먼저 `New-Item -ItemType Directory -Force out`으로 출력 디렉터리를 만들고, `out/game.gb`를 자신의 ROM 경로로 바꾸세요. KOKURA는 ROM 경로 뒤에 옵션을 지정하며, KUROSAKI의 `run` 하위 명령을 사용하지 않습니다. 설치한 실행 파일의 옵션 목록은 `--help`로 확인할 수 있습니다.

### 13.1 실행 작업과 프레임 상한 선택

| 인수 | 용도와 동작 |
| --- | --- |
| `ROM` | 일반 실행에 사용할 ROM 파일입니다. 작업이나 테스트 행렬에서 ROM을 따로 지정할 수도 있습니다. |
| `--hardware auto`, `dmg`, `cgb` | 하드웨어를 선택합니다. 기본값은 `auto`입니다. 두 모드를 지원하는 게임은 각 모드를 명시하여 시험하세요. |
| `--run-frames 120` | 직접 실행의 최대 프레임 수이며, 기본값은 1입니다. 중단 조건에 따라 더 일찍 끝날 수 있습니다. 입력 시퀀스에도 별도의 지속 시간이 있습니다. |
| `--job out/test.json` | JSON 작업을 실행합니다. 프레임 상한은 `run.frames`에 지정하고, ROM·상태·입력·캡처 설정은 작업에서 읽습니다. 작업 내부의 상대 경로는 작업 파일을 기준으로 해석합니다. |
| `--dump-report out/run.json` | 결과 보고서를 JSON으로 저장합니다. 출력 경로를 지정하지 않으면 일반 실행에서는 보고서를 표준 출력으로 내보냅니다. |
| `--regression-matrix out/matrix.json` | 기대 관측값을 포함하는 작업들을 실행합니다. 행렬 실행 명령이 성공해도 모든 사례가 통과했다는 뜻은 아니므로, JSON에서 각 사례의 결과를 확인하세요. |

한 번의 호출에는 하나의 작업을 선택하세요. 작업 선택의 우선순위는 디컴파일, 디스어셈블, 회귀 테스트 행렬, 링크 작업, 명령줄에 지정한 링크 세션, 일반 실행 순입니다. 여러 모드를 함께 지정해도 순서대로 모두 실행되지는 않습니다.

{{COMMAND:0}}

최대 120개의 에뮬레이션 프레임을 진행한 뒤 최종 화면과 보고서를 저장합니다. 이미지를 해석하기 전에 보고서의 실제 실행 프레임 수와 중단 이유를 확인하세요.

### 13.2 버튼을 계속 누르거나 시간별 입력 전달

| 옵션 | 문법과 사용법 |
| --- | --- |
| `--input "A,RIGHT"` | 직접 실행 중 두 버튼을 계속 누릅니다. 이름의 대소문자는 구분하지 않으며, `NONE`은 모든 버튼을 놓습니다. |
| `--input-seq "NONE:30;A:1;NONE:89"` | `BUTTONS:FRAMES` 구간을 세미콜론으로 구분하여 순서대로 실행합니다. 이 예는 30프레임 동안 버튼을 놓고, A를 1프레임 누른 뒤, 89프레임 동안 놓습니다. |
| `--input-script "NONE:30;A:1;NONE:89"` | 같은 형식의 시퀀스 문자열을 받으며, 파일 이름이 아닙니다. 두 시퀀스 옵션을 모두 지정하면 `--input-script`가 우선합니다. |

버튼 이름은 `RIGHT,LEFT,UP,DOWN,A,B,SELECT,START`입니다. 16진수 마스크는 RIGHT=0x01, LEFT=0x02, UP=0x04, DOWN=0x08, A=0x10, B=0x20, SELECT=0x40, START=0x80입니다. KOKURA의 입력 마스크이므로 NES 패드 마스크를 그대로 사용하지 마세요. PowerShell에서는 전체 시퀀스를 따옴표로 감쌉니다. 새로 누르는 순간을 시험할 때는 버튼을 놓는 구간을 넣고, 관측하려는 전체 시간 구간을 시퀀스가 포함하도록 하세요.

{{COMMAND:1}}

버튼 카운터 예제에서는 카운트가 한 번 증가해야 합니다. 정지 화면 한 장만으로는 길게 누를 때 반복 입력이 올바른지 판단할 수 없습니다. 계속 누르는 구간과 여러 번 나누어 누르는 경우를 비교하세요.

### 13.3 화면·움직임·음향 캡처

| 옵션 | 문법과 사용법 |
| --- | --- |
| `--png out/final.png` | 최종 화면을 저장합니다. `--screenshot`과 함께 지정하면 이 옵션이 우선합니다. |
| `--screenshot out/frame.png` | 화면 저장 경로를 지정하는 다른 옵션입니다. PNG와 BMP를 지원하며, 확장자가 없으면 `.png`를 붙입니다. |
| `--screenshot-frames 30:32` | 선택한 각 프레임을 저장하고 파일 이름에 프레임 번호를 넣습니다. 화면 저장 경로도 지정해야 합니다. |
| `--record-wav out/audio.wav` | 음향을 WAV로 녹음합니다. 실제로 소리를 재생하는 ROM과 구간을 사용하세요. |
| `--record-wav-frames 1:180` | 양 끝을 포함하는 녹음 구간입니다. 수치는 샘플 수가 아니라 프레임 번호입니다. |
| `--record-video out/motion.gif` | 움직임을 GIF 또는 Y4M으로 기록합니다. 확장자가 없으면 `.gif`를 붙이며, MP4는 지원 형식이 아닙니다. |
| `--record-video-frames 30:120` | 양 끝을 포함하는 영상 기록 구간을 선택합니다. |
| `--audio-buffer-frames 8192` | 스테레오 샘플 프레임 단위로 오디오 버퍼 용량을 설정합니다. 에뮬레이션 영상 프레임이나 개별 좌우 샘플의 수가 아닙니다. |

캡처 범위는 1부터 시작하는 10진수입니다. `30`은 한 프레임을, `30:32`는 30·31·32번 프레임을 선택합니다. 0이나 역순 범위는 거부됩니다. 캡처 번호는 이번 실행을 기준으로 하므로 저장 상태를 재개할 때는 보고서도 보관하세요. 캡처 전에 상위 디렉터리를 만들어 두세요.

{{COMMAND:2}}

스크롤과 애니메이션은 여러 프레임으로 평가하세요. 음향은 WAV로 확인해야 합니다. 화면에 완료 번호가 표시되었다고 해서 의도한 채널이 실제로 발음했다고 증명되는 것은 아닙니다.

### 13.4 기기 상태 저장과 재개

| 옵션 | 용도와 우선순위 |
| --- | --- |
| `--save-state out/checkpoint.kqs` | 실행이 끝날 때 기기 상태를 저장합니다. |
| `--snapshot out/checkpoint.kqs` | 같은 종류의 상태 출력이며, `--save-state`보다 우선합니다. |
| `--load-state out/checkpoint.kqs` | 실행 전에 KQS 상태를 불러옵니다. |
| `--resume-state out/checkpoint.kqs` | `--load-state`보다 우선하며, 작업에 지정된 입력 상태도 덮어쓸 수 있습니다. |
| `--snapshot-at "frame=60&&frame_end=>out/frame60.kqs"` | 관측 조건이 일치하면 저장합니다. 여러 번 지정할 수 있습니다. `=>path`가 없으면 현재 디렉터리에 ROM 이름을 바탕으로 번호가 붙은 파일 이름을 만듭니다. |

ROM과 에뮬레이터 버전에 맞는 상태를 사용하세요. KQS는 기기 상태이며, 카트리지 저장 RAM이나 C API의 JSON 직렬화 데이터와 다릅니다.

{{COMMAND:3}}

### 13.5 이름을 붙인 메모리 영역 관찰

| 옵션 | 문법과 사용법 |
| --- | --- |
| `--symbols out/game.map` | 해당 빌드의 컴파일러 출력에서 심볼을 불러옵니다. |
| `--source-map out/game.source_map.txt` | 실행 위치를 소스 위치와 연결합니다. |
| `--toolchain-metadata out/game.dbg2.json` | 구조화된 툴체인 메타데이터를 불러옵니다. ROM 옆의 대응하는 보조 파일을 자동으로 찾을 수도 있습니다. |
| `--watch-window "player:0xC700:16"` | 0xC700부터 16바이트를 player라는 이름으로 관찰합니다. 여러 영역을 각각 지정할 수 있습니다. 메모리를 관찰하는 기능이며 그 자체로 실행을 중단하지는 않습니다. |
| `--watch-baseline-mode initial` | 초기값과 비교합니다. `previous-frame`은 연속된 프레임끼리 비교하고, `named`는 명시적으로 캡처한 기준값을 선택합니다. |
| `--watch-baseline-tag ready` | 이름 기반 비교에서 사용할 기준값 이름을 선택합니다. |
| `--capture-watch-baseline "ready=>frame=30&&frame_end"` | 조건이 일치할 때 이름을 붙여 기준값을 캡처합니다. 다른 기준값도 반복 지정할 수 있습니다. |
| `--watch-fields preview,diff` | 관찰 필드 그룹을 `hash`, `activity`, `preview`, `baseline`, `diff`, `insights`, `all` 중에서 선택합니다. 미리보기 바이트는 제한된 범위의 미리보기이며, 전체 메모리 덤프가 아닙니다. |
| `--report-sections cpu,watched_memory` | 지정한 보고서 섹션을 남깁니다. `meta`와 `schema_version`은 항상 유지됩니다. 알 수 없는 이름을 지정해도 새 섹션이 생성되지 않습니다. |
| `--report-minimal cpu,watched_memory` | 섹션 목록을 받는 다른 옵션이며 `--report-sections`보다 우선합니다. 쉼표로 구분한 값이 필요하고, 켜기·끄기 스위치가 아닙니다. |

주소와 크기는 10진수 또는 `0x` 접두어가 있는 16진수를 받습니다. 변수 위치는 현재 빌드의 심볼로 찾으세요. 아래의 0xC700은 예시 주소이며 플레이어의 표준 위치가 아닙니다.

{{COMMAND:4}}

### 13.6 실행 조건이나 하드웨어 이벤트에서 중단

| 옵션 | 문법과 용도 |
| --- | --- |
| `--breakpoint "pc:0x0150"` | CPU 주소에서 중단합니다. `symbol:main`은 심볼을 사용하며, `@bank:2`를 덧붙이면 뱅크를 제한합니다. |
| `--watchpoint "player@0xC700+4"` | 4바이트 범위에 대한 메모리 쓰기에서 중단합니다. 앞의 이름은 선택 사항입니다. `+size`를 생략하면 1바이트를 감시합니다. |
| `--stop-on-mmio "scroll@0xFF43"` | 지정한 MMIO 레지스터에 쓰면 중단합니다. 여기서는 SCX입니다. |
| `--stop-on-irq "vblank:serviced"` | 인터럽트 종류와 단계를 선택합니다. 단계는 `requested`, `serviced`, `blocked`, `any`입니다. 단계만 지정하면 모든 인터럽트 종류에 일치합니다. |
| `--stop-on-dma oam_start` | DMA 이벤트를 선택합니다. 사용할 수 있는 이름은 `oam_start`, `oam_complete`, `hdma_start`, `hdma_block`, `hdma_complete`, `hdma_cancel`, `gdma_stall`, `hdma_deferred`, `hdma_ignored`입니다. |
| `--run-until "frame=60&&frame_end"` | 관측 조건의 모든 항목이 일치하면 중단합니다. 조건을 추가하려면 옵션을 반복 지정하세요. |

중단점 표기 `pc:`, `symbol:`, `@bank:`는 대소문자를 구분합니다. 메모리 주소와 뱅크는 10진수 또는 `0x` 접두어가 있는 16진수입니다. 발생하지 않을 수도 있는 중단 조건을 지정하더라도 프레임 상한은 유지하세요.

관측 조건은 AND 연산에 `&&`를 사용하며 C 식이 아닙니다. 지원 항목은 `frame=`, `ly=`, `pc=`, `bank=`, `bank_pc=bank:pc`, `symbol=`, `source=`, `event=`, `ppu_mode=`(또는 `mode=`), `basis=`입니다. 프레임과 LY 값은 10진수입니다. 심볼·소스·이벤트 항목은 문자열로 일치 여부를 판단합니다. basis 값에는 `frame_start`, `frame_end`, `step`, `event`, `trace`, `snapshot`, `stop`이 있습니다. 값 지정 없이 `frame_start`, `frame_end`, `stop`, `vblank`만 써도 됩니다. `hp<10` 같은 비교는 이 문법에 포함되지 않습니다.

{{COMMAND:5}}

첫 명령은 진입점을 조사하고, 두 번째 명령은 가로 스크롤 값을 바꾸는 코드를 찾는 데 사용합니다. 요청한 중단이 실제로 발생했는지 확인하세요.

### 13.7 관측 지점 기록과 실행 결과 비교

| 옵션 | 용도 |
| --- | --- |
| `--trace-point "frame=30&&frame_end"` | 조건이 일치하면 관측값을 기록합니다. 여러 지점을 반복 지정할 수 있습니다. |
| `--timeline-out out/timeline.jsonl` | 관측 타임라인을 저장합니다. |
| `--trace-jsonl out/timeline.jsonl` | 타임라인 저장 경로를 지정하는 다른 옵션이며 `--timeline-out`보다 우선합니다. 모든 명령을 빠짐없이 추적하라는 뜻은 아닙니다. |
| `--timeline-format jsonl` | `jsonl`(기본값) 또는 `csv`를 선택합니다. 파일 이름의 확장자는 형식에 맞게 직접 지정하세요. |
| `--replay-interval 1` | 리플레이 체크포인트를 활성화하고 프레임 단위 간격을 선택합니다. |
| `--replay-max-checkpoints 120` | 보관할 체크포인트 수를 제한합니다. 리플레이 기본값은 16개, 간격은 1입니다. |
| `--rewind-on-stop-frames 10` | 중단 후 보관된 리플레이 이력을 사용하여 되감도록 요청합니다. |
| `--stop-on-divergence` | 리플레이 제어기의 불일치 시 중단 동작을 활성화합니다. |
| `--dump-replay-tape out/baseline.json` | 기록한 리플레이 데이터를 내보냅니다. 생성하려면 리플레이 기록을 켜야 합니다. |
| `--compare-replay-tape out/baseline.json` | 내보낸 리플레이 데이터와 비교합니다. 결정적인 비교를 위해 같은 ROM·입력·초기 상태를 사용하세요. |
| `--compare-replay-watch-only` | 기기 전체의 비교 대신 관찰 대상 메모리의 관측값만 비교합니다. |
| `--snapshot-on-replay-mismatch out/mismatch` | 불일치가 발견되었을 때 조사용 자료에 사용할 파일 이름 접두어를 지정합니다. |

{{COMMAND:6}}

보고서에서 비교 결과와 첫 번째 불일치를 확인하세요. 두 파일이 생성되었다는 사실만으로 비교가 통과한 것은 아닙니다.

### 13.8 진단과 재현 가능한 조사

| 옵션 | 실제 동작 |
| --- | --- |
| `--emit-diagnostics out/events.jsonl` | SARAKURA에서 사용할 진단 이벤트를 내보냅니다. |
| `--diagnostics-jsonl out/events.jsonl` | 직접 실행의 진단 저장 경로를 지정하는 다른 옵션입니다. `--emit-diagnostics`가 우선합니다. |
| `--repro-bundle out/repro.zip` | 보고서, 진단 이벤트, 매니페스트를 묶습니다. ROM과 메타데이터는 경로로 참조하며 묶음 안에 넣지 않습니다. 화면·상태·트레이스도 자동으로 포함되지 않습니다. |
| `--break-on-diagnostic all` | 최종 보고서의 진단과 일치하는 경우 조사 자료를 캡처합니다. 문제가 되는 첫 명령에서 CPU를 중단하는 기능은 **아닙니다**. 필터가 비어 있지 않으면 최종 진단 중 어느 것이든 캡처 처리로 이어질 수 있습니다. |
| `--png-on-diagnostic out/diagnostic-images` | 진단 캡처 시 최종 화면을 저장할 디렉터리입니다. 파일 이름은 `diagnostic_000001.png`입니다. |
| `--snapshot-on-diagnostic out/diagnostic-states` | `diagnostic_000001.kqs`를 저장할 디렉터리입니다. 이 캡처는 각 이벤트가 발생한 순간이 아니라 현재의 최종 상태를 반영합니다. |
| `--diagnostic-pack NAME` | 인수는 받지만 실행 경로에서 진단 팩을 적용하지 않습니다. |
| `--diagnostic-rule RULE` | 반복 지정할 수 있는 인수이지만 실행 경로에서 선택한 규칙을 적용하지 않습니다. |
| `--diagnostic-summary-limit N` | 인수는 받지만 실행 경로에서 이 요약 상한을 적용하지 않습니다. |

{{COMMAND:7}}

특정 명령이나 쓰기 동작에서 중단하려면 13.6절의 디버거 옵션을 사용하세요. 진단은 상황에 맞게 해석해야 합니다. 의도적으로 대기하는 타이틀 화면에서도 게임 결함이 아닌 관측 결과가 나올 수 있습니다.

### 13.9 명령 디스어셈블과 의사 코드 조사

| 옵션 | 문법과 용도 |
| --- | --- |
| `--disassemble-out out/code.txt` | 일반 에뮬레이션 작업을 실행하지 않고 ROM 명령을 해독합니다. |
| `--disassemble-range "0:0100-0150"` | `BANK:START-END` 범위를 선택합니다. 여러 범위를 반복 지정할 수 있습니다. **세 숫자는 모두 16진수**이며, `0x`가 없어도 같습니다. |
| `--disassemble-format text` | `text`(기본값), `markdown`, `json` 중에서 선택합니다. |
| `--decompile-out out/functions.json` | 의사 코드와 제어 흐름 정보를 생성합니다. |
| `--decompile-format json` | `json`(기본값), `markdown`, `text` 중에서 선택합니다. |
| `--decompile-function main` | 함수를 선택합니다. 여러 함수를 반복 지정할 수 있으며, 대응하는 심볼이 있으면 식별 정확도가 높아집니다. |
| `--decompile-all` | 디컴파일러가 알고 있는 이름 있는 함수를 모두 포함합니다. |
| `--decompile-annotations out/annotations.json` | 디컴파일러의 JSON 형식으로 작성한 주석 정보를 읽습니다. |
| `--decompile-trace out/trace.json` | 디컴파일러 트레이스 메타데이터를 읽습니다. 임의의 JSONL 진단 로그로 대신할 수 없습니다. |

{{COMMAND:8}}

디스어셈블은 생성된 명령을 확인하는 데, 의사 코드는 제어 흐름을 파악하는 데 유용합니다. 어느 쪽도 원래의 C 프로그램을 정확히 복원하지는 않습니다. 같은 ROM 빌드에서 나온 심볼과 메타데이터를 보관하세요.

### 13.10 여러 기기를 연결하여 실행

| 옵션 | 문법과 용도 |
| --- | --- |
| `--link-job out/pair.json` | JSON 링크 작업에서 연결 구조와 세션을 읽습니다. 상대 경로는 작업 디렉터리를 기준으로 해석합니다. |
| `--link-topology pair` | 명령줄에 직접 지정한 세션의 연결 구조를 `pair`, `four_player_adapter`, `dmg07` 중에서 선택합니다. |
| `--link-session SPEC` | 세션 하나를 추가합니다. 최소 두 세션이 필요합니다. PowerShell에서는 세로줄로 구분한 문자열 전체를 따옴표로 감싸세요. |
| `--link-initial-peer-slot 1` | 상대 선택을 사용하는 연결 구조에서 최초 상대를 선택합니다. |

세션 필드에는 `name`, `slot`, `rom`, `symbols`, `source_map`, `toolchain_metadata`, `load_state`, `save_state`, `input`, `input_sequence`, `audio_buffer_frames`, `watch_window`가 있으며, `rom`은 필수입니다. 관찰 필드에는 `a:0xC700:4,b:0xC710:4`처럼 쉼표로 구분한 여러 영역을 넣을 수 있습니다. 실제로 직렬 데이터를 교환하는 프로그램을 사용하세요. 화면 두 개가 실행된다는 사실만으로 통신이 입증되지는 않습니다.
