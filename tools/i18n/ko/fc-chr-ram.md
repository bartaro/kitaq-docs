### 8.1 그래픽을 갱신할 수 있는 CHR RAM

`--nes-chr-ram`은 쓰기 가능한 8 KiB CHR RAM을 사용하는 카트리지 ROM을 만듭니다. ROM 파일에는 CHR 데이터가 저장되지 않으므로 초기화할 때 프로그램이 타일 패턴을 PPU에 업로드해야 합니다. `wire3d.c` 렌더러가 이 모드를 사용합니다.

{{BUILD}}

`--nes-chr=tiles.chr` 또는 `--chr-rom=tiles.chr`은 준비한 패턴을 CHR ROM으로 포함합니다. 두 옵션 모두 `--nes-chr-ram`과 함께 사용할 수 없습니다. CNROM 설정도 CHR RAM 모드를 지원하지 않습니다. 대상 매퍼와 보드에 필요한 CHR RAM이 있는지 확인하세요.

CHR 옵션을 모두 생략하면 빈 8 KiB CHR ROM이 포함됩니다. 실행 중에 패턴을 업로드하는 예제에서는 `--nes-chr-ram`을 명시하세요. CHR RAM은 CPU 쪽 PRG RAM과 별개이며, 와이어프레임 임시 버퍼용 PRG RAM도 따로 확보해야 합니다.
