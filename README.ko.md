# KITAQ SERIES 설명서

[English](README.md#english) | [日本語](README.md#japanese) | **한국어**

<!-- ai-prompts:start -->
## 생성형 AI 게임 개발 프롬프트

요구 사항을 작성한 뒤 프롬프트 전체를 AI에 전달하세요. 구현, 에뮬레이터 테스트, SARAKURA 분석, 수정 후 재검증까지 다룹니다.

KITAQGB · KITAQFC
<!-- ai-prompts:end -->

## 도구별 설명서 바로 열기

아래 링크를 누르면 해당 도구의 한국어 설명서가 바로 열립니다.

| 설명서 | 내용 |
| --- | --- |

## HTML 설명서

2026년 9월 14일의 소스를 기준으로 한 설명서 7권을 9개 언어로 제공합니다. 모든 언어판에는 같은 API 항목 1,055개와 완성 예제 프로그램 47개가 있습니다. 한국어는 `ko/index.html`, 영어는 `en/index.html`, 일본어는 `index.html`을 여세요. 각 권에서 언어를 바꿀 수 있습니다. 검증 기록에는 시험에 사용한 소스, 실행 파일, 조건이 명시되어 있습니다.

원본 소스에서 발췌한 코드와 도구의 실행 출력은 그대로 유지합니다. [저장소를 내려받아 배치하는 방법](GITHUB_SETUP.md)과 [공개 전 확인 기록](PUBLICATION_CHECKS.md)도 참고하세요. HTML은 오프라인으로 읽을 수 있고, 권별 검색·코드 복사·인쇄 기능을 제공합니다.

전체 목차와 제1권 앞부분에는 KITAQGB 이름의 두 가지 뜻과 NORCAL에 대한 감사의 글이 있습니다. 영문자·숫자·기호에는 제공된 `samples/assets/ascii.c`를 사용합니다. GB용 데이터는 ASCII 순서로 재배열하고, FC용 데이터는 NES 비트플레인 형식으로 변환합니다. 글자 모양은 바꾸지 않습니다.

본문, 추가 예제, 생성 도구는 MIT 라이선스로 제공합니다. 제공된 92개 글자 모양도 2026년 9월 12일에 작성자가 직접 제작했으며 MIT로 공개해도 된다고 확인했습니다. 기존 소프트웨어의 발췌 부분은 원래 저작권 고지를 유지합니다. 재배포할 때는 [제3자 권리 고지](THIRD_PARTY_NOTICES.md)와 해당 라이선스를 함께 포함하세요.

설명서에는 [영어 라이선스 원문](LICENSE)과 [일본어 참고 번역](LICENSE.ja)이 들어 있습니다. [제3자 권리 고지](THIRD_PARTY_NOTICES.md)에서 각 도구의 일본어 라이선스로도 이동할 수 있습니다. 해석이 다르면 영어 원문을 우선합니다. 소프트웨어 바이너리를 배포할 때는 의존 라이브러리의 별도 라이선스도 필요합니다. 설명서를 공개할 수 있다는 사실이 모든 도구와 의존 항목을 MIT만으로 재배포할 수 있다는 뜻은 아닙니다.

## 예제 빌드

여러 저장소를 하나의 상위 폴더 아래에 나란히 clone한 뒤, 그 상위 폴더에서 다음 명령을 실행하세요. 배치 예시는 [GITHUB_SETUP.md](GITHUB_SETUP.md)에 있습니다. 제공된 컴파일러를 쓰거나 설명서의 절차로 다시 빌드하세요. 이번 판에는 컴파일러 수정 사항도 포함되어 있습니다.

```powershell
.\kitaq-docs\samples\build.ps1 -Only gb_hello,fc_hello
.\kitaq-docs\samples\build.ps1
```

소스를 다른 위치에 두었다면 `-Root "소스 트리의 절대 경로"`를 지정하세요. 실행 파일이 다른 곳에 있으면 `-GbCompiler`와 `-FcCompiler`로 선택할 수 있습니다. 생성한 ROM과 로그는 기본적으로 `samples/out/<sample-id>`에 저장됩니다. 이 설명서 패키지에는 컴파일러 실행 파일, 상용 ROM, BIOS가 포함되지 않습니다.

`samples/api-fragments`는 초기화와 유효한 인수를 갖춘 프로그램에 넣어 사용하는 코드 조각입니다. ROM 일괄 빌드 대상은 `samples/manifest.json`의 완성 프로그램 47개입니다. 각 권에서는 선언만 있는 API, 실행하지 않은 코드 조각, 실물 하드웨어에서 확인하지 않은 기능을 구분합니다.

## GitHub에 공개하기

1. 이 폴더의 내용을 저장소 최상위 또는 `docs` 폴더에 넣습니다.
2. `index.html`, 7권의 본편, `verification.html`, `loop-engineering.html`, `prompts`, 언어별 폴더, `assets`, `samples`, `reference`, `verification`, README, 라이선스 고지를 함께 업로드합니다. `.nojekyll`도 포함하세요.
3. GitHub의 Settings → Pages → Build and deployment에서 Source를 Deploy from a branch로 설정합니다.
4. 업로드한 브랜치와 배치에 맞는 `/ (root)` 또는 `/docs`를 선택하고 저장합니다.
5. 배포가 완료되면 Pages에 표시된 주소를 열고 목차와 각 권의 링크를 확인합니다.

자세한 설정은 [GitHub의 게시 소스 설정 안내](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)를 참고하세요. `manual/_manual_work`는 로컬 빌드·검증 작업 공간이며 공개 대상에서 제외합니다.

## 편집과 갱신

일본어 본문은 `tools/chapters.py`, 영어 본문은 `tools/en/*.md`에 있습니다. `tools/generate_en.py`는 영어판을 생성하며, `tools/generate.py`에는 API 사전과 페이지 생성 처리가 있습니다. 화면 스타일은 `assets/manual.css`에서 정합니다. 설명서를 갱신할 때는 Python을 사용합니다.

```powershell
python -B kitaq-docs/tools/collect.py
python -B kitaq-docs/tools/make_samples.py
python -B kitaq-docs/tools/catalog.py
python -B kitaq-docs/tools/generate.py
python -B kitaq-docs/tools/generate_en.py
foreach ($language in @('ko','zh-CN','zh-TW','es','pt','fr','de')) {
    python -B kitaq-docs/tools/generate_i18n.py --language $language
    if ($LASTEXITCODE -ne 0) { throw "Manual generation failed: $language" }
}
python -B kitaq-docs/tools/check_site.py
python -B kitaq-docs/tools/check_bilingual.py
```

확인한 화면은 샘플 설명과 함께 제공합니다. 빌드 로그, 실행 로그 및 로컬 검증 기록은 공개 파일에 포함하지 않습니다. 업로드하기 전에 `tools/export_public.py`로 매뉴얼을 별도의 Git 작업 폴더에 내보내세요. [제3자 권리 고지](THIRD_PARTY_NOTICES.md)도 확인하세요.

## 이번 소스 공개의 범위

KOKURA-GUI, KUROSAKI-GUI, PLITA는 이번 업로드에서 제외합니다. 공개 소스와 설명서는 명령줄 도구, 코어, 연동 API를 다룹니다.
